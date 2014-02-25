'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Utility module with general purpose functions used by murphy framework
FIXME: this module needs to move some routines out of here
'''

import types, json, os
import subprocess
from murphy.path_tested import StepState

#fixme: make clear guides for naming and good error descriptions

def is_valid_view_name(name):
    '''
    Returns True if the given view name is valid for murphy convention
    A valid name is composed with words whose first letter is capitalized
    '''
    if name.find("  ") != -1:
        return False
    if name.find(".") != -1:
        return False

    return True
    words = name.split(" ")
    for word in words:
        if word != word[0].upper() + word[1:].lower():
            return False

    return True


def is_valid_verb_name(name):
    '''
    Returns True if the given module verb is valid for murphy convention
    A valid name is composed with first word Capitalized and the rest
    are lowercased
    '''
    if name.find("  ") != -1:
        return False
    if name.find(".") != -1:
        return False

    words = name.split(" ")
    first = True
    for word in words:
        if first:
            if word != word[0].upper() + word[1:].lower():
                return False
            first = False
        else:
            if word != word.lower():
                return False

    return True


def is_valid_module(module):
    '''
    Valid module means it is usable for murphy as it contains
    the self description needed for it's usage
    A module is valid if it has a here dictionary with a desc key
    '''
    there = None
    if module.__dict__.has_key("HERE"):
        there = module.HERE

    if there:
        if isinstance(there, types.DictType):
            if there.has_key("desc"):
                if not is_valid_view_name(there['desc']):
                    raise Exception(("Module %s description '%s' is invalid, " +
                                     "all words must be capitalized, for " +
                                     "example Clean Machine") % (
                                     module.__name__, there['desc']))
                else:
                    return True
    return False

def list_verbs(module):
    '''
    Returns a dictionary containing all the recognizable verbs for the
    given module, verbs are module level fields that starts with v_ or V_
    '''
    module_verbs = dict()

    for elem in module.__dict__:
        if elem[0:2].lower() == "v_":
            if not 'desc' in module.__dict__.get(elem):
                raise Exception("Verb %s in %s does not contain valid desc" % (elem, module.__name__))
            desc = module.__dict__.get(elem)['desc']
            if not is_valid_verb_name(desc):
                raise Exception(("Verb description '%s' is invalid, 1st word " +
                                 "must be capitalized, next ones lowercases, " +
                                 "'.' and multiple spaces are not permitted") %
                                desc)
            if desc in module_verbs:
                raise Exception("There are more than one verb with the same " +
                                "description in module " + module.HERE['desc'])
            module_verbs[desc] = module.__dict__.get(elem)

    return module_verbs


def load_text_file(file_name):
    '''
    Convenience method for loading a text file
    '''
    a_file = open(file_name, "r")
    try:
        ret = "".join(a_file.readlines())
    finally:
        a_file.close()
    return ret


def save_file(content, file_name):
    '''
    Saves the content into a file
    '''
    a_file = open(file_name,"w")
    try:
        a_file.write(content)
    finally:
        a_file.close()


def load_json_object(file_name):
    '''
    Convenience method for loading an object from file using json encode
    '''
    a_file = open(file_name, "rb")
    try:
        ret = json.load(a_file)
    finally:
        a_file.close()
    return ret


def save_json_object(obj, file_name):
    '''
    Convenience method for saving an object into a file using json encode
    '''
    a_file = open(file_name, 'wb')
    try:
        json.dump(obj, a_file)
    finally:
        a_file.close()


def load_coverage(file_name):
    '''
    Loads coverage file, it is an array of arrays of StepStates
    encoded in json format
    '''
    if os.path.isfile(file_name):
        dict_content = load_json_object(file_name)
        ret_array = []
        for run in dict_content:
            run_array = []
            for step in run:
                run_array.append(StepState.decode(step))
            ret_array.append(run_array)
        return ret_array
    else:
        return []

def encode_coverage(coverage):
    save_array = []
    for run in coverage:
        run_array = []
        for step in run:
            run_array.append(step.encode())
        save_array.append(run_array)
    return save_array
    
def save_coverage(coverage, file_name):
    '''
    Saves coverage file, coverage must be an array of arrays of StepStates
    The file will be encoded in json
    '''
    save_array = encode_coverage(coverage)
    save_json_object(save_array, file_name)


class CommandException(Exception):
    '''
    Exception raised when executing a command fails, provides appropriate
    methods for getting the return code, std output and std error of the
    executed command
    '''
    def __init__(self, description, retcode, stdout, stderr):
        super(CommandException, self).__init__(description)
        self._return_code = retcode
        self._stdout = stdout
        self._stderr = stderr

    @property
    def return_code(self):
        '''
        Returns the return code of the executed command
        '''
        return self._return_code

    @property
    def std_out(self):
        '''
        Returns the standard output captured when the command was executed
        '''
        return self._stdout

    @property
    def std_err(self):
        '''
        Returns the standard error captured when the command was executed
        '''
        return self._stderr


def launch_command(cmd, args=None, working_dir=None):
    '''
    Launches the given command and returns the process immediately (wont wait
    for process to finish)
    This method will hide any command window if the given process will show
    one
    If cmd fails (return code other than 0) it will raise a CommandException
    containing the return code, std out and std err of the executed command
    Example:
    proc = launch_command("test.bat",
        ["1st param", "-c"],
        "c:\\temp\\dir with spaces")
    Use execute_command instead if you want instead to wait for the process
    to finish.
    '''

    the_command = [cmd]
    if args:
        the_command = the_command + args

    startupinfo = subprocess.STARTUPINFO()
    subprocess.STARTF_USESHOWWINDOW = 1
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    #TODO: add logging
    try:
        process = subprocess.Popen(the_command,
                                   startupinfo=startupinfo,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=working_dir)
    except Exception, unexpected:
        print "Launch command failed, command was %s, working dir was %s" % (str(the_command), str(working_dir))
        print "Launch command exception was %s" % unexpected
        raise

    return process


def execute_command(cmd, args=None, working_dir=None):
    '''
    Executes the given command and returns stdout and stderr as tuple once the
    process has finished
    This method will hide any command window if the given process will show
    one
    If cmd fails (return code other than 0) it will raise a CommandException
    containing the return code, std out and std err of the executed command
    Example:
    execute_command("test.bat", ["1st param", "-c"], "c:\\temp\\dir with spaces")
    Use launch_command instead if you dont want to wait for the process to
    finish
    '''
    process = launch_command(cmd, args, working_dir)
    pout, perr = process.communicate()
    process.wait()

    if process.returncode != 0:
        desc = ("Failed when executing command %s %s, return code was %s\n" +
                         "Std Output is:\n%s\n" +
                         "Std Error is:\n%s") % (cmd,
                                                 str(args),
                                                 str(process.returncode),
                                                 pout,
                                                 perr)
        raise CommandException(desc, process.returncode, pout, perr)

    return pout, perr

