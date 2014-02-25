'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Node 1',
        'snapshots': ['node_01.0.bmp'],
        'snapshots mask': [3978044416],
        'reference snapshots': ['node_01.0.ref.bmp'],
        'custom': {}}


WORKER = None


ELEM_00 = {'visual': (41, 236, 355, 255),
           'snapshots': ['node_01.edge.Element 0.0.bmp'],
           'uses': 'value for Node 1.Element 0',
           'type': 'text input'}

ELEM_01 = {'visual': (328, 353, 400, 373),
           'snapshots': ['node_01.edge.Element 1.0.bmp'],
           'type': 'normal'}

ELEM_02 = {'visual': (369, 234, 456, 255),
           'snapshots': ['node_01.edge.Element 2.0.bmp'],
           'type': 'normal'}

ELEM_03 = {'visual': (414, 353, 486, 373),
           'snapshots': ['node_01.edge.Element 3.0.bmp'],
           'type': 'normal'}


V_ELEM_00 = {'desc': 'Element 0',
             'goes to': 'Node 1',
             'how': ELEM_00,
             'uses': 'value for Node 1.Element 0',
             'custom': {}}

V_ELEM_01 = {'desc': 'Element 1',
             'goes to': 'Node 2',
             'how': ELEM_01,
             'custom': {}}

V_ELEM_02 = {'desc': 'Element 2',
             'goes to': 'Node 3',
             'how': ELEM_02,
             'custom': {}}

V_ELEM_03 = {'desc': 'Element 3',
             'goes to': 'Node 4',
             'how': ELEM_03,
             'custom': {}}

