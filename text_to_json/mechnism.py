import json
import os
import copy
import math
import re
import time
from PyQt5.QtWidgets import *
from text_to_json import common_page, ability
from text_to_json.WikiError import editerror

def get_source_to_data(all_json, tlist, version, text_base,name_base,costom_mech,change_all_template_link_to_html,loop_time=1,selfw=''):
    # 一定报错的内容
    for i in tlist:
        if i not in all_json['机制']:
            raise (editerror('机制源', i, "在【机制】中缺少关于【" + i + '】的信息，请及时补充'))
        if i not in all_json['机制源']:
            raise (editerror('机制', i, "在【机制源】中缺少关于【" + i + '】的信息，请及时补充'))
    for loop in range(loop_time):
        for targeti in range(len(tlist)):
            target=tlist[targeti]
            if "图片大小" not in all_json['机制源'][target]:
                all_json['机制源'][target]["图片大小"]='120'
            fromdict = copy.deepcopy(all_json['机制源'][target])
            all_json['机制源'][target]['分类'] = '机制源'
            all_json['机制源'][target]['页面名'] = target
            all_json['机制源'][target]["版本"] = version
            if '日志标识' not in all_json['机制源'][target]:
                all_json['机制源'][target]['日志标识']={}
            if '手填标签' not in all_json['机制源'][target]:
                all_json['机制源'][target]['手填标签']={}
            if '标签' not in all_json['机制'][target]:
                all_json['机制'][target]['标签']=[]
            todict = all_json['机制'][target]
            todict['分类'] = '机制'
            todict['页面名'] = target
            todict["版本"] = version
            for i in ["图片", "迷你图片", "图片大小", "简述"]:
                todict[i] = fromdict[i]
            todict['自定义机制'] = {}
            for i in fromdict['自定义机制']:
                v=fromdict['自定义机制'][i]
                if v['名称']=='':
                    dictkey='自定义机制'+i
                else:
                    dictkey=v['名称']
                todict['自定义机制'][dictkey]={}
                todict['自定义机制'][dictkey]['分隔符']=fromdict['自定义机制'][i]['分隔符']
                todict['自定义机制'][dictkey]['目标']=fromdict['自定义机制'][i]['目标']
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
                        ability.change_combine_txt(todict, i, text_base, all_json, target, ttarget + ['混合文字'],change_all_template_link_to_html)
                    else:
                        ability.loop_check(todict[i], text_base, all_json, target, ttarget)
            for i in ["属性", "简单条目", "具体条目",'自定义机制']:
                for j in todict[i]:
                    ttarget = ['机制源', target, i, j]
                    if isinstance(todict[i][j], dict):
                        if "混合文字" in todict[i][j]:
                            ability.change_combine_txt(todict[i], j, text_base, all_json, target, ttarget + ['混合文字'],change_all_template_link_to_html)
                        else:
                            ability.loop_check(todict[i][j], text_base, all_json, target, ttarget,change_all_template_link_to_html)
            # 这里要是拆开来分析，主要是为了让机制能调用其他机制的内容
            ability.loop_check(all_json['机制'][target]['内容'], text_base, all_json, target, ['机制源', target, '内容'],change_all_template_link_to_html)
            # 上面将文字全部转化掉
            for i in todict['自定义机制']:
                v=todict['自定义机制'][i]
                splitop='、'
                if v['分隔符']!='':
                    splitop=v['分隔符']
                all_mech=v['目标'].split(splitop)
                v.clear()
                j=0
                ll=0
                while j<len(all_mech):
                    if all_mech[j]=='':
                        all_mech.pop(j)
                    else:
                        j+=1
                for j in all_mech:
                    v[j]={}
                    mechname=(target,i)
                    if mechname in costom_mech and j in costom_mech[mechname]:
                        for k in costom_mech[mechname][j]:
                            w=costom_mech[mechname][j][k]
                            ll+=1
                            l=str(ll)
                            buffname='{{buff|'+k[0]+'|'+k[1]+'}}'
                            if '升级来源' in w:
                                for m in w['升级来源']:
                                    buffname+='{{额外信息框|{{图片|' + w['升级来源'][m]['图片'] + '}}|' + w['升级来源'][m]['名称'] + '}}'
                            v[j][buffname]={'值':w['值'],'序数':w['排序']}
            #上面将自定义机制完全生成完毕
            all_json['机制'][target]['曾用名'] = []
            if target in name_base:
                for namej in name_base[target]:
                    if namej != target:
                        all_json['机制'][target]['曾用名'].append(namej)
            for i in all_json['机制源'][target]['日志标识']:
                all_json['机制'][target]['曾用名'].append(all_json['机制源'][target]['日志标识'][i])
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
            if selfw!='':
                selfw.addtext(['《'+target+'》已经更新了'+str(loop+1)+'次',1], targeti+loop*len(tlist))
                QApplication.processEvents()

def fulfil_labels(all_json):
    for i in all_json['机制']:
        v1=all_json['机制'][i]
        v2=all_json['机制源'][i]
        v1['标签'] = []
        if v1['次级分类'] != '' and v1['次级分类'] not in v2['手填标签'].values():
            v2['手填标签'][str(len(v2['手填标签'])+1)]=v1['次级分类']
        for i in v2['手填标签']:
            if v2['手填标签'][i] != '':
                v1['标签'].append(v2['手填标签'][i])
        v1['标签'].append('机制')