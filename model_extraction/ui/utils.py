'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details
'''

from model_extraction.image2 import Image2

TASKBAR_HEIGHT = 41

def dump_array(output, array, key, as_string):
    '''
    Given an array of dictionaries, dumpt the contents of the given key
    '''
    output.write("[")
    for elem in array:
        if as_string:
            output.write("'%s'" % elem[key])
        else:
            output.write("%s" % elem[key])
        if not elem is array[-1]:
            output.write(", ")
    output.write("]")
    
