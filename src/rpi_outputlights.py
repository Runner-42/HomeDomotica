'''
Name:		rpi_outputlights.py
Purpose:	Class RPiOutputLights is used to handle digital outputs on the PiFace boards

Author:	Wim

Created:	22/09/2018
Copyright:	(c) Wim 2018
Licence:
'''
import time

from rpi_processframework import RPiProcessFramework
from rpi_piface import RPiPiface

class RPiOutputLights(RPiProcessFramework, RPiPiface):
    '''
    
    '''
    def __init__(self):
        # Initialize process framework attributes so we can start using them
        RPiProcessFramework.__init__(self, default_log_level='INFO')
    
        # We make use of a PiFace, so let's initialize an instance
        RPiPiface.__init__(self)
        if self.get_number_of_boards() == 0:
            self.logger_instance.critical(
                "RPiOutputLights - No PiFace boards detected. \
                Unable to process input signals"
                )
            self.run_process = False    # No need to continue
        elif self.get_number_of_boards() == 4:
            self.logger_instance.info("RPiOutputLights - Four PiFace boards detected")
        else:
            self.logger_instance.warning(
                "RPiOutputLights - Potentially not all PiFace boards detected." +\
                "Address of last detected board = {}".format(self.get_number_of_boards()-1))

        # Initialize the output lights dictionary
        self.output_lights = self.create_output_lights_list(self.process_attributes.__repr__())
        # Initialize the process logic dictionary
        self.process_logic = self.create_process_logic_dictionary()

    def __del__(self):
        self.logger_instance.info("RPiOutputLights - Process Stopping!")

    def __str__(self):
        long_string = RPiProcessFramework.__str__(self)
        long_string += RPiPiface.__str__(self)
        if self.output_lights != {}:
            long_string += "output_lights:\n"
            for key, value in self.output_lights.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No output_relays information found!\n"
        if self.process_logic != {}:
            long_string += "process_logic:\n"
            for key, value in self.process_logic.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No output_relays process logic information found!\n"

        return long_string

    def _get_state(self, key):
        '''
        Gether method to retrieve state value for a digital output
        '''
        return self.output_lights[key][0]

    def _get_description(self, key):
        '''
        Gether method to retrieve description for a relay
        '''
        return self.output_lights[key][1]

    def _set_state(self, key, state):
        '''
        Sether method to set state value for a digital output to
        the value provided by the state parameter
        '''
        self.output_lights[key][0] = state

    def create_output_lights_list(self, process_attribute_list):
        '''
        Return value is a dictionary where
          - The key is set as the address consisting of the board and light number
          - The corresponding values a list structure containing following attributes:
            - State => integer that is either 0 => Output pin in 'off' state or
              1 => Output pin in 'on' state
            - Description => String value
            - Logic => logic that indicates what should happen based on the message
              send by an input handler (for example input buttons)
            - Pulse => integer that is either 0 (=Nothing going on) or 1 (=Pulse action ongoing)
            - PulseTimeStamp => timestamp when the pulse state was changed
        '''
        reply = {}
        
        for board in range(0, self.get_number_of_boards()):
            for pin in range(0, 7):
                key = "Light" + str(board) + str(pin)
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
                            logic_list]  # Timestamp when pulse status was change
                        self.logger_instance.debug(
                            "RPiOutputLights - Initializing digital output - lights: {}".format(
                                attribute_key) +\
                            " - State: {}".format(
                                reply[attribute_key][0]) +\
                            " - Description: {}".format(
                                reply[attribute_key][1]) +\
                            " - Logic: {}".format(
                                reply[attribute_key][2])
                            )
        
        return reply

    def create_process_logic_dictionary(self):
        '''
        This method creates a process logic dictionary based on an active output light list
        If no active lights available, an empty dictionary is returned
        '''
        self.logger_instance.debug(
            "RPIOutputLights - Creating Process Logic Dictionary")
        logic_dictionary = {}
        if self.output_lights:
            for key in self.output_lights:
                action_list = []
                attributes = self.output_lights[key]
                logic_list = attributes[2]
                for items in logic_list:
                    input_reference, action = items.split('|')
                    action_list_item = [key, action]
                    if input_reference in logic_dictionary: # pylint: disable=consider-using-get
                        action_list = logic_dictionary[input_reference]
                    else:
                        action_list = []
                    self.logger_instance.debug(
                        "RPIOutputLights - Adding item to logic process list {}: {}".format(
                                                                                            input_reference,
                                                                                            action_list_item))
                    action_list.append(action_list_item)
                    logic_dictionary[input_reference] = action_list

        return logic_dictionary

    def parse_input_button_message(self, message):
        '''
        Method responsible to parse an incomming input button message
        Valid actions:
        - TOGGLE
        Other actions are ignored
        '''
        self.logger_instance.debug(
            "RPIOutputLights - Parsing input button message {}".format(message))

        try:
            action_list = self.process_logic[message]
            for light_key, light_action in action_list:
                if light_action == "TOGGLE":
                    if self._get_state(light_key) == 0:
                        self._set_state(light_key, 1)
                        self.logger_instance.info(
                            "RPIOutputLights - Setting light {} - {}".format(
                                light_key,
                                self._get_description(light_key)))
                    else:
                        self._set_state(light_key, 0)
                        self.logger_instance.info(
                            "RPIOutputLights - Resetting light {} - {}".format(
                                light_key,
                                self._get_description(light_key)))
        except KeyError:
            self.logger_instance.warning(
                "RPIOutputLights - Unknow input event received {} - skipping".format(message))

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
                self.output_lights = self.create_output_lights_list(
                    self.process_attributes.__repr__())
                self.process_logic = self.create_process_logic_dictionary()
        elif message_list[0] == "I":  # An input button related message was received
            self.logger_instance.debug(
                "RPIOutputLights - Parsing input button message received {} - {}".format(
                    message,
                    message_list[1]))
            self.parse_input_button_message(message_list[1])

        return reply

    def process_output_lights(self):
        '''
        This method will scan all active lights in the list
        and sets the 'state' value as stored in the attributes for each digital output - light.
        '''
        for key in self.output_lights:
            board_number = int(key[1])
            pin_number = int(key[3])
            if self._get_state(key):
                self.set_output_pin(board_number, pin_number)
            else:
                self.reset_output_pin(board_number, pin_number)
def main():
    '''
    Initiating the RPiOutputLights process
    '''

    output_handler_instance = RPiOutputLights()

    while output_handler_instance.run_process:
        with output_handler_instance.process_input_queue as consumer:
            output_handler_instance.run_process = consumer.consume(  # pylint: disable=assignment-from-no-return
                output_handler_instance.process_message,
                output_handler_instance.process_output_lights)

if __name__ == '__main__':
    main()