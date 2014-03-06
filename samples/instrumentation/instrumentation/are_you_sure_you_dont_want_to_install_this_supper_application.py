'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Are You Sure You Dont Want To Install This Supper Application',
        'snapshots': ['are_you_sure_you_dont_want_to_install_this_supper_application.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['are_you_sure_you_dont_want_to_install_this_supper_application.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 197240, "childs": [{"hwnd": 458976, "control id": 1, "wm text": "OK", "rect": {"top": 429, "right": 623, "left": 535, "bottom": 455}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 590322, "control id": 2, "wm text": "Cancel", "rect": {"top": 429, "right": 719, "left": 631, "bottom": 455}, "text": "Cancel", "class": "Button", "enabled": true}, {"hwnd": 197290, "control id": 20, "wm text": "", "rect": {"top": 359, "right": 359, "left": 327, "bottom": 391}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 197288, "control id": 65535, "wm text": "Are you sure you dont want to install this supper application?", "rect": {"top": 367, "right": 691, "left": 367, "bottom": 384}, "text": "Are you sure you dont want to install this supper application?", "class": "Static", "enabled": true}], "class": "#32770", "rect": {"top": 308, "right": 730, "left": 299, "bottom": 469}, "text": "Installation"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (236, 121, 324, 147),
           'snapshots': ['are_you_sure_you_dont_want_to_install_this_supper_application.edge.Ok.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (332, 121, 420, 147),
           'snapshots': ['are_you_sure_you_dont_want_to_install_this_supper_application.edge.Cancel.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Ok',
             'goes to': 'Node 0',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 458976, "control id": 1, "wm text": "OK", "rect": {"top": 429, "right": 623, "left": 535, "bottom": 455}, "text": "OK", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'Cancel',
             'goes to': 'Welcome To Superapp',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 590322, "control id": 2, "wm text": "Cancel", "rect": {"top": 429, "right": 719, "left": 631, "bottom": 455}, "text": "Cancel", "class": "Button", "enabled": true}}}

