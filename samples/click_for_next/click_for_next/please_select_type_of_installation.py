'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Please Select Type Of Installation',
        'snapshots': ['please_select_type_of_installation.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['please_select_type_of_installation.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 262556, "childs": [{"hwnd": 1048940, "control id": 3, "wm text": "Please select type of installation", "rect": {"top": 166, "right": 373, "left": 188, "bottom": 191}, "text": "Please select type of installation", "class": "Static", "enabled": true}, {"hwnd": 590278, "control id": 4, "wm text": "Full, the product will install all it's components", "rect": {"top": 196, "right": 448, "left": 188, "bottom": 226}, "text": "Full, the product will install all it's components", "class": "Button", "enabled": true}, {"hwnd": 262724, "control id": 5, "wm text": "Minimal, only the core components", "rect": {"top": 226, "right": 448, "left": 188, "bottom": 256}, "text": "Minimal, only the core components", "class": "Button", "enabled": true}, {"hwnd": 524642, "control id": 6, "wm text": "&Cancel", "rect": {"top": 554, "right": 310, "left": 206, "bottom": 582}, "text": "&Cancel", "class": "Button", "enabled": true}, {"hwnd": 262586, "control id": 7, "wm text": "&Next", "rect": {"top": 554, "right": 822, "left": 718, "bottom": 582}, "text": "&Next", "class": "Button", "enabled": false}], "class": "AutoIt v3 GUI", "rect": {"top": 131, "right": 851, "left": 175, "bottom": 599}, "text": "SuperApp Installer"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (13, 65, 273, 95),
           'snapshots': ['please_select_type_of_installation.edge.Full the product will install all its components.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (13, 95, 273, 125),
           'snapshots': ['please_select_type_of_installation.edge.Minimal only the core components.0.bmp'],
           'type': 'normal'}

ELEM_02 = {'visual': (31, 423, 135, 451),
           'snapshots': ['please_select_type_of_installation.edge.Cancel.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Full the product will install all its components',
             'goes to': 'Please Select Type Of Installation_2',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 590278, "control id": 4, "wm text": "Full, the product will install all it's components", "rect": {"top": 196, "right": 448, "left": 188, "bottom": 226}, "text": "Full, the product will install all it's components", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'Minimal only the core components',
             'goes to': 'Please Select Type Of Installation_2',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 262724, "control id": 5, "wm text": "Minimal, only the core components", "rect": {"top": 226, "right": 448, "left": 188, "bottom": 256}, "text": "Minimal, only the core components", "class": "Button", "enabled": true}}}

V_ELEM_02 = {'desc': 'Cancel',
             'goes to': 'Node 0',
             'how': ELEM_02,
             'custom': {"window": {"hwnd": 524642, "control id": 6, "wm text": "&Cancel", "rect": {"top": 554, "right": 310, "left": 206, "bottom": 582}, "text": "&Cancel", "class": "Button", "enabled": true}}}

