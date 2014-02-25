'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Choose Install Location',
        'snapshots': ['choose_install_location.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['choose_install_location.0.ref.bmp'],
        'custom': {"scrap": {"hwnd": 2228642, "childs": [{"hwnd": 4063586, "control id": 1, "wm text": "&Install", "rect": {"top": 521, "right": 662, "left": 587, "bottom": 544}, "text": "&Install", "class": "Button", "enabled": true}, {"hwnd": 590236, "control id": 2, "wm text": "Cancel", "rect": {"top": 521, "right": 748, "left": 673, "bottom": 544}, "text": "Cancel", "class": "Button", "enabled": true}, {"hwnd": 524686, "control id": 1035, "wm text": "", "rect": {"top": 508, "right": 751, "left": 271, "bottom": 510}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 3146122, "control id": 1036, "wm text": "", "rect": {"top": 251, "right": 771, "left": 263, "bottom": 253}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 2359788, "control id": 1256, "wm text": "www.7-zip.org ", "rect": {"top": 500, "right": 754, "left": 271, "bottom": 513}, "text": "www.7-zip.org ", "class": "Static", "enabled": true}, {"hwnd": 655808, "control id": 1028, "wm text": "www.7-zip.org", "rect": {"top": 500, "right": 754, "left": 271, "bottom": 513}, "text": "www.7-zip.org", "class": "Static", "enabled": false}, {"hwnd": 590264, "control id": 1034, "wm text": "", "rect": {"top": 194, "right": 761, "left": 263, "bottom": 251}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 2949526, "control id": 1037, "wm text": "Choose Install Location", "rect": {"top": 202, "right": 698, "left": 278, "bottom": 218}, "text": "Choose Install Location", "class": "Static", "enabled": true}, {"hwnd": 721288, "control id": 1038, "wm text": "Choose the folder in which to install 7-Zip 9.20.", "rect": {"top": 220, "right": 699, "left": 286, "bottom": 246}, "text": "Choose the folder in which to install 7-Zip 9.20.", "class": "Static", "enabled": true}, {"hwnd": 328110, "control id": 1039, "wm text": "", "rect": {"top": 207, "right": 745, "left": 713, "bottom": 239}, "text": "", "class": "Static", "enabled": true}, {"hwnd": 393720, "control id": 0, "wm text": "", "rect": {"top": 267, "right": 736, "left": 286, "bottom": 495}, "text": "", "class": "#32770", "enabled": true}, {"hwnd": 262580, "control id": 1019, "wm text": "C:\\Program Files (x86)\\7-Zip", "rect": {"top": 405, "right": 616, "left": 301, "bottom": 425}, "text": "", "class": "Edit", "enabled": true}, {"hwnd": 3474054, "control id": 1001, "wm text": "B&rowse...", "rect": {"top": 402, "right": 718, "left": 628, "bottom": 426}, "text": "B&rowse...", "class": "Button", "enabled": true}, {"hwnd": 1966496, "control id": 1024, "wm text": "Space available: 7.2GB", "rect": {"top": 470, "right": 511, "left": 286, "bottom": 483}, "text": "Space available: 7.2GB", "class": "Static", "enabled": true}, {"hwnd": 459190, "control id": 1023, "wm text": "Space required: 3.3MB", "rect": {"top": 454, "right": 511, "left": 286, "bottom": 467}, "text": "Space required: 3.3MB", "class": "Static", "enabled": true}, {"hwnd": 3670486, "control id": 1006, "wm text": "Setup will install 7-Zip 9.20 in the following folder. To install in a different folder, click Browse and select another folder. Click Install to start the installation.", "rect": {"top": 267, "right": 736, "left": 286, "bottom": 365}, "text": "Setup will install 7-Zip 9.20 in the following folder. To install in a different folder, click Browse and select another folder. Click Install to start the installation.", "class": "Static", "enabled": true}, {"hwnd": 262568, "control id": 1020, "wm text": "Destination Folder", "rect": {"top": 381, "right": 736, "left": 286, "bottom": 438}, "text": "Destination Folder", "class": "Button", "enabled": true}], "class": "#32770", "rect": {"top": 169, "right": 763, "left": 260, "bottom": 558}, "text": "7-Zip 9.20 Setup "}, "scraper": "windows api"}}


WORKER = None


ELEM_00 = {'visual': (327, 352, 402, 375),
           'snapshots': ['choose_install_location.edge.Install.0.bmp'],
           'type': 'normal'}

ELEM_01 = {'visual': (413, 352, 488, 375),
           'snapshots': ['choose_install_location.edge.Cancel.0.bmp'],
           'type': 'normal'}

ELEM_02 = {'visual': (41, 236, 356, 256),
           'snapshots': ['choose_install_location.edge.Text input.0.bmp'],
           'uses': 'value for Choose Install Location.Text input',
           'type': 'text input'}

ELEM_03 = {'visual': (368, 233, 458, 257),
           'snapshots': ['choose_install_location.edge.Browse.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Install',
             'goes to': 'Completing The 7_Zip 9_20 Setup Wizard',
             'how': ELEM_00,
             'custom': {"window": {"hwnd": 4063586, "control id": 1, "wm text": "&Install", "rect": {"top": 521, "right": 662, "left": 587, "bottom": 544}, "text": "&Install", "class": "Button", "enabled": true}}}

V_ELEM_01 = {'desc': 'Cancel',
             'goes to': 'Are You Sure You Want To Quit 7_Zip 9_20 Setup',
             'how': ELEM_01,
             'custom': {"window": {"hwnd": 590236, "control id": 2, "wm text": "Cancel", "rect": {"top": 521, "right": 748, "left": 673, "bottom": 544}, "text": "Cancel", "class": "Button", "enabled": true}}}

V_ELEM_02 = {'desc': 'Text input',
             'goes to': 'Choose Install Location',
             'how': ELEM_02,
             'uses': 'value for Choose Install Location.Text input',
             'custom': {"window": {"hwnd": 262580, "control id": 1019, "wm text": "C:\\Program Files (x86)\\7-Zip", "rect": {"top": 405, "right": 616, "left": 301, "bottom": 425}, "text": "", "class": "Edit", "enabled": true}}}

V_ELEM_03 = {'desc': 'Browse',
             'goes to': 'Select The Folder To Install 7_Zip 9_20 In',
             'how': ELEM_03,
             'custom': {"window": {"hwnd": 3474054, "control id": 1001, "wm text": "B&rowse...", "rect": {"top": 402, "right": 718, "left": 628, "bottom": 426}, "text": "B&rowse...", "class": "Button", "enabled": true}}}

