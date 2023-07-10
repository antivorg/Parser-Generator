#!/usr/bin/env python3
import sys

class cmd_args:

    validKeys = {
            "--help" : 0,
            "-h" : 0,
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


class grammar:

    def __init__(self, fileName):
        with open(fileName, "r") as file:
            text = file.read()
        self.__parse_file(text)

    def __parse_file(self, text):
        print("yo")


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

