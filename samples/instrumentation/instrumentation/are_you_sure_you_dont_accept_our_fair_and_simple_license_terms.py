'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Are You Sure You Dont Accept Our Fair And Simple License Terms',
        'snapshots': ['are_you_sure_you_dont_accept_our_fair_and_simple_license_terms.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['are_you_sure_you_dont_accept_our_fair_and_simple_license_terms.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 262208, "childs": [{"hwnd": 458976, "control id": 1, "wm text": "OK", "rect": {"top": 429, "right": 626, "left": 538, "bottom": 455}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 590322, "control id": 2, "wm text": "Cancel", "rect": {"top": 429, "right": 724, "left": 636, "bottom": 455}, "text": "Cancel", "class": "Button", "enabled": true}, {"hwnd": 197290, "control id": 20, "wm text": "", "rect": {"top": 359, "right": 352, "left": 320, "bottom": 391}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 197288, "control id": 65535, "wm text": "Are you sure you dont accept our fair and simple license terms?", "rect": {"top": 367, "right": 696, "left": 360, "bottom": 384}, "text": "Are you sure you dont accept our fair and simple license terms?", "class": "Static", "enabled": true}], "class": "#32770", "rect": {"top": 308, "right": 736, "left": 292, "bottom": 469}, "text": "Installation"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (246, 121, 334, 147),
           'snapshots': ['are_you_sure_you_dont_accept_our_fair_and_simple_license_terms.edge.Ok.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (344, 121, 432, 147),
           'snapshots': ['are_you_sure_you_dont_accept_our_fair_and_simple_license_terms.edge.Cancel.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Ok',
             'goes to': 'Node 0',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 458976, "control id": 1, "wm text": "OK", "rect": {"top": 429, "right": 626, "left": 538, "bottom": 455}, "text": "OK", "class": "Button", "enabled": true}},
             'logs': "log-62157100-a2cb-11e3-a262-028037ec0200.json"}

V_ELEM_01 = {'desc': 'Cancel',
             'goes to': 'Welcome To Superapp_2',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 590322, "control id": 2, "wm text": "Cancel", "rect": {"top": 429, "right": 724, "left": 636, "bottom": 455}, "text": "Cancel", "class": "Button", "enabled": true}}}

