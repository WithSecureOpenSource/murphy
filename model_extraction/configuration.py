"""
Copyright (c) 2011-2014 F-Secure
See LICENSE for details
"""

import os, json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = THIS_DIR + '/default_config.json'
CUSTOM_CONFIG = THIS_DIR + '/custom_config.json'

def get_config():
    with open(DEFAULT_CONFIG, "rb") as the_file:
        default = json.load(the_file)

    try:
        with open(CUSTOM_CONFIG, "rb") as the_file:
            custom = json.load(the_file)
        default["configurations"].update(custom["configurations"])
        if "default configuration" in custom:
            default["default configuration"] = custom["default configuration"]
            
    except IOError:
        pass #unreadable, or may not exists, or just deleted, or hell is frozen
    
    default["default configuration"] = default['configurations'][default['default configuration']]
    return default
    
def get_default_config():
    return get_config()["default configuration"]
    
