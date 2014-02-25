'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'User Access Control_2',
        'snapshots': ['node_02.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['node_02.0.ref.bmp'],
        'custom': {}}


WORKER = None


ELEM_00 = {'visual': (17, 198, 103, 216),
           'snapshots': ['node_02.edge.Hide details.0.bmp'],
           'type': 'other'}

ELEM_01 = {'visual': (292, 195, 364, 217),
           'snapshots': ['node_02.edge.Yes.0.bmp'],
           'type': 'other'}

ELEM_02 = {'visual': (373, 195, 445, 217),
           'snapshots': ['node_02.edge.No.0.bmp'],
           'type': 'other'}


V_ELEM_00 = {'desc': 'Hide details',
             'goes to': 'User Access Control',
             'how': ELEM_00,
             'custom': {}}

V_ELEM_01 = {'desc': 'Yes',
             'goes to': 'Choose Install Location',
             'how': ELEM_01,
             'custom': {}}

V_ELEM_02 = {'desc': 'No',
             'goes to': 'Node 0',
             'how': ELEM_02,
             'custom': {}}

