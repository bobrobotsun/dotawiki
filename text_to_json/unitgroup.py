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
        for j in all_json['单位组'][i]['成员']:
            members = all_json['单位组'][i]['成员'][j]
            # 成员数量，生命值，金钱，经验，物理生命，魔法生命
            result = {'数量': [[[0], {}]], '生命值': [[[0], {}]], '金钱上限': [[[0], {}]], '金钱下限': [[[0], {}]], '经验': [[[0], {}]], '物理生命': [[[0], {}]], '魔法生命': [[[0], {}]]}
            kk = 0
            while True:
                kk += 1
                k = str(kk)
                if k in members:
                    if members[k]['单位名'] in all_json['非英雄单位']:
                        one_member = all_json['非英雄单位'][members[k]['单位名']]
                        one_result = {}
                        one_result['数量'] = ability.one_combine_txt_numbers(members[k]['数量']['代码'], all_json, text_base, ['单位组', i, '成员', '数量'])
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
                for l in ['经验', '金钱上限', '金钱下限']:
                    name=k+'平均'+l
                    result[name]=ability.calculate_combine_txt_numbers(result[l], result[k], '/')
            for k in ['生命值','物理生命','魔法生命']:
                for l in ['经验', '金钱上限', '金钱下限']:
                    name='平均1000'+k+l
                    result[name]=ability.calculate_combine_txt_numbers(result[l], result[k], '/')
                    for m in result[name]:
                        for n in range(len(m[0])):
                            m[0][n] = m[0][n] * 1000
            for k in result:
                rere=''
                rere += ability.combine_numbers_post_level(result[k][0][0])
                if len(result[k]) > 1:
                    rere += "("
                    for l in range(1, len(result[k])):
                        for m in result[k][l][1]:
                            rere += "[[file:" + result[k][l][1][m] + "|x18px|link=" + m + "]]"
                        rere += ability.combine_numbers_post_level(result[k][l][0])
                    rere += ")"
                members[k] = rere