'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'User Access Control_2',
        'snapshots': ['node_04.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['node_04.0.ref.bmp'],
        'custom': {}}


WORKER = None


ELEM_00 = {'visual': (292, 195, 364, 217),
           'snapshots': ['node_04.edge.Element 0.0.bmp'],
           'type': 'other'}

ELEM_01 = {'visual': (373, 195, 445, 217),
           'snapshots': ['node_04.edge.Element 1.0.bmp'],
           'type': 'other'}

ELEM_02 = {'visual': (236, 239, 447, 253),
           'snapshots': ['node_04.edge.Element 2.0.bmp'],
           'type': 'other'}

ELEM_03 = {'visual': (17, 198, 103, 216),
           'snapshots': ['node_04.edge.Element 3.0.bmp'],
           'type': 'other'}


V_ELEM_00 = {'desc': 'Element 0',
             'goes to': 'Choose Install Location',
             'how': ELEM_00,
             'custom': {}}

V_ELEM_01 = {'desc': 'Element 1',
             'goes to': 'Node 0',
             'how': ELEM_01,
             'custom': {}}

V_ELEM_02 = {'desc': 'Element 2',
             'how': ELEM_02,
             'custom': {}}

V_ELEM_03 = {'desc': 'Element 3',
             'goes to': 'User Access Control',
             'how': ELEM_03,
             'custom': {}}

