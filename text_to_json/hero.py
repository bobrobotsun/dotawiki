import json
import hashlib
import re
import copy
from xpinyin import Pinyin
from text_to_json import ability
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
            elif len(pro) == 4:
                data[pro[3]] = {"1": pro[2][source[j + 1:k]]}
            else:
                if number:
                    data[pro[1]] = {"1": float(source[j + 1:k])}
                else:
                    data[pro[1]] = {"1": source[j + 1:k]}
    return


def get_lore_data_from_vpk(base_txt, ffile):
    this_string = ffile.read().decode('utf8')
    alltext = re.finditer('"npc_dota_hero_(.*?)_bio".*?"((.|\n)*?)"', this_string)
    for i in alltext:
        name = i.group(1)
        if name in base_txt:
            base_txt[name]['lore'] = {'1': i.group(2)}


def get_dota_data_from_vpk(base_txt, ffile):
    this_string = ffile.read().decode('utf8')
    alltext = re.finditer('"npc_dota_hero_(.*?)_hype".*?"(.*?)"', this_string)
    for i in alltext:
        name = i.group(1)
        if name in base_txt:
            base_txt[name]['hype'] = {'1': i.group(2)}


def get_hero_data_from_txt(base_txt, source_address):
    this_file = open(source_address, mode="r")
    this_string = this_file.read()
    alltext = re.finditer('"npc_dota_hero_(.*?)"\n\t\{(.|\n)*?\n\t\}', this_string)
    for i in alltext:
        name = i.group(1)
        if name == 'base':
            base_txt[name] = copy.deepcopy(hero_default)
        else:
            base_txt[name] = copy.deepcopy(base_txt['base'])
        all_pro = re.finditer('\n\t\t"(.*?)".*?"(.*?)"', i.group(0))
        base_txt[name]['ability'] = []
        for j in all_pro:
            temp_name = j.group(1)
            temp_value = j.group(2)
            if re.match('Ability[0-9]+', temp_name) == None:
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
                                if temp_name == l[1]:
                                    if len(l) == 3 and temp_valuek in l[2]:
                                        base_txt[name][temp_name][str(k + 1)] = l[2][temp_valuek]
                                    elif len(l) == 4 and temp_valuek in l[2]:
                                        base_txt[name][l[3]] = {}
                                        base_txt[name][l[3]][str(k + 1)] = l[2][temp_valuek]
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


def fulfill_hero_json(base_txt, all_json, version, name_base):
    for i in all_json:
        if all_json[i]["代码名"] in base_txt["英雄"]:
            all_json[i]["分类"] = "英雄"
            all_json[i]["版本"] = version
            all_json[i]['图片'] = 'Heroes_' + all_json[i]["代码名"] + '.png'
            all_json[i]['迷你图片'] = 'Miniheroes_' + all_json[i]["代码名"] + '.png'
            all_json[i]['攻击后摇'] = float(all_json[i]['攻击后摇'])
            all_json[i]['背景'] = base_txt["英雄"][all_json[i]["代码名"]]['lore']['1']
            all_json[i]['简介'] = base_txt["英雄"][all_json[i]["代码名"]]['hype']['1']
            if '手填标签' not in all_json[i]:
                all_json[i]['手填标签']={}
            if '标签' not in all_json[i]:
                all_json[i]['标签']=[]
            for j in heropro_txt:
                if len(j) == 4 and j[3] in base_txt["英雄"][all_json[i]["代码名"]]:
                    proname = j[3]
                elif j[1] in base_txt["英雄"][all_json[i]["代码名"]]:
                    proname = j[1]
                all_json[i][j[0]] = {"代码": proname}
                for k in base_txt["英雄"][all_json[i]["代码名"]][proname]:
                    all_json[i][j[0]][k] = base_txt["英雄"][all_json[i]["代码名"]][proname][k]
            for j in heropro_num:
                if j[1] in base_txt["英雄"][all_json[i]["代码名"]]:
                    all_json[i][j[0]] = {"代码": j[1]}
                    for k in base_txt["英雄"][all_json[i]["代码名"]][j[1]]:
                        all_json[i][j[0]][k] = base_txt["英雄"][all_json[i]["代码名"]][j[1]][k]
            all_json[i]['前摇冷却'] = round(all_json[i]['攻击间隔']['1'] - all_json[i]['攻击前摇']['1'], 3)
            all_json[i]['总前后摇'] = round(all_json[i]['攻击前摇']['1'] + all_json[i]['攻击后摇'], 3)
            all_json[i]['后摇空闲'] = round(all_json[i]['攻击间隔']['1'] - all_json[i]['总前后摇'], 3)
            all_json[i]['曾用名'] = []
            if i in name_base:
                for namej in name_base[i]:
                    if namej != i:
                        all_json[i]['曾用名'].append(namej)


def fulfil_talent_show(all_json, html_function):
    for i in all_json['英雄']:
        db = all_json['英雄'][i]
        talent = {}
        talent['全天赋'] = '<div class="dota_hero_talent_simple_show_complete">'
        for jj in [25, 20, 15, 10]:
            j = str(jj)
            colorcontent = str(160 - 4 * jj) + ',' + str(160 - 4 * jj) + ',' + str(160 - 4 * jj)
            colorlevel = '0,' + str(250 - 5 * jj) + ',' + str(8 * jj)
            talent[j] = ''
            talent[j] += '<div class="dota_hero_talent_simple_show_row" style="background:rgb(' + colorcontent \
                         + ');"><div class="dota_hero_talent_simple_show_talent_left">' \
                         + all_json['技能'][i + j + '级左天赋']['中文名'] + '</div>' \
                                                                   '<div class="dota_hero_talent_simple_show_level" style="background:rgb(' + colorlevel + ');><b>' + j \
                         + '</b></div><div class="dota_hero_talent_simple_show_talent_right">' \
                         + all_json['技能'][i + j + '级右天赋']['中文名'] + '</div></div>'
            talent[j] = html_function(talent[j])
            talent['全天赋'] += talent[j]
        talent['全天赋'] += '</div>'
        db['天赋展示'] = talent


def create_file(all_json):
    for i in all_json:
        file = open("E:/json/pythonupload/" + i + '.json', mode="w")
        file.write(json.dumps(all_json[i]))
        file.close()


def fulfil_complex_and_simple_show_attri_0(name, value):
    return '<div class="bgc_black" style="text-align:right;padding:0 0.5em 0 0;">' + name + '</div><div class="border_black" style="text-align:left;padding:0 0 0 0.5em;">' + value + '</div>'

def fulfil_complex_and_simple_show_attri_1(name, value):
    return '<div style="padding:1px;"><div class="bgc_black">' + name + '</div><div class="border_black">' + value + '</div></div>'


def fulfil_complex_and_simple_show_attri_2(name, value, prepost=''):
    retxt = '<span class="dota_hero_comprehensive_attri_dict_hero_attri_text" data-hero-attri-name="' + name + '"'
    if prepost != '':
        retxt += ' data-show-transform-function="transform_function_prefix_postfix" data-transform-prefix-postfix="' + prepost + '"'
    retxt += '>' + value + '</span>'
    return retxt


def fulfil_complex_and_simple_show(all_json, html_function):
    for i in all_json['英雄']:
        db = all_json['英雄'][i]
        #下面是生成标签功能
        db['标签']=[]
        for k in db['手填标签']:
            if db['手填标签'][k]!='':
                db['标签'].append(db['手填标签'][k])
        db['标签'].append('英雄')
        db['标签'].append(db['主属性']['1']+'英雄')
        db['标签'].append(db['近战远程']['1'])
        db['标签'].append(db['阵营']['1'])
        main_color = ''
        if db["主属性"]['1'] == '力量':
            main_color = 'background-color:#822;'
        elif db["主属性"]['1'] == '敏捷':
            main_color = 'background-color:#282;'
        elif db["主属性"]['1'] == '智力':
            main_color = 'background-color:#228;'
        main_attri_1 = {'力量': '', '敏捷': '', '智力': ''}
        main_attri_1[db["主属性"]['1']] = main_color
        main_attri_2 = {'力量': '', '敏捷': '', '智力': ''}
        main_attri_2[db["主属性"]['1']] = '_Main'
        main_attri = {'力量': '', '敏捷': '', '智力': ''}
        main_attri[db["主属性"]['1']] = 'background-color:#ff6;'
        all_attri = {}
        for ii in ['力量', '敏捷', '智力', '主属性', '生命值', '生命恢复', '魔法值', '魔法恢复', '攻击上限', '攻击下限', '护甲', '攻击速度', '攻击间隔', '攻击前摇']:
            all_attri[ii] = db[ii]['1']
        all_attri['生命值'] += 20 * all_attri['力量']
        all_attri['生命恢复'] += 0.1 * all_attri['力量']
        all_attri['魔法值'] += 12 * all_attri['智力']
        all_attri['魔法恢复'] += 0.05 * all_attri['智力']
        all_attri['攻击速度'] += all_attri['敏捷']
        all_attri['护甲'] += all_attri['敏捷'] / 6
        all_attri['攻击上限'] += all_attri[all_attri['主属性']]
        all_attri['攻击下限'] += all_attri[all_attri['主属性']]
        all_attri['攻击力'] = (all_attri['攻击上限'] + all_attri['攻击下限']) / 2
        all_attri['攻击间隔'] = all_attri['攻击间隔'] / all_attri['攻击速度'] * 100
        all_attri['攻击前摇'] = all_attri['攻击前摇'] / all_attri['攻击速度'] * 100
        all_attri['攻击后摇'] = db['攻击后摇']/ all_attri['攻击速度'] * 100
        all_attri['物理抗性'] = 6 * all_attri['护甲'] / (1 + abs(0.06 * all_attri['护甲']))
        all_attri['物理血量'] =all_attri['生命值']/(100-all_attri['物理抗性'])*100
        all_attri['魔法血量'] =all_attri['生命值']/(100-db['魔法抗性']['1'])*100
        for ii in all_attri:
            if not isinstance(all_attri[ii], str):
                all_attri[ii] = round(all_attri[ii], 2)
        bt = '<span class="dota_compound_list_select_input dota_hero_comprehensive_attri_dict">' \
             +'<div class="dota_hero_comprehensive_attri_dict_hero bgc_black" style="width:360px;float:right;color:white;text-align:center;" data-hero-name="' + i + '">' \
             + '<div style="text-align:center;"><div id="'+db['页面名']+'" style="font-size:200%;font-weight:normal;padding:2px;margin:0px;text-align:center;' + main_color + '">' + db['中文名'] + '</div>' \
             + '<div style="font-size:100%;padding: 2px;text-align:center;' + main_color + '">' + db['英文名'] + '</div>[[file:npc_dota_hero_' + db['代码名'] + '.webm|center|360px|link=]]' \
             + '<div style="padding:0.25em;text-align:center;">' \
             + '<span class="ability_indicator" style="' + main_color + 'color:white;"><span class="dota_get_image_by_json_name" data-json-name="' + db["阵营"]['1'] + '" data-text-link="0"></span></span>' \
             + '<span class="ability_indicator" style="' + main_color + 'color:white;"><span class="dota_get_image_by_json_name" data-json-name="' + db["主属性"]['1'] + '" data-text-link="0"></span></span>' \
             + '<span class="ability_indicator" style="' + main_color + 'color:white;"><span class="dota_get_image_by_json_name" data-json-name="' + db["近战远程"]['1'] + '" data-text-link="0"></span></span></div></div>' \
             + '<div class="bg-primary" style="height:30px;">等级<span class="dota_hero_comprehensive_attri_dict_input dota_compound_number_input" ' \
             + 'style="width:300px;float:right;height:30px; vertical-align:middle;" data-number-input-attri-dict="步长=1；最小=1；最大=30；" ></span></div>' \
             + '<div style="display:flex;flex-wrap:wrap;justify-content:space-around;">' \
             + '<div style="flex-grow:1;margin:1em;' + main_attri_1['力量'] + '">' + str(db['力量']['1']) + '+' + str(db['力量成长']['1']) \
             + '{{图片|Strength_Icon' + main_attri_2['力量'] + '.png|w60|center}}' + fulfil_complex_and_simple_show_attri_2('总力量', '', '，') + '</div>' \
             + '<div style="flex-grow:1;margin:1em;' + main_attri_1['敏捷'] + '">' + str(db['敏捷']['1']) + '+' + str(db['敏捷成长']['1']) \
             + '{{图片|Agility_Icon' + main_attri_2['敏捷'] + '.png|w60|center}}' + fulfil_complex_and_simple_show_attri_2('总敏捷', '', '，') + '</div>' \
             + '<div style="flex-grow:1;margin:1em;' + main_attri_1['智力'] + '">' + str(db['智力']['1']) + '+' + str(db['智力成长']['1']) \
             + '{{图片|Intelligence_Icon' + main_attri_2['智力'] + '.png|w60|center}}' + fulfil_complex_and_simple_show_attri_2('总智力', '', '，') + '</div></div>'\
             +'<div style="display: grid;grid-template-columns:1fr 2fr;place-content:right left;background:#ccc;color:#000;">'\
             + fulfil_complex_and_simple_show_attri_0('生命值', fulfil_complex_and_simple_show_attri_2('总生命值', str(all_attri['生命值']))) \
             + fulfil_complex_and_simple_show_attri_0('生命恢复', fulfil_complex_and_simple_show_attri_2('总生命恢复', str(all_attri['生命恢复']))) \
             + fulfil_complex_and_simple_show_attri_0('魔法值', fulfil_complex_and_simple_show_attri_2('总魔法值', str(all_attri['魔法值']))) \
             + fulfil_complex_and_simple_show_attri_0('魔法恢复', fulfil_complex_and_simple_show_attri_2('总魔法恢复', str(all_attri['魔法恢复']))) \
             + fulfil_complex_and_simple_show_attri_0('攻击力', fulfil_complex_and_simple_show_attri_2('总攻击力', ability.better_float_to_text(all_attri['攻击力'])) \
                                                      + '(' + fulfil_complex_and_simple_show_attri_2('总攻击下限', str(all_attri['攻击下限'])) \
                                                      + '~' + fulfil_complex_and_simple_show_attri_2('总攻击上限', str(all_attri['攻击上限'])) + ')') \
             + fulfil_complex_and_simple_show_attri_0('攻击速度', fulfil_complex_and_simple_show_attri_2('总攻击速度', str(all_attri['攻击速度'])) + '(' + str(db['攻击速度']['1']) + ')') \
             + fulfil_complex_and_simple_show_attri_0('攻击间隔', fulfil_complex_and_simple_show_attri_2('总攻击间隔', str(all_attri['攻击间隔'])) + '(' + str(db['攻击间隔']['1']) + ')') \
             + fulfil_complex_and_simple_show_attri_0('攻击前摇', fulfil_complex_and_simple_show_attri_2('总攻击前摇', str(all_attri['攻击前摇'])) + '(' + str(db['攻击前摇']['1']) + ')') \
             + fulfil_complex_and_simple_show_attri_0('攻击后摇', fulfil_complex_and_simple_show_attri_2('总攻击后摇', str(all_attri['攻击后摇'])) + '(' + str(db['攻击后摇']) + ')') \
             + fulfil_complex_and_simple_show_attri_0('攻击距离', fulfil_complex_and_simple_show_attri_2('总攻击距离', str(db['攻击距离']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('警戒范围', fulfil_complex_and_simple_show_attri_2('总警戒范围', str(db['警戒范围']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('弹道速度', fulfil_complex_and_simple_show_attri_2('总弹道速度', str(db['弹道速度']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('护甲(物理抗性)', fulfil_complex_and_simple_show_attri_2('总护甲', str(all_attri['护甲'])) \
                                                      + '(' + fulfil_complex_and_simple_show_attri_2('总物理抗性', str(all_attri['物理抗性']) + '%', '，%') + ')') \
             + fulfil_complex_and_simple_show_attri_0('物理血量', fulfil_complex_and_simple_show_attri_2('总物理血量',str(all_attri['物理血量']))) \
             + fulfil_complex_and_simple_show_attri_0('魔法抗性', fulfil_complex_and_simple_show_attri_2('总魔法抗性', str(db['魔法抗性']['1']) + '%', '，%')) \
             + fulfil_complex_and_simple_show_attri_0('魔法血量', fulfil_complex_and_simple_show_attri_2('总魔法血量',str(all_attri['魔法血量']))) \
             + fulfil_complex_and_simple_show_attri_0('移动速度', fulfil_complex_and_simple_show_attri_2('总移动速度', str(db['移动速度']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('转身速率', fulfil_complex_and_simple_show_attri_2('总转身速率', str(db['转身速率']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('白天视野', fulfil_complex_and_simple_show_attri_2('总白天视野', str(db['白天视野']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('夜晚视野', fulfil_complex_and_simple_show_attri_2('总夜晚视野', str(db['夜晚视野']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('碰撞体积', fulfil_complex_and_simple_show_attri_2('总碰撞体积',str(db['碰撞体积']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('边界体积', fulfil_complex_and_simple_show_attri_2('总边界体积',str(db['边界体积']['1']))) \
             + fulfil_complex_and_simple_show_attri_0('腿数量', fulfil_complex_and_simple_show_attri_2('总腿数量',str(db['腿数量']['1']))) \
             + '</div>'  # 完整显示
        st = '<div class="dota_simple_infobox bgc_white dota_hero_comprehensive_attri_dict_hero" data-hero-name="' + i + '">' \
             + '<div style="text-align:center;"><div class="bg-primary" style="float:left;padding:0.5em">' \
             + '<span class="dota_get_image_by_json_name" data-json-name="' + i + '" data-image-height="72" data-image-link="1" data-image-center="1"></span></div>' \
             + '<div class="bg-primary" style="font-size:150%;font-weight:normal;padding:2px;margin:0px;text-align:center;">[[' + db["页面名"] + '|' + db["中文名"] + ']]</div>' \
             + '<div class="bg-primary" style="font-size:100%;padding: 2px;text-align:center;">' + db["英文名"] + '</div>' \
             + '<div style="padding:0.25em;text-align:center;">' \
             + '<span class="ability_indicator" style="background:#a33;color:white;"><span class="dota_get_image_by_json_name" data-json-name="' + db["阵营"]['1'] + '" data-text-link="0"></span></span>' \
             + '<span class="ability_indicator" style="background:#a33;color:white;"><span class="dota_get_image_by_json_name" data-json-name="' + db["主属性"]['1'] + '" data-text-link="0"></span></span>' \
             + '<span class="ability_indicator" style="background:#a33;color:white;"><span class="dota_get_image_by_json_name" data-json-name="' + db["近战远程"]['1'] + '" data-text-link="0"></span></span></div></div>' \
             + '<div style="display:flex;flex-wrap:wrap;justify-content:space-around;">' \
             + '<div style="padding:0.25em;border:1px #333 solid;' + main_attri['力量'] \
             + '"><span class="dota_get_image_by_json_name" data-json-name="力量" title="力量"></span>' + str(db['力量']['1']) + '+' + str(db['力量成长']['1']) \
             + fulfil_complex_and_simple_show_attri_2('总力量', '', '=，') + '</div><div style="padding:0.25em;border:1px #333 solid;' + main_attri['敏捷'] \
             + '"><span class="dota_get_image_by_json_name" data-json-name="敏捷" title="敏捷"></span>' + str(db['敏捷']['1']) + '+' + str(db['敏捷成长']['1']) \
             + fulfil_complex_and_simple_show_attri_2('总敏捷', '', '=，') + '</div><div style="padding:0.25em;border:1px #333 solid;' + main_attri['智力'] \
             + '"><span class="dota_get_image_by_json_name" data-json-name="智力" title="智力"></span>' + str(db['智力']['1']) + '+' + str(db['智力成长']['1']) \
             + fulfil_complex_and_simple_show_attri_2('总智力', '', '=，') \
             + '</div></div>' \
             + '<div style="display: grid;grid-template-columns:repeat(4,1fr);place-content:center center;background:#ccc;color:#000;">' \
             + fulfil_complex_and_simple_show_attri_1('生命值', fulfil_complex_and_simple_show_attri_2('总生命值', str(all_attri['生命值']))) \
             + fulfil_complex_and_simple_show_attri_1('生命恢复', fulfil_complex_and_simple_show_attri_2('总生命恢复', str(all_attri['生命恢复']))) \
             + fulfil_complex_and_simple_show_attri_1('魔法值', fulfil_complex_and_simple_show_attri_2('总魔法值', str(all_attri['魔法值']))) \
             + fulfil_complex_and_simple_show_attri_1('魔法恢复', fulfil_complex_and_simple_show_attri_2('总魔法恢复', str(all_attri['魔法恢复']))) \
             + fulfil_complex_and_simple_show_attri_1('攻击力', fulfil_complex_and_simple_show_attri_2('总攻击力', ability.better_float_to_text(all_attri['攻击力'])) \
                                                      + '(' + fulfil_complex_and_simple_show_attri_2('总攻击下限', str(all_attri['攻击下限'])) \
                                                      + '~' + fulfil_complex_and_simple_show_attri_2('总攻击上限', str(all_attri['攻击上限'])) + ')') \
             + fulfil_complex_and_simple_show_attri_1('攻击速度', fulfil_complex_and_simple_show_attri_2('总攻击速度', str(all_attri['攻击速度'])) + '(' + str(db['攻击速度']['1']) + ')') \
             + fulfil_complex_and_simple_show_attri_1('攻击间隔', fulfil_complex_and_simple_show_attri_2('总攻击间隔', str(all_attri['攻击间隔'])) + '(' + str(db['攻击间隔']['1']) + ')') \
             + fulfil_complex_and_simple_show_attri_1('攻击前摇', fulfil_complex_and_simple_show_attri_2('总攻击前摇', str(all_attri['攻击前摇'])) + '(' + str(db['攻击前摇']['1']) + ')') \
             + fulfil_complex_and_simple_show_attri_1('攻击距离', fulfil_complex_and_simple_show_attri_2('总攻击距离', str(db['攻击距离']['1']))) \
             + fulfil_complex_and_simple_show_attri_1('弹道速度', fulfil_complex_and_simple_show_attri_2('总弹道速度', str(db['弹道速度']['1']))) \
             + fulfil_complex_and_simple_show_attri_1('护甲', fulfil_complex_and_simple_show_attri_2('总护甲', str(all_attri['护甲'])) \
                                                      + '(' + fulfil_complex_and_simple_show_attri_2('总物理抗性', str(all_attri['物理抗性']) + '%', '，%') + ')') \
             + fulfil_complex_and_simple_show_attri_1('魔法抗性', fulfil_complex_and_simple_show_attri_2('总魔法抗性', str(db['魔法抗性']['1']) + '%', '，%')) \
             + fulfil_complex_and_simple_show_attri_1('移动速度', fulfil_complex_and_simple_show_attri_2('总移动速度', str(db['移动速度']['1']))) \
             + fulfil_complex_and_simple_show_attri_1('转身速率', fulfil_complex_and_simple_show_attri_2('总转身速率', str(db['转身速率']['1']))) \
             + fulfil_complex_and_simple_show_attri_1('白天视野', fulfil_complex_and_simple_show_attri_2('总白天视野', str(db['白天视野']['1']))) \
             + fulfil_complex_and_simple_show_attri_1('夜晚视野', fulfil_complex_and_simple_show_attri_2('总夜晚视野', str(db['夜晚视野']['1']))) \
             + '</div>' \
               '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(48px,1fr));gap:2px;place-content:center center;">'
        for ii in range(len(db['技能']) - 8):
            v = db['技能'][ii]
            st += '<div class="dota_click_absolute_additional_infomation_frame dota_click_find_text_in_json_and_show">' \
                  '<div class="dota_get_image_by_json_name dota_click_absolute_additional_infomation_frame_button" data-json-name="' + v \
                  + '" data-image-height="36" data-image-center="1"></div>' \
                    '<div class="dota_click_absolute_additional_infomation_frame_frame dota_click_find_text_in_json_and_show_textarea">' \
                    '<div class="dota_click_find_text_in_json_and_show_button" data-find-text-in-json-address="' + v + '，简易展示">点击显示《' + v + '》详细信息</div></div></div>'
        bt += '<div class="bgc_white" style="display:grid;grid-template-columns:1fr 30px 1fr;">' \
              + '<div class="border_black">' + all_json['技能'][i + '25级左天赋']['中文名'] \
              + '</div><div class="bgc_black">25</div><div class="border_black">' + all_json['技能'][i + '25级右天赋']['中文名'] + '</div>' \
              + '<div class="border_black">' + all_json['技能'][i + '20级左天赋']['中文名'] \
              + '</div><div class="bgc_black">20</div><div class="border_black">' + all_json['技能'][i + '20级右天赋']['中文名'] + '</div>' \
              + '<div class="border_black">' + all_json['技能'][i + '15级左天赋']['中文名'] \
              + '</div><div class="bgc_black">15</div><div class="border_black">' + all_json['技能'][i + '15级右天赋']['中文名'] + '</div>' \
              +'<div class="border_black">' + all_json['技能'][i + '10级左天赋']['中文名'] \
              + '</div><div class="bgc_black">10</div><div class="border_black">' + all_json['技能'][i + '10级右天赋']['中文名'] + '</div>' \
              + '</div>'
        st += '</div><div style="display:grid;grid-template-columns:1fr 30px 1fr;">' \
              + '<div class="border_black">' + all_json['技能'][i + '25级左天赋']['中文名'] \
              + '</div><div class="bgc_black">25</div><div class="border_black">' + all_json['技能'][i + '25级右天赋']['中文名'] + '</div>' \
              + '<div class="border_black">' + all_json['技能'][i + '20级左天赋']['中文名'] \
              + '</div><div class="bgc_black">20</div><div class="border_black">' + all_json['技能'][i + '20级右天赋']['中文名'] + '</div>' \
              + '<div class="border_black">' + all_json['技能'][i + '15级左天赋']['中文名'] \
              + '</div><div class="bgc_black">15</div><div class="border_black">' + all_json['技能'][i + '15级右天赋']['中文名'] + '</div>' \
              +'<div class="border_black">' + all_json['技能'][i + '10级左天赋']['中文名'] \
              + '</div><div class="bgc_black">10</div><div class="border_black">' + all_json['技能'][i + '10级右天赋']['中文名'] + '</div>' \
              + '</div>'
        if db['全属性黄点'] > 0:
            bt += '<div class="dota_ability_level_point_change_show" data-ability-level-point-level-max=' + str(db['全属性黄点']) \
                  + ' data-ability-level-point-level-now=' + str(db['全属性黄点']) + ' style="padding:0.25em;">+ 2 全 属 性</div>'
            st += '<div class="dota_ability_level_point_change_show" data-ability-level-point-level-max=' + str(db['全属性黄点']) \
                  + ' data-ability-level-point-level-now=' + str(db['全属性黄点']) + '>+ 2 全 属 性</div>'
        bt += '<div class="adminpanel" style="text-align:left;"><b>[[data:' + db["页面名"] + '.json|J]]</b></div></div></span>'\
              +'<div class="dota_invisible_menu_item_at_right_of_the_screen">[[#' + db["页面名"] + '|' + db["页面名"] + ']]</div>'
        st += '</div>'
        # 缩略显示
        db['简易展示'] = html_function(st)
        db['具体展示'] = html_function(bt)


def create_html_data_page(all_json):
    retxt = '<script>\ndota_json_hero_data={'
    p = Pinyin()
    for i in all_json['英雄']:
        retxt += '\n"' + i + '":{"拼音":"' + p.get_pinyin(i).replace('-', '') + '","英文":"' + all_json['英雄'][i]['英文名'] + '","代码":"' + all_json['英雄'][i]['代码名'] + '","攻击后摇":"' + str(all_json['英雄'][i]['攻击后摇']) + '",'
        for j in [['主属性'], ['近战远程'], ['阵营'], ['碰撞体积'], ['边界体积'], ['体质类型']] + heropro_num:
            retxt += '"' + j[0] + '":'
            if isinstance(all_json['英雄'][i][j[0]]['1'], str):
                retxt += '"' + all_json['英雄'][i][j[0]]['1'] + '",'
            else:
                retxt += ability.better_float_to_text(all_json['英雄'][i][j[0]]['1']) + ','
        retxt += '"技能":['
        for j in range(len(all_json['英雄'][i]['技能'])-8):
            retxt += '"' + all_json['英雄'][i]['技能'][j] + '",'
        talent=['10级左','10级右','15级左','15级右','20级左','20级右','25级左','25级右']
        for j in talent:
            retxt+='"' +i+ j + '天赋",'
        retxt = retxt.rstrip(',') + '],"技能中文名":['
        for j in range(len(all_json['英雄'][i]['技能'])-8):
            w=all_json['英雄'][i]['技能'][j]
            retxt += "'" + all_json['技能'][w]['中文名'] + "',"
        for j in talent:
            w=i+ j + '天赋'
            retxt+= "'" + all_json['技能'][w]['中文名'] + "',"
        retxt = retxt.rstrip(',') + '],"全属性黄点":' + str(all_json['英雄'][i]['全属性黄点']) + ','
        retxt = retxt.rstrip(',') + '},'
    retxt = retxt.rstrip(',') + '};\n</script>'
    return retxt


heropro_txt = [["主属性", "AttributePrimary", {"DOTA_ATTRIBUTE_STRENGTH": "力量", "DOTA_ATTRIBUTE_AGILITY": "敏捷", "DOTA_ATTRIBUTE_INTELLECT": "智力"}]
    , ["近战远程", "AttackCapabilities", {"DOTA_UNIT_CAP_MELEE_ATTACK": "近战", "DOTA_UNIT_CAP_RANGED_ATTACK": "远程", "DOTA_UNIT_CAP_NO_ATTACK": "不攻击"}]
    , ["阵营", "Team", {"Good": "天辉", "Bad": "夜魇", "good": "天辉", "bad": "夜魇"}]
    , ["碰撞体积", "BoundsHullName", {"DOTA_HULL_SIZE_HERO": 28, "DOTA_HULL_SIZE_SMALL": 18}]
    , ["边界体积", "BoundsHullName", {"DOTA_HULL_SIZE_HERO": 24, "DOTA_HULL_SIZE_SMALL": 8}, 'BoundsHullName2']
    , ["定位", "Role", {"Carry": "核心", "Escape": "逃生", "Nuker": "爆发", "Initiator": "先手", "Durable": "耐久", "Disabler": "控制", "Jungler": "打野", "Support": "辅助", "Pusher": "推进"}]
    , ['定位等级', 'Rolelevels']
    , ['体质类型', 'GibType']]
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
