'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

import sys, logging
from murphy.model import Model

def run_remote_test(test_function, model_file):
    remoting_obj = None
    try:
        model = Model(model_file)
        remoting_obj = model.rules.get_remoting_vnc_object()
        worker = model.new_worker(remoting_obj.automation)
        test_function(worker)
        print "PASS"
    except Exception, e:
        print "FAILED TEST, error: %s" % str(e)
    finally:
        if remoting_obj:
            remoting_obj.deallocate()
           

def run_local_test(test_function, model_file):
    try:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        model = Model(model_file)
        worker = model.new_worker()
        test_function(worker)
        print "PASS"
    except Exception, e:
        print "FAILED TEST, error: %s" % str(e)
