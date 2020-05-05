def menu_init(menu):
    menu['单位']['英雄']=[]
    menu['单位']['召唤物']=[]
    menu['单位']['守卫']=[]
    menu['单位']['英雄级单位']=[]
    menu['单位']['中立生物']=[]
    menu['单位']['远古生物']=[]
    menu['单位']['小兵']=[]

    menu['地图']['物品']=[]
    menu['地图']['中立物品']=[]
    menu['地图']['神符']=[]
    return menu

def menu_单位_召唤物(json):
    return json['类型']=='召唤物'

def menu_单位_守卫(json):
    return '关联类型' in json and json['关联类型']=='守卫'

def menu_单位_英雄级单位(json):
    return int(json['英雄级单位']["1"]["1"])==1

def menu_单位_中立生物(json):
    return json['类型']=='中立生物'

def menu_单位_远古生物(json):
    return int(json['远古单位']["1"]["1"])==1

def menu_单位_小兵(json):
    return json['类型']=='士兵'

def menu_地图_中立物品(json):
    for i in json['商店']:
        if '中立' in json['商店'][i]:
            return True
    return False

def menu_地图_神符(json):
    return '神符' in json['页面名']