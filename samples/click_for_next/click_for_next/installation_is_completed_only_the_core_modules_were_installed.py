'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Installation Is Completed Only The Core Modules Were Installed',
        'snapshots': ['installation_is_completed_only_the_core_modules_were_installed.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['installation_is_completed_only_the_core_modules_were_installed.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 1114538, "childs": [{"hwnd": 1376510, "control id": 2, "wm text": "OK", "rect": {"top": 421, "right": 696, "left": 608, "bottom": 447}, "text": "OK", "class": "Button", "enabled": true}, {"hwnd": 1245508, "control id": 65535, "wm text": "Installation is completed, only the core modules were installed.", "rect": {"top": 368, "right": 668, "left": 335, "bottom": 385}, "text": "Installation is completed, only the core modules were installed.", "class": "Static", "enabled": true}], "class": "#32770", "rect": {"top": 317, "right": 708, "left": 320, "bottom": 461}, "text": "Installation completed"}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (288, 104, 376, 130),
           'snapshots': ['installation_is_completed_only_the_core_modules_were_installed.edge.Ok.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Ok',
             'goes to': 'Node 0',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 1376510, "control id": 2, "wm text": "OK", "rect": {"top": 421, "right": 696, "left": 608, "bottom": 447}, "text": "OK", "class": "Button", "enabled": true}}}

