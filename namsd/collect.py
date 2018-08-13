import os
import shutil
import datetime
import time
import json
import threading
import queue
import logging
import traceback
from multiprocessing import Process
from multiprocessing import freeze_support
from multiprocessing import JoinableQueue

from db import DataBase
from controller import Controller
from defs import COLUMN_CONTROLLERS
from defs import COLUMN_POOLS
from defs import COLUMN_DEVICES
from defs import COLUMN_MODULES
from defs import get_db_time_format
from defs import get_dir_time_format
from defs import get_data_dir
from defs import get_controller_data_file
from defs import get_device_data_file
from defs import get_module_data_file
from defs import get_pool_data_file
from config import config
import logger


def get_ctrls(db, logger):
    db.connect()
    ctrl_info = db.run('select', 'controllers')
    logger.info("controllers: %s", ctrl_info)
    db.disconnect()
    return ctrl_info


def init_ctrl_queue(ctrl_info):
    ctrl_queue = JoinableQueue()
    for c in ctrl_info:
        ctrl_queue.put(Controller(**c))
    return ctrl_queue


class CtrlThread(threading.Thread):
    def __init__(self, ctrl_queue, data_queue, timestamp, seq):
        threading.Thread.__init__(self)
        self.ctrl_queue = ctrl_queue
        self.data_queue = data_queue
        self.timestamp = timestamp
        self.seq = seq
        self.logger = logger.create_file_logger("Ctrl Thread", logging.INFO,
                                                timestamp, 'collect_ctrl_thread.log')

    def run(self):
        self.logger.info("thread start")
        while True:
            try:
                ctrl = self.ctrl_queue.get(False)
                self.logger.info("collect ctrl %d %s", self.seq, ctrl.ip)
            except queue.Empty:
                break
            try:
                self.logger.info("collect ctrl %s", ctrl.ip)
                temp = ctrl.collect(self.timestamp, self.logger)
                self.logger.info("collect ctrl result, %s", ctrl.ip)
                self.data_queue.put(temp)
            except Exception as e:
                self.logger.info("ctrl Exception: %s, trace: %s", repr(e), traceback.print_exc())
            finally:
                self.ctrl_queue.task_done()
        self.logger.info("collect ctrl end")


class DataThread(threading.Thread):
    def __init__(self, data_queue, sql_queue, timestamp):
        threading.Thread.__init__(self)
        self.data_queue = data_queue
        self.sql_queue = sql_queue
        self.logger = logger.create_file_logger("Data Thread", logging.INFO,
                                                timestamp, 'collect_data_thread.log')

    def run(self):
        self.logger.info("thread start")
        while True:
            try:
                data = self.data_queue.get(False)
            except queue.Empty:
                continue
            if data is None:
                self.logger.info("break")
                break
            self.logger.info("data : %s", data.ip)
            try:
                processed_data = data.reformat(self.logger)
                self.logger.info("data reformat: %s", str(processed_data))
                self.sql_queue.put(processed_data)
            except Exception as e:
                self.logger.info("data Exception: %s", repr(e))
        self.logger.info("data end")


class SQLThread(threading.Thread):
    def __init__(self, sql_queue, db_info, timestamp):
        threading.Thread.__init__(self)
        self.sql_queue = sql_queue
        self.db = DataBase(**db_info)
        self.timestamp = timestamp
        self.logger = logger.create_file_logger("Sql Thread", logging.INFO,
                                                timestamp, 'collect_sql_thread.log')

    def run(self):
        self.logger.info("thread start")
        os.makedirs(get_data_dir(self.timestamp), exist_ok=True)
        ctrl_file = open(get_controller_data_file(self.timestamp), 'a')
        pool_file = open(get_pool_data_file(self.timestamp), 'a')
        module_file = open(get_module_data_file(self.timestamp), 'a')
        device_file = open(get_device_data_file(self.timestamp), 'a')
        local = 0
        while True:
            try:
                data = self.sql_queue.get(False)
            except queue.Empty:
                continue
            if data is None:
                self.logger.info("disconnect")
                break
            try:
                self.logger.info('data %s', str(data))
                ctrl_file.write(json.dumps(data['controllers']) + '\n')
                ctrl_file.flush()
                for p in data['pools']:
                    pool_file.write(json.dumps(data['pools'][p]) + '\n')
                pool_file.flush()
                for d in data['devices']:
                    device_file.write(json.dumps(data['devices'][d]) + '\n')
                device_file.flush()
                for d in data['modules']:
                    for m in data['modules'][d]:
                        module_file.write(json.dumps(data['modules'][d][m]) + '\n')
                module_file.flush()

                local += data['controllers']['mhs_5m']
            except Exception as e:
                self.logger.info("sql Exception: %s", repr(e))
        ctrl_file.close()
        pool_file.close()
        module_file.close()
        device_file.close()
        update_db(self.db, self.timestamp, local)


def CtrlProcess(ctrl_queue, data_queue, timestamp, thread_num):
    for i in range(thread_num):
        th = CtrlThread(ctrl_queue, data_queue, timestamp, i)
        th.start()
    ctrl_queue.join()
    for i in range(thread_num):
        data_queue.put(None)


def DataProcess(data_queue, sql_queue, timestamp, thread_num):
    ths = []
    for i in range(thread_num):
        th = DataThread(data_queue, sql_queue, timestamp)
        th.start()
        ths.append(th)
    for th in ths:
        th.join()
    for i in range(thread_num):
        sql_queue.put(None)


def SQLProcess(sql_queue, db_info, timestamp, thread_num):
    # ths = []
    # for i in range(thread_num):
    th = SQLThread(sql_queue, db_info, timestamp)
    th.start()
    # ths.append(th)
    # for th in ths:
    th.join()


def init_db(db, miner_type, timestamp):
    db.connect()
    db.run('create',
           'controllers_data_{:%y%m%d_%H%M}'.format(timestamp),
           COLUMN_CONTROLLERS,
           'PRIMARY KEY(`time`, `ip`)')
    db.run('create',
           'pools_data_{:%y%m%d_%H%M}'.format(timestamp),
           COLUMN_POOLS,
           'PRIMARY KEY(`time`, `ip`, `pool_id`)')
    db.run('create',
           'devices_data_{:%y%m%d_%H%M}'.format(timestamp),
           COLUMN_DEVICES[miner_type],
           'PRIMARY KEY(`time`, `ip`, `device_id`)')
    db.run('create',
           'modules_data_{:%y%m%d_%H%M}'.format(timestamp),
           COLUMN_MODULES[miner_type],
           'PRIMARY KEY(`time`, `ip`, `device_id`, `module_id`)')
    db.commit()
    db.disconnect()


def update_db_if_needed(db, timestamp):
    db.connect()
    res = db.run('raw', 'SELECT pref_value from `preferences` where pref_key = "force_update"')
    if res[0]['pref_value'] == '1':
        formater = '{:' + (get_db_time_format()) + '}'
        formatted_ts = formater.format(timestamp)
        db.run('raw', 'update preferences set pref_value = "{0}" where pref_key = "timestamp"'.format(formatted_ts))
        db.commit()
    db.disconnect()


def update_db(db, timestamp, local):
    db.connect()
    formater = '{:' + (get_db_time_format()) + '}'
    print(formater)
    formatted_ts = formater.format(timestamp)
    sql = 'REPLACE INTO hashrate (time, local) VALUES("{0}", {1})'.format(formatted_ts, local)
    print(sql)
    db.run('raw', sql)
    db.run('raw', 'update preferences set pref_value = "{0}" where pref_key = "timestamp"'.format(formatted_ts))
    db.run('raw', 'update preferences set pref_value = "0" where pref_key = "force_update"')
    db.commit()
    db.disconnect()
    pass


def get_collect_interval(db):
    db.connect()
    interval = db.run('raw',
                      'select pref_value from preferences where pref_key = "collect_interval"')
    db.disconnect()
    return int(interval[0]['pref_value']) * 60


def clean_data_log():
    timestamp = get_dir_time_format().format(datetime.datetime.now() - datetime.timedelta(days=1))
    remove_subdir(timestamp, config['data_dir'])
    remove_subdir(timestamp, config['log_dir'])


def remove_subdir(timestamp, dir):
    dirs = os.listdir(dir)
    for f in dirs:
        path = os.path.join(dir, f)
        print(path, timestamp)
        if os.path.isdir(path) and timestamp > os.path.basename(path):
            print('remove ', path, timestamp)
            try:
                shutil.rmtree(path, ignore_errors=True)
            except Exception as e:
                print(e)


def collect():
    db_info = config['db']
    thread_num = config['thread_num']
    miner_type = config['miner_type']
    db = DataBase(**db_info)
    _logger = logger.create_rotate_logger("Collect Info", logging.INFO, "collect.log")

    while True:
        _logger.info("collect start")
        timestamp = datetime.datetime.now()
        update_db_if_needed(db, timestamp)

        # init_db(db, miner_type, timestamp)

        ctrl_info = get_ctrls(db, _logger)
        ctrl_queue = init_ctrl_queue(ctrl_info)
        data_queue = JoinableQueue()
        sql_queue = JoinableQueue()

        ctrl_process = Process(
            target=CtrlProcess,
            name="collect ctrl",
            args=(ctrl_queue, data_queue, timestamp, thread_num))
        data_process = Process(
            target=DataProcess,
            name="collect data",
            args=(data_queue, sql_queue, timestamp, thread_num))
        sql_process = Process(
            target=SQLProcess,
            name="collect sql",
            args=(sql_queue, db_info, timestamp, thread_num))

        ctrl_process.start()
        data_process.start()
        sql_process.start()

        ctrl_process.join()
        data_process.join()
        sql_process.join()

        _logger.info("collect end")
        clean_data_log()

        duration = (datetime.datetime.now() - timestamp).seconds
        interval = get_collect_interval(db)
        _logger.info('time %d %d', duration, interval)
        if duration < interval:
            time.sleep(interval - duration)


def collect_test():
    # for debug only
    ctrl = Controller('192.168.1.81', '', 'avalon7')
    ctrl_info = [ctrl]
    timestamp = datetime.datetime.now()
    try:
        temp = ctrl.collect(timestamp)
        temp.reformat()
        print("collect ctrl result, ", ctrl.ip)
    except Exception as e:
        print("ctrl Exception: %s, trace: %s", repr(e), traceback.print_exc())
    duration = (datetime.datetime.now() - timestamp).seconds
    interval = 60
    print('time ', duration, interval)
    while duration < interval:
        print('need sleep')
        time.sleep(3)
        new_ctrl_info = [ctrl]
        # 用户改了ip段，要立刻开始扫描
        if (len(ctrl_info) != len(new_ctrl_info) or
                (len(ctrl_info) > 0 and ctrl_info[0].ip != new_ctrl_info[0].ip)):
            print('controllers changed, break')
            break
        duration = (datetime.datetime.now() - timestamp).seconds


if __name__ == "__main__":
    os.makedirs(config['log_dir'], exist_ok=True)
    os.makedirs(config['data_dir'], exist_ok=True)
    freeze_support()
    # collect_test()
    collect()
