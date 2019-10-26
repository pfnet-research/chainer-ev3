import logging
import yaml
#import configparser
import numpy as np
import math

SettingsRegistry = {}


class SharedSettings(object):

    @staticmethod
    def create(name, parser, **kwargs):
        obj = SharedSettings(name, parser, **kwargs)
        return obj

    def __init__(self, name, args, **kwargs):
        # register this settings object
        SettingsRegistry[name] = self

        # add all parameters internally
        with open(args.setting_file) as file:
            conf = yaml.safe_load(file)
        for key, val in conf.items():
            setattr(self, key, val)

        # Use a string instead of a list of string, because a list of string is
        # converted into list of unicodes by smt when it's passed as below:
        #   smt run a.cfg global.simulation_cars="['car1','car2']"
        #   -> simulation_cars=[u'car1',u'car2'] (in a generated config file)

        FORMAT = '%(asctime)s.%(msecs)03d %(levelname)-7s %(message)s'
        logging.basicConfig(level=logging.ERROR,
                            format=FORMAT,
                            datefmt='%H:%M:%S')
        self.logger = logging.getLogger(name)

        # Set optional parameters
        for k, v in kwargs.items():
            self.logger.info("optional parameter {0}: {1}".format(k, v))
            setattr(self, k, v)

