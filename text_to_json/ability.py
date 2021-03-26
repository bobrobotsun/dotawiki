import json
import os
import copy
import math
import hashlib
import re
import time
from text_to_json import common_page, edit_json
from text_to_json.WikiError import editerror
from xpinyin import Pinyin


def change_str_to_int(s):
    rere = 0
    try:
        if float(int(s)) == float(s):
            rere = int(s)
        else:
            rere = float(s)
    except ValueError:
        rere = str(s)
    finally:
        return rere


def change_str_to_float(s):
    rere = 0
    try:
        rere = float(s)
    except ValueError:
        rere = str(s)
    finally:
        return rere


def dict_to_list_first_1(dic):
    rere = []
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in dic:
            rere.append(dic[i])
        else:
            break
    return rere


# 将数字转化为文字，取消小数点和无用末尾0
def better_float_to_text(x,rounds=4):
    if isinstance(x, float):
        if int(x) == x:
            return str(int(x))
        else:
            return str(round(x,rounds))
    else:
        return str(x)


def get_dota_data_from_vpk(base_txt, ffile):
    this_string = ffile.read().decode('utf8')
    alltext = re.finditer('"DOTA_Tooltip_ability_(.*?)_Lore".*?"(.*?)"', this_string)
    for i in alltext:
        name = i.group(1)
        if name in base_txt:
            base_txt[name]['lore'] = {'1': i.group(2)}


def get_hero_data_from_txt(base_txt, address):
    this_file = open(address, mode="r")
    this_string = this_file.read()
    alltext = re.finditer('"(.*?)".*?\n\t\{(.|\n)*?\n\t\}', this_string)
    for i in alltext:
        name = i.group(1)
        base_txt[name] = {}
        all_pro = re.finditer('\t*?"(.*?)".*?"(.+?)"', i.group(0))
        for j in all_pro:
            temp_name = j.group(1)
            temp_value = j.group(2)
            base_txt[name][temp_name] = {}
            if temp_value.find('|') == -1:
                temp_list = temp_value.split(' ')
            else:
                temp_list = temp_value.split('|')
            for k in range(len(temp_list)):
                temp_valuek = temp_list[k].strip()
                try:
                    base_txt[name][temp_name][str(k + 1)] = int(temp_valuek)
                except ValueError:
                    try:
                        base_txt[name][temp_name][str(k + 1)] = float(temp_valuek)
                    except ValueError:
                        base_txt[name][temp_name][str(k + 1)] = temp_valuek


def autoget_talent_source(all_json, base):
    retxt = ''
    for i in all_json['技能']:
        bool = True
        if all_json['技能'][i]['次级分类'] == '天赋技能':
            this_source = cal_ability_source_index(all_json, base, i)
            for j in all_json['技能源']:
                if all_json['技能源'][j]['代码'] == this_source:
                    bool = False
                    all_json['技能'][i]['数据来源'] = all_json['技能源'][j]['页面名']
                    break
            if bool:
                retxt += '\n《' + i + '》并没有读取到合理技能源，请查询后添加。'
    return retxt


def cal_ability_source_index(json, base, i):
    arr = {'10级左天赋': -7, '10级右天赋': -8, '15级左天赋': -5, '15级右天赋': -6, '20级左天赋': -3, '20级右天赋': -4, '25级左天赋': -1,
           '25级右天赋': -2}
    return base[json['英雄'][i[:-6]]['代码名']]['ability'][arr[i[-6:]]]


def fulfill_vpk_data(json, base):
    for i in json['技能源']:
        if json['技能源'][i]['代码'] in base['技能'] and 'lore' in base['技能'][json['技能源'][i]['代码']]:
            json['技能源'][i]['传说'] = base['技能'][json['技能源'][i]['代码']]['lore']['1']


def loop_check_source_to_change_content(json):
    for i in json:
        if isinstance(json[i], dict):
            if "混合文字" in json[i]:
                for j in json[i]['混合文字']:
                    if isinstance(json[i]['混合文字'][j], dict) and '类型' not in json[i]['混合文字'][j]:
                        temp = {'类型': ''}
                        temp.update(json[i]['混合文字'][j])
                        json[i]['混合文字'][j] = copy.deepcopy(temp)
            else:
                loop_check_source_to_change_content(json[i])


# 应用：0、因改版而被删除；1、正在使用；2、因为拥有者删除而被删除
def get_source_to_data(all_json, upgrade_json, version, name_base):
    for i in all_json['技能源']:
        all_json['技能源'][i]['页面名'] = i
        all_json['技能源'][i]['分类'] = '技能源'
        if '升级' in all_json['技能源'][i]:
            if 'A杖' in all_json['技能源'][i]['升级']:
                all_json['技能源'][i]['升级']['神杖'] = copy.deepcopy(all_json['技能源'][i]['升级']['A杖'])
                all_json['技能源'][i]['升级'].pop('A杖')
            if '混合' in all_json['技能源'][i]['升级']:
                all_json['技能源'][i]['升级'].pop('混合')
            if '魔晶' not in all_json['技能源'][i]['升级']:
                all_json['技能源'][i]['升级']['魔晶'] = ''
            if '神杖' not in all_json['技能源'][i]['升级']:
                all_json['技能源'][i]['升级']['神杖'] = ''
        # loop_check_source_to_change_content(all_json['技能源'][i])
    # alllogs=[]
    for ijk in all_json['技能']:
        unit_dic = all_json['技能'][ijk]
        # if unit_dic["次级分类"] not in alllogs:
        #     alllogs.append(unit_dic["次级分类"])
        #     print(ijk,alllogs)
        if 'A杖信息' in unit_dic:
            unit_dic.pop('A杖信息')
        unit_dic['页面名'] = ijk
        unit_dic["分类"] = "技能"
        unit_dic["版本"] = version
        unit_dic['曾用名'] = []
        if unit_dic["次级分类"] == 'a杖技能' or unit_dic["次级分类"] == 'A杖技能':
            unit_dic["次级分类"] = '神杖技能'
        elif unit_dic["次级分类"] == '非英雄单位' or unit_dic["次级分类"] == '非英雄技能':
            unit_dic["次级分类"] = '非英雄单位技能'
        elif unit_dic["次级分类"] == '':
            raise (editerror('技能', ijk, '没有在【技能】中搜索到【次级分类】内容，请检查后及时输入'))
        if '升级属性' in unit_dic:
            unit_dic.pop('升级属性')
        if ijk in name_base:
            for namej in name_base[ijk]:
                if namej != ijk:
                    unit_dic['曾用名'].append(namej)
        if unit_dic["技能排序"] == "":
            if unit_dic["默认按键"] == "Q":
                unit_dic["技能排序"] = "d"
            elif unit_dic["默认按键"] == "W":
                unit_dic["技能排序"] = "e"
            elif unit_dic["默认按键"] == "E":
                unit_dic["技能排序"] = "f"
            elif unit_dic["默认按键"] == "D":
                unit_dic["技能排序"] = "g"
            elif unit_dic["默认按键"] == "F":
                unit_dic["技能排序"] = "h"
            elif unit_dic["默认按键"] == "R":
                unit_dic["技能排序"] = "i"
            elif unit_dic["默认按键"] == "T":
                unit_dic["技能排序"] = "j"
            else:
                unit_dic["技能排序"] = "z"
        if unit_dic["数据来源"] in all_json['技能源']:
            temp1 = all_json['技能源'][unit_dic["数据来源"]]
            if unit_dic["次级分类"] == "天赋技能":
                unit_dic["图片"] = all_json["英雄"][unit_dic["技能归属"]]["图片"]
                unit_dic["迷你图片"] = 'Talent.png'
            elif unit_dic["次级分类"] == "物品技能":
                if unit_dic["技能归属"] in all_json["物品"]:
                    unit_dic["图片"] = all_json["物品"][unit_dic["技能归属"]]["图片"]
                    unit_dic["迷你图片"] = all_json["物品"][unit_dic["技能归属"]]["迷你图片"]
                else:
                    unit_dic["图片"] = "Items_" + temp1["代码"] + ".png"
                    unit_dic["迷你图片"] = "Items_" + temp1["代码"] + ".png"
            else:
                unit_dic["图片"] = "Spellicons_" + temp1["代码"] + ".png"
                unit_dic["迷你图片"] = "Spellicons_" + temp1["代码"] + ".png"
            for i in temp1:
                if i in ability_trait_level[0]:
                    unit_dic[i] = temp1[i]
                elif i in ability_trait_level[1]:
                    unit_dic[i] = {}
                    j = 0
                    while True:
                        j += 1
                        if str(j) in temp1[i]:
                            unit_dic[i][str(j)] = group_source(temp1[i][str(j)])
                        else:
                            break
                elif i in ability_trait_level[2]:
                    unit_dic[i] = {}
                    j = 0
                    while True:
                        j += 1
                        if str(j) in temp1[i]:
                            unit_dic[i][str(j)] = {}
                            k = 0
                            while True:
                                k += 1
                                if str(k) in temp1[i][str(j)]:
                                    unit_dic[i][str(j)][str(k)] = group_source(temp1[i][str(j)][str(k)])
                                else:
                                    break
                            if '名称' in temp1[i][str(j)]:
                                unit_dic[i][str(j)]['名称'] = temp1[i][str(j)]['名称']
                        else:
                            break
                elif i in ability_trait_level[3]:
                    unit_dic[i] = {}
                    if '代码' in temp1[i]:
                        temp1[i] = {'1': temp1[i]}
                    for j in temp1[i]:
                        unit_dic[i][j] = group_source(temp1[i][j])
                elif i == "升级":
                    if ("神杖" in temp1[i] and len(temp1[i]["神杖"]) > 0 or "技能" in temp1[i] and len(
                            temp1[i]["技能"]) > 0 or "魔晶" in temp1[i] and len(temp1[i]["魔晶"]) > 0) and unit_dic['应用'] == 1:
                        upgrade_json[unit_dic["页面名"]] = copy.deepcopy(temp1[i])
                elif i == "页面名" or i == '应用' or i == '分类':
                    continue
                else:
                    unit_dic[i] = group_source(temp1[i])
            unit_dic["技能升级信息"] = {}
        else:
            raise (editerror('技能', ijk, '没有在【技能源】中搜索到' + unit_dic["数据来源"]))


def group_source(a):
    temp = {"1": {}}
    for i in a:
        if i == "名称" or i == "后缀":
            temp[i] = a[i]
        else:
            temp["1"][i] = a[i]
    return temp


def input_upgrade(all_json, upgrade_json):
    for upname in ['神杖', '魔晶', '技能']:
        for i in upgrade_json:
            for j in upgrade_json[i][upname]:
                if upgrade_json[i][upname][j]["目标"]["1"] == "":
                    upgrade_json[i][upname][j]["目标"]["1"] = "技能"
                if upgrade_json[i][upname][j]["目标"]["2"] == "":
                    upgrade_json[i][upname][j]["目标"]["2"] = i
                if "代码" in upgrade_json[i][upname][j]["值"] and isinstance(upgrade_json[i][upname][j]["值"]["代码"], dict):
                    if "1" in upgrade_json[i][upname][j]["值"]["代码"] and upgrade_json[i][upname][j]["值"]["代码"]["1"] == "":
                        upgrade_json[i][upname][j]["值"]["代码"]["1"] = "技能"
                    if "2" in upgrade_json[i][upname][j]["值"]["代码"] and upgrade_json[i][upname][j]["值"]["代码"]["2"] == "":
                        upgrade_json[i][upname][j]["值"]["代码"]["2"] = all_json["技能"][i]["代码"]
                k = 1
                temp = all_json[upgrade_json[i][upname][j]["目标"]["1"]]
                while True:
                    k += 1
                    if str(k) in upgrade_json[i][upname][j]["目标"]:
                        if upgrade_json[i][upname][j]["目标"][str(k)] in temp:
                            temp = temp[upgrade_json[i][upname][j]["目标"][str(k)]]
                        else:
                            temp[upgrade_json[i][upname][j]["目标"][str(k)]] = {}
                            temp = temp[upgrade_json[i][upname][j]["目标"][str(k)]]
                    else:
                        break
                upcount = 2
                while True:
                    if str(upcount) in temp:
                        upcount += 1
                    else:
                        break
                upstr = str(upcount)
                if "0" in upgrade_json[i][upname][j]["目标"] and upgrade_json[i][upname][j]["目标"]["0"] == "替换":
                    temp[upstr] = copy.deepcopy(temp["1"])
                    for k in upgrade_json[i][upname][j]["值"]:
                        temp[upstr][k] = copy.deepcopy(upgrade_json[i][upname][j]["值"][k])
                else:
                    temp[upstr] = upgrade_json[i][upname][j]["值"]
                if upname == '神杖':
                    temp[upstr]["升级来源"] = {"1": {"名称": '阿哈利姆神杖', '图片': 'agha.png'}}
                elif upname == '魔晶':
                    temp[upstr]["升级来源"] = {"1": {"名称": '阿哈利姆魔晶', '图片': 'shard.png'}}
                elif upname == '技能':
                    temp[upstr]["升级来源"] = {"1": {"名称": i, '图片': all_json['技能'][i]['迷你图片']}}
    for i in all_json["技能"]:
        for j in all_json["技能"][i]["效果"]:
            kk = 2
            while True:
                k = str(kk)
                kk += 1
                if k in all_json["技能"][i]["效果"][j]:
                    if '名称' in all_json["技能"][i]["效果"][j][k]:
                        all_json["技能"][i]["效果"][j]['名称'] = all_json["技能"][i]["效果"][j][k]['名称']
                        all_json["技能"][i]["效果"][j][k].pop('名称')
                    l = 0
                    while True:
                        l += 1
                        if str(l) in all_json["技能"][i]["效果"][j][k] and all_json["技能"][i]["效果"][j][k][str(l)] == '删除':
                            m = l
                            while True:
                                m = m + 1
                                if str(m) in all_json["技能"][i]["效果"][j][k]:
                                    all_json["技能"][i]["效果"][j][k][str(m - 1)] = copy.deepcopy(all_json["技能"][i]["效果"][j][k][str(m)])
                                else:
                                    all_json["技能"][i]["效果"][j][k].pop(str(m - 1))
                                    l -= 1
                                    break
                        else:
                            break
                    m = 0
                    l -= 1
                    while True:
                        m += 1
                        l += 1
                        if "+" + str(m) in all_json["技能"][i]["效果"][j][k]:
                            all_json["技能"][i]["效果"][j][k][str(l)] = copy.deepcopy(all_json["技能"][i]["效果"][j][k]["+" + str(m)])
                            all_json["技能"][i]["效果"][j][k].pop("+" + str(m))
                        else:
                            break
                else:
                    break


def complete_upgrade(all_json, base_txt):
    for i in all_json:
        if all_json[i]['应用'] > 0:
            for j in all_json[i]["属性"]:
                if fulfil(all_json[i]["属性"][j], all_json[i]):
                    one_upgrade(all_json[i]["属性"][j], base_txt, i, '第' + str(j) + '个【属性】')
            for j in all_json[i]["冷却时间"]:
                if '名称' not in all_json[i]["冷却时间"][j]:
                    all_json[i]["冷却时间"][j]['名称'] = ''
                kk = 2
                while True:
                    k = str(kk)
                    kk += 1
                    if k in all_json[i]["冷却时间"][j] and '名称' in all_json[i]["冷却时间"][j][k]:
                        all_json[i]["冷却时间"][j]['名称'] = all_json[i]["冷却时间"][j][k]['名称']
                        all_json[i]["冷却时间"][j][k].pop('名称')
                    else:
                        break
                if fulfil(all_json[i]["冷却时间"][j], all_json[i]):
                    one_upgrade(all_json[i]["冷却时间"][j], base_txt, i, '第' + str(j) + '个【冷却时间】')
            for j in all_json[i]["魔法消耗"]:
                if '名称' not in all_json[i]["魔法消耗"][j]:
                    all_json[i]["魔法消耗"][j]['名称'] = ''
                for k in all_json[i]["魔法消耗"][j]:
                    if k != '名称':
                        ll = 2
                        while True:
                            l = str(ll)
                            ll += 1
                            if l in all_json[i]["魔法消耗"][j][k] and '名称' in all_json[i]["魔法消耗"][j][k][l]:
                                all_json[i]["魔法消耗"][j]['名称'] = all_json[i]["魔法消耗"][j][k][l]['名称']
                                all_json[i]["魔法消耗"][j][k][l].pop('名称')
                            else:
                                break
                        if fulfil(all_json[i]["魔法消耗"][j][k], all_json[i]):
                            one_upgrade(all_json[i]["魔法消耗"][j][k], base_txt, i, '第' + str(j) + '个【魔法消耗】')
            for j in all_json[i]["施法前摇"]:
                fulfil(all_json[i]["施法前摇"][j], all_json[i])
                one_upgrade(all_json[i]["施法前摇"][j], base_txt, i, '第' + str(j) + '个【施法前摇】')
            for j in all_json[i]["施法后摇"]:
                fulfil(all_json[i]["施法后摇"][j], all_json[i])
                one_upgrade(all_json[i]["施法后摇"][j], base_txt, i, '第' + str(j) + '个【施法后摇】')


def fulfil(arr, json):
    for i in arr:
        if i.isnumeric():
            if '0' in arr[i]['代码'] and arr[i]['代码']['0'] == '手填':
                continue
            else:
                if "1" in arr[i]['代码'] and arr[i]['代码']["1"] == "":
                    if json['次级分类'] == '物品技能':
                        arr[i]['代码']["1"] = "物品"
                    else:
                        arr[i]['代码']["1"] = "技能"
                if "2" in arr[i]['代码'] and arr[i]['代码']["2"] == "":
                    arr[i]['代码']["2"] = json["代码"]
    return True


def one_upgrade(json, base_txt, name, target):
    ii = 1
    while True:
        ii += 1
        i = str(ii)
        if i not in json:
            break
    extra = ii - 2
    getvalue = [[] for _ in range(extra + 2)]
    calvalue = [[] for _ in range(pow(2, extra))]
    caloprate = ['' for _ in range(extra + 2)]
    if "1" in json:
        if "0" in json["1"]["代码"] and json["1"]["代码"]['0'] != '':
            if json["1"]["代码"]["0"] == "手填":
                k = 0
                while True:
                    k += 1
                    if str(k) in json["1"]["代码"] and json["1"]["代码"][str(k)] != '':
                        try:
                            getvalue[0].append(float(json["1"]["代码"][str(k)]))
                        except ValueError:
                            getvalue[0].append(json["1"]["代码"][str(k)])
                    else:
                        break
            elif json["1"]["代码"]["0"] == "高等级":
                levels = int(json["1"]["代码"]["4"])
                if json["1"]["代码"]["3"] in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]]:
                    for k in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]]:
                        if int(k) < levels:
                            getvalue[0].append(0)
                        else:
                            getvalue[0].append(base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]][k])
                else:
                    raise (editerror('技能源', name, target + '没有找到数据库中《' + json["1"]["代码"]["1"] + '→' + json["1"]["代码"]["2"] + '》' + json["1"]["代码"]["3"] + '的内容'))
            elif json["1"]["代码"]["0"] == "有限等级":
                levels = int(json["1"]["代码"]["4"])
                if json["1"]["代码"]["3"] in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]]:
                    for k in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]]:
                        if int(k) <= levels:
                            getvalue[0].append(base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]][k])
                else:
                    raise (editerror('技能源', name, target + '没有找到《' + json["1"]["代码"]["1"] + '→' + json["1"]["代码"]["2"] + '》数据库中' + json["1"]["代码"]["3"] + '的内容'))
            elif json["1"]["代码"]["0"] == "不存在":
                return
        else:
            if json["1"]["代码"]["1"] in base_txt:
                if json["1"]["代码"]["3"] in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]]:
                    if '4' in json["1"]["代码"] and json["1"]["代码"]["4"] in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]]:
                        getvalue[0].append(base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]][json["1"]["代码"]["4"]])
                    else:
                        for k in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]]:
                            getvalue[0].append(base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["代码"]["3"]][k])
                else:
                    raise (editerror('技能源', name, target + '没有找到《' + json["1"]["代码"]["1"] + '→' + json["1"]["代码"]["2"] + '》数据库中' + json["1"]["代码"]["3"] + '的内容'))
            else:
                getvalue[0].append(json["1"]["代码"]["1"])
        if json["1"]["修正"]["1"] != "":
            caloprate[1] = json["1"]["修正"]["1"]
            k = 1
            try:
                while True:
                    k += 1
                    if str(k) in json["1"]["修正"]:
                        getvalue[1].append(float(json["1"]["修正"][str(k)]))
                    else:
                        break
            except ValueError:
                if json["1"]["修正"]["2"] in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]]:
                    for k in base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["修正"]["2"]]:
                        getvalue[1].append(base_txt[json["1"]["代码"]["1"]][json["1"]["代码"]["2"]][json["1"]["修正"]["2"]][k])
                else:
                    raise (editerror('技能源', name, target + '没有找到《' + json["1"]["代码"]["1"] + '→' + json["1"]["代码"]["2"] + '》数据库中' + json["1"]["修正"]["2"] + '的内容'))
    else:
        getvalue[0].append(0)
        json["1"] = {}
        tempi = '2'
        for tempj in json[tempi]:
            if not tempj.isnumeric() and tempj != '代码':
                json["1"][tempj] = copy.deepcopy(json[tempi][tempj])
    for ii in range(2, extra + 2):
        i = str(ii)
        if "0" in json[i]["代码"] and json[i]["代码"]["0"] == "手填":
            k = 0
            while True:
                k += 1
                if str(k) in json[i]["代码"]:
                    try:
                        getvalue[ii].append(float(json[i]["代码"][str(k)]))
                    except ValueError:
                        getvalue[ii].append(json[i]["代码"][str(k)])
                else:
                    break
        else:
            if json[i]["代码"]["3"] in base_txt[json[i]["代码"]["1"]][json[i]["代码"]["2"]]:
                if '4' in json[i]["代码"] and json[i]["代码"]["4"] in base_txt[json[i]["代码"]["1"]][json[i]["代码"]["2"]][json[i]["代码"]["3"]]:
                    getvalue[ii].append(base_txt[json[i]["代码"]["1"]][json[i]["代码"]["2"]][json[i]["代码"]["3"]][json[i]["代码"]["4"]])
                else:
                    for k in base_txt[json[i]["代码"]["1"]][json[i]["代码"]["2"]][json[i]["代码"]["3"]]:
                        getvalue[ii].append(base_txt[json[i]["代码"]["1"]][json[i]["代码"]["2"]][json[i]["代码"]["3"]][k])
            else:
                raise (editerror('技能源', name, target + '没有找到《' + json[i]["代码"]["1"] + '→' + json[i]["代码"]["2"] + '》数据库中' + json[i]["代码"]["3"] + '的内容'))
        caloprate[ii] = json[i]["修正"]["1"]
    maxlen = 0
    for i in range(len(getvalue)):
        maxlen = max(maxlen, len(getvalue[i]))
    for i in range(len(getvalue)):
        for j in range(maxlen):
            if 0 < len(getvalue[i]) and len(getvalue[i]) <= j:
                getvalue[i].append(getvalue[i][j - 1])
    for i in range(len(calvalue)):
        calvalue[i] = copy.deepcopy(getvalue[0])
    # 优先生效的修正
    while True:
        nowcheck = [0, 0]
        for ii in range(2, extra + 2):
            if len(caloprate[ii]) > 0 and caloprate[ii][0].isnumeric():
                nowcheck = [-1 * int(caloprate[ii][0]), ii - 1]
        if nowcheck[0] < 0:
            for j in range(len(calvalue)):
                if j >> (nowcheck[1] - 1) & 1:
                    calvalue[j] = array_cal(calvalue[j], getvalue[nowcheck[1] + 1], caloprate[nowcheck[1] + 1][1:])
            caloprate[nowcheck[1] + 1] = ''
        else:
            break
    for ii in range(2, extra + 2):
        if len(caloprate[ii]) > 0 and not caloprate[ii][-1].isnumeric():
            for j in range(len(calvalue)):
                if j >> (ii - 2) & 1:
                    calvalue[j] = array_cal(calvalue[j], getvalue[ii], caloprate[ii])
            caloprate[ii] = ''
    if len(caloprate[1]) > 0:
        for j in range(len(calvalue)):
            calvalue[j] = array_cal(calvalue[j], getvalue[1], caloprate[1])
    while True:
        nowcheck = [0, 0]
        for ii in range(2, extra + 2):
            if len(caloprate[ii]) > 0 and caloprate[ii][-1].isnumeric():
                nowcheck = [-1 * int(caloprate[ii][-1]), ii - 1]
        if nowcheck[0] < 0:
            for j in range(len(calvalue)):
                if j >> (nowcheck[1] - 1) & 1:
                    calvalue[j] = array_cal(calvalue[j], getvalue[nowcheck[1] + 1], caloprate[nowcheck[1] + 1][:-1])
            caloprate[nowcheck[1] + 1] = ''
        else:
            break
    for i in range(len(calvalue)):
        if len(calvalue[i]) > 0:
            cut_the_same_to_one(calvalue[i])
    bitsum_list = [all_bit_sum(i) for i in range(pow(2, extra))]
    result_to_show_index = []
    for i in range(extra + 1):
        for j in range(len(bitsum_list)):
            if bitsum_list[j] == i:
                result_to_show_index.append(j)
    for i in range(len(calvalue)):
        for k in range(len(calvalue[result_to_show_index[i]])):
            if str(i + 1) not in json:
                json[str(i + 1)] = {}
            json[str(i + 1)][str(k + 1)] = calvalue[result_to_show_index[i]][k]
        if bitsum_list[result_to_show_index[i]] > 1:
            json[str(i + 1)]["升级来源"] = {}
            for j in range(extra):
                if result_to_show_index[i] >> j & 1:
                    for l in json[str(result_to_show_index[j + 1] + 1)]:
                        if not l.isdigit() and l != '代码' and l != '修正' and l != '升级来源':
                            json[str(i + 1)][l] = json[str(result_to_show_index[j + 1] + 1)][l]
                    json[str(i + 1)]["升级来源"][str(len(json[str(i + 1)]["升级来源"]) + 1)] = json[str(result_to_show_index[j + 1] + 1)]["升级来源"]['1']


def all_bit_sum(i):
    rere = 0
    while True:
        if i > 0:
            rere += i & 1
            i = i >> 1
        else:
            break
    return rere


def cut_the_same_to_one(lists):
    bool = True
    i = 1
    delete_number = 0
    while i < len(lists):
        if lists[0] == lists[i]:
            delete_number += 1
            i = i + 1
        else:
            bool = False
            break
    if bool and i > 1:
        for i in range(delete_number):
            lists.pop(1)


def array_cal(arr1, arr2, opp):
    for i in range(len(arr1)):
        if i < len(arr2):
            try:
                temp = float(arr2[i])
            except ValueError:
                temp = arr2[i]
        else:
            try:
                temp = float(arr2[i])
            except ValueError:
                temp = arr2[i]
        if isinstance(arr1[i], str) and '=' not in opp:
            if opp == '=':
                arr1[i] = temp
        else:
            if isinstance(temp, str):
                arr1[i] = temp
            elif opp == '=':
                arr1[i] = temp
            elif opp == '+':
                arr1[i] = arr1[i] + temp
            elif opp == '-':
                arr1[i] = arr1[i] - temp
            elif opp == '\\-':
                arr1[i] = temp - arr1[i]
            elif opp == '*':
                arr1[i] = arr1[i] * temp
            elif opp == '/':
                arr1[i] = arr1[i] / temp
            elif opp == '\\':
                arr1[i] = temp / arr1[i]
            elif opp == '%-':
                arr1[i] = arr1[i] * (100 - temp) / 100
            elif opp == '%+':
                arr1[i] = arr1[i] * (100 + temp) / 100
            elif opp == '-%':
                arr1[i] = arr1[i] * (1 - temp)
            elif opp == '+%':
                arr1[i] = arr1[i] * (1 + temp)
            elif opp == 'round':
                arr1[i] = round(arr1[i], int(temp))
            elif opp == 'ceil':
                arr1[i] = math.ceil(arr1[i] * pow(10, int(temp))) / pow(10, int(temp))
            elif opp == 'floor':
                arr1[i] = math.floor(arr1[i] * pow(10, int(temp))) / pow(10, int(temp))
            elif opp == '*round':
                arr1[i] = round(arr1[i] * temp)
            elif opp == '*ceil':
                arr1[i] = math.ceil(arr1[i] * temp)
            elif opp == '*floor':
                arr1[i] = math.floor(arr1[i] * temp)
            elif opp[0] == '=' and opp[-1] == '+':
                arr1[i] = float(opp[1:-1]) + temp
            elif opp[0] == '=' and opp[-1] == '-':
                arr1[i] = float(opp[1:-1]) - temp
            elif opp[0] == '=' and opp[-1] == '*':
                arr1[i] = float(opp[1:-1]) * temp
            elif opp[0] == '=' and opp[-1] == '/':
                arr1[i] = float(opp[1:-1]) / temp
    return arr1


def complete_mech(all_json, mech_json):
    for i in all_json:
        for j in all_json[i]["施法目标"]:
            mech_target(all_json[i]["施法目标"][j], mech_json["目标"])
        for j in all_json[i]["效果"]:
            for k in all_json[i]["效果"][j]:
                if "生效目标" in all_json[i]["效果"][j][k]:
                    mech_target(all_json[i]["效果"][j][k]["生效目标"], mech_json["目标"])
        mech_mech(all_json[i], mech_json["机制"])
        mech_junior(all_json[i], mech_json["次级"])
        mech_sign(all_json[i]["效果"], mech_json["标记"])
        mech_repeat(all_json[i]["效果"], mech_json["叠加"])
        mech_others(all_json[i], mech_json)


def mech_target(json, mech):
    for i in ["不分类", "英雄", "非英雄"]:
        if i in json:
            for j in json[i]:
                json[i][j]["值"] = mech["势力"][str(json[i][j]["代码"])]["名称"]
                json[i][j]["颜色"] = mech["势力"][str(json[i][j]["代码"])]["颜色"]
                k = 0
                while True:
                    k = k + 1
                    if str(k) in json[i][j]:
                        json[i][j][str(k)]["值"] = mech["分类"][str(json[i][j][str(k)]["代码"])]["名称"]
                        l = 0
                        while True:
                            l += 1
                            if str(l) in json[i][j][str(k)]:
                                json[i][j][str(k)][str(l)]["值"] = mech["分类"][str(json[i][j][str(k)]["代码"])][
                                    str(json[i][j][str(k)][str(l)]["代码"])]
                            else:
                                break
                    else:
                        break


def mech_mech(json, mech):
    for i in mech:
        if i == "施法类型":
            for j in json["施法类型"]:
                k = 0
                while True:
                    k += 1
                    if str(k) in json["施法类型"][j]:
                        json["施法类型"][j][str(k)]["值"] = mech["施法类型"][str(json["施法类型"][j][str(k)]["代码"])]
                    else:
                        break
        elif i == "效果":
            for j in json[i]:
                for k in json[i][j]:
                    if "代码" in json[i][j][k]:
                        json[i][j][k]["值"] = mech[i][str(json[i][j][k]["代码"])]["名称"]
                        json[i][j][k]["图片"] = mech[i][str(json[i][j][k]["代码"])]["图片"]
        else:
            for j in json[i]:
                for k in json[i][j]:
                    if str(json[i][j][k]["代码"]) in mech[i]:
                        json[i][j][k]["值"] = mech[i][str(json[i][j][k]["代码"])]["名称"]
                        json[i][j][k]["图片"] = mech[i][str(json[i][j][k]["代码"])]["图片"]
                        if json[i][j][k]["简述"] == "":
                            json[i][j][k]["简述"] = mech[i][str(json[i][j][k]["代码"])]["简述"]


def mech_junior(json, mech):
    for i in mech:
        if i in ["即时攻击", "技能窃取"]:
            for j in json[i]:
                for jj in json[i][j]:
                    k = 0
                    while True:
                        k += 1
                        if str(k) in json[i][j][jj]:
                            if str(json[i][j][jj][str(k)]["代码"]) in mech[i]:
                                json[i][j][jj][str(k)]["值"] = mech[i][str(json[i][j][jj][str(k)]["代码"])]["名称"]
                                if "简述" not in json[i][j][jj][str(k)] or json[i][j][jj][str(k)]["简述"] == "":
                                    json[i][j][jj][str(k)]["简述"] = mech[i][str(json[i][j][jj][str(k)]["代码"])]["简述"]
                        else:
                            break
        else:
            for j in json["效果"]:
                for k in json["效果"][j]:
                    if isinstance(json["效果"][j][k], dict) and i in json["效果"][j][k]:
                        if str(json["效果"][j][k][i]["代码"]) in mech[i]:
                            json["效果"][j][k][i]["值"] = mech[i][str(json["效果"][j][k][i]["代码"])]["名称"]
                            if "图片" in mech[i][str(json["效果"][j][k][i]["代码"])]:
                                json["效果"][j][k][i]["图片"] = mech[i][str(json["效果"][j][k][i]["代码"])]["图片"]
                            if "简述" not in json["效果"][j][k][i] or json["效果"][j][k][i]["简述"] == "":
                                json["效果"][j][k][i]["简述"] = mech[i][str(json["效果"][j][k][i]["代码"])]["简述"]


def mech_sign(json, mech):
    for i in json:
        for j in json[i]:
            if isinstance(json[i][j], dict) and "标记" in json[i][j]:
                for k in json[i][j]["标记"]:
                    if json[i][j]["标记"][k]["类型"] in mech and str(json[i][j]["标记"][k]["代码"]) in mech[json[i][j]["标记"][k]["类型"]]:
                        json[i][j]["标记"][k]["值"] = mech[json[i][j]["标记"][k]["类型"]][str(json[i][j]["标记"][k]["代码"])]


def mech_repeat(json, mech):
    for i in json:
        for j in json[i]:
            if isinstance(json[i][j], dict) and "叠加" in json[i][j]:
                for k in json[i][j]["叠加"]:
                    if str(json[i][j]["叠加"][k]["代码1"]) in mech["来源"] and str(json[i][j]["叠加"][k]["代码2"]) in mech["方式"]:
                        json[i][j]["叠加"][k]["来源"] = mech["来源"][str(json[i][j]["叠加"][k]["代码1"])]
                        json[i][j]["叠加"][k]["方式"] = mech["方式"][str(json[i][j]["叠加"][k]["代码2"])]


def mech_others(json, mech):
    for i in json["魔法消耗"]:
        for j in json["魔法消耗"][i]:
            if j != '名称':
                for k in json["魔法消耗"][i][j]:
                    if "类型" in json["魔法消耗"][i][j][k]:
                        json["魔法消耗"][i][j][k]["类型"]["值"] = mech["魔法消耗"][str(json["魔法消耗"][i][j][k]["类型"]["代码"])]['名称']
                        json["魔法消耗"][i][j][k]["类型"]["后缀"] = mech["魔法消耗"][str(json["魔法消耗"][i][j][k]["类型"]["代码"])]['后缀']
    for i in json["冷却时间"]:
        for j in json["冷却时间"][i]:
            if j != '名称':
                if "类型" in json["冷却时间"][i][j]:
                    json["冷却时间"][i][j]["类型"]["值"] = mech["冷却时间"][str(json["冷却时间"][i][j]["类型"]["代码"])]["名称"]
                    json["冷却时间"][i][j]["类型"]["图片"] = mech["冷却时间"][str(json["冷却时间"][i][j]["类型"]["代码"])]["图片"]
    for i in json["施法前摇"]:
        for j in json["施法前摇"][i]:
            if j != '名称':
                if str(json["施法前摇"][i][j]["即时生效"]["代码"]) in mech["即时生效"]:
                    json["施法前摇"][i][j]["即时生效"]["图片"] = mech["即时生效"][str(json["施法前摇"][i][j]["即时生效"]["代码"])]


def loop_check(json, data, all_json, name, target):
    for i in json:
        ttarget = copy.deepcopy(target)
        ttarget.append(i)
        if isinstance(json[i], dict):
            if "混合文字" in json[i]:
                ttarget.append("混合文字")
                change_combine_txt(json, i, data, all_json, name, ttarget)
            else:
                loop_check(json[i], data, all_json, name, ttarget)


def change_combine_txt(json, ii, data, all_json, name, target):
    returntxt = ""
    i = 0
    while True:
        i += 1
        if str(i) in json[ii]["混合文字"]:
            if isinstance(json[ii]["混合文字"][str(i)], dict):
                if json[ii]["混合文字"][str(i)]['类型'] == '' or json[ii]["混合文字"][str(i)]['类型'] == '数据' or json[ii]["混合文字"][str(i)]['类型'][:2] == '切换':
                    if json[ii]["混合文字"][str(i)]['类型'][:2] == '切换':
                        if len(json[ii]["混合文字"][str(i)]['类型']) <= 2 or json[ii]["混合文字"][str(i)]['类型'][2] == '0':
                            returntxt += '<div class="dota_rotatey_transform_switch_content0">'
                        else:
                            returntxt += '<div class="dota_rotatey_transform_switch_content1">'
                    j = 0
                    while True:
                        j += 1
                        if str(j) in json[ii]["混合文字"][str(i)]:
                            if json[ii]["混合文字"][str(i)][str(j)]["0"][-2:] == "属性":
                                if json[ii]["混合文字"][str(i)][str(j)]["1"] == "":
                                    json[ii]["混合文字"][str(i)][str(j)]["1"] = target[0] if target[0][-1] != '源' else target[0][:-1]
                                if json[ii]["混合文字"][str(i)][str(j)]["2"] == "":
                                    json[ii]["混合文字"][str(i)][str(j)]["2"] = name
                            elif json[ii]["混合文字"][str(i)][str(j)]["0"] == "数据库":
                                if json[ii]["混合文字"][str(i)][str(j)]["1"] == "":
                                    json[ii]["混合文字"][str(i)][str(j)]["1"] = target[0] if target[0][-1] != '源' else target[0][:-1]
                                if json[ii]["混合文字"][str(i)][str(j)]["2"] == "":
                                    json[ii]["混合文字"][str(i)][str(j)]["2"] = all_json[target[0]][name]["代码"]
                        else:
                            break
                    ttarget = copy.deepcopy(target)
                    ttarget.append(str(i))
                    temp = combine_txt_numbers(json[ii]["混合文字"][str(i)], [1], all_json, data, ttarget)
                    if "等级" in json[ii]["混合文字"][str(i)] and int(json[ii]["混合文字"][str(i)]["等级"]) > 0:
                        level = int(json[ii]["混合文字"][str(i)]["等级"])
                    else:
                        level = 0
                    if "后缀" in json[ii]["混合文字"][str(i)]:
                        post = json[ii]["混合文字"][str(i)]["后缀"]
                    else:
                        post = ""
                    for j in range(len(temp)):
                        bool = True
                        for k in range(len(temp[j][0])):
                            bool = bool and temp[j][0][0] == temp[j][0][k]
                        if bool:
                            temp[j][0] = [temp[j][0][0]]
                    returntxt += combine_numbers_post_level(temp[0][0], post, level)
                    if len(temp) > 1:
                        returntxt += "("
                        for j in range(1, len(temp)):
                            for k in temp[j][1]:
                                returntxt += "[[file:"
                                if target[2] == '描述':
                                    returntxt += temp[j][1][k]
                                else:
                                    returntxt += temp[j][1][k].replace('Talent.png', 'Talentb.png')
                                returntxt += "|x18px|link=" + k + "]]"
                            returntxt += combine_numbers_post_level(temp[j][0], post, level)
                        returntxt += ")"
                    if json[ii]["混合文字"][str(i)]['类型'][:2] == '切换':
                        returntxt += '</div>'
                elif json[ii]["混合文字"][str(i)]['类型'] == '机制切换':
                    re0=''
                    re1=''
                    j = 0
                    while True:
                        j += 1
                        if str(j) in json[ii]["混合文字"][str(i)]:
                            if json[ii]["混合文字"][str(i)][str(j)]["0"] == "":
                                jsonname=name
                            else:
                                jsonname=json[ii]["混合文字"][str(i)][str(j)]["0"]
                            if jsonname in all_json['机制']:
                                if json[ii]["混合文字"][str(i)][str(j)]["1"] == "":
                                    raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n没有输入条目的名称，请进行输入'))
                                else:
                                    listname=json[ii]["混合文字"][str(i)][str(j)]["1"]
                                    if listname in all_json['机制'][jsonname]['简单条目']:
                                        re0+=all_json['机制'][jsonname]['简单条目'][listname]
                                    if listname in all_json['机制'][jsonname]['具体条目']:
                                        re1+=all_json['机制'][jsonname]['具体条目'][listname]
                        else:
                            break
                    returntxt += '<div class="dota_rotatey_transform_switch_content0">'+re0+'</div>'\
                                 +'<div class="dota_rotatey_transform_switch_content1">'+re1+'</div>'
                elif json[ii]["混合文字"][str(i)]['类型'][:2] == '检索' or json[ii]["混合文字"][str(i)]['类型'][:2] == '查询':
                    ttarget = copy.deepcopy(target)
                    ttarget.append(str(i))
                    firstsep=(len(json[ii]["混合文字"][str(i)]['类型'])<=2 or json[ii]["混合文字"][str(i)]['类型'][2]!='1') and returntxt!=''
                    returntxt += find_the_jsons_by_conditions_and_show(json[ii]["混合文字"][str(i)], all_json, ttarget,firstsep)
            else:
                returntxt += json[ii]["混合文字"][str(i)]
        else:
            break
    json[ii] = returntxt


def combine_txt_numbers(json, index, all_json, base_txt, target):
    i = index[0]
    if json[str(i)]["1"] == "(" or json[str(i)]["1"] == "（":
        index[0] = i + 1
        rere = combine_txt_numbers(json, index, all_json, base_txt, target)
        i = index[0]
    else:
        ttarget = copy.deepcopy(target)
        ttarget.append(str(i))
        rere = one_combine_txt_numbers(json[str(i)], all_json, base_txt, ttarget)
    while True:
        i += 1
        if str(i) in json:
            if json[str(i)]["1"] == "(" or json[str(i)]["1"] == "（":
                index[0] = i + 1
                temp = combine_txt_numbers(json, index, all_json, base_txt, target)
                rere = calculate_combine_txt_numbers(rere, temp, json[str(i)]["符号"])
                i = index[0]
            elif json[str(i)]["符号"] == ")" or json[str(i)]["符号"] == "）":
                index[0] = i
                return rere
            else:
                ttarget = copy.deepcopy(target)
                ttarget.append(str(i))
                temp = one_combine_txt_numbers(json[str(i)], all_json, base_txt, ttarget)
                rere = calculate_combine_txt_numbers(rere, temp, json[str(i)]["符号"])
        else:
            return rere


def one_combine_txt_numbers(json, all_json, base_txt, target):
    rere = [[[], {}]]
    if json["0"] == "属性":
        if json["3"] in all_json[json["1"]][json["2"]]:
            temp = all_json[json["1"]][json["2"]][json["3"]]
            i = 3
            while True:
                i += 1
                if str(i) in json and json[str(i)] != '':
                    temp = temp[json[str(i)]]
                else:
                    break
            j = 0
            while True:
                j += 1
                if str(j) in temp:
                    rere[0][0].append(change_str_to_float(temp[str(j)]))
                else:
                    break
        else:
            raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n没有找到《' + json["1"] + '→' + json["2"] + '》数据库中' + json["3"] + '的内容'))
    elif json["0"] == "数据库":
        if json["3"] in base_txt[json["1"]][json["2"]]:
            temp = base_txt[json["1"]][json["2"]][json["3"]]
            i = 3
            while True:
                i += 1
                if str(i) in json and json[str(i)] != '':
                    temp = temp[json[str(i)]]
                else:
                    break
            if isinstance(temp, dict):
                j = 0
                while True:
                    j += 1
                    if str(j) in temp:
                        rere[0][0].append(change_str_to_float(temp[str(j)]))
                    else:
                        break
            else:
                rere[0][0].append(change_str_to_float(temp))
        else:
            raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n没有找到《' + json["1"] + '→' + json["2"] + '》数据库中' + json["3"] + '的内容'))
    elif json['0'] == '普通属性':
        if json["3"] in all_json[json["1"]][json["2"]]:
            temp = all_json[json["1"]][json["2"]][json["3"]]
            i = 3
            while True:
                i += 1
                if str(i) in json and json[str(i)] != '':
                    temp = temp[json[str(i)]]
                else:
                    break
            rere[0][0].append(change_str_to_int(temp))
        else:
            raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n没有找到《' + json["1"] + '→' + json["2"] + '》数据库中' + json["3"] + '的内容'))
    elif json['0'] == '全部文字属性':
        temp = all_json[json["1"]][json["2"]]
        temptext = ''
        seps = json['符号']
        ii = 2
        while True:
            ii += 1
            i = str(ii)
            if i in json and json[i] != '':
                if json[i] in temp:
                    temp = temp[json[i]]
                else:
                    raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n没有找到《' + json["1"] + '→' + json["2"] + '》数据库中第' + i + '项' + json[i] + '的内容'))
            else:
                break
        if isinstance(temp, dict):
            for i in temp:
                if isinstance(temp[i], str):
                    if temptext != '':
                        temptext += seps
                    temptext += temp[i]
        rere[0][0].append(temptext)
    elif json['0'] == '图片链接':
        temp = all_json[json["1"]][json["2"]]
        rere[0][0].append('[[file:' + temp['迷你图片'] + '|' + json['3'] + '|link=]][[' + temp['页面名'] + ']]')
    elif json["0"] == "手填":
        j = 0
        while True:
            j += 1
            if str(j) in json:
                rere[0][0].append(change_str_to_float(json[str(j)]))
            else:
                break
    elif json["0"] == "升级属性":
        if json["3"] in all_json[json["1"]][json["2"]]:
            temp = all_json[json["1"]][json["2"]][json["3"]]
            i = 3
            while True:
                i += 1
                if str(i) in json:
                    if str(json[str(i)]) == '升级':
                        ii = i + 1
                        break
                    else:
                        if str(json[str(i)]) in temp:
                            temp = temp[str(json[str(i)])]
                        elif str(json[str(i)]).isdigit():
                            temp = temp["1"]
                else:
                    ii = 0
                    break
            i = 0
            while True:
                i += 1
                if str(i) in temp:
                    if i > 1:
                        rere.append([[], {}])
                        for j in temp[str(i)]["升级来源"]:
                            rere[i - 1][1][temp[str(i)]["升级来源"][j]['名称']] = temp[str(i)]["升级来源"][j]['图片']
                    if ii == 0:
                        j = 0
                        while True:
                            j += 1
                            if str(j) in temp[str(i)]:
                                rere[i - 1][0].append(temp[str(i)][str(j)])
                            else:
                                break
                    else:
                        if str(json[str(ii)]) in temp[str(i)]:
                            rere[i - 1][0] = [temp[str(i)][json[str(ii)]]]
                        elif str(json[str(ii)]).isdigit():
                            rere[i - 1][0] = [temp[str(i)]["1"]]
                else:
                    break
        else:
            raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n没有找到《' + json["1"] + '→' + json["2"] + '》数据库中' + json["3"] + '的内容'))
    else:
        if json["3"] in all_json[json["1"]][json["2"]]:
            temp = all_json[json["1"]][json["2"]][json["3"]]
            i = 3
            while True:
                i += 1
                if str(i) in json:
                    if str(json[str(i)]) in temp:
                        temp = temp[str(json[str(i)])]
                    elif str(json[str(i)]).isdigit():
                        temp = temp["1"]
                else:
                    break
            i = 0
            while True:
                i += 1
                if str(i) in temp:
                    if i > 1:
                        rere.append([[], {}])
                        for j in temp[str(i)]["升级来源"]:
                            rere[i - 1][1][temp[str(i)]["升级来源"][j]['名称']] = temp[str(i)]["升级来源"][j]['图片']
                    if isinstance(temp[str(i)], dict):
                        j = 0
                        while True:
                            j += 1
                            if str(j) in temp[str(i)]:
                                rere[i - 1][0].append(temp[str(i)][str(j)])
                            else:
                                break
                    else:
                        rere[i - 1][0] = [temp[str(i)]]
                else:
                    break
        else:
            raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n没有找到《' + json["1"] + '→' + json["2"] + '》数据库中' + json["3"] + '的内容'))
    return rere


def calculate_combine_txt_numbers(list1, list2, op):
    all_up_source = {}
    for i in list1 + list2:
        if len(i[1]) == 1:
            all_up_source.update(i[1])
    lack1 = copy.deepcopy(all_up_source)
    lack2 = copy.deepcopy(all_up_source)
    for i in list1:
        for j in i[1]:
            if j in lack1:
                lack1.pop(j)
    for i in list2:
        for j in i[1]:
            if j in lack2:
                lack2.pop(j)
    expand1 = expand_value_source_list_with_another_source_dict(list1, lack1, all_up_source)
    expand2 = expand_value_source_list_with_another_source_dict(list2, lack2, all_up_source)
    for i in range(len(expand1)):
        if op == 'max_stack':  # 前最大值，后公差，首项为0
            expand1[i][0] = [expand1[i][0][0]]
            j = 0
            while True:
                if j * expand2[i][0][0] < expand1[i][0][j]:
                    expand1[i][0].insert(j, j * expand2[i][0][0])
                    j += 1
                else:
                    break
        elif op == 'max_stack2':  # 前最大值，后项数，首项为0
            expand1[i][0] = [expand1[i][0][0]]
            for j in range(int(expand2[i][0][0])):
                expand1[i][0].insert(j, j * expand1[i][0][j] / expand2[i][0][0])
        elif op == 'num_stack':  # 前项数，后公差，首项为0
            jj = expand1[i][0][0]
            expand1[i][0] = []
            for j in range(int(jj)):
                expand1[i][0].append(j * expand2[i][0][0])
        elif op == 'stack_list':  # 将这列数字延展到固定长度
            while len(expand1[i][0]) > expand2[i][0][0]:
                expand1[i][0].pop()
            while len(expand1[i][0]) < expand2[i][0][0]:
                expand1[i][0].append(expand1[i][0][-1])
        elif op == 'stack_sum':  # 对这列数字求和，前数列，后最大项数
            if expand2[i][0][0] > 0:
                while len(expand1[i][0]) > expand2[i][0][0]:
                    expand1[i][0].pop()
                while len(expand1[i][0]) < expand2[i][0][0]:
                    expand1[i][0].append(expand1[i][0][-1])
            lenre = len(expand1[i][0])
            for x in range(lenre):
                sum = 0
                for y in range(lenre - x):
                    sum += expand1[i][0][y]
                expand1[i][0][lenre - x - 1] = sum
        elif op == 'catch':  # 抓取第n个数字提出
            if len(expand1[i][0]) < expand2[i][0][0]:
                expand1[i][0] = [expand1[i][0][-1]]
            else:
                expand1[i][0] = [expand1[i][0][expand2[i][0][0]]]
        elif op == 'matrix+':  # 前后两组矩阵乘，生成m*n组数值。
            matx = copy.deepcopy(expand1[i][0])
            maty = copy.deepcopy(expand2[i][0])
            expand1[i][0] = []
            for j in range(len(matx)):
                for k in range(len(maty)):
                    expand1[i][0].append(matx[j] + maty[k])
        elif op == 'matrix*':  # 前后两组矩阵乘，生成m*n组数值。
            matx = copy.deepcopy(expand1[i][0])
            maty = copy.deepcopy(expand2[i][0])
            expand1[i][0] = []
            for j in range(len(matx)):
                for k in range(len(maty)):
                    expand1[i][0].append(matx[j] * maty[k])
        # 这里要注意，填入的运算数数量很大，它们分别是0、首格填入的字（每行描述：1、前置字符2、初始数字3、步长4、层数5、后置字符）（每列描述：6、前置字符7、初始数字8、步长9、层数10、后置字符）
        elif op == 'matrix_table':
            at = copy.deepcopy(expand2[i][0])
            x = int(at[4])
            y = int(at[9])
            rere = '{{属性表格|' + at[0]
            for j in range(y):
                rere = rere + ',' + at[6] + str(int(at[7] + j * at[8])) + at[10]
            for j in range(x):
                rere = rere + ';' + at[1] + str(int(at[2] + j * at[3])) + at[5]
                for k in range(y):
                    rere = rere + ',' + str(expand1[i][0][j * y + k])
            rere = rere + '}}'
            expand1[i][0] = [rere]
        else:
            for j in range(max(len(expand1[i][0]), len(expand2[i][0]))):
                if j >= len(expand1[i][0]):
                    expand1[i][0].append(expand1[i][0][j - 1])
                if j >= len(expand2[i][0]):
                    expand2[i][0].append(expand2[i][0][j - 1])
            for j in range(len(expand1[i][0])):
                if op == '..':
                    expand1[i][0][j] = number_to_string(expand1[i][0][j]) + number_to_string(expand2[i][0][j])
                elif op == '+':
                    expand1[i][0][j] += expand2[i][0][j]
                elif op == '-':
                    expand1[i][0][j] -= expand2[i][0][j]
                elif op == '*':
                    expand1[i][0][j] *= expand2[i][0][j]
                elif op == '/':
                    expand1[i][0][j] /= expand2[i][0][j]
                elif op == '\\':
                    expand1[i][0][j] = expand2[i][0][j] / expand1[i][0][j]
                elif op == '^' or op == 'pow':
                    expand1[i][0][j] = pow(expand1[i][0][j], expand2[i][0][j])
                elif op == '%-':
                    expand1[i][0][j] = expand1[i][0][j] * (100 - expand2[i][0][j]) / 100
                elif op == '-%':
                    expand1[i][0][j] = expand1[i][0][j] * (1 - expand2[i][0][j])
                elif op == '%+':
                    expand1[i][0][j] = expand1[i][0][j] * (100 + expand2[i][0][j]) / 100
                elif op == '+%':
                    expand1[i][0][j] = expand1[i][0][j] * (1 + expand2[i][0][j])
                elif op == 'min' or op == "↓":
                    expand1[i][0][j] = min(expand1[i][0][j], expand2[i][0][j])
                elif op == 'max' or op == "↑":
                    expand1[i][0][j] = max(expand1[i][0][j], expand2[i][0][j])
                elif op == 'round':
                    expand1[i][0][j] = round(expand1[i][0][j], int(expand2[i][0][j]))
                elif op == 'ceil':
                    expand1[i][0][j] = math.ceil(expand1[i][0][j] * pow(10, expand2[i][0][j])) / pow(10, expand2[i][0][j])
                elif op == 'floor':
                    expand1[i][0][j] = math.floor(expand1[i][0][j] * pow(10, expand2[i][0][j])) / pow(10, expand2[i][0][j])
                elif op == '%*%':
                    expand1[i][0][j] = (100 - (100 - expand1[i][0][j]) * (100 - expand2[i][0][j]) / 100)
                elif op == 'a2%':
                    expand1[i][0][j] = 13 * expand1[i][0][j] / (225 + 12 * abs(expand1[i][0][j])) * expand2[i][0][j]
                elif op == '%2a':
                    expand1[i][0][j] = 225 * expand1[i][0][j] / (13 * expand2[i][0][j] - 12 * abs(expand1[i][0][j]))
                elif op == 'int':
                    expand1[i][0][j] = int(expand1[i][0][j])
                elif op == 'gp_s':  # 等比数列（GP）求和（前公比，后项数，首项1）
                    expand1[i][0][j] = (1 - pow(expand1[i][0][j], expand2[i][0][j])) / (1 - expand1[i][0][j])
                elif op == 'ap_s':  # 等比数列（AP）求和（前公差，后项数，首项1倍公差）
                    expand1[i][0][j] = expand1[i][0][j] * (1 + expand2[i][0][j]) * expand2[i][0][j] / 2
                elif op == 'ap_s2':  # 等比数列（AP）求和（前末项，后项数，首项1倍公差）
                    expand1[i][0][j] = expand1[i][0][j] * (1 + expand2[i][0][j]) / 2
    return expand1


# 查询满足条件的内容并展示
def find_the_jsons_by_conditions_and_show(json, all_json, target, firstseps=False):
    retxt = ''
    all_results_with_sort_mark = []
    conditions = change_json_to_condition_dict(json, target)
    seps = json['后缀']
    for i in all_json:
        if i[-1] != '源':
            for j in all_json[i]:
                result, bool = check_the_json_meet_the_conditions(conditions['满足'], all_json[i][j], target)
                if bool:
                    for k in range(len(result)):
                        all_results_with_sort_mark.append(change_the_right_result_json_to_text_to_show(conditions, result[k], all_json[i][j], all_json, target))
    if seps == '数量':
        retxt = str(len(all_results_with_sort_mark))  # 这个地方直接用=是为了防止之前加入一些奇怪的东西
    else:
        if len(all_results_with_sort_mark) > 0:
            sorttime = len(all_results_with_sort_mark[0])
            for i in range(1, sorttime):
                reverse = all_results_with_sort_mark[0][i][1] == '-'
                all_results_with_sort_mark.sort(key=lambda x: x[i][0], reverse=reverse)
            for i in range(len(all_results_with_sort_mark)):
                if firstseps or i > 0:
                    retxt += seps
                retxt += all_results_with_sort_mark[i][0]
        else:
            retxt = ''
    return retxt


def change_the_right_result_json_to_text_to_show(conditions, result, json, all_json, target):
    sort_mark = []
    retxt = ''
    miniimage = ''
    minisource = ''
    if '迷你图片' in json and json['迷你图片'] != '':
        miniimage = '[[file:' + json['迷你图片'] + '|x24px|link=]]'
    if '技能归属' in json:
        for i in all_json:
            if json['技能归属'] in all_json[i]:
                if '迷你图片' in all_json[i][json['技能归属']] and all_json[i][json['技能归属']]['迷你图片'] != '':
                    minisource = '[[file:' + all_json[i][json['技能归属']]['迷你图片'] + '|x24px|link=]]'
                minisource += '[[' + json['技能归属'] + ']] - '
    if '排序' in conditions:
        for i in range(len(conditions['排序'])):
            sort_mark += find_json_by_condition_with_result(conditions['排序'][i], i, json, result, target)
    if conditions['函数'][0][0] == '短':
        another_image = ''
        another_name = ''
        another_info = ''
        traitlist = []

        if '条件升级图片' in conditions:
            for i in range(len(conditions['条件升级图片'])):
                tempjson = find_json_by_condition_with_result(conditions['条件升级图片'][i], i, json, result, target)
                if '升级来源' in tempjson:
                    for j in tempjson['升级来源']:
                        another_image += '[[file:' + tempjson['升级来源'][j]['图片'] + '|x22px|link=]]'
        if '条件名称' in conditions:
            for i in range(len(conditions['条件名称'])):
                tempjson = find_json_by_condition_with_result(conditions['条件名称'][i], i, json, result, target)
                if isinstance(tempjson, str):
                    another_name += '(' + tempjson + ')'

        if '条件属性' in conditions:
            for i in range(len(conditions['条件属性'])):
                tempjson = find_json_by_condition_with_result(conditions['条件属性'][i], i, json, result, target)
                kk = 0
                while True:
                    kk += 1
                    k = str(kk)
                    if k in tempjson:
                        if str(tempjson[k]) in json['属性']:
                            if str(tempjson[k]) not in traitlist:
                                traitlist.append(str(tempjson[k]))
                        else:
                            raise (editerror(target[0], target[1], '在调用第' + str(i) + '条【条件属性】时，没有找到【' + json['页面名'] + '】的第' + str(tempjson[k]) + '条【属性】'))
                    else:
                        break
        if len(traitlist) > 0:
            another_info += '('
            for i in range(len(traitlist)):
                if i > 0:
                    another_info += ';'
                another_info += common_page.create_upgrade_text(json["属性"], traitlist[i], image_size='x18px')
            another_info += ')'

        if '条件物品属性' in conditions:
            for i in conditions['条件物品属性']:
                another_info += '(' + number_to_string(json[i[0]]['1']) + json[i[0]]['后缀'] + ')'

        retxt += '[[file:' + json['迷你图片'] + '|x24px|link=]]' + another_image + '[[' + json['页面名'] + ']]' + another_name + another_info
    else:  # 普通的ability_desc
        another_image = ''
        another_name = ''
        trait = ''
        traitlist = []
        mech = ''
        note = ''
        if ('中文名' not in conditions or conditions['中文名'][0][0] != '0') and '次级分类' in json and json['次级分类'] == '天赋技能' and isinstance(json['中文名'], str):
            another_name += '(' + json['中文名'] + ')'

        if '条件升级图片' in conditions:
            for i in range(len(conditions['条件升级图片'])):
                tempjson = find_json_by_condition_with_result(conditions['条件升级图片'][i], i, json, result, target)
                if '升级来源' in tempjson:
                    for j in tempjson['升级来源']:
                        another_image += '[[file:' + tempjson['升级来源'][j]['图片'] + '|x22px|link=' + tempjson['升级来源'][j]['名称'] + ']]'
        if '条件名称' in conditions:
            for i in range(len(conditions['条件名称'])):
                tempjson = find_json_by_condition_with_result(conditions['条件名称'][i], i, json, result, target)
                if isinstance(tempjson, str):
                    another_name += '(' + tempjson + ')'
        if '属性名' in conditions:
            for i in conditions['属性名'][0]:
                for j in json['属性']:
                    if json['属性'][j]['名称'] == i:
                        if j not in traitlist:
                            traitlist.append(j)
        if '条件属性' in conditions:
            for i in range(len(conditions['条件属性'])):
                tempjson = find_json_by_condition_with_result(conditions['条件属性'][i], i, json, result, target)
                kk = 0
                while True:
                    kk += 1
                    k = str(kk)
                    if k in tempjson:
                        if str(tempjson[k]) in json['属性']:
                            if str(tempjson[k]) not in traitlist:
                                traitlist.append(str(tempjson[k]))
                        else:
                            raise (editerror(target[0], target[1], '在调用第' + str(i) + '条【条件属性】时，没有找到【' + json['页面名'] + '】的第' + str(tempjson[k]) + '条【属性】'))
                    else:
                        break
                if '简述' in tempjson and tempjson['简述'] != '':
                    note += '<div>' + tempjson['简述'] + '</div>'
        for i in traitlist:
            trait += '<div>' + json['属性'][i]['名称'] + '：' + common_page.create_upgrade_text(json["属性"], i, image_size='x18px') + '</div>'

        if '条件物品属性' in conditions:
            for i in conditions['条件物品属性']:
                trait += '<div>' + i[0] + '：' + number_to_string(json[i[0]]['1']) + json[i[0]]['后缀'] + '</div>'

        if '条件机制' in conditions:
            for i in range(len(conditions['条件机制'])):
                tempjson = find_json_by_condition_with_result(conditions['条件机制'][i], i, json, result, target)
                if '代码' in tempjson:
                    if tempjson['代码'] != 0:
                        mech += ability_desc_show_one_mech(tempjson)
                else:
                    has_mech = False
                    if isinstance(tempjson, dict):
                        for j in tempjson:
                            if isinstance(tempjson[j], dict) and '代码' in tempjson[j]:
                                has_mech = True
                                if tempjson[j]['代码'] != 0:
                                    mech += ability_desc_show_one_mech(tempjson[j], True)
                    if not has_mech:
                        raise (editerror(target[0], target[1], '在调用第' + str(i) + '条【条件机制】时，没有找到任何可能的机制内容，请检查输入是否正确（本功能不能一个条件输入多个机制）'))

        if '条件注释' in conditions:
            for i in range(len(conditions['条件注释'])):
                tempjson = find_json_by_condition_with_result(conditions['条件注释'][i], i, json, result, target)
                if isinstance(tempjson, str) and tempjson != '':
                    note += '<div>' + tempjson + '</div>'

        if '次级分类' in json:
            if json['次级分类'] == '神杖技能':
                note += '<div style="float:right;color:#4189d4">[[file:Agha.png|x18px|link=]]&nbsp;由阿哈利姆神杖获得</div>'
            elif json['次级分类'] == '魔晶技能':
                note += '<div style="float:right;color:#4189d4">[[file:Shard.png|x18px|link=]]&nbsp;由阿哈利姆魔晶获得</div>'

        retxt += '<div class="dota-ability-wrapper">' \
                 '<span class="dota-ability-image">[[file:' + json['图片'] + '|72px|link=]]</span>' \
                                                                           '<span class="dota-ability-right">' \
                                                                           '<div class="dota-ability-title"><span>' + minisource + '[[' + json[
                     '页面名'] + ']]' + another_image + another_name + '</span></div>' \
                                                                    '<div class="dota-ability-desc">' + trait + mech + note + '</div></span></div>'
    return [retxt] + sort_mark


def ability_desc_show_one_mech(json, upgrade=False):
    retxt = '<div>'
    if upgrade and '升级来源' in json:
        for i in json['升级来源']:
            retxt += '[[file:' + json['升级来源'][i]['图片'] + '|x18px|link=' + json['升级来源'][i]['名称'] + ']]'
    if '图片' in json:
        retxt += '[[file:' + json['图片'] + '|x18px|link=]]'
    if '值' in json:
        retxt += json['值']
    if '简述' in json:
        retxt += '：' + json['简述']
    retxt += '</div>'
    return retxt


def find_json_by_condition_with_result(condition, i, tempjson, result, target):
    for j in range(len(condition)):
        the_key = ''
        if '-' in condition[j]:
            indexlist = condition[j].split('-')
            indexlist[0] = change_str_to_int(indexlist[0])-1
            indexlist[1] = change_str_to_int(indexlist[1])
            if indexlist[0] < len(result) and indexlist[1] < len(result[indexlist[0]]):
                the_key = result[indexlist[0]][indexlist[1]]
            else:
                raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在调用第' + str(i) + '条【条件属性】第' + str(j) + '项时，检查到序数超标了，请检查是否填写错误'))
        elif condition[j] == '@average' or condition[j] == '@平均' or condition[j] == '@min' or condition[j] == '@最小' or condition[j] == '@max' or condition[j] == '@最大':
            _sum, count, _min, _max = 0, 0, float('inf'), float('-inf')
            kk = 0
            while True:
                kk += 1
                k = str(kk)
                if k in tempjson:
                    _sum += tempjson[k]
                    count += 1
                    _min = min(_min, tempjson[k])
                    _max = max(_max, tempjson[k])
                else:
                    break
            if len(condition) >= j + 2 and (condition[j + 1] == '+' or condition[j] == '-'):
                if condition[j] == '@average' or condition[j] == '@平均':
                    return [[_sum / count, condition[j + 1]]]
                if condition[j] == '@min' or condition[j] == '@最小':
                    return [[_min, condition[j + 1]]]
                if condition[j] == '@max' or condition[j] == '@最大':
                    return [[_max, condition[j + 1]]]
            else:
                raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在调用第' + str(i) + '条【条件属性】第' + str(j) + '项时，您的排序没有声明升降序，或声明发生了错误'))
        elif condition[j] == '@技能':
            if tempjson['分类'] == '技能':
                p = Pinyin()
                list1 = [tempjson['技能排序'], '+']
                list2 = [p.get_pinyin(tempjson['技能归属']), '+']
                indexdict = {'英雄技能': 1, '非英雄单位技能': 2, '物品技能': 3}
                indexkey = tempjson['次级分类']
                list3 = []
                if indexkey in indexdict:
                    list3 = [indexdict[indexkey], '+']
                else:
                    list3 = [1, '+']
                return [list1, list2, list3]
            else:
                raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在调用第' + str(i) + '条【条件属性】第' + str(j) + '项时，查询到的不是技能，请重新确定自己【满足】条件'))
        elif condition[j] == '@pinyin' or condition[j] == '@拼音':
            if isinstance(tempjson, str) and len(condition) >= j + 2 and (condition[j + 1] == '+' or condition[j] == '-'):
                p = Pinyin()
                return [[p.get_pinyin(tempjson), condition[j + 1]]]
            else:
                raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在调用第' + str(i) + '条【条件属性】第' + str(j) + '项时，您的排序没有声明升降序，或声明发生了错误，或目标不是文字'))
        elif condition[j] == '@+' or condition[j] == '@升序':
            return [[tempjson, '+']]
        elif condition[j] == '@-' or condition[j] == '@降序':
            return [[tempjson, '-']]
        elif condition[j] == '@大分类' or condition[j] == '@英非物':
            indexkey = {'英雄技能': 1, '非英雄单位技能': 2, '物品技能': 3}
            if len(condition) >= j + 2 and len(condition[j + 1]) > 0:
                indexkey['英雄技能'] = int(condition[j + 1][0])
                if len(condition[j + 1]) > 1:
                    indexkey['非英雄单位技能'] = int(condition[j + 1][1])
                    if len(condition[j + 1]) > 2:
                        indexkey['物品技能'] = int(condition[j + 1][2])
            if tempjson in indexkey:
                return [[indexkey[tempjson], '+']]
            else:
                return [[indexkey['英雄技能'], '+']]
        else:
            the_key = condition[j]
        if the_key in tempjson:
            tempjson = tempjson[the_key]
        else:
            raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在调用第' + str(i) + '条【条件属性】第' + str(j) + '项时，怀疑到您有跳级的嫌疑，请确认输入的顺序正确'))
    return tempjson


def check_the_json_meet_the_conditions(conditions, json, target):
    relist = [[]]  # 预设一个空结果，防止复制失败
    all_bools = True
    for i in conditions:
        one_result, one_bool = check_the_json_meet_one_condition(i, json, target, [0])
        if one_bool:
            while len(relist) < len(one_result):  # 将总结果数扩充为已知结果数个数
                relist.append(copy.copy(relist[-1]))
            for j in range(len(relist)):  # 将当前条件的结果填入内容
                if len(one_result) > j:
                    relist[j].append(one_result[j])
                else:
                    relist[j].append(one_result[0])
        else:
            all_bools = False
            break
    return relist, all_bools


def check_the_json_meet_one_condition(condition, json, target, index):
    relist = [[]]
    all_bools = True
    tempjson = json
    ii = index[0]
    while True:
        if ii < len(condition):
            i = condition[ii]
            half_result = []
            if isinstance(i, list):
                if all_bools:
                    half_result, one_bool = check_the_json_meet_one_condition(i, tempjson, target, [0])
                    for i in half_result:
                        i.insert(0, '(')
                        i.append(')')
                    all_bools = one_bool
            elif i == '@and' or i == '@和':
                if all_bools:  # true
                    index[0] = ii + 1
                    half_result, one_bool = check_the_json_meet_one_condition(condition, json, target, index)
                    for j in half_result:
                        j.insert(0,i)
                    all_bools = one_bool
                    ii = index[0] - 1
            elif i == '@except' or i == '@除了':
                if all_bools:  # true
                    index[0] = ii + 1
                    half_result, one_bool = check_the_json_meet_one_condition(condition, json, target, index)
                    for j in half_result:
                        j.insert(0,i)
                    all_bools = not one_bool
                    ii = index[0] - 1
            elif i == '@or' or i == '@或':
                index[0] = ii + 1
                half_result, one_bool = check_the_json_meet_one_condition(condition, json, target, index)
                for j in half_result:
                    j.insert(0, i)
                all_bools = all_bools or one_bool
                ii = index[0] - 1
                if one_bool:
                    relist = relist + half_result
                    continue
            elif i == '@one':  # 在一系列数字作为key的键值中，选择第一个有效的项
                if all_bools:  # true
                    one_bool = False
                    jj = 0
                    while True:
                        jj += 1
                        j = str(jj)
                        if j in tempjson:
                            index[0] = ii + 1
                            one_half_result, one_half_bool = check_the_json_meet_one_condition(condition, tempjson[j], target, index)
                            if one_half_bool:
                                one_half_result[0] = [j] + one_half_result[0]
                                half_result.append(one_half_result[0])
                                one_bool = one_bool or one_half_bool
                            if one_bool:
                                break
                        else:
                            if jj > 1:
                                break
                    all_bools = one_bool
                    ii = index[0] - 1
            elif i == '@list':  # 在一系列数字作为key的键值中，选择所有有效的项
                if all_bools:  # true
                    one_bool = False
                    jj = 0
                    while True:
                        jj += 1
                        j = str(jj)
                        if j in tempjson:
                            index[0] = ii + 1
                            one_half_result, one_half_bool = check_the_json_meet_one_condition(condition, tempjson[j], target, index)
                            if one_half_bool:
                                one_half_result[0] = [j] + one_half_result[0]
                                half_result = half_result + one_half_result
                                one_bool = one_bool or one_half_bool
                        else:
                            if jj > 1:
                                break
                    all_bools = one_bool
                    ii = index[0] - 1
            elif i == '@has' or i == '@have':
                all_bools = isinstance(tempjson, str) and tempjson != ''
                half_result.append([i])
            elif i == '@hasnot' or i == '@havenot':
                all_bools = isinstance(tempjson, str) and tempjson == ''
                half_result.append([i])
            elif i[0] == '@':
                if len(condition) >= ii + 2:
                    if i == '@=' or i == '@==':
                        all_bools = operation_number_str_equal(tempjson, condition[ii + 1])
                    elif i == '@!=' or i == '@<>' or i == '@><':
                        all_bools = not operation_number_str_equal(tempjson, condition[ii + 1])
                    elif i == '@<' or i == '@<=' or i == '@>' or i == '@>=':
                        all_bools = operation_number_check(tempjson, condition[ii + 1], i[1:])
                    elif i == '@in':
                        all_bools = isinstance(tempjson, dict) and condition[ii + 1] in tempjson
                    elif i == '@notin':
                        all_bools = isinstance(tempjson, dict) and condition[ii + 1] not in tempjson
                    else:
                        raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在【检索】' + '→'.join(json) + '时，没有找到您输入的符号”' + i + '“请重新检查输入'))
                    ii += 1
                    half_result.append([i,condition[ii]])
                else:
                    raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在【检索】' + '→'.join(json) + '时，没有找到符号”' + i + '“后的值，请检查代码错误还是输入缺失'))
            else:
                if isinstance(tempjson, dict):
                    if i in tempjson:
                        for j in relist:
                            j.append(i)
                            tempjson = tempjson[i]
                    else:
                        all_bools = False
            if all_bools:
                k1 = len(relist)
                k2 = len(half_result)
                if k2 > 0:
                    combinejson = [0 for _ in range(k1 * k2)]
                    for m in range(k1):
                        for n in range(k2):
                            combinejson[m * k2 + n] = relist[m] + half_result[n]
                    relist = combinejson
            ii += 1
        else:
            break
    index[0] = ii
    return relist, all_bools


def change_json_to_condition_dict(json, target):
    redict = {}
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in json:
            if '符号' in json[i] and json[i]['符号'] != '':
                key = json[i]['符号']
                if json[i]['符号'] not in redict:
                    redict[key] = []
                redict[key].append(change_one_condition_dict(json[i], [0]))
        else:
            break
    if '函数' not in redict:
        redict['函数'] = [['']]
    if '满足' not in redict:
        raise (editerror(target[0], target[1], '→'.join(target[2:]) + '：\n在【检索】时没有找到“满足”的条件，请正确填写'))
    yingyong = True
    for i in redict['满足']:
        if i[0] == '应用':
            yingyong = False
            break
    if yingyong:
        redict['满足'].append(['应用', '@=', '1'])
    return redict


def change_one_condition_dict(json, index):
    relist = []
    while True:
        i = str(index[0])
        index[0] += 1
        if i in json:
            if json[i] == '(' or json[i] == '（':
                relist.append(change_one_condition_dict(json, index))
            elif json[i] == ')' or json[i] == '）':
                return relist
            elif json[i] == '':
                continue
            else:
                relist.append(json[i])
        else:
            return relist


# 通过符号检查两边的信息是否完全相等（会将内容)
def operation_number_str_equal(str1, str2):
    if isinstance(str1, dict) or isinstance(str2, dict):
        return False
    try:
        i1 = float(str1)
        i2 = float(str2)
        return i1 == i2
    except ValueError:
        i1 = str(str1)
        i2 = str(str2)
        return i1 == i2


# 通过符号检查两边的信息是否满足条件（必须是两个数字，否则返回false)
def operation_number_check(num1, num2, op):
    try:
        i1 = float(num1)
        i2 = float(num2)
        if op == '>':
            return i1 > i2
        elif op == '>=':
            return i1 >= i2
        elif op == '<':
            return i1 < i2
        elif op == '<=':
            return i1 <= i2
    except ValueError:
        return False


def number_to_string(number, rr=2):
    i = number
    try:
        if float(int(i)) == float(i):
            return str(int(i))
        else:
            return str(round(i, rr))
    except ValueError:
        return str(i)


# list、dict、sort
def expand_value_source_list_with_another_source_dict(l, d, s):
    lenl = len(l)
    lend = len(d)
    lenexd = pow(2, lend)  # 会多一个空dict
    lenexl = lenexd * lenl
    tempd = []  # lend
    exd = [{} for i in range(lenexd)]  # lenexd
    for i in d:
        tempd.append({i: d[i]})
    for i in range(lenexd):
        for j in range(lend):
            if i >> j & 1:
                exd[i].update(tempd[j])
    exl = []  # len=0，之后会append到lenexl
    for i in l:
        for j in exd:
            temp = copy.deepcopy(i)
            temp[1].update(j)
            exl.append(temp)
    lens = len(s)
    lenexs = pow(2, lens)
    temps = []
    exs = [{} for i in range(lenexs)]
    for i in s:
        temps.append({i: s[i]})
    for i in range(lenexs):
        for j in range(lens):
            if i >> j & 1:
                exs[i].update(temps[j])
    bitsum_list = [all_bit_sum(i) for i in range(lenexs)]
    sorteds = []
    for i in range(lens + 1):
        for j in range(lenexs):
            if bitsum_list[j] == i:
                sorteds.append(exs[j])
    rel = []
    for i in sorteds:
        for j in exl:
            if i == j[1]:
                rel.append(j)
                break
    return rel


def combine_numbers_post_level(arr, post='', level=0,round=4):
    re = ""
    if level > 0:
        if level < len(arr):
            re += better_float_to_text(arr[level],round)
        else:
            re += better_float_to_text(arr[0],round)
        if re[-1].isnumeric():
            re += post
    else:
        for i in range(len(arr)):
            if i > 0:
                if i % 8 == 0:
                    re += ' '
                re += "/"
            re += better_float_to_text(arr[i],round)
            if len(re)>0 and re[-1].isnumeric():
                re += post
    return re

def confirm_upgrade_info(arr):
    for i in arr:
        if len(arr[i]) > 0:
            for j in arr[i]['技能升级信息']:
                arr[i]['技能升级信息'][j]['中文名'] = arr[arr[i]['技能升级信息'][j]['技能名']]['中文名']
                arr[i]['技能升级信息'][j]['图片'] = arr[arr[i]['技能升级信息'][j]['技能名']]['迷你图片']


def create_file(all_json):
    for i in all_json:
        file = open("E:/json/pythonupload/" + i + '.json', mode="w")
        file.write(json.dumps(all_json[i]))
        file.close()


abilitypro_num = [["a_cast_range", "AbilityCastRange"]
    , ["a_cast_range_buff", "AbilityCastRangeBuffer"]
    , ["a_cast", "AbilityCastPoint"]
    , ["a_channel", "AbilityChannelTime"]
    , ["a_cool", "AbilityCooldown"]
    , ["a_duration", "AbilityDuration"]
    , ["a_damage", "AbilityDamage"]
    , ["a_mana", "AbilityManaCost"]
    , ["a_charges", "AbilityCharges"]
    , ["a_charges_restore_time", "AbilityChargeRestoreTime"]]
abilitypro_bool = [["immediate", "DOTA_ABILITY_BEHAVIOR_IMMEDIATE"]
    , ["ignore_channel", "DOTA_ABILITY_BEHAVIOR_IGNORE_CHANNEL"]]
ability_trait_level = [["中文名", "英文名", "代码", "传说", "描述", "天赋代码", "神杖信息", "魔晶信息", "注释"], ["效果", "属性", "施法前摇", "施法后摇", "冷却时间"], ["魔法消耗"]
    , ['技能免疫', '无敌', '技能抵挡', '技能反弹', '技能共享', '技能窃取', '幻象', '破坏', '持续施法', '躲避', '缠绕', '即时攻击', '视野', '真实视域', '独立机制']]
