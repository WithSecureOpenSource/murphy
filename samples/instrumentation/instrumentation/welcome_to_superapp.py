'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Welcome To Superapp',
        'snapshots': ['welcome_to_superapp.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['welcome_to_superapp.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 852294, "childs": [{"hwnd": 1114314, "control id": 3, "wm text": "Welcome to SuperApp!", "rect": {"top": 266, "right": 613, "left": 288, "bottom": 321}, "text": "Welcome to SuperApp!", "class": "Static", "enabled": true}, {"hwnd": 852006, "control id": 4, "wm text": "To install superapp please press next.", "rect": {"top": 311, "right": 613, "left": 288, "bottom": 366}, "text": "To install superapp please press next.", "class": "Static", "enabled": true}, {"hwnd": 655976, "control id": 5, "wm text": "&Cancel", "rect": {"top": 454, "right": 400, "left": 296, "bottom": 482}, "text": "&Cancel", "class": "Button", "enabled": true}, {"hwnd": 590358, "control id": 6, "wm text": "&Next >>", "rect": {"top": 454, "right": 732, "left": 628, "bottom": 482}, "text": "&Next >>", "class": "Button", "enabled": true}], "class": "AutoIt v3 GUI", "rect": {"top": 231, "right": 751, "left": 275, "bottom": 499}, "text": "SuperApp Installer"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (21, 223, 125, 251),
           'snapshots': ['welcome_to_superapp.edge.Cancel.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (353, 223, 457, 251),
           'snapshots': ['welcome_to_superapp.edge.Next.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Cancel',
             'goes to': 'Are You Sure You Dont Want To Install This Supper Application',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 655976, "control id": 5, "wm text": "&Cancel", "rect": {"top": 454, "right": 400, "left": 296, "bottom": 482}, "text": "&Cancel", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'Next',
             'goes to': 'Welcome To Superapp_2',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 590358, "control id": 6, "wm text": "&Next >>", "rect": {"top": 454, "right": 732, "left": 628, "bottom": 482}, "text": "&Next >>", "class": "Button", "enabled": true}},
             'logs': "log-6212159e-a2cb-11e3-846e-028037ec0200.json"}

