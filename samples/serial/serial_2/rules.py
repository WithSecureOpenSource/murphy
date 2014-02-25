def get_remoting_vnc_object():
    import time
    from model_extraction import virtualbox, configuration

    config = configuration.get_default_config()
    ret = virtualbox.VirtualBoxMachine(name=config["image name"],
                                       snapshot=config["snapshot"],
                                       already_prepared=config["already prepared"])
    ret.prepare_command = config["prepare command"]
    time.sleep(10)
    return ret
        
def is_path_valid(path, consider_only_last_node = True):
    return True
    