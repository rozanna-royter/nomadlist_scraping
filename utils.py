import json
import os
import sys
import config


def go_to_url(driver, url):
    """
    Navigates the browser to the url
    :param driver: The instantiated web driver
    :param url: URL to navigate to
    :return: None
    """
    driver.get(url)


def write_dict_to_json(filename, dct):
    """
    Writes a dictionary to a json file
    :param filename: Name of file to write to
    :param dct: Dictionary that's being written
    :return: None
    """
    check_if_file_exists(filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(dct))


def read_dict_from_json(filename):
    """
    Reads a json file and returns it as a dictionary
    :param filename: Name of file to read
    :return: A json dictionary from file
    """
    check_if_file_exists(filename)
    with open(filename, 'r') as file:
        return json.load(file)


def write_list_to_file(filename, lst):
    """
    Writes a list to a file
    :param filename: Name of file to write to
    :param lst: List that's being written
    :return: None
    """
    check_if_file_exists(filename)
    with open(filename, 'w') as f:
        for li in lst:
            f.write('%s\n' % li)


def read_list_from_file(filename):
    """
    Reads list from a file
    :param filename: Name of file to read
    :return: List from file
    """
    check_if_file_exists(filename)
    with open(filename, 'r') as file:
        return file.read().split()


def check_if_file_exists(filename):
    """
    Prints an error if file doesn't exist
    :param filename: Name of file to check
    :return: None
    """
    if not os.path.isfile(filename):
        print(f"File {filename} doesn't exist")
        sys.exit(1)


def get_new_items(existing_list, new_list):
    """
    Returns a list of items that are present in new_list, but not present in existing_list.
    Same as set, but keeping the order
    :param existing_list: List to check against
    :param new_list: List of items
    :return: List of new items
    """
    res_list = []
    for li in new_list:
        if li not in existing_list:
            res_list.append(li)
    return res_list


def get_chromedriver_path():
    """
    Gets the correct chromedriver based on your system
    :return: Path to chromedriver
    """
    osname = sys.platform
    try:
        return config.OS_DRIVER_PATHS.get(osname)
    except:
        raise NotImplementedError(f"Unknown OS '{osname}'")
