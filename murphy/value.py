'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Simple class that wraps a value, it's description, attributes that may compose
it and so
'''
import itertools, copy

class Value(object):

    def __init__(self, attribs):
        if not 'value' in attribs:
            raise ValueError('Attributes dictionary needs a "value" attribute')
        self._attributes = attribs
        
    def __getattr__(self, name):
        attribute = self._attributes[name]
        if name == 'value':
            if hasattr(attribute, '__call__'):
                self._attributes[name] = attribute(self._attributes)
                attribute = self._attributes[name]
        return self._attributes[name]
        
    def __str__(self):
        return str(self._attributes)

    def __repr__(self):
        return str(self._attributes)


class ValueFactory(object):

    def __init__(self, attribs, generator_fn=None, ui_fn=None):
        self._attributes = attribs
        self._generator_fn = generator_fn
        self._generate_from_ui = ui_fn
        
    def get_values(self):
        varNames = sorted(self._attributes)
        product = [dict(zip(varNames, prod))
                        for prod in itertools.product(*(self._attributes[varName] for varName in varNames))]
        values = []
        for attribs in product:
            full_attribs = copy.deepcopy(attribs)
            full_attribs['value'] = self._generator_fn
            value = Value(full_attribs)
            values.append(value)

        return values

    def is_value_list(self):
        return type(self._generate_from_ui) is list

    def is_ui_function_selector(self):
        return hasattr(self._generate_from_ui, '__call__')
        
    def from_ui(self, parent=None):
        if self.is_value_list():
            return self._generate_from_ui
        else:
            return self._generate_from_ui(parent)


        
def test_generator_fn(attribs):
    return {'product': 'ols',
            'type': 'predefined',
            'size': 3,
            'days': 90,
            'value': 'abcd-efgh'}

def test_generator_fn_product(attribs):
    return attribs['product']
    
def test():
    a_desc = {'product': 'ols', 'type': 'trial', 'size': 1, 'value': 'abcd-efgh'}
    
    value = Value(a_desc)
    print value.__class__.__name__
    
    assert (value.product, value.type) == ('ols', 'trial')
    
        
    factory = ValueFactory({'product': ['ols', 'olb', 'compsec', 'sync'],
                            'type': ['predefined', 'trial'],
                            'size': [1, 2, 3, 10],
                            'days': [90]},
                            test_generator_fn,
                            None)

    value = factory.get_values()[0]
    value.value
    assert str(value) == "{'product': 'ols', 'type': 'predefined', 'days': 90, 'value': {'product': 'ols', 'type': 'predefined', 'days': 90, 'value': 'abcd-efgh', 'size': 3}, 'size': 1}"
    print value.value

    factory = ValueFactory({'product': ['ols', 'olb', 'compsec', 'sync']},
                            test_generator_fn_product,
                            ['ols', 'olb', 'compsec', 'sync'])
    value = factory.get_values()[0]
    value.value
    print value.value

if __name__ == '__main__':
    test()