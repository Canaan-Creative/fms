import socket
import json

from data import Data


class Controller():
    def __init__(self, ip, passwd, miner_type, miner_port=4028,
                 luci_port=80, https_enable=False,
                 tty_port=22, ssh_enable=True):
        self.ip = ip
        self.passwd = passwd
        self.miner_port = miner_port
        self.luci_port = luci_port
        self.https_enable = https_enable
        self.tty_port = tty_port
        self.ssh_enable = ssh_enable
        self.cgminer = CGMiner(self.ip, self.miner_port)
        self.miner_type = miner_type

    def collect(self, timestamp, logger):
        logger.info('collect start %s', self.ip)
        self.cgminer.run(logger, 'debug', 'D')
        d = {'timestamp': timestamp}
        for c in ['summary', 'edevs', 'estats', 'pools']:
            d[c] = self.cgminer.run(logger, c)
            logger.info('collect: %s, %s, %s', self.ip, c, d[c])
        self.cgminer.run(logger, 'debug', 'D')
        data = Data(ip=self.ip, miner_type=self.miner_type, **d)
        logger.info('collect end %s', self.ip)
        return data


class CGMiner():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def run(self, logger, command, parameter=None, timeout=1):
        if parameter is None:
            request = '{{"command": "{}"}}'.format(command)
        else:
            request = '{{"command": "{}", "parameter": "{}"}}'.format(
                command, parameter)

        logger.info('miner %s, request %s', self.ip, request)
        addlist = []
        retry = 3
        while len(addlist) == 0 and retry > 0:
            try:
                addlist = socket.getaddrinfo(
                    self.ip,
                    self.port,
                    socket.AF_UNSPEC,
                    socket.SOCK_STREAM)
            except Exception as e:
                logger.info('miner %s, request %s, except: %s', self.ip, request, repr(e))
                retry = retry - 1

        for res in addlist:
            logger.info('miner %s, request %s addr, %s', self.ip, request, str(res))
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except (socket.error, ConnectionError):
                s = None
                continue
            logger.info('miner %s, request %s create socket', self.ip, request)
            s.settimeout(timeout)
            try:
                s.connect(sa)
                logger.info('miner %s, request %s socket connected', self.ip, request)
            except (socket.error, ConnectionError):
                logger.info('miner %s, request %s connect error', self.ip, request)
                s.close()
                s = None
                continue
            break
        if s is None:
            logger.info('miner %s socket error', self.ip)
            raise socket.error
        s.sendall(request.encode())
        response = s.recv(32768)
        while True:
            recv = s.recv(32768)
            if not recv:
                break
            else:
                response += recv

        logger.info('miner %s response %s', self.ip, response)
        response = ''.join(
            [x if ord(x) >= 32 else '' for x in response.decode()])

        logger.info('miner %s joined response %s', self.ip, response)
        obj = json.loads(response)
        logger.info('miner %s json load %s', json.dumps(obj))
        s.close()
        return obj
