'''
Name:		rpi_inputbutton.py
Purpose:	Class RPiInputButton is used to handle inputs on the PiFace boards

Author:	Wim

Created:	28/07/2018
Copyright:	(c) Wim 2018
Licence:
'''

import time

from rpi_processframework import RPiProcessFramework
from rpi_piface import RPiPiface
from rpi_messagesender import RPiMessageSender
import json


class RPiInputButton(RPiProcessFramework, RPiPiface):
    '''
    This class is created to handle the Input Buttons available on a piface board
    Following attributes are inherited from the RPiProcessFramework class:
        - run_process => boolean to indicate if process should be running
        - process_attributes => dictionary containing all attribues used by this process
          including following keys:
            - ProcessName
            - InputQueueName
        - process_input_queue => Handle to the input queue
        - logger_instance => Handle to the logger instance
    Following attributes are defined in the RPiInputButton class:
        - input_buttons => dictionary where
            - The key is set as the address of the input pin consisting of the board and pin number
            - The corresponding values a list structure containing following attributes:
                - State => integer that is either 0 (=Not Pressed) or 1 (=Pressed)
                - Previous State => integer that is either 0 (=Not Pressed) or 1 (=Pressed)
                - SignalUpTimestamp => Time stamp when the button was pressed
                    (ie. move from State 0 to 1)
                - SignalDownTimestamp => Time stamp when the button was released
                    (ie.move from State 1 to 0)
                - PreviousSignalDownTimestamp => Time stamp of the previous SignalDownTimestamp.
                    This is used to identify "double press" activities
                - ButtonPressedCount => Attribute of a button to identify double press events
                - Description => String value
                - OutputHandler => String value that indicates to which "Outputhandler" the button
                    input event should be send to. If more than  hanlder is required, they can be
                    separated by a "," (=comma)
        - process_consumer_queue => dictionary where
            - The key is set as the consumer reference
            - The corresponding value is the queue name
    '''

    def __init__(self):
        # Initialize process framework attributes so we can start using them
        RPiProcessFramework.__init__(self, default_log_level='INFO')

        # We make use of a PiFace, so let's initialize an instance
        RPiPiface.__init__(self)
        if self.get_number_of_boards() == 0:
            self.logger_instance.critical(
                "RPiInputButton - No PiFace boards detected. \
                Unable to process input signals"
            )
            self.run_process = False    # No need to continue
        elif self.get_number_of_boards() == 4:
            self.logger_instance.info(
                "RPiInputButton - Four PiFace boards detected")
        else:
            self.logger_instance.warning(
                "RPiInputButton - Potentially not all PiFace boards detected." +
                "Address of last detected board = {}".format(self.get_number_of_boards()-1))

        # Initialize the input buttons dictionary
        self.input_buttons = self.create_inputbutton_list(
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
        self.logger_instance.info("RPiInputButton - Process Stopping!")

    def __str__(self):
        long_string = RPiProcessFramework.__str__(self)
        long_string += RPiPiface.__str__(self)
        if self.input_buttons != {}:
            long_string += "input_buttons:\n"
            for key, value in self.input_buttons.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No input_buttons information found!\n"
        if self.process_consumers != {}:
            long_string += "process consumers:\n"
            for key, value in self.process_consumers.items():
                long_string += "{} = {}\n".format(key, value)
        else:
            long_string += "No input_buttons process consumers information found!\n"

        return long_string

    def __repr__(self):
        return str(self.get_number_of_boards())

    def create_inputbutton_list(self, process_attribute_list):
        '''
        Return value is a dictionary where
          - The key is set as the address of the input pin consisting of the board and pin number
          - The corresponding values a list structure containing following attributes:
            - State => integer that is either 0 (=Not Pressed) or 1 (=Pressed)
            - Previous State => integer that is either 0 (=Not Pressed) or 1 (=Pressed)
            - SignalUpTimestamp => Time stamp when the button was pressed
              (ie. move from State 0 to 1)
            - SignalDownTimestamp => Time stamp when the button was released
              (ie.move from State 1 to 0)
            - PreviousSignalDownTimestamp => Time stamp of the previous SignalDownTimestamp.
              This is used to identify "double press" activities
            - ButtonPressedCount => Attribute of a button to identify double press events
            - Description => String value
            - Consumer => String value that indicates to which "consummers" the button
              input event should be send to. If more than 1 consummer is required, they can be
              separated by a "," (=comma)
        '''
        reply = {}

        for board in range(0, self.get_number_of_boards()):
            for pin in range(0, 8):
                key = "Button" + str(board) + str(pin)
                if key in process_attribute_list:
                    value = process_attribute_list[key]
                    attribute_key, description, consumer = value.split(
                        ";")
                    if description != "Not Used":
                        reply[attribute_key] = [
                            0,  # State
                            0,  # Previous state
                            description,
                            consumer,
                            0,  # SignalUpTimestamp
                            0,  # SignalDownTimestamp
                            0,  # PreviousSignalDownTimestamp
                            0]  # ButtonPressedCount
                        self.logger_instance.debug(
                            "RPiInputButton - Initializing input_button: {}".format(
                                attribute_key) +
                            " - State: {}".format(
                                reply[attribute_key][0]) +
                            " - Previous State: {}".format(
                                reply[attribute_key][1]) +
                            " - Description: {}".format(
                                reply[attribute_key][2]) +
                            " - Consumer: {}".format(
                                reply[attribute_key][3]) +
                            " - Signal Up Timestamp: {}".format(
                                reply[attribute_key][4]) +
                            " - Signal Down Timestamp: {}".format(
                                reply[attribute_key][5]) +
                            " - Previous Signal Down Timestamp: {}".format(
                                reply[attribute_key][6]) +
                            " - Button Pressed Count: {}".format(
                                reply[attribute_key][7])
                        )

        return reply

    def create_message_senders(self, process_attribute_list):
        '''
        method to create a consumer queue list based on all consumer entries found
        in the input_buttons list and the correspondng queue name in the
        process attribute list.
        Note: leading and trailing spaces are removed from the key to avoid KeyErrors
        '''
        process_consumer_queue = {}
        for key in self.input_buttons:
            consumer_list = self._get_button_consumers(key)
            queue_list = []
            try:
                for consumer in consumer_list:
                    queue_list.append(
                        process_attribute_list[str(consumer).lstrip().rstrip()])
                process_consumer_queue[key] = queue_list
                self.logger_instance.debug(
                    "RPiInputButton - Initializing process_consumers {} = {}".format(
                        key, queue_list))
            except Exception:   # pylint: disable=broad-except
                process_consumer_queue[key] = []
                self.logger_instance.warning(
                    "RPiInputButton - Invalide queue reference '{}' for input button {}. ".format(
                        consumer, key) +
                    "No events are created for this input button! " +
                    "Check {}!".format(str.lower(self.process_attributes.get_item(
                        "ProcessName")) + ".cfg")
                )

        return process_consumer_queue

    def _get_button_state(self, key):
        '''
        function that retrieves the button state value as set in the input
        button list
        '''
        return self.input_buttons[key][0]

    def _get_previous_button_state(self, key):
        '''
        function that retrieves the previous button state value as set in the input
        button list
        '''
        return self.input_buttons[key][1]

    def _get_button_description(self, key):
        '''
        function that retrieves the button description as set in the input
        button list
        '''
        return self.input_buttons[key][2]

    def _get_button_consumers(self, key):
        '''
        function that retrieves the button consumer list as set in the input
        button list
        '''
        return str(self.input_buttons[key][3]).split(",")

    def _get_button_signalup_timestamp(self, key):
        '''
        function that retrieves the button signal up timestamp
        as set in the input button list
        '''
        return self.input_buttons[key][4]

    def _get_button_signaldown_timestamp(self, key):
        '''
        function that retrieves the button signal down timestamp
        as set in the input button list
        '''
        return self.input_buttons[key][5]

    def _get_button_previous_signaldown_timestamp(self, key):
        '''
        function that retrieves the button previous signal down timestamp
        as set in the input button list
        '''
        return self.input_buttons[key][6]

    def _get_button_presscount(self, key):
        '''
        function that retrieves the button signal press count
        as set in the input button list
        '''
        return self.input_buttons[key][7]

    def _set_button_state(self, key, state):
        '''
        function that sets the button state value
        in the input button list
        '''
        self.input_buttons[key][0] = int(state)

    def _set_previous_button_state(self, key, state):
        '''
        method that sets the previous button state value
        in the input button list
        '''
        self.input_buttons[key][1] = int(state)

    def _set_button_description(self, key, description):
        '''
        method that sets the button description
        in the input button list
        '''
        self.input_buttons[key][2] = description

    def _set_button_consummers(self, key):
        '''
        method that sets the button consummer list
        in the input button list
        '''
        str(self.input_buttons[key][3]).split(",")

    def _set_button_signalup_timestamp(self, key, timestamp):
        '''
        method that sets the button signal up timestamp
        in the input button list
        '''
        self.input_buttons[key][4] = timestamp

    def _set_button_signaldown_timestamp(self, key, timestamp):
        '''
        method that sets the button signal down timestamp
        in the input button list
        '''
        self.input_buttons[key][5] = timestamp

    def _set_button_previous_signaldown_timestamp(self, key):
        '''
        method that sets the button previous signal down timestamp
        in the input button list
        '''
        self.input_buttons[key][6] = self.input_buttons[key][5]

    def _set_button_presscount(self, key):
        '''
        method that sets the button signal press count to 1
        in the input button list
        '''
        self.input_buttons[key][7] = 1

    def _reset_button_presscount(self, key):
        '''
        method that sets the button signal press count to 0
        in the input button list
        '''
        self.input_buttons[key][7] = 0

    def _read_input_buttons(self):
        '''
        method that reads all the (physical) inputs on the piface boards
        and store the actual status in the input_buttons dictionary
            key[1] represents the board number
            key[3] represents the pin number on this board
        '''
        for key in self.input_buttons:
            self._set_button_state(
                key,
                self.get_input_button_state(_get_board_number(key), _get_pin_number(key)))

    def process_input_buttons(self):
        '''
        method to process changes on input buttons.
        and send events as required.
        Valid events are:
        - UP
        - DOWN
        - PRESSED
        - PRESSEDLONG
        - PRESSEDDOUBLE
        Messages are constructed with following syntax:
        - "I;<process_name>_<board_number>_<pin_number>_<event>"
        '''
        # We first read the status of all input buttons
        self._read_input_buttons()

        # Now let's process the changes
        for key in self.input_buttons:
            if self._get_button_state(key) != self._get_previous_button_state(key):
                message_pre_able = "I;{}_{}_{}_".format(
                    self.process_attributes.get_item("ProcessName").upper(),
                    _get_board_number(key),
                    _get_pin_number(key),)
                if self._get_button_state(key) == 1:    # Up event dedected
                    # set "time stamp" of button up event
                    self._set_button_signalup_timestamp(key, time.time())
                    # set "time stamp" of the previous button down action
                    # We know this has taken place, otherwise we couldn't have had a
                    # button up action
                    self._set_button_previous_signaldown_timestamp(key)
                    self.logger_instance.info(
                        "RPiInputButton - Up event detected on board {} pin {} for {}".format(
                            _get_board_number(key),
                            _get_pin_number(key),
                            self._get_button_description(key))
                    )
                    # TO-DO: Add code to send "UP-event" message to consummer queue(s)
                    self.process_output_queue_handler.send_message(
                        self.process_consumers[key], message_pre_able+"UP")
                else:                                   # Down event detected
                    # set "time stamp" of button down event
                    self._set_button_signaldown_timestamp(key, time.time())
                    self.logger_instance.info(
                        "RPiInputButton - Down event detected on board {} pin {} for {}".format(
                            _get_board_number(key),
                            _get_pin_number(key),
                            self._get_button_description(key))
                    )
                    # TO-DO: Add code to send "DOWN-event" message to consummer queue(s)
                    self.process_output_queue_handler.send_message(
                        self.process_consumers[key], message_pre_able+"DOWN")
                    # Check to see if we have a Pulse, Long Pulse or Double pulse event
                    # by assessing the duration of the pulse and the time since the previous pulse
                    pulse_duration = self._get_button_signaldown_timestamp(key) -\
                        self._get_button_signalup_timestamp(key)
                    duration_since_last_pulse = self._get_button_signalup_timestamp(key) -\
                        self._get_button_previous_signaldown_timestamp(key)
                    # If the duration since last pulse is more than 1 second
                    # it can no longer be a Double Pulse event.
                    if duration_since_last_pulse > 1:
                        self._reset_button_presscount(key)
                    if pulse_duration > 0.75:
                        # Long button pressed identified
                        self.logger_instance.info(
                            "RPiInputButton - Long button pressed event for {}".format(
                                self._get_button_description(key)))
                        # TO-DO: Add code to send "Long buttong pressed event" message
                        # to consummer queue(s)
                        self.process_output_queue_handler.send_message(
                            self.process_consumers[key],
                            message_pre_able+"PRESSEDLONG")
                    elif pulse_duration > 0.25:
                        # Button pressed identified
                        self.logger_instance.info(
                            "RPiInputButton - Button pressed event for {}".format(
                                self._get_button_description(key)))
                        # TO-DO: Add code to send "Long buttong pressed event" message
                        # to consummer queue(s)
                        self.process_output_queue_handler.send_message(
                            self.process_consumers[key],
                            message_pre_able+"PRESSED")
                    else:
                        # If this is the first "short" pulse (this is a pulse that is shorter
                        # than 0,25 seconds) remember this. It could be the start of
                        # a double button pressed
                        if self._get_button_presscount(key) == 0:
                            # Set the Button Pressed count to 1
                            self._set_button_presscount(key)
                        else:
                            # if this is not the first "short" pulse, it's a double press
                            self.logger_instance.info(
                                "RPiInputButton - Double button pressed event for {}".format(
                                    self._get_button_description(key)))
                            # TO-DO: Add code to send "Long buttong pressed event"
                            # message to consummer queue(s)
                            self.process_output_queue_handler.send_message(
                                self.process_consumers[key],
                                message_pre_able+"PRESSEDDOUBLE")
                            # Reset the Button Pressed Count back to 0
                            self._reset_button_presscount(key)

                #  set "Previous state" to current state
                self._set_previous_button_state(
                    key, self._get_button_state(key))

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
            f"RPiInputButton - Processing Message {message}")

        event_message = json.loads(message)
        if event_message["Type"] == "Processing":
            self.logger_instance.debug(
                f"RPiInputButton - {event_message['Type']} Message received")
            reply = super().process_message(message)
            # When the process attribute list has been refreshed
            # It's also necessary to refresh the inputbutton list to update any
            # changes
            if reply is True and event_message["Event"] == "REFRESH_PROCESS_ATTRIBUTES":
                self.logger_instance.debug(
                    f"RPiInputButton - {event_message['Event']} event received")
                self.input_buttons = self.create_inputbutton_list(
                    self.process_attributes.__repr__())
                self.process_consumers = self.create_message_senders(
                    self.process_attributes.__repr__())

        message_list = message.split(";")
        if message_list[0] == "P":  # A process related message was received,
            reply = super().process_message(message)
            # When the process attribute list has been refreshed
            # It's also necessary to refresh the inputbutton list to update any
            # changes
            if reply is True and message_list[1] == 'REFRESH_PROCESS_ATTRIBUTES':
                self.input_buttons = self.create_inputbutton_list(
                    self.process_attributes.__repr__())
                self.process_consumers = self.create_message_senders(
                    self.process_attributes.__repr__())

        return reply


def _get_board_number(key):
    '''
    function that retrieves the button board number
    '''
    return int(key[1])


def _get_pin_number(key):
    '''
    function that retrieves the button board number
    '''
    return int(key[3])


def main():
    '''
    Initiating the RPiInputButton process including:
        - Parsing the config file and store elements in disctionary => TO DO
    '''

    input_handler_instance = RPiInputButton()

    while input_handler_instance.run_process:
        with input_handler_instance.process_input_queue as consumer:
            input_handler_instance.run_process = consumer.consume(  # pylint: disable=assignment-from-no-return
                input_handler_instance.process_message,
                input_handler_instance.process_input_buttons)


if __name__ == '__main__':
    main()
