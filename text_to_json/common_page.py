import re

target_url = 'https://dota.huijiwiki.com/w/api.php'


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


def create_upgrade_text(numjsons, k, post_each=lambda x: x['后缀'] if '后缀' in x else '', post_group=lambda x: ''):
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
                        retext += '[[file:' + numjson[i]['升级来源'][j]["图片"] + '|x22px|link=' + numjson[i]['升级来源'][j][
                            "名称"] + ']]'
                jj = 0
                while True:
                    jj += 1
                    j = str(jj)
                    if j in numjson[i]:
                        if jj > 1:
                            retext += "/"
                        try:
                            if float(int(numjson[i][j])) == float(numjson[i][j]):
                                retext += str(int(numjson[i][j]))
                            else:
                                retext += str(numjson[i][j])
                            retext += post_each(numjsons[k])
                        except ValueError:
                            retext += str(numjson[i][j])
                    else:
                        break
                retext += post_group(numjson)
            else:
                break
        return retext
    else:
        return ''


def create_upgrade_cast_style(db):
    retxt = ''
    for ii in range(1, 5):
        i = str(ii)
        if i in db:
            retxt += '<div style="padding:0.25em 0.5em;text-align:center;">'
            if ii > 1:
                jj = 0
                while True:
                    jj += 1
                    j = str(jj)
                    if j in db[i]["升级来源"]:
                        w = db[i]["升级来源"][j]
                        retxt += '[[file:' + w["图片"] + '|x22px|link=' + w["名称"] + ']]'
                    else:
                        break
            jj = 0
            while True:
                jj += 1
                j = str(jj)
                if j in db[i]:
                    w = db[i][j]
                    retxt += '<span class="ability_indicator" style="background:#1166cc;color:white;">' + w[
                        "值"] + '</span>'
                else:
                    break
            retxt += '</div>'
    return retxt


def create_upgrade_cast_target(db):
    retxt = ''
    for h in range(1, 5):
        if str(h) in db:
            arr = db[str(h)]
            retxt += '<div style="padding:0.25em 0.5em;text-align:center;">' \
                     + '<table align="center"><tr><td style="padding:0.25em">'
            if h > 1:
                retxt += '<td>'
                ii = 0
                while True:
                    ii += 1
                    i = str(ii)
                    if i in arr["升级来源"]:
                        v = arr["升级来源"][i]
                        retxt += '[[file:' + v["图片"] + '|x22px|link=' + v["名称"] + ']]'
                    else:
                        break
            retxt += '</td>'
            ii = 0
            while True:
                ii += 1
                i = str(ii)
                if i in arr:
                    v = arr[i]
                    bool = True
                    if len(v) == 0:
                        bool = False
                    elif i == '不分类':
                        retxt += '<td style="padding:0.25em 0em;">'
                    elif i == '英雄':
                        retxt += '<td style="background:#000033;cursor:help;padding:0.5em 0em;" title="被视为英雄">'
                    elif i == '非英雄':
                        retxt += '<td style="background:#003300;cursor:help;padding:0.5em 0em;" title="被视为普通单位">'
                    else:
                        bool = False
                    if bool:
                        jj = 0
                        while True:
                            jj += 1
                            j = str(jj)
                            if j in v:
                                w = arr[j]
                                kk = 0
                                while True:
                                    kk += 1
                                    k = str(kk)
                                    if k in w:
                                        x = arr[k]
                                        retxt += '<span class="ability_indicator" style="cursor:help;background:' + w[
                                            "颜色"] + ';color:white;" title="(' + w["值"] + ')'
                                        ll = 0
                                        while True:
                                            ll += 1
                                            l = str(ll)
                                            if l in x:
                                                y = arr[l]
                                                if ll > 1:
                                                    retxt += ','
                                                retxt += y['值']
                                            else:
                                                break
                                        retxt += '">'
                                        if w['代码'] == 1 and x['代码'] == 1:
                                            retxt += '自身'
                                        else:
                                            retxt += x["值"]
                                        retxt += '</span>'
                                    else:
                                        break
                            else:
                                break
                        retxt += '</td>'
                else:
                    break
            retxt += '</tr></table></div>'
    return retxt


def create_upgrade_cast_point_backswing(arr1, arr2):
    retxt = ''
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in arr1:
            v = arr1[i]
            retxt += '<div style="padding:0.5em 0.5em 0em 1em">[[file:Ability cooldown.png|16px|link=]] 前后摇'
            if v['名称'] != '':
                retxt += '（' + v['名称'] + '）'
            if i in arr2 and arr2[i]['名称'] != '':
                retxt += '（' + arr2[i]['名称'] + '）'
            retxt += '： ' + create_upgrade_text(arr1, i, lambda x: '',
                                                lambda x: x['1']["即时生效"]['图片']['图片'] if x['1']["即时生效"][
                                                                                            '代码'] != 0 else '') + ' + ' \
                     + create_upgrade_text(arr2, i) + '</div>'
        else:
            break
    return retxt


def create_upgrade_manacost(arr):
    retxt = ''
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in arr:
            v = arr[i]
            retxt += '<div style="padding:0.5em 0.5em 0em 1em"><span style="cursor:help;" title="' + v[
                '名称'] + '">[[file:mana cost.png|16px|link=]]</span> '
            jj = 0
            while True:
                jj += 1
                j = str(jj)
                if j in v:
                    w = v[j]
                    if jj > 1:
                        retxt += '+'
                    retxt += '<span style="cursor:help;" title="' + w['1']['类型']['值'] + '">' \
                             + create_upgrade_text(v, j, lambda x: x['1']['类型']['后缀'] if '后缀' in x['1']['类型'] else '') \
                             + '</span>'
                else:
                    break
            retxt += '</div>'
        else:
            break
    return retxt


def create_upgrade_cooldown(arr):
    retxt = ''
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in arr:
            v = arr[i]
            bool = [False, False, False]
            for j in range(2, 5):
                bool[j - 2] = str(j) in v
            retxt += '<div style="padding:0.5em 0.5em 0em 1em;cursor:help;" title="' + v[
                '名称'] + '"><span style="cursor:help;" title="' \
                     + v['1']['类型']['值'] + '">[[file:' + v['1']['类型']['图片'] + '|16px|link=]]</span> '
            jj = 0
            while True:
                jj += 1
                j = str(jj)
                if j in v['1']:
                    if jj > 1:
                        retxt += '/'
                    retxt += str(v['1'][j])
                else:
                    break
            if bool[0] or bool[1]:
                retxt += '('
                for jj in range(2, 5):
                    j = str(jj)
                    if bool[jj - 2]:
                        kk = 0
                        while True:
                            kk += 1
                            k = str(kk)
                            if k in v[j]['升级来源']:
                                x = v[j]['升级来源'][k]
                                retxt += '[[file:' + x['图片'] + '|x18px|link=' + x['名称'] + ']]'
                            else:
                                break
                        retxt += '<span style="cursor:help;" title="' + v[j]['类型']['值'] + '">[[file:' \
                                 + v[j]['类型']['图片'] + '|16px|link=]]</span>'
                        kk = 0
                        while True:
                            kk += 1
                            k = str(kk)
                            if k in v[j]:
                                x = v[j][k]
                                if kk > 1:
                                    retxt += '/'
                                retxt += str(x)
                            else:
                                break
                retxt += ')'
            retxt += '</div>'
        else:
            break
    return retxt


def create_upgrade_buff(json_dict):
    buff_mech = {'技能免疫', '状态抗性', '无敌'}
    retxt = '<div style="paddin:0.5em;"><table>'
    for i in range(1, 5):
        if str(i) in json_dict:
            retxt += '<tr><td>'
            if i > 1:
                for j in json_dict[str(i)]['升级来源']:
                    retxt += '[[file:' + re.sub(r'talent.png', lambda x: 'talentb.png',
                                                json_dict[str(i)]['升级来源'][j]['图片']) + '|x22px|link=' + \
                             json_dict["名称"] + ']] '
            retxt += '</td><td style="padding:0.25em>'
            if '图片' in json_dict[str(i)] and json_dict[str(i)]['图片'] != '':
                retxt += '<span style="cursor:help;" title="' + json_dict[str(i)]['值'] + '">[[file:' + \
                         json_dict[str(i)]['图片'] + '|x22px|link=]]</span> '
            for j in buff_mech:
                if json_dict[str(i)][j]['代码'] != 0:
                    retxt += '<span style="cursor:help;" title="' + json_dict[str(i)][j]['简述'] + '">[[file:' + \
                             json_dict[str(i)][j]['图片'] + '|x22px|link=]]</span> '
            retxt += json_dict['名称'] + ' '
            if json_dict[str(i)]['驱散']['代码'] != 0:
                retxt += '<span class="ability_indicator" style="cursor:help;background:#2266dd;color:white;" title="' + \
                         json_dict[str(i)]['驱散']['简述'] + '">' + json_dict[str(i)]['驱散']['值'] + '</span>'
            for j in json_dict[str(i)]['叠加']:
                if json_dict[str(i)]['叠加'][j]['代码1'] != 0:
                    retxt += '<span class="ability_indicator" style="cursor:help;background:#2266dd;color:white;" title="' + \
                             json_dict[str(i)]['叠加'][j]['来源'] + '来源' + json_dict[str(i)]['叠加'][j]['方式'] + '">' + \
                             json_dict[str(i)]['叠加'][j]['方式'] + '</span>'
            for j in json_dict[str(i)]['标记']:
                if json_dict[str(i)]['标记'][j]['代码'] != 0:
                    retxt += '<span class="ability_indicator" style="background:#2266dd;color:white;">' + \
                             json_dict[str(i)]['标记'][j]['值'] + '</span>'
            if json_dict[str(i)]['生效从属']['代码'] > 1:
                retxt += '<span class="ability_indicator" style="background:#009688;color:white;" title="' + \
                         json_dict[str(i)]['生效从属']['简述'] + '">' + json_dict[str(i)]['生效从属']['值'] + '</span>'
            for j in json_dict[str(i)]['生效目标']:
                if len(json_dict[str(i)]['生效目标'][j]) > 0:
                    target_dict = json_dict[str(i)]['生效目标'][j]
                    if j == '不分类':
                        retxt += '<span style="padding:0.25em 0em;">'
                    elif j == '英雄':
                        retxt += '<span style="background:#d1ffd1;cursor:help;padding:0.5em 0em;" title="被视为英雄">'
                    elif j == '非英雄':
                        retxt += '<span style="background:#ffd1d1;cursor:help;padding:0.5em 0em;" title="被视为普通单位">'
                    kk = 0
                    while True:
                        kk += 1
                        k = str(kk)
                        if k in target_dict:
                            ll = 0
                            while True:
                                ll += 1
                                l = str(ll)
                                if l in target_dict[k]:
                                    retxt += '<span class="ability_indicator" style="cursor:help;background:' + \
                                             target_dict[k]["颜色"] + ';color:white;" title="(' + target_dict[k][
                                                 "值"] + ')'
                                    mm = 0
                                    while True:
                                        mm += 1
                                        m = str(mm)
                                        if m in target_dict[k][l]:
                                            if mm > 1:
                                                retxt += ','
                                            retxt += target_dict[k][l][m]['值']
                                        else:
                                            break
                                    retxt += '">'
                                    if target_dict[k]['代码'] == 1 and target_dict[k][l]['代码'] == 1:
                                        retxt += '自身'
                                    else:
                                        retxt += target_dict[k][l]['值']
                                    retxt += '</span>'
                                else:
                                    break
                        else:
                            break
                    retxt += '</span>'

            jj = 0
            while True:
                jj += 1
                j = str(jj)
                if j in json_dict[str(i)]:
                    if json_dict[str(i)][j]['名称'] != '':
                        if jj == 1:
                            retxt += '：包含'
                        else:
                            retxt += '，'
                        retxt += json_dict[str(i)][j]['名称']
                else:
                    break
            retxt += '</td></tr>'
    retxt += '</table></div>'
    return retxt


def create_upgrade_mech(json_dict):
    mech_mech = {'技能窃取', '即时攻击'}
    retxt = '<div style="paddin:0.5em;"><table>'
    for ii in range(1, 5):
        i = str(ii)
        if i in json_dict and json_dict[i]['代码'] != 0:
            retxt += '<tr><td>'
            if ii > 1:
                for j in json_dict[i]['升级来源']:
                    retxt += '[[file:' + re.sub(r'talent.png', lambda x: 'talentb.png',
                                                json_dict[i]['升级来源'][j]["图片"]) + '|x22px|link=' + \
                             json_dict[i]['升级来源'][j]["名称"] + ']] '
            retxt += '</td><td style="padding:0.25em><span style="cursor:help;">[[file:' + json_dict[i][
                '图片'] + '|x22px|link=]]</span> (' + json_dict[i]['值'] + ') '
            for j in mech_mech:
                if j in json_dict[i]:
                    kk = 0
                    while True:
                        kk += 1
                        k = str(kk)
                        if k in json_dict[i][j]:
                            if json_dict[i][j][k]['代码'] != 0:
                                retxt += '<span class="ability_indicator" style="cursor:help;background:#2266dd;color:white;" title="' + \
                                         json_dict[i][j][k]['简述'] + '">' + json_dict[i][j][k]['值'] + '</span> '
            retxt += '：' + json_dict[i]['简述'] + '</td></tr>'
    retxt += '</table></div>'
    return retxt


def create_page_ability(db):
    retxt = '<div style="display-block;clear:both;overflow: hidden;margin-bottom:1em;background-color: #d1d1d1;">' \
            + '<div style="float:left;">' \
            + '<div class="abilitybox full-width-xs" style="float:left;padding-bottom:1em;background:#222;color:#eee;width:400px;margin-right:8px;font-size:85%;">' \
            + '<div class="bg-primary" style="font-size:100%;background:'
    if db["次级分类"] == "终极技能":
        retxt += '#6c3d83'
    elif db["次级分类"] == "A杖技能":
        retxt += '#105aa7'
    else:
        retxt += '#803024'
    retxt += ';padding:0.5em;">'
    if db["传统按键"] != "":
        retxt += "<div style='background:#111;color:#fff;float:left;margin:0 0.1em;padding:0 0.2em;display:inline-block;border-radius:0px;' title='传统按键'>'''" + \
                 db["传统按键"] + "'''</div>"
    if db["默认按键"] != "":
        retxt += "<div style='background:#111;color:#fff;float:left;margin:0 0.1em;padding:0 0.2em;display:inline-block;border-radius:0px;' title='默认按键'>'''" + \
                 db["默认按键"] + "'''</div>"
    retxt += '<h4 id="' + db["代码"] + '"  style="font-weight:normal;padding:0px;margin:0px;display:inline-block;">' + db[
        "页面名"] + '</h4>' + '<span class="" style="float:right;font-size:125%">\'\'\'[[Data:' + db[
                 "数据来源"] + '/源.json|S]] [[Data:' + db[
                 "页面名"] + '.json|J]]\'\'\'</span><br/>' + '<span style="font-weight:normal;padding:0px;margin:0px;display:inline-block;">' + \
             db[
                 "中文名"] + '</span>' + '<span style="font-size:12px;color:#ccc;white-space: nowrap;padding: 2px; width:75px;overflow: hidden;text-overflow: ellipsis;text-align: center;"> ' + \
             db["英文名"] + '</span></div>'
    retxt += create_upgrade_cast_style(db["施法类型"])
    retxt += create_upgrade_cast_target(db["施法目标"])
    retxt += '<div>[[file:' + db["图片"] + '|160px|center|link=' + db['页面名'] + ']]</div>'
    if db['描述'] != '':
        retxt += '<div style="background:#111133;padding:1em;">' + db['描述'] + '</div>'
    if db['A杖信息'] != '':
        retxt += '<div style="background:#222266;padding:0.5em;">[[file:agha.png|x18px|link=]]：' + db['A杖信息'] + '</div>'
    if '技能升级信息' in db and '1' in db['技能升级信息']:
        retxt += '<div style="background:#222266;padding:0.25em;">'
        ii = 0
        while True:
            ii += 1
            i = str(ii)
            if i in db['技能升级信息']:
                v = db['技能升级信息'][i]
                retxt += '<div style="padding:0.25em;">[[file:' + v['图片'] + '|x18px|link=' + v['技能名'] + ']] [[' + v[
                    '技能名'] + ']]（' + v['中文名'] + ')</div>'
            else:
                break
        retxt += '</div>'
    retxt += create_upgrade_cast_point_backswing(db["施法前摇"], db["施法后摇"])
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in db["属性"]:
            v = db["属性"][i]
            if '名称' in v:
                v1 = v['名称']
            else:
                v1 = '名字没了'
            retxt += '<div style="padding:0.5em 0.5em 0em 1em">' + v1 + '：' + create_upgrade_text(db["属性"],
                                                                                                  i) + '</div>'
        else:
            break
    retxt += create_upgrade_manacost(db['魔法消耗']) + create_upgrade_cooldown(db['冷却时间'])
    if db['传说'] != '':
        retxt += '<div style="font-size:75%;padding:1em;border-top:1px solid #777;margin-top:1em;color:#bbb">「 ' + db[
            "传说"] + ' 」</div>'
    if db["次级分类"] == "A杖技能":
        retxt += '<div style="padding:0px 1em 0px 0px;float:right;font-size:14px;color:#4189d4">[[file:Agha.png|x18px|link=]]&nbsp;由阿哈利姆神杖获得</div>'
    retxt += '</div>' \
             + '<div style="font-size:16px;display:table;padding-left:4px;margin-bottom:24px;padding-right:0em;padding-top:1em;">' \
             + '<span style="margin-top:0px;padding-top:0px;font-size:120%"><big>\'\'\'技能详情\'\'\'</big></span><div>'
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in db['效果']:
            v = db['效果'][i]
            retxt += create_upgrade_buff(v)
        else:
            break
    for v in ['技能免疫', '无敌', '技能抵挡', '技能反弹', '技能共享', '技能窃取', '幻象', '破坏', '持续施法', '躲避', '缠绕', '即时攻击', '视野', '真实视域']:
        jj = 0
        while True:
            jj += 1
            j = str(jj)
            if j in db[v]:
                w = db[v][j]
                retxt += create_upgrade_mech(w)
            else:
                break
    retxt += '<div>'
    uls = 0
    if db['注释'] != '':
        ii = 0
        while True:
            ii += 1
            i = str(ii)
            if i in db['注释']:
                v = db['注释'][i]
                if v['序列级数'] > uls:
                    for j in range(1, v['序列级数'] - uls + 1):
                        retxt += '<ul>'
                    uls = v['序列级数']
                elif uls > v['序列级数']:
                    for j in range(1, uls - v['序列级数'] + 1):
                        retxt += '</ul>'
                    uls = v['序列级数']
                retxt += '<li>' + v['文字'] + '</li>'
            else:
                break
    for i in range(1, uls + 1):
        retxt += '</ul>'
    retxt += '</div></div></div></div>' + '{{#invoke:unit data|summon_unit_card|' + db['页面名'] + '}}' + '</div>'
    return retxt


def create_role_set(role, level):
    retxt = '<div style="margin:auto;display:inline-block" title="' + str(level) + '级' + str(role) + '">[[file:'
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


def create_navboxhero(json_base):
    lists = ['', '', '']
    for i in json_base['英雄']:
        j = 0
        if json_base['英雄'][i]['主属性']['1'] == '力量':
            j = 0
        elif json_base['英雄'][i]['主属性']['1'] == '敏捷':
            j = 1
        elif json_base['英雄'][i]['主属性']['1'] == '智力':
            j = 2
        lists[j] += '<span style="margin:0 6px;">[[file:' + json_base['英雄'][i]['迷你图片'] + '|link=' + json_base['英雄'][i]['页面名'] + ']]</span>'
    retxt = '|group1=力量|list1=' + lists[0] + '|group2=敏捷|list2=' + lists[1] + '|group3=智力|list3=' + lists[2]
    return retxt


def create_miniimage_with_link(json_base):
    if '迷你图片' in json_base and json_base['迷你图片'] != '':
        retxt = '[[file:' + json_base['迷你图片'] + '|x24px|link=]] [[' + json_base['页面名'] + ']]'
    else:
        retxt = '[[' + json_base['页面名'] + ']]'
    return retxt


def create_navboxunit(json_base):
    lists = ['', '', '', '', '', '']
    for i, v in json_base['非英雄单位'].items():
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
        elif "关联类型" in v and v["关联类型"] == '守卫':
            if len(lists[4]) > 0:
                lists[4] += '&nbsp;{{!}}&nbsp;'
            lists[4] += create_miniimage_with_link(v)
        elif v["类型"] == '士兵':
            if len(lists[5]) > 0:
                lists[5] += '&nbsp;{{!}}&nbsp;'
            lists[5] += create_miniimage_with_link(v)
    retxt = '|group1=远古生物|list1=' + lists[0] \
            + '|group2=英雄级单位|list2=' + lists[1] \
            + '|group3=中立生物|list3=' + lists[2] \
            + '|group4=召唤生物|list4=' + lists[3] \
            + '|group5=守卫|list5=' + lists[4] \
            + '|group6=士兵|list6=' + lists[5]
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
                        for k, x in w.items():
                            showit = False
                            for l in range(2, len(x)):
                                if x[0] == name:
                                    showit = True
                                else:
                                    for m in range(len(x[l]['目标'])):
                                        showit = showit and x[l]['目标'][m] == name
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
        retxt += '<b>[[' + name + '/版本改动|完整的更新内容请点此处查看……]]</b>'
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
                 + '<div style="display:inline-block;">' + db["dota中文别名"] + '&nbsp;' + db["dota英文别名"] + '</div><br/>' \
                 + '<div style="display:inline-block;margin-left:1em"><small>' + db["dota中文名"] + '&nbsp;' + db["dota英文名"] + '</small></div>' \
                 + '</div>' \
                 + '</div>'
    retxt += db["dota背景"] \
             + '<h3>DOTA2</h3>' \
             + db["背景"] \
             + '</div>' \
             + '</div>'
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in db['技能']:
            retxt += create_page_ability(json_base['技能'][db['技能'][i]])
        else:
            break
    retxt += '<h2>历史更新</h2>' \
             + create_2nd_logs(json_base, log_base, log_list, db["页面名"], 10) \
             + '<h2>饰品</h2>' \
             + '[[data:' + db["中文名"] + '/equipment|点击进入查看饰品信息]]' \
             + '{{navbox|title=DotA中的英雄|name=navboxhero|basestyle=max-width:800px;text-align:center;line-height:2em;' \
             + create_navboxhero(json_base) + '}}'
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


def create_page_unit(json_base, log_base, log_list, unit):
    db = json_base['非英雄单位'][unit]
    retxt = '__NOTOC__<div>{{#invoke:unit data|unitinfobox|' + db["页面名"] + '}}' + db["页面名"] + '是DOTA2中的一种'
    if db["远古单位"]["1"]["1"] == 1:
        retxt += '远古[[分类:远古单位]]'
    if db["英雄级单位"]["1"]["1"] == 1:
        retxt += '[[英雄级单位|英雄级]]单位[[分类:英雄级单位]][[分类:召唤物]]'
    if db["召唤物"]["1"]["1"] == 1:
        retxt += '召唤物[[分类:召唤物]]'
    if db["中立生物"]["1"]["1"] == 1:
        retxt += '[[中立生物]][[分类:中立生物]]'
    if "关联类型" in db and db["关联类型"] == '守卫':
        retxt += '[[守卫]][[分类:守卫]][[分类:召唤物]]'
    if "简介" in db and db["简介"] != '':
        retxt += '<br/>' + db["简介"]
    if db["中立生物"]["1"]["1"] == 1:
        # 这里有个东西，是关于野怪营地的东西，目前还没办法改动
        retxt += '<h2>营地</h2>{{#arraymap:{{#ask:[[Creep type::' + db['页面名'] + ']]|link=none}}|,|@@@|[[{{#ask:[[has subobject::@@@]]|?name|mainlabel=-|headers=hide}}]]}}'
    if db["召唤物"]["1"]["1"] == 1 or db["英雄级单位"]["1"]["1"] == 1 or db["关联类型"] == '守卫':
        retxt += '<h2>召唤源技能</h2>'
        for i, v in db['源技能'].items():
            if v in json_base['技能']:
                sdb = json_base['技能'][v]
                retxt += '<br/><div>[[' + v + ']]<br/>:[[file:' + sdb['图片'] + '|64px|link=' + sdb['页面名'] + '|left]]' + sdb['描述'] + '<br/><br/></div>'
    retxt += '</div>'
    if db["类型"] == '士兵':
        retxt += '[[分类:士兵]]'
    ii = 0
    while True:
        ii += 1
        i = str(ii)
        if i in db['技能']:
            retxt += create_page_ability(json_base['技能'][db['技能'][i]])
        else:
            break
    retxt += '<h2>历史更新</h2>' + create_2nd_logs(json_base, log_base, log_list, db["页面名"], 10) \
             + '<div>{{navbox|title=DotA中的非英雄单位|name=navbox minion' + create_navboxunit(json_base) + '}}</div>[[分类:非英雄单位]]'
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
