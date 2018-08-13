import sys
import os


if sys.platform.startswith('linux') or 'ython' in sys.argv[0]:
    path = './'
    log_dir = os.path.join(path, 'log')
    data_dir = os.path.join(path, 'data')
elif sys.platform.startswith('win32'):
    path = os.path.dirname(sys.executable)
    log_dir = os.path.join(path, '../log')
    data_dir = os.path.join(path, '../data')

config = {
    'db': {
        'addr': os.path.join(path, 'nams.db'),
        'db_type': 'sqlite3'
    },
    'miner_type': 'avalon7',
    'thread_num': 4,
    'port': 4139,
    'path': path,
    'log_dir': log_dir,
    'data_dir': data_dir,
    'version': '1.0',
}
