import re

from defs import convertor
from defs import COLUMN_CONTROLLERS
from defs import COLUMN_POOLS
from defs import COLUMN_DEVICES
from defs import COLUMN_MODULES


class Data:
    def __init__(self, ip, miner_type, timestamp,
                 summary, edevs, estats, pools):
        self.ip = ip
        self.timestamp = timestamp
        self.miner_type = miner_type

        self.summary_o = summary
        self.edevs_o = edevs
        self.estats_o = estats
        self.pools_o = pools

        self.controllers = {}
        self.devices = {}
        self.modules = {}
        self.pools = {}

    def fmt_summary(self):
        summary = self.summary_o['SUMMARY'][0]

        self.controllers['precise_time'] = self.summary_o['STATUS'][0]['When']

        for key in summary:
            c = key.strip('%').replace(' ', '_').lower()
            if c in COLUMN_CONTROLLERS:
                self.controllers[c] = convertor(
                    COLUMN_CONTROLLERS[c], summary[key])

    def fmt_pools(self):
        pools = self.pools_o['POOLS']

        precise_time = self.pools_o['STATUS'][0]['When']

        for pool in pools:
            pool_id = pool['POOL']
            self.pools[pool_id] = {
                'precise_time': precise_time}
            for key in pool:
                c = key.strip('%').replace(' ', '_').lower()
                if c in COLUMN_POOLS:
                    self.pools[pool_id][c] = convertor(
                        COLUMN_POOLS[c], pool[key])

    def fmt_edevs(self):
        edevs = self.edevs_o['DEVS']

        precise_time = self.edevs_o['STATUS'][0]['When']

        for edev in edevs:
            device_id = edev['ID']
            if device_id not in self.devices:
                self.devices[device_id] = {
                    'precise_time': precise_time}
            for key in edev:
                c = key.strip('%').replace(' ', '_').lower()
                if c in COLUMN_DEVICES[self.miner_type]:
                    self.devices[device_id][c] = convertor(
                        COLUMN_DEVICES[self.miner_type][c], edev[key])

    def fmt_estats(self, logger):
        estats = self.estats_o['STATS']
        precise_time = self.estats_o['STATUS'][0]['When']

        for device_id, estat in enumerate(estats):
            if device_id not in self.devices:
                self.devices[device_id] = {
                    'precise_time': precise_time}
            self.modules[device_id] = {}
            for key in estat:
                logger.info('key in estat: %s, %s', self.ip, key)
                c = key.strip('%').replace(' ', '_').lower()
                if c in COLUMN_DEVICES[self.miner_type]:
                    self.devices[device_id][c] = convertor(
                        COLUMN_DEVICES[self.miner_type][c], estat[key])
                elif key[:5] == 'MM ID':
                    module_id = int(key[5:])
                    logger.info('found module_id: %s, %d', self.ip, module_id)
                    self.modules[device_id][module_id] = {
                        'precise_time': precise_time}
                    self.fmt_estat(device_id, module_id, estat[key])

    def fmt_estat(self, device_id, module_id, info):
        pattern = re.compile(
            r'(?P<name>[-a-zA-Z_0-9]*)'
            '\[(?P<value>[-._a-zA-Z0-9\s]*)%{0,1}\]')
        for res in pattern.finditer(info):
            key = res['name']
            vs = res['value']
            c = key.strip('%').replace(' ', '_').lower()
            if ' ' in vs:
                i = 0
                for v in vs.split(' '):
                    if v == '':
                        continue
                    name = '{}_{}'.format(c, i)
                    if name in COLUMN_MODULES[self.miner_type]:
                        self.modules[device_id][module_id][name] = convertor(
                            COLUMN_MODULES[self.miner_type][name], v)
                    i += 1
            elif c in COLUMN_MODULES[self.miner_type]:
                self.modules[device_id][module_id][c] = convertor(
                    COLUMN_MODULES[self.miner_type][c], vs)

    def reformat(self, logger):
        self.fmt_summary()
        self.fmt_pools()
        self.fmt_edevs()
        self.fmt_estats(logger)

        self.controllers['ip'] = self.ip
        for p in self.pools:
            self.pools[p]['ip'] = self.ip
            self.pools[p]['pool_id'] = p
        for d in self.devices:
            self.devices[d]['ip'] = self.ip
            self.devices[d]['device_id'] = d
        for d in self.modules:
            for m in self.modules[d]:
                self.modules[d][m]['ip'] = self.ip
                self.modules[d][m]['device_id'] = d
                self.modules[d][m]['module_id'] = m

        return {
            'controllers': self.controllers,
            'devices': self.devices,
            'modules': self.modules,
            'pools': self.pools,
        }
