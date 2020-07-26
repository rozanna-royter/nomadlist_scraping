import logging
import sys


class Logger(object):
    """
    Class for setting up the logger
    """

    def __init__(self, name):
        # Gets or creates a logger
        self.logger = logging.getLogger(name)
        # set log level
        self.logger.setLevel(logging.INFO)
        # define file handler and set formatter
        file_handler = logging.FileHandler(f'{name}.log')
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        file_handler.setFormatter(formatter)
        # add file handler to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
