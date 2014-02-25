'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Generic window scraping based on windows API calls
'''

import ctypes, re

WM_GETTEXT = 0x000d
WM_GETTEXTLENGTH = 0x000e
                
CB_GETCOUNT = 0x0146
CB_GETLBTEXT = 0x0148

class RECT(ctypes.Structure):
    '''
    As per windows API
    '''
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))

class WindowNotFound(Exception): pass
                
class WindowScraper(object):
    '''
    Generic window scraper, collects all child windows info.
    '''
    def __init__(self):
        self._childs = []
        
    def foreach_window(self, hwnd, lParam):
        '''
        Enumeration callback, uses instance variable to collect results
        '''
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            rect = self.get_window_rect(hwnd)
            self._childs.append({'hwnd': hwnd,
                                 'rect': {'left': rect.left,
                                          'top': rect.top,
                                          'right': rect.right,
                                          'bottom': rect.bottom}})
        return True


    def get_window_rect(self, hwnd):
        '''
        Returns the window rect in screen coords for the given window
        '''
        rect = RECT()
        result = ctypes.windll.user32.GetWindowRect(hwnd,
                                                    ctypes.pointer(rect))
        if result == 0:
            raise Exception("Failed GetWindowRect for %s" % hwnd)
        else:
            return rect
            
            
    def get_window_class(self, hwnd):
        '''
        Returns the class name for the given window
        '''
        max_count = 1024
        text_buffer = ctypes.create_unicode_buffer(max_count)
        result = ctypes.windll.user32.GetClassNameW(hwnd,
                                                    ctypes.pointer(text_buffer),
                                                    max_count)
        if result != 0:
            return ctypes.wstring_at(text_buffer)
        else:
            raise Exception('Failed to get window class')
        

    def get_window_text(self, hwnd):
        '''
        Returns the associated window text as per windows API
        '''
        max_count = 38911
        text_buffer = ctypes.create_unicode_buffer(max_count)
        length = ctypes.windll.user32.GetWindowTextW(hwnd,
                                                     text_buffer,
                                                     max_count)
        if length > 0 and length != 38911:
            return ctypes.wstring_at(text_buffer)
        elif length == 38911:
            max_count = 122365
            text_buffer = ctypes.create_unicode_buffer(max_count)
            ctypes.windll.user32.GetWindowTextW(hwnd, text_buffer, max_count)
            return ctypes.wstring_at(text_buffer)
        return ''
        
        
    def get_window_wm_text(self, hwnd):
        '''
        Returns the text as per window WM_GETTEXT
        '''
        max_count = 38911
        text_buffer = ctypes.create_unicode_buffer(max_count)
        length = ctypes.windll.user32.SendMessageW(hwnd,
                                                   WM_GETTEXT,
                                                   max_count,
                                                   ctypes.pointer(text_buffer))
        if length != 38911:
            return ctypes.wstring_at(text_buffer)
        else:
            max_count = 122365
            text_buffer = ctypes.create_unicode_buffer(max_count)
            length = ctypes.windll.user32.SendMessageW(hwnd,
                                                       WM_GETTEXT,
                                                       max_count,
                                                    ctypes.pointer(text_buffer))
            return ctypes.wstring_at(text_buffer)
    
    
    def get_combobox_items(self, hwnd):
        '''
        Returns a list with all the combobox items (texts) for the given handle
        '''
        item_count = ctypes.windll.user32.SendMessageW(hwnd,
                                                       CB_GETCOUNT,
                                                       0,
                                                       0)
        items = []
        max_count = 1024
        for i in range(item_count):
            text_buffer = ctypes.create_unicode_buffer(max_count)
            length = ctypes.windll.user32.SendMessageW(hwnd,
                                                       CB_GETLBTEXT,
                                                       i,
                                                    ctypes.pointer(text_buffer))
            items.append(ctypes.wstring_at(text_buffer))
        return items
    
    
    def scrap(self, hwnd):
        '''
        Scraps the given window, returns a dictionary with everyting it sees
        '''
        elems = self.collect_child_windows(hwnd)
        self.collect_window_info(elems)
        rect = self.get_window_rect(hwnd)
        return {'hwnd': hwnd,
                'class': self.get_window_class(hwnd),
                'text': self.get_window_text(hwnd),
                'rect': {'left': rect.left,
                         'top': rect.top,
                         'right': rect.right,
                         'bottom': rect.bottom},
                'childs': elems}
    
        
    def collect_window_info(self, windows):
        '''
        Collects various information on each window in the given array, the
        expected format is the one returned by collect_child_windows
        '''
        for win in windows:
            hwnd = win['hwnd']
            win['class'] = self.get_window_class(hwnd)
            win['text'] = self.get_window_text(hwnd)
            win['wm text'] = self.get_window_wm_text(hwnd)
            win['control id'] = ctypes.windll.user32.GetDlgCtrlID(hwnd)
            win['enabled'] = ctypes.windll.user32.IsWindowEnabled(hwnd) != 0
            if win['class'] == 'ComboBox':
                win['items'] = self.get_combobox_items(hwnd)

                
    def collect_child_windows(self, hwnd):
        '''
        Collects info on all the visible child windows of the given window
        '''
        proc = EnumWindowsProc(self.foreach_window)
        ctypes.windll.user32.EnumChildWindows(hwnd, proc, 0)
        return self._childs


    @staticmethod
    def find_window(title_regexp=None, class_regexp=None):
        '''
        Searches a window that matches either the given title or class name,
        the window MUST be visible, returns the first one that matches.
        '''
        scraper = WindowScraper()
        proc = EnumWindowsProc(scraper.foreach_window)
        ctypes.windll.user32.EnumWindows(proc, 0)
        
        if title_regexp:
            title_pattern = re.compile(title_regexp)
        else:
            title_pattern = None
        
        if class_regexp:
            class_pattern = re.compile(class_regexp)
        else:
            class_pattern = None

        if title_regexp is None and class_regexp is None:
            raise ValueError("Neither title nor class reg exp specified")
        
        for child in scraper._childs:
            if title_pattern:
                title = scraper.get_window_text(child['hwnd'])
                if title_pattern.search(title):
                    return child['hwnd']
            if class_pattern:
                class_name = scraper.get_window_class(child['hwnd'])
                if class_pattern.search(class_name):
                    return child['hwnd']
        
        if title_regexp:
            raise WindowNotFound("Window with title %s not found" % 
                                                             str(title_regexp))
        if class_regexp: 
            raise WindowNotFound("Window with class %s not found" % 
                                                             str(class_regexp))
