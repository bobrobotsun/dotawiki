#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
修改页面，用于修改、增加一个新的属性页，属性页的性质和填写方式由不同的dict进行决定。


作者: 莫无煜
网站: https://dota.huijiwiki.com
"""

import json
import requests
import os
import time
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from text_to_json import hero, ability, item, unit


class Edit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initParam()
        self.initUI()

    def initParam(self):
        self.title = 'dotawiki'
        # 登录用的一些东西，包括网址、request（包含cookie）、api指令
        self.target_url = 'https://dota.huijiwiki.com/w/api.php'
        self.seesion = requests.session()
        self.get_login_token_data = {'action': 'query', 'meta': 'tokens', 'type': 'login', 'format': 'json'}
        self.login_data = {'action': 'clientlogin', 'loginreturnurl': 'https://www.huijiwiki.com/', 'rememberMe': 1, 'format': 'json'}
        self.get_csrf_token_data = {'action': 'query', 'meta': 'tokens', 'format': 'json'}
        self.logout_data = {'action': 'logout', 'format': 'json'}
        # 菜单栏
        self.ml = {}
        self.mainlayout = {}
        # 获取屏幕大小
        screen_rect = QApplication.desktop().screenGeometry()
        self.screen_size = [screen_rect.width(), screen_rect.height()]
        # 图标
        self.icon = QIcon(os.path.join('material_lib', 'DOTA2.jpg'))
        # 数据库信息

    def initUI(self):
        # 设定软件的图标
        self.setWindowIcon(self.icon)
        # 设定窗口大小、位置至0.8倍屏幕长宽，且边缘为0.1倍长宽
        self.setGeometry(self.screen_size[0] * 0.1, self.screen_size[1] * 0.1, self.screen_size[0] * 0.8, self.screen_size[1] * 0.8)
        # 创建一个菜单栏
        self.create_menubar()
        self.main_layout()
        self.checklogin()
        self.show()
        self.load_data()
        # 设定窗口状态栏
        # self.statusBar().showMessage('准备完毕')


