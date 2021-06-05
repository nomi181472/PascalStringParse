# pip install pathlib2
from pathlib import Path
import pandas as pd


class CustomGrammerInitializer:
    def __init__(self):
        self.nonteminals = "{"
        self.epsilon = "{}"
        self.tokenType = "("
        self.stringConst = '"'
        self.intConst = "intConst"
        self.readConst = "readConst"
        self.productionTransition = "::"
        self.grammerFileName = "grammer.txt"
        self.grammerString = ""
        self.produtionRulesMapp = {}
        self.produtionRulesMappStr = {}
        self.stringSeparator = " "
        self.produtionRules = {}
        self.rightHandSight = {}
        # self.produtionRulesCount=[]
        self.ProductionMap = {}

    def read_file(self):
        self.grammerString = Path(self.grammerFileName).read_text()

    def MapGrammerRules(self):
        lineNumber = 0
        strr = ""
        key = ""
        transition = False
        for ch in self.grammerString:
            if ch == ":" and transition == False:
                key = strr
                strr = ""
                transition = True

            if strr == self.productionTransition:
                strr = ""
            if (ch == "\n"):
                lineNumber = lineNumber + 1
                if key not in self.produtionRules:
                    self.produtionRules[key] = 1
                else:
                    self.produtionRules[key] += 1
                ind = self.produtionRules[key]
                self.produtionRulesMappStr[key + str(ind)] = strr
                arr = strr.split(" ")
                # arr=[a for a in arr if a!="" or a!=" "]
                self.produtionRulesMapp[key + str(ind)] = list(filter(None, arr))
                key = ""
                strr = ""
                transition = False
                continue
            strr += ch


class StringParser:
    def __init__(self):
        self.string = ""
        self.token_type = []
        self.lexemes = []
        self.lines = []
        self.df = pd.DataFrame(columns=["Token_Type", "Lexeme", "Line_Number", "Position"])
        self.data = {}
        self.allData = []
        self.grammar = CustomGrammerInitializer()
        self.last_production = ""
        self.last_string_index = 0
        self.track = 1
        self.countRet = 0
        self.leave = False
        self.maxIndeices = {}
        self.builtinFunction = ["intConst", "realConst", "stringConst"]
        self.keyword = ["integer", "real", "begin", "var", "program", "end", "while", "do", "then"]
        self.token_type = {"keyword": "keyword", "id": "identifier", "sym": "sym", "intConst": "function",
                           "realConst": "function", "stringConst": "function"}

    def read_string(self, path):
        self.string = Path(path).read_text()
        self.grammar.read_file()
        self.grammar.MapGrammerRules()

        print(self.string)

    def find_item(self, ind, array_val):
        temp_str = ""
        while (ind >= 0):
            temp_str += array_val[ind]
            ind -= 1
        return temp_str[::-1]

    def check_identifer(self, char):
        char_int = ord(char)
        return (char_int >= 65 and char_int <= 90) or (char_int >= 97 and char_int <= 122)

    def get_word_of_string(self, last_string_index):
        characters = ""
        for i in range(last_string_index, len(self.string)):
            last_string_index = i
            if self.string[i] != " " and self.string[i] != "\n":
                if characters == "" and self.string[i] == ";":
                    return (self.string[i], last_string_index + 1)
                elif characters != "" and (self.string[i] == ";" or self.string[i] == ":"):
                    return (characters, last_string_index)
                elif self.string[i] in ["(", ")"]:
                    return (self.string[i], last_string_index + 1)
                else:
                    characters += self.string[i]
            else:
                if characters == "":
                    continue
                else:
                    return (characters, last_string_index + 1)

    def string_back_track(self, char):
        flag = True
        while (self.string[self.last_string_index] != char or flag):
            flag = False
            self.last_string_index -= 1

    def backword(self, leftHandtrack, last_production, input_string, rightHand, leftHand):
        leftHandtrack[last_production] = (leftHandtrack[last_production] % self.maxIndeices[last_production]) + 1
        self.last_string_index -= len(input_string)

        flag = False
        while (self.string[self.last_string_index] not in [" ", ":", ";", '(', ')']):
            flag = True
            self.last_string_index -= 1
        if flag:
            self.last_string_index += 1
        self.handle_production(last_production, 1, rightHand, leftHand, leftHandtrack, last_production)
        if leftHandtrack[last_production] != 1:
            leftHandtrack[last_production] -= 1

    def parsing(self, line, right, rightHand, leftHand, leftHandtrack, last_production=""):

        for pos, array_val in enumerate(right):
            if array_val == "{}":
                return
            if self.leave:
                if self.countRet > 0:
                    self.countRet -= 1
                    if self.countRet != 1:
                        return
                    else:
                        self.countRet -= 1

                else:
                    self.leave = False
            if "(" in array_val:
                ind = array_val.find("(")
                word = self.find_item(ind - 1, array_val)
                input_string, self.last_string_index = self.get_word_of_string(self.last_string_index)
                if word in self.token_type:
                    self.data["Token_Type"] = self.token_type[word]
                    if word == "id":
                        if input_string not in self.keyword and input_string not in [";", ":=", ".", "(", ")"]:
                            self.data["Lexeme"] = input_string
                        else:
                            mappedstr = f'{last_production} {self.maxIndeices[last_production]}'
                            last_data = {"Lexeme": ""}
                            mappedstr2 = f'{last_production} {leftHandtrack[last_production]}'
                            is_terminal_state = self.grammar.produtionRulesMappStr[mappedstr2]
                            if input_string not in ["(", ")"]:
                                self.string_back_track(";")
                            else:
                                self.last_string_index -= (len(input_string) + 1)
                            self.last_string_index += 1
                            if (self.grammar.produtionRulesMappStr[mappedstr] in is_terminal_state):
                                self.leave = True
                                return
                            else:

                                leftHandtrack[last_production] =(leftHandtrack[last_production]%self.maxIndeices[last_production])+1
                                self.handle_production(last_production, 1, rightHand, leftHand, leftHandtrack,
                                                       last_production)
                                if leftHandtrack[last_production]!=1:
                                    leftHandtrack[last_production] -= 1
                                self.leave = True
                                return
                    elif word == "keyword":
                        if input_string in array_val and input_string not in [";", ":=", ".", "(", ")"]:
                            self.data["Lexeme"] = input_string
                        else:
                            self.backword(leftHandtrack, last_production, input_string, rightHand, leftHand)
                            if self.countRet > 2:
                                self.leave = True
                            else:
                                self.leave = False
                            return
                    elif word == "sym":
                        if input_string == "(":
                            input_string = '"("'
                        if input_string in array_val:
                            if input_string == '"("':
                                input_string = '('
                            self.data["Lexeme"] = input_string

                        else:
                            if input_string == '"("':
                                input_string = '('
                            self.backword(leftHandtrack, last_production, input_string, rightHand, leftHand)
                            if self.countRet > 2:
                                self.leave = True
                            else:
                                self.leave = False
                            return
                    elif word in self.builtinFunction:
                        if input_string.isdigit():
                            self.data["Lexeme"] = input_string
                        else:
                            self.backword(leftHandtrack, last_production, input_string, rightHand, leftHand)
                            if self.countRet > 2:
                                self.leave = True
                            else:
                                self.leave = False
                            return

                self.data["Line_Number"] = line
                self.data["Position"] = pos + 1
                # self.df = self.df.append(self.data, ignore_index=True)
                self.allData.append(self.data.copy())
                # print('{self.token_type[word]} {input_string}')
                print(self.data)

            elif "{" in array_val:
                last_production = array_val
                self.handle_production(array_val, pos, rightHand, leftHand, leftHandtrack, last_production)

    def handle_production(self, array_val, pos, rightHand, leftHand, leftHandtrack, last_production):

        mappedstr = f'{array_val} {leftHandtrack[array_val]}'
        right = ""

        if mappedstr in self.grammar.produtionRulesMapp:
            right = self.grammar.produtionRulesMapp[mappedstr]
        else:
            leftHandtrack[array_val] = 1
            mappedstr = f'{array_val} {1}'
            right = self.grammar.produtionRulesMapp[mappedstr]
        if pos == 0 and "{" in right[pos]:
            item = right.pop(0)
            right.append(item)
            self.countRet += 1
        line = rightHand.index(right) + 1
        # self.track = int(leftHand[line - 1].split(" ")[1])
        self.parsing(line, right, rightHand, leftHand, leftHandtrack, last_production)

    def parse(self):
        leftHand = self.grammar.produtionRulesMapp.keys()
        rightHand = self.grammar.produtionRulesMapp.values()
        leftHandtrack = {}

        for left in list(leftHand):
            l = left.split(" ")
            leftHandtrack[l[0]] = 1
            self.maxIndeices[l[0]] = int(l[1])

        for line, right in enumerate(rightHand):
            self.parsing(line + 1, right, list(rightHand), list(leftHand), leftHandtrack)


a = CustomGrammerInitializer()
a.read_file()
a.MapGrammerRules()
a = StringParser()
a.read_string('string.txt')
a.parse()
