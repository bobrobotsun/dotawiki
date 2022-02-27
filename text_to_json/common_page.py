import re
import math
from xpinyin import Pinyin
from text_to_json import hero, ability, edit_json
import mainwindow

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
def all_the_names(db, json_base, bool=True):
    relist = [db['页面名']]
    if '曾用名' in db:
        for i in db['曾用名']:
            relist.append(i)
    if '技能' in db:
        for i in db['技能']:
            if i not in relist:
                relist += all_the_names(json_base['技能'][i], json_base, False)
    if bool and '源技能' in db:
        for i in db['源技能']:
            v = db['源技能'][i].lstrip('#')
            if v in json_base['技能'] and v not in relist:
                relist += all_the_names(json_base['技能'][v], json_base, bool)
    if '技能召唤物' in db:
        for i in db['技能召唤物']:
            if i not in relist:
                relist += all_the_names(json_base['非英雄单位'][i], json_base, False)
    if bool and '技能归属' in db and db['技能归属'] in json_base['物品']:
        v = db['技能归属']
        if v not in relist:
            relist += all_the_names(json_base['物品'][v], json_base, False)
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


def create_upgrade_text(numjsons, k, post_each=lambda x: x['后缀'] if '后缀' in x else '', post_group=lambda x, y: '', image_size=''):
    if image_size != '' and '|' not in image_size:
        print('报错')
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
                        retext += image_with_tip_with_link(numjson[i]['升级来源'][j]["图片"],numjson[i]['升级来源'][j]["名称"],False)
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


def nocheck_create_upgrade_text(numjson, post_each=lambda x: x['后缀'] if '后缀' in x else '', post_group=lambda x, y: '', image_size=''):
    if image_size != '' and '|' not in image_size:
        print('报错')
    retext = ''
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in numjson:
            if ii > 1:
                for j in numjson[i]['升级来源']:
                    retext += image_with_tip_with_link(numjson[i]['升级来源'][j]["图片"],numjson[i]['升级来源'][j]["名称"],False)
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
                    retxt += image_with_tip_with_link(w["图片"],w["名称"],False)
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


def create_role_set(role, level):
    retxt = ''
    image=''
    if role == '核心':
        image += 'carry'
    elif role == '爆发':
        image += 'nuker'
    elif role == '先手':
        image += 'initiator'
    elif role == '控制':
        image += 'disabler'
    elif role == '耐久':
        image += 'durable'
    elif role == '逃生':
        image += 'escape'
    elif role == '辅助':
        image += 'support'
    elif role == '打野':
        image += 'jungler'
    elif role == '推进':
        image += 'pusher'
    image+='.png'
    retxt+=image_with_tip_with_link(image,number_to_string(level) + '级' + number_to_string(role),False,False,'h32')
    return retxt


def create_miniimage_with_link(json_base):
    return '{{小图片|' + json_base['页面名'] + '|text=1}}'


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


def create_page_logs(title, log_base, log_list):
    retxt = ''
    retxt += right_menu() + '<table class="wikitable" style="text-align:center;background:#333;width:300px;color:#fff;float:right;">\n<tr><th colspan=2>' \
             + title + '</th></tr>\n<tr><td>游戏本体</td><td>' + \
             log_base['游戏本体'] + '</td></tr>' + '\n<tr><td>更新日期</td><td>' + log_base['更新日期'] + '</td></tr>'
    if log_base['地图作者'] != '':
        retxt += '\n<tr><td>作者</td><td>' + log_base['地图作者'] + '</td></tr>'
    junior = False
    bools = False
    index_of_upgrade = -1
    index_of_index = -1
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
                index_of_index = j
                junior = True
                bools = True
                break
        if bools:
            break
    if index_of_upgrade == -1:
        return '请前往<span class="dota_create_link_to_wiki_page">data:版本更新.json</span>添加当前版本号，以方便确认其前后版本。'
    else:
        if junior:
            retxt += '\n<tr><td>大版本</td><td>[[' + log_list[index_of_upgrade][0] + ']]</td></tr>'
            if index_of_index > 1:
                retxt += '\n<tr><td>上一小版本</td><td>[[' + log_list[index_of_upgrade][0] + '/' + log_list[index_of_upgrade][index_of_index - 1] + ']]</td></tr>'
            if index_of_index < len(log_list[index_of_upgrade]) - 1:
                retxt += '\n<tr><td>下一小版本</td><td>[[' + log_list[index_of_upgrade][0] + '/' + log_list[index_of_upgrade][index_of_index + 1] + ']]</td></tr>'
        else:
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
    retxt += '\n<tr><td colspan=2 style="text-align:right;font-size:85%"><span class="dota_create_link_to_wiki_page" data-link-page-name="data:' + title + '.json">' \
             + '<i class="fa fa-database" aria-hidden="true"></i></span></td></tr></table>'
    table_name = ["开头", '英雄', "物品", "中立生物", "建筑", "兵线", "通用", "结尾"]
    for i in range(len(table_name)):
        if table_name[i] in log_base:
            v = log_base[table_name[i]]
            if isinstance(v, dict) and '无标题' in v:
                if table_name[i] == '开头' or table_name[i] == '结尾':
                    titles = '=='
                else:
                    titles = '==='
                    retxt += '\n==' + table_name[i] + '==\n<div class="dota_invisible_menu_item_at_right_of_the_screen">[[#' + table_name[i] + '|' + table_name[i] + ']]</div>'
                for j0, w0 in v.items():
                    if j0 != '无标题':
                        retxt += '\n' + titles + j0 + titles + '\n<div class="dota_invisible_menu_item_at_right_of_the_screen">[[#' + j0 + '|--' + j0 + ']]</div>'
                    for j, w in w0.items():
                        if w[0] != '':
                            retxt += '\n===={{大图片|' + w[0] + '|h36}}[[' + w[0] + ']]===='
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
                                show_text = ''
                                for y in x['标签']:
                                    if y in edit_json.version_label:
                                        show_text += '{{额外信息框|' + edit_json.version_label[y] + '|' + y + '}}'
                                    if y in edit_json.version_label2:
                                        show_text += '{{额外信息框|' + edit_json.version_label2[y] + '|' + y + '}}'
                                show_text += x['文字']
                                if current_ul == 0:
                                    retxt += '\n' + show_text + '\n'
                                else:
                                    retxt += '\n'
                                    for tnumber in range(current_ul):
                                        retxt += '\t'
                                    retxt += '<li>' + show_text + '</li>'
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
                                                retxt += '<h4><span class="dota_create_link_to_wiki_page">' + log_name + '</span></h4>'
                                            else:
                                                retxt += '<h3><span class="dota_create_link_to_wiki_page">' + log_name + '</span>\t<small>' + v['更新日期'] + '</small></h3>'
                                        if x[l]['序列级数'] > current_ul:
                                            for m in range(x[l]['序列级数'] - current_ul):
                                                retxt += '<ul>'
                                            current_ul = x[l]['序列级数']
                                        elif x[l]['序列级数'] < current_ul:
                                            for m in range(current_ul - x[l]['序列级数']):
                                                retxt += '</ul>'
                                            current_ul = x[l]['序列级数']
                                        show_text = ''
                                        for y in x[l]['标签']:
                                            if y in edit_json.version_label:
                                                show_text += '{{额外信息框|' + edit_json.version_label[y] + '|' + y + '}}'
                                            if y in edit_json.version_label2:
                                                show_text += '{{额外信息框|' + edit_json.version_label2[y] + '|' + y + '}}'
                                        show_text += x[l]['文字']
                                        retxt += '<li>' + show_text + '</li>'
                for m in range(current_ul):
                    retxt += '</ul>'
    if limit > 0:
        retxt += '<b><span class="dota_create_link_to_wiki_page" data-link-page-name="' + name[0] + '/版本改动">完整的更新内容请点此处查看……</span></b>'
    return retxt


def create_switch_log(log_base, log_list, name,title='', limit=10):
    retxt = ''
    button = ''
    content = ''
    log_len = 0
    log_show_list = []
    ub = ''
    for i in range(len(log_list) - 1, -1, -1):
        for j in range(len(log_list[i]) - 1, -1, -1):
            if j > 0:
                log_name = log_list[i][0] + '/' + log_list[i][j]
            else:
                log_name = log_list[i][j]
            if log_name in log_base:
                v = log_base[log_name]
                current_ul = 0
                new_log = True
                all_labels = []
                for j, w in v.items():
                    if isinstance(w, dict):
                        for j2, w2 in w.items():
                            for k, x in w2.items():
                                for l in range(2, len(x)):
                                    showit = False
                                    if x[0] != '' and x[0] in name:
                                        showit = True
                                    else:
                                        for m in range(len(x[l]['目标'])):
                                            showit = showit or x[l]['目标'][m] in name
                                    showit = showit and x[l]['文字'] != ''
                                    if showit:
                                        if new_log:
                                            button += '<div class="dota_dict_label_switch_content_by_click_button" data-display-len="2" data-check-key="' + log_name + '">' + log_name
                                            ub = log_name + '=1；' + ub
                                            content += '<div class="dota_dict_label_switch_content_by_click_content" data-check-key="' + log_name + '=1；" data-display-type="block">' \
                                                       + '<h3>[[' + log_name+'#'+title + '|' + log_name + ']]\t<small>' + v['更新日期'] + '</small></h3>'
                                            if log_len < limit or limit <= 0:
                                                log_show_list.insert(0, log_name)
                                            new_log = False
                                        log_len += 1
                                        if x[l]['序列级数'] > current_ul:
                                            for m in range(x[l]['序列级数'] - current_ul):
                                                content += '<ul>'
                                            current_ul = x[l]['序列级数']
                                        elif x[l]['序列级数'] < current_ul:
                                            for m in range(current_ul - x[l]['序列级数']):
                                                content += '</ul>'
                                            current_ul = x[l]['序列级数']
                                        show_text = ''
                                        all_labels.extend(x[l]['标签'])
                                        show_text += edit_json.change_label_list_to_text(x[l]['标签'], 'list')
                                        show_text += x[l]['文字']
                                        if current_ul > 0:
                                            content += '<li>' + show_text + '</li>'
                                        else:
                                            content += '<br>' + show_text
                if current_ul > 0:
                    for m in range(current_ul):
                        content += '</ul>'
                if not new_log:
                    button += edit_json.change_label_list_to_text(all_labels, count=True) + '</div>'
                    content += '</div>'
    ub = '<div class="dota_dict_label_switch_button_by_click_button" data-check-dict="' + ub + '">全部显示</div>'
    if log_len > 0:
        retxt += '<div class="dota_dict_label_switch_content_by_click" data-display-dict="'
        for i in log_show_list:
            retxt += i + '=1；'
        retxt += '" data-need-new-tip="1">' + button + ub + '<div>' + content + '</div></div>'
        if limit == 0:
            retxt = right_menu() + retxt + '您可以点击上面的版本号按钮来快速查看对应的更新日志。'
        else:
            retxt += '<br><ul><li>您可以点击上面的版本号按钮来快速查看对应的更新日志，或者您可以<b>[[' + name[0] + '/版本改动|点此处查看完整的日志页面……]]</b></li></ul>'
    elif limit == 0:
        retxt += '你看，我说[[' + name[0] + '|《' + name[0] + '》]]没有更新日志，您还不信。<br>' \
                 + '实在不行，要不您先看看[[' + log_list[-1][0] + '|最新的更新日志：' + log_list[-1][0] + ']]'
    else:
        retxt += '没有查询到[[' + name[0] + '/版本改动|《' + name[0] + '》的更新日志]]'
    return retxt


def create_page_hero(json_base, log_base, log_list, hero):
    db = json_base['英雄'][hero]
    retxt = '__NOTOC__' + right_menu() + '<div style="float:left;">' \
            + '<div class="bg-primary" style="margin-left:0px;margin-top:1em;display:block;height:48px;">' \
            + '<div class="heronavi" style="margin-bottom:0px">{{小图片|' + db["页面名"] + '}}</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/英雄语音|英雄语音]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '#DotA|dota1资料]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/equipment|饰品]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/版本改动|完整改动]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '#旧有技能|旧有技能]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '/攻略|攻略玩法]]</div>' \
            + '<div class="heronavi" style="margin-bottom:0px">[[' + db["中文名"] + '#代码查询|代码查询]]</div>' \
            + '<div class="heronavi hidden-xs" style="float:right;padding:0px;">'
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in db["定位"]:
            retxt += create_role_set(db["定位"][i], str(db["定位等级"][i]))
        else:
            break
    retxt += '&nbsp;{{图片|heroes_' + db["代码名"] + '.png|h48}}' \
             + '{{图片|heroes_' + db["代码名"] + '_alt1.png|h48}}</div></div>' \
             + "<p><b>" + db["中文名"] + "</b>（" + db["英文名"] + '）是Dota2中的一位' + db["主属性"]['1'] + '<span class="dota_create_link_to_wiki_page">英雄</span>。</p>' \
             + db["具体展示"] \
             + '<div style="line-height: 200%;">' \
             + '<h2>简介</h2>' \
             + db["简介"] \
             + '<h2>背景</h2>' \
             + '<h3>DotA</h3>'
    if "dota中文名" in db:
        retxt += '<div class="full-width-xs" style="padding:0.5em;display:block;">' \
                 + '<div style="float:left;margin-right:0.5em;">{{图片|dota_hero_' + db["代码名"] + '.png|w64}}</div>' \
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
             + create_switch_log(log_base, log_list, all_the_names(db, json_base),hero) \
             + '<ul><li>或者你可以点击下列技能名字，来跳转到对应技能的日志页面：'
    for i in range(len(db['技能']) - 8):
        retxt += '{{H|' + db['技能'][i] + '|link=' + db['技能'][i] + '/版本改动}}'
    for i in ['10', '15', '20', '25']:
        retxt += '{{H|' + hero + i + '级天赋|link=' + hero + i + '级天赋/版本改动}}'
    retxt += '{{图片|talent.png}}[[' + hero + '/天赋/版本改动|' + hero + '全部天赋]]</li>'
    if len(db['删除技能']) > 0:
        retxt += '<li>或者您可以在此查询一些已经被删除的技能：'
        for i in db['删除技能']:
            retxt += '{{H|' + i + '}}'
        retxt += '</li>'
    retxt += '</ul>\n==饰品==\n' \
             + '<span class="dota_create_link_to_wiki_page" data-link-page-name="data:' + db["中文名"] + '/equipment">点击进入查看饰品信息</span>' \
             + '\n==代码查询==\n' \
             + '<ul><li>' + db['页面名'] + '：{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}、{{点击复制|<code>npc_dota_hero_' + db['代码名'] + '</code>|npc_dota_hero_' + db['代码名'] + '|td=0}}</li>'
    for i in db['技能']:
        retxt += '<li>' + i + '（' + json_base['技能'][i]['中文名'] + '）：{{点击复制|<code>' + json_base['技能'][i]['代码'] + '</code>|' + json_base['技能'][i]['代码'] + '|td=0}}</li>'
    retxt += '<li>[[常用测试指令#' + db['页面名'] + '|点击此处可以查看全部测试指令]]</li>'
    retxt += '</ul>\n'
    retxt += json_base['机制']['通用']['简单条目']['英雄导航']
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
                if retxt[i + 1] == 't' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    rere += '<div class="dota_invisible_menu_item_at_right_of_the_screen">[[#历史更新|更新日志]]<br>[[#代码查询|代码查询]]</div>'
    for i in db['标签']:
        rere += '[[分类:' + i + ']]'
    return rere


def create_page_unit(json_base, log_base, log_list, unit):
    db = json_base['非英雄单位'][unit]
    retxt = '__NOTOC__' + right_menu() + '<div>' + db['具体展示'] + db["页面名"] + '是DOTA2中的一种'
    if db["远古单位"]["1"]["1"] == 1:
        retxt += '远古'
    if db["英雄级单位"]["1"]["1"] == 1:
        retxt += '<span class="dota_create_link_to_wiki_page" data-link-page-name="英雄级单位">英雄级</span>单位'
    if db["召唤物"]["1"]["1"] == 1:
        retxt += '召唤物'
    if db["中立生物"]["1"]["1"] == 1:
        retxt += '<span class="dota_create_link_to_wiki_page">中立生物</span>'
    if db["类型"] == '建筑物':
        retxt += '<span class="dota_create_link_to_wiki_page">建筑物</span>'
    if db["单位关系类型"]["1"]["1"] == '守卫':
        retxt += '<span class="dota_create_link_to_wiki_page">守卫</span>'
    elif db["单位关系类型"]["1"]["1"] != '默认':
        retxt += '<span class="dota_create_link_to_wiki_page">' + db["单位关系类型"]["1"]["1"] + '</span>'
    if "简介" in db and db["简介"] != '':
        retxt += '<br>' + db["简介"]
    if '1' in db['源技能']:
        retxt += '\n==召唤源技能==\n'
        for i, v in db['源技能'].items():
            if v in json_base['技能'] and json_base['技能'][v]['应用'] == db['应用']:
                retxt += '<span style="padding:0.5em;">' + json_base['技能'][v]['简易展示'] + '</span>'
    unitgroup = []
    for i, v in json_base['单位组'].items():
        if unit in v['全部单位']:
            unitgroup.append(i)
    if len(unitgroup) > 0:
        retxt += '\n==所属单位组==\n<div class="dota_rotatey_transform_switch_content1">'
        for i in unitgroup:
            retxt += '<div>' + json_base['单位组'][i]['成员']['1']['具体展示'] + '</div>'
        retxt += '</div><div class="dota_rotatey_transform_switch_content0">'
        for i in unitgroup:
            retxt += '<div>' + json_base['单位组'][i]['成员']['1']['简易展示'] + '</div>'
    retxt += '</div>'
    for i in db['技能']:
        retxt += json_base['技能'][i]['具体展示']
    retxt += '\n==历史更新==\n' + create_switch_log(log_base, log_list, all_the_names(db, json_base),unit) + '<ul>'
    if len(db['技能']) > 0:
        retxt += '<li>或者你可以点击下列技能名字，来跳转到对应技能的日志页面：'
        for i in range(len(db['技能'])):
            retxt += '{{H|' + db['技能'][i] + '|link=' + db['技能'][i] + '/版本改动}}'
        retxt += '</li>'
    if len(db['删除技能']) > 0:
        retxt += '<li>或者您可以在此查询一些已经被删除的技能：'
        for i in db['删除技能']:
            retxt += '{{H|' + i + '}}'
        retxt += '</li>'
    retxt += '</ul>\n==代码查询==\n' \
             + '<ul><li>' + db['页面名'] + '：</li><ul>'
    for i in db['代码名']:
        retxt += '<li>' + i + '：{{点击复制|<code>' + db['代码名'][i] + '</code>|' + db['代码名'][i] + '|td=0}}、{{点击复制|<code>npc_dota_' + db['代码名'][i] + '</code>|npc_dota_' + db['代码名'][i] + '|td=0}}</li>'
    retxt += '</ul>'
    for i in db['技能']:
        retxt += '<li>' + i + '（' + json_base['技能'][i]['中文名'] + '）：{{点击复制|<code>' + json_base['技能'][i]['代码'] + '</code>|' + json_base['技能'][i]['代码'] + '|td=0}}</li>'
    retxt += '</ul>'
    retxt += '<div>' + json_base['机制']['通用']['简单条目']['非英雄单位导航'] + '</div>'
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
                if retxt[i + 1] == 't' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    rere += '<div class="dota_invisible_menu_item_at_right_of_the_screen"><span class="dota_create_link_to_wiki_page" data-link-page-name="Data:' + unit + '.json">' + unit + '</span></div>'
    for i in db['标签']:
        rere += '[[分类:' + i + ']]'
    return rere


def create_page_item(json_base, log_base, log_list, item):
    db = json_base['物品'][item]
    retxt = '__NOTOC__' + right_menu() + json_base['物品'][item]['具体展示'] + '<b>' + db["页面名"] + '</b>是DOTA2中的一种<span class="dota_create_link_to_wiki_page">物品</span>，可以在<b>"'
    for i, v in db['商店'].items():
        if i != '1':
            retxt += '、'
        retxt += db['商店'][i]
    retxt += '"</b>商店获得。<br>'
    for i, v in db['商店'].items():
        retxt += '<br><b>' + v + '商店</b>出售以下商品：<br><br>' + '<table style="font-size:16px;">'
        for j, w in db["同商店物品"][i].items():
            if int(j) % 4 == 1:
                retxt += '\n<tr>'
            retxt += '<td style="padding:6px;text-align:center;">{{大图片|' + w['物品名'] + '|w52|link=1|center|text=1}}</td>'
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
                    retxt += '{{小图片|' + all_the_item_name[j][0] + '|text=1}}(' + all_the_item_name[j][1] + ')'
            retxt += '。'
    for i in db['技能']:
        retxt += json_base['技能'][i]['具体展示']
    retxt += '\n==历史更新==\n' + create_switch_log(log_base, log_list, all_the_names(db, json_base),item) + '<ul>'
    if len(db['技能']) > 0:
        retxt += '<li>或者你可以点击下列技能名字，来跳转到对应技能的日志页面：'
        for i in range(len(db['技能'])):
            retxt += '{{H|' + db['技能'][i] + '|link=' + db['技能'][i] + '/版本改动}}'
        retxt += '</li>'
    if len(db['删除技能']) > 0:
        retxt += '<li>或者您可以在此查询一些已经被删除的技能：'
        for i in db['删除技能']:
            retxt += '{{H|' + i + '}}'
        retxt += '</li>'
    retxt += '</ul>\n==代码查询==\n' \
             + '<ul><li>' + db['页面名'] + '：{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}、{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</li>'
    for i in db['技能']:
        retxt += '<li>' + i + '（' + json_base['技能'][i]['中文名'] + '）：{{点击复制|<code>' + json_base['技能'][i]['代码'] + '</code>|' + json_base['技能'][i]['代码'] + '|td=0}}</li>'
    retxt += '<li>[[常用测试指令#' + db['页面名'] + '|点击此处可以查看全部测试指令]]</li>'
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
                if retxt[i + 1] == 't' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    rere += '<div class="dota_invisible_menu_item_at_right_of_the_screen"><span class="dota_create_link_to_wiki_page" data-link-page-name="Data:' + item + '.json">' + item + '</span></div>'
    for i in db['标签']:
        rere += '[[分类:' + i + ']]'
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
        retxt += create_one_chapter_content_page_mechnism(db['内容'][i])
    return retxt


def create_one_chapter_content_page_mechnism(db):
    retxt = ''
    for j in db['内容']:
        retxt += db['内容'][j]['内容'] + '\n'
    return retxt


def create_page_normal_ability(json_base, log_base, log_list, ability):
    db = json_base['技能'][ability]
    retxt = ''
    retxt += '您当前进入的页面是{{H|' + db['技能归属'] + '}}的技能{{H|' + ability + '}}的更新日志页面。'\
             +'<span class="dota_click_infomation_hide_and_seek"><span class="dota_click_infomation_hide_and_seek_button" style="border:1px black solid;background-color:#fff">点击显示技能详情</span>'\
             +'<div class="dota_click_infomation_hide_and_seek_frame" data-display-type="block">'+db['具体展示']+'</div></span>'\
             +'\n'+ create_switch_log(log_base, log_list, all_the_names(db, json_base, False),db['技能归属'], 0) + thanks_for_the_audience()
    retxt += '[[分类:更新日志]]'
    return retxt


def create_page_talent_ability(json_base,log_base, log_list, hero, talent_type, talent_names):
    retxt = '您当前进入的页面是{{H|' + hero + '}}的'
    if talent_type == '':
        retxt += '全部{{图片|talent.png}}天赋的更新日志页面。<br>\n'\
                 +'<div style="max-width:500px;display:grid;grid-template-columns:1fr 30px 1fr;">' \
              + '<div class="border_black">' + json_base['技能'][hero + '25级左天赋']['中文名'] \
              + '</div><div class="bgc_black">25</div><div class="border_black">' + json_base['技能'][hero + '25级右天赋']['中文名'] + '</div>' \
              + '<div class="border_black">' + json_base['技能'][hero + '20级左天赋']['中文名'] \
              + '</div><div class="bgc_black">20</div><div class="border_black">' + json_base['技能'][hero + '20级右天赋']['中文名'] + '</div>' \
              + '<div class="border_black">' + json_base['技能'][hero + '15级左天赋']['中文名'] \
              + '</div><div class="bgc_black">15</div><div class="border_black">' + json_base['技能'][hero + '15级右天赋']['中文名'] + '</div>' \
              +'<div class="border_black">' + json_base['技能'][hero + '10级左天赋']['中文名'] \
              + '</div><div class="bgc_black">10</div><div class="border_black">' + json_base['技能'][hero + '10级右天赋']['中文名'] + '</div>' \
              + '</div><br>\n'
    else:
        retxt += '{{H|' + hero + talent_type + '级左天赋}}（'+json_base['技能'][hero + talent_type + '级左天赋']['中文名']\
                 +'）{{H|' + hero + talent_type + '级右天赋}}（'+json_base['技能'][hero + talent_type + '级右天赋']['中文名']+'）的更新日志页面。<br>\n'
    retxt += create_switch_log(log_base, log_list, talent_names,hero, 0) + thanks_for_the_audience()
    retxt += '[[分类:更新日志]]'
    return retxt


def create_page_old_ability(json_base, log_base, log_list, ability):
    db = json_base['技能'][ability]
    retxt = ''
    retxt += '您当前进入的页面是一个陈旧的、被删除的技能。考虑到它可能无法呈现在{{H|' + db['技能归属'] + '}}的页面上，因此我们将其所有的信息保存在它们自己的页面上。您将在此看到这个技能在删除前的最后一个版本的数据，和它的更新日志。\n\n' + db['具体展示'] \
             + '\n==历史更新==\n' + create_switch_log(log_base, log_list, all_the_names(db, json_base, False),db['技能归属'], 0) + thanks_for_the_audience()
    for i in db['标签']:
        retxt += '[[分类:' + i + ']]'
    return retxt


def create_page_mechnism(json_base, log_base, log_list, mech):
    db = json_base['机制'][mech]
    retxt = right_menu()
    if db['次级分类'] != '引用机制':
        if db['图片'] != '':
            retxt += '{{图片|' + db['图片'] + '|w' + db['图片大小'] + '|right}}'
    retxt += db['简述'] + create_all_chapter_page_mechnism(db)
    if db['次级分类'] != '引用机制':
        retxt += '\n==历史更新==\n' + create_switch_log(log_base, log_list, all_the_names(db, json_base),mech)
        retxt += thanks_for_the_audience()
        retxt += '<div class="dota_invisible_menu_item_at_right_of_the_screen"><span class="dota_create_link_to_wiki_page" data-link-page-name="Data:' + mech + '/源.json">' \
                 + mech + '/源</span><br><span class="dota_create_link_to_wiki_page" data-link-page-name="Data:' + mech + '.json">' + mech + '</span></div>'
    rere = ''
    nums = 0
    for i in range(len(retxt)):
        if retxt[i] == '<':
            if retxt[i + 1] == '/':
                nums -= 1
            elif retxt[i + 1] == 'b' and retxt[i + 2] == 'r':
                nums += 0
            else:
                if retxt[i + 1] == 't' or retxt[i + 1] == 'h' or retxt[i + 1] == 'l':
                    rere += '\n'
                    for j in range(nums):
                        rere += '\t'
                nums += 1
        rere += retxt[i]
    for i in db['标签']:
        rere += '[[分类:' + i + ']]'
    return rere


def create_page_unitgroup(json_base, log_base, log_list, unitgroup):
    db = json_base['单位组'][unitgroup]
    retxt = right_menu()
    if db['图片'] != '':
        retxt += '{{图片|' + db['图片'] + '|w120|right}}\n'
    retxt += '==组信息==\n<div class="dota_rotatey_transform_switch_content1">'
    for i in db['成员']:
        retxt += '<div>' + db['成员'][i]['具体展示'] + '</div>'
    retxt += '</div><div class="dota_rotatey_transform_switch_content0">'
    for i in db['成员']:
        retxt += '<div>' + db['成员'][i]['简易展示'] + '</div>'
    retxt += '</div>'
    retxt += '\n==成员信息==\n'
    for i in db['全部单位']:
        if i in json_base['非英雄单位']:
            retxt += json_base['非英雄单位'][i]['简易展示']
    temp = ''
    for i, v in db['单位来源'].items():
        if v in json_base['技能']:
            temp += json_base['技能'][v]['简易展示']
    if temp != '':
        retxt += '\n==单位来源==\n' + temp
    retxt += '\n==历史更新==\n' + create_switch_log(log_base, log_list, all_the_names(db, json_base),unitgroup)
    retxt += thanks_for_the_audience()
    if db['次级分类'] != '':
        retxt += '\n'
        if len(db['次级分类']) >= 4 and db['次级分类'] == '中立生物营地':
            retxt += json_base['机制']['通用']['简单条目']['中立生物营地导航']
    retxt += '<div class="dota_invisible_menu_item_at_right_of_the_screen"><span class="dota_create_link_to_wiki_page" data-link-page-name="Data:' \
             + unitgroup + '.json">' + unitgroup + '</span></div>'
    for i in db['标签']:
        retxt += '[[分类:' + i + ']]'
    return retxt


def create_hero_choose_element(json_base, args, dict, post):
    args.insert(1, '')
    retxt = ''
    retxt += '<div class="dota_dict_label_switch_content_by_click" data-display-dict="简易拼音=1；">' \
             + '<div class="dota_compound_list_select_input_button_empty">↑↑删除框内内容↑↑</div>' \
             + '<span class="dota_stretch_out_and_draw_back" data-stretch-attri-dict="' + dict + '">' \
             + '<span class="dota_stretch_out_and_draw_back_input dota_compound_number_input"></span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="简易拼音" data-display-len="3">拼音</span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="完整英文" data-display-len="3">英文</span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="完整代码" data-display-len="3">代码</span>'
    for i in ['近战', '远程']:
        retxt += '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element"' \
                 + ' data-check-key="' + i + '" data-display-len="3">' + i + '</span>'
    for i in ['力量', '敏捷', '智力', '生命值', '魔法值', '生命恢复', '魔法恢复', '攻击力', '攻击速度', '攻击前摇', '护甲', '移动速度', '弹道速度']:
        retxt += '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element"' \
                 + ' data-check-key="总' + i + '" data-display-len="3">' + i + '</span>'
    retxt += '</span>'
    all_kind = {'天辉力量':'','天辉敏捷':'','天辉智力':'','夜魇力量':'','夜魇敏捷':'','夜魇智力':''}
    for i in json_base['英雄']:
        if json_base['英雄'][i]['应用'] == 1:
            args[1] = i
            kind=json_base['英雄'][i]['阵营']['1']+json_base['英雄'][i]['主属性']['1']
            all_kind[kind]+= '<span class="dota_compound_list_select_input_button dota_dict_label_switch_content_by_click_content dota_hero_comprehensive_attri_dict_hero"' \
                     + ' data-select-input-text="' + i + '"  data-check-key-name="hero-comprehensive-attri-dict" data-hero-name="' + i + '"' \
                     + ' style="border:1px black solid;margin:2px;text-align:center;">' \
                     + '{{' + '|'.join(args) + '}}' + post + '</span>'
    retxt += '<div style="display: grid;grid-template-columns:repeat(auto-fill,minmax(358px,1fr));">'
    for i in all_kind:
        retxt += '<span class="dota_simple_label_exchange_fieldset" data-fieldset-legend="' + i + '">' + all_kind[i] + '</span>'
    retxt += '</div></div>'
    return retxt


def create_item_choose_element(json_base, args, dict, post):
    args.insert(1, '')
    retxt = ''
    p = Pinyin()
    all_shop = {}
    retxt += '<div class="dota_dict_label_switch_content_by_click" data-display-dict="价格=1；">' \
             + '<div class="dota_compound_list_select_input_button_empty">↑↑删除框内内容↑↑</div>' \
             + '<span class="dota_stretch_out_and_draw_back" data-stretch-attri-dict="' + dict + '">' \
             + '<span class="dota_stretch_out_and_draw_back_input dota_compound_number_input"></span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="价格" data-display-len="3">价格</span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="简易拼音" data-display-len="3">拼音</span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="完整代码" data-display-len="3">代码</span>'
    for i in edit_json.item_shop:
        all_shop[i] = ''
    for i in edit_json.edit_adition['物品属性']:
        retxt += '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element"' \
                 + ' data-check-key="' + i + '" data-display-len="3">' + i + '</span>'
    retxt += '</span>'
    for i in json_base['物品']:
        if json_base['物品'][i]['应用'] == 1:
            temp = '<span class="dota_compound_list_select_input_button dota_dict_label_switch_content_by_click_content" data-select-input-text="' + i + '" data-check-key="' \
                   + '价格=' + ability.better_float_to_text(json_base['物品'][i]['价格']['1']) + '；简易拼音=' + p.get_pinyin(i).replace('-', '')[:3] + '；完整代码=' + json_base['物品'][i]['代码名'] + '；'
            for j in edit_json.edit_adition['物品属性']:
                if j in json_base['物品'][i]:
                    temp += j + '=' + ability.better_float_to_text(json_base['物品'][i][j]['1']) + '；'
            args[1] = i
            temp += '" style="border:1px black solid;margin:2px;text-align:center;">{{' + '|'.join(args) + '}}' + post + '</span>'
            for j in json_base['物品'][i]['商店']:
                w = json_base['物品'][i]['商店'][j]
                if w in all_shop:
                    all_shop[w] += temp
                else:
                    all_shop[w] = temp
    retxt += '<div style="display: grid;grid-template-columns:repeat(auto-fill,minmax(358px,1fr));">'
    for i in all_shop:
        retxt += '<span class="dota_simple_label_exchange_fieldset" data-fieldset-legend="' + i + '">' + all_shop[i] + '</span>'
    retxt += '</div></div>'
    return retxt


def create_delete_item_choose_element(json_base, args, post):
    args.insert(1, '')
    retxt = ''
    for i in json_base['物品']:
        if json_base['物品'][i]['应用'] != 1:
            args[1] = i
            retxt += '<span style="border:1px black solid;margin:2px;text-align:center;display: inline-block;">{{' + '|'.join(args) + '}}' + post + '</span>'
    retxt += ''
    return retxt


def create_neutral_item_choose_element(json_base, args, dict, post):
    args.insert(1, '')
    retxt = ''
    p = Pinyin()
    all_shop = {}
    retxt += '<div class="dota_dict_label_switch_content_by_click" data-display-dict="价格=1；'
    retxt += '"><div class="dota_compound_list_select_input_button_empty">↑↑删除框内内容↑↑</div>' \
             + '<span class="dota_stretch_out_and_draw_back" data-stretch-attri-dict="' + dict + '">' \
             + '<span class="dota_stretch_out_and_draw_back_input dota_compound_number_input"></span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="价格" data-display-len="3">中立等级</span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="简易拼音" data-display-len="3">拼音</span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="完整代码" data-display-len="3">代码</span>'
    for i in range(5):
        all_shop['中立第' + str(i + 1) + '级'] = ''
    for i in edit_json.item_shop:
        retxt += '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element"' \
                 + ' data-check-key="' + i + '" data-display-len="3">' + i + '</span>'
    for i in edit_json.edit_adition['物品属性']:
        retxt += '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element"' \
                 + ' data-check-key="' + i + '" data-display-len="3">' + i + '</span>'
    retxt += '</span><div>'
    for i in json_base['物品']:
        if json_base['物品'][i]['应用'] == 1 and json_base['物品'][i]['商店']['1'][:3] == '中立第':
            temp = '<span class="dota_compound_list_select_input_button dota_dict_label_switch_content_by_click_content" data-select-input-text="' + i + '" data-check-key="' \
                   + '价格=' + ability.better_float_to_text(json_base['物品'][i]['价格']['1']) + '；简易拼音=' + p.get_pinyin(i).replace('-', '')[:3] + '；完整代码=' + json_base['物品'][i]['代码名'] + '；'
            for j in edit_json.edit_adition['物品属性']:
                if j in json_base['物品'][i]:
                    temp += j + '=' + ability.better_float_to_text(json_base['物品'][i][j]['1']) + '；'
            args[1] = i
            temp += '" style="border:1px black solid;margin:2px;text-align:center;">{{' + '|'.join(args) + '}}' + post + '</span>'
            for j in json_base['物品'][i]['商店']:
                w = json_base['物品'][i]['商店'][j]
                if w in all_shop:
                    all_shop[w] += temp
                else:
                    all_shop[w] = temp
    retxt += '<div style="display: grid;grid-template-columns:repeat(auto-fill,minmax(358px,1fr));">'
    for i in all_shop:
        retxt += '<span class="dota_simple_label_exchange_fieldset" data-fieldset-legend="' + i + '">' + all_shop[i] + '</span>'
    retxt += '</div></div>'
    return retxt


def create_delete_neutral_item_choose_element(json_base, args, post):
    args.insert(1, '')
    retxt = ''
    for i in json_base['物品']:
        if json_base['物品'][i]['应用'] != 1 and json_base['物品'][i]['商店']['1'][:3] == '中立第':
            args[1] = i
            retxt += '<span style="border:1px black solid;margin:2px;text-align:center;display: inline-block;">{{' + '|'.join(args) + '}}' + post + '</span>'
    retxt += ''
    return retxt


def create_version_choose_element(list, base, dict):
    retxt = ''
    retxt += '<div class="dota_dict_label_switch_content_by_click" data-display-dict="版本号=2；">' \
             + '<div class="dota_compound_list_select_input_button_empty">↑↑删除框内内容↑↑</div>' \
             + '<span class="dota_stretch_out_and_draw_back" data-stretch-attri-dict="' + dict + '">' \
             + '<span class="dota_stretch_out_and_draw_back_input dota_compound_number_input"></span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="版本号" data-display-len="3">版本号</span>' \
             + '<span class="dota_dict_label_switch_content_by_click_button dota_stretch_out_and_draw_back_element" data-check-key="时间" data-display-len="3">时间</span>'
    retxt += '</span><div>'
    for i in list:
        for j in range(len(i)):
            version_name = i[0]
            if j > 0:
                version_name += '/' + i[j]
            if version_name in base:
                db = base[version_name]
                retxt += '<span class="dota_compound_list_select_input_button dota_dict_label_switch_content_by_click_content"' \
                         + ' data-select-input-text="' + version_name + '" data-check-key="版本号=' + version_name + '.；时间=' + db['更新日期'] + '；"' \
                         + ' style="border:1px black solid;margin:2px;text-align:center;">' \
                         + version_name + '</span>'
    retxt += '</div></div>'
    return retxt

def image_with_tip_with_link(image, name, black=True,text_link=True,image_size='h18'):
    retxt = ''
    retxt += '{{额外信息框|{{图片|'
    if black:
        retxt += image.replace('Talent.png', 'Talentb.png')
    else:
        retxt += image
    retxt += '|' + image_size + '}}|'
    if text_link:
        retxt += '[['+name+']]'
    else:
        retxt += name
    retxt += '}}'
    return retxt

def right_menu(a='#', b='↑↑置顶↑↑'):
    return '<div class="dota_invisible_menu_item_at_right_of_the_screen">[[' + a + '|' + b + ']]</div>'


def thanks_for_the_audience():
    retxt = '\n==感谢您的阅读==' \
            '\n以上内容均通过特殊方式上传，如果您觉得书写内容有误，需要修改，请通过以下方式告知我们：' \
            '\n#[[用户:Bobrobotsun]]、[[用户:Axiaosiris]]' \
            '\n#QQ群：539026033' \
            '\n#新浪微博：[https://weibo.com/u/5617043593 DotA中文wiki]'
    return retxt
