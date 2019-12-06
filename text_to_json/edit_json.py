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
        new.append(alist[i[1]])
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
        "dota背景": ['text', '']
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
        "英雄级单位": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "远古单位": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "中立生物": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "召唤物": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "等级": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "生命值": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "生命恢复": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "魔法值": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "魔法恢复": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击上限": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击下限": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击间隔": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击前摇": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击距离": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击距离缓冲": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "警戒范围": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "弹道速度": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "护甲": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "魔法抗性": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "移动速度": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "转身速率": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击类型": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "护甲类型": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "近战远程": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "移动方式": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "经验": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "金钱下限": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "金钱上限": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "跟随距离": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "攻击欲望": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "白天视野": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "夜晚视野": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "碰撞体积": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
        "模型比例": ['tree', {"1": ['tree', {'代码': ['tree', {'list': ['txt', '', 0, 3, False]}]}]}],
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
        "共享": ['int', 1],
        "合成": ['int', -1],
        "传说": ['text', ''],
        '价格': ['tree', {'代码': ['text', 'ItemCost']}],
        '全属性': ['tree', {'代码': ['text', 'bonus_all_stats']}, True],
        '主属性': ['tree', {'代码': ['text', 'bonus_primary_stat']}, True],
        '主属性百分比': ['tree', {'代码': ['text', 'primary_stat_percent']}, True],
        '次级属性': ['tree', {'代码': ['text', 'secondary_stats']}, True],
        '力量': ['tree', {'代码': ['text', 'bonus_strength']}, True],
        '敏捷': ['tree', {'代码': ['text', 'bonus_agility']}, True],
        '智力': ['tree', {'代码': ['text', 'bonus_intellect']}, True],
        '生命值': ['tree', {'代码': ['text', 'bonus_health']}, True],
        '魔法值': ['tree', {'代码': ['text', 'bonus_mana']}, True],
        '负魔法值': ['tree', {'代码': ['text', 'bonus_mana']}, True],
        '生命恢复': ['tree', {'代码': ['text', 'bonus_health_regen']}, True],
        '魔法恢复': ['tree', {'代码': ['text', 'bonus_mana_regen']}, True],
        '攻击力': ['tree', {'代码': ['text', 'bonus_damage']}, True],
        '近战攻击力': ['tree', {'代码': ['text', 'bonus_damage_melee']}, True],
        '远程攻击力': ['tree', {'代码': ['text', 'bonus_damage_range']}, True],
        '百分比攻击力': ['tree', {'代码': ['text', 'base_attack_damage']}, True],
        '攻击距离': ['tree', {'代码': ['text', 'bonus_attack_range']}, True],
        '近战攻击距离': ['tree', {'代码': ['text', 'melee_attack_range']}, True],
        '远程攻击距离': ['tree', {'代码': ['text', 'range_attack_range']}, True],
        '施法距离': ['tree', {'代码': ['text', 'cast_range_bonus']}, True],
        '攻击吸血': ['tree', {'代码': ['text', 'attack_lifesteal']}, True],
        '技能吸血': ['tree', {'代码': ['text', 'spell_lifesteal']}, True],
        '吸血增强': ['tree', {'代码': ['text', 'hp_regen_amp']}, True],
        '护甲': ['tree', {'代码': ['text', 'bonus_armor']}, True],
        '负护甲': ['tree', {'代码': ['text', 'bonus_armor']}, True],
        '魔法抗性': ['tree', {'代码': ['text', 'bonus_magic_resistance']}, True],
        '技能增强': ['tree', {'代码': ['text', 'bonus_spell_amp']}, True],
        '闪避': ['tree', {'代码': ['text', 'bonus_evasion']}, True],
        '攻击速度': ['tree', {'代码': ['text', 'bonus_attack_speed']}, True],
        '基础攻击间隔': ['tree', {'代码': ['text', 'base_attack_time']}, True],
        '百分比弹道速度': ['tree', {'代码': ['text', 'projectile_bonus']}, True],
        '定值移速': ['tree', {'代码': ['text', 'bonus_movement_speed']}, True],
        '百分比移速': ['tree', {'代码': ['text', 'bonus_movement_speed']}, True],
        '百分比转身速率': ['tree', {'代码': ['text', 'turn_rate']}, True],
        '魔法损耗': ['tree', {'代码': ['text', 'manacost_reduction']}, True],
        '状态抗性': ['tree', {'代码': ['text', 'status_resistance']}, True],
        '状态抗性降低': ['tree', {'代码': ['text', 'status_resistance']}, True],
        '百分比生命恢复': ['tree', {'代码': ['text', 'health_regen_multiplier']}, True],
        '百分比魔法恢复': ['tree', {'代码': ['text', 'mana_regen_multiplier']}, True],
        '生命恢复效果百分比': ['tree', {'代码': ['text', 'hp_regen_amp']}, True],
        '魔法恢复效果百分比': ['tree', {'代码': ['text', 'mp_regen_amp']}, True],
        '白天视野': ['tree', {'代码': ['text', 'day_vision']}, True],
        '夜晚视野': ['tree', {'代码': ['text', 'night_vision']}, True],
        '金钱': ['tree', {'代码': ['text', 'bonus_gpm']}, True]
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
        "A杖信息": ['text', ''],
        "传说": ['text', ''],
        "描述": ['text', ''],
        "注释": ['text', ''],
        "施法目标": ['tree', {'不分类': ['tree', {"list":
                                               ['tree', {'代码': ['number', 1], 'list':
                                                   ['tree', {'代码': ['number', 1], 'list':
                                                       ['tree', {'代码': ['number', 1]}, 1, 1, False]
                                                             }, 1, 1, False]
                                                         }, 1, 0, True]
                                           }]}],
        "施法类型": ['tree', {'list': ['tree', {'代码': ['number', 1]}, 1, 1, False]}],
        "效果": ['tree', {'list': ['tree', {'list': ['tree', {'list': ['number', 1, 1, 1, False], '名称': ['text', ''], '简述': ['text', '']}, 1, 1, False],
                                          '名称': ['text', ''],
                                          '代码': ['number', 1],
                                          '驱散': ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
                                          '技能免疫': ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
                                          '状态抗性': ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
                                          '无敌': ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
                                          '标记': ['tree', {'list': ['tree', {'类型': ['text', ''], '代码': ['number', 0]}, 1, 1, False]}],
                                          '叠加': ['tree', {'list': ['tree', {'代码1': ['number', 0], '代码2': ['number', 0]}, 1, 1, False]}],
                                          '生效目标': ['tree', {'不分类': ['tree', {"list":
                                                                                 ['tree', {'代码': ['number', 1], 'list':
                                                                                     ['tree', {'代码': ['number', 1], 'list':
                                                                                         ['tree', {'代码': ['number', 1]}, 1, 1, False]
                                                                                               }, 1, 1, False]
                                                                                           }, 1, 0, True]
                                                                             }]}],
                                          }, 1, 1, False]}],
        "技能免疫": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "无敌": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "技能抵挡": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "技能反弹": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "技能传递": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "技能窃取": ['tree', {'list': ['tree', {'代码': ['number', 0]}, 1, 1, False], '代码': ['number', 0], '简述': ['text', '']}],
        "幻象": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "破坏": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "持续施法": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "躲避": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "缠绕": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "即时攻击": ['tree', {'list': ['tree', {'代码': ['number', 0], '简述': ['text', '']}, 1, 1, False], '代码': ['number', 0], '简述': ['text', '']}],
        "视野": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "真实视域": ['tree', {'代码': ['number', 0], '简述': ['text', '']}],
        "施法前摇": ['tree', {'代码': ['tree', {'list': ['text', '', 0, 4, False]}], '修正': ['tree', {'list': ['text', '', 1, 1, False]}], '即时生效': ['tree', {'代码': ['number', 0]}]}],
        "施法后摇": ['tree', {'代码': ['tree', {'list': ['text', '', 0, 4, False]}], '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}],
        "魔法消耗": ['tree', {'list': ['tree', {'名称': ['text', ''], 'list': ['tree', {
            '代码': ['tree', {'list': ['text', '', 0, 4, False]}],
            '类型': ['tree', {'代码': ['number', 1]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 1, False]}, 1, 1, False]}],
        "冷却时间": ['tree', {'list': ['tree', {
            '名称': ['text', ''],
            '代码': ['tree', {'list': ['text', '', 0, 4, False]}],
            '类型': ['tree', {'代码': ['number', 1]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 1, False]}],
        "属性": ['tree', {'list': ['tree', {
            '名称': ['text', ''],
            '后缀': ['text', ''],
            '代码': ['tree', {'list': ['text', '', 0, 4, False]}],
            '修正': ['tree', {'list': ['text', '', 1, 1, False]}]}, 1, 1, False]}],
        "升级": ['tree', {
            'A杖': ['tree', {'list': ['tree', {'目标': ['tree', {'list': ['text', '', 0, 4, False]}], '值': ['random_tree', {}], }, 1, 0, True]}],
            '技能': ['tree', {'list': ['tree', {'目标': ['tree', {'list': ['text', '', 0, 4, False]}], '值': ['random_tree', {}], }, 1, 0, True]}],
            '混合': ['tree', {
                'list': ['tree', {'目标': ['tree', {'list': ['text', '', 0, 4, False]}], '来源技能': ['tree', {"1": ['text', ""], "2": ['text', ""]}], '值': ['random_tree', {}], }, 1, 0,
                         True]}]
        }]
    }
}
