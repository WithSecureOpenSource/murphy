'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Virtual Machine management interface, used for launching processes, copying
files and so
'''

class Management(object):
    '''
    Base class for virtual machine management API.
    Default implementation uses the provided helper but should be overwritten
    with virtualization specific implementation when desired, for most cases
    default management implementation will suffice
    '''
    def __init__(self, helper):
        self._helper = helper

    def execute(self, command, wait_finishes=True):
        '''
        Runs the given command in the remote machine, if wait_finishes is True
        it returns the std output and std error as a tuple.
        With wait_finishes False will return immediately, no error checking nor
        process wait will occurr
        TODO: run as given user and elevated/non elevated on windows platforms
        '''
        if wait_finishes:
            return self._helper.execute(command)
        else:
            return self._helper.launch(command)

    def get_file(self, remote_filename, local_filename):
        '''
        Fetches the given file from the remote machine and save it locally with
        the given name
        '''
        self._helper.get_file(remote_filename, local_filename)

    def put_file(self, local_filename, remote_filename):
        '''
        Put the given file in the remote machine
        '''
        raise RuntimeError("Not implemented")

    @property
    def network(self):
        '''
        Returns True if the network interface is enabled, false otherwise
        '''
        raise RuntimeError("Not implemented")

    @network.setter
    def network(self, state=True):
        '''
        Set to True to enable the network, false otherwise
        '''
        raise RuntimeError("Not implemented")
