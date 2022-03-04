import json
import math
import re

def calculate_value_from_equation(equation):
    revalue=0


def calculate_value_from_equation_list(equa_list):
    i=0
    while len(equa_list)>2:
        if isinstance(equa_list[0],list):
            calculate_value_from_equation_list(equa_list[0])
        if isinstance(equa_list[2],list):
            calculate_value_from_equation_list(equa_list[2])
        operate = equa_list[1]
        x = equa_list[0]
        y = equa_list[2]
        if operate == '+':
            value = x + y
        elif operate == '-':
            value = x - y
        elif operate == '*':
            value = x * y
        elif operate == '/':
            value = x / y
        elif operate == '^':
            value = math.pow(x , y)
        elif operate == '-':
            value = x - y
        elif operate == '-':
            value = x - y


class YouLiShu:
    def __init__(self,mu=0,zi=1):
        self.fenmu=mu
        self.fenzi=zi

    def __repr__(self):
        return self.fenmu/self.fenzi

    def __str__(self):
        if self.fenzi==1:
            return str(self.fenmu)
        else:
            return str(self.fenmu)+'/'+str(self.fenzi)