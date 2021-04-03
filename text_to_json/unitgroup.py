import json
import os
import copy
import math
import re
import time
from text_to_json import common_page, ability
from text_to_json.WikiError import editerror


def get_source_to_data(all_json, version, text_base):
    for i in all_json['单位组']:
        all_json['单位组'][i]['页面名'] = i
        all_json['单位组'][i]['分类'] = '单位组'
        all_units=[]
        for j in all_json['单位组'][i]['成员']:
            members = all_json['单位组'][i]['成员'][j]
            #bt大表格
            bt='<table class="wikitable" style="width:100%;text-align:right;"><tr><td colspan="2" style="text-align:center;">[['\
               +i+']]（'+members['名称']+'）</td></tr><tr><td rowspan="5" style="text-align:center;">'
            st='<table class="wikitable" style="width:100%;text-align:center;"><tr><td>[['\
               +i+']]（'+members['名称']+'）</td></tr><tr><td>'
            #st小表格
            # 成员数量，生命值，金钱，经验，物理生命，魔法生命
            result = {'数量': [[[0], {}]], '生命值': [[[0], {}]], '金钱上限': [[[0], {}]], '金钱下限': [[[0], {}]], '经验': [[[0], {}]], '物理生命': [[[0], {}]], '魔法生命': [[[0], {}]]}
            kk = 0
            while True:
                kk += 1
                k = str(kk)
                if k in members:
                    if members[k]['单位名'] in all_json['非英雄单位']:
                        one_member = all_json['非英雄单位'][members[k]['单位名']]
                        if members[k]['单位名'] not in all_units:
                            all_units.append(members[k]['单位名'])
                        one_result = {}
                        one_result['数量'] = ability.one_combine_txt_numbers(members[k]['数量']['代码'], all_json, text_base, ['单位组', i, '成员', '数量'])
                        bt+='<div style="display:inline-block;padding:0 0.25em;"><div>[[file:'+one_member['图片']+'|x100px|center|link=]]</div><div>[['+one_member['页面名']+']]×'+change_combine_numbers_to_str(one_result['数量'])+'</div></div>'
                        st+='<div>{{H|' + one_member['页面名'] + '}}×'+change_combine_numbers_to_str(one_result['数量'])+'</div>'
                        codes = {'0': '升级属性', '1': '非英雄单位', '2': members[k]['单位名']}
                        for l in ['生命值', '护甲', '魔法抗性', '经验', '金钱上限', '金钱下限']:
                            codes['3'] = l
                            one_result[l] = ability.one_combine_txt_numbers(codes, all_json, text_base, ['单位组', i, '成员', '单位名称'])
                        for l in ['生命值', '经验', '金钱上限', '金钱下限']:
                            one_result[l] = ability.calculate_combine_txt_numbers(one_result[l], one_result['数量'], '*')
                        for l in one_result['护甲']:
                            for k in range(len(l[0])):
                                l[0][k] = 1 - 0.06 * l[0][k] / (1 + 0.06 * abs(l[0][k]))
                        for l in one_result['魔法抗性']:
                            for k in range(len(l[0])):
                                l[0][k] = 1 - l[0][k] / 100
                        one_result['物理生命']=ability.calculate_combine_txt_numbers(one_result['生命值'], one_result['护甲'], '/')
                        one_result['魔法生命']=ability.calculate_combine_txt_numbers(one_result['生命值'], one_result['魔法抗性'], '/')
                        for l in result:
                            result[l]=ability.calculate_combine_txt_numbers(result[l], one_result[l], '+')
                    else:
                        raise (editerror('单位组', i, '在【单位组】【' + i + '】的第' + j + '组第' + k + '个【成员】【' + members[k]['单位名'] + '】没有找到，请检查后修正'))
                else:
                    break
            for k in ['数量']:
                kk=k+'平均'
                result[kk]={}
                for l in ['经验', '金钱上限', '金钱下限']:
                    result[kk][l]=ability.calculate_combine_txt_numbers(result[l], result[k], '/')
            for k in ['生命值','物理生命','魔法生命']:
                kk=k+'平均'
                result[kk]={}
                for l in ['经验', '金钱上限', '金钱下限']:
                    result[kk][l]=ability.calculate_combine_txt_numbers(result[l], result[k], '/')
                    for m in result[kk][l]:
                        for n in range(len(m[0])):
                            m[0][n] = m[0][n] * 1000
            members['总计']={}
            for k in ['经验', '金钱上限', '金钱下限']:
                members['总计'][k]=combine_numbers_back_to_json(result[k])
            for k in ['数量','生命值','物理生命','魔法生命']:
                kk=k+'平均'
                members[k]={k:combine_numbers_back_to_json(result[k])}
                for l in ['经验', '金钱上限', '金钱下限']:
                    members[k][l]=combine_numbers_back_to_json(result[kk][l])
            bt+='</td><td style="background-color:#eeeecc;">总计' \
                '{{H|金钱}}'+change_double_combine_numbers_to_str(result['金钱下限'],result['金钱上限'])\
                +'{{H|经验}}'+change_combine_numbers_to_str(result['经验'])+'</td></tr>'
            st+='</td></tr><tr><td style="background-color:#eeeecc;">{{H|金钱}}'+change_double_combine_numbers_to_str(result['金钱下限'],result['金钱上限'])\
                +'</td></tr><tr><td style="background-color:#eeeecc;">{{H|经验}}'+change_combine_numbers_to_str(result['经验'])+'</td></tr>'
            for k in [['数量','cceeee'],['生命值','cceecc'],['物理生命','eecccc'],['魔法生命','ccccee']]:
                kk=k[0]+'平均'
                bt+='<tr><td style="background-color:#'+k[1]+';">共'+change_combine_numbers_to_str(result[k[0]])
                st+='<tr><td style="background-color:#'+k[1]+';">'+change_combine_numbers_to_str(result[k[0]])
                if k[0]=='数量':
                    bt+='个单位，'
                    st+='个单位'
                else:
                    bt+=k[0]+'，千血'
                    st+=k[0]
                bt+='平均{{H|金钱}}'+change_double_combine_numbers_to_str(result[kk]['金钱下限'],result[kk]['金钱上限'])\
                    +'{{H|经验}}'+change_combine_numbers_to_str(result[kk]['经验'])+'</td></tr>'
                st+='</td></tr>'
            bt+='</table>'
            st += '</table>'
            members['大表格']=bt
            members['小表格']=st
        all_json['单位组'][i]['全部单位']=all_units

def combine_numbers_back_to_json(slist):
    redict={}
    for ii in range(len(slist)):
        i=str(ii+1)
        redict[i]={}
        for jj in range(len(slist[ii][0])):
            j=str(jj+1)
            redict[i][j]=slist[ii][0][jj]
        if len(slist[ii][1])>0:
            redict[i]['升级来源']={}
            kk=0
            for v,w in slist[ii][1].items():
                kk+=1
                k=str(kk)
                redict[i]['升级来源'][k]= {'名称':v,'图片':w}
    return redict

def change_combine_numbers_to_str(slist):
    rere = ''
    rere += ability.combine_numbers_post_level(slist[0][0],round=1)
    if len(slist) > 1:
        rere += "("
        for l in range(1, len(slist)):
            for m in slist[l][1]:
                rere += "[[file:" + slist[l][1][m] + "|x18px|link=" + m + "]]"
            rere += ability.combine_numbers_post_level(slist[l][0],round=1)
        rere += ")"
    return rere

def change_double_combine_numbers_to_str(slist1,slist2,linkop='~'):
    rere = ''
    rere += ability.combine_numbers_post_level(slist1[0][0],round=1)+linkop+ability.combine_numbers_post_level(slist2[0][0],round=1)
    if len(slist1) > 1:
        rere += "("
        for l in range(1, len(slist1)):
            for m in slist1[l][1]:
                rere += "[[file:" + slist1[l][1][m] + "|x18px|link=" + m + "]]"
            rere += ability.combine_numbers_post_level(slist1[l][0],round=1)+linkop+ability.combine_numbers_post_level(slist2[l][0],round=1)
        rere += ")"
    return rere
