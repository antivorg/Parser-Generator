#!/usr/bin/env python3
import sys
import re

class cmd_args:

    validKeys = {
            "--help" : 0,
            "-h" : 0,
            "--bnf" : 0,
            "-b" : 0,
            "--grammar" : 1,
            "-g" : 1
    }

    def __init__(self):
        self.__check_arg_structure()
        self._args = sys.argv

    def __check_arg_structure(self):
        i=1
        while i < len(sys.argv):
            if sys.argv[i][0] != "-" \
                    or not sys.argv[i] in self.validKeys:
                self.print_help()
                sys.exit()
            else:
                j=1
                while j != self.validKeys[sys.argv[i]]+1:
                    if i+j >= len(sys.argv):
                        self.print_help()
                        sys.exit()
                    elif sys.argv[i+j][0] == "-":
                        self.print_help()
                        sys.exit()
                    j += 1
            i += j

    def find(self, name):
        for i in range(0, len(self._args)):
            if self._args[i] == name:
                return i
        return -1

    def read_next_arg(self, name):
        keyInd = self.find(name)
        if len(self._args) < keyInd:
            return -1
        else:
            return self._args[keyInd+1]

    def read_nth_arg(self, index):
        if index >= len(self._args):
            return ""
        else:
            return self._args[index]

    def no_args(self):
        if len(self._args) == 1:
            return True
        else:
            return False

    def print_help(self):
        print("helpful")


class token:

    def __init__(self, char, line):
        if line == -1:
            self._type = "SOF"
        elif char.isspace():
            self._type = "white space"
        elif char == "<":
            self._type = "symbol"
        elif char == ":":
            self._type = "assignment"
        elif char == "|":
            self._type = "choice"
        elif char == "":
            self._type = "EOF"
        #elif char == ";":
        #    self._type = "comment"
        else:
            self._type = "string"
        self._token = char
        self._line = line

    def add_char(self, char):
        self._token += char
        if not (self._token in "::=") and self._type == "assignment":
            self._token = "string"

    def valid_token(self):
        for i in range(0, len(self._token)):
            if self._type == "white space" \
                    and not self._token[i].isspace():
                return False
            elif self._type == "symbol" and self._token[0] != "<":
                return False
            elif self._type == "assignment" \
                    and self._token[i] != "::="[i]:
                return False
            else:
                return True

    def end_of_token(self, char):
        if self._type == "SOF" or self._type == "EOF" or \
                (self._type == "white space" \
                and not char.isspace()) \
                or (self._type == "symbol" \
                and self._token[-1] == ">") \
                or (self._type == "assignment" \
                and self._token[-1] == "=") \
                or (self._type == "choice") \
                or (self._type == "EOF") \
                or (self._type == "comment" \
                and self._token[-1] == "\n") \
                or (self._type == "string" \
                and char.isspace() or char == "<"):
            return True
        else:
            return False

    def type(self):
        return self._type

    def read_token(self):
        return self._token

    def read_line(self):
        return self._line


class lexer:

    def __init__(self, body):
        self._tokens = [token("", -1)]
        i = 0
        line = 0
        while i < len(body):
            if body[i] == "\n":
                line += 1
            if self._tokens[-1].end_of_token(body[i]):
                self._tokens.append(token(body[i], line))
            else:
                self._tokens[-1].add_char(body[i])
            if not self._tokens[-1].valid_token():
                print("Line " + str(line) + "Lexing Error: " \
                        +"\""+self._tokens[-1].read_token()+"\"")
                sys.exit()
            i += 1
        self._tokens.append(token("", line))
        self._iterator = 0

    def fetch_token(self):
        print(self._tokens[self._iterator].read_token()+"\t"\
                +self._tokens[self._iterator].type())
        self._iterator += 1
        return self._tokens[self._iterator-1]

class expression:

    def __init__(self, token):
        if (token.type() != "symbol"):
            print("Line " + str(token.read_line()) \
                    + " Parse Error, expression must begin with " \
                    + "symbol, not: \"" + token.read_token()+"\"")
            sys.exit()
        self._LHS = token
        self._RHS = [[]]

    def add_choice(self):
        self._RHS.append([])

    def add_list(self, ls):
        self._RHS[-1] = ls

    def contains_symbols(self):
        return self.__recursive_contains_symbols(self._RHS)

    def substitute_symbols(self, expr):
        self.__recursive_substitute_symbols(self._RHS, expr)

    def read_LHS(self):
        return self._LHS.read_token()

    def read_RHS(self):
        return self._RHS

    def __recursive_contains_symbols(self, ls):
        for item in ls:
            if type(item) == list:
                does = self.__recursive_contains_symbols(item)
                if does:
                    return True
            elif item.type() == "symbol":
                return True
        return False

    def __recursive_substitute_symbols(self, ls, expr):
        for i in range(0, len(ls)):
            if type(ls[i]) == list:
                self.__recursive_substitute_symbols(ls[i], expr)
            elif expr.get_LHS() == ls[i].read_token():
                ls[i] = expr.read_RHS

class grammar:

    def __init__(self, fileName):
        with open(fileName, "r") as file:
            text = file.read()
        self.__parse_file(text)

    def __parse_file(self, text):
        lex = lexer(text)
        exprs = self.__parse_expressions(lex)
        reducedExprs = self.__reduce_expressions(exprs)

    def __parse_expressions(self, lex):
        token = lex.fetch_token()
        while token.type() == "white space" \
                or token.type() == "comment":
            token = lex.fetch_token()
        parseStack = []
        expr = None
        exprs = []
        while token.type() != "EOF":
            if token.type() == "symbol" \
                    or token.type() == "string":
                parseStack.append(token)
            if token.type() == "choice":
                expr.add_choice()
            if token.type() == "assignment":
                if expr is None:
                    if len(parseStack) == 0 \
                            or len(parseStack) > 1 \
                            or parseStack[0].type() != "symbol":
                        self.__parse_error(token, "Invalid LHS")
                        sys.exit()
                    expr = expression(parseStack[0])
                    parseStack = []
                else:
                    expr.add_list(parseStack[:-1])
                    exprs.append(expr)
                    expr = expression(parseStack[-1])
            token = lex.fetch_token()
            while token.type() == "white space" \
                    or token.type() == "comment":
                token = lex.fetch_token()
        expr.add_list(parseStack)
        exprs.append(expr)
        return exprs

    def __reduce_expressions(self, exprs):
        # root expression assumed to be primary
        root = exprs[0]
        while root.contains_symbols():
            for expr in exprs:
                root.substitute_symbols(expr)

    def __parse_error(self, token, msg):
        print("Line " + str(token.read_line()) + " " \
                + msg + ", not: \"" + token.read_token()+"\"")
        sys.exit()

def main():

    args = cmd_args()

    if args.find("--help") != -1 or args.find("-h") != -1 \
            or args.no_args():
        args.print_help()

    if args.find("--grammar") != -1:
        grammar(args.read_next_arg("--grammar"))
    elif args.find("-g") != -1:
        grammar(args.read_next_arg("-g"))


if __name__ == "__main__":
    main()

