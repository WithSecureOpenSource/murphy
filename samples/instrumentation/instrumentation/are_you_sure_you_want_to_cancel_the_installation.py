'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Are You Sure You Want To Cancel The Installation',
        'snapshots': ['are_you_sure_you_want_to_cancel_the_installation.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['are_you_sure_you_want_to_cancel_the_installation.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 524552, "childs": [{"hwnd": 983500, "control id": 1, "wm text": "OK", "rect": {"top": 429, "right": 589, "left": 501, "bottom": 455}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 262822, "control id": 2, "wm text": "Cancel", "rect": {"top": 429, "right": 687, "left": 599, "bottom": 455}, "text": "Cancel", "class": "Button", "enabled": true}, {"hwnd": 327744, "control id": 20, "wm text": "", "rect": {"top": 359, "right": 393, "left": 361, "bottom": 391}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 655858, "control id": 65535, "wm text": "Are you sure you want to cancel the installation?", "rect": {"top": 367, "right": 658, "left": 401, "bottom": 384}, "text": "Are you sure you want to cancel the installation?", "class": "Static", "enabled": true}], "class": "#32770", "rect": {"top": 308, "right": 698, "left": 333, "bottom": 469}, "text": "Installation"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (168, 121, 256, 147),
           'snapshots': ['are_you_sure_you_want_to_cancel_the_installation.edge.Ok.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (266, 121, 354, 147),
           'snapshots': ['are_you_sure_you_want_to_cancel_the_installation.edge.Cancel.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Ok',
             'goes to': 'Node 0',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 983500, "control id": 1, "wm text": "OK", "rect": {"top": 429, "right": 589, "left": 501, "bottom": 455}, "text": "OK", "class": "Button", "enabled": true}},
             'logs': "log-621745c0-a2cb-11e3-ad89-028037ec0200.json"}

V_ELEM_01 = {'desc': 'Cancel',
             'goes to': 'Welcome To Superapp_3',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 262822, "control id": 2, "wm text": "Cancel", "rect": {"top": 429, "right": 687, "left": 599, "bottom": 455}, "text": "Cancel", "class": "Button", "enabled": true}}}

