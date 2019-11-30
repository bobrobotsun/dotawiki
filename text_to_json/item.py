import json
import os


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


def finditemname(source, tb):
    i = source.rfind('\"', 0, tb[0])
    j = source.rfind('\"', 0, i - 1)
    return source[j + 6:i]


# 寻找属性（查询源字符串，数据存储位置，上下限，属性序数，是否继承默认数据）
def finditempro(source, data, tb, pro, number=True, bool=False):
    if bool:
        i = source.find(pro[1], tb[0], tb[1])
        if i != -1:
            data[pro[1]] = {"1": 1}
    else:
        i = source.find('\"' + pro[1] + '\"', tb[0], tb[1])
        if i != -1:
            j = source.find('\"', i + 1, tb[1])
            j = source.find('\"', j + 1, tb[1])
            k = source.find('\"', j + 1, tb[1])
            if number:
                if source[j + 1:k] != '':
                    data[pro[1]] = {}
                    splitit = source[j + 1:k].split(' ')
                    for l in range(len(splitit)):
                        data[pro[1]][str(l + 1)] = float(splitit[l])
            else:
                if source[j + 1:k] != '':
                    data[pro[1]] = {}
                    splitit = source[j + 1:k].split(';')
                    splitit = source[j + 1:k].split(';')
                    if len(pro) == 3:
                        for l in range(len(splitit)):
                            data[pro[1]][str(l + 1)] = pro[2][splitit[l]]
                    else:
                        for l in range(len(splitit)):
                            data[pro[1]][str(l + 1)] = splitit[l]


def finditemrequire(source, data, tb):
    data["ItemRequirements"] = {}
    i = source.find("ItemRequirements", tb[0], tb[1])
    if i == -1:
        return
    else:
        j = source.find("{", i, tb[1])
        k = source.find("}", j + 1, tb[1])
        r = [j, j]
        while True:
            r[0] = source.find('\"', r[1] + 1, k) + 1
            if r[0] != 0:
                r[0] = source.find('\"', r[0], k) + 1
                r[0] = source.find('\"', r[0], k) + 1
                r[1] = source.find('\"', r[0], k)
                splitit = source[r[0]:r[1]].split(';')
                data["ItemRequirements"][str(len(data["ItemRequirements"]) + 1)] = {}
                for l in range(len(splitit)):
                    data["ItemRequirements"][str(len(data["ItemRequirements"]))][str(l + 1)] = splitit[l][5:]
            else:
                return


def finditemspecial(source, data, tb):
    i = source.find("AbilitySpecial", tb[0], tb[1])
    if i == -1:
        return
    else:
        k = source.find("{", i, tb[1])
        while True:
            j = source.find("{", k + 1, tb[1])
            k = source.find("}", k + 1, tb[1])
            if j < k and j != -1:
                r = [0, 0, 0, 0]
                r[0] = source.find('\"', j, k) + 1
                r[0] = source.find('\"', r[0], k) + 1
                r[0] = source.find('\"', r[0], k) + 1
                r[0] = source.find('\"', r[0], k) + 1
                r[0] = source.find('\"', r[0], k) + 1
                r[1] = source.find('\"', r[0], k)
                r[2] = source.find('\"', r[1] + 1, k) + 1
                r[3] = source.find('\"', r[2], k)
                splitit = source[r[2]:r[3]].split(' ')
                data[source[r[0]:r[1]]] = {}
                for l in range(len(splitit)):
                    if (splitit[l][-1] == 'f'):
                        data[source[r[0]:r[1]]][str(l + 1)] = float(splitit[l][0:-1])
                    else:
                        data[source[r[0]:r[1]]][str(l + 1)] = float(splitit[l])
            else:
                return


def get_hero_data_from_txt(base_txt,address):
    ffile = open(address, mode="r")
    source_string = ffile.read()
    tb = [0, source_string.find("{") + 1]
    item_all = {}
    item_count = 0
    while (True):
        if (findtb(source_string, tb[1] + 2, len(source_string), tb, 0)):
            name = finditemname(source_string, tb)
            base_txt[name] = {}
            for i in itempro_txt:
                finditempro(source_string, base_txt[name], tb, i, False)
            for i in itempro_num:
                finditempro(source_string, base_txt[name], tb, i)
            for i in itempro_bool:
                finditempro(source_string, base_txt[name], tb, i, False, True)
            finditemrequire(source_string, base_txt[name], tb)
            finditemspecial(source_string, base_txt[name], tb)
        else:
            break


def fulfill_item_json(base_txt, all_json,version):
    for ii in all_json:
        all_json[ii]["分类"] = "物品"
        all_json[ii]["版本"] = version
        all_json[ii]["应用"] = 1
        if '升级' in all_json[ii]:
            all_json[ii].pop('升级')
        for i in item_for_item:
            if i in base_txt["物品"][all_json[ii]['代码名']]:
                all_json[ii][i] = base_txt["物品"][all_json[ii]['代码名']][i]
        for i in all_json[ii]:
            if isinstance(all_json[ii][i], dict) and '代码' in all_json[ii][i] and all_json[ii][i]["代码"] in base_txt["物品"][all_json[ii]["代码名"]]:
                if str(all_json[ii]['等级']) in base_txt["物品"][all_json[ii]["代码名"]][all_json[ii][i]["代码"]]:
                    all_json[ii][i]["1"] = base_txt["物品"][all_json[ii]["代码名"]][all_json[ii][i]["代码"]][str(all_json[ii]['等级'])]
                else:
                    all_json[ii][i]["1"] = base_txt["物品"][all_json[ii]["代码名"]][all_json[ii][i]["代码"]]["1"]
        # 以下是确认物品的组件、卷轴情况
        if ('recipe_' + all_json[ii]["代码名"]) in base_txt["物品"]:
            all_json[ii]["组件"] = {}
            if base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemCost"]["1"] != 0:
                all_json[ii]["卷轴价格"] = {'代码': 'ItemCost', '1': base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemCost"]["1"]}
                all_json[ii]["组件"] = {}
                for jj in base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"]:
                    all_json[ii]["组件"][jj] = base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"][jj]
            else:
                if base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"][str(len(base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"]))][
                   0:6] == 'recipe':
                    all_json[ii]["卷轴价格"] = {'代码': 'ItemCost', '1':
                        base_txt["物品"][
                            base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"][str(len(base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"]))]][
                            "ItemCost"]["1"]}
                    all_json[ii]["组件"] = {}
                    for j in range(len(base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"]) - 1):
                        all_json[ii]["组件"][str(j + 1)] = base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"][str(j + 1)]
                else:
                    all_json[ii]["卷轴价格"] = {'代码': 'ItemCost', '1': 0}
                    if all_json[ii]["合成"] == 0:
                        all_json[ii]["组件"] = {}
                        for jj in base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"]:
                            all_json[ii]["组件"][jj] = base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"][jj]
                    else:
                        all_json[ii]["组件"] = {}
                        for jj in base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"]["1"]:
                            all_json[ii]["组件"][jj] = base_txt["物品"]['recipe_' + all_json[ii]["代码名"]]["ItemRequirements"][str(all_json[ii]["合成"])][jj]
        all_json[all_json[ii]["页面名"]] = all_json[ii]
    # 接下来把所有的组件变成中文名+图片的形式
    for i in all_json:
        if "组件" in all_json[i]:
            for j in all_json[i]["组件"]:
                for k in all_json:
                    if all_json[i]["组件"][j] == all_json[k]["代码名"]:
                        all_json[i]["组件"][j] = {"物品名": all_json[k]["页面名"], "图片": all_json[k]["图片"]}
    # 接下来把所有的升级放在这儿
    for i in all_json:
        if "组件" in all_json[i]:
            if all_json[i]["合成"] == 0:
                for j in base_txt["物品"]['recipe_' + all_json[i]["代码名"]]["ItemRequirements"]:
                    for k in base_txt["物品"]['recipe_' + all_json[i]["代码名"]]["ItemRequirements"][j]:
                        for l in all_json:
                            if all_json[l]["代码名"] == base_txt["物品"]['recipe_' + all_json[i]["代码名"]]["ItemRequirements"][j][k]:
                                if "升级" not in all_json[l]:
                                    all_json[l]["升级"] = {"1": {"物品名": all_json[i]["页面名"], "图片": all_json[i]["图片"]}}
                                elif all_json[l]["升级"][str(len(all_json[l]["升级"]))]["物品名"] != i:
                                    all_json[l]["升级"][str(len(all_json[l]["升级"]) + 1)] = {"物品名": all_json[i]["页面名"], "图片": all_json[i]["图片"]}
            else:
                for j in all_json[i]["组件"]:
                    if "升级" not in all_json[all_json[i]["组件"][j]["物品名"]]:
                        all_json[all_json[i]["组件"][j]["物品名"]]["升级"] = {"1": {"物品名": all_json[i]["页面名"], "图片": all_json[i]["图片"]}}
                    elif all_json[all_json[i]["组件"][j]["物品名"]]["升级"][str(len(all_json[all_json[i]["组件"][j]["物品名"]]["升级"]))]["物品名"] != i:
                        all_json[all_json[i]["组件"][j]["物品名"]]["升级"][str(len(all_json[all_json[i]["组件"][j]["物品名"]]["升级"]) + 1)] = {"物品名": all_json[i]["页面名"],
                                                                                                                                  "图片": all_json[i]["图片"]}
        # 这里开始同商店物品填入
        all_json[i]["同商店物品"] = {}
        for j in all_json:
            if all_json[i]["商店"] == all_json[j]["商店"]:
                all_json[i]["同商店物品"][str(len(all_json[i]["同商店物品"]) + 1)] = {"物品名": all_json[j]["页面名"], "图片": all_json[j]["图片"]}


def create_file(all_json):
    for i in all_json:
        file = open("E:/json/pythonupload/" + i + '.json', mode="w")
        file.write(json.dumps(all_json[i]))
        file.close()

itempro_txt = [["商店标识", "ItemShopTags"]
    , ["质量", "ItemQuality"]
    , ["别名", "ItemAliases"]
    , ["可拆分", "ItemDisassembleRule", {"DOTA_ITEM_DISASSEMBLE_NEVER": 0, "DOTA_ITEM_DISASSEMBLE_ALWAYS": 1}]
               ]
itempro_num = [["施法距离", "AbilityCastRange"]
    , ["魔法消耗", "AbilityManaCost"]
    , ["施法前摇", "AbilityCastPoint"]
    , ["冷却时间", "AbilityCooldown"]
    , ["价格", "ItemCost"]
    , ["边路商店", "SideShop"]
    , ["可堆叠", "ItemStackable"]
    , ["耗尽后不消失", "ItemPermanent"]
    , ["初始充能", "ItemInitialCharges"]
    , ["上货时间", "ItemStockTime"]
    , ["初始货量", "ItemStockInitial"]
    , ["最大货量", "ItemStockMax"]
    , ["初始上货时间", "ItemInitialStockTime"]
    , ["可提醒队友", "ItemAlertable"]
               ]
itempro_bool = [["即时生效", "DOTA_ABILITY_BEHAVIOR_IMMEDIATE"]]
item_for_item = ["边路商店", "价格", "上货时间", "初始货量", "最大货量", "初始上货时间", "可提醒队友", "可拆分"]

