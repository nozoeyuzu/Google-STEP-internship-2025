#! /usr/bin/python3

def read_number(line, index):
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10
            index += 1
    token = {'type': 'NUMBER', 'number': number}
    return token, index


def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1


def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1

def read_multiply(line, index):
    token = {'type': 'MULTIPLY'}
    return token, index + 1

def read_divide(line, index):
    token = {'type': 'DIVIDE'}
    return token, index + 1

def read_left_parenthesis(line, index):
    token = {'type': 'LEFT_PARENTHESIS'}
    return token, index + 1

def read_right_parenthesis(line, index):
    token = {'type': 'RIGHT_PARENTHESIS'}
    return token, index + 1

def tokenize(line):
    tokens = []
    index = 0
    while index < len(line):
        if line[index].isdigit():
            (token, index) = read_number(line, index)
        elif line[index] == '+':
            (token, index) = read_plus(line, index)
        elif line[index] == '-':
            (token, index) = read_minus(line, index)
        elif line[index] == '*':
            (token, index) = read_multiply(line, index) 
        elif line[index] == '/':
            (token, index) = read_divide(line, index)
        elif line[index] == '(':
            (token, index) = read_left_parenthesis(line, index)
        elif line[index] == ')':
            (token, index) = read_right_parenthesis(line, index)
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens

def evaluate_parenthesis(tokens, index):
    new_tokens = []
    while index < len(tokens):
        token = tokens[index]
        if token['type'] == 'LEFT_PARENTHESIS':
            value, index = evaluate_parenthesis(tokens, index + 1)
            new_tokens.append({'type': 'NUMBER', 'number': value})
            continue
        elif token['type'] == 'RIGHT_PARENTHESIS':
            simplified_tokens = evaluate_multiply_divide(new_tokens)
            result = evaluate_plus_minus(simplified_tokens)
            return result, index + 1
        else:
            new_tokens.append(token)
        index += 1
    simplified_tokens = evaluate_multiply_divide(new_tokens)
    result = evaluate_plus_minus(simplified_tokens)
    return result, index

def evaluate_multiply_divide(tokens):
    new_tokens = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token['type'] == 'NUMBER':
            number = token['number']
            while index + 1 < len(tokens) and (tokens[index + 1]['type'] == 'MULTIPLY' or tokens[index + 1]['type'] == 'DIVIDE'):
                operater = tokens[index + 1]['type']
                next_number = tokens[index + 2]['number']
                if operater == 'MULTIPLY':
                    number *= next_number   
                elif operater == 'DIVIDE':
                    if next_number == 0:
                        print('Division by zero is not allowed.')
                        exit(1)
                    number /= next_number
                index += 2
            new_tokens.append({'type': 'NUMBER', 'number': number})
            index += 1
        else:
            new_tokens.append(token)
            index += 1
    return new_tokens

def evaluate_plus_minus(tokens):
    answer = 0
    tokens.insert(0, {'type': 'PLUS'}) # Insert a dummy '+' token
    index = 1
    while index < len(tokens):
        if tokens[index]['type'] == 'NUMBER':
            if tokens[index - 1]['type'] == 'PLUS':
                answer += tokens[index]['number']
            elif tokens[index - 1]['type'] == 'MINUS':
                answer -= tokens[index]['number']
            else:
                print('Invalid syntax')
                exit(1)
        index += 1
    return answer


def test(line):
    tokens = tokenize(line)
    actual_answer, _ = evaluate_parenthesis(tokens, 0)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print("PASS! (%s = %f)" % (line, expected_answer))
    else:
        print("FAIL! (%s should be %f but was %f)" % (line, expected_answer, actual_answer))


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1.0+2.1-3")
    test("1+2*3")
    test("1+2/3")
    test("1+2*3/4")
    test("1+2*2*2*2")
    test("27/3/3")
    test("(3.0+4*(2-1))/5")
    test("(7+8)*2")
    test("1+(2+(3+4)*5)+6")
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer, _ = evaluate_parenthesis(tokens, 0)
    print("answer = %f\n" % answer)