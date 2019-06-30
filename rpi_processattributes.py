'''
Name:		RPiProcessAttributes.py
Purpose:	Class RPiProcessAttributes that is used to store all parameter
            information required by the different process in the Homedomotica
            service

Author:	Wim

Created:	19/05/2018
Copyright:	(c) Wim 2018
Licence:
'''

class RPiProcessAttributes():
    '''
    This class encapsulates the attributes used within the different processes
    in the Homedomitica service.

    The attributes are stored as a key-value pair in a dictionary
    '''

	# Initiator Method

    def __init__(self, p_attributes=None):
        #	(Private) Attributes
        if isinstance(p_attributes, dict):   # Check if the parameter is of type 'dictionary'
            self._dict_process_attributes = p_attributes
        else:
            if p_attributes is None:
                self._dict_process_attributes = {}
            else:
                self._dict_process_attributes = None

    # Standard Methods

    def __repr__(self):
        return self._dict_process_attributes

    def __str__(self):
        if self._dict_process_attributes is None:
            _return_string = None
        else:
            _return_string = ""
            for key, value in self._dict_process_attributes.items():
                _return_string += "{} = {}\n".format(key, value)

        return _return_string

    # Other Methods
    def push_item(self, p_attributes={}):   # pylint: disable=dangerous-default-value
        '''
        method to add a single key-value to the dictionary
        '''
        if isinstance(p_attributes, dict):   # Check if the parameter is of type 'dictionary'
            self._dict_process_attributes.update(p_attributes)

        return self._dict_process_attributes

    def delete_item(self, key_to_remove):
        '''
        method to remove a single key-value from the dictionary
        '''
        if key_to_remove in self._dict_process_attributes:
            self._dict_process_attributes.pop(key_to_remove)

        return self._dict_process_attributes

    def delete_all_items(self):
        '''
        method to delete all key-values from the dictionary
        '''
        self._dict_process_attributes.clear()

        return self._dict_process_attributes

    def get_item(self, key):
        '''
        method to retrieve a single value from the dictionary
        '''
        if key in self._dict_process_attributes:
            return self._dict_process_attributes[key]
        return None

def main():
    '''
    main function, mainly used for testing purposes
    '''
    print("Hello world")
    new_instance = RPiProcessAttributes()
    print(new_instance.__repr__())
    new_instance.push_item()
    data = {'key': 'value', 'man': 'wim', 'vrouw': 'Krista', 5: 'nummertje'}
    new_instance.push_item(data)
    print(new_instance.__str__())
    print(new_instance.__repr__())
    new_instance.delete_item('vrouw')
    print(new_instance.__str__())
    print(new_instance.__repr__())
    print("Bye world")

if __name__ == '__main__':
    main()
