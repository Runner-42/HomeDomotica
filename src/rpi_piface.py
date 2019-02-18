'''
Name:		RPiPiface.py
Purpose:	The Piface class is used to initiate and interact with
            the piface cards

Author:	    Wim

Created:	9/09/2018
Copyright:	(c) Wim 2018
Licence:
'''

import pifacedigitalio
from pifacedigitalio import NoPiFaceDigitalDetectedError

class RPiPiface():
    '''
    This class is created to handle piface specific functionaity
    It's been implemented to avoid code duplication in those processes
    making use of a piface board like rpi_inputbutton, rpi_outputrelay...etc
    Following attributes are defined in the RPiInputButton class:
        - piface => List of pifacedigitalio objects. One item per Piface Board
        - number_of_boards => total number of Piface boards detected
    '''
    
    def __init__(self):
        self.piface = []
        self.number_of_boards = 0
        for board in range(0, 5):
            # A maximim of 4 boards can be installed, each with a dedicated address 0, 1, 2 or 3
            # We will try to initialize a board with these addresses
            # Once the initialization fails (and it eventually will fail when we try address 4)
            # we return the last successfull initialized board
            # Note: this will be 0 when no boards are dedected
            try:
                self.piface.append(pifacedigitalio.PiFaceDigital(board))
            except NoPiFaceDigitalDetectedError:
                self.number_of_boards = board

                break   # we assume that there are no gaps in the addresses of
                        # the PiFace boards so we exit the for loop

    def __str__(self):
        long_string = "Number of PiFace boards detected: {}\n".format(self.number_of_boards)
        return long_string

    def get_number_of_boards(self):
        return self.number_of_boards

    # Methods related to the digital inputs
    def get_input_button_state(self, board_number, input_number):
        '''
        get method to retrieve the actual status of a digital input
        2 parameters need to be provide:
        - board_number: allow values 0->3
        - input_number to represent the pin: allowed values 0->7 
        '''
        if (0 <= board_number < self.number_of_boards) and (0 <= input_number <= 7):
            return self.piface[board_number].input_pins[input_number].value
        else:
            return -1

    # Methods related to the digital outputs
    def get_output_pin_state(self, board_number, pin_number):
        '''
        get method to retrieve the actual status of a digital output
        2 parameters need to be provide:
        - board_number: allow values 0->3
        - pin_number to represent the pin: allowed values 0->7 
        '''
        if (0 <= board_number < self.number_of_boards) and (0 <= pin_number <= 7):
            return self.piface[board_number].output_pins[pin_number].value
        else:
            return -1

    def set_output_pin(self, board_number, pin_number):
        '''
        set method to put the actual status of a digital output to 'on'
        2 parameters need to be provide:
        - board_number: allow values 0->3
        - pin_number to represent the pin: allowed values 0->7 
        '''
        if (0 <= board_number < self.number_of_boards) and (0 <= pin_number <= 7):
            self.piface[board_number].output_pins[pin_number].value = 1

    def reset_output_pin(self, board_number, pin_number):
        '''
        set method to put the actual status of a digital output to 'off'
        2 parameters need to be provide:
        - board_number: allow values 0->3
        - pin_number to represent the pin: allowed values 0->7 
        '''
        if (0 <= board_number < self.number_of_boards) and (0 <= pin_number <= 7):
            self.piface[board_number].output_pins[pin_number].value = 0

    # Methods related to the output relays
    def get_output_relay_state(self, board_number, relay_number):
        '''
        get method to retrieve the actual status of a digital output
        2 parameters need to be provide:
        - board_number: allow values 0->3
        - relay_number: allowed values 0->1 
        '''
        if (0 <= board_number < self.number_of_boards) and (0 <= relay_number <= 1):
            return self.piface[board_number].relays[relay_number].value
        else:
            return -1

    def set_output_relay(self, board_number, relay_number):
        '''
        set method to put the actual status of a digital output to 'on'
        2 parameters need to be provide:
        - board_number: allow values 0->3
        - relay_number: allowed values 0->1 
        '''
        if (0 <= board_number < self.number_of_boards) and (0 <= relay_number <= 1):
            self.piface[board_number].relays[relay_number].value = 1

    def reset_output_relay(self, board_number, relay_number):
        '''
        set method to put the actual status of a relay to 'off'
        2 parameters need to be provide:
        - board_number: allow values 0->3
        - relay_number: allowed values 0->1 
        '''
        if (0 <= board_number < self.number_of_boards) and (0 <= relay_number <= 1):
            self.piface[board_number].relays[relay_number].value = 0