'''
Name:		rpi_lightsimulator.py
Purpose:	Class RPiLightSimulator is used to run light simulator scenarios

Author:	Wim

Created:	07/07/2019
Copyright:	(c) Wim 2019
Licence:
'''

import schedule
import time
import json

from rpi_processframework import RPiProcessFramework
from rpi_messagesender import RPiMessageSender


class RPiLightSimulator(RPiProcessFramework):
    '''
    This class is created to handle the simulations of input buttons
    Following attributes are inherited from the RPiProcessFramework class:
        - run_process => boolean to indicate if process should be running
        - process_attributes => dictionary containing all attribues used by this process
          including following keys:
            - ProcessName
            - InputQueueName
        - process_input_queue => Handle to the input queue
        - logger_instance => Handle to the logger instance
    Following attributes are defined in the RPiLightSimulator class:
        - 
        - 
    '''

    def __init__(self):
        # Initialize process framework attributes so we can start using them
        RPiProcessFramework.__init__(self, default_log_level='INFO')

        # Initialize the schedule dictionary
        self.schedule_dict = self.create_schedule_dict(
            self.process_attributes.__repr__())

        # Initialize message sender handles so we can send messages
        self.process_consumers = self.create_message_senders(
            self.process_attributes.__repr__())

        # Initialize the message sender handler
        output_queue_configuration = {'exchangeName': 'HOMEDOMOTICA',
                                      'host': 'localhost'}
        self.process_output_queue_handler = RPiMessageSender(
            output_queue_configuration, self.logger_instance)

    def __del__(self):
        self.logger_instance.info("RPiLightSimulator - Process Stopping!")

    def __str__(self):
        long_string = RPiProcessFramework.__str__(self)

        if self.schedule_dict != {}:
            long_string += "Schedule dictionary:\n"
            for key, value in self.schedule_dict.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No schedule dictionary found!\n"

        if self.process_consumers != {}:
            long_string += "Process consumer dictionary:\n"
            for key, value in self.process_consumers.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No process consumer dictionary found!\n"

        long_string += "Scheduled jobs:\n"
        long_string += str(schedule.jobs)

        return long_string

    def get_activation_date(self, schedule_list):
        '''
        function that retrieves the activation_date from a list entry
        in the schedule dictionary
        '''
        return str(schedule_list[0])

    def get_activation_event(self, schedule_list):
        '''
        function that retrieves the activation_event from a list entry
        in the schedule dictionary
        '''
        return str(schedule_list[1])

    def get_inactivation_date(self, schedule_list):
        '''
        function that retrieves the inactivation_date from a list entry
        in the schedule dictionary
        '''
        return str(schedule_list[2])

    def get_inactivation_event(self, schedule_list):
        '''
        function that retrieves the inactivation_event from a list entry
        in the schedule dictionary
        '''
        return str(schedule_list[3])

    def get_message_queue(self, schedule_list):
        '''
        function that retrieves the message queue from a list entry
        in the schedule dictionary
        '''
        return str(schedule_list[4])

    def create_message_senders(self, process_attribute_list):
        '''
        method to create a consumer queue list based on all consumer entries found
        in the lightsimulator dictionary and the correspondng queue name in the
        process attribute list
        Note: leading and trailing spaces are removed from the key to avoid KeyErrors
        '''
        process_consumer_queue = {}
        for key, value in self.schedule_dict.items():
            for schedule_list in value:
                try:
                    queue = self.get_message_queue(schedule_list)
                    process_consumer_queue[queue] = process_attribute_list[str(
                        queue).lstrip().rstrip()].split()
                    self.logger_instance.debug(
                        "RPiLightSimulator - Initializing message queue {} = {}".format(
                            queue, process_consumer_queue[queue]))
                except Exception:   # pylint: disable=broad-except
                    process_consumer_queue[queue] = []
                    self.logger_instance.warning(
                        "RPiLightSimulator - Invalide queue reference '{}' for scenario '{}'. ".format(
                            queue, key) +
                        "At least 1 queue reference is not created for this scenario! " +
                        "Check {}!".format(str.lower(self.process_attributes.get_item(
                            "ProcessName")) + ".cfg")
                    )

        return process_consumer_queue

    def create_schedule_dict(self, process_attribute_list):
        '''
        This method creates a process logic dictionary based on the scenarios
        defined in the configuration file
        The dictionary key is set to the scenario (first parameter in the config file)
        A scenario can hold multiple actions. Each action is put on a separate line in 
        the configuration file and is tored as a separate list n the dictionary
        Each action has 5 parameters:
        - Date/time to initiate the action
        - Message that can be put on a process queue to initiate the action
        - Date/time to revert the action
        - Message that can be put on a process queue to revert the action
        - Reference to the process queue
        If no scenarios are defined, an empty dictionary is returned
        '''

        reply = {}

        # We will read each Simulation key and add it to the schedule dictionary
        # with the scenario as key
        # It is assumed that the first counter value is 00 and the maximum is 99

        for counter in range(100):
            key = "Simulation" + format(counter, '02')
            if key in process_attribute_list:
                value = process_attribute_list[key]
                if value[0:8] != "Not Used":
                    try:
                        scenario,\
                            activate_time, activate_event,\
                            inactivate_time, inactivate_event,\
                            message_queue = value.split(";")

                        scenario_list_item = [
                            activate_time,
                            activate_event,
                            inactivate_time,
                            inactivate_event,
                            message_queue]

                        if scenario in reply:  # pylint: disable=consider-using-get
                            scenario_list = reply[scenario]
                        else:
                            scenario_list = []

                        scenario_list.append(scenario_list_item)
                        reply[scenario] = scenario_list

                        self.logger_instance.debug(
                            "RPILightSimulator - Adding key {} with value {} to schedule dictionary".
                            format(scenario, reply[scenario]))
                    except KeyError:
                        self.logger_instance.warning(
                            "RPILightSimulator - Unknow scenario found {} -> {}".format(key, value))
                    except ValueError:
                        self.logger_instance.warning(
                            "RPILightSimulator - Invalid scenario information found {} -> {}".format(key, value))

        return reply

    def execute_schedule_job(self, message, message_queue):
        '''
        This job is run for every action triggered in the scheduler
        It will send a message to the message queue
        Note format of a light simulator message is {"Type": "Simulation",
                                                     "Event": <message>}
        '''
        data = {"Type": "Simulation",
                "Event": message}
        json_data = json.dumps(data)
        self.process_output_queue_handler.send_message(
            self.process_consumers[message_queue],
            json_data)
        self.logger_instance.info(
            f"RPILightSimulator - Send {message} event to queue {self.process_consumers[message_queue]}")

    def activate_scenario(self, scenario):
        '''
        Activation of a scenario will add all actions to the schedule queue
        in the list included in the schedule_dict dictionary with 'scenario' as key
        '''

        # To avoid double entries of the same scenario, for example when executing
        # the activate event more than once, clear any existing entries of this scenario
        schedule.clear(scenario)

        for schedule_list in self.schedule_dict[scenario]:
            activation_date = self.get_activation_date(schedule_list)
            activation_event = self.get_activation_event(schedule_list)
            inactivation_date = self.get_inactivation_date(schedule_list)
            inactivation_event = self.get_inactivation_event(schedule_list)
            message_queue = self.get_message_queue(schedule_list)

            activation_days, activation_time = activation_date.split()
            if activation_days == '*':
                schedule.every().day.at(activation_time).do(self.execute_schedule_job,
                                                            activation_event,
                                                            message_queue).tag(scenario)
                self.logger_instance.debug(
                    "RPILightSimulator - activating message {} every day at {} to {}".format(
                        activation_event,
                        activation_time,
                        message_queue))
            else:
                for day in activation_days.split(','):
                    if day == "Monday":
                        schedule.every().monday.at(activation_time).do(self.execute_schedule_job,
                                                                       activation_event,
                                                                       message_queue).tag(scenario)
                    elif day == "Tuesday":
                        schedule.every().tuesday.at(activation_time).do(self.execute_schedule_job,
                                                                        activation_event,
                                                                        message_queue).tag(scenario)
                    elif day == "Wednesday":
                        schedule.every().wednesday.at(activation_time).do(self.execute_schedule_job,
                                                                          activation_event,
                                                                          message_queue).tag(scenario)
                    elif day == "Thursday":
                        schedule.every().thursday.at(activation_time).do(self.execute_schedule_job,
                                                                         activation_event,
                                                                         message_queue).tag(scenario)
                    elif day == "Friday":
                        schedule.every().friday.at(activation_time).do(self.execute_schedule_job,
                                                                       activation_event,
                                                                       message_queue).tag(scenario)
                    elif day == "Saterday":
                        schedule.every().saturday.at(activation_time).do(self.execute_schedule_job,
                                                                         activation_event,
                                                                         message_queue).tag(scenario)
                    elif day == "Sunday":
                        schedule.every().sunday.at(activation_time).do(self.execute_schedule_job,
                                                                       activation_event,
                                                                       message_queue).tag(scenario)
                    self.logger_instance.debug(
                        "RPILightSimulator - activating message {} every {} at {} to {}".format(
                            activation_event,
                            day,
                            activation_time,
                            message_queue))

            inactivation_days, inactivation_time = inactivation_date.split()
            if inactivation_days == '*':
                schedule.every().day.at(inactivation_time).do(self.execute_schedule_job,
                                                              inactivation_event,
                                                              message_queue).tag(scenario)
                self.logger_instance.debug(
                    "RPILightSimulator - activating message {} every day at {} to {}".format(
                        inactivation_event,
                        inactivation_time,
                        message_queue))
            else:
                for day in inactivation_days.split(','):
                    if day == "Monday":
                        schedule.every().monday.at(inactivation_time).do(self.execute_schedule_job,
                                                                         inactivation_event,
                                                                         message_queue).tag(scenario)
                    elif day == "Tuesday":
                        schedule.every().tuesday.at(inactivation_time).do(self.execute_schedule_job,
                                                                          inactivation_event,
                                                                          message_queue).tag(scenario)
                    elif day == "Wednesday":
                        schedule.every().wednesday.at(inactivation_time).do(self.execute_schedule_job,
                                                                            inactivation_event,
                                                                            message_queue).tag(scenario)
                    elif day == "Thursday":
                        schedule.every().thursday.at(inactivation_time).do(self.execute_schedule_job,
                                                                           inactivation_event,
                                                                           message_queue).tag(scenario)
                    elif day == "Friday":
                        schedule.every().friday.at(inactivation_time).do(self.execute_schedule_job,
                                                                         inactivation_event,
                                                                         message_queue).tag(scenario)
                    elif day == "Saterday":
                        schedule.every().saturday.at(inactivation_time).do(self.execute_schedule_job,
                                                                           inactivation_event,
                                                                           message_queue).tag(scenario)
                    elif day == "Sunday":
                        schedule.every().sunday.at(inactivation_time).do(self.execute_schedule_job,
                                                                         inactivation_event,
                                                                         message_queue).tag(scenario)
                    self.logger_instance.debug(
                        "RPILightSimulator - activating message {} every {} at {} to {}".format(
                            inactivation_event,
                            day,
                            inactivation_time,
                            message_queue))

    def deactivate_scenario(self, scenario):
        '''
        Deactivating a scenario will remove all entries in the schedule queue that
        match the schedule Tag with the scenario.
        '''
        schedule.clear(scenario)
        self.logger_instance.info(
            "RPILightSimulator - Deactivating scheduler for scenario {}".format(scenario))

    def parse_simulation_message(self, message):
        '''
        Method responsible to parse an incomming simulation message
        Valid actions:
        - ACTIVATE
        - DEACTIVATE
        Other actions are ignored

        These actions are expected to be passed with 1 parameter.
        This parameter represents the scenario to be activated.

        Correct syntax of the message is "ACTIVATE|<scenario>" or
        "DEACTIVATE|<scenario>"
        '''
        try:
            self.logger_instance.debug(
                "RPILightSimulator - Parsing message {}".format(message))
            simulation_action, simulation_scenario = message.split('|')
            if simulation_action == "ACTIVATE":
                self.activate_scenario(simulation_scenario)
                self.logger_instance.debug(
                    "RPILightSimulator - Activating scenario {}".format(
                        simulation_scenario))
            elif simulation_action == "DEACTIVATE":
                self.deactivate_scenario(simulation_scenario)
                self.logger_instance.debug(
                    "RPILightSimulator - Deactivating scenario {}".format(
                        simulation_scenario))
            else:
                self.logger_instance.warning(
                    "RPILightSimulator - Unknow simulation action received {} - skipping".format(
                        simulation_action))
        except KeyError:
            self.logger_instance.warning(
                "RPILightSimulator - Unknow simulation event received {} - skipping".format(message))
        except ValueError:
            self.logger_instance.warning(
                "RPILightSimulator - Invalid simulation event received {} - skipping".format(message))

    def process_message(self, message):
        '''
        Function responsible to handle messages coming from the process
        input queue. The message is passed as a parameter.
        Return value:
        - True: No STOP event received
        - False: STOP event received
        '''
        reply = True    # We assume we keep going

        self.logger_instance.debug(
            f"RPiLightSimulator - Processing Message {message}")

        event_message = json.loads(message)
        # A process related message was received
        if event_message["Type"] == "Processing":
            reply = super().process_message(message)
            # When the process attribute list has been refreshed
            # It's also necessary to refresh the lightsimulator list to process any
            # changes
            if reply is True and event_message["Event"] == 'REFRESH_PROCESS_ATTRIBUTES':
                self.logger_instance.debug(
                    f"RPiLightSimulator - {event_message['Event']} event received")
                self.schedule_dict = self.create_schedule_dict(
                    self.process_attributes.__repr__())
                self.process_consumers = self.create_message_senders(
                    self.process_attributes.__repr__())
        # A Simulation message was received
        elif event_message["Type"] == "Simulation":
            self.logger_instance.debug(
                f"RPILightSimulator - Parsing Simulation event - {event_message['Event']}")
            self.parse_simulation_message(event_message['Event'])

        return reply

    def process_simulation_message(self):
        '''
        Method that is called when no messages are received via the input queue.
        We start by sleeping a bit
        and then continue with any scheduled task in the scheduler queue
        '''
        time.sleep(0.5)
        schedule.run_pending()


def main():
    '''
    Initiating the RPiLightSimulator process
    '''
    lightsimulator_handler_instance = RPiLightSimulator()

    while lightsimulator_handler_instance.run_process:
        with lightsimulator_handler_instance.process_input_queue as consumer:
            lightsimulator_handler_instance.run_process = consumer.consume(  # pylint: disable=assignment-from-no-return
                lightsimulator_handler_instance.process_message,
                lightsimulator_handler_instance.process_simulation_message)


if __name__ == '__main__':
    main()
