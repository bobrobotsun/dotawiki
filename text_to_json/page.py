import json
from text_to_json import edit_json

target_url = 'https://dota.huijiwiki.com/w/api.php'


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
            if '即时生效' in numjson[i] and numjson[i]['即时生效']['代码'] != 0:
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
    upload_info = seesion.post(target_url, data=upload_data)
    return analyse_upload_json('施法前摇和后摇', upload_info)
