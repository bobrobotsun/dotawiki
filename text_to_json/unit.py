import json
import copy
import math
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
    if i == -1:
        if inherit and pro[1] in unit_default:
            data[pro[1]] = unit_default[pro[1]]
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
            data[pro[1]] = {"1": pro[2][source[j + 1:k]]}
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


def fulfill_unit_json(base_txt, all_json, version,name_base):
    for i in all_json:
        all_json[i]["分类"] = "非英雄单位"
        all_json[i]["版本"] = version
        all_json[i]['曾用名'] = []
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
        for j in unitpro_txt + unitpro_num:
            popit = []
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
                            all_json[i][j[0]][k][str(l)] = all_json[i][j[0]][k]["代码"][str(l)]
                else:
                    if all_json[i][j[0]][k]["代码"]["2"] == "":
                        bool = True
                        for l in all_json[i]["代码名"]:
                            all_json[i][j[0]][k][l] = base_txt["非英雄单位"][all_json[i]["代码名"][l]][j[1]]["1"]
                            bool = bool and all_json[i][j[0]][k]["1"] == all_json[i][j[0]][k][l]
                        all_json[i][j[0]][k]['代码']['3'] = j[1]
                        if bool:
                            ll=2
                            while True:
                                l=str(ll)
                                ll+=1
                                if l in all_json[i][j[0]][k]:
                                    all_json[i][j[0]][k].pop(l)
                                else:
                                    break
                    else:
                        temp_daima=all_json[i][j[0]][k]["代码"]
                        for l in base_txt[temp_daima["1"]][temp_daima["2"]][temp_daima["3"]]:
                            all_json[i][j[0]][k][l] = base_txt[temp_daima["1"]][temp_daima["2"]][temp_daima["3"]][l]


def complete_upgrade(all_json, base_txt):
    for i in all_json:
        for jj in unitpro_txt + unitpro_num:
            j = jj[0]
            if isinstance(all_json[i][j],dict):
                one_upgrade(all_json[i][j], base_txt, i, j)

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
        ii=1
        while True:
            i=str(ii)
            ii+=1
            if i in json['1']:
                getvalue[0].append(json['1'][i])
            else:
                break
    else:
        getvalue[0].append(0)
        json["1"] = {}
        tempi='2'
        for tempj in json[tempi]:
            if not tempj.isnumeric() and tempj != '代码':
                json["1"][tempj] = copy.deepcopy(json[tempi][tempj])
    for ii in range(2,extra+2):
        i=str(ii)
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
                raise (editerror('非英雄单位', name, target + '没有找到《' + json[i]["代码"]["1"] + '→' + json[i]["代码"]["2"] + '》数据库中' + json[i]["代码"]["3"] + '的内容'))
        caloprate[ii]=json[i]["修正"]["1"]
    maxlen = 0
    for i in range(len(getvalue)):
        maxlen = max(maxlen, len(getvalue[i]))
    for i in range(len(getvalue)):
        for j in range(maxlen):
            if 0 < len(getvalue[i]) and len(getvalue[i]) <= j:
                getvalue[i].append(getvalue[i][j - 1])
    for i in range(len(calvalue)):
        calvalue[i] = copy.deepcopy(getvalue[0])
    #优先生效的修正
    while True:
        nowcheck=[0,0]
        for ii in range(2,extra+2):
            if len(caloprate[ii])>0 and caloprate[ii][0].isnumeric():
                nowcheck=[-1*int(caloprate[ii][0]),ii-1]
        if nowcheck[0]<0:
            for j in range(len(calvalue)):
                if j>>(nowcheck[1]-1)&1:
                    array_cal(calvalue[j], getvalue[nowcheck[1]+1], caloprate[nowcheck[1]+1][1:])
            caloprate[nowcheck[1] + 1]=''
        else:
            break
    for ii in range(2,extra+2):
        if len(caloprate[ii])>0 and not caloprate[ii][-1].isnumeric():
            for j in range(len(calvalue)):
                if j>>(ii-2)&1:
                    array_cal(calvalue[j], getvalue[ii], caloprate[ii])
            caloprate[ii] = ''
    if len(caloprate[1]) > 0:
        for j in range(len(calvalue)):
            array_cal(calvalue[j], getvalue[1], caloprate[1])
    while True:
        nowcheck = [0, 0]
        for ii in range(2,extra+2):
            if len(caloprate[ii])>0 and caloprate[ii][-1].isnumeric():
                nowcheck=[-1*int(caloprate[ii][-1]),ii-1]
        if nowcheck[0]<0:
            for j in range(len(calvalue)):
                if j>>(nowcheck[1]-1) & 1:
                    array_cal(calvalue[j], getvalue[nowcheck[1]+1], caloprate[nowcheck[1]+1][:-1])
            caloprate[nowcheck[1] + 1]=''
        else:
            break
    for i in range(len(calvalue)):
        if len(calvalue[i])>0:
            cut_the_same_to_one(calvalue[i])
    bitsum_list=[all_bit_sum(i) for i in range(pow(2, extra))]
    result_to_show_index=[]
    for i in range(extra+1):
        for j in range(len(bitsum_list)):
            if bitsum_list[j]==i:
                result_to_show_index.append(i)
    for i in range(len(calvalue)):
        for k in range(len(calvalue[result_to_show_index[i]])):
            json[str(i+1)][str(k+1)]=calvalue[result_to_show_index[i]][k]
        if bitsum_list[result_to_show_index[i]]>1:
            json[str(i+1)]["升级来源"]={}
            for j in range(extra):
                if result_to_show_index[i]>>j &1:
                    json[str(i + 1)]["升级来源"][str(len(json[str(i+1)]["升级来源"])+1)]=json[str(result_to_show_index[j+1]+1)]["升级来源"]['1']

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


unitpro_txt = [
    ["攻击类型", "CombatClassAttack", {"DOTA_COMBAT_CLASS_ATTACK_BASIC": "基础", "DOTA_COMBAT_CLASS_ATTACK_HERO": "英雄",
                                   "DOTA_COMBAT_CLASS_ATTACK_PIERCE": "穿刺", "DOTA_COMBAT_CLASS_ATTACK_SIEGE": "攻城"}]
    , ["护甲类型", "CombatClassDefend", {"DOTA_COMBAT_CLASS_DEFEND_BASIC": "基础", "DOTA_COMBAT_CLASS_DEFEND_HERO": "英雄",
                                     "DOTA_COMBAT_CLASS_DEFEND_STRUCTURE": "建筑"}]
    , ["近战远程", "AttackCapabilities",
       {"DOTA_UNIT_CAP_MELEE_ATTACK": "近战", "DOTA_UNIT_CAP_RANGED_ATTACK": "远程", "DOTA_UNIT_CAP_NO_ATTACK": "不攻击"}]
    , ["移动方式", "MovementCapabilities",
       {"DOTA_UNIT_CAP_MOVE_GROUND": "地面", "DOTA_UNIT_CAP_MOVE_FLY": "飞行", "DOTA_UNIT_CAP_MOVE_NONE": "不移动"}]
    , ["碰撞体积", "BoundsHullName",
       {"DOTA_HULL_SIZE_SMALL": 16, "DOTA_HULL_SIZE_REGULAR": 16, "DOTA_HULL_SIZE_HERO": 24,
        "DOTA_HULL_SIZE_TOWER": 144, "DOTA_HULL_SIZE_FILLER": 96, "DOTA_HULL_SIZE_BARRACKS": 144,
        "DOTA_HULL_SIZE_BUILDING": 81, "DOTA_HULL_SIZE_SIEGE": 16, "DOTA_HULL_SIZE_SMALLEST": 8,
        "DOTA_HULL_SIZE_HUGE": 80}]
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
               ]
unit_default = {"ConsideredHero": {"1": 0}, "IsSummoned": {"1": 0}, "ModelScale": {"1": 1}}
