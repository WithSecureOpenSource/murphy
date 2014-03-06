'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Are You Sure You Want To Quit 7_Zip 9_20 Setup',
        'snapshots': ['are_you_sure_you_want_to_quit_7_zip_9_20_setup.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['are_you_sure_you_want_to_quit_7_zip_9_20_setup.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 4326024, "childs": [{"hwnd": 655818, "control id": 6, "wm text": "&Yes", "rect": {"top": 429, "right": 586, "left": 498, "bottom": 455}, "text": "&Yes", "class": "Button", "enabled": true}, {"hwnd": 328088, "control id": 7, "wm text": "&No", "rect": {"top": 429, "right": 683, "left": 595, "bottom": 455}, "text": "&No", "class": "Button", "enabled": true}, {"hwnd": 1245548, "control id": 20, "wm text": "", "rect": {"top": 359, "right": 396, "left": 364, "bottom": 391}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 786886, "control id": 65535, "wm text": "Are you sure you want to quit 7-Zip 9.20 Setup?", "rect": {"top": 367, "right": 654, "left": 404, "bottom": 384}, "text": "Are you sure you want to quit 7-Zip 9.20 Setup?", "class": "Static", "enabled": true}], "class": "#32770", "rect": {"top": 308, "right": 694, "left": 336, "bottom": 469}, "text": "7-Zip 9.20 Setup"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (162, 121, 250, 147),
           'snapshots': ['are_you_sure_you_want_to_quit_7_zip_9_20_setup.edge.Yes.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (259, 121, 347, 147),
           'snapshots': ['are_you_sure_you_want_to_quit_7_zip_9_20_setup.edge.No.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Yes',
             'goes to': 'Node 0',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 655818, "control id": 6, "wm text": "&Yes", "rect": {"top": 429, "right": 586, "left": 498, "bottom": 455}, "text": "&Yes", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'No',
             'goes to': 'Choose Install Location',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 328088, "control id": 7, "wm text": "&No", "rect": {"top": 429, "right": 683, "left": 595, "bottom": 455}, "text": "&No", "class": "Button", "enabled": true}}}

