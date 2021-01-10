import json,math
from text_to_json import edit_json

target_url = 'https://dota.huijiwiki.com/w/api.php'
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.55'}

def analyse_upload_json(text, upload_info):
    upload_info_json = upload_info.json()
    retxt = ''
    if 'edit' in upload_info_json and upload_info_json['edit']['result'] == 'Success':
        if 'nochange' in upload_info.json()['edit']:
            retxt = '《' + text + '》没有修改'
        elif 'oldrevid' in upload_info.json()['edit']:
            retxt = '《' + text + '》修改' + str(upload_info.json()['edit']['oldrevid']) + '为' + str(upload_info.json()['edit'][
                'newrevid'])
        else:
            retxt = '《' + text + '》修改成功'
    else:
        retxt = '《' + text + '》修改失败'
    return retxt + '\n'


def create_upgrade_cast_text(numjsons,k):
    if k in numjsons:
        numjson=numjsons[k]
        retext = ''
        for i in numjson:
            if i == "2" or i == "4":
                retext += '[[file:agha.png|x22px|link=阿哈利姆神杖]]'
            if i == "3" or i == "4":
                for j in numjson[i]['升级来源']:
                    retext += '[[file:' + numjson[i]['升级来源'][j]["图片"] + '|x22px|link=' + numjson[i]['升级来源'][j][
                        "名称"] + ']]'
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


def ability_cast_point_and_backswing(seesion, json_base, csrf_token):
    retxt = '<table class="wikitable sortable"><tr><th>英雄-技能</th><th>前摇</th><th>后摇</th></tr>'
    for i in ['英雄', '非英雄单位', '物品']:
        temp_base = edit_json.sortedDictValues(json_base[i], True)
        for j in temp_base:
            for k in temp_base[j]['技能']:
                ability_name = temp_base[j]['技能'][k]
                if ability_name in json_base['技能']:
                    k = 0
                    while True:
                        k += 1
                        if str(k) in json_base['技能'][ability_name]['施法前摇']:
                            retxt += '<tr><td>{{H|' + j + '}}{{A|' + ability_name + '}}'
                            if '名称' in json_base['技能'][ability_name]['施法前摇'][str(k)] and json_base['技能'][ability_name]['施法前摇'][str(k)]['名称']!='':
                                retxt+='（'+json_base['技能'][ability_name]['施法前摇'][str(k)]['名称']+'）'
                            if str(k) in json_base['技能'][ability_name]['施法后摇'] and '名称' in json_base['技能'][ability_name]['施法后摇'][str(k)] and json_base['技能'][ability_name]['施法后摇'][str(k)]['名称']!='':
                                retxt+='（'+json_base['技能'][ability_name]['施法后摇'][str(k)]['名称']+'）'
                            retxt+='</td><td>' + create_upgrade_cast_text(
                                json_base['技能'][ability_name]['施法前摇'],str(k)) + '</td><td>' + create_upgrade_cast_text(
                                json_base['技能'][ability_name]['施法后摇'],str(k)) + '</td></tr>'
                        else:
                            break
    retxt += '</table>'
    upload_data = {'action': 'edit', 'title': '施法前摇和后摇', 'text': retxt, 'format': 'json',
                   'token': csrf_token}
    upload_info = seesion.post(target_url,headers=headers, data=upload_data)
    return analyse_upload_json('施法前摇和后摇', upload_info)

def calculate_armor_number_to_physical_resistance_percentage(armor):
    return min(0.06*armor/(1+0.06*abs(armor))*100,100)

def calculate_physical_resistance_percentage_to_physical_health_percentage(pr):
    return str(round(10000/(100-pr),1))+'%' if pr<100 else '无限'

def calculate_physical_damage_change_by_armor_change(pr,pr2):
    pr2=min(pr2,100)
    if pr2>=100:
        return '不再受伤' if pr < 100 else '皆不受伤'
    else:
        return str(round((pr-pr2) / (100 - pr)*100, 1)) + '%' if pr < 100 else '重新受伤'

def armor_physic_resistance_page148237(seesion, csrf_token):
    retxt='<table class="wikitable" style="text-align:center">'\
         '<tr><th>护甲<br/>物理抗性<br/>物理生命<ref>护甲结算时，因为能抗下更多物理伤害，因此相当于增加了一定百分比的生命值。物理生命为承受物理伤害时，相对于正常血量的百分比</ref>' \
         '<th>+2护甲<br/>物理抗性<br/>物理生命<br/>伤害减免<ref>之后所有的伤害减免和伤害加深都是指在增加或减少了这个数量的护甲后，相对于初始状态少承受或多承受的伤害百分比</ref></th>' \
         '<th>-2护甲<br/>物理抗性<br/>物理生命<br/>伤害加深</th><th>+4护甲<br/>物理抗性<br/>物理生命<br/>伤害减免</th><th>-6护甲<br/>物理抗性<br/>物理生命<br/>伤害加深</th>' \
         '<th>+10护甲<br/>物理抗性<br/>物理生命<br/>伤害减免</th><th>-8护甲<br/>物理抗性<br/>物理生命<br/>伤害加深</th><th>+15护甲<br/>物理抗性<br/>物理生命<br/>伤害减免</th>' \
         '<th>-20护甲<br/>物理抗性<br/>物理生命<br/>伤害加深</th></tr>'
    for i in [-20,-10,-5,0,2,5,10,15,20,30,50,80,150]:
        pr=calculate_armor_number_to_physical_resistance_percentage(i)
        ph=calculate_physical_resistance_percentage_to_physical_health_percentage(pr)
        retxt+='<tr><td>'+str(i)+'('+str(round(pr,1))+'%)<br/>'+ph+'</td>'
        for j in [2,-2,4,-6,10,-8,15,-20]:
            arj=i+j
            prj=calculate_armor_number_to_physical_resistance_percentage(arj)
            phj=calculate_physical_resistance_percentage_to_physical_health_percentage(prj)
            dcj=calculate_physical_damage_change_by_armor_change(pr,prj)
            retxt+='<td>'+str(arj)+'('+str(round(prj,1))+'%)<br/>'+phj+'('+dcj+')</td>'
        retxt+='</tr>'
    retxt+='</table>{{reflist}}'
    upload_data = {'action': 'edit', 'title': '护甲/物理抗性表格', 'text': retxt, 'format': 'json','token': csrf_token}
    upload_info = seesion.post(target_url,headers=headers, data=upload_data)
    return analyse_upload_json('护甲/物理抗性表格', upload_info)