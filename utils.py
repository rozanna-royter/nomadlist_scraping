import json


def write_dict_to_json(filename, dct):
    """Writes a dictionary to a json file"""
    with open(filename, 'w') as file:
        file.write(json.dumps(dct))


def read_dict_from_json(filename):
    """Reads a json file and returns it as a dictionary"""
    with open(filename, 'r') as file:
        return json.load(file)


def write_list_to_file(filename, lst):
    """Writes a list to a file"""
    with open(filename, 'w') as f:
        for li in lst:
            f.write('%s\n' % li)


def read_list_from_file(filename):
    """Reads list from a file"""
    with open(filename, 'r') as file:
        return file.read().split()
