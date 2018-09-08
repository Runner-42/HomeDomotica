'''
Name:		RPiLogger.py
Purpose:	The Logger class is used a wrapper to handle all logging activities
            based on the build-in logging module

Author:	    Wim

Created:	29/05/2018
Copyright:	(c) Wim 2018
Licence:
'''

import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
import sys

# Define formater structure as Constants
CONSOLE_FORMATTER = '%(levelname)s: %(message)s'
LOGFILE_FORMATTER = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
SYSLOG_FORMATTER = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"

class RPiLogger(): # pylint: disable=too-many-arguments
    '''
    This class is created to handle the logging functionality for
    all homedomotica modules and processes. Available log levels:

    DEBUG (10)    Detailed information, typically of interest only when
                  diagnosing problems.
    INFO (20)     Confirmation that things are working as expected.
    WARNING (30)  An indication that something unexpected happened, or
                  indicative of some problem in the near future
                  (e.g. ‘disk space low’). The software is still working
                  as expected.
    ERROR (40)	  Due to a more serious problem, the software has not been
                  able to perform some function.
    CRITICAL (50) A serious error, indicating that the program itself may
                  be unable to continue running.
    '''

    def __init__(self, default_log_level=logging.INFO, # pylint: disable=too-many-arguments
                 default_log_file="/var/log/homedomotica/RPiHomedomotica.log",
                 default_log_to_console_enabled=False,
                 default_log_to_file_enabled=False,
                 default_log_to_syslog_enabled=False):
        if isinstance(default_log_level, str):
            if default_log_level == "WARNING":
                self._log_level = logging.WARNING
            elif default_log_level == "ERROR":
                self._log_level = logging.ERROR
            elif default_log_level == "DEBUG":
                self._log_level = logging.DEBUG
            elif default_log_level == "CRITICAL":
                self._log_level = logging.CRITICAL
            else:
                self._log_level = logging.INFO
        elif isinstance(default_log_level, int):
            self._log_level = default_log_level
        else:
            self._log_level = logging.INFO

        self._log_file = default_log_file

        # Initialize Handlers
        self.console_handler = None         # Console Handler
        self.log_file_handler = None        # Log File Handler
        self.syslog_handler = None          # Syslog Handler

        # Initialize Logger
        self._homedomotica_logger = logging.getLogger('HomeDomotica')
        self._homedomotica_logger.level = self._log_level
        if default_log_to_console_enabled:
            self.enable_console_logging()
        if default_log_to_file_enabled:
            self.enable_logfile_logging()
        if default_log_to_syslog_enabled:
            self.enable_syslog_logging()

    # Standard Methods
    def __repr__(self):
        if self.console_handler is None:
            log_to_console_enabled = False
        else:
            log_to_console_enabled = True

        if self.log_file_handler is None:
            log_to_file_enabled = False
        else:
            log_to_file_enabled = True

        if self.syslog_handler is None:
            log_to_syslog_enabled = False
        else:
            log_to_syslog_enabled = True

        return str(self._log_level) + ' ' + \
               self._log_file + ' ' + \
               str(log_to_console_enabled) + ' ' + \
               str(log_to_file_enabled) + ' ' + \
               str(log_to_syslog_enabled)

    def __str__(self):
        _return_string = ""

        if self._log_level == 10:
            log_level = "DEBUG"
        elif self._log_level == 20:
            log_level = "INFO"
        elif self._log_level == 30:
            log_level = "WARNING"
        elif self._log_level == 40:
            log_level = "ERROR"
        else:
            log_level = "CRITICAL"

        if self.console_handler is None:
            log_to_console_enabled = False
        else:
            log_to_console_enabled = True

        if self.log_file_handler is None:
            log_to_file_enabled = False
        else:
            log_to_file_enabled = True

        if self.syslog_handler is None:
            log_to_syslog_enabled = False
        else:
            log_to_syslog_enabled = True

        _return_string = "Log file name: {}\n".format(self._log_file) + \
                         "Log level: {} ({})\n".format(self._log_level, log_level) + \
                         "Log to Console enabled: {}\n".format(log_to_console_enabled) + \
                         "Log to file enabled: {}\n".format(log_to_file_enabled) + \
                         "Log to Syslog enabled: {}\n".format(log_to_syslog_enabled)
        return _return_string

    # Other Methods
    def set_log_level(self, log_level):
        '''
        set_log_level is used to assign a proper log level value to the _log_level class attribute
        as well as the _homedomotica_logger class
        '''

        if isinstance(log_level, str):
            if log_level == "WARNING":
                self._log_level = logging.WARNING
            elif log_level == "ERROR":
                self._log_level = logging.ERROR
            elif log_level == "DEBUG":
                self._log_level = logging.DEBUG
            elif log_level == "CRITICAL":
                self._log_level = logging.CRITICAL
            else:
                self._log_level = logging.INFO
        elif isinstance(log_level, int):
            self._log_level = log_level
        else:
            self._log_level = logging.INFO

        self._homedomotica_logger.level = self._log_level

    def set_log_file(self, log_file="/var/log/RPiHomedomotica.log"):
        '''
        set_log_file is a setter method for the _log_file attribute
        '''
        self._log_file = log_file

    def get_log_file(self):
        '''
        get_log_file is a getter method for the _log_file attribute
        '''
        return self._log_file

    def get_log_level(self):
        '''
        get_log_level is a getter method for the log level set
        in the _homedomotica_logger class
        '''
        return self._homedomotica_logger.getEffectiveLevel()

    def enable_logfile_logging(self):
        '''
        Function that enables logging to logfile
        the name of the logfile should be set using the appropriate setter function
        log files will be rotating with a maximum size of 100000 bytes per file
        A maximum of 10 log files are retained
        '''
        formatter = logging.Formatter(LOGFILE_FORMATTER)

        self.log_file_handler = RotatingFileHandler(self.get_log_file(),
                                                    maxBytes=100000,
                                                    backupCount=10)
        self.log_file_handler.setFormatter(formatter)
        self._homedomotica_logger.addHandler(self.log_file_handler)

    def disable_logfile_logging(self):
        '''
        Function that disables logging to logfile
        '''
        self._homedomotica_logger.removeHandler(self.log_file_handler)
        self.log_file_handler = None

    def enable_syslog_logging(self):
        '''
        Function that enables logging to syslog
        '''
        formatter = logging.Formatter(SYSLOG_FORMATTER)

        self.syslog_handler = SysLogHandler(address='/dev/log')
        self.syslog_handler.setLevel(logging.ERROR)
        self.syslog_handler.setFormatter(formatter)
        self._homedomotica_logger.addHandler(self.syslog_handler)

    def disable_syslog_logging(self):
        '''
        Function that disables logging to syslog
        '''
        self._homedomotica_logger.removeHandler(self.syslog_handler)
        self.syslog_handler = None

    def enable_console_logging(self):
        '''
        Function that enables logging to console
        '''
        formatter = logging.Formatter(CONSOLE_FORMATTER)

        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(formatter)
        self._homedomotica_logger.addHandler(self.console_handler)

    def disable_console_logging(self):
        '''
        Function that disables logging to console
        '''
        self._homedomotica_logger.removeHandler(self.console_handler)
        self.console_handler = None

    def info(self, message):
        '''
        The info method is used to log an "INFO" message
        to the _homedomotica_logger handlers
        '''
        self._homedomotica_logger.info(message)

    def debug(self, message):
        '''
        The debug method is used to log a "DEBUG" message
        to the _homedomotica_logger handlers
        '''
        self._homedomotica_logger.debug(message)

    def warning(self, message):
        '''
        The warning method is used to log a "WARNING" message
        to the _homedomotica_logger handlers
        '''
        self._homedomotica_logger.warning(message)

    def error(self, message):
        '''
        The error method is used to log an "ERROR" message
        to the _homedomotica_logger handlers
        '''
        self._homedomotica_logger.error(message)

    def critical(self, message):
        '''
        The critical method is used to log a "CRITICAL" message
        to the _homedomotica_logger handlers
        '''
        self._homedomotica_logger.critical(message)


def main():
    '''
    main function used mainly for testing purposes
    '''
    print("Hello world")
    logger_instance = RPiLogger('DEBUG', '/tmp/wimpie.log')
    print(logger_instance.__str__())
    logger_instance.info("info testje")
    logger_instance.error("error testje")
    logger_instance.critical("critical testje")
    logger_instance.warning("warning testje")
    logger_instance.debug("debug testje")
    print("Bye world")

if __name__ == '__main__':
    main()
