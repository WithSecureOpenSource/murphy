'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Please Type In Your Installation Key And Click Ok',
        'snapshots': ['please_type_in_your_installation_key_and_click_ok.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['please_type_in_your_installation_key_and_click_ok.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 262800, "childs": [{"hwnd": 1245656, "control id": 1002, "wm text": "Please type in your installation key and click OK", "rect": {"top": 354, "right": 634, "left": 390, "bottom": 393}, "text": "Please type in your installation key and click OK", "class": "Static", "enabled": true}, {"hwnd": 4588068, "control id": 1001, "wm text": "", "rect": {"top": 388, "right": 634, "left": 390, "bottom": 408}, "text": "", "class": "Edit", "enabled": true}, {"hwnd": 3735956, "control id": 1, "wm text": "OK", "rect": {"top": 413, "right": 489, "left": 414, "bottom": 436}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 983440, "control id": 2, "wm text": "Cancel", "rect": {"top": 413, "right": 611, "left": 536, "bottom": 436}, "text": "Cancel", "class": "Button", "enabled": true}], "class": "#32770", "rect": {"top": 314, "right": 652, "left": 372, "bottom": 454}, "text": "Welcome to superapp"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (18, 74, 262, 94),
           'snapshots': ['please_type_in_your_installation_key_and_click_ok.edge.Text input.0.bmp'],
           'uses': 'value for Please Type In Your Installation Key And Click Ok.Text input',
           'type': 'text input'}

ELEM_01 = {'visual': (42, 99, 117, 122),
           'snapshots': ['please_type_in_your_installation_key_and_click_ok.edge.Ok.0.bmp'],
           'type': 'normal'}

ELEM_02 = {'visual': (164, 99, 239, 122),
           'snapshots': ['please_type_in_your_installation_key_and_click_ok.edge.Cancel.0.bmp'],
           'type': 'normal'}

ELEM_03 = {'visual': (18, 74, 262, 94),
           'snapshots': ['please_type_in_your_installation_key_and_click_ok.edge.Valid serial.0.bmp'],
           'type': 'normal'}


def press_ok():
    '''
    Simplest way, press enter...
    '''        
    WORKER.input.keyboard.enters('{enter}')


ELEM_04 = {'visual': (18, 74, 262, 94),
           'snapshots': ['please_type_in_your_installation_key_and_click_ok.edge.Demo serial.0.bmp'],
           'type': 'normal'}


def press_ok():
    '''
    Simplest way, press enter...
    '''        
    WORKER.input.keyboard.enters('{enter}')



V_ELEM_00 = {'desc': 'Text input',
             'goes to': 'Please Type In Your Installation Key And Click Ok',
             'how': ELEM_00,
             'uses': 'value for Please Type In Your Installation Key And Click Ok.Text input',
             'custom': {"window": {"hwnd": 4588068, "control id": 1001, "wm text": "", "rect": {"top": 388, "right": 634, "left": 390, "bottom": 408}, "text": "", "class": "Edit", "enabled": true}}}

V_ELEM_01 = {'desc': 'Ok',
             'goes to': 'Invalid Key Please Try Again',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 3735956, "control id": 1, "wm text": "OK", "rect": {"top": 413, "right": 489, "left": 414, "bottom": 436}, "text": "OK", "class": "Button", "enabled": true}}}

V_ELEM_02 = {'desc': 'Cancel',
             'goes to': 'Were Sorry You Did Not Installed Us',
             'how': ELEM_02,
             'custom': {"window": {"hwnd": 983440, "control id": 2, "wm text": "Cancel", "rect": {"top": 413, "right": 611, "left": 536, "bottom": 436}, "text": "Cancel", "class": "Button", "enabled": true}}}

V_ELEM_03 = {'desc': 'Valid serial',
             'goes to': 'Thans For Installing Our Full Version',
             'how': press_ok,
             'custom': {}}

V_ELEM_04 = {'desc': 'Demo serial',
             'goes to': 'Thans For Installing Our Demo Version',
             'how': press_ok,
             'custom': {}}

