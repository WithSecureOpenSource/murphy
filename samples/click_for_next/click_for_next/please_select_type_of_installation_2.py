'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Please Select Type Of Installation_2',
        'snapshots': ['please_select_type_of_installation_2.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['please_select_type_of_installation_2.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 2884142, "childs": [{"hwnd": 1901040, "control id": 3, "wm text": "Please select type of installation", "rect": {"top": 166, "right": 373, "left": 188, "bottom": 191}, "text": "Please select type of installation", "class": "Static", "enabled": true}, {"hwnd": 1900990, "control id": 4, "wm text": "Full, the product will install all it's components", "rect": {"top": 196, "right": 448, "left": 188, "bottom": 226}, "text": "Full, the product will install all it's components", "class": "Button", "enabled": true}, {"hwnd": 917850, "control id": 5, "wm text": "Minimal, only the core components", "rect": {"top": 226, "right": 448, "left": 188, "bottom": 256}, "text": "Minimal, only the core components", "class": "Button", "enabled": true}, {"hwnd": 262800, "control id": 6, "wm text": "&Cancel", "rect": {"top": 554, "right": 310, "left": 206, "bottom": 582}, "text": "&Cancel", "class": "Button", "enabled": true}, {"hwnd": 1245498, "control id": 7, "wm text": "&Next", "rect": {"top": 554, "right": 822, "left": 718, "bottom": 582}, "text": "&Next", "class": "Button", "enabled": true}], "class": "AutoIt v3 GUI", "rect": {"top": 131, "right": 851, "left": 175, "bottom": 599}, "text": "SuperApp Installer"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (13, 65, 273, 95),
           'snapshots': ['please_select_type_of_installation_2.edge.Full the product will install all its components.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (13, 95, 273, 125),
           'snapshots': ['please_select_type_of_installation_2.edge.Minimal only the core components.0.bmp'],
           'type': 'normal'}

ELEM_02 = {'visual': (31, 423, 135, 451),
           'snapshots': ['please_select_type_of_installation_2.edge.Cancel.0.bmp'],
           'type': 'normal'}

ELEM_03 = {'visual': (543, 423, 647, 451),
           'snapshots': ['please_select_type_of_installation_2.edge.Next.0.bmp'],
           'type': 'normal'}

ELEM_04 = {'visual': (543, 423, 647, 451),
           'snapshots': ['please_select_type_of_installation_2.edge.Next_2.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Full the product will install all its components',
             'goes to': 'Please Select Type Of Installation_2',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 1900990, "control id": 4, "wm text": "Full, the product will install all it's components", "rect": {"top": 196, "right": 448, "left": 188, "bottom": 226}, "text": "Full, the product will install all it's components", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'Minimal only the core components',
             'goes to': 'Please Select Type Of Installation_2',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 917850, "control id": 5, "wm text": "Minimal, only the core components", "rect": {"top": 226, "right": 448, "left": 188, "bottom": 256}, "text": "Minimal, only the core components", "class": "Button", "enabled": true}}}

V_ELEM_02 = {'desc': 'Cancel',
             'goes to': 'Node 0',
             'how': ELEM_02,
             'custom': {"window": {"hwnd": 262800, "control id": 6, "wm text": "&Cancel", "rect": {"top": 554, "right": 310, "left": 206, "bottom": 582}, "text": "&Cancel", "class": "Button", "enabled": true}}}

V_ELEM_03 = {'desc': 'Next',
             'goes to': 'Installation Is Completed Only The Core Modules Were Installed',
             'how': ELEM_03,
             'custom': {"window": {"hwnd": 1245498, "control id": 7, "wm text": "&Next", "rect": {"top": 554, "right": 822, "left": 718, "bottom": 582}, "text": "&Next", "class": "Button", "enabled": true}}}

V_ELEM_04 = {'desc': 'Next_2',
             'goes to': 'Installation Is Completed For The Full Product',
             'how': ELEM_04,
             'custom': {"window": {"hwnd": 1245498, "control id": 7, "wm text": "&Next", "rect": {"top": 554, "right": 822, "left": 718, "bottom": 582}, "text": "&Next", "class": "Button", "enabled": true}}}

