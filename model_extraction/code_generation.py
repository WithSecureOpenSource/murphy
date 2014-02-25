'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Code generator for windows

Python module layout:

head comment - docstring introducing the module

imports

class declaration

    class comment

init method

other methods
    method docstring
    method code
    

'''

import time
import StringIO, string, unicodedata

HEADER_TEMPLATE = '\'\'\'\n\
%(docstring)s\n\
\'\'\'\n'

CLASS_DECLARATION_TEMPLATE = '\
class %(class_name)s(object):\n'

CLASS_DOCSTRING_TEMPLATE = '\
    \'\'\'\n\
    %(docstring)s\n\
    \'\'\'\n'

CLASS_INIT_TEMPLATE = '\
    def __init__(self):\n\
        %(body)s\n'

METHOD_DECLARATION_TEMPLATE = '\
    def %(name)s(self):\n'

METHOD_DOCSTRING_TEMPLATE = '\
        \'\'\'\n\
        %(docstring)s\n\
        \'\'\'\n'


VALID_CHARS = '_%s%s' % (string.ascii_letters, string.digits)

def letterize(text):
    '''
    Returns a string formed by letters, symbols are replaced for their textual
    representation
    '''
    result = ''
    for letter in text:
        if letter in VALID_CHARS or letter == ' ':
            result += letter
        elif letter == '+':
            #result += 'plus'
            result += '_'
        elif letter == '-':
            result += '_'
        elif letter == ',':
            #result += 'comma'
            result += ''
        elif letter == '.':
            #result += 'period'
            result += '_'
        else:
            letter += '_'
    
    while True:
        original = result
        if len(result) > 1 and result[-1] == '_':
            result = result[:-1]
        if len(result) > 1 and result[0] == '_':
            result = result[1:]
        if len(result) == 0:
            return 'unknown'
        result = result.strip()
        if original == result:
            break
    
    return result


def fix_repetition(identifier, existing_ones):
    '''
    Returns an identifier that is not repeated inside existing_ones list,
    it does so by adding a _x index to it
    '''
    candidate = identifier
    counter = 2
    while candidate in existing_ones:
        candidate = identifier + '_%s' % counter
        counter += 1
    
    return candidate


def class_name_from_text(text):
    '''
    Given a string returns a valid python class name that closely resembles
    such string
    '''
    if isinstance(text, unicode):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')

    text = text.title().replace(' ', '')
    # Remove non letter / numbers
    # Check against reserved
    # Check against duplicated
    return letterize(text)


def method_name_from_text(title, names_used):
    '''
    Given a string returns a valid python class name that closely resembles
    such string
    '''
    if isinstance(title, unicode):
        title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')

    title = title.lower().replace(' ', '_')
    # Remove non letter / numbers
    # Check against reserved
    # Check against duplicated
    title = letterize(title)
    candidate = title
    counter = 1
    while candidate in names_used:
        counter += 1
        candidate = title + '_' + str(counter)
    return candidate


class CodeGenerator(object): # pylint: disable=R0903
    '''
    Base code generator template, inherit and customize
    '''    
    def __init__(self):
        self._code = None

    
    def _generate_module_head_comment(self):
        '''
        Add here all the usefull information for the module header comment like
        date & time, version info, generator and so
        '''
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        docstring = 'Automatically generated on %s' % now
        docstring = HEADER_TEMPLATE % {'docstring': docstring}
        self._code.write(docstring)

    
    def _generate_imports(self):
        '''
        Add here all the necessary imports used by the class
        '''
        self._code.write('import something.needed\n')

    
    def _generate_class_declaration(self):
        '''
        Add here all the customization needed for the class declaration
        '''
        self._code.write(CLASS_DECLARATION_TEMPLATE % {'class_name': 'foo'})


    def _generate_class_docstring(self):
        '''
        Add here usefull information about the class, for example the title of
        the window that this class represents, etc
        '''
        docstring = 'Generated for window with title "Region and Language"'
        docstring = CLASS_DOCSTRING_TEMPLATE % {'docstring': docstring}
        self._code.write(docstring)

        
    def _generate_class_init(self):
        '''
        Add here all the initialization needed, for example control id's and
        so.
        '''
        self._code.write(CLASS_INIT_TEMPLATE % {'body': 'pass'})


    def _generate_method_signature(self):
        '''
        Add here customization for the method name and params.
        '''
        self._code.write(METHOD_DECLARATION_TEMPLATE % {'name': 'foo'})
        
    
    def _generate_method_docstring(self):
        '''
        Add here a useful docstring, for example the return type.
        '''
        self._code.write(METHOD_DOCSTRING_TEMPLATE % {'docstring':
                                                     'Automatically generated'})
        
    
    def _generate_method_body(self):
        '''
        Add here the body of the method being generated
        '''
        self._code.write((' ' * 8) + 'pass\n')
    
    
    def _generate_next_method(self):
        '''
        Generate the code for the next method, return True if there are more
        methods to generate, False to indicate that there are no more methods
        to generate
        '''
        self._generate_method_signature()
        self._generate_method_docstring()
        self._generate_method_body()
        return False # When there are no more methods to generate"

    def generate_code(self):
        '''
        Generates the file code and returns a string out of it
        '''
        self._code = StringIO.StringIO()
        self._generate_module_head_comment()
        self._code.write('\n')
        self._generate_imports()
        self._code.write('\n')
        self._generate_class_declaration()
        self._generate_class_docstring()
        self._code.write('\n')
        self._generate_class_init()
        self._code.write('\n\n')
        while self._generate_next_method():
            self._code.write('\n\n')
        
        return self._code.getvalue()

    
def test():
    code_gen = CodeGenerator()
    print code_gen.generate_code()
    
    
if __name__ == '__main__':
    test()