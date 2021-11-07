import json
import copy
import math
from text_to_json import common_page, ability
from text_to_json.WikiError import editerror


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


# 查询数据范围
def findtb(source, start, end, tb, brace=0):
    i = j = 0
    tb[0] = start
    tb[1] = end
    for i in range(start, end):
        if source[i] == '{':
            brace += 1
            if brace > 0:
                tb[0] = i + 1
                for j in range(i + 1, tb[1]):
                    if source[j] == '{':
                        brace += 1
                    elif source[j] == '}':
                        brace -= 1
                        if brace == 0:
                            tb[1] = j - 1
                            return True
        elif source[i] == '}':
            return False
    return False


def findunitname(source, tb):
    i = source.rfind('\"', 0, tb[0])
    j = source.rfind('\"', 0, i - 1)
    return source[j + 10:i]


# 寻找属性（查询源字符串，数据存储位置，上下限，属性序数，是否继承默认数据）
def findunitpro(source, data, tb, pro, inherit=True, number=True):
    i = source.find('\"' + pro[1] + '\"', tb[0], tb[1])
    proname=pro[1]
    if len(pro)>3:
        proname=pro[3]
    if i == -1:
        if inherit and proname in unit_default:
            data[proname] = unit_default[proname]
    else:
        j = source.find('\"', i + 1, tb[1])
        j = source.find('\"', j + 1, tb[1])
        k = source.find('\"', j + 1, tb[1])
        if number:
            if source[j + 1:k] == '':
                data[pro[1]] = {"1": 0}
            else:
                data[pro[1]] = {"1": float(source[j + 1:k])}
        else:
            data[proname] = {"1": pro[2][source[j + 1:k]]}
    return


def get_hero_data_from_txt(base_txt, address):
    ffile = open(address, mode="r")
    source_string = ffile.read()
    tb = [0, 0]
    findtb(source_string, 0, len(source_string), tb, -1)
    for i in unitpro_txt:
        findunitpro(source_string, unit_default, tb, i, False, False)
    for i in unitpro_num:
        findunitpro(source_string, unit_default, tb, i, False, True)
    while True:
        if findtb(source_string, tb[1] + 2, len(source_string), tb, 0):
            name = findunitname(source_string, tb)
            base_txt[name] = {}
            for i in unitpro_txt:
                findunitpro(source_string, base_txt[name], tb, i, True, False)
            for i in unitpro_num:
                findunitpro(source_string, base_txt[name], tb, i, True, True)
        else:
            break


def fulfill_unit_json(base_txt, all_json, version, name_base):
    for i in all_json:
        all_json[i]["页面名"] = i
        all_json[i]["分类"] = "非英雄单位"
        all_json[i]["版本"] = version
        all_json[i]['曾用名'] = []
        if i in name_base:
            for namej in name_base[i]:
                if namej != i:
                    all_json[i]['曾用名'].append(namej)
        for namei in name_base:
            if namei != all_json[i]['页面名']:
                for namej in name_base[namei]:
                    if namej[0] == all_json[i]['页面名']:
                        all_json[i]['曾用名'].append(namei)
        if len(all_json[i]['图片']) > 1:
            all_json[i]['图片'] = all_json[i]['图片'][0].upper() + all_json[i]['图片'][1:]
            all_json[i]['图片'] = all_json[i]['图片'].replace(' ', '_')
        if len(all_json[i]['迷你图片']) > 1:
            all_json[i]['迷你图片'] = all_json[i]['迷你图片'][0].upper() + all_json[i]['迷你图片'][1:]
            all_json[i]['迷你图片'] = all_json[i]['迷你图片'].replace(' ', '_')
        if '手填标签' not in all_json[i]:
            all_json[i]['手填标签'] = {}
        if '标签' not in all_json[i]:
            all_json[i]['标签'] = []
        for j in unitpro_txt + unitpro_num:
            popit = []
            if j[0] not in all_json[i]:
                all_json[i][j[0]] = {'1': {'代码': {'0': '', '1': '', '2': '', '3': ''}, '修正': {'1': ''}}}
            for k in all_json[i][j[0]]:
                if k != "代码" and k != "1" and k != '修正':
                    popit.append(k)
            for k in popit:
                all_json[i][j[0]].pop(k)
            for k in all_json[i][j[0]]:
                if "0" in all_json[i][j[0]][k]["代码"] and all_json[i][j[0]][k]["代码"]["0"] == "手填":
                    l = 0
                    while True:
                        l += 1
                        if str(l) in all_json[i][j[0]][k]["代码"]:
                            all_json[i][j[0]][k][str(l)] = change_str_to_int(all_json[i][j[0]][k]["代码"][str(l)])
                        else:
                            break
                else:
                    if all_json[i][j[0]][k]["代码"]["2"] == "":
                        bool = True
                        proname=j[3] if len(j)>3 else j[1]
                        for l in all_json[i]["代码名"]:
                            all_json[i][j[0]][k][l] = base_txt["非英雄单位"][all_json[i]["代码名"][l]][proname]["1"]
                            bool = bool and all_json[i][j[0]][k]["1"] == all_json[i][j[0]][k][l]
                        all_json[i][j[0]][k]['代码']['3'] = proname
                        if bool:
                            ll = 2
                            while True:
                                l = str(ll)
                                ll += 1
                                if l in all_json[i][j[0]][k]:
                                    all_json[i][j[0]][k].pop(l)
                                else:
                                    break
                    else:
                        temp_daima = all_json[i][j[0]][k]["代码"]
                        for l in base_txt[temp_daima["1"]][temp_daima["2"]][temp_daima["3"]]:
                            all_json[i][j[0]][k][l] = base_txt[temp_daima["1"]][temp_daima["2"]][temp_daima["3"]][l]


def complete_upgrade(all_json, base_txt):
    for i in all_json:
        for jj in unitpro_txt + unitpro_num:
            j = jj[0]
            if isinstance(all_json[i][j], dict):
                one_upgrade(all_json[i][j], base_txt, i, j, all_json)


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


def one_upgrade(json, base_txt, name, target, all_json):
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
        ii = 1
        while True:
            i = str(ii)
            ii += 1
            if i in json['1']:
                getvalue[0].append(json['1'][i])
            else:
                break
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
                edits = [json["1"]["修正"]["2"], json["1"]["修正"]["3"], json["1"]["修正"]["4"]]
                if edits[0] == '':
                    edits[0] = '非英雄单位'
                if edits[1] == '':
                    edits[1] = name
                if edits[1] in base_txt[edits[0]]:
                    if edits[2] in base_txt[edits[0]][edits[1]]:
                        for k in base_txt[edits[0]][edits[1]][edits[2]]:
                            getvalue[1].append(base_txt[edits[0]][edits[1]][edits[2]][k])
                    else:
                        raise (editerror('非英雄单位', name, target + '没有找到《' + '→'.join(edits) + '》的内容'))
                elif edits[1] in all_json:
                    for l in all_json[edits[1]]["代码名"]:
                        if edits[2] in base_txt['非英雄单位'][all_json[edits[1]]["代码名"][l]]:
                            getvalue[1].append(base_txt['非英雄单位'][all_json[edits[1]]["代码名"][l]][edits[2]]['1'])
                        else:
                            raise (editerror('非英雄单位', name, target + '没有找到《' + '→'.join(edits) + '》的内容'))
                else:
                    raise (editerror('非英雄单位', name, target + '没有找到《' + '→'.join(edits) + '》的内容'))
    elif '2' in json:
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
                    getvalue[ii].append(change_str_to_int(json[i]["代码"][str(k)]))
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
                raise (editerror('非英雄单位', name, target + '没有找到《' + json[i]["代码"]["1"] + '→' + json[i]["代码"]["2"] + '》数据库中' + json[i]["代码"]["3"] + '的内容'))
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
                    array_cal(calvalue[j], getvalue[nowcheck[1] + 1], caloprate[nowcheck[1] + 1][1:])
            caloprate[nowcheck[1] + 1] = ''
        else:
            break
    for ii in range(2, extra + 2):
        if len(caloprate[ii]) > 0 and not caloprate[ii][-1].isnumeric():
            for j in range(len(calvalue)):
                if j >> (ii - 2) & 1:
                    array_cal(calvalue[j], getvalue[ii], caloprate[ii])
            caloprate[ii] = ''
    if len(caloprate[1]) > 0:
        for j in range(len(calvalue)):
            array_cal(calvalue[j], getvalue[1], caloprate[1])
    while True:
        nowcheck = [0, 0]
        for ii in range(2, extra + 2):
            if len(caloprate[ii]) > 0 and caloprate[ii][-1].isnumeric():
                nowcheck = [-1 * int(caloprate[ii][-1]), ii - 1]
        if nowcheck[0] < 0:
            for j in range(len(calvalue)):
                if j >> (nowcheck[1] - 1) & 1:
                    array_cal(calvalue[j], getvalue[nowcheck[1] + 1], caloprate[nowcheck[1] + 1][:-1])
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
                temp = float(arr2[0])
            except ValueError:
                temp = arr2[0]
        if opp == '=':
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


def create_file(all_json):
    for i in all_json:
        file = open("E:/json/pythonupload/" + i + '.json', mode="w")
        file.write(json.dumps(all_json[i]))
        file.close()


def fulfil_complex_and_simple_show(all_json,html_function):
    for i in all_json['非英雄单位']:
        db = all_json['非英雄单位'][i]
        db['标签'] = []
        if db["召唤物"]["1"]["1"] == 1 and '召唤物' not in db['手填标签'].values():
            db['手填标签'][str(len(db['手填标签'])+1)]='召唤物'
        if db["类型"] != '' and db["类型"] not in db['手填标签'].values():
            db['手填标签'][str(len(db['手填标签'])+1)]=db["类型"]
        if db["单位关系类型"]["1"]["1"] != '默认' and db["单位关系类型"]["1"]["1"] != '' and db["单位关系类型"]["1"]["1"] not in db['手填标签'].values():
            db['手填标签'][str(len(db['手填标签'])+1)]=db["单位关系类型"]["1"]["1"]
        for k in db['手填标签']:
            if db['手填标签'][k] != '':
                db['标签'].append(db['手填标签'][k])
        db['标签'].append('非英雄单位')
        bt = ''  # 完整显示
        st = ''  # 缩略显示
        bt='<table class="infobox" style="text-align:center;background:#222;width:300px;color:#fff;margin-top:12px;margin-right:12px;">' \
           '<tr class="infobox-title"><th colspan=2 style="background:#000;padding:8px 16px 0 16px;text-align:center;">' \
           '<span id="'+db['页面名']+'" style="font-size:36px;"> ' \
           + common_page.get_unit_value(db["中文名"]) + ' </span><br><span style="font-size:24px;text-align:center;"> '\
           +common_page.get_unit_value(db["英文名"])+' </span></th></tr><tr><td class="dota_unit_simple_infobox_label" colspan=2>'
        st += '<div class="dota_simple_infobox"><div style="text-align:center;min-height:100px">' \
              '<div class="bg-primary" style="float:left;">' \
              '<span class="dota_get_image_by_json_name" data-json-name="'+i+'" data-image-height="100" data-image-link="1" data-image-center="1"></span></div>'\
              +'<div class="bg-primary" style="font-size:200%;font-weight:normal;padding:0.25em;">[['+db["页面名"]+'|'+common_page.get_unit_value(db["中文名"])+']]</div>'\
              +'<div class="bg-primary" style="font-size:150%;padding:0.25em;text-align:center;"> '+common_page.get_unit_value(db["英文名"])+' </div><div style="padding:0.25em;">'
        if db["英雄级单位"]['1']['1'] == 1:
            bt += '<span class="label bg-primary">英雄级</span>'
            st += '<span class="ability_indicator bg-primary">英雄级</span>'
            db['标签'].append('英雄级单位')
        else:
            bt += '<span class="label bg-default">非英雄级</span>'
            st += '<span class="ability_indicator bg-default">非英雄级</span>'
        if db["单位关系类型"]['1']['1'] == '守卫':
            bt += ' <span class="label bg-warning">守卫</span>'
            st += ' <span class="ability_indicator bg-warning">守卫</span>'
            db['标签'].append('守卫')
        else:
            bt += ' <span class="label bg-default">非守卫</span>'
            st += ' <span class="ability_indicator bg-default">非守卫</span>'
        if db["远古单位"]['1']['1'] == 1:
            bt += ' <span class="label bg-warning">远古</span>'
            st += ' <span class="ability_indicator bg-warning">远古</span>'
            db['标签'].append('远古单位')
        else:
            bt += ' <span class="label bg-default">非远古</span>'
            st += ' <span class="ability_indicator bg-default">非远古</span>'
        if db["生命类型"] == '攻击次数':
            bt += ' <span class="label bg-warning">攻击次数型</span>'
            st += ' <span class="ability_indicator bg-warning">攻击次数型</span>'
            db['标签'].append('攻击次数型生命值')
        else:
            bt += ' <span class="label bg-default">生命值型</span>'
            st += ' <span class="ability_indicator bg-default">生命值型</span>'
        if db["中立生物"]["1"]["1"] == 1:
            db['标签'].append('中立生物')
        bt += '</td></tr>' \
              '<tr><td colspan=2 style="background:#fff"><div class="center">'
        st += '</div></div>' \
              '<div style="display:flex;flex-wrap:wrap;justify-content:space-around;">'
        if db['图片'] != '':
            bt+= '{{图片|' + db['图片'] + '|w200|link=' + i + '|center}}'
        bt+='</div></td></tr>'
        btlist = [['等级', [['等级']]], ['奖励金钱', [['金钱下限', '金钱上限']]], ['奖励经验', [['经验']]], ['生命值', [['生命值']]], ['英雄攻击', [['英雄攻击伤害']]], ['非英雄攻击', [['非英雄攻击伤害']]]
            , ['魔法值', [['魔法值']]], ['生命恢复', [['生命恢复']]], ['魔法恢复', [['魔法恢复']]], ['攻击力<br>(攻击类型)', [['攻击下限', '攻击上限']], '<br>（', [['攻击类型']], '）']
            , ['攻击距离+<br>不中断距离', [['攻击距离']], '+', [['攻击距离缓冲']]], ['攻击前摇', [['攻击前摇']]], ['基础攻击间隔', [['攻击间隔']]], ['攻击速度', [['攻击速度']]]
            , ['远近程', [['近战远程']]], ['警觉范围', [['警戒范围']]], ['攻击欲望', [['攻击欲望']]], ['弹道速度', [['弹道速度']]]
            , ['护甲<br>(护甲类型)', [['护甲']], '<br>（', [['护甲类型']], '）'], ['魔法抗性', [['魔法抗性'], lambda x: '%']]
            , ['移动速度', [['移动速度']]], ['移动类型', [['移动方式']]], ['转身速率', [['转身速率']]], ['跟随距离', [['跟随距离']]]
            , ['白天视野', [['白天视野']]], ['夜晚视野', [['夜晚视野']]], ['碰撞体积', [['碰撞体积']]], ['边界体积', [['边界体积']]], ['模型大小', [['模型比例']]]]
        btlabel = 'style="width:30%;border:1px solid white;padding:0px 8px;background:#000;text-align:right;"'
        btdata = 'style="border:1px solid white;padding:0px 8px;background:#000;text-align:left;"'
        for ii in btlist:
            if len(db[ii[1][0][0]]) > 0:
                bt += '<tr><td ' + btlabel + '>' + ii[0] + '</td><td ' + btdata + '>'
                for j in range(1, len(ii)):
                    if j % 2 == 1:
                        if len(ii[j][0]) == 1:
                            if len(ii[j]) == 1:
                                bt += common_page.create_upgrade_text(db, ii[j][0][0])
                            else:
                                bt += common_page.create_upgrade_text(db, ii[j][0][0], ii[j][1])
                        else:
                            if len(i[j]) == 1:
                                bt += common_page.get_unit_upgrade_double(db[ii[j][0][0]], db[ii[j][0][1]])
                            else:
                                bt += common_page.get_unit_upgrade_double(db[ii[j][0][0]], db[ii[j][0][1]], ii[j][1])
                    else:
                        bt += ii[j]
                bt += '</td></tr>'
        bt += '<tr><td colspan=2 style="background:#000;text-align:left;"><div class="adminpanel">\'\'\'' \
              '<span class="dota_create_link_to_wiki_page" data-link-page-name="data:' + db["页面名"] \
              + '.json">J</span> <span class="dota_create_link_to_wiki_page" data-link-page-name="' + db["页面名"] + '">P</span>\'\'\'</div></td></tr></table>'\
              +'<div class="dota_invisible_menu_item_at_right_of_the_screen">[[#' + db["页面名"] + '|' + db["页面名"] + ']]</div>'
        st_flex_list=[['等级','',['等级'],''],['生命值','',['生命值'],''],['生命恢复','',['生命恢复'],''],['魔法值','',['魔法值'],''],['魔法恢复','',['魔法恢复'],'']
                ,['攻击力','攻击类型',['攻击下限','攻击上限'],''],['攻击间隔','',['攻击间隔'],''],['攻击距离','近战远程',['攻击距离'],'']]
        if db['生命类型']=='生命值':
            st_flex_list+=[['护甲','护甲类型',['护甲'],''],['魔法抗性','',['魔法抗性'],'%']]
        elif db['生命类型']=='攻击次数':
            st_flex_list+=[['英雄攻击伤害','',['英雄攻击伤害'],''],['非英雄攻击伤害','',['非英雄攻击伤害'],'']]
        st_flex_list +=[['移动速度','',['移动速度'],''],['白天视野','',['白天视野'],''],['夜晚视野','',['夜晚视野'],''],['金钱','',['金钱下限','金钱上限'],''],['经验','',['经验'],'']]
        for j in st_flex_list:
            st+=flex_div(j[0],j[1],db,j[2],j[3])
        st+='</div><div style="display:flex;flex-wrap:wrap;justify-content:space-around;">'
        if len(db['技能'])>0:
            st+='<div class="border_white" style="padding:0.25em;flex-grow:1;"><div>拥有技能：</div>'
            for j in db['技能']:
                st += unit_ability_image_with_click_infomation(j,'简易展示')
            st+='</div>'
        if '1' in db['源技能']:
            st+='<div class="border_white" style="padding:0.25em;flex-grow:1;"><div>源技能：</div>'
            for j in db['源技能']:
                if db['源技能'][j] in all_json['技能'] and all_json['技能'][db['源技能'][j]]['应用']==db['应用']:
                    st += unit_ability_image_with_click_infomation(db['源技能'][j],'简易展示')
            st+='</div>'
        unitgroup = []
        for j,w in all_json['单位组'].items():
            if i in w['全部单位']:
                unitgroup.append(j)
        if len(unitgroup) > 0:
            st+='<div class="border_white" style="padding:0.25em;flex-grow:1;"><div>所属单位组：</div>'
            for j in unitgroup:
                st += unit_ability_image_with_click_infomation(j,'成员，1，简易展示')
            st+='</div>'
        st+='</div></div>'
        db['简易展示'] = html_function(st)
        db['具体展示'] = html_function(bt)

def flex_div(name,name2,db,strtar,post):
    nickname=common_page.create_upgrade_text(db, name2, lambda x: post, lambda x, y: '<br>' if str(1 + int(y)) in x else '')
    value=''
    if nickname!='':
        nickname='('+nickname+')'
    if len(strtar)==1:
        value=common_page.create_upgrade_text(db, strtar[0], lambda x: post, lambda x, y: '<br>' if str(1 + int(y)) in x else '')
        if value=='':
            return ''
    elif len(strtar)==2:
        if db[strtar[0]] and db[strtar[1]]:
            value=change_double_combine_numbers_to_str(db[strtar[0]],db[strtar[1]])
        else:
            return ''
    return '<div style="padding:0.25em;flex-grow:1;"><div class="bgc_white">'+name+nickname+'</div><div class="border_white">'+value+'</div></div>'

def unit_ability_image_with_click_infomation(name,tar):
    retxt='<span class="dota_click_absolute_additional_infomation_frame dota_click_find_text_in_json_and_show">' \
            '<span class="dota_get_image_by_json_name dota_click_absolute_additional_infomation_frame_button" data-json-name="' + name \
            + '" data-image-height="40"></span>' \
            '<div class="dota_click_absolute_additional_infomation_frame_frame dota_click_find_text_in_json_and_show_textarea">' \
            '<div class="dota_click_find_text_in_json_and_show_button" data-find-text-in-json-address="' + name + '，'+tar+'">点击显示《' \
            + name + '》详细信息</div></div></span>'
    return retxt

def change_combine_numbers_to_str(s1, s2, post=''):
    return common_page.create_upgrade_text(s1, s2, lambda x: post, lambda x, y: '<br>' if str(1 + int(y)) in x else '')


def change_double_combine_numbers_to_str(slist1, slist2):
    return common_page.get_unit_upgrade_double(slist1, slist2)


unitpro_txt = [
    ["攻击类型", "CombatClassAttack", {"DOTA_COMBAT_CLASS_ATTACK_BASIC": "基础", "DOTA_COMBAT_CLASS_ATTACK_HERO": "英雄",
                                   "DOTA_COMBAT_CLASS_ATTACK_PIERCE": "穿刺", "DOTA_COMBAT_CLASS_ATTACK_SIEGE": "攻城"}]
    , ["护甲类型", "CombatClassDefend", {"DOTA_COMBAT_CLASS_DEFEND_BASIC": "基础", "DOTA_COMBAT_CLASS_DEFEND_HERO": "英雄",
                                     "DOTA_COMBAT_CLASS_DEFEND_STRUCTURE": "建筑"}]
    , ["近战远程", "AttackCapabilities",
       {"DOTA_UNIT_CAP_MELEE_ATTACK": "近战", "DOTA_UNIT_CAP_RANGED_ATTACK": "远程", "DOTA_UNIT_CAP_NO_ATTACK": "不攻击"}]
    , ["移动方式", "MovementCapabilities",
       {"DOTA_UNIT_CAP_MOVE_GROUND": "地面", "DOTA_UNIT_CAP_MOVE_FLY": "飞行", "DOTA_UNIT_CAP_MOVE_NONE": "不移动"}]
    , ["单位关系类型", "UnitRelationshipClass",
       {"DOTA_NPC_UNIT_RELATIONSHIP_TYPE_DEFAULT": "默认", "DOTA_NPC_UNIT_RELATIONSHIP_TYPE_WARD": "守卫", "DOTA_NPC_UNIT_RELATIONSHIP_TYPE_ATTACHED": "附着物"
           , "DOTA_NPC_UNIT_RELATIONSHIP_TYPE_COURIER": "信使", 'DOTA_NPC_UNIT_RELATIONSHIP_TYPE_BUILDING': '建筑', 'DOTA_NPC_UNIT_RELATIONSHIP_TYPE_BARRACKS': '兵营'
           , 'DOTA_NPC_UNIT_RELATIONSHIP_TYPE_SIEGE': '投石车'}]
    , ["碰撞体积", "BoundsHullName",
       {"DOTA_HULL_SIZE_BUILDING": 314, "DOTA_HULL_SIZE_BARRACKS": 161, "DOTA_HULL_SIZE_TOWER": 144,
        "DOTA_HULL_SIZE_FILLER": 112, "DOTA_HULL_SIZE_HUGE": 80,
        "DOTA_HULL_SIZE_HERO": 28, "DOTA_HULL_SIZE_REGULAR": 36, "DOTA_HULL_SIZE_SIEGE": 40,
        "DOTA_HULL_SIZE_SMALL": 18, "DOTA_HULL_SIZE_SMALLEST": 4
        }]
    , ["边界体积", "BoundsHullName",
       {"DOTA_HULL_SIZE_BUILDING": 298, "DOTA_HULL_SIZE_BARRACKS": 144, "DOTA_HULL_SIZE_TOWER": 144,
        "DOTA_HULL_SIZE_FILLER": 96, "DOTA_HULL_SIZE_HUGE": 80,
        "DOTA_HULL_SIZE_HERO": 24, "DOTA_HULL_SIZE_REGULAR": 16, "DOTA_HULL_SIZE_SIEGE": 16,
        "DOTA_HULL_SIZE_SMALL": 8, "DOTA_HULL_SIZE_SMALLEST": 2
        },'BoundsHullName2']
]
unitpro_num = [["远古单位", "IsAncient"]
    , ["中立生物", "IsNeutralUnitType"]
    , ["英雄级单位", "ConsideredHero"]
    , ["召唤物", "IsSummoned"]
    , ["等级", "Level"]
    , ["攻击上限", "AttackDamageMax"]
    , ["攻击下限", "AttackDamageMin"]
    , ["攻击间隔", "AttackRate"]
    , ["攻击前摇", "AttackAnimationPoint"]
    , ["警戒范围", "AttackAcquisitionRange"]
    , ["攻击距离", "AttackRange"]
    , ["攻击距离缓冲", "AttackRangeBuffer"]
    , ["弹道速度", "ProjectileSpeed"]
    , ["经验", "BountyXP"]
    , ["金钱下限", "BountyGoldMin"]
    , ["金钱上限", "BountyGoldMax"]
    , ["移动速度", "MovementSpeed"]
    , ["转身速率", "MovementTurnRate"]
    , ["跟随距离", "FollowRange"]
    , ["护甲", "ArmorPhysical"]
    , ["魔法抗性", "MagicalResistance"]
    , ["生命值", "StatusHealth"]
    , ["生命恢复", "StatusHealthRegen"]
    , ["魔法值", "StatusMana"]
    , ["魔法恢复", "StatusManaRegen"]
    , ["白天视野", "VisionDaytimeRange"]
    , ["夜晚视野", "VisionNighttimeRange"]
    , ["攻击欲望", "AttackDesire"]
    , ["模型比例", "ModelScale"]
    , ["英雄攻击伤害", "StatusHealth"]
    , ["非英雄攻击伤害", "StatusHealth"]
    , ["攻击速度", "BaseAttackSpeed"]
               ]
unit_default = {"ConsideredHero": {"1": 0}, "IsSummoned": {"1": 0}, "ModelScale": {"1": 1}, "BaseAttackSpeed": {"1": 100}}
