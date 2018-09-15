'''
Name:		rpi_processframework.py
Purpose:	RPiProcessFramework is used to define a parent class
            for homedomotica processes running on the raspberry pi
            This framework implements all common components of the
            homedomotca processes including:
            - creation of an input queue
            - creation of the logger instance
            - creation of the process attribute dictionary

Author:	Wim

Created:	18/08/2018
Copyright:	(c) Wim 2018
Licence:
'''

import argparse
import time


import rpi_logger
from rpi_processattributes import RPiProcessAttributes
from rpi_homedomoticaconfigurationfile import RPiHomedomoticaConfigurationFile
from rpi_messageconsumer import RPiMessageConsumer

class RPiProcessFramework():
    '''
    This class is created to handle the Input Buttons available on a piface board
    Following attributes are defined:
        - logger_instance => handle to the logger
        - run_process => boolean to indicate if process should be running
        - process_attributes => dictionary containing all attribues used by this process
          including following keys:
            - ProcessName
            - InputQueueName
            - All entries provided in the process configuration file in block "[<process name>]"
        - process_input_queue => Handle to the input queue message processor
    '''

    def __init__(self,                                                          # pylint: disable=too-many-arguments
                 default_log_level='INFO',
                 default_log_file="/var/log/homedomotica/RPiHomedomotica.log",
                 default_log_to_console_enabled=False,
                 default_log_to_file_enabled=True,
                 default_log_to_syslog_enabled=False):

        # Set variable to indicate the process should be running
        self.run_process = True

        #Initiate process attribute dictionary
        self.process_attributes = RPiProcessAttributes()

        # Parse command line arguments
        parser = argparse.ArgumentParser()

        # => Push process name to process attribute dictionary
        self.process_attributes.push_item({"ProcessName": parser.prog[:-3]})

        # => check if an input queue name is provided as a parameter.
        #If not, use process name as basis for the queue name
        parser.add_argument(
            "-q",
            nargs="?",
            type=str,
            const="IQ_"+str.upper(self.process_attributes.get_item("ProcessName")),
            default="IQ_"+str.upper(self.process_attributes.get_item("ProcessName")),
            action="store",
            dest="input_queue_name",
            help="Input queue name (default is set to the process name, prefixed by IQ_"
            )
        # => check if a name for the configuration file is provided as a parameter.
        #If not, use the default name <process_name>.cfg
        parser.add_argument(
            "-cf",
            nargs="?",
            type=str,
            const=self.process_attributes.get_item("ProcessName") + ".cfg",
            default=self.process_attributes.get_item("ProcessName") + ".cfg",
            action="store",
            dest="config_file_name",
            help="Name of the process configuration file (Deault value is <process name>.cfg)."
            )
        # => check if a location for the configuration file is provided as a parameter.
        #If not, use the default location /home/homedomotica
        parser.add_argument(
            "-cfp",
            nargs="?",
            type=str,
            const="/home/homedomotica",
            default="/home/homedomotica",
            action="store",
            dest="config_file_path",
            help="Path to the process configuration file (Deault value is /home/homedomotica)."
            )
        # => check if a log level is provided as a parameter.
        #If not, use the default log level 'INFO'
        parser.add_argument(
            "-l",
            nargs="?",
            type=str,
            choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
            action="store",
            dest="process_log_level",
            help="Process log level (Deault value is 'INFO')."
            )

        if parser.parse_args().process_log_level:
            default_log_level = parser.parse_args().process_log_level

        # Initiate Logger function so we can start logging stuff
        self.logger_instance = rpi_logger.RPiLogger(default_log_level,
                                                    default_log_file,
                                                    default_log_to_console_enabled,
                                                    default_log_to_file_enabled,
                                                    default_log_to_syslog_enabled)

        # Tell the logger we are starting
        self.logger_instance.info("{} - Process Starting!".format(__name__))

        # Send process name information to the logger
        self.logger_instance.debug(
            "{} - Push 'ProcessName = {}' to process attribute dictionary".format(
                __name__,
                parser.prog[:-3])
            )

        # Add the parameters to the process attributes dictionary
        self.process_attributes.push_item({"InputQueueName": parser.parse_args().input_queue_name})
        self.logger_instance.debug(
            "{} - Push 'InputQueueName = {}' to process attribute dictionary".format(
                __name__,
                self.process_attributes.get_item("InputQueueName")
                )
            )
        self.process_attributes.push_item(
            {"ConfigFileName": str.lower(parser.parse_args().config_file_name)})
        self.logger_instance.debug(
            "{} - Push 'ConfigFileName = {}' to process attribute dictionary".format(
                __name__,
                self.process_attributes.get_item("ConfigFileName")
                )
            )
        self.process_attributes.push_item({"ConfigFilePath": parser.parse_args().config_file_path})
        self.logger_instance.debug(
            "{} - Push 'ConfigFilePath = {}' to process attribute dictionary".format(
                __name__,
                self.process_attributes.get_item("ConfigFilePath")
                )
            )
        self.process_attributes.push_item(
            {"ProcessLogLevel": parser.parse_args().process_log_level})
        self.logger_instance.debug(
            "{} - Push 'ProcessLogLevel = {}' to process attribute dictionary".format(
                __name__,
                self.process_attributes.get_item("ProcessLogLevel")
                )
            )

        # Initialize process configuration file
        # Name of the config file is set to the process name (lower case) and file extension .cfg
        self.config_file = RPiHomedomoticaConfigurationFile(
            file_name=self.process_attributes.get_item("ConfigFileName"),
            file_path=self.process_attributes.get_item("ConfigFilePath"))
        self.refresh_process_attributes()

        # Initialize Input Queue so we can receive messages
        input_queue_configuration = {'queueName':\
                                        self.process_attributes.get_item("InputQueueName"),
                                     'routingKey':\
                                        self.process_attributes.get_item("InputQueueName"),
                                     'exchangeName': 'HOMEDOMOTICA',
                                     'host': 'localhost',
                                     'exchangeType': 'direct',
                                     'exchangePassive': False,
                                     'exchangeDurable': True,
                                     'exchangeAutoDelete': False,
                                     'exchangeInternal': False,
                                     'queuePassive': False,
                                     'queueDurable': False,
                                     'queueExclusive': False,
                                     'queueAutoDelete': False,
                                     'sleepTime': 0.1}
        self.process_input_queue = RPiMessageConsumer(
            input_queue_configuration)

    def __del__(self):
        self.logger_instance.info("{} - Process Stopping!".format(__name__))

    def __str__(self):
        long_string = ""
        long_string += "Process Name: {}\n".format(self.process_attributes.get_item("ProcessName"))
        long_string += "Input Queue Name: {}\n".format(
            self.process_attributes.get_item("InputQueueName"))
        long_string += self.logger_instance.__str__()
        long_string += self.config_file.__str__()
        long_string += self.process_attributes.__str__()
        return long_string

    def __repr__(self):
        long_string = ""
        long_string += self.process_attributes.get_item("ProcessName") + " " +\
                       str(self.run_process) + " " +\
                       self.process_attributes.get_item("InputQueueName")
        return long_string

    def process_message(self, message): # pylint: disable=too-many-branches
        '''
        Function responsible to handle messages coming from the process
        input queue which are specific to the process.
        Valid message, passed as a parameter are:
        - STOP => stop the process
        - ENABLE_CONSOLE_LOGGING
        - ENABLE_LOGFILE_LOGGING
        - ENABLE_SYSLOG_LOGGING
        - DISABLE_CONSOLE_LOGGING
        - DISABLE_LOGFILE_LOGGING
        - DISABLE_SYSLOG_LOGGING
        - SET_LOG_LEVEL
        - PRINT_PROCESS_STATUS
        - REFRESH_PROCESS_ATTRIBUTES
        other messages are ignored
        Return value:
        - True: No STOP event received
        - False: STOP event received
        '''

        reply = True   # Assuming we don't need to stop processing

        message_list = message.split(";")
        if message_list[0] == "P":  # We first check it is an actual process message
            if message_list[1] == "STOP":
                reply = False
            elif message_list[1] == "ENABLE_CONSOLE_LOGGING":
                self.logger_instance.enable_console_logging()
            elif message_list[1] == "DISABLE_CONSOLE_LOGGING":
                self.logger_instance.disable_console_logging()
            elif message_list[1] == "ENABLE_LOGFILE_LOGGING":
                self.logger_instance.enable_logfile_logging()
            elif message_list[1] == "DISABLE_LOGFILE_LOGGING":
                self.logger_instance.disable_logfile_logging()
            elif message_list[1] == "ENABLE_SYSLOG_LOGGING":
                self.logger_instance.enable_syslog_logging()
            elif message_list[1] == "DISABLE_SYSLOG_LOGGING":
                self.logger_instance.disable_syslog_logging()
            elif message_list[1] == "SET_LOG_LEVEL":
                if len(message_list) == 3 and\
                   message_list[2] in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                    self.logger_instance.set_log_level(message_list[2])
            elif message_list[1] == "PRINT_PROCESS_STATUS":
                self.logger_instance.info("Process Status:\n{}".format(self.__str__()))
            elif message_list[1] == "REFRESH_PROCESS_ATTRIBUTES":
                self.refresh_process_attributes()
            else:
                self.logger_instance.warning(
                    "{} - Unknown process message '{}' received on queue {}".format(
                        __name__,
                        message_list[1],
                        self.process_attributes.get_item("InputQueueName")))
                return reply

            self.logger_instance.info(
                "{} - Process message '{}' received on queue {}".format(
                    __name__,
                    message_list[1],
                    self.process_attributes.get_item("InputQueueName")))

        return reply

    def refresh_process_attributes(self):
        '''
        Method to refresh the process attribute dictionary
        -> process name and input queue are retained, all other entries are deleted
        -> attributes from the process configuration file are read from the file
           and added to the dictionary
        '''
        process_name = self.process_attributes.get_item("ProcessName")
        iq_name = self.process_attributes.get_item("InputQueueName")

        self.process_attributes.delete_all_items()
        self.process_attributes.push_item({"ProcessName": process_name})
        self.process_attributes.push_item({"InputQueueName": iq_name})

        # Read configuration file and add all items to the dictionary
        block = "[" + str.upper(self.process_attributes.get_item("ProcessName")) + "]"
        self.process_attributes.push_item(self.config_file.read_configuration_file(block))
        if self.config_file.invalid_config_file is True:
            self.logger_instance.critical(
                "{} - Invalid entries found in config file {} - {}".format(
                    __name__,
                    self.config_file.__repr__(),
                    self.config_file.invalid_keyword_list))
            self.run_process = False    # No need to continue

    def no_message_received_process(self):
        '''
        method that should be implemented in the calling class
        '''
        pass

def main():
    '''
    used mainly for testing purposes
    '''
    process_instance = RPiProcessFramework()
    print(process_instance)

    while process_instance.run_process:
        with process_instance.process_input_queue as consumer:
            process_instance.run_process = consumer.consume(    # pylint: disable=assignment-from-no-return
                process_instance.process_message,
                process_instance.no_message_received_process)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
