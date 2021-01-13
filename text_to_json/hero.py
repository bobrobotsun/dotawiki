import json
import hashlib
import re
import copy
from text_to_json.WikiError import editerror

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


def findheroname(source, tb):
    i = source.rfind('\"', 0, tb[0])
    j = source.rfind('\"', 0, i - 1)
    return source[j + 15:i]


# 寻找属性（查询源字符串，数据存储位置，统一数据库，上下限，属性序数，是否继承默认数据）
def findheropro(source, data, tb, pro, inherit=True, number=True, splitit=False):
    if pro[0] in data:
        return
    else:
        i = source.find('\"' + pro[1] + '\"', tb[0], tb[1])
        if i == -1:
            if inherit:
                data[pro[1]] = hero_default[pro[1]]
        else:
            j = source.find('\"', i + 1, tb[1])
            j = source.find('\"', j + 1, tb[1])
            k = source.find('\"', j + 1, tb[1])
            if splitit:
                rolesplit = source[j + 1:k].split(',')
                data[pro[1]] = {}
                if number:
                    for j in range(len(rolesplit)):
                        data[pro[1]][str(j + 1)] = float(rolesplit[j])
                else:
                    for j in range(len(rolesplit)):
                        data[pro[1]][str(j + 1)] = pro[2][rolesplit[j]]
            elif len(pro) == 3:
                data[pro[1]] = {"1": pro[2][source[j + 1:k]]}
            else:
                if number:
                    data[pro[1]] = {"1": float(source[j + 1:k])}
                else:
                    data[pro[1]] = {"1": source[j + 1:k]}
    return

def get_lore_data_from_vpk(base_txt,ffile):
    this_string = ffile.read().decode('utf8')
    alltext = re.finditer('"npc_dota_hero_(.*?)_bio".*?"((.|\n)*?)"', this_string)
    for i in alltext:
        name=i.group(1)
        if name in base_txt:
            base_txt[name]['lore']={'1':i.group(2)}

def get_dota_data_from_vpk(base_txt,ffile):
    this_string = ffile.read().decode('utf8')
    alltext = re.finditer('"npc_dota_hero_(.*?)_hype".*?"(.*?)"', this_string)
    for i in alltext:
        name=i.group(1)
        if name in base_txt:
            base_txt[name]['hype']={'1':i.group(2)}

def get_hero_data_from_txt(base_txt, source_address):
    this_file = open(source_address, mode="r")
    this_string = this_file.read()
    alltext = re.finditer('"npc_dota_hero_(.*?)"\n\t\{(.|\n)*?\n\t\}', this_string)
    for i in alltext:
        name = i.group(1)
        if name=='base':
            base_txt[name]=copy.deepcopy(hero_default)
        else:
            base_txt[name] = copy.deepcopy(base_txt['base'])
        all_pro = re.finditer('\n\t\t"(.*?)".*?"(.*?)"', i.group(0))
        base_txt[name]['ability'] = []
        for j in all_pro:
            temp_name = j.group(1)
            temp_value = j.group(2)
            if re.match('Ability[0-9]+',temp_name)==None:
                base_txt[name][temp_name] = {}
                temp_list = temp_value.split(',')
                for k in range(len(temp_list)):
                    temp_valuek = temp_list[k].strip()
                    try:
                        base_txt[name][temp_name][str(k + 1)] = int(temp_valuek)
                    except ValueError:
                        try:
                            base_txt[name][temp_name][str(k + 1)] = float(temp_valuek)
                        except ValueError:
                            for l in heropro_txt:
                                if temp_name==l[1] and len(l)>2 and temp_valuek in l[2]:
                                    base_txt[name][temp_name][str(k + 1)] = l[2][temp_valuek]
                            if str(k + 1) not in base_txt[name][temp_name]:
                                base_txt[name][temp_name][str(k + 1)] = temp_valuek
            else:
                while len(base_txt[name]['ability']) <= int(temp_name[7:]):
                    base_txt[name]['ability'].append('')
                base_txt[name]['ability'][int(temp_name[7:]) - 1] = temp_value
                i = 0
                while i < len(base_txt[name]['ability']):
                    if base_txt[name]['ability'][i] == '':
                        base_txt[name]['ability'].pop(i)
                    else:
                        i += 1


def fulfill_hero_json(base_txt, all_json, version,name_base):
    for i in all_json:
        if all_json[i]["代码名"] in base_txt["英雄"]:
            all_json[i]["分类"] = "英雄"
            all_json[i]["版本"] = version
            all_json[i]['图片'] = 'Heroes_' + all_json[i]["代码名"] + '.png'
            all_json[i]['迷你图片'] = 'Miniheroes_' + all_json[i]["代码名"] + '.png'
            all_json[i]['攻击后摇']=float(all_json[i]['攻击后摇'])
            all_json[i]['背景']=base_txt["英雄"][all_json[i]["代码名"]]['lore']['1']
            all_json[i]['简介']=base_txt["英雄"][all_json[i]["代码名"]]['hype']['1']
            if '图片地址' in all_json[i]:
                all_json[i].pop('图片地址')
            if '迷你图片地址' in all_json[i]:
                all_json[i].pop('迷你图片地址')
            for j in heropro_txt:
                if j[1] in base_txt["英雄"][all_json[i]["代码名"]]:
                    all_json[i][j[0]] = {"代码": j[1]}
                    for k in base_txt["英雄"][all_json[i]["代码名"]][j[1]]:
                        all_json[i][j[0]][k] = base_txt["英雄"][all_json[i]["代码名"]][j[1]][k]
            for j in heropro_num:
                if j[1] in base_txt["英雄"][all_json[i]["代码名"]]:
                    all_json[i][j[0]] = {"代码": j[1]}
                    for k in base_txt["英雄"][all_json[i]["代码名"]][j[1]]:
                        all_json[i][j[0]][k] = base_txt["英雄"][all_json[i]["代码名"]][j[1]][k]
            all_json[i]['前摇冷却']=round(all_json[i]['攻击间隔']['1']-all_json[i]['攻击前摇']['1'],3)
            all_json[i]['总前后摇']=round(all_json[i]['攻击前摇']['1']+all_json[i]['攻击后摇'],3)
            all_json[i]['后摇空闲']=round(all_json[i]['攻击间隔']['1']-all_json[i]['总前后摇'],3)
            all_json[i]['曾用名']=[]
            for namei in name_base:
                if namei!=all_json[i]['页面名']:
                    for namej in name_base[namei]:
                        if namej[0]==all_json[i]['页面名']:
                            all_json[i]['曾用名'].append(namei)


def create_file(all_json):
    for i in all_json:
        file = open("E:/json/pythonupload/" + i + '.json', mode="w")
        file.write(json.dumps(all_json[i]))
        file.close()


heropro_txt = [["主属性", "AttributePrimary", {"DOTA_ATTRIBUTE_STRENGTH": "力量", "DOTA_ATTRIBUTE_AGILITY": "敏捷", "DOTA_ATTRIBUTE_INTELLECT": "智力"}]
    , ["近战远程", "AttackCapabilities", {"DOTA_UNIT_CAP_MELEE_ATTACK": "近战", "DOTA_UNIT_CAP_RANGED_ATTACK": "远程", "DOTA_UNIT_CAP_NO_ATTACK": "不攻击"}]
    , ["阵营", "Team", {"Good": "天辉", "Bad": "夜魇", "good": "天辉", "bad": "夜魇"}]
    , ["碰撞体积", "BoundsHullName", {"DOTA_HULL_SIZE_HERO": 24, "DOTA_HULL_SIZE_SMALL": 16}]
    , ["定位", "Role", {"Carry": "核心", "Escape": "逃生", "Nuker": "爆发", "Initiator": "先手", "Durable": "耐久", "Disabler": "控制", "Jungler": "打野", "Support": "辅助", "Pusher": "推进"}]
    ,['定位等级','Rolelevels']
    ,['体质类型','GibType']]
heropro_num = [["攻击下限", "AttackDamageMin"]
    , ["攻击上限", "AttackDamageMax"]
    , ["攻击间隔", "AttackRate"]
    , ["攻击前摇", "AttackAnimationPoint"]
    , ["警戒范围", "AttackAcquisitionRange"]
    , ["攻击距离", "AttackRange"]
    , ["弹道速度", "ProjectileSpeed"]
    , ["力量", "AttributeBaseStrength"]
    , ["力量成长", "AttributeStrengthGain"]
    , ["敏捷", "AttributeBaseAgility"]
    , ["敏捷成长", "AttributeAgilityGain"]
    , ["智力", "AttributeBaseIntelligence"]
    , ["智力成长", "AttributeIntelligenceGain"]
    , ["移动速度", "MovementSpeed"]
    , ["转身速率", "MovementTurnRate"]
    , ["护甲", "ArmorPhysical"]
    , ["魔法抗性", "MagicalResistance"]
    , ["生命值", "StatusHealth"]
    , ["生命恢复", "StatusHealthRegen"]
    , ["魔法值", "StatusMana"]
    , ["魔法恢复", "StatusManaRegen"]
    , ["白天视野", "VisionDaytimeRange"]
    , ["夜晚视野", "VisionNighttimeRange"]
    , ["复杂度", "Complexity"]
    , ["腿数量", "Legs"]
    , ["攻击速度", "BaseAttackSpeed"]]
hero_default = {"StatusHealthRegen": {"1": 0}, "GibType": {"1": "default"}, "Team": {"1": "天辉"}, "Complexity": {"1": 1}}
