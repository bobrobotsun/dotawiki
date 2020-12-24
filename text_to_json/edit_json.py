#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
确定机制结构基础的json


作者: 莫无煜
网站: https://dota.huijiwiki.com
"""
from xpinyin import Pinyin


# dict排序方法
def sortedDictValues(adict, pinyin):
    keys = []
    new = {}
    if pinyin:
        p = Pinyin()
        for i in adict:
            keys.append([p.get_pinyin(i), i])
            keys = sorted(keys, key=lambda x: x[0])
        for i in keys:
            new[i[1]] = adict[i[1]]
    else:
        keys = sorted(adict)
        for i in keys:
            new[i] = adict[i]
    return new


def sortedList(alist):
    keys = []
    new = []
    p = Pinyin()
    for i in alist:
        keys.append([p.get_pinyin(i), i])
        keys = sorted(keys, key=lambda x: x[0])
    for i in keys:
        new.append(i[1])
    return new

def version_sort(version_json,version_list):
    rejson={}
    for i in range(len(version_list)):
        for j in range(len(version_list[i])):
            if j > 0:
                log_name = version_list[i][0] + '/' + version_list[i][j]
            else:
                log_name = version_list[i][j]
            if log_name in version_json:
                rejson[log_name]=version_json[log_name]
    return rejson

def one_version_name_sort(version_json):
    keys = []
    new = {}
    p = Pinyin()
    for i in version_json:
        if i!='0':
            keys.append([p.get_pinyin(version_json[i][0]), i])
    keys = sorted(keys, key=lambda x: x[0])
    new['0']=version_json['0']
    for i in range(len(keys)):
        new[str(i+1)] = version_json[keys[i][1]]
    return new

def special_sort_dict_by_pinyin(version_json,sortfun=lambda x,y:x[y]):
    keys = []
    new = {}
    p = Pinyin()
    for i in version_json:
        keys.append([p.get_pinyin(sortfun(version_json,i)), i])
    keys = sorted(keys, key=lambda x: x[0])
    for i in keys:
        new[i[1]] = version_json[i[1]]
    return new

def special_sort_list_by_pinyin(version_json,sortfun=lambda x,y:x[y]):
    keys = []
    new = []
    p = Pinyin()
    for i in range(len(version_json)):
        keys.append([p.get_pinyin(sortfun(version_json,i)), i])
    keys = sorted(keys, key=lambda x: x[0])
    for i in keys:
        new.append(version_json[i[1]])
    return new

edit_source = {
    '英雄': ['英雄'],
    '物品': ['物品'],
    '非英雄单位': ['非英雄单位'],
    '技能': [],
    '技能源': ['技能', '机制检索']
}
edit = {
    '英雄': {
        "页面名": ['text', ''],
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
        "模型技能": ['text', ''],
        "简介": ['text', ''],
        "背景": ['text', ''],
        "dota背景": ['text', ''],
        "曾用名": ['tree', {"list": ['text', '', 1, 0, False]}]
    },
    '非英雄单位': {
        "页面名": ['text', ''],
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
        "源技能": ['tree', {"list": ['text', '', 1, 1, False]}],
        "英雄级单位": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                          '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "远古单位": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "中立生物": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "召唤物": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                        '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "等级": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                       '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "生命值": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                        '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "生命恢复": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "魔法值": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                        '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "魔法恢复": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击上限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击下限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击间隔": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击前摇": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击距离": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击距离缓冲": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                           '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "警戒范围": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "弹道速度": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "护甲": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                       '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "魔法抗性": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "移动速度": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "转身速率": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击类型": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "护甲类型": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "近战远程": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "移动方式": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "经验": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                       '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "金钱下限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "金钱上限": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "跟随距离": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "攻击欲望": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "白天视野": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "夜晚视野": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "碰撞体积": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
        "模型比例": ['tree', {"list": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}],
                                         '修正': ['tree', {'list': ['txt', '', 1, 1, False]}]},1,1,False]}],
    },
    '物品': {
        "页面名": ['text', ''],
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
        '价格': ['tree', {'代码': ['text', 'ItemCost']}]
    },
    '技能': {
        "页面名": ['text', ''],
        "数据来源": ['text', ''],
        "技能归属": ['text', ''],
        "次级分类": ['text', ''],
        "默认按键": ['text', ''],
        "传统按键": ['text', ''],
        "技能排序": ['text', '']
    },
    '技能源': {
        "页面名": ['text', ''],
        "中文名": ['text', ''],
        "英文名": ['text', ''],
        "代码": ['text', ''],
        "天赋代码": ['text', ''],
        "神杖信息": ['text', ''],
        "魔晶信息": ['text', ''],
        "传说": ['text', ''],
        "描述": ['text', ''],
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
            '叠加': ['tree', {'list': ['tree', {'代码1': ['int', 0], '代码2': ['int', 0]}, 1, 1, False]}],
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
        "独立机制":['tree', {"list": ['tree', {'机制名': ['text', ''], '简述': ['text', '']}, 1, 0, True]}],
        "施法前摇": ['tree', {'list': ['tree', {'名称': ['text', ''],'代码': ['tree', {'list': ['text', '', 0, 4, False]}],
                                            '修正': ['tree', {'list': ['text', '', 1, 1, False]}],
                                            '即时生效': ['tree', {'代码': ['int', 0]}]}, 1, 0, True]}],
        "施法后摇": ['tree', {'list': ['tree', {'名称': ['text', ''],'代码': ['tree', {'list': ['text', '', 0, 4, False]}],
                                            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 0, True]}],
        "魔法消耗": ['tree', {'list': ['tree', {'名称': ['text', ''], 'list': ['tree', {
            '代码': ['tree', {'list': ['text', '', 0, 4, False]}],
            '类型': ['tree', {'代码': ['int', 1]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 1, False]}, 1, 0, True]}],
        "冷却时间": ['tree', {'list': ['tree', {
            '名称': ['text', ''],
            '代码': ['tree', {'list': ['text', '', 0, 4, False]}],
            '类型': ['tree', {'代码': ['int', 1]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 0, True]}],
        "属性": ['tree', {'list': ['tree', {
            '名称': ['text', ''],
            '后缀': ['text', ''],
            '代码': ['tree', {'list': ['text', '', 0, 4, False]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 1, False]}],
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
    }
}
edit_adition={
    '物品属性': {
        '全属性': {'代码': 'bonus_all_stats', '后缀': '', '展示前缀': '+', '展示后缀': '[[属性|全属性]]'},
        '主属性': {'代码': 'bonus_primary_stat', '后缀': '', '展示前缀': '+', '展示后缀': '[[属性|主属性]]'},
        '主属性百分比': {'代码': 'primary_stat_percent', '后缀': '%', '展示前缀': '+', '展示后缀': '[[属性|主属性]]'},
        '次级属性': {'代码': 'secondary_stats', '后缀': '', '展示前缀': '+', '展示后缀': '[[属性|次级属性]]'},
        '力量': {'代码': 'bonus_strength', '后缀': '', '展示前缀': '+', '展示后缀': '[[file:Strength_Icon.png|24px]][[力量]]'},
        '敏捷': {'代码': 'bonus_agility', '后缀': '', '展示前缀': '+', '展示后缀': '[[file:Agility_Icon.png|24px]][[敏捷]]'},
        '智力': {'代码': 'bonus_intellect', '后缀': '', '展示前缀': '+', '展示后缀': '[[file:Intelligence_Icon.png|24px]][[智力]]'},
        '生命值': {'代码': 'bonus_health', '后缀': '', '展示前缀': '+', '展示后缀': '[[生命值]]'},
        '魔法值': {'代码': 'bonus_health', '后缀': '', '展示前缀': '+', '展示后缀': '[[魔法值]]'},
        '负魔法值': {'代码': 'bonus_health', '后缀': '', '展示前缀': '-', '展示后缀': '[[魔法值]]'},
        '生命恢复': {'代码': 'bonus_health', '后缀': '', '展示前缀': '+', '展示后缀': '[[生命恢复速率]]'},
        '魔法恢复': {'代码': 'bonus_mana_regen', '后缀': '', '展示前缀': '+', '展示后缀': '[[魔法恢复速率]]'},
        '百分比最大生命恢复': {'代码': 'health_regen_pct', '后缀': '%', '展示前缀': '+', '展示后缀': '[[百分比最大生命恢复]]'},
        '百分比最大魔法恢复': {'代码': 'mana_regen_pct', '后缀': '%', '展示前缀': '+', '展示后缀': '[[百分比最大魔法恢复]]'},
        '攻击力': {'代码': 'bonus_damage', '后缀': '', '展示前缀': '+', '展示后缀': '[[攻击力]]'},
        '近战攻击力': {'代码': 'bonus_damage_melee', '后缀': '', '展示前缀': '+', '展示后缀': '[[攻击力]]（近战）'},
        '远程攻击力': {'代码': 'bonus_damage_range', '后缀': '', '展示前缀': '+', '展示后缀': '[[攻击力]]（远程）'},
        '百分比攻击力': {'代码': 'base_attack_damage', '后缀': '%', '展示前缀': '+', '展示后缀': '[[攻击力]]'},
        '攻击距离': {'代码': 'bonus_attack_range', '后缀': '', '展示前缀': '+', '展示后缀': '[[攻击距离]]'},
        '近战攻击距离': {'代码': 'melee_attack_range', '后缀': '', '展示前缀': '+', '展示后缀': '[[攻击距离]]（近战）'},
        '远程攻击距离': {'代码': 'range_attack_range', '后缀': '', '展示前缀': '+', '展示后缀': '[[生命值]]（远程）'},
        '施法距离': {'代码': 'cast_range_bonus', '后缀': '', '展示前缀': '+', '展示后缀': '[[施法距离]]'},
        '攻击吸血': {'代码': 'attack_lifesteal', '后缀': '%', '展示前缀': '+', '展示后缀': '[[攻击吸血]]'},
        '技能吸血': {'代码': 'spell_lifesteal', '后缀': '%', '展示前缀': '+', '展示后缀': '[[技能吸血]]'},
        '护甲': {'代码': 'bonus_armor', '后缀': '', '展示前缀': '+', '展示后缀': '[[护甲]]'},
        '负护甲': {'代码': 'bonus_armor', '后缀': '', '展示前缀': '-', '展示后缀': '[[护甲]]'},
        '魔法抗性': {'代码': 'bonus_magic_resistance', '后缀': '%', '展示前缀': '+', '展示后缀': '[[魔法抗性]]'},
        '技能增强': {'代码': 'bonus_spell_amp', '后缀': '%', '展示前缀': '+', '展示后缀': '[[技能增强]]'},
        '闪避': {'代码': 'bonus_evasion', '后缀': '%', '展示前缀': '+', '展示后缀': '[[闪避]]'},
        '攻击速度': {'代码': 'bonus_attack_speed', '后缀': '', '展示前缀': '+', '展示后缀': '[[攻击速度]]'},
        '基础攻击间隔': {'代码': 'base_attack_time', '后缀': '', '展示前缀': '+', '展示后缀': '[[基础攻击间隔]]'},
        '弹道速度': {'代码': 'projectile_speed', '后缀': '', '展示前缀': '+', '展示后缀': '[[弹道速度]]'},
        '百分比弹道速度': {'代码': 'projectile_bonus', '后缀': '%', '展示前缀': '+', '展示后缀': '[[弹道速度]]'},
        '定值移速': {'代码': 'bonus_movement_speed', '后缀': '', '展示前缀': '+', '展示后缀': '[[移动速度]]'},
        '百分比移速': {'代码': 'bonus_movement_speed', '后缀': '%', '展示前缀': '+', '展示后缀': '[[移动速度]]'},
        '百分比转身速率': {'代码': 'turn_rate', '后缀': '%', '展示前缀': '+', '展示后缀': '[[转身速率]]'},
        '魔法损耗': {'代码': 'manacost_reduction', '后缀': '%', '展示前缀': '+', '展示后缀': '魔法消耗/损失降低'},
        '状态抗性': {'代码': 'status_resistance', '后缀': '%', '展示前缀': '+', '展示后缀': '[[状态抗性]]'},
        '状态抗性降低': {'代码': 'status_resistance', '后缀': '%', '展示前缀': '+', '展示后缀': '[[状态抗性]]'},
        '吸血增强': {'代码': 'lifesteal_amp', '后缀': '', '展示前缀': '+', '展示后缀': '[[吸血增强]]'},
        '技能吸血增强': {'代码': 'spell_lifesteal_amp', '后缀': '', '展示前缀': '+', '展示后缀': '[[技能吸血增强]]'},
        '恢复增强': {'代码': 'hp_regen_amp', '后缀': '', '展示前缀': '+', '展示后缀': '[[恢复增强]]'},
        '魔法恢复增强': {'代码': 'mana_regen_multiplier', '后缀': '', '展示前缀': '+', '展示后缀': '[[魔法恢复增强]]'},
        '治疗增强': {'代码': 'hp_regen_reduction', '后缀': '', '展示前缀': '+', '展示后缀': '[[治疗增强]]'},
        '魔法获取增强': {'代码': 'mp_regen_reduction', '后缀': '', '展示前缀': '+', '展示后缀': '[[魔法获取增强]]'},
        '白天视野': {'代码': 'day_vision', '后缀': '', '展示前缀': '+', '展示后缀': '[[白天视野]]'},
        '夜晚视野': {'代码': 'night_vision', '后缀': '', '展示前缀': '+', '展示后缀': '[[夜晚视野]]'},
        '金钱': {'代码': 'bonus_gpm', '后缀': '', '展示前缀': '+', '展示后缀': '[[金钱]]/分钟'},
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
            if base['英雄'][i]['近战远程']['1'] == '远程':
                v['近战英雄'].append(i)
            elif base['英雄'][i]['近战远程']['1'] == '远程':
                v['远程英雄'].append(i)
    return v
