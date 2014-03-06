'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'User Account Control Settings',
        'snapshots': ['user_account_control_settings.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['user_account_control_settings.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 590234, "childs": [{"hwnd": 4391266, "control id": 0, "wm text": "", "rect": {"top": 114, "right": 884, "left": 140, "bottom": 636}, "text": "", "class": "DirectUIHWND", "enabled": true}, {"hwnd": 4391560, "control id": 0, "wm text": "", "rect": {"top": 184, "right": 808, "left": 228, "bottom": 199}, "text": "", "class": "CtrlNotifySink", "enabled": true}, {"hwnd": 721316, "control id": 0, "wm text": "<a href=\"\">Tell me more about User Account Control settings</a>", "rect": {"top": 184, "right": 808, "left": 228, "bottom": 199}, "text": "<a href=\"\">Tell me more about User Account Control settings</a>", "class": "SysLink", "enabled": true}, {"hwnd": 590264, "control id": 0, "wm text": "", "rect": {"top": 244, "right": 294, "left": 268, "bottom": 464}, "text": "", "class": "CtrlNotifySink", "enabled": true}, {"hwnd": 655808, "control id": 0, "wm text": "", "rect": {"top": 244, "right": 294, "left": 268, "bottom": 464}, "text": "", "class": "msctls_trackbar32", "enabled": true}, {"hwnd": 524718, "control id": 0, "wm text": "", "rect": {"top": 576, "right": 720, "left": 644, "bottom": 599}, "text": "", "class": "CtrlNotifySink", "enabled": true}, {"hwnd": 524686, "control id": 0, "wm text": "OK", "rect": {"top": 576, "right": 720, "left": 644, "bottom": 599}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 3736024, "control id": 0, "wm text": "", "rect": {"top": 576, "right": 802, "left": 726, "bottom": 599}, "text": "", "class": "CtrlNotifySink", "enabled": true}, {"hwnd": 3146122, "control id": 0, "wm text": "Cancel", "rect": {"top": 576, "right": 802, "left": 726, "bottom": 599}, "text": "Cancel", "class": "Button", "enabled": true}], "class": "NativeHWNDHost", "rect": {"top": 84, "right": 892, "left": 132, "bottom": 644}, "text": "User Account Control Settings"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (96, 100, 676, 115),
           'snapshots': ['user_account_control_settings.edge.Tell me more about user account control settings.0.bmp'],
           'type': 'link'}

ELEM_01 = {'visual': (512, 492, 588, 515),
           'snapshots': ['user_account_control_settings.edge.Ok.0.bmp'],
           'type': 'normal'}

ELEM_02 = {'visual': (594, 492, 670, 515),
           'snapshots': ['user_account_control_settings.edge.Cancel.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Tell me more about user account control settings',
             'goes to': 'Windows Help And Support',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 721316, "control id": 0, "wm text": "<a href=\"\">Tell me more about User Account Control settings</a>", "rect": {"top": 184, "right": 808, "left": 228, "bottom": 199}, "text": "<a href=\"\">Tell me more about User Account Control settings</a>", "class": "SysLink", "enabled": true}}}

V_ELEM_01 = {'desc': 'Ok',
             'goes to': 'User Access Control_3',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 524686, "control id": 0, "wm text": "OK", "rect": {"top": 576, "right": 720, "left": 644, "bottom": 599}, "text": "OK", "class": "Button", "enabled": true}}}

V_ELEM_02 = {'desc': 'Cancel',
             'goes to': 'Node 0',
             'how': ELEM_02,
             'custom': {"window": {"hwnd": 3146122, "control id": 0, "wm text": "Cancel", "rect": {"top": 576, "right": 802, "left": 726, "bottom": 599}, "text": "Cancel", "class": "Button", "enabled": true}}}

