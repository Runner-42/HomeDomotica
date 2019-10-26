'''
Name:		rpi_outputventilator.py
Purpose:	Class RPiOutputVentilator is used to handle Ventilator devices
            used for example in a bathroom. The Ventilator is controled 
            by the Relays on the PiFace boards

Author:	Wim

Created:	21/10/2019
Copyright:	(c) Wim 2019
Licence:
'''

import time
from rpi_piface import RPiPiface

from rpi_processframework import RPiProcessFramework

class RPiOutputVentilator(RPiProcessFramework, RPiPiface):
    '''
    This class is created to handle the Ventilator objects using the Output Relays available
    on a piface board.
    Following attributes are inherited from the RPiProcessFramework class:
        - run_process => boolean to indicate if process should be running
        - process_attributes => dictionary containing all attribues used by this process
          including following keys:
            - ProcessName
            - InputQueueName
        - process_input_queue => Handle to the input queue
        - logger_instance => Handle to the logger instance
    Following attributes are defined in the RPiOutputVentilator class:
        - output_relays => Dictionary including all active relays
            - Key: Unique reference to the output relay. Type: String
                   Example: (0,1) => relay 1 on piface board 0
            - Value: Attributes for the output relay. Type: List
                     Example: [1, "Relay 1", "RPI_INPUTBUTTON_1_5_PRESSED|PULSE", 0, 0]
                        => Current state of the relay: 1
                        => Description: Releay 1
                        => Logic: In case of an buttong event 'RPI_INPUT_BUTTON_1_5_PRESSED',
                                  a PULSE action needs to be triggered
                        => Pulse action: 0 (ie. no pulse action is ongoing)
                        => Time stamp of last Pulse action: 0 (ie.no pulse action took place yet)
        - process_logic => dictionary including all the actions required for a
                            received input button event
            - Key: Unique reference to the input event. Type: String
                   Example: "RPI_INUTBUTTON_1_5_PRESSED"
            - Value: Required actions when event is received. Type: List of dictionaries
                     Example: [{(0,1): TOGGLE}, {(1, 1): TOGGLE}]
                              => TOGGLE action should be triggered for output relay 1
                                  on boards 0 and 1
        - relay_timer => dictionary where
            - Key: Unique reference to the output relay. Type: String
                   Example: (0,1) => relay 1 on piface board 0
            - Value:
                    - State => Indicates if the timer is active.
                               2 values are allowed either 0 (=Not Running) or 1 (=Pressed)
                    - Description => Timer description
                    - StartTime => Time stamp when the Ventilator started running
                    - StopTime => Time stamp when the Ventilator stopped running
                    - LagTime => Delay to actually stop Ventilator from running after
                                 receiving the "Stop" event.
                                 Value = 0 means that no lag is used
                    - RunTime => Time the Ventilator should run after receiving the "Start" event
                                 Value = 0 means that now timer is used. Stopping the Ventilator
                                 is handled externally
    '''
    def __init__(self):
        # Initialize process framework attributes so we can start using them
        RPiProcessFramework.__init__(self, default_log_level='INFO')

        # Initialize all installed PiFace boards
        self.logger_instance.debug("RPiOutputVentilator - Initializing PiFace boards")
        RPiPiface.__init__(self)
        # Let's share some log information
        if RPiPiface.get_number_of_boards(self) == 0:
            self.logger_instance.critical(
                "RPiOutputVentilator - No PiFace boards detected. \
                Unable to process input signals"
                )
            self.run_process = False    # No need to continue
        elif RPiPiface.get_number_of_boards(self) == 1:
            self.logger_instance.info("RPiOutputVentilator - One PiFace boards detected")
        else:
            self.logger_instance.warning(
                "RPiOutputVentilator - More than one PiFace board detected." +\
                "Address of last detected board = {}".format(RPiPiface.get_number_of_boards(self)-1))

        # Initialize the output relay dictionary
        self.output_relays = self.create_output_relay_list(self.process_attributes.__repr__())
        # Initialize the relay timer dictionary
        self.relays_timer = self.create_relay_timer_list(self.process_attributes.__repr__())
        # Initialize the process logic dictionary
        self.process_logic = self.create_process_logic_dictionary()

    def __del__(self):
        self.logger_instance.info("RPiOutputVentilator - Process Stopping!")

    def __repr__(self):
        return str(RPiPiface.get_number_of_boards(self))

    def __str__(self):
        long_string = RPiProcessFramework.__str__(self)
        long_string += "Number of PiFace boards detected: {}\n".format(RPiPiface.get_number_of_boards(self))
        if self.output_relays != {}:
            long_string += "output_relays:\n"
            for key, value in self.output_relays.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No output_relays information found!\n"
        if self.relays_timer != {}:
            long_string += "relays_timer:\n"
            for key, value in self.relays_timer.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No relays_timer information found!\n"
        if self.process_logic != {}:
            long_string += "process_logic:\n"
            for key, value in self.process_logic.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No output_relays process logic found!\n"

        return long_string

    @classmethod
    def _get_board_number(cls, key):
        '''
        function that retrieves the button board number
        '''
        return int(key[1])

    @classmethod
    def _get_relay_number(cls, key):
        '''
        function that retrieves the button relay number
        '''
        return int(key[3])

    def _get_state(self, key):
        '''
        Gether method to retrieve state value for a relay
        '''
        return self.output_relays[key][0]

    def _get_description(self, key):
        '''
        Gether method to retrieve description for a relay
        '''
        return self.output_relays[key][1]

    def _get_logic(self, key):
        '''
        Gether method to retrieve logic value for a relay
        '''
        return self.output_relays[key][2]

    def _get_pulse(self, key):
        '''
        Gether method to retrieve pulse value for a relay
        '''
        return self.output_relays[key][3]

    def _get_pulse_timestamp(self, key):
        '''
        Gether method to retrieve pulse timestamp value for a relay
        '''
        return self.output_relays[key][4]

    def _set_state(self, key, state):
        '''
        Sether method to set state value for a relay to
        the value provided by the state parameter
        '''
        self.output_relays[key][0] = state

    def _set_pulse(self, key, state):
        '''
        Sether method to set pulse value for a relay to
        the value provided by the state parameter
        '''
        self.output_relays[key][3] = state

    def _set_relay_timestamp(self, key, timestamp):
        '''
        method that sets the output relay pulse timestamp
        '''
        self.output_relays[key][4] = timestamp

    def _get_relaytimer_state(self, key):
        '''
        Gether method to retrieve state value for a relay timer
        '''
        return self.relays_timer[key][0]

    def _get_relaytimer_description(self, key):
        '''
        Gether method to retrieve description for a relay timer
        '''
        return self.relays_timer[key][1]

    def _get_relaytimer_lagtime(self, key):
        '''
        Geter method to retrieve lagtime for a relay timer
        '''
        return self.relays_timer[key][2]

    def _get_relaytimer_runtime(self, key):
        '''
        Geter method to retrieve runtime for a relay timer
        '''
        return self.relays_timer[key][3]

    def _get_relaytimer_starttime(self, key):
        '''
        Geter method to retrieve start time for a relay timer
        '''
        return self.relays_timer[key][4]

    def _get_relaytimer_stoptime(self, key):
        '''
        Geter method to retrieve stop time for a relay timer
        '''
        return self.relays_timer[key][5]

    def _set_relaytimer_state(self, key, state):
        '''
        Sether method to set state value for a relay timer to
        the value provided by the state parameter
        '''
        self.relays_timer[key][0] = state

    def _set_relaytimer_start_timestamp(self, key, timestamp):
        '''
        method that sets relay timer start time
        '''
        self.relays_timer[key][4] = timestamp

    def _set_relaytimer_stop_timestamp(self, key, timestamp):
        '''
        method that sets relay timer stop time
        '''
        self.relays_timer[key][5] = timestamp

    def create_output_relay_list(self, process_attribute_list):
        '''
        Return value is a dictionary where
          - The key is set as the address consisting of the board and relay number
          - The corresponding values a list structure containing following attributes:
            - State => integer that is either 0 =>Relay in 'released' state or
              1 => Relay in 'pulled' state
            - Description => String value
            - Logic => logic that indicates what should happen based on the message
              send by an input handler (for example input buttons)
            - Pulse => integer that is either 0 (=Nothing going on) or 1 (=Pulse action ongoing)
            - PulseTimeStamp => timestamp when the pulse state was changed
        '''
        reply = {}

        for board in range(0, RPiPiface.get_number_of_boards(self)):
            for pin in range(0, 2):
                key = "Relay" + str(board) + str(pin)
                if key in process_attribute_list:
                    value = process_attribute_list[key]
                    attribute_key, description, logic = value.split(
                        ";")
                    logic_list = []
                    logic_list = logic.split(',')
                    if description != "Not Used":
                        reply[attribute_key] = [
                            0,  # State
                            description,
                            logic_list,
                            0,  # Pulse
                            0]  # Timestamp when pulse status was change
                        self.logger_instance.debug(
                            "RPiOutputVentilator - Initializing output_relay: {}".format(
                                attribute_key) +\
                            " - State: {}".format(
                                reply[attribute_key][0]) +\
                            " - Description: {}".format(
                                reply[attribute_key][1]) +\
                            " - Logic: {}".format(
                                reply[attribute_key][2]) +\
                            " - Pulse: {}".format(
                                reply[attribute_key][3]) +\
                            " - Pulse Time Stamp: {}".format(
                                reply[attribute_key][4])
                            )

        return reply

    def create_relay_timer_list(self, process_attribute_list):
        '''
        Return value is a dictionary where
          - The key is set as the address consisting of the board and relay number
          - The corresponding values a list structure containing following attributes:
            - State => integer that is either 0 => Timer is not running or
              1 => Timer is running
            - Description => String value
            - lagtime => Number of seconds the ventilator will remain active after
                         "stop" event is received
            - runtime => Maximum number of seconds the ventilator should run
        '''
        reply = {}

        for board in range(0, RPiPiface.get_number_of_boards(self)):
            for pin in range(0, 2):
                key = "RelayTimer" + str(board) + str(pin)
                if key in process_attribute_list:
                    value = process_attribute_list[key]
                    attribute_key, description, lagtime, runtime = value.split(
                        ";")
                    if description != "Not Used":
                        reply[attribute_key] = [
                            0,  # State
                            description,
                            int(lagtime),
                            int(runtime),
                            0, # start_time
                            0] # stop_time
                        self.logger_instance.debug(
                            "RPiOutputVentilator - Initializing relay_timer: {}".format(
                                attribute_key) +\
                            " - State: {}".format(
                                reply[attribute_key][0]) +\
                            " - Description: {}".format(
                                reply[attribute_key][1]) +\
                            " - LagTime: {}".format(
                                reply[attribute_key][2]) +\
                            " - RunTime: {}".format(
                                reply[attribute_key][3])
                            )

        return reply
        
    def create_process_logic_dictionary(self):
        '''
        This method creates a process logic dictionary based on an active output relay list
        If no active relays available, an empty dictionary is returned
        '''
        self.logger_instance.debug(
            "RPiOutputVentilator - Creating Process Logic Dictionary")
        logic_dictionary = {}
        if self.output_relays:
            for key in self.output_relays:
                action_list = []
                attributes = self.output_relays[key]
                logic_list = attributes[2]
                for items in logic_list:
                    input_reference, action = items.split('|')
                    action_list_item = [key, action]
                    if input_reference in logic_dictionary: # pylint: disable=consider-using-get
                        action_list = logic_dictionary[input_reference]
                    else:
                        action_list = []
                    self.logger_instance.debug(
                        "RPiOutputVentilator - Adding item to process logic list {}: {}".format(
                                                                                           input_reference,
                                                                                           action_list_item))
                    action_list.append(action_list_item)
                    logic_dictionary[input_reference] = action_list

        return logic_dictionary

    def _handle_output_relays(self):
        '''
        This method will scan all active relays and sets the 'state' value
        as stored in the attributes for each relay.
        '''
        for key in self.output_relays:
            if self._get_state(key) == 0:
                RPiPiface.reset_output_relay(self, self._get_board_number(key), self._get_relay_number(key))
            else:
                RPiPiface.set_output_relay(self, self._get_board_number(key), self._get_relay_number(key))

    def parse_input_button_message(self, message):
        '''
        Method responsible to parse an incomming input button message
        Valid actions:
        - PULSE
        Other actions are ignored
        '''
        self.logger_instance.debug(
            "RPiOutputVentilator - Parsing input button message {}".format(message))
        try:
            action_list = self.process_logic[message]
            for relay_key, relay_action in action_list:
                if relay_action == "TOGGLE":
                    if self._get_state(relay_key) == 0:
                        self._set_state(relay_key, 1)
                        self.logger_instance.info(
                            "RPiOutputVentilator - Setting relay {} - {}".format(
                                relay_key,
                                self._get_description(relay_key)))
                        self._set_relaytimer_state(relay_key, 1)
                        self._set_relaytimer_start_timestamp(relay_key, time.time())
                        # set stop timestamp to 0 to indicate we entered a new run cycle
                        self._set_relaytimer_stop_timestamp(relay_key, 0)
                        self.logger_instance.debug(
                            "RPiOutputVentilator - Setting relay timer {} - {} at {}".format(
                                relay_key,
                                self._get_relaytimer_description(relay_key),
                                self._get_relaytimer_starttime(relay_key)))
                    else:
                    # We don't actually reset the relay state but only set the time we received the
                    # stop event. Actual resetting of the relay state is handled on a different place
#                        self._set_state(relay_key, 0)
#                        self.logger_instance.info(
#                            "RPiOutputVentilator - Resetting relay {} - {}".format(
#                                relay_key,
#                                self._get_description(relay_key)))
#                        self._set_relaytimer_state(relay_key, 0)
                        self._set_relaytimer_stop_timestamp(relay_key, time.time())
                        self.logger_instance.debug(
                            "RPiOutputVentilator - Stop event received for relay {} - {} at {}".format(
                                relay_key,
                                self._get_relaytimer_description(relay_key),
                                self._get_relaytimer_stoptime(relay_key)))
        except KeyError:
            self.logger_instance.warning(
                "RPiOutputVentilator - Unknow input event received {} - skipping".format(message))

    def process_message(self, message):
        '''
        Function responsible to handle messages coming from the process
        input queue. The message is passed as a parameter.
        Return value:
        - True: No STOP event received
        - False: STOP event received
        '''
        reply = True    # We assume we keep going

        message_list = message.split(";")
        if message_list[0] == "P":  # A process related message was received
            reply = super().process_message(message)
            # When the process attribute list has been refreshed
            # It's also necessary to refresh the outputrelay list to update any
            # changes
            if reply is True and message_list[1] == 'REFRESH_PROCESS_ATTRIBUTES':
                self.logger_instance.debug(
                    "RPiOutputVentilator - Refreshing process attributes")
                self.output_relays = self.create_output_relay_list(
                    self.process_attributes.__repr__())
                self.relays_timer = self.create_relay_timer_list(
                    self.process_attributes.__repr__())
                self.process_logic = self.create_process_logic_dictionary()
        elif message_list[0] == "I":  # An input button related message was received
            self.logger_instance.debug(
                "RPiOutputVentilator - Parsing input button message received {} - {}".format(
                    message,
                    message_list[1]))
            self.parse_input_button_message(message_list[1])

        return reply

    def process_output_ventilator(self):
        '''
        Method to handle output relays to control the ventilators
        First we check if the Ventilator should be switched off
        based on the timer function
        Next we set all the relays accordig to their status
        '''
        for relay in self.output_relays:
            if (self._get_relaytimer_state(relay) == 1) and (self._get_relaytimer_runtime(relay) > 0):
                # If the ventilator is active for more than "runtime" second, reset the relay state
                if (time.time() - self._get_relaytimer_starttime(relay)) > self._get_relaytimer_runtime(relay):
                    self._set_state(relay, 0)
                    self._set_relaytimer_state(relay, 0)
                    self.logger_instance.info(
                        "RPiOutputVentilator - Resetting pulse state to 0 for {} after maximum runtime period ({} seconds)".format(relay, self._get_relaytimer_runtime(relay)))
            if (self._get_relaytimer_state(relay) == 1) and (self._get_relaytimer_stoptime(relay) != 0):
                # If the ventilator is "stopped" for more than "lagtime" second, reset the relay state
                if (time.time() - self._get_relaytimer_stoptime(relay)) > self._get_relaytimer_lagtime(relay):
                    self._set_state(relay, 0)
                    self._set_relaytimer_state(relay, 0)
                    self._set_relaytimer_stop_timestamp(relay, 0)
                    self.logger_instance.info(
                        "RPiOutputVentilator - Resetting pulse state to 0 for {} after lagtime period ({} seconds)".format(relay, self._get_relaytimer_lagtime(relay)))

        self._handle_output_relays()

def main():
    '''
    Initiating the RPiOutputVentilator process
    '''

    output_handler_instance = RPiOutputVentilator()

    while output_handler_instance.run_process:
        with output_handler_instance.process_input_queue as consumer:
            output_handler_instance.run_process = consumer.consume(  # pylint: disable=assignment-from-no-return
                output_handler_instance.process_message,
                output_handler_instance.process_output_ventilator)

if __name__ == '__main__':
    main()
