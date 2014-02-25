'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Simple wrap around virtualbox for instantiating and restoring virtual machines
'''

import subprocess, time, socket
import logging
LOGGER = logging.getLogger('root.' + __name__)

from model_extraction import vm_world

VIRTUALBOX_DIR = "C:\\Program Files\\Oracle\\VirtualBox\\"
    
class VirtualBoxMachine(vm_world.VirtualMachine):
    '''
    Simple class for allocating and deallocating virtual machines.
    VirtualBox does not provide VNC connectivity so it has to be installed
    as a service in the operating system
    Customize this class as appropriate with the ip and port addresses
    Most information as host ip can be obtained by querying virtual box instead
    of hardcoding it.
    '''
    def __init__(self, name, snapshot=None, already_prepared=False,
      ip='192.168.56.1', port=5900):
        self._name = name
        vnc = {'host': ip,
               'port': port,
               'user': None,
               'password': None}
               
        if snapshot is None:
            raise ValueError("No snapshot name specified")
        
        subprocess.check_output([VIRTUALBOX_DIR + "\\vboxmanage.exe",
                                 "snapshot",
                                 name,
                                 "restore",
                                 snapshot],
                                 stderr=subprocess.STDOUT)
                                 
        subprocess.check_output([VIRTUALBOX_DIR + "\\vboxmanage.exe",
                                 "startvm",
                                 name,
                                 "--type",
                                 "headless"],
                                 stderr=subprocess.STDOUT)
        
        super(VirtualBoxMachine, self).__init__(ip, vnc)
        self.prepared = already_prepared
        vm_world.wait_socket_port_ready(ip, port)
        
    @property
    def automation(self):
        '''
        Returns the automation interface (user, screen, keyboard) tweaking
        an annoying thing with kvm keyboard and vnc
        FIXME: the default should be not tweaked and moved into kvm_machine
        and not here
        '''
        ret = super(VirtualBoxMachine, self).automation
        ret.keyboard.tweak_kb = False
        return ret

        
    def deallocate(self):
        '''
        Stops this virtual machine, all unsaved information will be lost.
        '''
        if self._automation:
            self._automation.disconnect()
            self._automation = None
        
        if self.helper:
            try:
                self.helper._connection.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.helper._connection.close()
            except:
                pass
            self.helper = 0
                
        subprocess.check_output([VIRTUALBOX_DIR + "\\vboxmanage.exe",
                                 "controlvm",
                                 self._name,
                                 "poweroff"],
                                 stderr=subprocess.STDOUT)

    def wait_idling(self):
        '''
        Experimental synchronization against machine load and screen changes
        FIXME: todo... perf counters are different than a real machine or kvm
        '''
        LOGGER.info("Wait for remote machine to be idle...")
        self.automation.wait_stable_screen()