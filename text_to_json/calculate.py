import json
import math
import re


calculate_function={
    '+':lambda x,y:x+y,
    '*':lambda x,y:x*y,
    '-':lambda x,y:x-y,
    '/':lambda x,y:x/y,
    '%':lambda x,y:x%y,
    '^':lambda x,y:pow(x, y),
    '→':lambda x,y:round(x, int(y)),
    '↓':lambda x,y:math.floor(x * pow(10, int(y))) / pow(10, int(y)),
    '↑':lambda x,y:math.ceil(x * pow(10, int(y))) / pow(10, int(y))
}

def analyse_text_with_change_sign_and_calculate(equation,parameter):
    retxt=re.sub(r'【([^【】]*?)】',lambda x: change_sign_to_value_in_equation_sub_function(x.group(1), parameter),equation)
    retxt=re.sub(r'《([^《》]*?)》',lambda x: calculate_result_from_equation_text(x.group(1)),retxt)
    return retxt

def change_sign_to_value_in_equation(equation,parameter):
    return re.sub(r'【(.*?)】',lambda x: change_sign_to_value_in_equation_sub_function(x.group(1), parameter),equation)

def change_sign_to_value_in_equation_sub_function(x,para):
    retxt='0'
    if x in para:
        retxt= str(para[x])
    else:
        try:
            if int(x) in para:
                retxt= str(para[int(x)])
        finally:
            retxt='0'
    return retxt

def calculate_result_from_equation_text(equation):
    retxt=re.sub(r'\s','',equation)
    retxt=split_near_bracket_in_equation_list([retxt])
    retxt=split_number_operate_in_equation_list(retxt)
    retxt=calculate_value_from_equation_list(retxt)
    if float(int(retxt)) == float(retxt):
        retxt = int(retxt)
    else:
        retxt = float(retxt)
    return str(retxt)


def split_near_bracket_in_equation_list(equalist):
    bool=True
    templist=[]
    for i in range(len(equalist)):
        v=equalist[i]
        if isinstance(v,str):
            find=re.search(r'[\(（][^()（）]*?[\)）]',v)
            if find:
                if find.span()[0]!=0:
                    templist.append(v[:find.span()[0]])
                if find.span()[1]>find.span()[0]+2:
                    templist.append([v[find.span()[0]+1:find.span()[1]-1]])
                    if find.span()[1] != len(v):
                        templist.append(v[find.span()[1]:])
                else:
                    templist[-1]+=v[find.span()[1]:]
                bool = False
            else:
                templist.append(v)
        else:
            templist.append(v)
    if bool:
        templist=split_far_bracket_in_equation_list(templist)
    else:
        templist=split_near_bracket_in_equation_list(templist)
    return templist

def split_far_bracket_in_equation_list(equalist):
    left = False
    temp_list = []
    new_list = []
    bool=True
    for i in range(len(equalist)):
        v = equalist[i]
        if isinstance(v, str) and bool:
            find = max(v.rfind(')'),v.rfind('）'))
            if find>=0:
                if find!=0:
                    new_list.append(v[:find])
                if left:
                    if len(new_list)==1 and isinstance(new_list,list) or len(temp_list)==0:
                        temp_list.extend(new_list)
                    else:
                        temp_list.append(new_list)
                else:
                    temp_list=[new_list]
                if find+1!=len(v):
                    temp_list.append(v[find+1:])
                bool=False
            else:
                find=max(v.rfind('('),v.rfind('（'))
                if find>=0:
                    if left:
                        if len(new_list)>0 and isinstance(new_list[0], str):
                            if len(temp_list)>0:
                                temp_list[-1]+=new_list[0]
                            else:
                                temp_list.append(new_list[0])
                            new_list.pop(0)
                        temp_list.extend(new_list)
                    new_list=[]
                    if find != 0:
                        temp_list.append(v[:find])
                    if find+1 != len(v):
                        new_list.append(v[find+1:])
                    left=True
                else:
                    if left:
                        new_list.append(v)
                        if len(new_list) == 1 and isinstance(new_list, list) or len(temp_list) == 0:
                            temp_list.extend(new_list)
                        else:
                            temp_list.append(new_list)
                        bool = False
                    else:
                        temp_list.append(v)
        else:
            if bool:
                new_list.append(v)
            if not left:
                temp_list.append(v)
    if not bool:
        temp_list=split_far_bracket_in_equation_list(temp_list)
    return temp_list

def split_number_operate_in_equation_list(equalist):
    templist=[]
    for i in range(len(equalist)):
        v=equalist[i]
        if isinstance(v, str):
            if v[0]=='-':
                v[0]='0'+v[0]
            temptxt=v
            while len(temptxt)>0:
                find = re.match(r'[.\d]+', temptxt)
                if find:
                    findlen = find.span()[1]
                    templist.append(float(temptxt[:findlen]))
                    temptxt=temptxt[findlen:]
                elif temptxt[0] in calculate_function:
                    templist.append(temptxt[0])
                    temptxt=temptxt[1:]
                else:
                    find=re.match(r'[^.\d'+''.join(calculate_function)+']+',temptxt)
                    if find:
                        templist.append(temptxt[:find.span()[1]])
                        temptxt = temptxt[find.span()[1]:]
                    else:
                        print('啥也不对，真是见了鬼了！')
        else:
            templist.append(split_number_operate_in_equation_list(v))
    return templist

def calculate_value_from_equation_list(equa_list):
    i=0
    while len(equa_list)>2:
        if isinstance(equa_list[0],list):
            equa_list[0]=calculate_value_from_equation_list(equa_list[0])
        if isinstance(equa_list[2],list):
            equa_list[2]=calculate_value_from_equation_list(equa_list[2])
        operate = equa_list[1]
        x = equa_list[0]
        y = equa_list[2]
        equa_list[0]=calculate_function[operate](x,y)
        equa_list.pop(1)
        equa_list.pop(1)
    return equa_list[0]


class YouLiShu:
    def __init__(self,shu=0):
        self.shu=1
        try:
            if float(int(shu)) == float(shu):
                self.shu = int(shu)
            else:
                self.shu = float(shu)
        except ValueError:
            self.shu=1
