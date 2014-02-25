'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Valid python names:

identifier ::=  (letter|"_") (letter | digit | "_")*
letter     ::=  lowercase | uppercase
lowercase  ::=  "a"..."z"
uppercase  ::=  "A"..."Z"
digit      ::=  "0"..."9"
'''
import string, unicodedata, re

RESERVED = ['and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or',
            'with', 'assert', 'else', 'if', 'pass', 'yield', 'break', 'except',
            'import', 'print', 'class', 'exec', 'in', 'raise', 'continue',
            'finally', 'is', 'return', 'def', 'for', 'lambda', 'try']

VALID_CHARS = '_%s%s' % (string.ascii_letters, string.digits) 

FILE = r"^(?:[\w]\:|\\)(\\[a-z_\-\s0-9\(\)\.]+)+\.(?i)(.+)$"
#Not perfect, but works
#FOLDER = r"^(?:[\w]\:|\\)(\\[a-z_\-\s0-9\(\)\.]+)+((\\[a-z_\-\s0-9]+)|\\)$"
FOLDER = r'^([\w]\:|\\)(\\[\w \(\)-]+)+\\?$'
LINK = r'^<a href=".*">(.*)</a>$'

def suggest_identifier(some_text):
    '''
    Returns a valid python name from the given text, it does:
    Remove unicodes
    Replace non valid chars for _
    Changes all __ for _
    Removes _ from beginning and end
    Trims
    Check against reserved words
    Result must be at least 2 chars long, and be of form [a-z_][a-z0-9_]{2,30}
    Checks against data format:
        directory: c:\some_thing
        file: some.thc
        futures:
            url: http://www.here.com
            date:
            time:
            etc
    '''
    if re.match(FOLDER, some_text):
        return "folder"
    if re.match(FILE, some_text):
        return "file"
    a_link = re.match(LINK, some_text)
    if a_link:
        some_text = a_link.groups()[0]
    
    some_text = some_text.strip()

    if isinstance(some_text, unicode):
        some_text = unicodedata.normalize('NFKD', some_text).encode('ascii',
                                                                    'ignore')
    
    suggestion = ''
    for letter in some_text:
        if letter in VALID_CHARS:
            suggestion += letter
        else:
            suggestion += '_'

    while suggestion.find('__') != -1:
        suggestion = suggestion.replace('__', '_')
    while len(suggestion) > 0 and suggestion[0] in ('_', ' '):
        suggestion = suggestion[1:]
    while len(suggestion) > 0 and suggestion[-1] in ('_', ' '):
        suggestion = suggestion[:-1]

    if len(suggestion) < 2:
        suggestion = 'Unknown'
    
    if suggestion[0] in string.digits:
        suggestion = 'n_%s' % suggestion
    
    suggestion = suggestion[:30].lower()
    
    if suggestion in RESERVED:
        suggestion += '0'
        
    return suggestion


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

def guess_combobox(combo_dict):
    '''
    Tries to guess what this combobox is about
    '''
    #FIXME: TODO!
    return 'Language'
    
    