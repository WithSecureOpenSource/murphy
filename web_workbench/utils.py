'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Almost generic routines
'''
import os, re, base64

def silent_remove(file_name):
    '''
    Silently remove a file, ignore errors that may happen due to file not found
    and so (caller knows there are sync risks when deleting)
    '''
    try:
        os.remove(file_name)
    except:  # pylint: disable=W0702
        pass


def files_modified_since(dirname, since):
    '''
    Returns True if any .py or .json file were modified since the given time.
    since must be of mtime type, for example:
        since = os.stat(a_file_name).st_mtime
    If dirname does not exists it returns True
    '''

    if not os.path.isdir(dirname):
        return True

    for root, _, files in os.walk(dirname):  # Walk directory tree
        for a_file in files:
            full_name = root + "/" + a_file
            file_time = os.stat(full_name).st_mtime
            if file_time > since:
                return True

    return False

def read_binary_file(file_name):
    '''
    Returns the whole content of the given file
    '''
    buff = ''
    with open(file_name, "rb") as a_file:
        byte = a_file.read(1)
        while byte != "":
            buff += byte
            byte = a_file.read(1)
    return buff


def _inline_it(matchobj):
    '''
    Return the image inlined inside the html object
    '''
    file_name = matchobj.group(1)
    if file_name.endswith(".png"):
        return ('xlink:href="data:image/png;base64,%s"' %
                                base64.b64encode(read_binary_file(file_name)))
    elif file_name.endswith(".gif"):
        return ('xlink:href="data:image/gif;base64,%s"' % 
                                base64.b64encode(read_binary_file(file_name)))
    else:
        return matchobj.group(0)


def inline_images(file_name):
    '''
    Inline images in the given file, note that it is specially coded for the
    svg files being generated.
    '''
    with open(file_name, 'r') as a_file:
        content = a_file.readlines()
    content = "".join(content)
    content = re.sub('xlink:href=\"(.+?)\"', _inline_it, content)
    new_name = (os.path.dirname(file_name) + "/inlined_" + 
                os.path.basename(file_name))
    with open(new_name, "w") as a_file:
        a_file.write(content)


