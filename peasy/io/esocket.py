'''
Simplified socket API with consistent error handling, timeout and other
niceties.
Note that this class is intended to be fully self contained and dependency free
'''
import logging, socket, select, errno

LOGGER = logging.getLogger('root.' + __name__)

ERR_REMOTE_CLOSED = "Socket connection broken (remote closed?)"
ERR_CLOSED = "Connection is closed, can't receive data"
ERR_TIMEOUT = "Operation timed out"

class TimeoutError(RuntimeError): pass             #pylint: disable=C0111,C0321
class ConnectionClosedError(RuntimeError): pass    #pylint: disable=C0111,C0321
class ConnectionBrokenError(RuntimeError): pass    #pylint: disable=C0111,C0321
class InvalidMessageFormatError(RuntimeError): pass#pylint: disable=C0111,C0321
class ConnectionRefusedError(RuntimeError): pass   #pylint: disable=C0111,C0321
class ConnectionIsClosedError(RuntimeError): pass  #pylint: disable=C0111,C0321

class ESocket(object):
    '''
    E(asy)Socket Base class with helpers, designed for easiness and not full
    control, full speed.
    Any send and receive is checked (sendall, recvall), consistent timeout
    handling, peek/poll functionality included, hopefully making life easier
    for robust communication.
    On errors (during send or receive, even timeout errors) the connection is
    closed
    '''
    def __init__(self, address, port, default_timeout=0):
        self._address = address
        self._port = port
        self._socket = None
        self._timeout = default_timeout

    def _what_timeout(self, timeout=None):
        '''
        Simple solver for timeout to be used
        '''
        if not timeout is None:
            return timeout
        else:
            return self._timeout

    @property
    def socket(self):
        '''
        Returns the python socket object itself
        '''
        return self._socket

    def is_connected(self):
        '''
        Returns True if connected, false otherwise.
        Note: remote host MAY had closed the connection, this call is unsafe
        in many ways, only inteded to be used for checking that double closing
        doesnt happen.
        '''
        return self._socket != None

    def connect(self, timeout=60):
        '''
        Connects to the remote machine, underlying implementation is the socket
        create_connection itself
        '''
        LOGGER.debug("Connecting to %s:%s", self._address, self._port)
        try:
            #use_timeout = self._what_timeout(timeout)
            self._socket = socket.create_connection((self._address, self._port),
                                                    timeout=timeout)
        except socket.error, sock_error:
            if sock_error[0] == errno.ECONNREFUSED:
                raise ConnectionRefusedError(ERR_REMOTE_CLOSED)
            else:
                raise
        LOGGER.debug("Connected to %s:%s", self._address, self._port)

    def sendall(self, content):
        '''
        Raises ConnectionIsClosedError if this connection is already closed
        Raises ConnectionBrokenError if remote peer closes the connection
        '''
        if self._socket is None:
            raise ConnectionIsClosedError(ERR_CLOSED)

        error_occurred = True
        try:
            self._socket.sendall(content)
            error_occurred = False
        except socket.error, sock_error:
            if sock_error[0] == errno.ECONNABORTED:
                raise ConnectionBrokenError(ERR_REMOTE_CLOSED)
            else:
                raise
        finally:
            if error_occurred:
                self.close()

    def recvall(self, length, timeout=None):
        '''
        Use this instead of recv, to ensure a given length is readed.
        Pass timeout as floating point number of seconds
        Client side calls should generally have a timeout, server calls may
        wait indefinitely if they dont want to disconnect inactive clients

        Raises ConnectionIsClosedError if this connection is already closed
        Raises ConnectionClosedError if remote peer closes the connection
        Raises ConnectionBrokenError if partial data was received and the
        connection closed
        Raises TimeoutError if it does not receive any data for timeout period
        of time.
        If any error is raised the connection is closed.
        '''
        if self._socket is None:
            raise ConnectionIsClosedError(ERR_CLOSED)
        received = 0
        remaining = length
        a_buffer = []
        # receive up to 64 kbytes chunks, large (mb) buffers throws memory
        # errors in python
        max_chunk_size = 1024 * 64
        timeout = self._what_timeout(timeout)

        while remaining > 0:
            if remaining > max_chunk_size:
                this_request_chunk = max_chunk_size
            else:
                this_request_chunk = remaining
            if timeout > 0:
                if self.has_data(timeout) == False:
                    LOGGER.error("Timeout occurred, closing connection.")
                    self.close()
                    raise TimeoutError(ERR_TIMEOUT)

            error_occurred = True
            try:
                this_chunk = self._socket.recv(this_request_chunk)
                error_occurred = False
            finally:
                if error_occurred:
                    self.close()
                    raise ConnectionBrokenError(ERR_REMOTE_CLOSED)

            received = len(this_chunk)
            if received == 0:
                #message broken, connection closed or cut in the middle of a
                #transfer
                self.close()
                raise ConnectionBrokenError(ERR_REMOTE_CLOSED)

            a_buffer.append(this_chunk)
            remaining -= received
            if remaining == 0:
                return "".join(a_buffer)

    def has_data(self, timeout=0):
        '''
        Returns True if there is data to be read from this socket, false
        otherwise.
        Timeout of 0 returns immediately, use a floating point number of seconds
        '''
        read, _, _ = select.select([self._socket], [], [], timeout)
        return len(read) > 0

    def close(self):
        '''
        Close this connection, no further communication should happen
        '''
        LOGGER.debug("Disconnecting from %s:%s", self._address, self._port)
        if not self._socket is None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except Exception, ex:                        #pylint: disable=W0703
                LOGGER.debug("Shutdown returned %s", str(ex))
            try:
                self._socket.close()
            except Exception, ex:                        #pylint: disable=W0703
                LOGGER.debug("Close returned %s", str(ex))
            self._socket = None
        LOGGER.debug("Disconnected from %s:%s", self._address, self._port)
