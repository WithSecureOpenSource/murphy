'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'User Access Control',
        'snapshots': ['node_01.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['node_01.0.ref.bmp'],
        'custom': {}}


WORKER = None


ELEM_00 = {'visual': (17, 181, 107, 199),
           'snapshots': ['node_01.edge.Show details.0.bmp'],
           'type': 'other'}

ELEM_01 = {'visual': (292, 178, 364, 200),
           'snapshots': ['node_01.edge.Yes.0.bmp'],
           'type': 'other'}

ELEM_02 = {'visual': (373, 178, 445, 200),
           'snapshots': ['node_01.edge.No.0.bmp'],
           'type': 'other'}


V_ELEM_00 = {'desc': 'Show details',
             'goes to': 'User Access Control_2',
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

