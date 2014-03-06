'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details
'''

def get_remoting_vnc_object():
    import time
    from model_extraction import configuration
    from virtualization import virtualbox

    config = configuration.get_default_config()
    ret = virtualbox.VirtualBoxMachine(name=config["image name"],
                                       snapshot=config["snapshot"],
                                       already_prepared=config["already prepared"])
    ret.prepare_command = config["prepare command"]
    ret.remote_instrumentation_file = config.get("remote logs")
    return ret
        
def is_path_valid(path, consider_only_last_node=True):
    return True
    