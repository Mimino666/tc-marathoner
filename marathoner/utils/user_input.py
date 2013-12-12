from six.moves import input


def get_input(msg, valid_values):
    while True:
        result = input(msg+' ').lower()
        if result in valid_values:
            return result
