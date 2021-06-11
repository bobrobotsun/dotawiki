import re
import math
from text_to_json import ability
target_url = 'http://dota.huijiwiki.com/w/api.php'


def analyse_upload_json(text, upload_info):
    upload_info_json = upload_info.json()
    if 'edit' in upload_info_json and upload_info_json['edit']['result'] == 'Success':
        if 'nochange' in upload_info.json()['edit']:
            return ['《' + text + '》没有修改', 0]
        elif 'oldrevid' in upload_info.json()['edit']:
            return ['《' + text + '》修改' + str(upload_info.json()['edit']['oldrevid']) + '为' + str(upload_info.json()['edit']['newrevid']), 1]
        else:
            return ['《' + text + '》修改成功', 1]
    else:
        return ['《' + text + '》修改失败', 0]


# 获得所有该单位+技能的名字和曾用名的list
def all_the_names(db, json_base):
    relist = [db['页面名']]
    if '曾用名' in db:
        for i in db['曾用名']:
            relist.append(i)
    if '技能' in db:
        for i in db['技能']:
            relist.append(i)
            if '曾用名' in json_base['技能'][i]:
                for j in json_base['技能'][i]['曾用名']:
                    relist.append(j)
    if '源技能' in db:
        for i in db['源技能']:
            v=db['源技能'][i]
            if v in db['技能']:
                relist.append(v)
                if '曾用名' in json_base['技能'][v]:
                    for j in json_base['技能'][v]['曾用名']:
                        relist.append(j)
    return relist


def number_to_string(number, rr=4):
    i = number
    try:
        if float(int(i)) == float(i):
            return str(int(i))
        else:
            return str(round(i, rr))
    except ValueError:
        return str(i)


def create_upgrade_text(numjsons, k, post_each=lambda x: x['后缀'] if '后缀' in x else '', post_group=lambda x, y: '', image_size='x22px'):
    if k in numjsons:
        numjson = numjsons[k]
        retext = ''
        ii = 0
        while True:
            ii += 1
            i = str(ii)
            if i in numjson:
                if ii > 1:
                    for j in numjson[i]['升级来源']:
                        retext += '[[file:' + numjson[i]['升级来源'][j]["图片"] + '|' + image_size + '|link=' + numjson[i]['升级来源'][j]["名称"] + ']]'
                jj = 0
                while True:
                    jj += 1
                    j = str(jj)
                    if j in numjson[i]:
                        if jj > 1:
                            retext += "/"
                        retext += number_to_string(numjson[i][j])
                        if retext[-1].isnumeric():
                            retext += post_each(numjsons[k])
                    else:
                        break
                retext += post_group(numjson, i)
            else:
                break
        return retext
    else:
        return ''

def nocheck_create_upgrade_text(numjson, post_each=lambda x: x['后缀'] if '后缀' in x else '', post_group=lambda x, y: '', image_size='x22px'):
    retext = ''
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in numjson:
            if ii > 1:
                for j in numjson[i]['升级来源']:
                    retext += '[[file:' + numjson[i]['升级来源'][j]["图片"] + '|' + image_size + '|link=' + numjson[i]['升级来源'][j]["名称"] + ']]'
            jj = 0
            while True:
                jj += 1
                j = str(jj)
                if j in numjson[i]:
                    if jj > 1:
                        retext += "/"
                    retext += number_to_string(numjson[i][j])
                    if retext[-1].isnumeric():
                        retext += post_each(numjson)
                else:
                    break
            retext += post_group(numjson, i)
        else:
            break
    return retext




def get_unit_value(array, post=''):
    if isinstance(array, dict):
        retxt = ''
        for i, v in array.items():
            if i != '1':
                retxt += '/'
            retxt += v + post
        return retxt
    else:
        return '无信息'


def get_unit_upgrade_double(db1, db2, combine='~', post=''):
    retxt = ''
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in db1:
            if ii > 1:
                retxt += '<br>'
                for j, w in db1[i]['升级来源'].items():
                    retxt += '[[file:' + w["图片"] + '|16px|link=' + w["名称"] + ']]'
            jj = 0
            while True:
                jj += 1
                j = str(jj)
                if j in db1[i]:
                    if jj > 1:
                        retxt += '/'
                    retxt += number_to_string(db1[i][j]) + post
                else:
                    break
            retxt += combine
            jj = 0
            while True:
                jj += 1
                j = str(jj)
                if j in db2[i]:
                    if jj > 1:
                        retxt += '/'
                    retxt += number_to_string(db2[i][j]) + post
                else:
                    break
        else:
            break
    return retxt

def get_item_value(db):
    if isinstance(db, dict):
        return db['1']
    else:
        return db


def create_infobox_item(db):
    common_tag = ['<tr><td colspan=2 style="background:#ccc;', '</td></tr>']
    common_pro = {'共享': ['color:#a03030;"><i class="fa fa-times" aria-hidden="true"></i>不可以给队友共享', ';color:#229944;"><i class="fa fa-check" aria-hidden="true"></i>可以给队友共享'],
                  '可拆分': ['color:#a03030;"><i class="fa fa-times" aria-hidden="true"></i>合成10秒后不可拆分', ';color:#229944;"><i class="fa fa-check" aria-hidden="true"></i>永久可以拆分']}
    normal_tag = ['<tr><td colspan=2 style="background:#ddd;color:#000;margin:6px;font-size:1em;">', '</td></tr>']
    retxt = '<table class="infobox" style="text-align:center;background:#fff;width:300px;color:#fff;"><tr class="infobox-title">' + '<th colspan=2 style="background: #a03030;padding: 0.5em 1em;;text-align:center;">' + '<span style="font-size:125%">' + \
            db["中文名"] + '</span><div style="text-align:center;">' + db["英文名"] + '</div>' + '</th></tr>'
    if db["图片"] != '':
        retxt += '<tr><td colspan=2 style="background:#222">[[file:' + db["图片"] + '|100px|center|link=' + db["页面名"] \
                 + ']]</td></tr><tr><td style="background:#a03030;font-size:12px;color:#eee;padding:12px;>' + db['传说'] + '</td></tr>' \
                 + '<tr><td colspan="2" style="border-bottom-width:0px;text-align:center;background:#c38a1c;padding:8px;font-size:16px;font-weight:bold;color:#fff;">[[file:Gold symbol.png|30px|link=]]&nbsp;' \
                 + number_to_string(db['价格']['1']) + ''
    if '卷轴价格' in db and db['卷轴价格']['1'] != 0:
        retxt += '<span style="margin-left:1em;">[[file:items recipe.png|24px|link=]]&nbsp;' + number_to_string(db['卷轴价格']['1']) + '</span>'
    retxt += '</td></tr>'
    for i, v in common_pro.items():
        if i != '可拆分' or '组件' in db:
            if i in db:
                retxt += common_tag[0] + v[get_item_value(db[i])] + common_tag[1]
            else:
                retxt += common_tag[0] + v[0] + common_tag[1]
    for i, v in db.items():
        if isinstance(v, dict) and '代码' in v and '后缀' in v and '展示前缀' in v and '展示后缀' in v and '1' in v:
            retxt += normal_tag[0] + v['展示前缀'] + number_to_string(v['1']) + v['后缀'] + v['展示后缀'] + normal_tag[1]
    if '升级' in db:
        retxt += '<tr><td colspan=2 style="background:#a03030;padding:4px;text-align:center;">' + '可合成</td></tr><tr><td colspan=2 style="background:#222;padding:6px;">'
        for i, v in db['升级'].items():
            if int(i) % 4 == 1 and int(i) > 1:
                retxt += '<br><br>'
            retxt += ' [[file:' + v["图片"] + '|48px|link=' + v["物品名"] + ']] '
        retxt += '</td></tr>'
    if '组件' in db:
        retxt += '<tr><td colspan=2 style="background:#a03030;padding:4px;text-align:center;">' + '配方</td></tr><tr><td colspan=2 style="background:#222;padding:6px;">'
        for i, v in db['组件'].items():
            if int(i) % 4 == 1 and int(i) > 1:
                retxt += '<br><br>'
            retxt += ' [[file:' + v["图片"] + '|48px|link=' + v["物品名"] + ']] '
        if '卷轴价格' in db and db['卷轴价格']['1'] != 0:
            retxt += ' [[file:items recipe.png|48px|link=]] '
        retxt += '</td></tr>'
    retxt += '<tr><td colspan=2 style="background:#000;text-align:left;"><div class="adminpanel" style="padding-left:0.25em">\'\'\' [[' + db["页面名"] + '|P]]  [[data:' + db[
        "页面名"] + '.json|J]] \'\'\'</div><div style="float:right;color:#000;padding-right:0.25em">' + db['代码名'] + '</div></td></tr></table>'
    return retxt


def create_role_set(role, level):
    retxt = '<div style="margin:auto;display:inline-block" title="' + number_to_string(level) + '级' + number_to_string(role) + '">[[file:'
    if role == '核心':
        retxt += 'carry'
    elif role == '爆发':
        retxt += 'nuker'
    elif role == '先手':
        retxt += 'initiator'
    elif role == '控制':
        retxt += 'disabler'
    elif role == '耐久':
        retxt += 'durable'
    elif role == '逃生':
        retxt += 'escape'
    elif role == '辅助':
        retxt += 'support'
    elif role == '打野':
        retxt += 'jungler'
    elif role == '推进':
        retxt += 'pusher'
    retxt += '.png|32px|link=]]</div>'
    return retxt

def create_miniimage_with_link(json_base):
    if '迷你图片' in json_base and json_base['迷你图片'] != '':
        retxt = '[[file:' + json_base['迷你图片'] + '|x24px|link=]] [[' + json_base['页面名'] + ']]'
    else:
        retxt = '[[' + json_base['页面名'] + ']]'
    return retxt


def create_navboxunit(json_base):
    lists = ['', '', '', '', '', '', '']
    for i, v in json_base['非英雄单位'].items():
        if v['应用'] == 1:
            if v["远古单位"]["1"]["1"] == 1:
                if len(lists[0]) > 0:
                    lists[0] += '&nbsp;{{!}}&nbsp;'
                lists[0] += create_miniimage_with_link(v)
            elif v["英雄级单位"]["1"]["1"] == 1:
                if len(lists[1]) > 0:
                    lists[1] += '&nbsp;{{!}}&nbsp;'
                lists[1] += create_miniimage_with_link(v)
            elif v["中立生物"]["1"]["1"] == 1:
                if len(lists[2]) > 0:
                    lists[2] += '&nbsp;{{!}}&nbsp;'
                lists[2] += create_miniimage_with_link(v)
            elif v["召唤物"]["1"]["1"] == 1:
                if len(lists[3]) > 0:
                    lists[3] += '&nbsp;{{!}}&nbsp;'
                lists[3] += create_miniimage_with_link(v)
            elif v["单位关系类型"]["1"]["1"] == '守卫':
                if len(lists[4]) > 0:
                    lists[4] += '&nbsp;{{!}}&nbsp;'
                lists[4] += create_miniimage_with_link(v)
            elif v["类型"] == '士兵':
                if len(lists[5]) > 0:
                    lists[5] += '&nbsp;{{!}}&nbsp;'
                lists[5] += create_miniimage_with_link(v)
            elif v["类型"] == '建筑物':
                if len(lists[6]) > 0:
                    lists[6] += '&nbsp;{{!}}&nbsp;'
                lists[6] += create_miniimage_with_link(v)
    retxt = '|group1=远古生物|list1=' + lists[0] \
            + '|group2=英雄级单位|list2=' + lists[1] \
            + '|group3=中立生物|list3=' + lists[2] \
            + '|group4=召唤生物|list4=' + lists[3] \
            + '|group5=守卫|list5=' + lists[4] \
            + '|group6=士兵|list6=' + lists[5] \
            + '|group7=建筑物|list7=' + lists[6]
    return retxt


def create_page_logs(title, log_base, log_list, name_base):
    retxt = ''
    retxt += '<table class="wikitable" style="text-align:center;background:#333;width:300px;color:#fff;float:right;">\n<tr><th colspan=2>' + title + '</th></tr>' + '\n<tr><td>游戏本体</td><td>' + \
             log_base['游戏本体'] + '</td></tr>' + '\n<tr><td>更新日期</td><td>' + log_base['更新日期'] + '</td></tr>'
    if log_base['地图作者'] != '':
        retxt += '\n<tr><td>作者</td><td>' + log_base['地图作者'] + '</td></tr>'
    junior = False
    bools = False
    index_of_upgrade = -1
    for i in range(len(log_list)):
        v = log_list[i]
        for j in range(len(v)):
            w = v[j]
            if title == w:
                index_of_upgrade = i
                bools = True
                break
            if title == v[0] + '/' + w:
                index_of_upgrade = i
                junior = True
                bools = True
                break
        if bools:
            break
    if index_of_upgrade == -1:
        return '请前往[[data:版本更新.json]]添加当前版本号，以方便确认其前后版本。'
    else:
        if not junior:
            if index_of_upgrade == 0:
                retxt += '\n<tr><td colspan=2>当前版本为可考的最古老版本</td></tr>'
            else:
                retxt += '\n<tr><td>上一版本</td><td>[[' + log_list[index_of_upgrade - 1][0] + ']]</td></tr>'
            if index_of_upgrade == len(log_list) - 1:
                retxt += '\n<tr><td colspan=2>当前版本为最新版本</td></tr>'
            else:
                retxt += '\n<tr><td>下一版本</td><td>[[' + log_list[index_of_upgrade + 1][0] + ']]</td></tr>'
    if '次级版本' in log_base and len(log_base['次级版本']) > 0:
        retxt += '\n<tr><td>小更新</td><td>'
        for i in range(len(log_base['次级版本'])):
            if i > 0:
                retxt += '<br>'
            retxt += '[[' + log_base['次级版本'][i] + ']]'
    if '官网链接' in log_base and log_base['官网链接'] != '' and log_base['官网链接'] != '-':
        retxt += '\n<tr><td colspan=2>[' + log_base['官网链接'] + ' ' + log_base['官网链接'] + ']</td></tr>'
    retxt += '\n<tr><td colspan=2 style="text-align:right;font-size:85%">[[data:' + title + '.json|<i class="fa fa-database" aria-hidden="true"></i>]]</td></tr></table>'
    table_name = ["开头", '英雄', "物品", "中立生物", "建筑", "兵线", "通用", "结尾"]
    for i in range(len(table_name)):
        if table_name[i] in log_base:
            v = log_base[table_name[i]]
            if isinstance(v, dict) and '无标题' in v:
                if table_name[i] == '开头' or table_name[i] == '结尾':
                    titles = '=='
                else:
                    titles = '==='
                    retxt += '\n==' + table_name[i] + '=='
                for j0, w0 in v.items():
                    if j0 != '无标题':
                        retxt += '\n' + titles + j0 + titles
                    for j, w in w0.items():
                        if w[0] != '':
                            retxt += '\n===='
                            if w[1] != '':
                                retxt += '[[file:' + w[1] + '|x36px|link=' + w[0] + ']][[' + w[0] + ']]===='
                            else:
                                if w[0] in name_base:
                                    for k in name_base[w[0]]:
                                        if k[1] != '':
                                            retxt += '[[file:' + k[1] + '|x36px|link=' + k[0] + ']]'
                                    retxt += '[[' + name_base[w[0]][0][0] + '|' + w[0] + ']]===='
                                else:
                                    retxt += '<span class="dota_image_by_json_name" data-name="' + w[0] + '" data-img-height="36px"></span>[[' + w[0] + ']]===='
                        current_ul = 0
                        for k in range(2, len(w)):
                            x = w[k]
                            if x['文字'] != '':
                                if x['序列级数'] > current_ul:
                                    allul = int(x['序列级数']) - current_ul
                                    for l in range(allul):
                                        retxt += '\n'
                                        for tnumber in range(current_ul):
                                            retxt += '\t'
                                        retxt += '<ul>'
                                        current_ul += 1
                                elif x['序列级数'] < current_ul:
                                    allul = current_ul - int(x['序列级数'])
                                    for l in range(allul):
                                        current_ul -= 1
                                        retxt += '\n'
                                        for tnumber in range(current_ul):
                                            retxt += '\t'
                                        retxt += '</ul>'
                                if current_ul == 0:
                                    retxt += '\n' + x['文字'] + '\n'
                                else:
                                    retxt += '\n'
                                    for tnumber in range(current_ul):
                                        retxt += '\t'
                                    retxt += '<li>' + x['文字'] + '</li>'
                        allul = current_ul
                        for l in range(allul):
                            current_ul -= 1
                            retxt += '\n'
                            for tnumber in range(current_ul):
                                retxt += '\t'
                            retxt += '</ul>'
                        if len(w) > 3:
                            retxt += '\n<br>'
    retxt += '\n[[分类:版本更新]]'
    retxt += thanks_for_the_audience()
    return retxt


def create_2nd_logs(json_base, log_base, log_list, name, limit=10):
    now = 0
    retxt = ''
    for i in range(len(log_list) - 1, -1, -1):
        for j in range(len(log_list[i]) - 1, -1, -1):
            if j > 0:
                log_name = log_list[i][0] + '/' + log_list[i][j]
            else:
                log_name = log_list[i][j]
            if log_name in log_base and (limit == 0 or limit >= now):
                v = log_base[log_name]
                current_ul = 0
                for j, w in v.items():
                    if isinstance(w, dict):
                        for j2, w2 in w.items():
                            for k, x in w2.items():
                                showit = False
                                for l in range(2, len(x)):
                                    if x[0] != '' and x[0] in name:
                                        showit = True
                                    else:
                                        for m in range(len(x[l]['目标'])):
                                            showit = showit and x[l]['目标'][m] in name
                                    showit = showit and x[l]['文字'] != ''
                                    if showit:
                                        now += 1
                                        if current_ul == 0:
                                            if limit > 0:
                                                retxt += '<h4>[[' + log_name + ']]</h4>'
                                            else:
                                                retxt += '<h3>[[' + log_name + ']]\t<small>' + v['更新日期'] + '</small></h3>'
                                        if x[l]['序列级数'] > current_ul:
                                            for m in range(x[l]['序列级数'] - current_ul):
                                                retxt += '<ul>'
                                            current_ul = x[l]['序列级数']
                                        elif x[l]['序列级数'] < current_ul:
                                            for m in range(current_ul - x[l]['序列级数']):
                                                retxt += '</ul>'
                                            current_ul = x[l]['序列级数']
                                        retxt += '<li>' + x[l]['文字'] + '</li>'
                for m in range(current_ul):
                    retxt += '</ul>'
    if limit > 0:
        retxt += '<b>[[' + name[0] + '/版本改动|完整的更新内容请点此处查看……]]</b>'
    return retxt


def create_page_hero(json_base, log_base, log_list, hero):
    db = json_base['英雄'][hero]
    retxt = '__NOTOC__<div style="float:left;">' \
            + '<div class="bg-primary" style="margin-left:0px;margin-top:1em;display:block;height:48px;">' \
            + '<div class="heronavi" style="margin-bottom:0px">[[file:miniheroes_' + db["代码名"] + '.png|link=' + db["中文名"] + ']]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/英雄语音|英雄语音]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '#DotA|dota1资料]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/equipment|饰品]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/版本改动|完整改动]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '#旧有技能|旧有技能]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/攻略|攻略玩法]]</div>' \
            + '<div class="heronavi hidden-xs" style="float:right;padding:0px;">'
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in db["定位"]:
            retxt += create_role_set(db["定位"][i], str(db["定位等级"][i]))
        else:
            break
    retxt += '&nbsp;[[file:heroes_' + db["代码名"] + '.png|x48px|link=]]' \
             + '{{#ifexist:file:heroes_' + db["代码名"] + '_alt1.png|[[file:heroes_' + db["代码名"] + '_alt1.png|x48px|link=]]}}</div></div>' \
             + "<p>'''" + db["中文名"] + "'''（" + db["英文名"] + '）是Dota2中的一位' + db["主属性"]['1'] + '[[英雄]]。</p>' \
             + '{{#invoke:hero data|heroheroheader|' + db["中文名"] + '}}[[file:npc dota hero ' + db["代码名"] \
             + '.webm|300px|center|link=]]{{#invoke:hero data|heroherodata|' + db["中文名"] \
             + '}}{{#invoke:hero data|heroherojs}}[[category:' + db["主属性"]['1'] + '英雄]]' \
             + '<div style="line-height: 200%;">' \
             + '<h2>简介</h2>' \
             + db["简介"] \
             + '<h2>背景</h2>' \
             + '<h3>DotA</h3>'
    if "dota中文名" in db:
        retxt += '<div class="full-width-xs" style="padding:0.5em;display:block;">' \
                 + '<div style="float:left;margin-right:0.5em;">[[file:dota hero ' + db["代码名"] + '.png|link=|64px]]</div>' \
                 + '<div>' \
                 + '<div style="display:inline-block;">' + db["dota中文别名"] + '&nbsp;' + db["dota英文别名"] + '</div><br>' \
                 + '<div style="display:inline-block;margin-left:1em"><small>' + db["dota中文名"] + '&nbsp;' + db["dota英文名"] + '</small></div>' \
                 + '</div>' \
                 + '</div>'
    retxt += db["dota背景"] \
             + '<h3>DOTA2</h3>' \
             + db["背景"] \
             + '</div>' \
             + '</div>'
    for i in db['技能']:
        retxt += json_base['技能'][i]['具体展示']
    retxt += '\n==历史更新==\n' \
             + create_2nd_logs(json_base, log_base, log_list, all_the_names(db, json_base), 10) \
             + '\n==饰品==\n' \
             + '[[data:' + db["中文名"] + '/equipment|点击进入查看饰品信息]]' \
             + json_base['机制']['通用']['简单条目']['英雄导航']
    retxt += thanks_for_the_audience()
    rere = ''
    nums = 0
    for i in range(len(retxt)):
        if retxt[i] == '<':
            if retxt[i + 1] == '/':
                nums -= 1
            elif retxt[i + 1] == 'b' and retxt[i + 2] == 'r':
                nums += 0
            else:
                if retxt[i + 1] == 't' or retxt[i + 1] == 'd' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    rere += '<div class="dota_invisible_menu_item_at_right_of_the_screen">[[Data:' + hero + '.json|' + hero + ']]</div>'
    return rere


def create_page_unit(json_base, log_base, log_list, unit):
    db = json_base['非英雄单位'][unit]
    retxt = '__NOTOC__<div>' + db['具体展示'] + db["页面名"] + '是DOTA2中的一种'
    if db["远古单位"]["1"]["1"] == 1:
        retxt += '远古[[分类:远古单位]]'
    if db["英雄级单位"]["1"]["1"] == 1:
        retxt += '[[英雄级单位|英雄级]]单位[[分类:英雄级单位]][[分类:召唤物]]'
    if db["召唤物"]["1"]["1"] == 1:
        retxt += '召唤物[[分类:召唤物]]'
    if db["中立生物"]["1"]["1"] == 1:
        retxt += '[[中立生物]][[分类:中立生物]]'
    if db["类型"] == '建筑物':
        retxt += '[[建筑物]][[分类:建筑物]]'
    if db["单位关系类型"]["1"]["1"] == '守卫':
        retxt += '[[守卫]][[分类:守卫]][[分类:召唤物]]'
    elif db["单位关系类型"]["1"]["1"] != '默认':
        retxt += '[['+db["单位关系类型"]["1"]["1"]+']]'
    if "简介" in db and db["简介"] != '':
        retxt += '<br>' + db["简介"]
    if '1' in db['源技能']:
        retxt += '\n==召唤源技能==\n'
        for i, v in db['源技能'].items():
            if v in json_base['技能']:
                sdb = json_base['技能'][v]
                retxt += '<br>'+sdb['简易展示']
    unitgroup=[]
    for i,v in json_base['单位组'].items():
        if unit in v['全部单位']:
            unitgroup.append(i)
    if len(unitgroup)>0:
        retxt += '\n==所属单位组==\n<div class="dota_rotatey_transform_switch_content1">'
        for i in unitgroup:
            retxt += '<div>' + json_base['单位组'][i]['成员']['1']['具体展示'] + '</div>'
        retxt += '</div><div class="dota_rotatey_transform_switch_content0">'
        for i in unitgroup:
            retxt += '<div>' + json_base['单位组'][i]['成员']['1']['简易展示'] + '</div>'
    retxt += '</div>'
    if db["类型"] == '士兵':
        retxt += '[[分类:士兵]]'
    for i in db['技能']:
        retxt += json_base['技能'][i]['具体展示']
    retxt += '\n==历史更新==\n' + create_2nd_logs(json_base, log_base, log_list, all_the_names(db, json_base), 10) \
             + '<div>' + json_base['机制']['通用']['简单条目']['非英雄单位导航'] + '</div>[[分类:非英雄单位]]'
    retxt += thanks_for_the_audience()
    rere = ''
    nums = 0
    for i in range(len(retxt)):
        if retxt[i] == '<':
            if retxt[i + 1] == '/':
                nums -= 1
            elif retxt[i + 1] == 'b' and retxt[i + 2] == 'r':
                nums += 0
            else:
                if retxt[i + 1] == 't' or retxt[i + 1] == 'd' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    rere += '<div class="dota_invisible_menu_item_at_right_of_the_screen">[[Data:' + unit + '.json|' + unit + ']]</div>'
    return rere


def create_page_item(json_base, log_base, log_list, item):
    db = json_base['物品'][item]
    retxt = '__NOTOC__' + json_base['物品'][item]['具体展示'] + '<b>' + db["页面名"] + '</b>是DOTA2中的一种[[物品]]，可以在<b>"'
    for i, v in db['商店'].items():
        if i != '1':
            retxt += '、'
        retxt += db['商店'][i] + '[[分类:' + db['商店'][i] + '物品]]'
    retxt += '"</b>商店获得。<br>'
    for i, v in db['商店'].items():
        retxt += '<br><b>' + v + '商店</b>出售以下商品：<br><br>' + '<table style="font-size:16px;">'
        for j, w in db["同商店物品"][i].items():
            if int(j) % 4 == 1:
                retxt += '\n<tr>'
            retxt += '<td style="padding:6px;text-align:center;">[[file:' + w['图片'] + '|52px|center|link=' + w['物品名'] + ']][[' + w['物品名'] + ']]</td>'
            if int(j) % 4 == 0 or int(j) == len(db["同商店物品"][i]):
                retxt += '</tr>'
        retxt += '</table>'
    for i, v in json_base['物品'][item].items():
        if isinstance(v, dict) and '叠加' in v and v['叠加'] != '':
            all_the_item_name = []
            for j, w in json_base['物品'].items():
                if j != item and w['应用'] == 1 and i in w and w[i]['叠加'] == v['叠加']:
                    all_the_item_name.append([j, number_to_string(w[i]['1']) + w[i]['后缀']])
            retxt += '<br>多个{{I|' + item + '}}的【' + i + '】(' + number_to_string(v['1']) + v['后缀'] + ')不会叠加'
            if len(all_the_item_name) > 0:
                retxt += '，且和以下物品不叠加，仅取最高值生效：'
                for j in range(len(all_the_item_name)):
                    if j > 0:
                        retxt += '、'
                    retxt += '{{I|' + all_the_item_name[j][0] + '}}(' + all_the_item_name[j][1] + ')'
            retxt += '。'
    for i in db['技能']:
        retxt += json_base['技能'][i]['具体展示']
    retxt += '\n==历史更新==\n' + create_2nd_logs(json_base, log_base, log_list, all_the_names(db, json_base), 10) + '[[分类:物品]]'
    retxt += thanks_for_the_audience()
    rere = ''
    nums = 0
    for i in range(len(retxt)):
        if retxt[i] == '<':
            if retxt[i + 1] == '/':
                nums -= 1
            elif retxt[i + 1] == 'b' and retxt[i + 2] == 'r':
                nums += 0
            else:
                if retxt[i + 1] == 't' or retxt[i + 1] == 'd' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    rere += '<div class="dota_invisible_menu_item_at_right_of_the_screen">[[Data:' + item + '.json|' + item + ']]</div>'
    return rere

def create_all_chapter_page_mechnism(db):
    retxt = ''
    for i in db['内容']:
        titles = db['内容'][i]['标题级数']
        retxt += '\n'
        if titles > 0:
            for es in range(titles):
                retxt += '='
            retxt += i
            for es in range(titles):
                retxt += '='
            retxt += '\n'
        retxt +=create_one_chapter_content_page_mechnism(db['内容'][i])
    return retxt

def create_one_chapter_content_page_mechnism(db):
    retxt=''
    anotherbool = False
    for j in db['内容']:
        if anotherbool:
            retxt += '\n'
        else:
            anotherbool = True
        retxt += db['内容'][j]['内容'] + '\n'
    return retxt


def create_page_mechnism(json_base, log_base, log_list, mech):
    db = json_base['机制'][mech]
    retxt = ''
    if db['次级分类'] != '引用机制':
        if db['图片'] != '':
            retxt += '[[file:' + db['图片'] + '|120px|right]]'
    retxt += db['简述'] +create_all_chapter_page_mechnism(db)
    if db['次级分类'] != '引用机制':
        retxt += thanks_for_the_audience()
        if db['次级分类'] != '':
            retxt += '[[分类:' + db['次级分类'] + ']]'
        retxt += '<div class="dota_invisible_menu_item_at_right_of_the_screen">[[Data:' + mech + '/源.json|' + mech + '/源]]<br>[[Data:' + mech + '.json|' + mech + ']]</div>'
    rere = ''
    nums = 0
    for i in range(len(retxt)):
        if retxt[i] == '<':
            if retxt[i + 1] == '/':
                nums -= 1
            elif retxt[i + 1] == 'b' and retxt[i + 2] == 'r':
                nums += 0
            else:
                if retxt[i + 1] == 't' or retxt[i + 1] == 'd' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    return rere


def create_page_unitgroup(json_base, log_base, log_list, unitgroup):
    db = json_base['单位组'][unitgroup]
    retxt = ''
    if db['图片'] != '':
        retxt += '[[file:' + db['图片'] + '|120px|right]]\n'
    retxt += '==组信息==\n<div class="dota_rotatey_transform_switch_content1">'
    for i in db['成员']:
        retxt += '<div>' + db['成员'][i]['具体展示'] + '</div>'
    retxt += '</div><div class="dota_rotatey_transform_switch_content0">'
    for i in db['成员']:
        retxt += '<div>' + db['成员'][i]['简易展示'] + '</div>'
    retxt += '</div>'
    retxt+='\n==成员信息==\n'
    for i in db['全部单位']:
        if i in json_base['非英雄单位']:
            retxt+=json_base['非英雄单位'][i]['简易展示']
    retxt += thanks_for_the_audience()
    retxt += '[[分类:单位组]]'
    if db['次级分类'] != '':
        retxt += '[[分类:' + db['次级分类'] + ']]\n'
        if len(db['次级分类'])>=4 and db['次级分类'][-4:] == '中立营地':
            retxt += json_base['机制']['通用']['简单条目']['中立生物营地导航']
    retxt += '<div class="dota_invisible_menu_item_at_right_of_the_screen">[[Data:' + unitgroup + '.json|' + unitgroup + ']]</div>'

    return retxt

def thanks_for_the_audience():
    retxt='\n==感谢您的阅读==' \
          '\n以上内容均通过特殊方式上传，如果您觉得书写内容有误，需要修改，请通过以下方式告知我们：' \
          '\n#[[用户:Bobrobotsun]]、[[用户:Axiaosiris]]' \
          '\n#QQ群：539026033' \
          '\n#新浪微博：[https://weibo.com/u/5617043593 DotA中文wiki]'
    return retxt