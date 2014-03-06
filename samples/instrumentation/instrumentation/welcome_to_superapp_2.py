'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Welcome To Superapp_2',
        'snapshots': ['welcome_to_superapp_2.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['welcome_to_superapp_2.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 983078, "childs": [{"hwnd": 590444, "control id": 3, "wm text": "Welcome to SuperApp!", "rect": {"top": 266, "right": 613, "left": 288, "bottom": 321}, "text": "Welcome to SuperApp!", "class": "Static", "enabled": true}, {"hwnd": 393744, "control id": 4, "wm text": "License Terms", "rect": {"top": 301, "right": 613, "left": 288, "bottom": 356}, "text": "License Terms", "class": "Static", "enabled": true}, {"hwnd": 655894, "control id": 5, "wm text": "&Cancel", "rect": {"top": 454, "right": 400, "left": 296, "bottom": 482}, "text": "&Cancel", "class": "Button", "enabled": true}, {"hwnd": 721512, "control id": 6, "wm text": "&Next >>", "rect": {"top": 454, "right": 732, "left": 628, "bottom": 482}, "text": "&Next >>", "class": "Button", "enabled": true}, {"hwnd": 197240, "control id": 7, "wm text": "I hereby accept full responsibility for whatever happens whenever happens for whatever I do\r\nBy pressing next I take all the risks like a grown up.", "rect": {"top": 326, "right": 738, "left": 288, "bottom": 386}, "text": "I hereby accept full responsibility for whatever happens whenever happens for whatever I do\r\nBy pressing next I take all the risks like a grown up.", "class": "Static", "enabled": true}], "class": "AutoIt v3 GUI", "rect": {"top": 231, "right": 751, "left": 275, "bottom": 499}, "text": "SuperApp Installer"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (21, 223, 125, 251),
           'snapshots': ['welcome_to_superapp_2.edge.Cancel.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (353, 223, 457, 251),
           'snapshots': ['welcome_to_superapp_2.edge.Next.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Cancel',
             'goes to': 'Are You Sure You Dont Accept Our Fair And Simple License Terms',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 655894, "control id": 5, "wm text": "&Cancel", "rect": {"top": 454, "right": 400, "left": 296, "bottom": 482}, "text": "&Cancel", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'Next',
             'goes to': 'Welcome To Superapp_3',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 721512, "control id": 6, "wm text": "&Next >>", "rect": {"top": 454, "right": 732, "left": 628, "bottom": 482}, "text": "&Next >>", "class": "Button", "enabled": true}}}

