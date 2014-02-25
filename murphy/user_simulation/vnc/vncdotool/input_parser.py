'''
Tokenizes input to be simulated:

    {}
    
'''


def tokenize(text):
    pointer = 0
    while pointer < len(text):
        letter = text[pointer]
        if letter == '{':
            pointer += 1
            token = ''
            while True:
                if pointer == len(text):
                    raise ValueError("Unbalanced bracket in: %s" % text)
                elif text[pointer] == '}' and len(token) > 0:
                    yield token
                    break
                token += text[pointer]
                pointer += 1
        elif letter == '}':
            raise ValueError("Unbalanced closing bracket in: %s" % text)
        else:
            yield letter
        pointer += 1
        
        
if __name__ == '__main__':
    input = "abc{def}ghi"
    print str(list(tokenize(input)))
    
    input = "abc{d}"
    print str(list(tokenize(input)))
    
    input = "{de}fg"
    print str(list(tokenize(input)))
    
    input = "{hij}"
    print str(list(tokenize(input)))

    input = "{{}{enter}{}}"
    print str(list(tokenize(input)))

    try:
        input = "{}"
        list(tokenize(input))
        raise Exception("Failed parsing invalid string %s" % input)
    except ValueError:
        pass

    try:
        input = "}"
        list(tokenize(input))
        raise Exception("Failed parsing invalid string %s" % input)
    except ValueError:
        pass

    try:
        input = "{}}}"
        list(tokenize(input))
        raise Exception("Failed parsing invalid string %s" % input)
    except ValueError:
        pass
        
        