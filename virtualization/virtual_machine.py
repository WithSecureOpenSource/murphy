'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details
'''

import socket, time, logging, uuid
from murphy.user_simulation.vnc.vnc_user import User
LOGGER = logging.getLogger('root.' + __name__)

from virtualization import vm_manage, vm_helper

#FIXME: There may be a better place for this...
def wait_socket_port_ready(ip, port, max_timeout=60):
    '''
    Waits until the connection to the given ip-port can be established, used
    as to synchronize when a virtual machine started up
    '''
    for _ in range(max_timeout):
        try:
            conn = socket.create_connection((ip, port), 1)
            conn.close()
            return
        except Exception, unexpected:
            LOGGER.debug("Connection to %s:%s not ready yet, retrying...,"
                         "error is %s", str(ip), str(port), str(unexpected))
            time.sleep(1)

    raise Exception("Unable to connect to %s:%s." % (str(ip), str(port)))

class VirtualMachine(object):
    '''
    Interface class for different virtualization technologies like VirtualBox,
    Kvm, vSphere and so on.
    vnc_info must be a dict {'host': '10.2.3.4',
                             'port': 1234,
                             'user': a,
                             'password': b}
    '''
    def __init__(self, ip, vnc_info):
        #allocate in subclass and pass it here
        self._ip_address = ip
        if vnc_info is None:
            vnc_info = {}
        self._vnc_info = vnc_info
        self._automation = None
        self._manager = None
        self.helper = None
        self._vnc_grab_screen = None
        self.prepared = False
        self.prepare_command = None
        self.vnc_host = vnc_info.get('host', '')
        self.vnc_port = vnc_info.get('port', '')
        self.remote_instrumentation_file = None
        self.output_dir = None
        self.live_broadcast = None
        self._last_broadcasted = None

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def automation(self):
        if self._automation is None:
            LOGGER.debug("Creating automation object")
            self._automation = User(self._vnc_info['host'],
                                    int(self._vnc_info['port']),
                                    self._vnc_info['user'],
                                    self._vnc_info['password'])
            self._vnc_grab_screen = self._automation.grab_screen
            self._automation.grab_screen = self._grab_best_screen
        return self._automation

    @property
    def management(self):
        '''
        Returns the management capabilitites, see Management class
        '''
        if self._manager is None:
            self._manager = vm_manage.Management(self.helper)
        return self._manager

    def deallocate(self):
        '''
        Deallocates this virtual machine
        If there are logs collected then it returns the name of the file where
        they were saved
        '''
        log_file = None
        if not self.helper is None:
            if (not self.remote_instrumentation_file is None and
              not self.output_dir is None):
                out_file = self.output_dir + "/%s.pml" % str(uuid.uuid1())
                has_logs = self.helper.collect_instrumented_data(
                                              self.remote_instrumentation_file,
                                              out_file)
                if has_logs:
                    log_file = out_file + ".csv"
        return log_file

    def _grab_best_screen(self):
        '''
        Only to be called from automation.grab_screen as we intercept to
        produce highest quality screenshot
        '''
        screen = None
        if self.helper:
            screen = self.helper.get_current_screen()

        #failover to vnc screenshot method
        if screen is None:
            if self.helper is None:
                LOGGER.debug("No helper set yet, resorting to vnc")
            else:
                LOGGER.debug("Not possible to get screen from helpers, "
                             "resorting to vnc")
            screen = self._vnc_grab_screen()

        if screen is None:
            LOGGER.warning("Unable to get the screen from the vnc connection")

        if self.live_broadcast:
            _last_broadcasted = screen.copy()
            try:
                _last_broadcasted.save(self.live_broadcast)
            except Exception, ex:
                print "problem while broadcasting: %s" % str(ex)
        
        return screen

    def prepare(self):
        already_prepared = self.prepared

        if not already_prepared:
            if self.prepare_command:
                self.automation.run_command(self.prepare_command)
            else:
                raise Exception("Prepare command not provided!")
            self.automation.show_desktop()
            #get the mouse out of the way, FIXME: this is needed only if by
            #accident the taskbar is focused on start!
            screen = self.automation.grab_screen()
            self.automation.mouse.click(screen.size[0] - 1, 1)

        helper_port = 8080
        LOGGER.debug("Waiting for remote helper")
        wait_socket_port_ready(self._ip_address, helper_port)
        self.helper = vm_helper.RemoteHelper(self._ip_address, helper_port)
        setattr(self.automation,
                'get_current_cursor',
                self.helper.get_current_cursor)
