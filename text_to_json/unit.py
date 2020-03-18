import json
import os
import copy
import hashlib


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


def get_hero_data_from_txt(base_txt,address):
    ffile = open("E:/Steam/steamapps/common/dota 2 beta/game/dota/scripts/npc/npc_units.txt", mode="r")
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


def fulfill_unit_json(base_txt, all_json,version):
    for i in all_json:
        all_json[i]["分类"] = "非英雄单位"
        all_json[i]["版本"] = version
        all_json[i]["应用"] = 1
        if len(all_json[i]['图片'])>1:
            all_json[i]['图片']=all_json[i]['图片'][0].upper()+all_json[i]['图片'][1:]
            all_json[i]['图片']=all_json[i]['图片'].replace(' ','_')
        if len(all_json[i]['迷你图片'])>1:
            all_json[i]['迷你图片']=all_json[i]['迷你图片'][0].upper()+all_json[i]['迷你图片'][1:]
        md5 = hashlib.md5()
        md5.update(all_json[i]['图片'].encode('utf-8'))
        all_json[i]['图片地址'] = md5.hexdigest()
        md5 = hashlib.md5()
        md5.update(all_json[i]['迷你图片'].encode('utf-8'))
        all_json[i]['迷你图片地址'] = md5.hexdigest()

        for j in unitpro_txt + unitpro_num:
            popit = []
            for k in all_json[i][j[0]]:
                if k != "代码" and k != "1":
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
                        if bool:
                            all_json[i][j[0]][k] = {"代码": {"1": all_json[i][j[0]][k]["代码"]["1"], "2": all_json[i][j[0]][k]["代码"]["2"], "3": all_json[i][j[0]][k]["代码"]["3"]},
                                                    "1": all_json[i][j[0]][k]["1"]}
                    else:
                        if "修正" in all_json[i][j[0]][k] and all_json[i][j[0]][k]["修正"]["1"] == '=':
                            for l in base_txt[all_json[i][j[0]][k]["代码"]["1"]][all_json[i][j[0]][k]["代码"]["2"]][all_json[i][j[0]][k]["代码"]["3"]]:
                                all_json[i][j[0]][k][l] = base_txt[all_json[i][j[0]][k]["代码"]["1"]][all_json[i][j[0]][k]["代码"]["2"]][all_json[i][j[0]][k]["代码"]["3"]][l]


def complete_upgrade(all_json, base_txt):
    for i in all_json:
        for jj in unitpro_txt + unitpro_num:
            j = jj[0]
            inbool = ["2" in all_json[i][j], "3" in all_json[i][j]]
            inbool.append(inbool[0] and inbool[1])
            inbool.append(inbool[0] or inbool[1])
            if inbool[3]:
                getvalue = [[], [], []]
                calvalue = [[], [], []]
                caloprate = [[], []]
                k = 0
                while True:
                    k += 1
                    if str(k) in all_json[i][j]["1"]:
                        getvalue[0].append(all_json[i][j]["1"][str(k)])
                    else:
                        break
                if inbool[0]:
                    if "0" in all_json[i][j]["2"]["代码"] and all_json[i][j]["2"]["代码"]["0"] == "手填":
                        k = 0
                        while True:
                            k += 1
                            if str(k) in all_json[i][j]["2"]["代码"]:
                                getvalue[1].append(all_json[i][j]["2"]["代码"][str(k)])
                            else:
                                break
                    else:
                        for k in base_txt[all_json[i][j]["2"]["代码"]["1"]][all_json[i][j]["2"]["代码"]["2"]][all_json[i][j]["2"]["代码"]["3"]]:
                            getvalue[1].append(base_txt[all_json[i][j]["2"]["代码"]["1"]][all_json[i][j]["2"]["代码"]["2"]][all_json[i][j]["2"]["代码"]["3"]][k])
                    k = 0
                    while True:
                        k += 1
                        if str(k) in all_json[i][j]["2"]["修正"]:
                            caloprate[0].append(all_json[i][j]["2"]["修正"][str(k)])
                        else:
                            break
                if inbool[1]:
                    if "0" in all_json[i][j]["3"]["代码"] and all_json[i][j]["3"]["代码"]["0"] == "手填":
                        k = 0
                        while True:
                            k += 1
                            if str(k) in all_json[i][j]["3"]["代码"]:
                                getvalue[2].append(all_json[i][j]["3"]["代码"][str(k)])
                            else:
                                break
                    else:
                        for k in base_txt[all_json[i][j]["3"]["代码"]["1"]][all_json[i][j]["3"]["代码"]["2"]][all_json[i][j]["3"]["代码"]["3"]]:
                            getvalue[2].append(base_txt[all_json[i][j]["3"]["代码"]["1"]][all_json[i][j]["3"]["代码"]["2"]][all_json[i][j]["3"]["代码"]["3"]][k])
                    k = 0
                    while True:
                        k += 1
                        if str(k) in all_json[i][j]["3"]["修正"]:
                            caloprate[1].append(all_json[i][j]["3"]["修正"][str(k)])
                        else:
                            break
                calvalue[0] = copy.deepcopy(getvalue[0])
                calvalue[1] = copy.deepcopy(getvalue[0])
                calvalue[2] = copy.deepcopy(getvalue[0])
                if inbool[0]:
                    array_cal(calvalue[0], getvalue[1], caloprate[0])
                    array_cal(calvalue[2], getvalue[1], caloprate[0])
                if inbool[1]:
                    array_cal(calvalue[1], getvalue[2], caloprate[1])
                    array_cal(calvalue[2], getvalue[2], caloprate[1])
                if inbool[0]:
                    for k in range(len(calvalue[0])):
                        all_json[i][j]["2"][str(k + 1)] = calvalue[0][k]
                if inbool[1]:
                    for k in range(len(calvalue[1])):
                        all_json[i][j]["3"][str(k + 1)] = calvalue[1][k]
                if inbool[2]:
                    all_json[i][j]["4"] = {}
                    for k in range(len(calvalue[2])):
                        all_json[i][j]["4"][str(k + 1)] = calvalue[2][k]
                    all_json[i][j]["4"]["升级来源"] = copy.deepcopy(all_json[i][j]["3"]["升级来源"])


def array_cal(arr1, arr2, op):
    for i in range(len(arr1)):
        if i < len(arr2):
            temp = arr2[i]
        else:
            temp = arr2[0]
        if op[0] == '=':
            arr1[i] = temp
        elif op[0] == '+':
            arr1[i] = arr1[i] + temp
        elif op[0] == '\\-':
            arr1[i] = temp - arr1[i]
        elif op[0] == '*':
            arr1[i] = arr1[i] * temp
        elif op[0] == '/':
            arr1[i] = arr1[i] / temp
        elif op[0] == '\\':
            arr1[i] = temp / arr1[i]
        elif op[0] == '%-':
            arr1[i] = arr1[i] * (100 - temp) / 100
        elif op[0] == '%+':
            arr1[i] = arr1[i] * (100 + temp) / 100
        elif op[0] == '-%':
            arr1[i] = arr1[i] * (1 - temp)
        elif op[0] == '=-':
            arr1[i] = temp - op[1]
        elif op[0] == '=+':
            arr1[i] = temp + op[1]
        elif op[0] == '=*':
            arr1[i] = temp * op[1]
        elif op[0] == '=/':
            arr1[i] = temp / op[1]


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
