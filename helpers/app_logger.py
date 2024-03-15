import logging
import socket
from logging.handlers import SysLogHandler

class LoggerFactory:
    def __init__(self, app_name, syslog_address, syslog_port):
        self.app_name = app_name
        self.syslog_address = syslog_address
        self.syslog_port = syslog_port

    class ContextFilter(logging.Filter):
        hostname = socket.gethostname()

        def filter(self, record):
            record.hostname = self.hostname
            return True

    def get_logger(self):
        # Create SysLogHandler
        syslog = SysLogHandler(address=(self.syslog_address, self.syslog_port))
        syslog.addFilter(self.ContextFilter())

        # Formatter
        format = '%(asctime)s %(hostname)s ' + self.app_name + ': %(message)s'
        formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
        syslog.setFormatter(formatter)

        # Logger setup
        logger = logging.getLogger(self.app_name)
        logger.addHandler(syslog)
        logger.setLevel(logging.INFO)  # Default level, can be changed later

        return logger