##############################
### IMPORTS ##################
##############################

from strings_with_arrows import *

##############################
### CONSTANTS ################
##############################

DIGITS = '0123456789'

##############################
### ERRORS ###################
##############################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        #creates a string showing error name
        result  = f'{self.error_name}, {self.details}; \n'
        result += f'Locaton: File {self.pos_start.fn}, Line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Illegal Syntax', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)

##############################
### POSITION #################
##############################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.fn = fn # filename
        self.ftxt = ftxt # filetext
        self.idx = idx # index
        self.ln = ln # line
        self.col = col # collum

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n': #make it ',' later
            self.ln += 1
            self.col = 0
        
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

##############################
### TOKENS ###################
##############################

# TT = token type
# EOF = end of file

TT_INT     = 'INT'
TT_FLOAT   = 'FLOAT'
TT_PLUS    = 'PLUS'
TT_MINUS   = 'MINUS'
TT_MUL     = 'MUL'
TT_DIV     = 'DIV'
TT_LPAREN  = 'LPAREN'
TT_RPAREN  = 'RPAREN'
TT_EOF     = 'EOF'

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_ 
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

##############################
### LEXER ####################
##############################

class Lexer:
    def __init__(self, fn, text):
        #reads the lines of text program
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        #moves the line
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        # repeat til end of text
        while self.current_char != None:
            # make sure its not a space or tab or exclude them of the sense, and if it is a space or tab than advance the current_char
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS: 
                # make number            
                tokens.append(self.make_number())
            elif self.current_char == 'p':
                # checks for a input in this case p (+) and inputs said token into token list and then of course advance
                tokens.append(Token(TT_PLUS, pos_start = self.pos))
                self.advance()
            elif self.current_char == 's':
                # s = subtract -
                tokens.append(Token(TT_MINUS, pos_start = self.pos))
                self.advance()
            elif self.current_char == 'm':
                # m = multiply *
                tokens.append(Token(TT_MUL, pos_start = self.pos))
                self.advance()
            elif self.current_char == 'd':
                # d = divide /
                tokens.append(Token(TT_DIV, pos_start = self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start = self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start = self.pos))
                self.advance()
            else:
                # return some error because it's an unknown char
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                # return empty list and IllegalError
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_number(self):
        # if no dots (.) in string integer but if there is it's a float
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            #check and place dot
            if self.current_char == '.':
                # break bec you cant have two dots
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                # must be a num
                num_str += self.current_char
            self.advance()
        
        # check if it is type integer or float and returning the proper token, and of course I convert the "num_str" to its proper form (float int)
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

##############################
### NODES ####################
##############################

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        #set pos start and end
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    # repr returns a printable version of the input
    def __repr__(self):
        return f'{self.tok}'

# binary operators
class BinOpNode:
    # (ex: 6 + 8) takes left node in this case 6, gets the operator token int this case +, and the right node 8 and computes them
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        # set pos start and end
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'   

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        #set pos start and end
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'   

##############################
### PARSE RESULT #############
##############################

class ParseResult:
    # takes output from parser and checks for inpit
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, result):
        if isinstance(result, ParseResult):
            if result.error: self.error = result.error
            return result.node

        return result

    def sucsess(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

##############################
### PARSER ###################
##############################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()
    
    def advance(self):
        self.tok_idx += 1
        # if in range of tok list
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok 


    #################################################
    
    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected operators 'p', 's', 'm' or 'd'"))
        return res

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_MINUS, TT_PLUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.sucsess(UnaryOpNode(tok, factor))

        # checks is float/integer advances and returns number node of the float/integer
        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.sucsess(NumberNode(tok))

        #check for parentheses ()
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.sucsess(expr)
            else: 
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected closing parentheses ')'"))

        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected integer or floating point"))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    #################################################

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.sucsess(left)

##############################
### RUNTIME RESULT ###########
##############################

class RTResult:
    #keeps track of current result or error
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value 

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

##############################
### VALUES ###################
##############################

# for storing and later operation numbers
class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()

    def set_pos(self, pos_start=None, pos_end=None):
        #initialize pos start and end
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value), None

    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value), None

    def multiplyed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value), None

    def divided_by(self, other):
        if isinstance(other, Number):
            # checking for division by 0
            if other.value == 0: 
                return None, RTError(other.pos_start, other.pos_end, 'Division by zero')

            return Number(self.value / other.value), None

    def __repr__(self):
        return str(self.value)

##############################
### CONTEXT ##################
##############################

class Context:
    def __init__(self, display_name, parrent=None, parrent_entry_pos=None):
        self.display_name = display_name
        self.parrent = parrent
        self.parrent_entry_pos = parrent_entry_pos

##############################
### INTERPRETER ##############
##############################

class Interpreter:
    # the interpreter will take the node and execute it ex: input int: 3 plus int: 4 and it will execute 3 + 4
    def visit(self, node):
        #take node and add visit_ to it and call the function ex: node = BinOpNode add visit_ visit_BinOpNode and call that method
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    
    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
         
    #######################################################################

    def visit_NumberNode(self, node):
        # a number node will allways return success because there is no operations happening
        return RTResult().success(
            Number(node.tok.value).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_BinOpNode(self, node):
        #visit child nodes
        res = RTResult()
        left = res.register(self.visit(node.left_node))
        if res.error: return res #error check
        right = res.register(self.visit(node.right_node))
        if res.error: return res

        # error = None ##del

        #find op tok
        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subtracted_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multiplyed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.divided_by(right)

        #check for error
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node):
        #make RTres instanse
        res = RTResult()
        #visit child node
        number = res.register(self.visit(node.node))
        if res.error: return res

        error = None

        #make neg
        if node.op_tok.type == TT_MINUS:
            number, error = number.multiplyed_by(Number(-1))
        
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end)) 

##############################
### RUN ######################
##############################

def run(fn, text):
    # get tokens / toks
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error #check for error

    # generate abstract syntax tree (AST) 
    #         expr          (2 * 7) + 3
    #        / | \
    #     term + term
    #     /|\     |
    #  fac + fac factor
    #   |     |     |
    #   2     7     3
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # run program
    interpreter = Interpreter()
    context = Context('<program>')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
