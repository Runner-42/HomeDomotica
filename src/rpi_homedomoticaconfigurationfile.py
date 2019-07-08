'''
Name:		RPiHomedomoticaConfigurationFile.py
Purpose:	Class HomedomoticaConfigurationFile is used to handle the
            configration file used by the different Homedomotica processes

Author:	Wim

Created:	21/05/2018
Copyright:	(c) Wim 2018
Licence:
'''

from sys import platform
import os

class RPiHomedomoticaConfigurationFile():
    '''
    This class is created to handle the configuration file used by the
    different homedomotica processes. This includes, reading the content
    of the file and verifying the correctness of this file

    A valid configuration file can have 3 types of lines:
        - Comment lines. These lines start with a '#' character. Leading spaces are permitted
        - Key-value pair, separated by an '=' character.
        - Keyword, indicating a start of a block in the configuration file. This keyword needs to
          be placed between []
    Examples of valid configuration file entries:
        # This is a valid comment lines
           # This is another one
        [S_RPIINPUTHANDLER]
        OutputHandler1 = [S_RPIOUTPUTHANDLER1]
        ButtonHandler2=[S_RPIINPUTHANDLER2]
    '''

    VALID_KEYWORDS = ("ConsumerQueue1", "ConsumerQueue2", "ConsumerQueue3",\
                      "ConsumerQueue4", "ConsumerQueue5", "ConsumerQueue6",\
                      "ConsumerQueue7", "ConsumerQueue8", "ConsumerQueue9",\
                      "[RPI_INPUTBUTTON]", "[RPI_INPUTBUTTON_PI1]", "[RPI_INPUTBUTTON_PI2]",\
                      "[RPI_INPUTBUTTON_PI3]", "[RPI_INPUTBUTTON_TST2]", "[RPI_OUTPUTLIGHTS]",\
                      "[RPI_OUTPUTLIGHTS_PI1]","[RPI_OUTPUTLIGHTS_PI2]", "[RPI_OUTPUTLIGHTS_PI3]",\
                      "[RPI_OUTPUTLIGHTS_TST2]", "[RPI_OUTPUTDIMMER]", "[RPI_OUTPUTDIMMER_PI1]",\
                      "[RPI_OUTPUTDIMMER_PI2]","[RPI_OUTPUTDIMMER_PI3]","[RPI_OUTPUTDIMMER_TST2]",\
                      "[RPI_OUTPUTRELAY]", "[RPI_OUTPUTRELAY_PI1]", "[RPI_OUTPUTRELAY_PI2]",\
                      "[RPI_OUTPUTRELAY_PI3]", "[RPI_OUTPUTRELAY_TST2]", "Port", "Host_IP",\
                      "[RPI_LIGHTSIMULATOR_TSTMGMT]", "[RPI_LIGHTSIMULATOR_MGMT]",\
                      "Button00", "Button01", "Button02", "Button03", "Button04",\
                      "Button05", "Button06", "Button07", "Button10", "Button11", "Button12",\
                      "Button13", "Button14", "Button15", "Button16", "Button17", "Button20",\
                      "Button21", "Button22", "Button23", "Button24", "Button25", "Button26",\
                      "Button27", "Button30", "Button31", "Button32", "Button33", "Button34",\
                      "Button35", "Button36", "Button37", "Output00",\
                      "Light00", "Light01", "Light02", "Light03", "Light04",\
                      "Light05", "Light06", "Light07", "Light10", "Light11", "Light12",\
                      "Light13", "Light14", "Light15", "Light16", "Light17", "Light20",\
                      "Light21", "Light22", "Light23", "Light24", "Light25", "Light26",\
                      "Light27", "Light30", "Light31", "Light32", "Light33", "Light34",\
                      "Light35", "Light36", "Light37",\
                      "Dimmer00", "Dimmer01", "Dimmer02", "Dimmer03", "Dimmer04",\
                      "Dimmer05", "Dimmer06", "Dimmer07", "Dimmer10", "Dimmer11", "Dimmer12",\
                      "Dimmer13", "Dimmer14", "Dimmer15", "Dimmer16", "Dimmer17", "Dimmer20",\
                      "Dimmer21", "Dimmer22", "Dimmer23", "Dimmer24", "Dimmer25", "Dimmer26",\
                      "Dimmer27", "Dimmer30", "Dimmer31", "Dimmer32", "Dimmer33", "Dimmer34",\
                      "Dimmer35", "Dimmer36", "Dimmer37",\
                      "Relay00", "Relay01", "Relay10", "Relay11", "Relay20", "Relay21",\
                      "Relay30", "Relay31",\
                      "Simulation00", "Simulation01", "Simulation02", "Simulation03",\
                      "Simulation04", "Simulation05", "Simulation06", "Simulation07",\
                      "Simulation08", "Simulation09", "Simulation10", "Simulation11")

	# Initiator Method

    def __init__(self, file_name="Homedomotica.cfg", file_path="/home/homedomotica/"):
        if platform == "win32":
            self._path_separator = "\\"
        else:
            self._path_separator = "/"

        self._file_name = file_name
        self._file_path = file_path
        if self._file_path[-1] == self._path_separator:
            self._full_file_name = self._file_path + self._file_name
        else:
            self._full_file_name = self._file_path + self._path_separator + self._file_name

        # We assume the config file is valid
        self.invalid_config_file = False
        self.invalid_keyword_list = []

    # Standard Methods
    def __repr__(self):
        return self._full_file_name

    def __str__(self):
        _return_string = ""

        _return_string = "Config file name: {}\n".format(self._full_file_name)
        return _return_string

    # Other Methods

    def exist(self):
        '''
        The exist method will check if a file, presented by the _full_file_name exists
        and is not empty.
        The function returns True if the file is present and contains data, False if not
        '''
        return os.path.isfile(self._full_file_name) and os.path.getsize(self._full_file_name) > 0

    @classmethod
    def get_keyword(cls, configuration_line_item):
        '''
        The get_keyword() method will extract the keyword from the string presented by parameter
        configuration_line_item
        In case a "keyword" is found, it is returned, None if not
        '''
        # Strip leading spaces and new line character
        configuration_line_item = str(configuration_line_item).lstrip().rstrip('\n')

        # check if the provided string is a comment line
        if configuration_line_item[0] == '#':
            return None     # No keyword found

        if configuration_line_item[0] == '[':       # start of 'Block' line found
            position = configuration_line_item.find(']')
            if position == -1:                      # No ']' character in the string found
                #self.invalid_keyword_list.append(configuration_line_item)
                keyword = None
            else:
                keyword = configuration_line_item[:position+1]
        else:
            if '=' in configuration_line_item:
                keyword, value = str(configuration_line_item).split('=')    # pylint: disable=unused-variable
                # Remove any leading or trailing spaces
                keyword = str(keyword).lstrip().rstrip()
            else:
                #self.invalid_keyword_list.append(configuration_line_item)
                keyword = None

        return keyword

    @classmethod
    def get_key_value(cls, configuration_line_item):
        '''
        The get_key_value() method will extract the value from the string presented
        by parameter configuration_line_item
        In case a "value" is found, it is returned, None if not
        '''
        # Strip leading spaces and new line character
        configuration_line_item = str(configuration_line_item).lstrip().rstrip('\n')

        # check if the provided string is a comment line or
        # a Key word indicating the start of a block
        if configuration_line_item[0] == '#' or configuration_line_item[0] == '[':
            return None     # No key value found

        if '=' in configuration_line_item:
            keyword, value = str(configuration_line_item).split('=')    # pylint: disable=unused-variable
            # Remove any leading or trailing spaces and return value
            return str(value).lstrip().rstrip()
        return None     # No key value found

    def is_valid_keyword(self, configuration_line_item):
        '''
        The is_valid_keyword() method will extract the key from the string presented by parameter
        configuration_line_item
        In case the "key" is found in the VALID_KEYWORDS list, True is returned, False if not
        '''
        if self.get_keyword(configuration_line_item) in self.VALID_KEYWORDS:
            return True

        self.invalid_keyword_list.append(str(configuration_line_item).lstrip().rstrip('\n'))
        return False

    @classmethod
    def is_comment_line(cls, configuration_line_item):
        '''
        The is_comment_line() method will check if the string presented by parameter
        configuration_line_item is a comment line
        In case it is True is returned, False if not
        '''
        # Strip leading spaces
        configuration_line_item = str(configuration_line_item).lstrip()

        if configuration_line_item[0] == '#':
            return True

        return False

    def is_valid_config_file(self):
        '''
        The is_valid_config_file() method will read each line in the configuration file
        and check if these entres are valid
        In case all lines are valid True is returned, False if not
        A file is considered valid when:
        - All keys in the file are valid keywords
        - Key-value pairs have a value that is not empty
        - The file exists (and is not empty)
        '''
        # Initiate some counters
        valid_lines_count = 0
        invalid_lines_count = 0
        comment_lines_count = 0

        if self.exist():
            with open(self._full_file_name, 'r') as file:
                for line in file:
                    if self.is_comment_line(line):
                        comment_lines_count += 1    # We have found a comment line
                    else:
                        if self.is_valid_keyword(line):
                        # Keyword is valid
                            if self.get_keyword(line)[0] == '[':
                                valid_lines_count += 1  # We have found a valid line
                            else:
                                if self.get_key_value(line) is None:
                                # We are expecting a Key-value pair, line is invalid
                                    invalid_lines_count += 1
                                else:
                                # We have found a Key-value pair, line is valid
                                    valid_lines_count += 1
                        # Keyword is not valid
                        else:
                            invalid_lines_count += 1
        else:
            self.invalid_keyword_list.append(
                "{} does not exist or is empty!".format(self._full_file_name))

        # In case we have not find a single valid line, must be something wrong
        if (valid_lines_count == 0) or (invalid_lines_count > 0):
            self.invalid_config_file = True
            return False

        return True    # No invalid lines found and at least one valid one

    def read_configuration_file(self, block_keyword):
        '''
        The read_configuration_file() method will read all key-value pairs in
        a (valid) configuration file and return these in a dictionary
        In case of an invalid file, None is returned
        '''
        if self.is_valid_config_file():
            found_block = False
            dic_to_return = {}
            with open(self._full_file_name, 'r') as file:
                # Scan through the file until the block_keyword is found
                for line in file:
                    if not self.is_comment_line(line):          # We can skip the comment lines
                        if found_block:
                            key = self.get_keyword(line)
                            if key[0] == '[':
                                found_block = False             # We have reached the next block
                            else:
                                value = self.get_key_value(line)
                                dic_to_return.update({key: value})
                        if self.get_keyword(line) == block_keyword:
                            found_block = True

            return dic_to_return

        return None         # In case the configuration file is not valid, we return None

def main():
    '''
    main function used mainly for testing purposes
    '''
    print("Hello world")
    file_instance = RPiHomedomoticaConfigurationFile("rpi_inputbutton.cfg")
    print(file_instance.__str__())
    print("Valid configuration file: ", file_instance.is_valid_config_file())
    content = file_instance.read_configuration_file("[RPI_INPUTBUTTON]")
    print(content)
    print("Bye world")

if __name__ == '__main__':
    main()
