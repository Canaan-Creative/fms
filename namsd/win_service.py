import socket
import configparser
import os
import logging
import subprocess
from subprocess import Popen

import win32serviceutil
import win32service
import win32event
import servicemanager

from namsd import init
from config import config
import logger


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "NAMS Service"
    _svc_display_name_ = "NAMS Service"

    _config = configparser.ConfigParser()

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.hWaitCollect = win32event.CreateEvent(None, 0, 0, "Global\\CollectEvent")
        socket.setdefaulttimeout(60)

        self._logger = logger.create_rotate_logger("NAMSD", logging.DEBUG, "service.log")

    def SvcStop(self):
        try:
            self.stop_process(self.api_process.pid)
            self.stop_process(self.collect_process.pid)
        except Exception:
            pass
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))

        self._logger.info("Service is starting")

        self.main()

    def start_process(self, args):
        return Popen(args)

    def stop_process(self, pid):
        subprocess.call(
            ['taskkill', '/F', '/T', '/PID', str(pid)])

    def main(self):
        try:
            init()
        except Exception as e:
            self._logger.info("init exception", e)

        self.api_process = self.start_process(
            [os.path.join(config['path'], 'api.exe')])
        self.collect_process = self.start_process(
            [os.path.join(config['path'], 'collect.exe')])

        while True:
            handles = [self.hWaitStop, self.hWaitCollect]
            rc = win32event.WaitForMultipleObjects(handles, 0, win32event.INFINITE)
            self._logger.info('event received, %d', rc)
            if rc == win32event.WAIT_OBJECT_0:
                break
            elif rc == win32event.WAIT_OBJECT_0+1:
                try:
                    self.stop_process(self.collect_process.pid)
                except:
                    pass
                self.collect_process = self.start_process(
                    [os.path.join(config['path'], 'collect.exe')])
                win32event.ResetEvent(self.hWaitCollect)
