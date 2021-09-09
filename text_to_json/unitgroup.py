import json
import os
import copy
import math
import re
import time
from text_to_json import common_page, ability
from text_to_json.WikiError import editerror


def get_source_to_data(all_json, version, text_base,name_base):
    for i in all_json['单位组']:
        all_json['单位组'][i]['页面名'] = i
        all_json['单位组'][i]['分类'] = '单位组'
        all_units=[]
        for j in all_json['单位组'][i]['成员']:
            members = all_json['单位组'][i]['成员'][j]
            if '额外属性' not in members:
                members['额外属性']={}
            if '大表格' in members:
                members.pop('大表格')
            if '小表格' in members:
                members.pop('小表格')
            extra_attribute=confirm_extra_attribute(members['额外属性'],all_json,i,j)
            #bt大表格
            bt='<table class="wikitable" style="width:100%;text-align:right;"><tr><td colspan="2" style="text-align:center;"><span class="dota_create_link_to_wiki_page">'\
               +i+'</span>（'+members['名称']+'）</td></tr><tr><td rowspan="5" style="text-align:center;">'
            st='<table class="wikitable" style="width:100%;text-align:center;"><tr><td><span class="dota_create_link_to_wiki_page">'\
               +i+'</span>（'+members['名称']+'）</td></tr><tr><td>'
            #st小表格
            # 成员数量，生命值，金钱，经验，物理生命，魔法生命
            result = {'数量': [[[0], {}]], '生命值': [[[0], {}]], '金钱上限': [[[0], {}]], '金钱下限': [[[0], {}]], '平均金钱': [[[0], {}]], '经验': [[[0], {}]], '物理生命': [[[0], {}]], '魔法生命': [[[0], {}]]}
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
                        bt+='<div style="display:inline-block;padding:0 0.25em;"><div>{{图片|'+one_member['图片']+'|h100|link='+one_member['页面名']+'|center}}</div><div><span class="dota_create_link_to_wiki_page">'\
                            +one_member['页面名']+'</span>×'+change_combine_numbers_to_str(one_result['数量'])+'</div></div>'
                        st+='<div>{{H|' + one_member['页面名'] + '}}×'+change_combine_numbers_to_str(one_result['数量'])+'</div>'
                        codes = {'0': '升级属性', '1': '非英雄单位', '2': members[k]['单位名']}
                        for l in ['生命值', '护甲', '魔法抗性', '经验', '金钱上限', '金钱下限']:
                            codes['3'] = l
                            one_result[l] = ability.one_combine_txt_numbers(codes, all_json, text_base, ['单位组', i, '成员', '单位名称'])
                        codes['3'] = '金钱上限'
                        one_result['平均金钱']=ability.one_combine_txt_numbers(codes, all_json, text_base, ['单位组', '金钱上限', '成员', '单位名称'])
                        one_result['平均金钱'] = ability.calculate_combine_txt_numbers(one_result['平均金钱'], one_result['金钱下限'], '+')
                        for l in one_result['平均金钱']:
                            for m in range(len(l[0])):
                                l[0][m] = l[0][m] / 2
                        one_result=apply_extra_attribute(one_result,extra_attribute,members[k]['单位名'])
                        for l in ['生命值', '经验', '金钱上限', '金钱下限', '平均金钱']:
                            one_result[l] = ability.calculate_combine_txt_numbers(one_result[l], one_result['数量'], '*')
                        for l in one_result['护甲']:
                            for m in range(len(l[0])):
                                l[0][m] = 1 - 0.06 * l[0][m] / (1 + 0.06 * abs(l[0][m]))
                        for l in one_result['魔法抗性']:
                            for m in range(len(l[0])):
                                l[0][m] = 1 - l[0][m] / 100
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
                for l in ['经验', '金钱上限', '金钱下限', '平均金钱']:
                    result[kk][l]=ability.calculate_combine_txt_numbers(result[l], result[k], '/')
            for k in ['生命值','物理生命','魔法生命']:
                kk=k+'平均'
                result[kk]={}
                for l in ['经验', '金钱上限', '金钱下限', '平均金钱']:
                    result[kk][l]=ability.calculate_combine_txt_numbers(result[l], result[k], '/')
                    for m in result[kk][l]:
                        for n in range(len(m[0])):
                            m[0][n] = m[0][n] * 1000
            members['总计']={}
            for k in ['经验', '金钱上限', '金钱下限', '平均金钱']:
                members['总计'][k]=combine_numbers_back_to_json(result[k])
            for k in ['数量','生命值','物理生命','魔法生命']:
                kk=k+'平均'
                members[k]={k:combine_numbers_back_to_json(result[k])}
                for l in ['经验', '金钱上限', '金钱下限', '平均金钱']:
                    members[k][l]=combine_numbers_back_to_json(result[kk][l])
            bt+='</td><td style="background-color:#eeeecc;">总计' \
                '{{H|金钱}}'+change_combine_numbers_to_str(result['平均金钱'])+'('+change_double_combine_numbers_to_str(result['金钱下限'],result['金钱上限'])+')'\
                +'{{H|经验}}'+change_combine_numbers_to_str(result['经验'])+'</td></tr>'
            st+='</td></tr><tr><td style="background-color:#eeeecc;">{{H|金钱}}'+change_combine_numbers_to_str(result['平均金钱'])\
                +'('+change_double_combine_numbers_to_str(result['金钱下限'],result['金钱上限'])+')'\
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
                bt+='平均{{H|金钱}}'+change_combine_numbers_to_str(result[kk]['平均金钱'])\
                    +'('+change_double_combine_numbers_to_str(result[kk]['金钱下限'],result[kk]['金钱上限'])+')'\
                    +'{{H|经验}}'+change_combine_numbers_to_str(result[kk]['经验'])+'</td></tr>'
                st+='</td></tr>'
            bt+='</table>'
            st += '</table>'
            members['简易展示'] = st
            members['具体展示'] = bt
        all_json['单位组'][i]['曾用名'] = []
        if i in name_base:
            for namej in name_base[i]:
                if namej != i:
                    all_json['单位组'][i]['曾用名'].append(namej)
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
                rere += '{{图片|' + slist[l][1][m] + '|h18|link='+m+'}}'
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
                rere += '{{图片|' + slist1[l][1][m] + '|h18|link='+m+'}}'
            rere += ability.combine_numbers_post_level(slist1[l][0],round=1)+linkop+ability.combine_numbers_post_level(slist2[l][0],round=1)
        rere += ")"
    return rere

def confirm_extra_attribute(jsons,all_json,name,index):
    relist=[]
    for i in jsons:
        v=jsons[i]
        if v['属性']!='':
            one_dict = {}
            one_dict['属性'] = v['属性']
            one_dict['目标'] = []
            for j, w in v['目标']:
                one_dict['目标'].append(w)
            tempcode = v['代码']
            tempcode['0'] = '升级属性' if tempcode['0'] == '' else tempcode['0']
            tempcode['1'] = '技能' if tempcode['1'] == '' else tempcode['1']
            one_dict['值'] = ability.one_combine_txt_numbers(tempcode, all_json, {}, ['单位组', name, '成员', index, '额外属性', i])
            relist.append(one_dict)
    return relist


def apply_extra_attribute(result,extra,name):
    for i in extra:
        if len(i['目标'])==0 or name in i['目标']:
            if i['属性']=='加百分比生命':
                result['生命值'] = ability.calculate_combine_txt_numbers(result['生命值'], i['值'], '%+')
            elif i['属性']=='加护甲':
                result['护甲'] = ability.calculate_combine_txt_numbers(result['护甲'], i['值'], '+')
            elif i['属性']=='加魔抗':
                result['魔法抗性'] = ability.calculate_combine_txt_numbers(result['魔法抗性'], i['值'], '%*%')
    return result
