import datetime
import os

import config


COLUMN_CONTROLLERS = {
    'time':                     'TIMESTAMP',
    'ip':                       'VARCHAR(40)',
    'precise_time':             'BIGINT',
    'elapsed':                  'BIGINT',
    'mhs_av':                   'DOUBLE',
    'mhs_5s':                   'DOUBLE',
    'mhs_1m':                   'DOUBLE',
    'mhs_5m':                   'DOUBLE',
    'mhs_15m':                  'DOUBLE',
    'mhs':                      'DOUBLE',
    'found_blocks':             'INT UNSIGNED',
    'new_blocks':               'INT UNSIGNED',
    'getworks':                 'BIGINT',
    'accepted':                 'BIGINT',
    'rejected':                 'BIGINT',
    'hardware_errors':          'INT',
    'utility':                  'DOUBLE',
    'discarded':                'BIGINT',
    'stale':                    'BIGINT',
    'get_failures':             'INT UNSIGNED',
    'local_work':               'INT UNSIGNED',
    'remote_failures':          'INT UNSIGNED',
    'network_blocks':           'INT UNSIGNED',
    'total_mh':                 'DOUBLE',
    'work_utility':             'DOUBLE',
    'difficulty_accepted':      'DOUBLE',
    'difficulty_rejected':      'DOUBLE',
    'difficulty_stale':         'DOUBLE',
    'best_share':               'BIGINT UNSIGNED',
    'device_hardware':          'DOUBLE',
    'device_rejected':          'DOUBLE',
    'pool_rejected':            'DOUBLE',
    'pool_stale':               'DOUBLE',
    'last_getwork':             'BIGINT'}

COLUMN_POOLS = {
    'time':                     'TIMESTAMP',
    'ip':                       'VARCHAR(40)',
    'precise_time':             'BIGINT',
    'pool_id':                  'TINYINT UNSIGNED',
    'pool':                     'INT',
    'url':                      'VARCHAR(64)',
    'status':                   'CHAR(1)',
    'priority':                 'INT',
    'quota':                    'INT',
    'bad_work':                 'INT',
    'long_poll':                'CHAR(1)',
    'getworks':                 'INT UNSIGNED',
    'accepted':                 'BIGINT',
    'rejected':                 'BIGINT',
    'works':                    'INT',
    'discarded':                'INT UNSIGNED',
    'stale':                    'INT UNSIGNED',
    'get_failures':             'INT UNSIGNED',
    'remote_failures':          'INT UNSIGNED',
    'user':                     'VARCHAR(32)',
    'last_share_time':          'BIGINT',
    'diff1_shares':             'BIGINT',
    'proxy_type':               'VARCHAR(32)',
    'proxy':                    'VARCHAR(64)',
    'difficulty_accepted':      'DOUBLE',
    'difficulty_rejected':      'DOUBLE',
    'difficulty_stale':         'DOUBLE',
    'last_share_difficulty':    'DOUBLE',
    'work_difficulty':          'DOUBLE',
    'has_stratum':              'BOOL',
    'stratum_active':           'BOOL',
    'stratum_difficulty':       'BIGINT UNSIGNED',
    'stratum_url':              'VARCHAR(64)',
    'has_gbt':                  'BOOL',
    'best_share':               'BIGINT UNSIGNED',
    'pool_rejected':            'DOUBLE',
    'pool_stale':               'DOUBLE'}

COLUMN_DEVICES = {}
COLUMN_MODULES = {}

COLUMN_DEVICES['avalon7'] = {
    'time':                     'TIMESTAMP',
    'ip':                       'VARCHAR(40)',
    'precise_time':             'BIGINT',
    'device_id':                'SMALLINT UNSIGNED',
    'asc':                      'INT',
    'name':                     'CHAR(3)',
    'enabled':                  'CHAR(1)',
    'status':                   'CHAR(1)',
    'temperature':              'DOUBLE',
    'mhs_av':                   'DOUBLE',
    'mhs_5s':                   'DOUBLE',
    'mhs_1m':                   'DOUBLE',
    'mhs_5m':                   'DOUBLE',
    'mhs_15m':                  'DOUBLE',
    'accepted':                 'INT',
    'rejected':                 'INT',
    'hardware_errors':          'INT',
    'utility':                  'DOUBLE',
    'last_share_pool':          'INT',
    'last_share_time':          'BIGINT',
    'total_mh':                 'DOUBLE',
    'diff1_work':               'BIGINT',
    'difficulty_accepted':      'DOUBLE',
    'difficulty_rejected':      'DOUBLE',
    'last_share_difficulty':    'DOUBLE',
    'no_device':                'BOOL',
    'last_valid_work':          'BIGINT',
    'device_hardware':          'DOUBLE',
    'device_rejected':          'DOUBLE',
    'device_elapsed':           'BIGINT',
    'mm_count':                 'INT',
    'smart_speed':              'BOOL',
    'automatic_voltage':        'BOOL',
    'auc_ver':                  'CHAR(12)',
    'auc_i2c_speed':            'INT',
    'auc_i2c_xdelay':           'INT',
    'auc_sensor':               'INT',
    'auc_temperature':          'DOUBLE',
    'usb_pipe':                 'VARCHAR(32)',
    'usb_delay':                'VARCHAR(32)',
    'usb_tmo':                  'VARCHAR(32)'}

COLUMN_MODULES['avalon7'] = {
    'time':         'TIMESTAMP',
    'ip':           'VARCHAR(40)',
    'precise_time': 'BIGINT',
    'device_id':    'SMALLINT UNSIGNED',
    'module_id':    'TINYINT UNSIGNED',
    'ver':          'CHAR(15)',
    'dna':          'CHAR(16)',
    'elapsed':      'BIGINT',
    'lw':           'BIGINT',
    'hw':           'BIGINT',
    'dh':           'DOUBLE',
    'temp':         'INT',
    'tmax':         'INT',
    'fan':          'INT',
    'fanr':         'INT',
    'ghsmm':        'DOUBLE',
    'wu':           'DOUBLE',
    'freq':         'DOUBLE',
    'pg':           'SMALLINT UNSIGNED',
    'led':          'BOOL',
    'ta':           'SMALLINT UNSIGNED',
    'ecmm':         'SMALLINT UNSIGNED',
    'fac0':         'SMALLINT',
    'fm':           'SMALLINT UNSIGNED',
    'pmuv_0':       'CHAR(4)',
    'pmuv_1':       'CHAR(4)'}

for i in range(4):
    COLUMN_MODULES['avalon7']['pvt_t_{}'.format(i)] = 'VARCHAR(18)'
    COLUMN_MODULES['avalon7']['mv_{}'.format(i)] = 'INT'
    COLUMN_MODULES['avalon7']['mh_{}'.format(i)] = 'INT'
    COLUMN_MODULES['avalon7']['vi_{}'.format(i)] = 'INT'
    COLUMN_MODULES['avalon7']['vo_{}'.format(i)] = 'INT'
    COLUMN_MODULES['avalon7']['echu_{}'.format(i)] = 'INT'
    COLUMN_MODULES['avalon7']['crc_{}'.format(i)] = 'INT'

    for j in range(6):
        COLUMN_MODULES['avalon7']['pll{}_{}'.format(i, j)] = 'INT'
        COLUMN_MODULES['avalon7']['sf{}_{}'.format(i, j)] = 'INT'

    for j in range(22):
        COLUMN_MODULES['avalon7']['mw{}_{}'.format(i, j)] = 'INT'
        COLUMN_MODULES['avalon7']['ghsmm0{}_{}'.format(i, j)] = 'DOUBLE'
        COLUMN_MODULES['avalon7']['eratio{}_{}'.format(i, j)] = 'DOUBLE'
        for k in range(5):
            COLUMN_MODULES['avalon7']['c_{}_0{}_{}'.format(i, k, j)] = 'INT'


def convertor(t, d):
    if 'INT' in t:
        return int(d)
    elif 'DOUBLE' in t:
        return float(d)
    elif 'CHAR' in t:
        return str(d)
    elif 'TIMESTAMP' in t:
        # workaround for bug https://bugs.python.org/issue29097
        if d == 0:
            return datetime.datetime(1971, 1, 1, 0, 0)
        return datetime.datetime.fromtimestamp(d)
    elif 'BOOL' in t:
        return bool(t)
    else:
        return d


def get_db_time_format():
    return '%Y-%m-%d %H:%M:%S.%f'


def get_dir_time_format():
    return '{:%y%m%d_%H%M}'


def get_log_dir(timestamp):
    dir = os.path.join(config.config['log_dir'], get_dir_time_format().format(timestamp))
    os.makedirs(dir, exist_ok=True)
    return dir


def get_data_dir(timestamp):
    dir = os.path.join(config.config['data_dir'], get_dir_time_format().format(timestamp))
    return dir


def get_controller_data_file(timestamp):
    return os.path.join(get_data_dir(timestamp), 'controller')


def get_device_data_file(timestamp):
    return os.path.join(get_data_dir(timestamp), 'device')


def get_module_data_file(timestamp):
    return os.path.join(get_data_dir(timestamp), 'module')


def get_pool_data_file(timestamp):
    return os.path.join(get_data_dir(timestamp), 'pool')


COLUMN_PREFERENCES = {
    'pref_key':  'VARCHAR(255)',
    'pref_value':  'VARCHAR(255)'}


PREF_KEY_DEFAULT_VALUE = {
    'controller_module': '5',
    'fan_temp': '30',
    'collect_interval': '5',
    'timestamp': '0',
    'force_update': '1',
    'mhs': '15'
}
