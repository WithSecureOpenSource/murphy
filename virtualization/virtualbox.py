'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Simple wrap around virtualbox for instantiating and restoring virtual machines
'''

import subprocess, logging, time, datetime
from virtualization import virtual_machine

LOGGER = logging.getLogger('root.' + __name__)

VIRTUALBOX_DIR = "C:\\Program Files\\Oracle\\VirtualBox\\"

class VirtualBoxMachine(virtual_machine.VirtualMachine):
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

        #FIXME: the damn network interface does reset itself when restoring a
        #snapshot, if we establish a connection too soon it sometimes misses
        #some events (vnc) and wont properly reconnect
        LOGGER.info("Waiting for networking on remote machine to reinitialize")
        time.sleep(5)
        super(VirtualBoxMachine, self).__init__(ip, vnc)
        self.prepared = already_prepared
        virtual_machine.wait_socket_port_ready(ip, port)

    def prepare(self):
        '''
        As per virtual machine contract, adds time sync wait and
        instrumentation
        FIXME: BIG FAT WARNING, it wont work if remote machines (cloud) is
        in a different timezone!
        '''
        super(VirtualBoxMachine, self).prepare()
        if self.helper is None:
            return

        time_in_sync = False
        for _ in range(60):
            stdout, stderr, retcode = self.helper.execute("echo %time%")
            if retcode == 0:
                timestamp = datetime.datetime.now().time()
                hours, mins, secs = stdout.strip().split(":")
                secs, millis = secs.split(",")
                client = (int(hours) * 60 * 60) + (int(mins) * 60) + int(secs)
                client += (int(millis) * 10000 / 1000000.0)
                local = (timestamp.hour * 60 * 60) + (timestamp.minute * 60)
                local += timestamp.second + (timestamp.microsecond / 1000000.0)
                if abs(local - client >= 0.8):
                    LOGGER.debug("Clocks not synced yet... waiting (remote %s,"
                                 "local %s", stdout.strip(), timestamp)
                    time.sleep(1)
                else:
                    LOGGER.debug("Clocks synced: (remote %s, local %s)",
                                 stdout.strip(), timestamp)
                    time_in_sync = True
                    break
                    
        if self.remote_instrumentation_file:
            self.helper.launch(("\\utils\\procmon\\procmon.exe /Minimized "
                                "/Quiet /BackingFile %s") % 
                               self.remote_instrumentation_file)
            launch_command = "\\utils\\procmon\\procmon.exe /WaitForIdle"
            stdout, stderr, retcode = self.helper.execute(launch_command)
            if retcode != 0:
                LOGGER.info("Instrumentation not available in virtual machine, "
                            "ret code is %d, stdout is  %s, stderr is %s",
                            retcode, stdout, stderr)
            else:
                LOGGER.info("Instrumentation data will be available")

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
        ret_val = super(VirtualBoxMachine, self).deallocate()
        if self._automation:
            self._automation.disconnect()
            self._automation = None

        if self.helper:
            self.helper.dispose()
            self.helper = None

        subprocess.check_output([VIRTUALBOX_DIR + "\\vboxmanage.exe",
                                 "controlvm",
                                 self._name,
                                 "poweroff"],
                                 stderr=subprocess.STDOUT)
        return ret_val

    def wait_idling(self):
        '''
        Experimental synchronization against machine load and screen changes
        FIXME: todo... perf counters are different than a real machine or kvm
        '''
        LOGGER.info("Wait for remote machine to be idle...")
        self.automation.wait_stable_screen()
