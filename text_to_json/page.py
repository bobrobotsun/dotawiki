import json, math
from text_to_json import edit_json

target_url = 'https://dota.huijiwiki.com/w/api.php'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}


def analyse_upload_json(text, upload_info):
    upload_info_json = upload_info.json()
    retxt = ''
    if 'edit' in upload_info_json and upload_info_json['edit']['result'] == 'Success':
        if 'nochange' in upload_info.json()['edit']:
            retxt = '《' + text + '》没有修改'
        elif 'oldrevid' in upload_info.json()['edit']:
            retxt = '《' + text + '》修改' + str(upload_info.json()['edit']['oldrevid']) + '为' + str(upload_info.json()['edit']['newrevid'])
        else:
            retxt = '《' + text + '》修改成功'
    else:
        retxt = '《' + text + '》修改失败'
    return retxt + '\n'


def create_upgrade_cast_text(numjsons, k):
    if k in numjsons:
        numjson = numjsons[k]
        retext = ''
        for i in numjson:
            if i == "2" or i == "4":
                retext += '<span class="dota_get_image_by_image_name" data-image-name="file:agha.png" data-image-link="阿哈利姆神杖"></span>'
            if i == "3" or i == "4":
                for j in numjson[i]['升级来源']:
                    retext += '<span class="dota_get_image_by_image_name" data-image-name="' + numjson[i]['升级来源'][j]["图片"] + '" data-image-link="' \
                              + numjson[i]['升级来源'][j]["名称"] + '"></span>'
            j = 1
            while True:
                if str(j) in numjson[i]:
                    if j > 1:
                        retext += "/"
                    try:
                        if float(int(numjson[i][str(j)])) == float(numjson[i][str(j)]):
                            retext += str(int(numjson[i][str(j)]))
                        else:
                            retext += str(numjson[i][str(j)])
                    except ValueError:
                        retext += str(numjson[i][str(j)])
                else:
                    break
                j += 1
            if '即时生效' in numjson[i] and int(numjson[i]['即时生效']['代码']) != 0:
                retext += numjson[i]['即时生效']['图片']['图片']
        return retext
    else:
        return ''


def calculate_armor_number_to_physical_resistance_percentage(armor):
    return min(0.06 * armor / (1 + 0.06 * abs(armor)) * 100, 100)


def calculate_physical_resistance_percentage_to_physical_health_percentage(pr):
    return str(round(10000 / (100 - pr), 1)) + '%' if pr < 100 else '无限'


def calculate_physical_damage_change_by_armor_change(pr, pr2):
    pr2 = min(pr2, 100)
    if pr2 >= 100:
        return '不再受伤' if pr < 100 else '皆不受伤'
    else:
        return str(round((pr - pr2) / (100 - pr) * 100, 1)) + '%' if pr < 100 else '重新受伤'

def common_code_chat_page(seesion, csrf_token,html_function):
    retxt=''
    retxt+='以下列表中{{点击复制|<code>代码样式文字</code>|代码样式文字|td=0}}均可以通过点击进行复制。\n'\
           +'<ul>'\
           +'<li>{{点击复制|<code>-gold</code> XX|-gold|td=0}}：获得金钱。</li>'\
           +'<ul><li>{{点击复制|<code>-gold 1000</code>|-gold 1000|td=0}}：获得1000金钱。</li>'\
           +'<li>{{点击复制|<code>-gold 99999</code>|-gold 99999|td=0}}：金钱最大化。</li></ul>'\
           +'<li>{{点击复制|<code>-lvlup</code> XX|-lvlup|td=0}}：自身等级升级。</li>'\
           +'<ul><li>{{点击复制|<code>-lvlup 6</code>|-lvlup 6|td=0}}：自身升6级。</li></ul>'\
           +'<li>{{点击复制|<code>-lvlmax</code>|-lvlmax|td=0}}：自身升到满级，技能自动学满。</li>'\
           +'<li>{{点击复制|<code>-levelbots</code> XX|-levelbots|td=0}}：所有机器人提升等级。</li>'\
           +'<ul><li>{{点击复制|<code>-levelbots 30</code>|-levelbots 30|td=0}}：所有机器人提升30级。</li></ul>'\
           +'<li>{{点击复制|<code>-wtf</code>|-wtf|td=0}}：技能无冷却、无耗蓝。</li>'\
           +'<li>{{点击复制|<code>-unwtf</code>|-unwtf|td=0}}：关闭wtf模式。</li>'\
           +'<li>{{点击复制|<code>-refresh</code>|-refresh|td=0}}：刷新状态和所有技能CD。</li>'\
           +'<li>{{点击复制|<code>-respawn</code>|-respawn|td=0}}：复活。</li>'\
           +'<li>{{点击复制|<code>-item</code> XX|-item|td=0}}：获得物品。[[#物品代码|点击此处可以跳转至物品代码处]]</li>'\
           +'<li>{{点击复制|<code>-givebots</code> XX|-givebots|td=0}}：所有机器人获得物品。[[#物品代码|点击此处可以跳转至物品代码处]]</li>'\
           +'<li>{{点击复制|<code>-createhero</code> XX|-createhero|td=0}}：获得物品。[[#英雄代码|点击此处可以跳转至英雄代码处]]</li>'\
           +'<li>{{点击复制|<code>-createhero</code> XX enemy|-createhero enemy|td=0}}：所有机器人获得物品。[[#英雄代码|点击此处可以跳转至英雄代码处]]</li>'\
           +'<li>{{点击复制|<code>-startgame</code>|-startgame|td=0}}：开始游戏，出兵。</li>'\
           +'<li>{{点击复制|<code>-spawncreeps</code>|-spawncreeps|td=0}}：立刻产生一波小兵。</li>'\
           +'<li>{{点击复制|<code>-spawnneutrals</code>|-spawnneutrals|td=0}}：立刻产生一波野怪。</li>'\
           +'<li>{{点击复制|<code>-spawnrune</code>|-spawnrune|td=0}}：立刻刷新一波神符，包括赏金神符和强化神符。</li>'\
           +'<li>{{点击复制|<code>-disablecreepspawn</code>|-disablecreepspawn|td=0}}：禁止产生小兵。</li>'\
           +'<li>{{点击复制|<code>-enablecreepspawn</code>|-enablecreepspawn|td=0}}：恢复产生小兵。</li>'\
           +'<li>{{点击复制|<code>-killwards</code>|-killwards|td=0}}：摧毁所有{{H|侦查守卫}}和{{H|岗哨守卫}}。</li>'\
           +'<li>{{点击复制|<code>-allvision</code>|-allvision|td=0}}：双方阵营共享视野。</li>'\
           +'<li>{{点击复制|<code>-normalvision</code>|-normalvision|td=0}}：视野恢复正常。</li>'\
           +'<li>{{点击复制|<code>-trees</code>|-trees|td=0}}：刷新树木。</li>'\
           +'</ul>\n'
    retxt=html_function(retxt)
    upload_data = {'action': 'edit', 'title': '常用测试指令/聊天框', 'text': retxt, 'format': 'json', 'token': csrf_token}
    upload_info = seesion.post(target_url, headers=headers, data=upload_data)
    return analyse_upload_json('常用测试指令/聊天框', upload_info)

def common_code_hero_page(json,seesion, csrf_token,html_function):
    retxt=''
    retxt+='英雄的所有表格中{{点击复制|<code>代码样式文字</code>|代码样式文字|td=0}}均可以通过点击进行复制。\n'\
           +'<table class="wikitable mw-collapsible" style="">'\
           +'<tr><th>英雄</th><th>代码</th><th>完整代码</th><th>创建友方英雄</th><th>创建敌方英雄</th></tr>'
    for i in json['英雄']:
        db=json['英雄'][i]
        if db['应用']==1:
            retxt+='<tr><td id="'+db['页面名']+'">{{小图片|'+db['主属性']['1']+'}}{{H|'+i+'}}</td>'\
                   +'<td>{{点击复制|<code>'+db['代码名']+'</code>|'+db['代码名']+'|td=0}}</td>'\
                   +'<td>{{点击复制|<code>npc_dota_hero_'+db['代码名']+'</code>|npc_dota_hero_'+db['代码名']+'|td=0}}</td>'\
                   +'<td>{{点击复制|<code>-createhero '+db['代码名']+'</code>|-createhero '+db['代码名']+'|td=0}}</td>'\
                   +'<td>{{点击复制|<code>-createhero '+db['代码名']+' enemy</code>|-createhero '+db['代码名']+' enemy|td=0}}</td></tr>'
    retxt+='</table>\n'
    retxt=html_function(retxt)
    upload_data = {'action': 'edit', 'title': '常用测试指令/英雄', 'text': retxt, 'format': 'json', 'token': csrf_token}
    upload_info = seesion.post(target_url, headers=headers, data=upload_data)
    return analyse_upload_json('常用测试指令/英雄', upload_info)

def common_code_item_page(json,seesion, csrf_token,html_function):
    retxt=''
    item={'肉山':[],'中立第1级':[],'中立第2级':[],'中立第3级':[],'中立第4级':[],'中立第5级':[],'普通物品':[],'已移除':[]}
    for i in json['物品']:
        db=json['物品'][i]
        if db['应用']==1:
            getbool=True
            for j in db['商店']:
                shop = db['商店'][j]
                if shop in item:
                    item[shop].append(i)
                    getbool = False
            if getbool:
                item['普通物品'].append(i)
        else:
            item['已移除'].append(i)
    retxt+='物品的所有表格中{{点击复制|<code>代码样式文字</code>|代码样式文字|td=0}}均可以通过点击进行复制。\n'\
           +'===肉山物品===\n'\
           +'<table class="wikitable mw-collapsible">'\
           +'<tr><th>物品</th><th>代码</th><th>完整代码</th><th>给予自己物品</th><th>给予机器人物品</th></tr>'
    for i in item['肉山']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='</table>\n'\
           +'===中立物品===\n'\
           +'<table class="wikitable mw-collapsible">'\
           +'<tr><th>物品</th><th>代码</th><th>完整代码</th><th>给予自己物品</th><th>给予机器人物品</th></tr>'\
           +'<tr><th colspan=5>中立第1级</th></tr>'
    for i in item['中立第1级']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='<tr><th colspan=5>中立第2级</th></tr>'
    for i in item['中立第2级']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='<tr><th colspan=5>中立第3级</th></tr>'
    for i in item['中立第3级']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='<tr><th colspan=5>中立第4级</th></tr>'
    for i in item['中立第4级']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='<tr><th colspan=5>中立第5级</th></tr>'
    for i in item['中立第5级']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='</table>\n'\
           +'===普通物品===\n'\
           +'<table class="wikitable mw-collapsible">'\
           +'<tr><th>物品</th><th>代码</th><th>完整代码</th><th>卷轴</th><th>给予自己物品</th><th>给予机器人物品</th></tr>'
    for i in item['普通物品']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>'
        if '组件' in db:
            retxt+='<td>{{点击复制|<code>recipe</code>|item_recipe_' + db['代码名'] + '|td=0}}</td>'
        else:
            retxt+='<td></td>'
        retxt += '<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='</table>\n'\
           +'===已移除物品===\n'\
           +'<table class="wikitable mw-collapsible">'\
           +'<tr><th>物品</th><th>代码</th><th>完整代码</th><th>给予自己物品</th><th>给予机器人物品</th></tr>'
    for i in item['已移除']:
        db=json['物品'][i]
        retxt += '<tr><td id="'+db['页面名']+'">{{H|' + i + '}}</td>' \
                 + '<td>{{点击复制|<code>' + db['代码名'] + '</code>|' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>item_' + db['代码名'] + '</code>|item_' + db['代码名'] + '|td=0}}</td>'\
                 +'<td>{{点击复制|<code>-item ' + db['代码名'] + '</code>|-item ' + db['代码名'] + '|td=0}}</td>' \
                 + '<td>{{点击复制|<code>-givebots ' + db['代码名'] + '</code>|-givebots ' + db['代码名'] + '|td=0}}</td></tr>'
    retxt+='</table>\n'
    retxt=html_function(retxt)
    upload_data = {'action': 'edit', 'title': '常用测试指令/物品', 'text': retxt, 'format': 'json', 'token': csrf_token}
    upload_info = seesion.post(target_url, headers=headers, data=upload_data)
    return analyse_upload_json('常用测试指令/物品', upload_info)

def translate_page_dota_hud_error(json,seesion, csrf_token,html_function):
    retxt=''
    retxt+='<table class="wikitable"><tr><th>代码</th><th>中文</th><th>英文</th></tr>'
    for i in json:
        if i[:15]=='dota_hud_error_':
            v=json[i]
            v1=''
            v2=''
            if '中文' in v:
                v1=v['中文']
            if '英文' in v:
                v2=v['英文']
            retxt+='<tr><td>{{点击复制|<code>' + i + '</code>|' + i + '|td=0}}</td><td>' + v1 + '</td><td>' + v2 + '</td></tr>'
    retxt+='</table>\n{{全部格式}}'
    retxt=html_function(retxt)
    upload_data = {'action': 'edit', 'title': '翻译对照/游戏报错', 'text': retxt, 'format': 'json', 'token': csrf_token}
    upload_info = seesion.post(target_url, headers=headers, data=upload_data)
    return analyse_upload_json('翻译对照/游戏报错', upload_info)

def all_version_simple_show(log_base,log_list,seesion, csrf_token,html_function):
    retxt = ''
    button = ''
    content = ''
    key=''
    log_show_list = []
    ub=['','','']
    for i in range(len(log_list) - 1, -1, -1):
        for j in range(len(log_list[i]) - 1, -1, -1):
            log_name = log_list[i][0]
            if j > 0:
                log_name = log_list[i][0] + '/' + log_list[i][j]
            else:
                ub[1]=log_name+'=1；'+ub[1]
            ub[0]=log_name+'=1；'+ub[0]
            if log_name in log_base:
                v = log_base[log_name]
                button += '<div class="dota_dict_label_switch_content_by_click_button" data-display-len="2" data-check-key="' + log_name + '">' + log_name + '</div>'
                content += '<div class="dota_dict_label_switch_content_by_click_content" data-check-key="' + log_name + '=1；" data-display-type="inline-block">' + v['简易展示'] + '</div>'
                if j==0:
                    key=log_name+'=1；'+key
    ub[0]='<div class="dota_dict_label_switch_button_by_click_button" data-check-dict="' + ub[0] + '">全部显示</div>'
    ub[1]='<div class="dota_dict_label_switch_button_by_click_button" data-check-dict="' + ub[1] + '">仅主版本</div>'
    ub[2]='<div class="dota_dict_label_switch_button_by_click_button" data-check-dict="' + ub[2] + '">全部清除</div>'
    retxt += '<div class="dota_dict_label_switch_content_by_click" data-display-dict="'+key+'" data-need-new-tip="1">' + button+ ub[0]+ ub[1]+ ub[2] + '<div>' + content + '</div></div>\n{{全部格式}}'
    retxt=html_function(retxt)
    upload_data = {'action': 'edit', 'title': '更新日志', 'text': retxt, 'format': 'json', 'token': csrf_token}
    upload_info = seesion.post(target_url, headers=headers, data=upload_data)
    return analyse_upload_json('更新日志', upload_info)
