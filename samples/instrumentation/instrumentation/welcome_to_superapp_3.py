'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Welcome To Superapp_3',
        'snapshots': ['welcome_to_superapp_3.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['welcome_to_superapp_3.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 1310922, "childs": [{"hwnd": 328362, "control id": 3, "wm text": "Welcome to SuperApp!", "rect": {"top": 266, "right": 613, "left": 288, "bottom": 321}, "text": "Welcome to SuperApp!", "class": "Static", "enabled": true}, {"hwnd": 983078, "control id": 4, "wm text": "Destination Folder", "rect": {"top": 341, "right": 613, "left": 288, "bottom": 396}, "text": "Destination Folder", "class": "Static", "enabled": true}, {"hwnd": 787048, "control id": 5, "wm text": "C:\\Program Files\\Here", "rect": {"top": 366, "right": 738, "left": 288, "bottom": 386}, "text": "C:\\Program Files\\Here", "class": "Edit", "enabled": true}, {"hwnd": 721430, "control id": 6, "wm text": "&Cancel", "rect": {"top": 454, "right": 400, "left": 296, "bottom": 482}, "text": "&Cancel", "class": "Button", "enabled": true}, {"hwnd": 459280, "control id": 7, "wm text": "&Next >>", "rect": {"top": 454, "right": 732, "left": 628, "bottom": 482}, "text": "&Next >>", "class": "Button", "enabled": true}], "class": "AutoIt v3 GUI", "rect": {"top": 231, "right": 751, "left": 275, "bottom": 499}, "text": "SuperApp Installer"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (13, 135, 463, 155),
           'snapshots': ['welcome_to_superapp_3.edge.Text input.0.bmp'],
           'uses': 'value for Welcome To Superapp_3.Text input',
           'type': 'text input'}

ELEM_01 = {'visual': (21, 223, 125, 251),
           'snapshots': ['welcome_to_superapp_3.edge.Cancel.0.bmp'],
           'type': 'normal'}

ELEM_02 = {'visual': (353, 223, 457, 251),
           'snapshots': ['welcome_to_superapp_3.edge.Next.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Text input',
             'goes to': 'Welcome To Superapp_3',
             'how': ELEM_00,
             'uses': 'value for Welcome To Superapp_3.Text input',
             'custom': {"window": {"hwnd": 787048, "control id": 5, "wm text": "C:\\Program Files\\Here", "rect": {"top": 366, "right": 738, "left": 288, "bottom": 386}, "text": "C:\\Program Files\\Here", "class": "Edit", "enabled": true}}}

V_ELEM_01 = {'desc': 'Cancel',
             'goes to': 'Are You Sure You Want To Cancel The Installation',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 721430, "control id": 6, "wm text": "&Cancel", "rect": {"top": 454, "right": 400, "left": 296, "bottom": 482}, "text": "&Cancel", "class": "Button", "enabled": true}}}

V_ELEM_02 = {'desc': 'Next',
             'goes to': 'Installation Completed Enjoy',
             'how': ELEM_02,
             'custom': {"window": {"hwnd": 459280, "control id": 7, "wm text": "&Next >>", "rect": {"top": 454, "right": 732, "left": 628, "bottom": 482}, "text": "&Next >>", "class": "Button", "enabled": true}},
             'logs': "log-62165b61-a2cb-11e3-a0f9-028037ec0200.json"}

