'''
Name:		rpi_outputdimmer.py
Purpose:	Class RPiOutputDimmer is used to handle dimmers using digital outputs on the PiFace boards

Author:	Wim

Created:	03/03/2019
Copyright:	(c) Wim 2019
Licence:
'''
from rpi_processframework import RPiProcessFramework
from rpi_piface import RPiPiface

class RPiOutputDimmer(RPiProcessFramework, RPiPiface):
    '''
    Class Name:   RPiOutputDimmer
    '''
    def __init__(self):
        # Initialize process framework attributes so we can start using them
        RPiProcessFramework.__init__(self, default_log_level='INFO')

        # We make use of a PiFace, so let's initialize an instance
        RPiPiface.__init__(self)
        if self.get_number_of_boards() == 0:
            self.logger_instance.critical(
                "RPiOutputDimmer - No PiFace boards detected. \
                Unable to process input signals"
                )
            self.run_process = False    # No need to continue
        elif self.get_number_of_boards() == 4:
            self.logger_instance.info("RPiOutputDimmer - Four PiFace boards detected")
        else:
            self.logger_instance.warning(
                "RPiOutputDimmer - Potentially not all PiFace boards detected." +\
                "Address of last detected board = {}".format(self.get_number_of_boards()-1))

        # Initialize the output dimmer dictionary
        self.output_dimmer = self.create_output_dimmer_list(self.process_attributes.__repr__())
        # Initialize the process logic dictionary
        self.process_logic = self.create_process_logic_dictionary()

    def __del__(self):
        self.logger_instance.info("RPiOutputDimmer - Process Stopping!")

    def __str__(self):
        long_string = RPiProcessFramework.__str__(self)
        long_string += RPiPiface.__str__(self)
        if self.output_dimmer != {}:
            long_string += "output dimmer:\n"
            for key, value in self.output_dimmer.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No output_dimmer information found!\n"
        if self.process_logic != {}:
            long_string += "process_logic:\n"
            for key, value in self.process_logic.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No output_dimmer process logic information found!\n"

        return long_string

    def _get_state(self, key):
        '''
        Gether method to retrieve state value for a digital output/dimmer
        '''
        return self.output_dimmer[key][0]

    def _get_description(self, key):
        '''
        Gether method to retrieve description for an output/dimmer
        '''
        return self.output_dimmer[key][1]

    def _set_state(self, key, state):
        '''
        Sether method to set state value for a digital output/dimmer to
        the value provided by the state parameter
        '''
        self.output_dimmer[key][0] = state

    def create_output_dimmer_list(self, process_attribute_list):
        '''
        Return value is a dictionary where
          - The key is set as the address consisting of the board and 'dimmer' number
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
        self.logger_instance.debug(
            "RPiOutputDimmer - create_output_dimmer_list - processing attribute list: {}".format(
                process_attribute_list))
        for board in range(0, self.get_number_of_boards()):
            for pin in range(0, 8):
                key = "Dimmer" + str(board) + str(pin)
                if key in process_attribute_list:
                    value = process_attribute_list[key]
                    attribute_key, description, logic = value.split(
                        ";")
                    logic_list = []
                    logic_list = logic.split(',')
                    self.logger_instance.debug(
                        "RPiOutputDimmer - create_output_dimmer_list - processing {}".format(key))
                    if description != "Not Used":
                        reply[attribute_key] = [
                            0,  # State
                            description,
                            logic_list]  # Timestamp when pulse status was change
                        self.logger_instance.debug(
                            "RPiOutputDimmer - create_output_dimmer_list - Dimmer: {}".format(
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
        This method creates a process logic dictionary based on an active output dimmer list
        If no active dimmers available, an empty dictionary is returned
        '''
        self.logger_instance.debug(
            "RPIOutputDimmer - Creating Process Logic Dictionary")
        logic_dictionary = {}
        if self.output_dimmer:
            for key in self.output_dimmer:
                action_list = []
                attributes = self.output_dimmer[key]
                logic_list = attributes[2]
                self.logger_instance.debug(
                    "RPIOutputDimmer - create_process_logic_dictionary - Processing {}: {}".format(
                        key,
                        logic_list))
                for items in logic_list:
                    input_reference, action = items.split('|')
                    action_list_item = [key, action]
                    self.logger_instance.debug(
                        "RPIOutputDimmer - create_process_logic_dictionary - " +
                        "Processing logic_list {}: {}".format(input_reference, action))
                    if input_reference in logic_dictionary: # pylint: disable=consider-using-get
                        action_list = logic_dictionary[input_reference]
                    else:
                        action_list = []
                    self.logger_instance.debug(
                        "RPIOutputDimmer - create_process_logic_dictionary - " +
                        "Adding item to logic process list {}: {}".format(
                            input_reference,
                            action_list_item))
                    action_list.append(action_list_item)
                    logic_dictionary[input_reference] = action_list
        else:
            self.logger_instance.debug(
                "RPIOutputDimmer - create_process_logic_dictionary - "&
                "No entries found in output_dimmer list!")

        return logic_dictionary

    def parse_input_button_message(self, message):
        '''
        Method responsible to parse an incomming input button message
        Valid actions:
        - ON
        - OFF
        Other actions are ignored
        '''
        self.logger_instance.debug(
            "RPIOutputDimmer - Parsing input button message {}".format(message))

        try:
            action_list = self.process_logic[message]
            for dimmer_key, dimmer_action in action_list:
                if dimmer_action == "ON":
                    self._set_state(dimmer_key, 1)
                    self.logger_instance.info(
                        "RPIOutputDimmer - 'ON' action received -> Setting dimmer {} - {}".format(
                            dimmer_key,
                            self._get_description(dimmer_key)))
                elif dimmer_action == "OFF":
                    self._set_state(dimmer_key, 0)
                    self.logger_instance.info(
                        "RPIOutputDimmer - 'OFF' action received -> Resetting dimmer {} - {}".
                        format(dimmer_key, self._get_description(dimmer_key)))
                else:
                    self.logger_instance.debug(
                        "RPIOutputDimmer - Unknown action received {} - skipping!".format(
                            dimmer_action))
        except KeyError:
            self.logger_instance.debug(
                "RPIOutputDimmer - Unknow input event received {} - skipping".format(message))

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
            # It's also necessary to refresh the output_dimmer list to update any
            # changes
            if reply is True and message_list[1] == 'REFRESH_PROCESS_ATTRIBUTES':
                self.output_dimmer = self.create_output_dimmer_list(
                    self.process_attributes.__repr__())
                self.process_logic = self.create_process_logic_dictionary()
        elif message_list[0] == "I":  # An input button related message was received
            self.logger_instance.debug(
                "RPIOutputDimmer - Input button message received {} - {}".format(
                    message,
                    message_list[1]))
            self.parse_input_button_message(message_list[1])

        return reply

    def process_output_dimmer(self):
        '''
        This method will scan all active dimmers in the list
        and sets the 'state' value as stored in the attributes for each digital output - dimmer.
        '''
        for key in self.output_dimmer:
            board_number = int(key[1])
            pin_number = int(key[3])
            if self._get_state(key):
                self.set_output_pin(board_number, pin_number)
            else:
                self.reset_output_pin(board_number, pin_number)
def main():
    '''
    Initiating the RPiOutputDimmer process
    '''

    output_handler_instance = RPiOutputDimmer()

    while output_handler_instance.run_process:
        with output_handler_instance.process_input_queue as consumer:
            output_handler_instance.run_process = consumer.consume(  # pylint: disable=assignment-from-no-return
                output_handler_instance.process_message,
                output_handler_instance.process_output_dimmer)

if __name__ == '__main__':
    main()
