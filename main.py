#pip install pathlib2
from pathlib import Path
import pandas as pd
class CustomGrammerInitializer:
    def __init__(self):
        self.nonteminals="{"
        self.epsilon="{}"
        self.tokenType="("
        self.stringConst='"'
        self.intConst="intConst"
        self.readConst="readConst"
        self.productionTransition="::"
        self.grammerFileName="grammer.txt"
        self.grammerString=""
        self.produtionRulesMapp={}
        self.stringSeparator=" "
        self.produtionRules={}
        self.rightHandSight={}
        #self.produtionRulesCount=[]
        self.ProductionMap={}
    def read_file(self):
        self.grammerString = Path(self.grammerFileName).read_text()

    def MapGrammerRules(self):
        lineNumber=0
        strr=""
        key = ""
        transition = False
        for ch in self.grammerString:
            if ch==":" and transition==False:
                key = strr
                strr=""
                transition=True

            if strr==self.productionTransition:
                strr = ""
            if(ch=="\n"):
                lineNumber = lineNumber + 1
                if key not in self.produtionRules:
                    self.produtionRules[key]=1
                else:
                    self.produtionRules[key] += 1
                ind=self.produtionRules[key]
                arr=strr.split(" ")
                #arr=[a for a in arr if a!="" or a!=" "]
                self.produtionRulesMapp[key+str(ind)]=list(filter(None, arr))
                key=""
                strr=""
                transition = False
                continue
            strr +=ch
class StringParser:
    def __init__(self):
        self.string=""
        self.token_type=[]
        self.lexemes=[]
        self.lines=[]
        self.df=pd.DataFrame(columns=["Token_Type", "Lexeme", "Line_Number", "Position"])
        self.data={}
        self.allData=[]
        self.grammar=CustomGrammerInitializer()
        self.last_production=""
        self.last_string_index=0
        self.track=1
        self.leave=False;
        self.keyword = ["integer","real","begin","var","program","end"]
        self.token_type={"keyword":"keyword","id":"identifier","sym":"sym",}
    def read_string(self,path):
        self.string=Path(path).read_text()
        self.grammar.read_file()
        self.grammar.MapGrammerRules()

        print(self.string)
    def find_item(self,ind,array_val):
        temp_str=""
        while(ind>=0):
            temp_str += array_val[ind]
            ind -=1
        return temp_str[::-1]
    def check_identifer(self,char):
        char_int=ord(char)
        return (char_int>=65 and char_int<=90) or (char_int>=97 and char_int<=122)
    def get_word_of_string(self,last_string_index):
        characters=""
        for i in range(last_string_index,len(self.string)):
            last_string_index=i
            if self.string[i] != " "and self.string[i]!="\n":
                if characters=="" and self.string[i]==";":
                    return (self.string[i], last_string_index+1)
                elif  characters!="" and( self.string[i]==";" or self.string[i]==":") :
                    return (characters, last_string_index)
                else:
                    characters += self.string[i]
            else:
                if characters=="":
                    continue
                else:
                    return (characters,last_string_index+1)


    def string_back_track(self,char):
        flag=True
        while(self.string[self.last_string_index]!=char or flag):
            flag=False
            self.last_string_index -=1
    def parsing(self,line,right,rightHand,leftHand):
        for pos, array_val in enumerate(right):
            if "(" in array_val:
                if self.leave:
                    if self.countRet>0:
                        self.countRet -=1
                        return
                    else:
                        self.leave=False

                ind = array_val.find("(")
                word = self.find_item(ind - 1, array_val)
                input_string, self.last_string_index = self.get_word_of_string(self.last_string_index)
                if word in self.token_type:
                    self.data["Token_Type"] = self.token_type[word]
                    if word == "id":
                        if input_string not in self.keyword:
                            self.data["Lexeme"] = input_string
                        else:
                            last_data=self.allData.pop()
                            if last_data["Lexeme"]==";":
                                self.string_back_track(";")
                                last_data['Lexeme']=""
                            while(last_data["Lexeme"]!=";"):
                                last_data = self.allData.pop()
                            self.allData.append(last_data)

                            self.string_back_track(";")
                            self.last_string_index += 1
                            self.track +=1
                            self.handle_production(self.last_production, 1, rightHand, leftHand)
                            self.track -= 1
                            self.leave=True
                            self.countRet=2
                            continue
                    elif word == "keyword":
                        if input_string in array_val:
                            self.data["Lexeme"] = input_string
                        else:
                            self.track +=1
                            self.last_string_index -=len(input_string)
                            self.handle_production(self.last_production,1,rightHand,leftHand)
                            self.track -=1
                            continue
                    elif word == "sym":
                        if input_string in array_val:
                            self.data["Lexeme"] = input_string
                        else:
                            self.track += 1
                            self.last_string_index -= len(input_string)
                            self.handle_production(self.last_production, 1, rightHand, leftHand)
                            self.track -= 1
                            continue

                self.data["Line_Number"] = line
                self.data["Position"] = pos+1
                #self.df = self.df.append(self.data, ignore_index=True)
                self.allData.append(self.data.copy())
                #print('{self.token_type[word]} {input_string}')
                print(self.data)

            elif "{" in array_val:
                self.last_production = array_val
                self.handle_production(array_val,pos,rightHand,leftHand)
    def handle_production(self,array_val,pos,rightHand,leftHand):
        mappedstr=f'{array_val} {self.track}'
        right=""
        if mappedstr in self.grammar.produtionRulesMapp:
            right = self.grammar.produtionRulesMapp[mappedstr]
        else:
            mappedstr = f'{array_val} {1}'
            right = self.grammar.produtionRulesMapp[mappedstr]
        if pos == 0 and "{" in right[pos] :
            item = right.pop(0)
            right.append(item)
        line = rightHand.index(right) + 1
        #self.track = int(leftHand[line - 1].split(" ")[1])
        self.parsing(line, right, rightHand, leftHand)
    def parse(self):
        leftHand=self.grammar.produtionRulesMapp.keys()
        rightHand=self.grammar.produtionRulesMapp.values()
        for line,right in enumerate(rightHand):
            self.parsing(line+1,right,list(rightHand),list(leftHand))














    #     for char in self.string:
    #         if(char=='\n'):
    #             line +=1
    #         ascii=ord(char)
    #
    #         if self.check_identifier(ascii):
    #             word +=char
    #         else:
    #             if word!="":
    #                 for prod_key in self.grammar.produtionRulesMapp.keys():
    #                     temp_ind=""
    #                     if(expect_identifer):
    #                         temp_ind=word
    #                         word="_"
    #                     if word in prod_key:
    #                         right_hand_side=self.grammar.produtionRulesMapp[prod_key]
    #                         ind=right_hand_side.find(word,last_parse_ind,)
    #                         last_production=word
    #                         last_parse_ind=ind+ len(word)
    #                         #self.lexemes.append(word)
    #                         self.data["Lexeme"]=word
    #                         word=""
    #                         ind -= 1
    #                         word=self.track_starting_string(ind,right_hand_side,word)
    #                     elif last_production in prod_key:
    #                         ind = right_hand_side.find(word, last_parse_ind,)
    #
    #                         last_parse_ind = ind + len(word)
    #                         self.data["Lexeme"] =temp_ind
    #                         word = ""
    #                         ind -= 1
    #                         word=self.track_starting_string(ind, right_hand_side, word)
    #
    #                     #self.token_type.append(word[::-1]) #reversing string
    #                     #self.lines(line+1)
    #                     self.data["Token_Type"]=word[::-1]
    #                     if(self.data["Token_Type"]=="keyword"):
    #                         expect_identifer=True
    #                     self.data["Line_Number"]=line+1
    #                     self.data["Position"]="a"
    #                     self.df.append(self.data,ignore_index=True)
    #                     word=""
    #                     break
    #
    #
    # def check_identifier(self,ascii):
    #     return (ascii >=65 and ascii<=91) or (ascii>=97 and ascii <=122)
    #
    #
    #
    #










a=CustomGrammerInitializer()
a.read_file()
a.MapGrammerRules()
a=StringParser()
a.read_string('string.txt')
a.parse()

