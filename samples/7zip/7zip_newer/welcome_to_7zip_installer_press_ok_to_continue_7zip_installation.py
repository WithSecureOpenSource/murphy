'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Welcome To 7Zip Installer Press Ok To Continue 7Zip Installation',
        'snapshots': ['welcome_to_7zip_installer_press_ok_to_continue_7zip_installation.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['welcome_to_7zip_installer_press_ok_to_continue_7zip_installation.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 262558, "childs": [{"hwnd": 2425310, "control id": 1, "wm text": "OK", "rect": {"top": 421, "right": 602, "left": 514, "bottom": 447}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 2753002, "control id": 2, "wm text": "Cancel", "rect": {"top": 421, "right": 698, "left": 610, "bottom": 447}, "text": "Cancel", "class": "Button", "enabled": true}, {"hwnd": 2425368, "control id": 65535, "wm text": "Welcome to 7zip installer, press OK to continue 7zip installation", "rect": {"top": 368, "right": 669, "left": 335, "bottom": 385}, "text": "Welcome to 7zip installer, press OK to continue 7zip installation", "class": "Static", "enabled": true}], "class": "#32770", "rect": {"top": 317, "right": 709, "left": 320, "bottom": 461}, "text": "7-Zip 9.90 Setup"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (194, 104, 282, 130),
           'snapshots': ['welcome_to_7zip_installer_press_ok_to_continue_7zip_installation.edge.Ok.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (290, 104, 378, 130),
           'snapshots': ['welcome_to_7zip_installer_press_ok_to_continue_7zip_installation.edge.Cancel.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Ok',
             'goes to': 'Choose Install Location',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 2425310, "control id": 1, "wm text": "OK", "rect": {"top": 421, "right": 602, "left": 514, "bottom": 447}, "text": "OK", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'Cancel',
             'goes to': 'Node 0',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 2753002, "control id": 2, "wm text": "Cancel", "rect": {"top": 421, "right": 698, "left": 610, "bottom": 447}, "text": "Cancel", "class": "Button", "enabled": true}}}

