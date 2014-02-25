'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Wrapper around vncdotool, converts from reactor centric code into a separate
process object
'''
from twisted.internet import reactor
import time
from Queue import Empty
from multiprocessing import Process, Queue
from PIL import Image

import logging
from murphy.user_simulation.vnc.vncdotool import client, input_parser
LOGGER = logging.getLogger('root.' + __name__)

class VncConnection(object):
    '''
    Isolates a vnc connection into a separate process where code is not
    reactor centric, communication is done by sending commands thru queues
    '''
    REACTOR = reactor
    _RUNNING = False
    
    def __init__(self, host, port, user, password):
        self._host = host
        self._port = port
        self._user = user
        self._password = password

        self._client = None
        self._factory = None
        self._reactor = VncConnection.REACTOR

        self._process = None
        self._keyboard = None
        self._mouse = None
        self._screen = None        

        self.queue_out = None
        self.queue_in = None
        self._loops = 0
        
    def connect(self):
        '''
        Asynchronously starts a connection with the device, once the connection
        is established the response queue is used to synchronize
        '''
        self._initiate_connection()
        
        
    @property
    def mouse(self):
        '''
        Returns the mouse object for this connection
        '''
        if self._mouse is None:
            self._mouse = Mouse(self.client)
        return self._mouse


    def _log_connected(self, protocol):
        '''
        Once connection is established log and notify the controller process
        '''
        LOGGER.info('connected to %s' % protocol.name)
        self._client = protocol
        self.queue_out.put("connected to it")
        return protocol

    
    def _stop(self, pcol):
        '''
        Stops this connection effectively disconnecting
        '''
        self._reactor.exit_status = 0
        pcol.transport.loseConnection()
        self._reactor.callLater(0.1, self._reactor.stop) #pylint: disable=E1101

        
    def _error(self, reason):
        '''
        Generic error handling
        '''
        reason.printTraceback()
        self._reactor.exit_status = 10
        self._reactor.stop() #pylint: disable=E1101
        self.queue_out.put("error")
        
        
    def _initiate_connection(self):
        '''
        Ininitates the connection process and main message loop
        '''
        self._factory = client.VNCDoToolFactory()
        self._factory.deferred.addCallback(self._log_connected)
        self._factory.deferred.addErrback(self._error)
        self._reactor.connectTCP(self._host, #pylint: disable=E1101
                                 self._port,
                                 self._factory,
                                 timeout=10)
        if VncConnection._RUNNING == False:
            VncConnection._RUNNING = True
            #self._reactor.run(installSignalHandlers=0)
            self._reactor.callLater(1, self.mainloop) #pylint: disable=E1101
            self._reactor.run() #pylint: disable=E1101
        
    def key_type(self, text):
        '''
        Type a key, simulates a key down and key up
        '''
        self.client.keyPress(text)

    def key_press(self, text):
        '''
        Hold down the given key
        '''
        self.client.keyDown(text)
    
    def key_release(self, text):
        '''
        Releases the given key
        '''
        self.client.keyUp(text)
        
    def mouse_move(self, coord_x, coord_y):
        '''
        Move the mouse to the given coord
        '''
        self.client.mouseMove(coord_x, coord_y)

    def mouse_down(self, button):
        '''
        Hold down the given mouse button
        '''
        self.client.mouseDown(button)

    def mouse_up(self, button):
        '''
        Releases the given mouse button
        '''
        self.client.mouseUp(button)

    def mouse_click(self, coord_x=0, coord_y=0):
        '''
        Performs a left-click in the given coordinates, if coordinates are
        given then both x and y are mandatory. 
        '''
        if coord_x != 0 and coord_y != 0:
            self.client.mouseMove(coord_x, coord_y)
            time.sleep(0.2)
        self.client.buttons = 0
        self.client.mousePress(1)
        #time.sleep(0.1)
        self.client.buttons = 0
        #self.client.mouseUp(0)


    def mainloop(self):
        '''
        Main message loop, periodically checks if there are commands sent
        by the controller process to execute
        '''
        self._loops += 1
        should_stop = False
        try:
            command = self.queue_in.get(False)
            if command[0] == "grab":
                self.client.captureScreen(self.queue_out)
            elif command[0] == "key type":
                self.key_type(command[1])
                self.queue_out.put("done")
            elif command[0] == "key press":
                self.key_press(command[1])
                self.queue_out.put("done")
            elif command[0] == "key release":
                self.key_release(command[1])
                self.queue_out.put("done")
            elif command[0] == "mouse move":
                self.mouse_move(command[1], command[2])
                self.queue_out.put("done")
            elif command[0] == "mouse down":
                self.mouse_down(command[1])
                self.queue_out.put("done")
            elif command[0] == "mouse up":
                self.mouse_up(command[1])
                self.queue_out.put("done")
            elif command[0] == "mouse click":
                self.mouse_click(command[1], command[2])
                self.queue_out.put("done")
            elif command[0] == "disconnect":
                should_stop = True
                self.queue_out.put("done")
                self._reactor.callLater(1, #pylint: disable=E1101
                                        self._stop,
                                        self.client)
            else:
                raise Exception("Unknown command: %s" % str(command))
        except Empty:
            pass
        except Exception, ex:
            LOGGER.error("Wops: %s" % str(ex))
        finally:
            if not should_stop:
                self._reactor.callLater(0.01, #pylint: disable=E1101
                                        self.mainloop)
        
    @property
    def client(self):
        '''
        Returns the vncdotool client object
        '''
        return self._client
        


TRANSLATION = {'control': 'ctrl',
               'escape': 'esc'}

def _translate(key):
    '''
    Few key names inconsistencies
    '''
    if key in TRANSLATION:
        return TRANSLATION[key]
    else:
        return key

        
def connect_vnc(host, port, queue_out, queue_in):
    '''
    Establishes a vnc connection using the given queues for communication
    Mean to be executed on a separate process from the controlling one
    '''
    connection = VncConnection(host, port, None, None)
    connection.queue_out = queue_in
    connection.queue_in = queue_out
    command = queue_out.get()
    if command == "connect":
        connection.connect()

    
class VncConnectionProxy(object):
    '''
    Encapsulates the control of the vnc connection in a separate process, this
    object lives in the main program process while the vncdotool object is in
    a separated one
    '''
    def __init__(self, host, port, user, password):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._queue_out = Queue()
        self._queue_in = Queue()
        self._process = Process(target=connect_vnc, args=(host,
                                                          port,
                                                          self._queue_out,
                                                          self._queue_in,))
        self._process.start()
        self._screen = None
        self._keyboard = None
        self._mouse = None
        self._delay = 0.2
    
    def connect(self):
        '''
        Connects to the remote device, returns once the connection is
        established
        Do not forget to call disconnect as it otherwise the other process will
        continue to live
        '''
        self._queue_out.put("connect")
        response = self._queue_in.get()
        if response != "connected to it":
            raise Exception("Failed to connect")

    def disconnect(self):
        '''
        Disconnects from the remote device, releases the 2nd process
        '''
        self._queue_out.put(["disconnect"])
        self._queue_in.get()
        self._process.join()
        self._process = None

    @property
    def screen(self):
        '''
        Returns a screen object for this vnc connection
        '''
        if not self._screen:
            self._screen = Screen(self._queue_out, self._queue_in)
        return self._screen

    @property
    def keyboard(self):
        '''
        Returns a keyboard object for this vnc connection
        '''
        if not self._keyboard:
            self._keyboard = Keyboard(self._queue_out,
                                      self._queue_in,
                                      self._delay)
        return self._keyboard

    @property
    def mouse(self):
        '''
        Returns a mouse object for this vnc connection
        '''
        if not self._mouse:
            self._mouse = Mouse(self._queue_out,
                                self._queue_in,
                                self._delay)
        return self._mouse


        
class Screen(object):
    '''
    Encapsulates access to the screen
    '''
    def __init__(self, queue_out, queue_in):
        self._queue_out = queue_out
        self._queue_in = queue_in
        
    def grab(self):
        '''
        Returns the current screen as seen by the user into a PIL Image object
        '''
        self._queue_out.put(["grab"])
        raw = self._queue_in.get()
        return Image.fromstring(raw[1], raw[0], raw[2])

        
class Keyboard(object):
    '''
    Encapsulates access to the keyboard
    '''
    def __init__(self, queue_out, queue_in, delay):
        self._queue_out = queue_out
        self._queue_in = queue_in
        self._delay = delay
        #FIXME: create machine codepage param
        self.tweak_kb = True
        
    def enters(self, text):
        '''
        Simulates user input, supports escape sequences for special keys
        '''
        tweaked_text = text.replace(":", "{+shift};{-shift}")
        tweaked_text = tweaked_text.replace("<", "{+shift},{-shift}")
        tweaked_text = tweaked_text.replace(">", "{+shift}.{-shift}")
        tweaked_text = tweaked_text.replace("_", "{+shift}-{-shift}")
        tweaked_text = tweaked_text.replace('"', "{+shift}'{-shift}")
        if self.tweak_kb == False:
            tweaked_text = text
        LOGGER.info("Sending keystrokes %s" % text)
        for key in input_parser.tokenize(tweaked_text):
            input_fn = 'type'
            if len(key) > 1:
                if key[0] == '+':
                    input_fn = 'press'
                    key = key[1:]
                elif key[0] == '-':
                    input_fn = 'release'
                    key = key[1:]
            translated = _translate(key)
            self._queue_out.put(['key ' + input_fn, translated])
            self._queue_in.get()
            time.sleep(self._delay)
        
    def enters_in_field(self, text):
        '''
        Simulates entering text into a field, replacing the old content
        '''
        self.enters('{+control}a{-control}' + text)
        
        
class Mouse(object):
    '''
    Encapsulates access to the mouse
    '''
    def __init__(self, queue_out, queue_in, delay):
        self._queue_out = queue_out
        self._queue_in = queue_in
        self._delay = delay
        
    def move(self, x_pos, y_pos):
        '''
        Moves the mouse to the given possition
        '''
        LOGGER.info("moving mouse to %s %s" % (x_pos, y_pos))
        self._queue_out.put(['mouse move', x_pos, y_pos])
        self._queue_in.get()
        time.sleep(self._delay)

    def click(self, x_pos=0, y_pos=0):
        '''
        Simulates a left click on the given coordinates, note that if
        coordinates are omitted the click is in the current mouse position,
        otherwise both x and y coordinates must be specified
        '''
        #self._queue_out.put(['mouse click', x, y])
        #response = self._queue_in.get()
        if x_pos == 0 and y_pos == 0:
            LOGGER.info("mouse click")
        else:
            LOGGER.info("mouse click at %s %s" % (x_pos, y_pos))
        if x_pos != 0 and y_pos != 0:
            self.move(x_pos, y_pos)
        self.down(1)
        self.up(1)

        
    def down(self, button):
        '''
        Presses the given mouse button
        '''
        self._queue_out.put(['mouse down', button])
        self._queue_in.get()
        time.sleep(self._delay)

    def up(self, button):
        '''
        Releases the given mouse button
        '''
        self._queue_out.put(['mouse up', button])
        self._queue_in.get()
        time.sleep(self._delay)
        
