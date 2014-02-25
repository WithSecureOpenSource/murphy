'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details
'''

import time, urllib, json, base64, traceback, sys, socket
import urllib2
from PIL import Image

from model_extraction.world import World

import logging
from murphy.user_simulation.vnc.vnc_user import User
LOGGER = logging.getLogger('root.' + __name__)

#FIXME: There may be a better place for this...
def wait_socket_port_ready(ip, port, max_timeout=60):
    for i in range(60):
        try:
            conn = socket.create_connection((ip, port), 1)
            conn.close()
            return
        except Exception, e:
            LOGGER.debug("Connection to %s:%s not ready yet, retrying..., error is %s" % (str(ip), str(port), str(e)))
            time.sleep(1)
            
    raise Exception("Unable to connect to %s:%s." % (str(ip), str(port)))
    
    
class VmWorld(World):
    '''
    Encapsulates a virtual machine as a world for crawling
    '''
    
    def __init__(self, allocator):
        self._allocator = allocator
        self._machine = None
        #Used during scraping to keep track of last known screen, it is the
        #last image before performing an edge, each edge to be performed saves
        #the current screenshot here
        self.last_screen = None

    
    def reset(self):
        '''
        Initializes or reinitializes the virtual machine to the starting state
        '''
        if self._machine:
            self.dispose()
            
        self._machine = self._allocator()
        self._machine.prepare()
        
        
    def dispose(self):
        '''
        Deallocates the virtual machine if it was allocated
        '''
        if self._machine:
            self._machine.deallocate()
            self._machine = None
        
        
    @property
    def machine(self):
        return self._machine
        
        
        
class VirtualMachine(object):
    '''
    Interface class for different virtualization technologies like VirtualBox,
    Kvm, vSphere and so on.
    vnc_info must be a dict {'host': '10.2.3.4', 'port': 1234, 'user': a, 'password': b}
    '''
    
    def __init__(self, ip, vnc_info):
        #allocate in subclass and pass it here
        self._ip_address = ip
        if vnc_info is None:
            vnc_info = {}
        self._vnc_info = vnc_info
        self._automation = None
        self.helper = None
        self._vnc_grab_screen = None
        self.prepared = False
        self.prepare_command = None
        self.vnc_host = vnc_info.get('host', '')
        self.vnc_port = vnc_info.get('port', '')
        
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
        
        
    def deallocate(self):
        #override
        pass

        
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
            
        return screen
    
    
    def prepare(self):
        already_prepared = self.prepared
            
        if not already_prepared:
            if self.prepare_command:
                self.automation.run_command(self.prepare_command)
            else:
                raise Exception("Prepare command not provided!")
            self.automation.show_desktop()
            #get the mouse out of the way, FIXME: this is needed only if by accident the taskbar is focused on start!
            screen = self.automation.grab_screen()
            self.automation.mouse.click(screen.size[0] - 1, 1)
            
        helper_port = 8080
        LOGGER.debug("Waiting for remote helper")
        wait_socket_port_ready(self._ip_address, helper_port)
        self.helper = RemoteHelper(self._ip_address, helper_port)
        setattr(self.automation, 'get_current_cursor', self.helper.get_current_cursor)
        

#FIXME: this needs a bit of refactoring, encapsulation. It is also duplicated
#in helpers
import socket
from urlparse import urlparse, parse_qs

def recv(client, length):
    received = 0
    remaining = length
    buffer = []
    max_chunk_size = 1024 * 64
    while remaining > 0:
        if remaining > max_chunk_size:
            this_request_chunk = max_chunk_size
        else:
            this_request_chunk = remaining
            
        this_chunk = client.recv(this_request_chunk)
        received = len(this_chunk)
        if received == 0:
            raise RuntimeError("Socket connection broken")
        buffer.append(this_chunk)
        remaining -= received
        if remaining == 0:
            return "".join(buffer)


def send(client, message):
    message_length = len(message)
    total_sent = 0
    while total_sent < message_length:
        sent = client.send(message[total_sent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        total_sent += sent
            
            
def recv_message(client):
    # header is 10 bytes string length of message
    message_length = int(recv(client, 10))
    # message is json object, always
    return json.loads(recv(client, message_length))
    
    
def send_message(client, object):
    message = json.dumps(object)
    message = str(len(message)).ljust(10) + message
    send(client, message)
        
class RemoteHelper(object):
    '''
    Helper class that encapsulates extra functionality for remoting a machine
    '''

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self._last_screen = None
        
        self._connect()
        
    def _connect(self):
        LOGGER.info("Connecting to remote helper")
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.connect((self.ip_address, self.port))
    
    def _request_url(self, url, url_prepared=False):
        if url_prepared == False:
            url = url % (self.ip_address, self.port)
            
        parsed=urlparse(url)
        query = parse_qs(parsed.query)
        message_obj = {'request': parsed.path}
        for k, v in query.items():
            message_obj[k] = v[0]
    
        try:
            send_message(self._connection, message_obj)
            obj = recv_message(self._connection)
        except Exception, ex:
            LOGGER.warn("Failed to send message to helper (will retry): %s" % str(ex))
            try:
                self._connection.close()
            except:
                pass
            self._connection = None
            self._connect()
            send_message(self._connection, message_obj)
            obj = recv_message(self._connection)
            
        if obj['status'] == 'ok':
            return obj
        else:
            raise Exception("Failed to retrieve %s, message is: %s" %
                            (url, obj['message']))


    def _screen_changed(self):
        obj = self._request_url("http://%s:%s/screen_changed")
        return obj['changed']
        
    def get_current_screen(self):
        '''
        Returns a screenshot from the remote machine current state
        '''
        try:
            if self._last_screen is None or self._screen_changed() == True:
                LOGGER.debug("Fetching image from helper")
                obj = self._request_url("http://%s:%s/screen")
                obj['bits'] = base64.b64decode(obj['bits'])
                self._last_screen = Image.fromstring("RGB",
                                                     (obj['width'], obj['height']),
                                                     obj['bits'],
                                                     'raw',
                                                     'BGRX',
                                                     0,
                                                     -1)
            else:
                LOGGER.debug("No changes in screen, using cached image")
            return self._last_screen.copy() #ensure readonly
                
        except Exception, ex: # pylint: disable=W0703
            LOGGER.warning("attempt to fetch screenshot from helper failed: %s" %
                   str(ex))
            traceback.print_exc()
            return None

    def get_current_cursor(self):
        '''
        Returns the current mouse cursor
        FIXME: values hardcoded and may not be universal
        '''
        try:
            obj = self._request_url("http://%s:%s/cursor")
            handle = int(obj['handle'])
            if handle == 65539:
                return 'normal'
            elif handle == 65541:
                return 'text'
            elif handle == 65567:
                return 'link'
            else:
                return 'other'
        except Exception, ex: # pylint: disable=W0703
            LOGGER.warning("attempt to fetch current cursor failed: %s" % str(ex))
            return 'other'

    def get_current_window_title(self):
        '''
        Returns the title of the active window
        '''
        try:
            obj = self._request_url("http://%s:%s/caption")
            return obj['caption']
        except Exception, ex: # pylint: disable=W0703
            LOGGER.warning("attempt to get current window title failed: %s" % 
                   str(ex))
            return ""

    def get_window_rect(self, hwnd):
        '''
        Returns a 4 tuple with the screen coordinates of the given window
        '''
        try:
            obj = self._request_url("http://%s:%s/window_rect?hwnd=" + hwnd)
            return (obj['left'], obj['top'], obj['right'], obj['bottom'])
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s" % str(ex))

        return None
            
    def get_active_window_rect(self):
        '''
        Returns a 4 tuple with the screen coordinates of the active window
        '''
        try:
            obj = self._request_url("http://%s:%s/active_window_rect")
            return (obj['left'], obj['top'], obj['right'], obj['bottom'])
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s" % str(ex))

        return None
        
    def get_clipboard(self):
        '''
        Returns the clipboard in unicode format
        '''
        try:
            obj = self._request_url("http://%s:%s/clipboard")
            return obj['data']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s" % str(ex))

        return None

    def get_active_window_class(self):
        '''
        Returns the class name of the active window
        '''
        try:
            obj = self._request_url("http://%s:%s/active_window_class")
            return obj['name']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s" % str(ex))

        return None
        
    def get_text_in_coords(self, x, y):
        '''
        Returns the text under the given screen coordinates
        '''
        try:
            coords = "?x=%s&y=%s" % (x, y)
            obj = self._request_url("http://%s:%s/text_in_coords" + coords)
            return obj['text']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s" % str(ex))

        return ''
        
    def get_control_id_in_coords(self, x, y):
        '''
        Returns the control id under the given screen coordinates
        '''
        try:
            coords = "?x=%s&y=%s" % (x, y)
            obj = self._request_url("http://%s:%s/control_id_in_coords" + coords)
            return obj['id']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s" % str(ex))

        return 0


    def scrap_active_window(self):
        try:
            obj = self._request_url("http://%s:%s/scrap_active_window")
            return obj['data']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s" % str(ex))

        return None
        
        
    def execute(self, command):
        '''
        Executes the given command in the remote machine, note that it must be
        present in the remote machine!
        '''
        obj = None
        try:
            url = ("http://%s:%s/execute?command=" % (self.ip_address, self.port)) + urllib.quote(command, '')
            LOGGER.debug("Will execute command: %s" % url)
            obj = self._request_url(url, True)
            return obj['stdout'], obj['stderr']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, error: %s\nGot from machine: %s" % (str(ex), str(obj)))

        return None, None
    