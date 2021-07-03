import json
import os
import copy
import math
import re
import time
from text_to_json import common_page, ability
from text_to_json.WikiError import editerror

def get_source_to_data(all_json, tlist, version, text_base,loop_time=1):
    # 一定报错的内容
    for i in tlist:
        if i not in all_json['机制']:
            raise (editerror('机制源', i, "在【机制】中缺少关于【" + i + '】的信息，请及时补充'))
        if i not in all_json['机制源']:
            raise (editerror('机制', i, "在【机制源】中缺少关于【" + i + '】的信息，请及时补充'))
    for loop in range(loop_time):
        for target in tlist:
            fromdict = copy.deepcopy(all_json['机制源'][target])
            all_json['机制源'][target]['分类'] = '机制源'
            all_json['机制源'][target]['页面名'] = target
            all_json['机制源'][target]["版本"] = version
            todict = all_json['机制'][target]
            todict['分类'] = '机制'
            todict['页面名'] = target
            todict["版本"] = version
            for i in ["图片", "迷你图片", "简述"]:
                todict[i] = fromdict[i]
            todict['属性'] = {}
            for i in fromdict['属性']:
                dictkey = i
                if fromdict['属性'][i]['标识'] != '':
                    dictkey = fromdict['属性'][i]['标识']
                todict['属性'][dictkey] = {}
                for j in fromdict['属性'][i]:
                    if j != '标识' and fromdict['属性'][i][j] != '':
                        todict['属性'][dictkey][j] = fromdict['属性'][i][j]
            for i in ["简单条目", "具体条目"]:
                todict[i] = {}
                for j in fromdict[i]:
                    dictkey = j
                    if fromdict[i][j]['标识'] != '':
                        dictkey = fromdict[i][j]['标识']
                    todict[i][dictkey] = fromdict[i][j]['文字']
            todict['内容'] = {}
            for i in fromdict['内容']:
                ii = i
                if fromdict['内容'][i]['标题'] != '':
                    ii = fromdict['内容'][i]['标题']
                todict['内容'][ii] = {'标题级数': fromdict['内容'][i]['标题级数']}
                todict['内容'][ii]['内容'] = {}
                for j in fromdict['内容'][i]['内容']:
                    jj = j
                    if fromdict['内容'][i]['内容'][j]['标识'] != '':
                        jj = fromdict['内容'][i]['内容'][j]['标识']
                    todict['内容'][ii]['内容'][jj] = {}
                    todict['内容'][ii]['内容'][jj]['内容'] = {}
                    for k in fromdict['内容'][i]['内容'][j]['内容']:
                        todict['内容'][ii]['内容'][jj]['内容'][k] = fromdict['内容'][i]['内容'][j]['内容'][k]
            for i in ["图片", "迷你图片", "简述"]:
                ttarget = ['机制源', target, i]
                if isinstance(todict[i], dict):
                    if "混合文字" in todict[i]:
                        ability.change_combine_txt(todict, i, text_base, all_json, target, ttarget + ['混合文字'])
                    else:
                        ability.loop_check(todict[i], text_base, all_json, target, ttarget)
            for i in ["属性", "简单条目", "具体条目"]:
                for j in todict[i]:
                    ttarget = ['机制源', target, i, j]
                    if isinstance(todict[i][j], dict):
                        if "混合文字" in todict[i][j]:
                            ability.change_combine_txt(todict[i], j, text_base, all_json, target, ttarget + ['混合文字'])
                        else:
                            ability.loop_check(todict[i][j], text_base, all_json, target, ttarget)
            # 这里要是拆开来分析，主要是为了让机制能调用其他机制的内容
            ability.loop_check(all_json['机制'][target]['内容'], text_base, all_json, target, ['机制源', target, '内容'])
            # 上面将文字全部转化掉
            # 下面把序列级数合并成为一串文字，以方便调用
            for i in all_json['机制'][target]['内容']:
                for j in all_json['机制'][target]['内容'][i]['内容']:
                    comtext = ''
                    uls = 0
                    for k in all_json['机制'][target]['内容'][i]['内容'][j]['内容']:
                        kk = all_json['机制'][target]['内容'][i]['内容'][j]['内容'][k]
                        while kk['序列级数'] > uls:
                            uls += 1
                            comtext += '<ul>'
                        while kk['序列级数'] < uls:
                            uls -= 1
                            comtext += '</ul>'
                        if uls == 0:
                            comtext += '\n' + kk['文字'] + '<br>'
                        else:
                            comtext += '<li>' + '\n' + kk['文字'] + '</li>'
                    for k in range(uls):
                        comtext += '</ul>'
                    all_json['机制'][target]['内容'][i]['内容'][j]['内容'] = comtext
