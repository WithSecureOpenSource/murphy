'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Were Sorry You Did Not Installed Us',
        'snapshots': ['were_sorry_you_did_not_installed_us.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['were_sorry_you_did_not_installed_us.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 459164, "childs": [{"hwnd": 1180012, "control id": 2, "wm text": "OK", "rect": {"top": 421, "right": 627, "left": 539, "bottom": 447}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 721350, "control id": 65535, "wm text": "We're sorry you did not installed us.", "rect": {"top": 368, "right": 598, "left": 409, "bottom": 385}, "text": "We're sorry you did not installed us.", "class": "Static", "enabled": true}], "class": "#32770", "rect": {"top": 317, "right": 638, "left": 394, "bottom": 461}, "text": "Bye"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (145, 104, 233, 130),
           'snapshots': ['were_sorry_you_did_not_installed_us.edge.Ok.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Ok',
             'goes to': 'Node 0',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 1180012, "control id": 2, "wm text": "OK", "rect": {"top": 421, "right": 627, "left": 539, "bottom": 447}, "text": "OK", "class": "Button", "enabled": true}}}

