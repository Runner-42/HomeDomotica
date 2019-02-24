'''
Name:		rpi_outputrelay.py
Purpose:	Class RPiOutputRelay is used to handle relays on the PiFace boards

Author:	Wim

Created:	25/08/2018
Copyright:	(c) Wim 2018
Licence:
'''

import time
from rpi_piface import RPiPiface

from rpi_processframework import RPiProcessFramework
#from rpi_messagesender import RPiMessageSender

class RPiOutputRelay(RPiProcessFramework, RPiPiface):
    '''
    This class is created to handle the Output Relays available on a piface board
    Following attributes are inherited from the RPiProcessFramework class:
        - run_process => boolean to indicate if process should be running
        - process_attributes => dictionary containing all attribues used by this process
          including following keys:
            - ProcessName
            - InputQueueName
        - process_input_queue => Handle to the input queue
        - logger_instance => Handle to the logger instance
    Following attributes are defined in the RPiOutputRelay class:
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
                     Example: [{(0,1): PULSE}, {(1, 1): PULSE}]
                              => PULSE action should be triggered for output relay 1
                                  on boards 0 and 1
    '''
    def __init__(self):
        # Initialize process framework attributes so we can start using them
        RPiProcessFramework.__init__(self, default_log_level='INFO')

        # Initialize all installed PiFace boards
        self.logger_instance.debug("RPiOutputRelay - Initializing PiFace boards")
        RPiPiface.__init__(self)
        # Let's share some log information
        if RPiPiface.get_number_of_boards(self) == 0:
            self.logger_instance.critical(
                "RPiOutputRelay - No PiFace boards detected. \
                Unable to process input signals"
                )
            self.run_process = False    # No need to continue
        elif RPiPiface.get_number_of_boards(self) == 4:
            self.logger_instance.info("RPiOutputRelay - Four PiFace boards detected")
        else:
            self.logger_instance.warning(
                "RPiOutputRelay - Potentially not all PiFace boards detected." +\
                "Address of last detected board = {}".format(RPiPiface.get_number_of_boards(self)-1))

        # Initialize the output relay dictionary
        self.output_relays = self.create_output_relay_list(self.process_attributes.__repr__())
        # Initialize the process logic dictionary
        self.process_logic = self.create_process_logic_dictionary()

    def __del__(self):
        self.logger_instance.info("RPiOutputRelay - Process Stopping!")

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

    def _set_pulse_timestamp(self, key, timestamp):
        '''
        method that sets the output relay pulse timestamp
        '''
        self.output_relays[key][4] = timestamp

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
                            "RPiOutputRelay - Initializing output_relay: {}".format(
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

    def create_process_logic_dictionary(self):
        '''
        This method creates a process logic dictionary based on an active output relay list
        If no active relays available, an empty dictionary is returned
        '''
        self.logger_instance.debug(
            "RPIOutputRelay - Creating Process Logic Dictionary")
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
                        "RPIOutputRelay - Adding item to process logic list {}: {}".format(
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
        - TOGGLE
        Other actions are ignored
        '''
        self.logger_instance.debug(
            "RPIOutputRelay - Parsing input button message {}".format(message))
        try:
            action_list = self.process_logic[message]
            for relay_key, relay_action in action_list:
                if relay_action == "PULSE":
                    self._set_state(relay_key, 1)
                    self._set_pulse(relay_key, 1)
                    self._set_pulse_timestamp(relay_key, time.time())
                    self.logger_instance.info(
                        "RPIOutputRelay - Activating pulse event for relay {} - {}".format(
                            relay_key,
                            self._get_description(relay_key)))
                elif relay_action == "TOGGLE":
                    if self._get_state(relay_key) == 0:
                        self._set_state(relay_key, 1)
                        self.logger_instance.info(
                            "RPIOutputRelay - Setting relay {} - {}".format(
                                relay_key,
                                self._get_description(relay_key)))
                    else:
                        self._set_state(relay_key, 0)
                        self.logger_instance.info(
                            "RPIOutputRelay - Resetting relay {} - {}".format(
                                relay_key,
                                self._get_description(relay_key)))
        except KeyError:
            self.logger_instance.warning(
                "RPIOutputRelay - Unknow input event received {} - skipping".format(message))

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
                self.output_relays = self.create_output_relay_list(
                    self.process_attributes.__repr__())
                self.process_logic = self.create_process_logic_dictionary()
        elif message_list[0] == "I":  # An input button related message was received
            self.logger_instance.debug(
                "RPIOutputRelay - Parsing input button message received {} - {}".format(
                    message,
                    message_list[1]))
            self.parse_input_button_message(message_list[1])

        return reply

    def process_output_relay(self):
        '''
        Method to handle output relays
        First we process te pulse relays to see if they can be switched off
        Next we set all the relays accordig to their status
        '''
        for relay in self.output_relays:
            if self._get_pulse(relay) == 1:
                # If the pulse is active for more than 1 second, reset it
                if (time.time() - self._get_pulse_timestamp(relay)) > 1:
                    self._set_state(relay, 0)
                    self._set_pulse(relay, 0)
                    self.logger_instance.debug(
                        "RPIOutputRelay - Resetting pulse state to 0 for {}".format(relay))

        self._handle_output_relays()

def main():
    '''
    Initiating the RPiOutputRelay process
    '''

    output_handler_instance = RPiOutputRelay()

    while output_handler_instance.run_process:
        with output_handler_instance.process_input_queue as consumer:
            output_handler_instance.run_process = consumer.consume(  # pylint: disable=assignment-from-no-return
                output_handler_instance.process_message,
                output_handler_instance.process_output_relay)

if __name__ == '__main__':
    main()
