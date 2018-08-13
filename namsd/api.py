import os
import json
import queue
import threading
import datetime
import logging
import win32event
from multiprocessing import freeze_support

from gevent.pywsgi import WSGIServer
from flask import Flask
from flask import g
from flask import request
from flask_cors import CORS

from db import DataBase
from config import config
from controller import Controller
import logger
import defs

app = Flask(__name__)
CORS(app)
db_info = config['db']


@app.before_request
def before_request():
    g.db = DataBase(**db_info)
    g.db.connect()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.disconnect()


@app.route('/led', methods=['POST'])
def set_led():
    def toggle(modules):
        while 42:
            try:
                mod = modules.get(False)
            except queue.Empty:
                break
            ctrl = Controller(mod['ip'], '', config['miner_type'])
            ctrl.cgminer.run(
                'ascset',
                '{},led,{}-{}'.format(
                    mod['device_id'], mod['module_id'], mod['led']))
            modules.task_done()

    data = request.json.get('modules')
    modules = queue.Queue()
    for m in data:
        modules.put(m)
    for i in range(0, min(50, len(data))):
        t = threading.Thread(target=toggle, args=(modules,))
        t.start()
    modules.join()
    return json.dumps({'result': True})


@app.route('/timestamp', methods=['GET'])
def get_timestamp():
    res = g.db.run('raw', 'SELECT * from `preferences` where pref_key in ("timestamp", "force_update")')
    return json.dumps({'result': {res[0]['pref_key']: res[0]['pref_value'], res[1]['pref_key']: res[1]['pref_value']}})


def get_data_from_file(f):
    res = []
    try:
        for line in f.readlines():  # 依次读取每行
            line = line.strip()  # 去掉每行头尾空白
            res.append(json.loads(line))
    except Exception as e:
        print(e)
    f.close()
    return res


@app.route('/controllers_data', methods=['GET'])
def get_controllers_data():
    timestamp = datetime.datetime.strptime(json.loads(get_timestamp())['result']['timestamp'], defs.get_db_time_format())
    f = open(defs.get_controller_data_file(timestamp), 'r')
    res = get_data_from_file(f)
    f.close()
    return json.dumps({'result': res})


@app.route('/pools_data', methods=['GET'])
def get_pools_data():
    timestamp = datetime.datetime.strptime(json.loads(get_timestamp())['result']['timestamp'], defs.get_db_time_format())
    f = open(defs.get_pool_data_file(timestamp), 'r')
    res = get_data_from_file(f)
    f.close()
    return json.dumps({'result': res})


@app.route('/devices_data', methods=['GET'])
def get_devices_data():
    timestamp = datetime.datetime.strptime(json.loads(get_timestamp())['result']['timestamp'], defs.get_db_time_format())
    f = open(defs.get_device_data_file(timestamp), 'r')
    res = get_data_from_file(f)
    f.close()
    return json.dumps({'result': res})


@app.route('/modules_data', methods=['GET'])
def get_modules_data():
    timestamp = datetime.datetime.strptime(json.loads(get_timestamp())['result']['timestamp'], defs.get_db_time_format())
    f = open(defs.get_module_data_file(timestamp), 'r')
    res = get_data_from_file(f)
    f.close()
    return json.dumps({'result': res})


@app.route('/controllers', methods=['GET'])
def get_controllers():
    res = g.db.run('select', 'controllers', ['ip'])
    return json.dumps({'result': res})


@app.route('/controllers', methods=['POST'])
def post_controllers():
    controllers = request.json.get('controllers')
    g.db.run('raw', 'DROP TABLE IF EXISTS controllers')
    g.db.run('create', 'controllers',
             {'ip': 'VARCHAR(40)',
              'passwd': 'VARCHAR(20)',
              'miner_type': 'VARCHAR(10) DEFAULT "{}"'.format(
                  config['miner_type']),
              'miner_port': 'INT DEFAULT 4028',
              'luci_port': 'INT DEFAULT 80',
              'tty_port': 'INT DEFAULT 22',
              'https_enable': 'BOOL DEFAULT 0',
              'ssh_enable': 'BOOL DEFAULT 1'},
             'PRIMARY KEY(`ip`)')

    for c in controllers:
        temp = {
            'ip': c['ip'],
            'passwd': getattr(c, 'passwd', ''),
            'miner_type': config['miner_type'],
            'miner_port': getattr(c, 'miner_port', 4028),
            'luci_port': getattr(c, 'luci_port', 80),
            'tty_port': getattr(c, 'tty_port', 22),
            'https_enable': getattr(c, 'https_enable', False),
            'ssh_enable': getattr(c, 'ssh_enable', True)}
        g.db.run('insert', 'controllers',
                 list(temp.keys()), list(temp.values()))
    g.db.commit()

    if len(controllers) > 0:
        update_force_refresh_timestamp()
        signal_restart_collect()
    return get_controllers()


@app.route('/controllers/<ip>', methods=['DELETE'])
def delete_controller(ip):
    g.db.run('raw', 'delete from controllers where ip = "' + ip + '"')
    g.db.commit()
    return get_controllers()


@app.route('/preference', methods=['POST'])
def post_preference():
    preference = request.json.get('preference')
    g.db.run('raw',
             'update preferences set pref_value="' + preference['pref_value'] + '" where pref_key="' + preference[
                 'pref_key'] + '"')
    g.db.commit()
    return get_preferences()


@app.route('/preferences', methods=['GET'])
def get_preferences():
    res = g.db.run('select', 'preferences')
    return json.dumps({'result': res})


def update_force_refresh_timestamp():
    g.db.run('raw', 'update preferences set pref_value = "1" where pref_key = "force_update"')
    g.db.commit()


def signal_restart_collect():
    hEvent = win32event.OpenEvent(win32event.EVENT_ALL_ACCESS, 0, "Global\\CollectEvent")
    if hEvent != None:
        win32event.SetEvent(hEvent)


def start_server():
    port = config['port']

    inf_logger = logger.create_rotate_logger("API Info", logging.INFO, "api_info.log")
    err_logger = logger.create_rotate_logger("API Error", logging.ERROR, "api_err.log")

    http_server = WSGIServer(
        ('127.0.0.1', port), app,
        log=inf_logger, error_log=err_logger)
    http_server.serve_forever()


if __name__ == '__main__':
    os.makedirs(config['log_dir'], exist_ok=True)
    freeze_support()
    start_server()
