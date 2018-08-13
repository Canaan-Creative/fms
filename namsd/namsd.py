#!/usr/bin/env python3

import sys
import os
from multiprocessing import Process
from multiprocessing import freeze_support
import time
import datetime
import logging

from collect import collect
from api import start_server
from db import DataBase
from defs import COLUMN_PREFERENCES
from defs import PREF_KEY_DEFAULT_VALUE
from config import config
from logger import create_rotate_logger


def db_init(db, miner_type):
    _logger = create_rotate_logger('NAMSD', logging.INFO, 'namsd.log')
    _logger.info('db_init')

    db.connect()
    db.run('create', 'controllers',
           {'ip': 'VARCHAR(40)',
            'passwd': 'VARCHAR(20)',
            'miner_type': 'VARCHAR(10) DEFAULT "{}"'.format(miner_type),
            'miner_port': 'INT DEFAULT 4028',
            'luci_port': 'INT DEFAULT 80',
            'tty_port': 'INT DEFAULT 22',
            'https_enable': 'BOOL DEFAULT 0',
            'ssh_enable': 'BOOL DEFAULT 1'},
           'PRIMARY KEY(`ip`)')
    db.run('create', 'hashrate',
           {'time': 'TIMESTAMP',
            'local': 'DOUBLE'},
           'PRIMARY KEY(`time`)')
    db.run('create', 'preferences',
           COLUMN_PREFERENCES,
           'PRIMARY KEY(`pref_key`)')

    for (k, v) in PREF_KEY_DEFAULT_VALUE.items():
        db.run('raw', 'insert or ignore into preferences (pref_key, pref_value) values("{0}", "{1}")'
               .format(k, v))
        db.commit()
    db.disconnect()


def init():
    db = DataBase(**(config['db']))
    miner_type = config['miner_type']

    db_init(db, miner_type)


def linux_main():
    init()
    api_process = Process(target=start_server)
    api_process.daemon = True
    api_process.start()

    collect_process = Process(target=collect)
    collect_process.start()
    # collect_process.join()
    # TODO: kill collect process when time up


def win32_main():
    import win32serviceutil
    import servicemanager
    from win_service import AppServerSvc
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppServerSvc)


if __name__ == '__main__':
    os.makedirs(config['log_dir'], exist_ok=True)
    if sys.platform.startswith('linux') or 'ython' in sys.argv[0]:
        linux_main()
    elif sys.platform.startswith('win32'):
        freeze_support()
        # init()
        win32_main()
