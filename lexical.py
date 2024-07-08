# TOKENS
# List of token names.
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_STRING = 'STRING'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'
TT_NEWLINE = 'NEWLINE'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_ASSIGN = 'ASSIGN'
TT_SEMICOLON = 'SEMICOLON'
TT_COMMA = 'COMMA'
TT_COLON = 'COLON'
TT_EQUALS = 'EQUALS'
TT_NOTEQUALS = 'NOTEQUALS'
TT_GREATER = 'GREATER'
TT_LESS = 'LESS'
TT_EOF = 'EOF'

# CONSTANTS
DIGITS = '0123456789'
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# KEYWORDS
KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'ELSE',
    'WHILE',
    'FOR',
    'FUNCTION',
    'RETURN',
    'TRUE',
    'FALSE',
]


# ERRORS
class Error:
        def __init__(self, pos_first, pos_end, error_name, details):
                self.pos_first = pos_first
                self.pos_end = pos_end
                self.error_name = error_name
                self.details = details



        def as_string(self):
                result = f'{self.error_name}: {self.details}'
                result += f'File {self.pos_first.file_name}, line {self.pos_first.line_number + 1}'
                return result

        @classmethod
        def ExpectedCharError(cls, start_pos, pos, details):
                return cls(start_pos, pos, 'Expected Character', details)


class IllegalCharError(Error):
        def __init__(self, pos_first, pos_end, details):
                super().__init__(pos_first, pos_end, 'Illegal Character', details)

class Position:
        def __init__(self, index, line_number, column_number, file_name, file_text):
                self.index = index
                self.line_number = line_number
                self.column_number = column_number
                self.file_name = file_name
                self.file_text = file_text

        def advance(self, current_char):
                self.index += 1
                self.column_number += 1

                if current_char == '\n':
                        self.line_number += 1
                        self.column_number += 0

                return self

        def copy(self):
                return Position(self.index, self.line_number, self.column_number, self.file_name, self.file_text)




class Tokens:

    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
            if self.value:
                    return f'{self.type}: {self.value}'
            return f'{self.type}'

######################
# LEXER
######################

class Lexer():
        def __init__(self, file_name, text):
                self.file_name = file_name
                self.text = text
                self.pos = Position(-1, 0, -1, file_name, text)
                self.current_char = None
                self.advance()

        def advance(self):
                self.pos.advance(self.current_char)
                self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

        def make_tokens(self):
                tokens = []

                while self.current_char is not None:
                        # Ignoring the characters such as spaces and tabs
                        if self.current_char in ' \t':
                                self.advance()
                        elif self.current_char == '#':
                                self.skip_comment()
                        elif self.current_char in DIGITS:
                                tokens.append(self.make_number())
                        elif self.current_char in LETTERS:
                                tokens.append(self.make_identifier())
                        elif self.current_char == '"':
                                tokens.append(self.make_string())
                        elif self.current_char in ';\n':
                                tokens.append(Tokens(TT_NEWLINE, pos_start=self.pos))
                        elif self.current_char == '+':
                                tokens.append(Tokens(TT_PLUS, self.current_char))
                                self.advance()
                        elif self.current_char == '-':
                                tokens.append(Tokens(TT_MINUS, self.current_char))
                                self.advance()
                        elif self.current_char == '*':
                                tokens.append(Tokens(TT_MUL, self.current_char))
                                self.advance()
                        elif self.current_char == '/':
                                tokens.append(Tokens(TT_DIV, self.current_char))
                                self.advance()
                        elif self.current_char == '(':
                                tokens.append(Tokens(TT_LPAREN))
                                self.advance()
                        elif self.current_char == ')':
                                tokens.append(Tokens(TT_RPAREN))
                                self.advance()
                        elif self.current_char == '[':
                                tokens.append(Tokens(TT_LSQUARE))
                                self.advance()
                        elif self.current_char == ']':
                                tokens.append(Tokens(TT_RSQUARE))
                                self.advance()
                        elif self.current_char == '^':
                                tokens.append(Tokens(TT_POW))
                                self.advance()
                        elif self.current_char == '!':
                                token, error = self.make_not_equals()
                                if error: return [], error
                                tokens.append(token)
                        elif self.current_char == '=':
                                tokens.append(self.make_equals())
                        elif self.current_char == '<':
                                tokens.append(self.make_less_than())
                        elif self.current_char == '>':
                                tokens.append(self.make_greater_than())
                        else:
                                pos_first = self.pos.copy()
                                char = self.current_char
                                self.advance()
                                return [], IllegalCharError(pos_first, self.pos, "'"+ char + "'")

                tokens.append(Tokens(TT_EOF))
                return tokens, None

        def skip_comment(self):
                while self.current_char is not None and self.current_char != '\n':
                        self.advance()

        def make_number(self):
                num_str = ''
                dot_count = 0

                while self.current_char is not None and self.current_char in DIGITS + '.':
                        if self.current_char == '.':
                                if dot_count == 1:
                                        break
                                dot_count += 1
                                num_str += '.'
                        else:
                                num_str += self.current_char
                        self.advance()

                if dot_count == 0:
                        return Tokens(Tokens(TT_INT), int(num_str))
                else:
                        return Tokens(Tokens(TT_FLOAT), float(num_str))

        def make_identifier(self):
                identifier_str = ''

                while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
                        identifier_str += self.current_char
                        self.advance()

                token_type = TT_KEYWORD if identifier_str in KEYWORDS else TT_IDENTIFIER

                return Tokens(token_type, identifier_str)

        def make_string(self):
                string = ''
                pos_start = self.pos.copy()
                escape_character = False
                self.advance()

                escape_characters = {
                        'n': '\n',
                        't': '\t'
                }

                while self.current_char is not None and (self.current_char != '"' or escape_character):
                        if escape_character:
                                string += escape_characters.get(self.current_char, self.current_char)
                        else:
                                if self.current_char == '\\':
                                        escape_character = True
                                else:
                                        string += self.current_char
                        self.advance()
                        escape_character = False

                self.advance()
                return Tokens(TT_STRING, string, pos_start, self.pos)

        def make_not_equals(self):
                start_pos = self.pos.copy()

                self.advance()

                if self.current_char == '=':
                        self.advance()
                        return Tokens(TT_NOTEQUALS), None
                else:
                        return None, Error.ExpectedCharError(start_pos, self.pos, 'Expected "=" after "!"')

        def make_equals(self):
                self.advance()
                return Tokens(TT_EQUALS)

        def make_less_than(self):
                self.advance()
                return Tokens(TT_LESS)

        def make_greater_than(self):
                self.advance()
                return Tokens(TT_GREATER)


def run(file_name, text):
        lexer = Lexer(file_name, text)
        tokens, error = lexer.make_tokens()

        return tokens, error