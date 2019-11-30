#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
确定机制结构基础的json


作者: 莫无煜
网站: https://dota.huijiwiki.com
"""
from xpinyin import Pinyin

#dict排序方法
def sortedDictValues(adict,pinyin):
    keys=[]
    new={}
    if pinyin:
        p=Pinyin()
        for i in adict:
            keys.append([p.get_pinyin(i),i])
            keys=sorted(keys,key=lambda x:x[0])
        for i in keys:
            new[i[1]]=adict[i[1]]
    else:
        keys=sorted(adict)
        for i in keys:
            new[i]=adict[i]
    return new

def sortedList(alist):
    keys=[]
    new=[]
    p = Pinyin()
    for i in alist:
        keys.append([p.get_pinyin(i), i])
        keys = sorted(keys, key=lambda x: x[0])
    for i in keys:
        new.append(alist[i[1]])
    return new

edit_source={
    '英雄':['代码名'],
    '物品':['代码名'],
    '非英雄单位':['代码名'],
    '技能':[],
    '技能源':['代码名','机制检索']
}
edit = {
        '英雄': {
            "页面名": ['text'],
            "分类": ['text'],
            "中文名": ['text'],
            "英文名": ['text'],
            "中文别名": ['text'],
            "英文别名": ['text'],
            "dota中文名": ['text'],
            "dota英文名": ['text'],
            "dota中文别名": ['text'],
            "dota英文别名": ['text'],
            "攻击后摇": ['number'],
            "图片": ['text'],
            "迷你图片": ['text'],
            "模型技能": ['text'],
            "简介": ['text'],
            "背景": ['text'],
            "dota背景": ['text']
        }
    }
