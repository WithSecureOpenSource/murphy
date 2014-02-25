"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
"""

import sys, urllib2, traceback

MB_ABORTRETRYIGNORE  = 2
MB_CANCELTRYCONTINUE = 6
MB_HELP              = 0x4000
MB_OK                = 0
MB_OKCANCEL          = 1
MB_RETRYCANCEL       = 5
MB_YESNO             = 4
MB_YESNOCANCEL       = 3

MB_ICONEXCLAMATION = 0x00000030
MB_ICONWARNING     = 0x00000030
MB_ICONINFORMATION = 0x00000040
MB_ICONASTERISK    = 0x00000040
MB_ICONQUESTION    = 0x00000020
MB_ICONSTOP        = 0x00000010
MB_ICONERROR       = 0x00000010
MB_ICONHAND        = 0x00000010

def report_error(msg):
    if sys.platform == "win32":
        import ctypes
        if type(msg) is unicode:
            ctypes.windll.user32.MessageBoxW(0, msg, u"Error", MB_OK + MB_ICONERROR)
        else:
            ctypes.windll.user32.MessageBoxA(0, msg, "Error", MB_OK + MB_ICONERROR)
    
    raise RuntimeError(msg)

    
def wget(url):
    filename = url.split('/')[-1].split('#')[0].split('?')[0]
    try:
        response = urllib2.urlopen(url)
        content = response.read()
        with open(filename, 'wb') as the_file:
            the_file.write(content)
    except Exception, ex:
        msg = "Error while retrieving url %s\n\n%s\n\n%s" % (str(url), str(ex), traceback.format_exc())
        report_error(msg)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        report_error("Use wget.py url")
    wget(sys.argv[1])
