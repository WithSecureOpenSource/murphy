"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
"""
import ctypes, base64, subprocess, json

import screen_grab
import window_scraper
from screen_grab import AccessDenied

class POINT(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_long),
        ('y', ctypes.c_long),
    ]

class CURSORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("flags", ctypes.c_ulong),
                ("hCursor", ctypes.c_void_p),
                ("ptScreenPos", POINT)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

import socket, os
import SocketServer
import SimpleHTTPServer
import urllib
from urlparse import urlparse, parse_qs

#FIXME: ugly, do it nicer...
SERVICES = {}

#@route('/cursor')
def get_cursor(query):
    '''
    Returns the current cursor handle
    '''
    cursor_info = CURSORINFO()
    cursor_info.cbSize = ctypes.sizeof(CURSORINFO)
    rval = ctypes.windll.user32.GetCursorInfo(ctypes.pointer(cursor_info))
    if rval == 0:
        return {'status': 'fail',
                'message': 'Error while getting the current cursor'}
    else:
        return {'status': 'ok', 'handle': cursor_info.hCursor}

SERVICES['/cursor'] = get_cursor
        
#@route('/caption')
def get_active_window_title(query):
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    max_count = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 5
    if max_count > 5:
        buffer = ctypes.create_unicode_buffer(max_count)
        ret = ctypes.windll.user32.GetWindowTextW(hwnd, buffer, max_count)
        if ret > 0:
            return {'status': 'ok', 'caption': ctypes.wstring_at(buffer)}
        else:
            return {'status': 'fail', 'message': 'Failed to get the window text'}
    else:
        return {'status': 'ok', 'caption': ''}

SERVICES['/caption'] = get_active_window_title


#@route('/screen')

LAST_SCREEN = None

def get_screen(query):
    global LAST_SCREEN
    try:
        screen, width, height = screen_grab.grab()
        LAST_SCREEN = "" + screen
        return {"status": "ok",
                "bits": base64.b64encode(LAST_SCREEN),
                "width": width,
                "height": height}
    except AccessDenied:
        return {"status": "fail",
                "message": "Access Denied"}
    except Exception, ex:
        return {"status": "fail",
                "message": str(ex)}
                
SERVICES['/screen'] = get_screen

def screen_changed(query):
    global LAST_SCREEN
    if LAST_SCREEN is None:
        return {'status': 'ok', 'changed': True}
        
    screen, width, height = screen_grab.grab()  
    return {'status': 'ok', 'changed': LAST_SCREEN != screen}
    
SERVICES['/screen_changed'] = screen_changed

#@route('/clipboard')
def get_clipboard(query):
    CF_UNICODETEXT = 13

    if ctypes.windll.user32.OpenClipboard(None) != 0:
        handle = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
        if handle:
            data = ctypes.c_wchar_p(handle).value
            ctypes.windll.user32.CloseClipboard()
        else:
            data = ''
        return {"status": "ok",
                "data": data}
        ctypes.windll.user32.CloseClipboard()
    return {'status': 'fail', 'message': 'Problem dealing with clipboard'}

SERVICES['/clipboard'] = get_clipboard

#@route('/window_rect')
def window_rect(query):
    rect = RECT()
    hWnd = query['hwnd'] #request.query.hwnd)
    result = ctypes.windll.user32.GetWindowRect(hWnd, ctypes.pointer(rect))
    if result == 0:
        return {'status': 'fail', 'message': 'Failed to get window rect'}
    else:
        return {'status': 'ok', 'left': rect.left, 'top': rect.top,
                'right': rect.right, 'bottom': rect.bottom}
    
SERVICES['/window_rect'] = window_rect

#@route('/active_window_rect')
def get_active_window_rect(query):
    rect = RECT()
    hWnd = ctypes.windll.user32.GetForegroundWindow()
    result = ctypes.windll.user32.GetWindowRect(hWnd, ctypes.pointer(rect))
    if result == 0:
        return {'status': 'fail', 'message': 'Failed to get window rect'}
    else:
        return {'status': 'ok', 'left': rect.left, 'top': rect.top,
                'right': rect.right, 'bottom': rect.bottom}

SERVICES['/active_window_rect'] = get_active_window_rect


#@route('/active_window_class')
def get_active_window_class(query):
    hWnd = ctypes.windll.user32.GetForegroundWindow()
    max_count = 1024
    buffer = ctypes.create_unicode_buffer(max_count)
    result = ctypes.windll.user32.GetClassNameW(hWnd, ctypes.pointer(buffer), max_count)
    if result == 0:
        return {'status': 'fail', 'message': 'Failed to get window class'}
    else:
        return {'status': 'ok', 'name': ctypes.wstring_at(buffer)}

SERVICES['/active_window_class'] = get_active_window_class


def get_combobox_items(hwnd):
    CB_GETCOUNT = 0x0146
    CB_GETLBTEXT = 0x0148
    item_count = ctypes.windll.user32.SendMessageW(hwnd, CB_GETCOUNT, 0, 0)
    items = []
    max_count = 1024
    for i in range(item_count):
        buffer = ctypes.create_unicode_buffer(max_count)
        length = ctypes.windll.user32.SendMessageW(hwnd, CB_GETLBTEXT, i, ctypes.pointer(buffer))
        items.append(ctypes.wstring_at(buffer))
    return items

    
#@route('/text_in_coords')
def text_in_coords(query):
    p = POINT()
    p.x = query['x']
    p.y = query['y']
    ret_value = ''
    hwnd = ctypes.windll.user32.WindowFromPoint(p)
    if hwnd:
        get_window_text = ''
        max_count = ctypes.windll.user32.GetWindowTextLengthW(hwnd) + 5
        if max_count > 5:
            buffer = ctypes.create_unicode_buffer(max_count)
            ret = ctypes.windll.user32.GetWindowTextW(hwnd, buffer, max_count)
            if ret > 0:
                get_window_text = ctypes.wstring_at(buffer)
        
        max_count = 1024
        buffer = ctypes.create_unicode_buffer(max_count)
        result = ctypes.windll.user32.GetClassNameW(hwnd, ctypes.pointer(buffer), max_count)
        if ctypes.wstring_at(buffer) == 'ComboBox':
            ret_value = {'combobox': {'value': get_window_text,
                                      'values': get_combobox_items(hwnd)}}
        else:
            WM_GETTEXT = 0x000d
            buffer = ctypes.create_unicode_buffer(max_count)
            length = ctypes.windll.user32.SendMessageW(hwnd, WM_GETTEXT, max_count, ctypes.pointer(buffer))
            get_text = ctypes.wstring_at(buffer)
            if len(get_text) > len(get_window_text):
                ret_value = get_text
            else:
                ret_value = get_window_text

    return {'status': 'ok', 'text': ret_value}

SERVICES['/text_in_coords'] = text_in_coords


#@route('/control_id_in_coords')
def control_id_in_coords(query):
    p = POINT()
    p.x = query['x'] #request.query.x)
    p.y = query['y'] #request.query.y)
    ret_value = 0
    hwnd = ctypes.windll.user32.WindowFromPoint(p)
    if hwnd:
        ret_value = ctypes.windll.user32.GetDlgCtrlID(hwnd)

    return {'status': 'ok', 'id': ret_value}

SERVICES['/control_id_in_coords'] = control_id_in_coords


#@route('/scrap_active_window')
def scrap_active_window(query):
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    try:
        scraper = window_scraper.WindowScraper()
        return {'status': 'ok', 'data': scraper.scrap(hwnd)}
    except Exception, ex:
        return {'status': 'fail', 'message': 'Failed to scrap: %s' % str(ex)}

SERVICES['/scrap_active_window'] = scrap_active_window

        
#@route('/execute')
def execute(query):
    '''
    Executes the given command and returns stdout and stderr as tuple once the
    process has finished
    This method will hide any command window if the given process will show
    one
    '''
    command = query['command'] #request.query.command
    startupinfo = subprocess.STARTUPINFO()
    subprocess.STARTF_USESHOWWINDOW = 1
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        process = subprocess.Popen(command,
                                   startupinfo=startupinfo,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd='c:\\utils',
                                   shell=True)
        pout, perr = process.communicate()
        process.wait()
        return {'status': 'ok',
                'stdout': pout,
                'stderr': perr,
                'returned': process.returncode}
    except Exception, ex:
        return {'status': 'fail', 'message': str(ex)}
    
SERVICES['/execute'] = execute


#@route('/launch')
def launch(query):
    '''
    Launch the given command, dont wait for it
    This method will hide any command window if the given process will show
    one
    '''
    command = query['command'] #request.query.command
    startupinfo = subprocess.STARTUPINFO()
    subprocess.STARTF_USESHOWWINDOW = 1
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        process = subprocess.Popen(command,
                                   startupinfo=startupinfo,
                                   cwd='c:\\utils',
                                   shell=True)
        return {'status': 'ok'}
    except Exception, ex:
        return {'status': 'fail', 'message': str(ex)}
    
SERVICES['/launch'] = launch


def get_file(query):
    try:
        filename = query['filename']
        #with open(filename, 'rb') as the_file:
        #    content = the_file.read()
        #return {'status': 'ok', 'size': base64.b64encode(content)}
        return {'status': 'ok', 'size': os.path.getsize(filename)}
    except Exception, ex:
        return {'status': 'fail', 'message': 'Failed to get the file: %s' % str(ex)}

SERVICES['/get_file'] = get_file



PORT = 8080

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
    #fixme: sendall
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
    # header is 10 bytes string length of message
    # message is json object, always
    message = json.dumps(object)
    message = str(len(message)).ljust(10) + message
    send(client, message)


def stream_file(conn, filename):
    #stream content in 64 kb chunks
    total_size = os.path.getsize(filename)
    remaining_size = total_size
    with open(filename, 'rb') as the_file:
        while remaining_size > 0:
            chunk = the_file.read(64 * 1024)
            conn.sendall(chunk)
            remaining_size -= len(chunk)
    
def client_run(client):
    try:
        while True:
            message = recv_message(client)
            handler = SERVICES.get(message['request'])
            if handler:
                send_message(client, handler(message))
                if message['request'] == '/get_file':
                    stream_file(client, message['filename'])
            else:
                raise Exception("Invalid message received, no handler found for message %s" % str(message))                
    except Exception, e:
        print "Error occurred: %s" % str(e)
        try:
            client.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            client.close()
        except:
            pass
            
if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen(5)
    print "Server listening on port %d" % PORT
    while True:
        (clientsocket, address) = server.accept()
        client_run(clientsocket)
            
