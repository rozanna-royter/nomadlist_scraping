import json
import os
import sys

PATH_TO_CHROMEDRIVER_MACOS = 'Drivers/macos/chromedriver'
PATH_TO_CHROMEDRIVER_LINUX = 'Drivers/linux/chromedriver'
PATH_TO_CHROMEDRIVER_WINDOWS = 'Drivers/windows/chromedriver.exe'


def write_dict_to_json(filename, dct):
    """Writes a dictionary to a json file"""
    check_if_file_exists(filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(dct))


def read_dict_from_json(filename):
    """Reads a json file and returns it as a dictionary"""
    check_if_file_exists(filename)
    with open(filename, 'r') as file:
        return json.load(file)


def write_list_to_file(filename, lst):
    """Writes a list to a file"""
    check_if_file_exists(filename)
    with open(filename, 'w') as f:
        for li in lst:
            f.write('%s\n' % li)


def read_list_from_file(filename):
    """Reads list from a file"""
    check_if_file_exists(filename)
    with open(filename, 'r') as file:
        return file.read().split()


def check_if_file_exists(filename):
    """Prints an error if file doesn't exist"""
    if not os.path.isfile(filename):
        print(f"File {filename} doesn't exist")
        sys.exit(1)


def get_new_items(existing_list, new_list):
    """
    Returns a list of items that are present in new_list, but not present in existing_list.
    Same as set, but keeping the order
    """
    res_list = []
    for li in new_list:
        if li not in existing_list:
            res_list.append(li)
    return res_list


def get_chromedriver_path():
    osname = sys.platform
    if osname == 'darwin':
        return PATH_TO_CHROMEDRIVER_MACOS
    elif osname == 'win32':
        return PATH_TO_CHROMEDRIVER_WINDOWS
    elif osname in ('linux', 'linux2'):
        return PATH_TO_CHROMEDRIVER_LINUX
    else:
        raise NotImplemented(f"Unknown OS '{osname}'")
