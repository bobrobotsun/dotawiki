#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
确定机制结构基础的json


作者: 莫无煜
网站: https://dota.huijiwiki.com
"""
import pypinyin

def getpinyin(word,sep='-',style=8):
    return sep.join([_[0] for _ in pypinyin.pinyin(word,style=style)])


# dict排序方法
def sortedDictValues(adict, pinyin, _reverse=False):
    keys = []
    new = {}
    if pinyin:
        for i in adict:
            keys.append([getpinyin(i), i])
        keys = sorted(keys, key=lambda x: x[0], reverse=_reverse)
        for i in keys:
            new[i[1]] = adict[i[1]]
    else:
        keys = sorted(adict)
        for i in keys:
            new[i] = adict[i]
    return new


def sortedList(alist, function=lambda x: x[0], _reverse=False):
    keys = []
    new = []
    for i in alist:
        keys.append([getpinyin(i), i])
    keys = sorted(keys, key=function, reverse=_reverse)
    for i in keys:
        new.append(i[1])
    return new


def version_sort(version_json, version_list):
    rejson = {}
    for i in range(len(version_list)):
        for j in range(len(version_list[i])):
            if j > 0:
                log_name = version_list[i][0] + '/' + version_list[i][j]
            else:
                log_name = version_list[i][j]
            if log_name in version_json:
                rejson[log_name] = version_json[log_name]
    return rejson


def one_version_name_sort(version_json):
    keys = []
    new = {}
    for i in version_json:
        if i != '0':
            keys.append([getpinyin(version_json[i][0]), i])
    keys = sorted(keys, key=lambda x: x[0])
    new['0'] = version_json['0']
    for i in range(len(keys)):
        new[str(i + 1)] = version_json[keys[i][1]]
    return new


def special_sort_dict_by_pinyin(version_json, sortfun=lambda x, y: x[y]):
    keys = []
    new = {}
    for i in version_json:
        keys.append([getpinyin(sortfun(version_json, i)), i])
    keys = sorted(keys, key=lambda x: x[0])
    for i in keys:
        new[i[1]] = version_json[i[1]]
    return new


def special_sort_list_by_pinyin(version_json, sortfun=lambda x, y: x[y]):
    keys = []
    new = []
    for i in range(len(version_json)):
        keys.append([getpinyin(sortfun(version_json, i)), i])
    keys = sorted(keys, key=lambda x: x[0])
    for i in keys:
        new.append(version_json[i[1]])
    return new


edit_source = {
    '英雄': ['英雄'],
    '物品': ['物品'],
    '非英雄单位': ['非英雄单位'],
    '技能': [],
    '技能源': ['技能', '机制检索'],
    '单位组': [],
    '机制': [],
    '机制源': []
}
edit = {
    '英雄': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "代码名": ['text', ''],
        "中文名": ['text', ''],
        "英文名": ['text', ''],
        "中文别名": ['text', ''],
        "英文别名": ['text', ''],
        "dota中文名": ['text', ''],
        "dota英文名": ['text', ''],
        "dota中文别名": ['text', ''],
        "dota英文别名": ['text', ''],
        "攻击后摇": ['number', 0],
        "全属性黄点": ['number', 7],
        "模型技能": ['text', ''],
        "dota背景": ['text', ''],
        "曾用名": ['tree', {"list": ['text', '', 1, 0, False]}],
        "手填标签": ['tree', {"list": ['text', '', 1, 0, True]}]
    },
    '非英雄单位': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "图片": ['text', ''],
        "迷你图片": ['text', ''],
        "类型": ['text', ''],
        "关联类型": ['text', ''],
        "简介": ['text', ''],
        "生命类型": ['text', "生命值"],
        "代码名": ['tree', {"list": ['text', '', 1, 1, False]}],
        "中文名": ['tree', {"list": ['text', '', 1, 1, False]}],
        "英文名": ['tree', {"list": ['text', '', 1, 1, False]}],
        "攻击后摇": ['tree', {"list": ['number', 0, 1, 1, False]}],
        "源技能": ['tree', {"list": ['text', '', 1, 0, True]}],
        "手填标签": ['tree', {"list": ['text', '', 1, 0, True]}],
        "英雄级单位": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                             '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "远古单位": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "中立生物": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "召唤物": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                           '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "单位关系类型": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                              '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "等级": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                          '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "生命值": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                           '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "生命恢复": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "魔法值": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                           '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "魔法恢复": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击上限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击下限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击间隔": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击前摇": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击距离": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击距离缓冲": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                              '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "警戒范围": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "弹道速度": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "护甲": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                          '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "魔法抗性": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "移动速度": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "转身速率": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击类型": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "护甲类型": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "近战远程": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "移动方式": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "经验": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                          '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "金钱下限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "金钱上限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "跟随距离": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击欲望": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "白天视野": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "夜晚视野": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "碰撞体积": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "边界体积": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "模型比例": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "英雄攻击伤害": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                              '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "非英雄攻击伤害": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                               '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
        "攻击速度": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]}, 1, 1, False]}],
    },
    '物品': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "代码名": ['text', ''],
        "中文名": ['text', ''],
        "英文名": ['text', ''],
        "图片": ['text', ''],
        "迷你图片": ['text', ''],
        "商店": ['tree', {'list': ['text', '', 1, 1, False]}],
        "等级": ['int', 1],
        "共享": ['int', 0],
        "合成": ['int', 0],
        "传说": ['text', ''],
        '价格': ['tree', {'代码': ['text', 'ItemCost']}],
        "手填标签": ['tree', {"list": ['text', '', 1, 0, True]}]
    },
    '技能': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "数据来源": ['text', ''],
        "技能归属": ['text', ''],
        "次级分类": ['text', ''],
        "默认按键": ['text', ''],
        "传统按键": ['text', ''],
        "技能排序": ['text', ''],
        "图片": ['text', ''],
        "迷你图片": ['text', ''],
        "图片类型": ['text', '']
    },
    '技能源': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "中文名": ['text', ''],
        "英文名": ['text', ''],
        "代码": ['text', ''],
        "天赋代码": ['text', ''],
        "神杖信息": ['text', ''],
        "魔晶信息": ['text', ''],
        "传说": ['text', ''],
        "描述": ['text', ''],
        "链接指向": ['tree', {"list": ['text', '', 1, 0, True]}],
        "手填标签": ['tree', {"list": ['text', '', 1, 0, True]}],
        "注释": ['tree', {'list': ['tree', {'序列级数': ['int', 1], '文字': ['text', '']}, 1, 0, True]}],
        "施法目标": ['tree', {'不分类': ['tree', {"list":
                                               ['tree', {'代码': ['int', 1], 'list':
                                                   ['tree', {'代码': ['int', 1], 'list':
                                                       ['tree', {'代码': ['int', 1]}, 1, 1, False]
                                                             }, 1, 1, False]
                                                         }, 1, 0, True]
                                           }],
                          '英雄': ['tree', {"list":
                                              ['tree', {'代码': ['int', 1], 'list':
                                                  ['tree', {'代码': ['int', 1], 'list':
                                                      ['tree', {'代码': ['int', 1]}, 1, 1, False]
                                                            }, 1, 1, False]
                                                        }, 1, 0, True]
                                          }],
                          '非英雄': ['tree', {"list":
                                               ['tree', {'代码': ['int', 1], 'list':
                                                   ['tree', {'代码': ['int', 1], 'list':
                                                       ['tree', {'代码': ['int', 1]}, 1, 1, False]
                                                             }, 1, 1, False]
                                                         }, 1, 0, True]
                                           }]}],
        "施法类型": ['tree', {'list': ['tree', {'代码': ['int', 1]}, 1, 1, False]}],
        "效果": ['tree', {'list': ['tree', {
            'list': ['tree', {'list': ['int', 1, 1, 1, False], '名称': ['text', ''], '简述': ['text', '']}, 1, 1, False],
            '名称': ['text', ''],
            '代码': ['int', 1],
            '驱散': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '技能免疫': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '状态抗性': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '无敌': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '标记': ['tree', {'list': ['tree', {'类型': ['text', ''], '代码': ['int', 0]}, 1, 1, False]}],
            '叠加': ['tree', {'list': ['tree', {'代码1': ['int', 0], '代码2': ['int', 0], '代码3': ['int', 0]}, 1, 1, False]}],
            '生效从属': ['tree', {'代码': ['int', 1], '简述': ['text', '']}],
            '生效目标': ['tree', {'不分类': ['tree', {"list":
                                                   ['tree', {'代码': ['int', 1], 'list':
                                                       ['tree', {'代码': ['int', 1], 'list':
                                                           ['tree', {'代码': ['int', 1]}, 1, 1, False]
                                                                 }, 1, 1, False]
                                                             }, 1, 0, True]
                                               }],
                              '英雄': ['tree', {"list":
                                                  ['tree', {'代码': ['int', 1], 'list':
                                                      ['tree', {'代码': ['int', 1], 'list':
                                                          ['tree', {'代码': ['int', 1]}, 1, 1, False]
                                                                }, 1, 1, False]
                                                            }, 1, 0, True]
                                              }],
                              '非英雄': ['tree', {"list":
                                                   ['tree', {'代码': ['int', 1], 'list':
                                                       ['tree', {'代码': ['int', 1], 'list':
                                                           ['tree', {'代码': ['int', 1]}, 1, 1, False]
                                                                 }, 1, 1, False]
                                                             }, 1, 0, True]
                                               }]
                              }],
            '自定义机制':['tree',{'list':['tree',{'机制': ['text', ''],'名称': ['text', ''],'自称': ['text', ''],'排序': ['int', 0],'目标': ['tree_all_text', {}]},1,0,True]}]
        }, 1, 1, False]}],
        "技能免疫": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "无敌": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "技能抵挡": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "技能反弹": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "技能共享": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "技能窃取": ['tree', {
            "list": ['tree', {'list': ['tree', {'代码': ['int', 0]}, 1, 1, False], '代码': ['int', 0], '简述': ['text', '']},
                     1, 0, True]}],
        "幻象": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "破坏": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "持续施法": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "躲避": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "缠绕": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "即时攻击": ['tree', {"list": ['tree', {'list': ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 1, False],
                                            '代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "视野": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "真实视域": ['tree', {"list": ['tree', {'代码': ['int', 0], '简述': ['text', '']}, 1, 0, True]}],
        "独立机制": ['tree', {"list": ['tree', {'机制名': ['text', ''], '简述': ['text', '']}, 1, 0, True]}],
        "施法前摇": ['tree', {'list': ['tree', {'名称': ['text', ''], '代码': ['tree', {'list': ['text', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['text', '', 1, 1, False]}],
                                            '即时生效': ['tree', {'代码': ['int', 0]}]}, 1, 0, True]}],
        "施法后摇": ['tree', {'list': ['tree', {'名称': ['text', ''], '代码': ['tree', {'list': ['text', '', 0, 3, False]}],
                                            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 0, True]}],
        "魔法消耗": ['tree', {'list': ['tree', {'名称': ['text', ''], 'list': ['tree', {
            '代码': ['tree', {'list': ['text', '', 0, 3, False]}],
            '类型': ['tree', {'代码': ['int', 1]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 1, False]}, 1, 0, True]}],
        "冷却时间": ['tree', {'list': ['tree', {
            '名称': ['text', ''],
            '代码': ['tree', {'list': ['text', '', 0, 3, False]}],
            '类型': ['tree', {'代码': ['int', 1]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 0, True]}],
        "属性": ['tree', {'list': ['tree', {
            '名称': ['text', ''],
            '后缀': ['text', ''],
            '代码': ['tree', {'list': ['text', '', 0, 3, False]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}],
            '标识': ['tree', {'list': ['tree', {'代码': ['text', ''], '描述': ['text', '']}, 1, 0, True]}]
        }, 1, 1, False]}],
        "升级": ['tree', {
            '神杖': ['tree', {
                'list': ['tree', {'目标': ['tree', {'list': ['text', '', 0, 4, False]}], '值': ['random_tree', {}], }, 1,
                         0, True]}],
            '魔晶': ['tree', {
                'list': ['tree', {'目标': ['tree', {'list': ['text', '', 0, 4, False]}], '值': ['random_tree', {}], }, 1,
                         0, True]}],
            '技能': ['tree', {
                'list': ['tree', {'目标': ['tree', {'list': ['text', '', 0, 4, False]}], '值': ['random_tree', {}], }, 1,
                         0, True]}]
        }]
    },
    '单位组': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "图片": ['text', ''],
        "迷你图片": ['text', ''],
        "次级分类": ['text', ''],
        "单位来源": ['tree', {"list": ['text', '', 1, 0, True]}],
        "手填标签": ['tree', {"list": ['text', '', 1, 0, True]}],
        "成员": ['tree', {"list": ["tree", {'名称': ['text', ''],
                                          '额外属性': ['tree', {'list': ['tree', {
                                              '属性': ['text', ''],
                                              '代码': ['tree', {'list': ['text', '', 0, 4, False]}],
                                              '目标': ['tree', {'list': ['text', '', 1, 0, True]}]}, 1, 0, True]}],
                                          'list': ['tree', {'单位名': ['text', ''], '数量': ['tree', {'代码': ['tree', {'list': ['text', '', 0, 4, False]}]}]}, 1, 1, False],
                                          }, 1, 1, False]}],
    },
    '机制': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "次级分类": ['text', '']
    },
    '机制源': {
        "页面名": ['text', ''],
        "应用": ['int', 1],
        "图片": ['text', ''],
        "迷你图片": ['text', ''],
        "图片大小": ['text', '120'],
        "简述": ['text', ''],
        "日志标识": ['tree', {"list": ['text', '', 1, 0, True]}],
        "手填标签": ['tree', {"list": ['text', '', 1, 0, True]}],
        "自定义机制": ['tree', {"list": ['tree', {'名称': ['text', ''],'分隔符': ['text', '、'],'目标': ['text', '']}, 1, 0, True]}],
        "应用自定义机制": ['tree', {"list": ['tree', {'机制': ['text', ''],'名称': ['text', ''],'自称': ['text', ''],'排序': ['int', 0],'目标': ['tree_all_text', {}]}, 1, 0, True]}],
        "属性": ['tree', {"list": ['tree', {'标识': ['text', ''], 'list': ['text', '', 1, 1, False]}, 1, 0, True]}],
        "简单条目": ['tree', {"list": ['tree', {'标识': ['text', ''], '文字': ['text', '']}, 1, 0, True]}],
        "具体条目": ['tree', {"list": ['tree', {'标识': ['text', ''], '文字': ['text', '']}, 1, 0, True]}],
        "内容": ['tree', {"list": ['tree', {'标题': ['text', ''], '标题级数': ['int', 2],
                                          '内容': ['tree', {"list": ['tree', {'标识': ['text', ''],
                                                                            '内容': ['tree', {"list": ['tree', {'序列级数': ['int', 0], '文字': ['text', '']}, 1, 1, False]}]
                                                                            }, 1, 1, False]}]

                                          }, 1, 0, True]}]
    }
}
edit_adition = {
    '混合文字': ['tree', {"类型": ['text', ''], "后缀": ['text', ''], "list": ['tree', {"符号": ['text', ''], "list": ['text', '', 0, 4, False]}, 1, 1, False]}, 1, 0, False],
    '物品属性': {
        '全属性': {'代码': 'bonus_all_stats', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page" data-link-page-name="属性">全属性</span>'},
        '主属性': {'代码': 'bonus_primary_stat', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page" data-link-page-name="属性">主属性</span>'},
        '百分比主属性': {'代码': 'primary_stat_percent', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page" data-link-page-name="属性">主属性</span>'},
        '次级属性': {'代码': 'secondary_stats', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page" data-link-page-name="属性">次级属性</span>'},
        '力量': {'代码': 'bonus_strength', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_get_image_by_json_name" data-json-name="力量" data-text-link="1"></span>'},
        '百分比力量': {'代码': 'strength_pct', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_get_image_by_json_name" data-json-name="敏捷" data-text-link="1"></span>'},
        '敏捷': {'代码': 'bonus_agility', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_get_image_by_json_name" data-json-name="敏捷" data-text-link="1"></span>'},
        '百分比敏捷': {'代码': 'agility_pct', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_get_image_by_json_name" data-json-name="敏捷" data-text-link="1"></span>'},
        '智力': {'代码': 'bonus_intellect', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_get_image_by_json_name" data-json-name="智力" data-text-link="1"></span>'},
        '百分比智力': {'代码': 'intelligence_pct', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_get_image_by_json_name" data-json-name="智力" data-text-link="1"></span>'},
        '生命值': {'代码': 'bonus_health', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">生命值</span>'},
        '魔法值': {'代码': 'bonus_mana', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">魔法值</span>'},
        '负魔法值': {'代码': 'bonus_mana', '后缀': '', '展示前缀': '-', '展示后缀': '<span class="dota_create_link_to_wiki_page">魔法值</span>'},
        '生命恢复': {'代码': 'bonus_health_regen', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">生命恢复速率</span>'},
        '魔法恢复': {'代码': 'bonus_mana_regen', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">魔法恢复速率</span>'},
        '百分比最大生命恢复': {'代码': 'health_regen_pct', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">百分比最大生命恢复</span>'},
        '百分比最大魔法恢复': {'代码': 'mana_regen_pct', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">百分比最大魔法恢复</span>'},
        '攻击力': {'代码': 'bonus_damage', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击力</span>'},
        '近战攻击力': {'代码': 'bonus_damage_melee', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击力</span>（近战）'},
        '远程攻击力': {'代码': 'bonus_damage_range', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击力</span>（远程）'},
        '百分比攻击力': {'代码': 'base_attack_damage', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击力</span>'},
        '攻击距离': {'代码': 'bonus_attack_range', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击距离</span>'},
        '近战攻击距离': {'代码': 'melee_attack_range', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击距离</span>（近战）'},
        '远程攻击距离': {'代码': 'range_attack_range', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击距离</span>（远程）'},
        '施法距离': {'代码': 'cast_range_bonus', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">施法距离</span>'},
        '攻击吸血': {'代码': 'lifesteal_percent', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击吸血</span>'},
        '技能吸血': {'代码': 'spell_lifesteal', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">技能吸血</span>'},
        '英雄技能吸血': {'代码': 'hero_lifesteal', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">技能吸血</span>（英雄）'},
        '非英雄技能吸血': {'代码': 'creep_lifesteal', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">技能吸血</span>（非英雄）'},
        '护甲': {'代码': 'bonus_armor', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">护甲</span>'},
        '负护甲': {'代码': 'bonus_armor', '后缀': '', '展示前缀': '-', '展示后缀': '<span class="dota_create_link_to_wiki_page">护甲</span>'},
        '魔法抗性': {'代码': 'bonus_magic_resistance', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">魔法抗性</span>'},
        '技能增强': {'代码': 'bonus_spell_amp', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">技能增强</span>'},
        '闪避': {'代码': 'bonus_evasion', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">闪避</span>'},
        '攻击速度': {'代码': 'bonus_attack_speed', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">攻击速度</span>'},
        '基础攻击间隔': {'代码': 'base_attack_time', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">基础攻击间隔</span>'},
        '百分比前摇攻击速度': {'代码': 'anim_increase', '后缀': '%', '展示前缀': '+', '展示后缀': '攻击前摇期间<span class="dota_create_link_to_wiki_page">攻击速度</span>'},
        '弹道速度': {'代码': 'projectile_speed', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">弹道速度</span>'},
        '百分比弹道速度': {'代码': 'projectile_bonus', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">弹道速度</span>'},
        '定值移速': {'代码': 'bonus_movement_speed', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">移动速度</span>'},
        '百分比移速': {'代码': 'bonus_movement_speed', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">移动速度</span>'},
        '百分比转身速率': {'代码': 'turn_rate', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">转身速率</span>'},
        '魔法损耗': {'代码': 'manacost_reduction', '后缀': '%', '展示前缀': '+', '展示后缀': '[[魔法损耗降低]]'},
        '状态抗性': {'代码': 'status_resistance', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">状态抗性</span>'},
        '状态抗性降低': {'代码': 'status_resistance', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">状态抗性</span>降低'},
        '吸血增强': {'代码': 'lifesteal_amp', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">吸血增强</span>'},
        '技能吸血增强': {'代码': 'spell_lifesteal_amp', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">技能吸血增强</span>'},
        '恢复增强': {'代码': 'hp_regen_amp', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">恢复增强</span>'},
        '魔法恢复增强': {'代码': 'mana_regen_multiplier', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">魔法恢复增强</span>'},
        '治疗增强': {'代码': 'hp_regen_reduction', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">治疗增强</span>'},
        '魔法获取增强': {'代码': 'mp_regen_reduction', '后缀': '%', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">魔法获取增强</span>'},
        '模型大小': {'代码': 'model_scale', '后缀': '%', '展示前缀': '+', '展示后缀': '模型大小'},
        '白天视野': {'代码': 'day_vision', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">白天视野</span>'},
        '夜晚视野': {'代码': 'night_vision', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">夜晚视野</span>'},
        '金钱': {'代码': 'bonus_gpm', '后缀': '', '展示前缀': '+', '展示后缀': '<span class="dota_create_link_to_wiki_page">金钱</span>/分钟'},
        '会耗竭的': {'代码': 'ItemPermanent', '后缀': '', '展示前缀': '', '展示后缀': ''},
        '开局供应量': {'代码': 'ItemStockInitial', '后缀': '', '展示前缀': '开局时可购买', '展示后缀': '件'},
        '首次购买时间': {'代码': 'ItemInitialStockTime', '后缀': '', '展示前缀': '', '展示后缀': '开始可购买'},
        '首次供应数量': {'代码': 'ItemInitialCharges', '后缀': '', '展示前缀': '初次供应', '展示后缀': '件'},
        '商店补货时间': {'代码': 'ItemStockTime', '后缀': '', '展示前缀': '每', '展示后缀': '补货一次'},
        '商店最大储存量': {'代码': 'ItemStockMax', '后缀': '', '展示前缀': '商店最多存储', '展示后缀': '件'}
    }
}
edit_default_target = {"list":
                           ['tree', {'代码': ['int', 1], 'list':
                               ['tree', {'代码': ['int', 1], 'list':
                                   ['tree', {'代码': ['int', 1]}, 1, 1, False]
                                         }, 1, 1, False]
                                     }, 1, 0, True]
                       }

edit_default_category = {
    '不分类敌军': {
        "1": {
            "代码": 3,
            "1": {
                "代码": 1,
                "1": {"代码": 1},
                "2": {"代码": 2},
                "3": {"代码": 3},
                "4": {"代码": 4},
                "5": {"代码": 5},
                "6": {"代码": 6}
            },
            "2": {
                "代码": 2,
                "1": {"代码": 1},
                "2": {"代码": 2}
            },
            "3": {
                "代码": 4,
                "1": {"代码": 1},
                "2": {"代码": 2}
            }
        },
        "2": {
            "代码": 7,
            "1": {
                "代码": 3,
                "1": {"代码": 1},
                "2": {"代码": 2},
                "3": {"代码": 3}
            }
        }
    },
    '不分类友军': {
        "1": {
            "代码": 2,
            "1": {
                "代码": 1,
                "1": {"代码": 1},
                "2": {"代码": 2},
                "3": {"代码": 3},
                "4": {"代码": 4},
                "5": {"代码": 5},
                "6": {"代码": 6}
            },
            "2": {
                "1": {"代码": 1},
                "2": {"代码": 2},
                "代码": 2
            },
            "3": {
                "代码": 3,
                "1": {"代码": 1},
                "2": {"代码": 2}
            },
            "4": {
                "代码": 4,
                "1": {"代码": 1},
                "2": {"代码": 2}
            }
        }
    }
}
edit_default_update_type={
    '属性': {'代码': ['tree', {'list': ['text', '', 0, 3, False]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]},
    '追加属性': {'名称': ['text', ''],
             '后缀': ['text', ''],
             '代码': ['tree', {'list': ['text', '', 0, 3, False]}],
             '修正': ['tree', {'list': ['text', '', 1, 1, False]}],
             '标识': ['tree', {'list': ['tree', {'类型': ['text', ''], '描述': ['text', '']}, 1, 0, True]}]
             },
    '效果': {'名称': ['text', ''],
            '代码': ['int', 1],
            '驱散': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '技能免疫': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '状态抗性': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '无敌': ['tree', {'代码': ['int', 0], '简述': ['text', '']}],
            '标记': ['tree', {'list': ['tree', {'类型': ['text', ''], '代码': ['int', 0]}, 1, 1, False]}],
            '叠加': ['tree', {'list': ['tree', {'代码1': ['int', 0], '代码2': ['int', 0], '代码3': ['int', 0]}, 1, 1, False]}],
            '生效从属': ['tree', {'代码': ['int', 1], '简述': ['text', '']}],
            '生效目标': ['tree', {'不分类': ['random_tree',{}],'英雄': ['random_tree',{}],'非英雄': ['random_tree',{}]}],
            '自定义机制':['tree',{'list':['tree',{'机制': ['text', ''],'名称': ['text', ''],'自称': ['text', ''],'排序': ['int', 0],'目标': ['tree_all_text', {}]},1,0,True]}]
           },
    '蓝耗冷却': {'代码': ['tree', {'list': ['text', '', 0, 3, False]}],
             '类型': ['tree', {'代码': ['int', 1]}],
             '修正': ['tree', {'list': ['text', '', 1, 1, False]}]},
    '施法前摇': {'代码': ['tree', {'list': ['text', '', 0, 3, False]}],
             '修正': ['tree', {'list': ['text', '', 1, 1, False]}],
             '即时生效': ['tree', {'代码': ['int', 0]}]},
    '机制': {
        '代码': ['int', 1],
        '简述': ['text', '']
    },
    '注释': {
        '序列级数': ['int', 1],
        '文字': ['text', '']
    }
}
edit_default_update_value={
    '属性':{
        '代码':{
            '0':'',
            '1':'',
            '2':'',
            '3':''
        },
        '修正':{
            '1':''
        }
    },
    '追加属性':{
        '名称':'',
        '后缀':'',
        '代码':{
            '0':'',
            '1':'',
            '2':'',
            '3':''
        },
        '修正':{
            '1':''
        },
        '标识':{}
    },
    '效果':{
        "名称": "",
        "代码": 1,
        "驱散": {
            "代码": 0,
            "简述": ""
        },
        "技能免疫": {
            "代码": 0,
            "简述": ""
        },
        "状态抗性": {
            "代码": 0,
            "简述": ""
        },
        "无敌": {
            "代码": 0,
            "简述": ""
        },
        "标记": {
            "1": {
                "类型": "",
                "代码": 0
            }
        },
        "叠加": {
            "1": {
                "代码1": 0,
                "代码2": 0,
                "代码3": 0
            }
        },
        "生效从属": {
            "代码": 1,
            "简述": ""
        },
        "生效目标": {
            "不分类": {},
            "英雄": {},
            "非英雄": {}
        },
        '自定义机制': {}
    },
    '蓝耗冷却': {
        '代码': {
            '0': '',
            '1': '',
            '2': '',
            '3': ''
        },
        '修正': {
            '1': ''
        },
        '类型': {
            '代码': 1
        }
    },
    '施法前摇':{
        '代码':{
            '0':'',
            '1':'',
            '2':'',
            '3':''
        },
        '修正':{
            '1':''
        },
        '即时生效':{
            '代码':0
        }
    },
    '机制':{
        '代码':1,
        '简述':''
    },
    '注释':{
        '序列级数':1,
        '文字':''
    }
}

version = {
    "更新日期": ['text', '2020/2/20'],
    "地图作者": ['text', "Icefrog"],
    "游戏本体": ['text', "DOTA2"],
    "官网链接": ['text', ""],
    "开头": ['tree', ''],
    "英雄": ['tree', '英雄'],
    "物品": ['tree', '物品'],
    "中立生物": ['tree', '非英雄单位'],
    "建筑": ['tree', ''],
    "兵线": ['tree', ''],
    "通用": ['tree', ''],
    "结尾": ['tree', '']
}
version_default = {
}
version_label = {
    '重要': '<i class="fa fa-warning" style="color:#aa3333"></i>',
    '加强': '<i class="fa fa-arrow-up" style="color:#33aa33"></i>',
    '削弱': '<i class="fa fa-arrow-down" style="color:#aa3333"></i>',
    '平衡': '<i class="fa fa-exchange" style="color:#3333aa"></i>',
    '英雄重做': '<i class="fa fa-user" style="color:#aa00aa"></i>',
    '技能重做': '<i class="fa fa-anchor" style="color:#aa00aa"></i>',
    '新天赋': '{{图片|Talent_all.png}}',
    '技能改动': '<i class="fa fa-anchor" style="color:#3333aa"></i>',
    '重要神杖更新': '{{图片|Agha.png}}',
    '重要魔晶更新': '{{图片|Shard.png}}',
    '神杖改动': '{{图片|Agha.png}}',
    '魔晶改动': '{{图片|Shard.png}}',
    '单位重做': '<i class="fa fa-paw" style="color:#aa00aa"></i>',
    '物品重做': '<i class="fa fa-gavel" style="color:#aa00aa"></i>',
    '错误修复': '<i class="fa fa-bug" style="color:#33aa33"></i>',
    '疑似漏洞': '<i class="fa fa-bug" style="color:#aa3333"></i>'
}
version_label2 = {
    '补偿性加强': '<i class="fa fa-arrow-circle-up" style="color:#33aa33"></i>',
    '补偿性削弱': '<i class="fa fa-arrow-circle-down" style="color:#aa3333"></i>',
    '补偿性平衡': '<i class="fa fa-retweet" style="color:#3333aa"></i>'
}


def change_label_list_to_text(labels, index='label', count=False):
    retxt = ''
    if index == 'label':
        for i in version_label:
            if i in labels:
                retxt += '{{额外信息框|' + version_label[i] + '|' + ((str(labels.count(i)) + '×') if count else '') + i + '}}'
        for i in version_label2:
            if i in labels:
                retxt += '{{额外信息框|' + version_label2[i] + '|' + ((str(labels.count(i)) + '×') if count else '') + i + '}}'
    elif index == 'list':
        for i in labels:
            if i in version_label:
                retxt += '{{额外信息框|' + version_label[i] + '|' + ((str(labels.count(i)) + '×') if count else '') + i + '}}'
            if i in version_label2:
                retxt += '{{额外信息框|' + version_label2[i] + '|' + ((str(labels.count(i)) + '×') if count else '') + i + '}}'
    return retxt


item_shop = ['消耗品', '属性', '装备', '其他', '配件', '辅助', '法器', '防具', '兵刃', '宝物', '神秘商店', '肉山', '共享', '中立第1级', '中立第2级', '中立第3级', '中立第4级', '中立第5级']


def set_version_default(base):
    v = {
        '全英雄': [],
        '力量英雄': [],
        '敏捷英雄': [],
        '智力英雄': [],
        '近战英雄': [],
        '远程英雄': [],
    }
    for i in base['英雄']:
        v['全英雄'].append(i)
        if '主属性' in base['英雄'][i]:
            if base['英雄'][i]['主属性']['1'] == '力量':
                v['力量英雄'].append(i)
            elif base['英雄'][i]['主属性']['1'] == '敏捷':
                v['敏捷英雄'].append(i)
            elif base['英雄'][i]['主属性']['1'] == '智力':
                v['智力英雄'].append(i)
            if base['英雄'][i]['近战远程']['1'] == '近战':
                v['近战英雄'].append(i)
            elif base['英雄'][i]['近战远程']['1'] == '远程':
                v['远程英雄'].append(i)
    return v

if __name__=='__main__':
    print(getpinyin('我是人'))