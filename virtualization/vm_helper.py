'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Remote machine helper functionality
'''

import json, base64, sys, traceback, logging
from PIL import Image
from peasy.io import esocket

LOGGER = logging.getLogger('root.' + __name__)

def _decompress(filename):
    import gzip
    dest = filename.replace(".gzXX", "")
    fin = gzip.open(filename, 'rb')
    fout = open(dest, 'wb')
    chunk_size = 1024 * 1024 * 1
    while True:
        chunk = fin.read(chunk_size)
        fout.write(chunk)
        if len(chunk) < chunk_size:
            break
    fout.close()
    fin.close()

    
class RemoteHelper(object):
    '''
    Helper class that encapsulates extra functionality for remoting a machine
    '''

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self._last_screen = None
        self._connection = None
        self._connect()

    def _connect(self):
        '''
        Connects to the remote helper
        '''
        LOGGER.info("Connecting to remote helper")
        self._connection = esocket.ESocket(self.ip_address, self.port, 60)
        self._connection.connect()

    def dispose(self):
        '''
        Closes any active connection and cleans up resources
        '''
        if self._connection:
            self._connection.close()
            self._connection = None

    def _send_message(self, obj):
        '''
        Sends a message, which is a 10 digits length + json encoded object
        '''
        message = json.dumps(obj)
        message = str(len(message)).ljust(10) + message
        self._connection.sendall(message)

    def _recv_message(self):
        '''
        Receive a message, encoded as send_message does
        '''
        message_length = int(self._connection.recvall(10))
        return json.loads(self._connection.recvall(message_length))

    def _request(self, obj):
        '''
        Same as http paradigm, send a message, expects a response
        '''
        try:
            self._send_message(obj)
            return self._recv_message()
        except Exception, ex:                            #pylint: disable=W0703
            LOGGER.warn("Failed to send message to helper (will retry): %s",
                        str(ex))
            try:
                self._connection.close()
            except:                                      #pylint: disable=W0702
                pass
            self._connection = None
            self._connect()
        self._send_message(obj)
        return self._recv_message()

    def _screen_changed(self):
        '''
        Checks if screen has changed since last time we pulled a screenshot
        '''
        obj = self._request({'request': '/screen_changed'})
        return obj['changed']

    def get_current_screen(self):
        '''
        Returns a screenshot from the remote machine current state
        '''
        obj = None
        try:
            if self._last_screen is None or self._screen_changed() == True:
                LOGGER.debug("Fetching image from helper")
                obj = self._request({'request': '/screen'})
                obj['bits'] = base64.b64decode(obj['bits'])
                size = (obj['width'], obj['height'])
                self._last_screen = Image.fromstring("RGB",
                                                     size,
                                                     obj['bits'],
                                                     'raw',
                                                     'BGRX',
                                                     0,
                                                     -1)
            else:
                LOGGER.debug("No changes in screen, using cached image")
            return self._last_screen.copy() #ensure readonly

        except Exception, ex: # pylint: disable=W0703
            LOGGER.warning("attempt to fetch screenshot from helper failed: %s",
                           str(ex))
            if obj:
                print "response is: %s" % str(obj)
            traceback.print_exc()
            return None

    def get_current_cursor(self):
        '''
        Returns the current mouse cursor
        FIXME: values hardcoded and may not be universal
        '''
        try:
            obj = self._request({'request': '/cursor'})
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
            LOGGER.warning("attempt to fetch current cursor failed: %s",
                           str(ex))
            return 'other'

    def get_current_window_title(self):
        '''
        Returns the title of the active window
        '''
        try:
            obj = self._request({'request': '/caption'})
            return obj['caption']
        except Exception, ex: # pylint: disable=W0703
            LOGGER.warning("attempt to get current window title failed: %s",
                   str(ex))
            return ""

    def get_window_rect(self, hwnd):
        '''
        Returns a 4 tuple with the screen coordinates of the given window
        '''
        try:
            obj = self._request({'request': '/window_rect', 'hwnd': hwnd})
            return (obj['left'], obj['top'], obj['right'], obj['bottom'])
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s", str(ex))

        return None

    def get_active_window_rect(self):
        '''
        Returns a 4 tuple with the screen coordinates of the active window
        '''
        try:
            obj = self._request({'request': '/active_window_rect'})
            return (obj['left'], obj['top'], obj['right'], obj['bottom'])
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s", str(ex))

        return None

    def get_clipboard(self):
        '''
        Returns the clipboard in unicode format
        '''
        try:
            obj = self._request({'request': '/clipboard'})
            return obj['data']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s", str(ex))

        return None

    def get_active_window_class(self):
        '''
        Returns the class name of the active window
        '''
        try:
            obj = self._request({'request': '/active_window_class'})
            return obj['name']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s", str(ex))

        return None

    def get_text_in_coords(self, x, y):
        '''
        Returns the text under the given screen coordinates
        '''
        try:
            obj = self._request({'request': '/text_in_coords', 'x': x, 'y': y})
            return obj['text']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s", str(ex))

        return ''

    def get_control_id_in_coords(self, x, y):
        '''
        Returns the control id under the given screen coordinates
        '''
        try:
            obj = self._request({'request': '/control_id_in_coords',
                                 'x': x,
                                 'y': y})
            return obj['id']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s", str(ex))

        return 0

    def scrap_active_window(self):
        '''
        Request for active window scraping
        '''
        try:
            obj = self._request({'request': '/scrap_active_window'})
            return obj['data']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, %s", str(ex))

        return None

    def execute(self, command):
        '''
        Executes the given command in the remote machine, note that it must be
        present in the remote machine!
        '''
        obj = None
        try:
            obj = self._request({'request': '/execute', 'command': command})
            LOGGER.debug("Will execute command: %s", command)
            return obj['stdout'], obj['stderr'], obj['returned']
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, error: %s\nGot from machine: %s",
                           str(ex),
                           str(obj))

        return None, None, None

    def launch(self, command):
        '''
        Will launch the given command in the remote machine, it wont wait for
        it to finish or return any error information
        '''
        try:
            LOGGER.debug("Will launch command: %s", command)
            self._request({'request': '/launch', 'command': command})
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, error: %s", str(ex))

    def get_file(self, remote_file, local_file):
        '''
        Fetch the remote file and save it locally with the given name
        '''
        try:
            LOGGER.debug("Will retrieve remote file %s and save locally as %s",
                         remote_file,
                         local_file)
            obj = self._request({'request': '/get_file',
                                 'filename': remote_file})
            total_size = obj['size']

            with open(local_file + ".gzXX", 'wb') as received:
                remaining = total_size + 0.0
                while remaining > 0:
                    #TODO: esocket still lacks stream receive thingy for large
                    #transfers
                    chunk = self._connection.socket.recv(64 * 1024)
                    print "%f%% (%d - %d)\r" % ((1 - (remaining / total_size)) * 100, total_size - remaining, total_size),
                    remaining -= len(chunk)
                    received.write(chunk)
            print "\rFile received, decompressing                 "
            _decompress(local_file + ".gzXX")
            return True
        except Exception, ex: # pylint: disable=W0703
            traceback.print_exc(file=sys.stdout)
            LOGGER.warning("Wopsy, error: %s\nGot from machine: %s",
                           str(ex),
                           str(obj))
            return False

    def collect_instrumented_data(self, remote_file, local_file):
        '''
        Collects events data from remote machine if available
        '''
        command = "\\utils\\procmon\\procmon.exe /Terminate"
        stdout, stderr, retcode = self.execute(command)
        if retcode == 0:
            command = ("\\utils\\procmon\\procmon.exe /Openlog " +
                       remote_file + " /SaveAs " + remote_file + ".csv")
            stdout, stderr, retcode = self.execute(command)
            if retcode == 0:
                self.get_file(remote_file + ".csv", local_file + ".csv")
                self.get_file(remote_file, local_file)
                LOGGER.debug("Instrumentation data saved as %s", local_file)
                return True
            else:
                LOGGER.error("Conversion of log failed, return code is %d"
                             " stdout is %s, stderr is %s", retcode, stdout,
                             stderr)
        else:
            LOGGER.warning("Procmon not found in remote machine? instrumented "
                           "data not available, command retcode "
                           "is %s", str(retcode))
        return False
