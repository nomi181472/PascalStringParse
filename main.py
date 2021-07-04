from pathlib import Path
import re
import pandas as pd
class LexicalAnalyzer:
    def __init__(self):
        self.keywords=[
            "integer","real","var","true","false", #types
            "program","begin","end","while", "if","else","then","do","until",#blocklevel
             "repeat", "readln", "write", "writeln", "writeln",#functions
            "or","div","mod","and","not","trunc",#operations
        ]
        self.symbols=[
            ";",":",":=","(",")","+","-","/","*"
        ]
        self.operators=[
            "<",">","<>",">=","<=",
        ]
    def read_file(self,filename):
        self.string = Path(filename).read_text()
def checkwordIdentifier(word):
    pattern = "[_a-zA-Z][_a-zA-Z0-9]{0,30}"
    return re.match(pattern, word, )
def checkFloat(word):
    pattern = "([-+]*\d+\.\d+|[-+]*\d+)"
    return re.match(pattern, word, )
def checkInt(word):
    pattern = "[0-9]+"
    return re.fullmatch(pattern, word, )
def update(tokentype,lexeme,lineNumber,position):
    return {"Token Type":tokentype,"Lexeme":lexeme,"Line Number":lineNumber,"Position":position}
def symbolUpdate(id,type):
    return {"Identifier":id,"Type":type}
def stringToList(la):
    word=""
    lexemes=pd.DataFrame(columns=["Token Type", "Lexeme", "Line Number", "Position"])
    symbolTable=pd.DataFrame(columns=["Identifier", "Type"])
    line=1
    pos=-1
    identifers={}
    lastkeyword=""
    lastidentifer=""
    str=la.string
    i=0
    off=True
    try:
        while i<len(str):
            if str[i] in( (la.symbols+[" ","\n"])+la.operators) and str!='"' and off:
                if word in la.keywords:
                    pos += 1
                    lexemes = lexemes.append(update("keyword", word, line, pos), ignore_index=True)
                    if word not in ["var","begin","while","do"]:
                        lastkeyword = word
                    else:
                        lastkeyword = ""
                    word=""
                    #continue
                if str[i] in la.symbols:
                    if checkwordIdentifier(word) and word not in la.keywords:
                        pos += 1
                        lexemes = lexemes.append(update("ID", word, line, pos), ignore_index=True)
                        lastidentifer = word
                        if word  in identifers:
                            lastkeyword=""
                            lastidentifer=""
                    elif word!="" and checkInt(word):
                        pos += 1
                        lexemes = lexemes.append(update("intConst", word, line, pos), ignore_index=True)
                        lastkeyword = "integer"
                    elif word!="" and  checkFloat(word):
                        pos += 1
                        lexemes = lexemes.append(update("realConst", word, line, pos), ignore_index=True)
                        lastkeyword = "real"
                    pos += 1
                    if (str[i] + str[i + 1] in la.symbols):
                        lexemes = lexemes.append(update("symbol", str[i] + str[i + 1], line, pos), ignore_index=True)
                        i += 1
                    else:
                        lexemes = lexemes.append(update("symbol", str[i], line, pos), ignore_index=True)
                    word=""
                if str[i] in la.operators:
                    if checkwordIdentifier(word) and word not in la.keywords:
                        pos += 1
                        lexemes = lexemes.append(update("ID", word, line, pos), ignore_index=True)
                        lastidentifer = word
                        if word  in identifers:
                            lastkeyword=""
                            lastidentifer=""
                    pos +=1
                    if (str[i] + str[i + 1] in la.operators):
                        lexemes = lexemes.append(update("operator", str[i] + str[i + 1], line, pos), ignore_index=True)
                        i += 1
                    else:
                        lexemes = lexemes.append(update("operator", str[i], line, pos), ignore_index=True)
                    word = ""
                if  checkInt(word) and checkwordIdentifier(str[i+1]):
                    pos += 1
                    lexemes = lexemes.append(update("intConst", word, line, pos), ignore_index=True)
                    lastkeyword = "integer"
                    word=""
                if str[i] == "\n":
                    line += 1
                    pos = -1
                    if lastkeyword != "" and lastidentifer!="":
                        symbolTable = symbolTable.append(symbolUpdate(lastidentifer, lastkeyword), ignore_index=True)
                        if lastidentifer not in identifers:
                            identifers[lastidentifer] = lastkeyword
            elif str[i]=='"':
                if off==True:
                    off=False
                    pos += 1
                    lexemes = lexemes.append(update("symbol", str[i], line, pos), ignore_index=True)
                else:
                    pos +=1
                    lexemes = lexemes.append(update("stringCont", word, line, pos), ignore_index=True)
                    off=True
                    lexemes = lexemes.append(update("symbol", str[i], line, pos), ignore_index=True)
                word=""
            else:
                word += str[i]
            i +=1
        pos=0
        lexemes = lexemes.append(update("keyword", word, line, pos), ignore_index=True)
        lexemes = lexemes.append(update("symbol", ".", line, pos+1), ignore_index=True)
        lexemes.to_csv("lexicalAnalyzer.csv")
        symbolTable.to_csv("symbolTable.csv")
    except Exception as e:
        print(f'error at line:{line} location:{pos+1}')
la=LexicalAnalyzer()
la.read_file("string.txt")
stringToList(la)

