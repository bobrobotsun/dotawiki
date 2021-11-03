#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
主页面，用于在开启软件后的显示窗口，用于展示绝大多数功能


作者: 莫无煜
网站: https://dota.huijiwiki.com
"""

import json
import requests
import os
import time
import threading
import copy
import vpk
import re
import math
import hashlib
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from text_to_json import hero, ability, item, unit, mechnism, unitgroup, edit_json, dota_menus, page, common_page, translate
from text_to_json.WikiError import editerror
import win32con
import win32clipboard as wincld
from xpinyin import Pinyin


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initParam()
        self.initUI()

    def initParam(self):
        self.version = '7.30e'
        self.title = 'dotawiki'
        # 登录用的一些东西，包括网址、request（包含cookie）、api指令
        self.target_url = 'http://dota.huijiwiki.com/w/api.php'
        self.image_url = 'http://huiji-public.huijistatic.com/dota/uploads'
        self.seesion = requests.session()
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
        self.get_login_token_data = {'action': 'query', 'meta': 'tokens', 'type': 'login', 'format': 'json'}
        self.login_data = {'action': 'clientlogin', 'loginreturnurl': 'http://www.huijiwiki.com/', 'rememberMe': 1, 'format': 'json'}
        self.get_csrf_token_data = {'action': 'query', 'meta': 'tokens', 'format': 'json'}
        self.logout_data = {'action': 'logout', 'format': 'json'}
        # 菜单栏
        self.ml = {}
        self.mainlayout = {}
        # 获取屏幕大小
        screen_rect = QApplication.desktop().screenGeometry()
        self.screen_size = [screen_rect.width(), screen_rect.height()]
        # 登录用的账号密码
        self.login_file_name = os.path.join('database', 'login.json')
        # 图标
        self.icon = QIcon(os.path.join('material_lib', 'DOTA2.jpg'))
        # 数据库信息
        self.text_base = {"英雄": {}, "非英雄单位": {}, "物品": {}, "技能": {}, "翻译": {}}
        self.json_base = {"英雄": {}, "非英雄单位": {}, "物品": {}, "技能": {}, '技能源': {}, '单位组': {}, "机制": {}, '机制源': {}}
        self.json_name = {"英雄": [], "非英雄单位": [], "物品": [], "技能": [], '技能源': [], '单位组': [], "机制": [], '机制源': []}
        self.entry_base = {}
        self.upgrade_base = {}
        self.mech = {}
        self.red = QBrush(Qt.red)
        self.green = QBrush(Qt.green)
        # 版本更新的内容
        self.version_list = {}
        self.version_base = {}
        # 曾用名的内容
        self.name_base = {'历史': [], '原生': [], '衍生': []}
        # 时间函数
        self.time_point_for_iterable_sleep = time.time()

    def initUI(self):
        # 设定软件的图标
        self.setWindowIcon(self.icon)
        # 设定窗口大小、位置至0.8倍屏幕长宽，且边缘为0.1倍长宽
        self.setGeometry(self.screen_size[0] * 0.02, self.screen_size[1] * 0.1, self.screen_size[0] * 0.96, self.screen_size[1] * 0.8)
        # 创建一个菜单栏
        self.create_menubar()
        self.main_layout()
        self.checklogin()
        self.show()
        self.load_data()
        self.check_test()
        self.fix_window_with_json_data()
        # 设定窗口状态栏
        # self.statusBar().showMessage('准备完毕')

    # 控制窗口显示在屏幕中心的方法
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 这是用来控制间隔时间的函数
    def time_point_for_iterable_sleep_by_time(self, staytime=0.06, pasttime=0.0):
        if pasttime == 0:
            pasttime = self.time_point_for_iterable_sleep
        temptime = time.time()
        if temptime - pasttime < staytime:
            time.sleep(staytime + pasttime - temptime)
        self.time_point_for_iterable_sleep = time.time()

    # 将文字转换为整数、2位小数,不行就返回文字
    def str_to_number(self, text, round_value=2):
        try:
            if float(int(text)) == float(text):
                return int(text)
            else:
                return float(round(text, round_value))
        except ValueError:
            return str(text)

    # 创建菜单栏
    def create_menubar(self):
        # menulist的简写，后面太多太复杂了，所以简单点
        self.ml = {}
        self.ml[0] = self.menuBar()
        # 文件栏
        self.ml['文件'] = {0: self.ml[0].addMenu('文件')}
        self.ml['文件']['登录'] = self.ml['文件'][0].addAction('登录')
        self.ml['文件']['登录'].triggered.connect(self.new_login_window)
        self.ml['文件']['注销'] = self.ml['文件'][0].addAction('注销')
        self.ml['文件']['注销'].triggered.connect(self.logout)
        self.ml['文件']['切换账号'] = self.ml['文件'][0].addAction('切换账号')
        self.ml['文件']['切换账号'].triggered.connect(self.change_account)
        self.ml['文件'][0].addSeparator()
        self.ml['文件']['退出'] = self.ml['文件'][0].addAction('退出')
        self.ml['文件']['退出'].triggered.connect(self.close)
        """"""
        self.ml['数据'] = {0: self.ml[0].addMenu('数据')}
        self.ml['数据']['重新加载数据'] = self.ml['数据'][0].addAction('重新加载数据')
        self.ml['数据']['重新加载数据'].triggered.connect(self.load_data)
        self.ml['数据']['从DOTA2游戏文件中读取基础数据'] = self.ml['数据'][0].addAction('从DOTA2游戏文件中读取基础数据')
        self.ml['数据']['从DOTA2游戏文件中读取基础数据'].triggered.connect(self.get_data_from_text)
        self.ml['数据']['从wiki重新下载基础数据'] = self.ml['数据'][0].addAction('从wiki重新下载基础数据')
        self.ml['数据']['从wiki重新下载基础数据'].triggered.connect(lambda: self.download_text_base)
        self.ml['数据']['从wiki重新下载合成数据'] = self.ml['数据'][0].addAction('从wiki重新下载合成数据')
        self.ml['数据']['从wiki重新下载合成数据'].triggered.connect(lambda: self.download_json_base)
        self.ml['数据']['从wiki重新下载合成数据列表'] = self.ml['数据'][0].addAction('从wiki重新下载合成数据列表')
        self.ml['数据']['从wiki重新下载合成数据列表'].triggered.connect(lambda: self.download_json_name)
        self.ml['数据']['从wiki重新下载机制定义'] = self.ml['数据'][0].addAction('从wiki重新下载机制定义')
        self.ml['数据']['从wiki重新下载机制定义'].triggered.connect(lambda: self.download_mech)
        self.ml['数据']['将wiki目录进行更新（不要乱点）'] = self.ml['数据'][0].addAction('将wiki目录进行更新（不要乱点）')
        self.ml['数据']['将wiki目录进行更新（不要乱点）'].triggered.connect(lambda: self.download_and_upload_wiki_menu)

    def checklogin(self):
        try:
            loginwords = open(self.login_file_name, mode="r", encoding="utf-8")
            logintxt = loginwords.read()
            if logintxt == '':
                self.login_success(False)
            else:
                self.login(json.loads(logintxt))
            loginwords.close()
        except FileNotFoundError:
            self.login_success(False)

    # 自动登录，通过读取文件夹内的文件储存的用户名和密码进行登录
    def login(self, password, **kwargs):
        # 判断此时是否打开了登录窗口
        if 'window' in kwargs:
            window = True
        else:
            window = False
            kwargs['window'] = self
        tryi = 0
        while True:
            # 获取登录令牌
            login_token = self.seesion.post(self.target_url, data=self.get_login_token_data, headers=self.header)
            # 使用登录令牌登录
            if login_token.status_code < 400:
                login_token_json = login_token.json()
                self.login_data['logintoken'] = login_token_json['query']['tokens']['logintoken']
                break
            else:
                tryi += 1
                self.time_point_for_iterable_sleep_by_time()
                QMessageBox.critical(self, '登录遭遇阻碍', '暂时登录失败，已尝试' + str(tryi) + '次！错误代码：' + str(login_token.status_code))
        self.login_data['username'] = password['用户名']
        self.login_data['password'] = password['密码']
        tryi = 0
        while True:
            login_info = self.seesion.post(self.target_url, data=self.login_data, headers=self.header)
            # 判断登录效果
            if login_info.status_code != 200 or login_info.json()["clientlogin"]["status"] == "FAIL":
                tryi += 1
                self.time_point_for_iterable_sleep_by_time()
                if tryi > 100:
                    messageBox = QMessageBox(QMessageBox.Critical, "登录失败", "请问是否重新登录？", QMessageBox.NoButton, self)
                    buttonY = messageBox.addButton('重新登录', QMessageBox.YesRole)
                    buttonN = messageBox.addButton('放弃登录', QMessageBox.YesRole)
                    messageBox.exec_()
                    if messageBox.clickedButton() == buttonY:
                        if not window:
                            self.new_login_window()
                            self.login_success(False)
                    else:
                        if window:
                            kwargs['window'].close()
                    break
            else:
                self.csrf_token = self.seesion.post(self.target_url, data=self.get_csrf_token_data, headers=self.header).json()['query']['tokens']['csrftoken']
                self.login_success(True, username=login_info.json()["clientlogin"]["username"], password=password['密码'])
                if window:
                    kwargs['window'].close()
                break

    # 通过一个新的窗口，进行登录
    def new_login_window(self):
        inputwindow = QDialog()
        # 设定软件的图标
        inputwindow.setWindowIcon(self.icon)
        # 设置窗口的标题
        inputwindow.setWindowTitle('登录')
        namelable = QLabel('用户名', inputwindow)
        nametext = QLineEdit('', inputwindow)
        passlable = QLabel('密码', inputwindow)
        passtext = QLineEdit('', inputwindow)
        passtext.setEchoMode(3)
        # 按钮
        yesbutton = QPushButton('确认登录', inputwindow)
        yesbutton.clicked.connect(lambda: self.login(password={'用户名': nametext.text(), '密码': passtext.text()}, window=inputwindow))
        nobutton = QPushButton('暂不登录', inputwindow)
        nobutton.clicked.connect(inputwindow.close)

        grid = QGridLayout()
        grid.setSpacing(self.screen_size[0] * 0.01)
        grid.addWidget(namelable, 0, 0)
        grid.addWidget(nametext, 0, 1)
        grid.addWidget(passlable, 1, 0)
        grid.addWidget(passtext, 1, 1)

        hbox = QHBoxLayout()
        hbox.addWidget(yesbutton)
        hbox.addWidget(nobutton)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(hbox)

        inputwindow.setLayout(vbox)
        inputwindow.show()

    # 登出
    def logout(self):
        logout_info = self.seesion.post(self.target_url, data=self.logout_data, headers=self.header)
        self.login_success(False)

    # 登出
    def change_account(self):
        self.logout()
        self.new_login_window()

    # 登录成功/失败后的一系列程序调整
    def login_success(self, bool, **kwargs):
        if bool:
            self.setWindowTitle(self.title + '\t\t【登录用户：' + kwargs['username'] + '】')
            self.ml['文件']['登录'].setEnabled(False)
            self.ml['文件']['注销'].setEnabled(True)
            self.ml['文件']['切换账号'].setEnabled(True)
            with open(self.login_file_name, mode='w', encoding="utf-8") as l:
                l.write(json.dumps({'用户名': kwargs['username'], '密码': kwargs['password']}))
        else:
            self.setWindowTitle(self.title + '\t\t【未登录】')
            self.ml['文件']['登录'].setEnabled(True)
            self.ml['文件']['注销'].setEnabled(False)
            self.ml['文件']['切换账号'].setEnabled(False)

            with open(self.login_file_name, mode='w', encoding="utf-8") as l:
                l.write('')

    # 以下是窗口布局
    def main_layout(self):
        self.setCentralWidget(QTabWidget(self))
        self.mainWidget = QWidget(self)
        self.centralWidget().addTab(self.mainWidget, '主页')
        self.mainlayout = {0: QVBoxLayout()}
        self.mainWidget.setLayout(self.mainlayout[0])
        self.mainlayout['加载信息'] = {0: QGroupBox('加载信息', self)}
        self.mainlayout[0].addWidget(self.mainlayout['加载信息'][0])
        self.mainlayout['加载信息']['信息'] = {0: QHBoxLayout()}
        self.mainlayout['加载信息'][0].setLayout(self.mainlayout['加载信息']['信息'][0])
        # self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['英雄'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['英雄'].setText('【英雄】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['英雄'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['非英雄单位'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['非英雄单位'].setText('【非英雄单位】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['非英雄单位'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['技能'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['技能'].setText('【技能】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['技能'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['技能源'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['技能源'].setText('【技能源】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['技能源'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['物品'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['物品'].setText('【物品】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['物品'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['单位组'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['单位组'].setText('【单位组】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['单位组'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['机制'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['机制'].setText('【机制】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['机制'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['机制源'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['机制源'].setText('【机制源】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['机制源'])
        # self.mainlayout['加载信息']['信息'][0].addStretch(1)

        self.mainlayout['加载按钮'] = {0: QHBoxLayout()}
        self.mainlayout[0].addLayout(self.mainlayout['加载按钮'][0])
        # self.mainlayout['加载按钮']['重新加载数据'] = QPushButton('重新加载数据', self)
        # self.mainlayout['加载按钮']['重新加载数据'].clicked.connect(self.load_data)
        # self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['重新加载数据'])
        self.mainlayout['加载按钮']['从wiki重新下载机制定义'] = QPushButton('1、下载机制定义（一般跳过即可）', self)
        self.mainlayout['加载按钮']['从wiki重新下载机制定义'].clicked.connect(self.download_mech)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载机制定义'])
        self.mainlayout['加载按钮']['重新读取DOTA2文件'] = QPushButton('2、读本地游戏文件（可跳过）', self)
        self.mainlayout['加载按钮']['重新读取DOTA2文件'].clicked.connect(self.get_data_from_text)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['重新读取DOTA2文件'])
        # self.mainlayout['加载按钮']['从wiki重新下载基础数据'] = QPushButton('从wiki重新下载基础数据', self)
        # self.mainlayout['加载按钮']['从wiki重新下载基础数据'].clicked.connect(self.download_text_base)
        # self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载基础数据'])
        self.mainlayout['加载按钮']['从wiki重新下载合成数据列表'] = QPushButton('3、下载列表（必点）', self)
        self.mainlayout['加载按钮']['从wiki重新下载合成数据列表'].clicked.connect(self.download_json_name)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载合成数据列表'])
        self.mainlayout['加载按钮']['从wiki重新下载合成数据'] = QPushButton('4、开始下载内容（正式下）', self)
        self.mainlayout['加载按钮']['从wiki重新下载合成数据'].clicked.connect(self.download_json_base)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载合成数据'])
        self.mainlayout['加载按钮'][0].addStretch(1)
        self.mainlayout['加载按钮']['将wiki目录进行更新（不要乱点）'] = QPushButton('将wiki目录进行更新（不要乱点）', self)
        self.mainlayout['加载按钮']['将wiki目录进行更新（不要乱点）'].clicked.connect(self.download_and_upload_wiki_menu)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['将wiki目录进行更新（不要乱点）'])
        self.mainlayout['加载按钮']['更新独立的页面（不要乱点）'] = QPushButton('更新独立的页面（不要乱点）', self)
        self.mainlayout['加载按钮']['更新独立的页面（不要乱点）'].clicked.connect(self.download_and_upload_single_pages)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['更新独立的页面（不要乱点）'])

        self.mainlayout['列表'] = {0: QHBoxLayout()}
        self.mainlayout[0].addLayout(self.mainlayout['列表'][0])
        self.mainlayout['列表']['英雄'] = {0: QGroupBox('英雄', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['英雄'][0])
        self.mainlayout['列表']['英雄']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['英雄'][0].setLayout(self.mainlayout['列表']['英雄']['布局'][0])
        self.mainlayout['列表']['英雄']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['英雄']['布局'][0].addWidget(self.mainlayout['列表']['英雄']['布局']['列表'])
        self.mainlayout['列表']['非英雄单位'] = {0: QGroupBox('非英雄单位', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['非英雄单位'][0])
        self.mainlayout['列表']['非英雄单位']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['非英雄单位'][0].setLayout(self.mainlayout['列表']['非英雄单位']['布局'][0])
        self.mainlayout['列表']['非英雄单位']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['非英雄单位']['布局'][0].addWidget(self.mainlayout['列表']['非英雄单位']['布局']['列表'])
        self.mainlayout['列表']['技能'] = {0: QGroupBox('技能', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['技能'][0])
        self.mainlayout['列表']['技能']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['技能'][0].setLayout(self.mainlayout['列表']['技能']['布局'][0])
        self.mainlayout['列表']['技能']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['技能']['布局'][0].addWidget(self.mainlayout['列表']['技能']['布局']['列表'])
        self.mainlayout['列表']['技能源'] = {0: QGroupBox('技能源', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['技能源'][0])
        self.mainlayout['列表']['技能源']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['技能源'][0].setLayout(self.mainlayout['列表']['技能源']['布局'][0])
        self.mainlayout['列表']['技能源']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['技能源']['布局'][0].addWidget(self.mainlayout['列表']['技能源']['布局']['列表'])
        self.mainlayout['列表']['物品'] = {0: QGroupBox('物品', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['物品'][0])
        self.mainlayout['列表']['物品']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['物品'][0].setLayout(self.mainlayout['列表']['物品']['布局'][0])
        self.mainlayout['列表']['物品']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['物品']['布局'][0].addWidget(self.mainlayout['列表']['物品']['布局']['列表'])
        self.mainlayout['列表']['单位组'] = {0: QGroupBox('单位组', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['单位组'][0])
        self.mainlayout['列表']['单位组']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['单位组'][0].setLayout(self.mainlayout['列表']['单位组']['布局'][0])
        self.mainlayout['列表']['单位组']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['单位组']['布局'][0].addWidget(self.mainlayout['列表']['单位组']['布局']['列表'])
        self.mainlayout['列表']['机制'] = {0: QGroupBox('机制', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['机制'][0])
        self.mainlayout['列表']['机制']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['机制'][0].setLayout(self.mainlayout['列表']['机制']['布局'][0])
        self.mainlayout['列表']['机制']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['机制']['布局'][0].addWidget(self.mainlayout['列表']['机制']['布局']['列表'])
        self.mainlayout['列表']['机制源'] = {0: QGroupBox('机制源', self)}
        self.mainlayout['列表'][0].addWidget(self.mainlayout['列表']['机制源'][0])
        self.mainlayout['列表']['机制源']['布局'] = {0: QVBoxLayout()}
        self.mainlayout['列表']['机制源'][0].setLayout(self.mainlayout['列表']['机制源']['布局'][0])
        self.mainlayout['列表']['机制源']['布局']['列表'] = QListWidget()
        self.mainlayout['列表']['机制源']['布局'][0].addWidget(self.mainlayout['列表']['机制源']['布局']['列表'])
        """
        上面是主页情况
        下面是修改页面
        """

    # 以下是数据相关的内容
    # 自动读取软件数据库中保存的数据
    def load_data(self):
        try:
            basefile = open(os.path.join('database', 'text_base.json'), mode="r", encoding="utf-8")
            self.text_base = json.loads(basefile.read())
            basefile.close()
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "请问您准备从哪里重新获取基础数据？", QMessageBox.NoButton, self)
            buttonWeb = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            buttonFile = messageBox.addButton('从游戏文件获取', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == buttonWeb:
                self.download_text_base()
            elif messageBox.clickedButton() == buttonFile:
                self.get_data_from_text()
        try:
            basefile = open(os.path.join('database', 'json_base.json'), mode="r", encoding="utf-8")
            self.json_base = json.loads(basefile.read())
            basefile.close()
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "请问您是否准备从wiki下载合成数据？", QMessageBox.NoButton, self)
            button1 = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            button2 = messageBox.addButton('没有网络，没法下载', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == button1:
                self.download_json_base()
        try:
            basefile = open(os.path.join('database', 'json_name.json'), mode="r", encoding="utf-8")
            self.json_name = json.loads(basefile.read())
            basefile.close()
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "请问您是否准备从wiki下载合成数据列表？", QMessageBox.NoButton, self)
            button1 = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            button2 = messageBox.addButton('没有网络，没法下载', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == button1:
                self.download_json_name()
        try:
            basefile = open(os.path.join('database', 'mech.json'), mode="r", encoding="utf-8")
            self.mech = json.loads(basefile.read())
            basefile.close()
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "请问您是否准备从wiki下载机制定义？", QMessageBox.NoButton, self)
            button1 = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            button2 = messageBox.addButton('没有网络，没法下载', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == button1:
                self.download_mech()
        try:
            basefile = open(os.path.join('database', 'name_base.json'), mode="r", encoding="utf-8")
            self.name_base = json.loads(basefile.read())
            basefile.close()
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "请问您是否准备从wiki下载曾用名？", QMessageBox.NoButton, self)
            button1 = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            button2 = messageBox.addButton('没有网络，没法下载', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == button1:
                self.download_name_base()
        try:
            basefile = open(os.path.join('database', 'entry_base.json'), mode="r", encoding="utf-8")
            self.entry_base = json.loads(basefile.read())
            basefile.close()
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "请问您是否准备从wiki下载词汇库？", QMessageBox.NoButton, self)
            button1 = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            button2 = messageBox.addButton('没有网络，没法下载', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == button1:
                self.download_entry_base()

    def get_data_from_text(self):
        try:
            basefile = open(os.path.join('database', 'dota2_address.json'), mode="r", encoding="utf-8")
            address = basefile.read()
            basefile.close()
            self.catch_file_from_dota2(address, False)
        except FileNotFoundError:
            self.find_dota2_folder()

    def find_dota2_folder(self):
        folders = ['steamapps', 'common', 'dota 2 beta', 'game', 'dota', 'scripts', 'npc']
        nowaddress = QFileDialog.getExistingDirectory(self, '请选择Steam的安装路径（使用完美启动器的用户请选择DOTA2目录下的steam文件夹）', '/home')
        for i in range(len(folders)):
            if folders[i] in os.listdir(nowaddress):
                nowaddress = os.path.join(nowaddress, folders[i])
            else:
                messageBox = QMessageBox(QMessageBox.Critical, '错误的路径',
                                         '您选择的路径下的' + nowaddress + '没有发现文件夹' + folders[i] + '\n请问是否重新重新选择Steam的安装路径？',
                                         QMessageBox.NoButton, self)
                button1 = messageBox.addButton('重新选择路径', QMessageBox.ResetRole)
                button2 = messageBox.addButton('选择从网上下载', QMessageBox.YesRole)
                button3 = messageBox.addButton('放弃加载，另寻出路', QMessageBox.NoRole)
                messageBox.exec_()
                if messageBox.clickedButton() == button1:
                    self.find_dota2_folder()
                elif messageBox.clickedButton() == button2:
                    self.download_text_base()
                return
        self.catch_file_from_dota2(nowaddress)

    def catch_file_from_dota2(self, address, bools=True):
        has_text = [['英雄', '技能', '非英雄单位', '物品', '翻译'],
                    ['npc_heroes.txt', 'npc_abilities.txt', 'npc_units.txt', 'items.txt'],
                    [False, False, False]]
        ttt = ''
        for i in range(3):
            if i > 0:
                ttt += '\n'
            ttt += has_text[0][i] + '数据：'
            if has_text[1][i] in os.listdir(address):
                ttt += '文件存在，成功读取'
                has_text[2][i] = True
            else:
                ttt += has_text[1][i] + '文件不存在，读取失败'
        ttt += '\n已经从vpk处提取物品、翻译文件'
        if has_text[2][0] or has_text[2][1] or has_text[2][2]:
            if has_text[2][0]:
                hero.get_hero_data_from_txt(self.text_base['英雄'], os.path.join(address, has_text[1][0]))
            if has_text[2][1]:
                ability.get_hero_data_from_txt(self.text_base['技能'], os.path.join(address, has_text[1][1]))
            if has_text[2][2]:
                unit.get_hero_data_from_txt(self.text_base['非英雄单位'], os.path.join(address, has_text[1][2]))
            pak1 = vpk.open(address.replace('scripts\\npc', "pak01_dir.vpk"))
            hero.get_lore_data_from_vpk(self.text_base['英雄'], pak1.get_file("resource/localization/hero_lore_schinese.txt"))
            hero.get_dota_data_from_vpk(self.text_base['英雄'], pak1.get_file("resource/localization/dota_schinese.txt"))
            ability.get_dota_data_from_vpk(self.text_base['技能'], pak1.get_file("resource/localization/abilities_schinese.txt"))
            item.get_hero_data_from_txt(self.text_base['物品'], pak1.get_file("scripts/npc/items.txt"))
            item.get_dota_data_from_vpk(self.text_base['物品'], pak1.get_file("resource/localization/abilities_schinese.txt"))
            translate.get_dota_data_from_vpk(self.text_base['翻译'], pak1.get_file("resource/localization/dota_schinese.txt"), pak1.get_file("resource/localization/dota_english.txt"))
            self.file_save(os.path.join('database', 'dota2_address.json'), address)
            self.file_save(os.path.join('database', 'text_base.json'), json.dumps(self.text_base))
            messagebox = QMessageBox(QMessageBox.Information, '文件抓取', ttt, QMessageBox.NoButton, self)
            messagebox.setStandardButtons(QMessageBox.Ok)
            messagebox.exec_()
            if bools:
                self.edit_category_selected_changed()
        else:
            messagebox = QMessageBox(QMessageBox.Critical, '错误的路径', '路径错误，没有发现任何有效文件，请重新选择路径！', QMessageBox.NoButton, self)
            messagebox.setStandardButtons(QMessageBox.Ok)
            messagebox.button(QMessageBox.Ok).animateClick(1000)
            messagebox.exec_()
            self.find_dota2_folder()

    # 将文件保存在目标文件夹内
    def file_save(self, file, content):
        with open(file, mode="w") as f:
            f.write(content)

    # 从wiki网站上下载对应的信息
    def download_json(self, pagename):
        if pagename[-5:] != '.json':
            pagename += '.json'
        download_data = {'action': 'jsondata', 'title': pagename, 'format': 'json'}
        warn = 0
        while True:
            self.time_point_for_iterable_sleep_by_time()
            download_info = self.seesion.post(self.target_url, data=download_data, headers=self.header)
            if download_info.status_code == 200:
                return download_info.json()['jsondata']
            else:
                warn += 1

    def download_text_base(self):
        self.text_base = self.download_json('text_base.json')
        self.file_save(os.path.join('database', 'text_base.json'), json.dumps(self.text_base))

    def download_json_name(self):
        for i in self.json_name:
            temp = self.seesion.post(self.target_url, headers=self.header,
                                     data={'action': 'parse', 'text': '{{#invoke:json|api_all_page_names|' + i + '}}', 'contentmodel': 'wikitext', 'prop': 'text',
                                           'disablelimitreport': 'false', 'format': 'json'}).json()['parse']['text']['*']
            texttemp = re.sub('<.*?>', '', temp)[:-1]
            tempjson = json.loads(texttemp)
            self.json_name.update(tempjson)
        self.file_save(os.path.join('database', 'json_name.json'), json.dumps(self.json_name))
        QMessageBox.information(self, '下载合成数据完成', '下载合成数据完成，请继续操作')

    def download_name_base(self):
        self.name_base = self.download_json('name_base.json')
        self.name_initial_name_base()
        self.file_save(os.path.join('database', 'name_base.json'), json.dumps(self.name_base))
        QMessageBox.information(self, '下载曾用名库完成', '下载曾用名库完成，请继续操作')

    def download_entry_base(self):
        self.entry_base = self.download_json('entry_base.json')
        self.entry_resort()
        self.entry_refresh_tree()
        self.file_save(os.path.join('database', 'entry_base.json'), json.dumps(self.entry_base))
        QMessageBox.information(self, '下载词汇库完成', '下载词汇库完成，请继续操作')

    def update_json_name(self, list):
        for i in list:
            for j in list[i]:
                if j not in self.json_name[i]:
                    self.json_name[i].append(j)

    def download_mech(self):
        self.mech = self.download_json('机制检索.json')
        self.file_save(os.path.join('database', 'mech.json'), json.dumps(self.mech))
        QMessageBox.information(self, '下载机制定义完成', '下载机制定义完成，请继续操作')

    def download_and_upload_wiki_menu(self):
        wiki_result = self.seesion.post(self.target_url, headers=self.header,
                                        data={'action': 'jsondata', 'title': '机制.json', 'format': 'json'}).json()
        wiki_menu = dota_menus.menu_init(wiki_result['jsondata'])
        for i in self.json_base['英雄']:
            wiki_menu['单位']['英雄'].append(i)

        for i in self.json_base['非英雄单位']:
            if self.json_base['非英雄单位'][i]['应用'] == 1:
                if dota_menus.menu_单位_召唤物(self.json_base['非英雄单位'][i]):
                    wiki_menu['单位']['召唤物'].append(i)
                if dota_menus.menu_单位_守卫(self.json_base['非英雄单位'][i]):
                    wiki_menu['单位']['守卫'].append(i)
                if dota_menus.menu_单位_英雄级单位(self.json_base['非英雄单位'][i]):
                    wiki_menu['单位']['英雄级单位'].append(i)
                if dota_menus.menu_单位_中立生物(self.json_base['非英雄单位'][i]):
                    wiki_menu['单位']['中立生物'].append(i)
                if dota_menus.menu_单位_远古生物(self.json_base['非英雄单位'][i]):
                    wiki_menu['单位']['远古生物'].append(i)
                if dota_menus.menu_单位_小兵(self.json_base['非英雄单位'][i]):
                    wiki_menu['单位']['小兵'].append(i)

        for i in self.json_base['物品']:
            if self.json_base['物品'][i]['应用'] == 1:
                wiki_menu['地图']['物品'].append(i)
                if dota_menus.menu_地图_中立物品(self.json_base['物品'][i]):
                    wiki_menu['地图']['中立物品'].append(i)

        for i in self.json_base['技能']:
            if dota_menus.menu_地图_神符(self.json_base['技能'][i]):
                wiki_menu['地图']['神符'].append(i)

        for i in range(8):
            wiki_menu['版本'].append(self.version_list['版本'][-1 * i - 1][0])
        self.upload_json('机制.json', wiki_menu)
        QMessageBox.information(self, '更改完毕', "已经将wiki目录更改完毕", QMessageBox.Yes, QMessageBox.Yes)

    def download_and_upload_single_pages(self):
        info_txt = ''
        info_txt += page.common_code_chat_page(self.seesion, self.csrf_token, self.change_all_template_link_to_html)
        info_txt += page.common_code_hero_page(self.json_base, self.seesion, self.csrf_token, self.change_all_template_link_to_html)
        info_txt += page.common_code_item_page(self.json_base, self.seesion, self.csrf_token, self.change_all_template_link_to_html)
        info_txt += page.translate_page_dota_hud_error(self.text_base['翻译'], self.seesion, self.csrf_token, self.change_all_template_link_to_html)
        QMessageBox.information(self, '更改完毕', info_txt, QMessageBox.Yes, QMessageBox.Yes)

    def download_json_base(self):
        try:
            namefile = open(os.path.join('database', 'json_name.json'), mode="r", encoding="utf-8")
            self.json_name = json.loads(namefile.read())
            namefile.close()
            total_num = 0
            for i in self.json_name:
                total_num += len(self.json_name[i])
            self.progress = upload_text('开始下载json')
            self.progress.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
            self.progress.setWindowIcon(self.icon)
            self.progress.setWindowTitle('下载json中……')
            self.current_num = [0, 0]
            self.download_json_list = []
            self.lock = threading.Lock()
            self.local = threading.local()
            for i in self.json_name:
                self.json_base[i] = {}
                for j in self.json_name[i]:
                    if i[-1] == '源':
                        self.download_json_list.append([i, j, j + '/源.json'])
                    else:
                        self.download_json_list.append([i, j, j + '.json'])
            self.progress.confirm_numbers(len(self.download_json_list))
            self.startactiveCount = threading.activeCount()
            for i in range(20):
                t = threading.Thread(target=self.download_json_thread, name='线程-' + str(i + 1001))
                t.start()
        except FileNotFoundError:
            mb = QMessageBox(QMessageBox.Critical, "获取名称集失败", "请问您是否准备从wiki下载合成数据列表？", QMessageBox.NoButton, self)
            button1 = mb.addButton('从网络下载', QMessageBox.YesRole)
            button2 = mb.addButton('没有网络，没法下载', QMessageBox.NoRole)
            mb.exec_()
            if mb.clickedButton() == button1:
                self.download_json_name()

    def download_json_thread(self):
        while True:
            self.lock.acquire()
            try:
                self.local.current_num = self.current_num[1]
                self.current_num[1] += 1
                if self.local.current_num >= len(self.download_json_list):
                    break
            except Exception as xx:
                print(self.download_json_list[self.local.current_num], '：分配出现错误，原因为：' + str(xx))
            finally:
                self.lock.release()
            self.local.download_data = {'action': 'jsondata', 'title': self.download_json_list[self.local.current_num][2], 'format': 'json'}
            self.local.seesion = self.seesion
            self.local.target_url = self.target_url
            self.local.k = 0
            while True:
                self.local.download_info = self.local.seesion.post(self.local.target_url, headers=self.header, data=self.local.download_data)
                self.lock.acquire()
                if self.local.download_info.status_code < 400:
                    try:
                        self.local.jsons = self.local.download_info.json()
                    except Exception as xx:
                        print(self.download_json_list[self.local.current_num], '：下载出现错误，原因为：' + str(xx))
                        continue
                    else:
                        self.json_base[self.download_json_list[self.local.current_num][0]][self.download_json_list[self.local.current_num][1]] = self.local.jsons['jsondata']
                        self.progress.addtext(['下载《' + self.download_json_list[self.local.current_num][2] + '》内容成功', 1], self.current_num[0], threading.current_thread().name)
                        self.current_num[0] += 1
                        break
                    finally:
                        self.time_point_for_iterable_sleep_by_time()
                        self.lock.release()
                else:
                    self.local.k += 1
                    self.time_point_for_iterable_sleep_by_time(1)
                    self.progress.addtext(
                        ['下载《' + self.download_json_list[self.local.current_num][2] + '》内容失败，代码：' + str(self.local.download_info.status_code) + '，尝试次数：' + str(self.local.k), 2],
                        self.current_num[0], threading.current_thread().name)
                    if self.local.k >= 20:
                        self.lock.release()
                        break
                    self.lock.release()
        self.lock.acquire()
        if (self.progress.success[1] == self.progress.maxmax):
            self.file_save(os.path.join('database', 'json_base.json'), json.dumps(self.json_base))
            self.fix_window_with_json_data()
            self.progress.addtext(['下载完毕，已为您下载合成数据，并已保存。您可以关闭本窗口', 0])
        self.lock.release()

    def create_icon_by_local_image(self, image_name):
        return QIcon(os.path.join('material_lib', image_name))

    # 通过技能源的名字，查找所有的引用了这个技能源的技能
    def find_the_ability_by_the_ability_source(self, ability_source):
        rere = []
        for i in self.json_base['技能']:
            if self.json_base['技能'][i]['数据来源'] == ability_source:
                rere.append(i)
        return rere

    def fix_window_with_json_data(self):
        try:
            self.resort()
            names = ['英雄', '非英雄单位', '技能', '技能源', '物品', '单位组', '机制', '机制源']
            p = Pinyin()
            for i in names:
                self.mainlayout['加载信息']['信息'][i].setText('【' + i + '】数据已加载' + str(len(self.json_base[i])) + '个')
                self.mainlayout['列表'][i]['布局']['列表'].setIconSize(QSize(36, 28))
                self.mainlayout['列表'][i]['布局']['列表'].clear()
                for j in self.json_base[i]:
                    temp = QListWidgetItem()
                    pinyin = p.get_pinyin(j)
                    temp.setText('【' + pinyin[:4].lower() + '】' + j)
                    if self.json_base[i][j]['应用'] == 2:
                        temp.setBackground(self.green)
                    elif self.json_base[i][j]['应用'] != 1:
                        temp.setBackground(self.red)
                    image_name = ''
                    if i == '技能源':
                        ability = self.find_the_ability_by_the_ability_source(j)
                        if len(ability) == 0:
                            image_name = 'DOTA2.jpg'
                        elif len(ability) == 1:
                            if '迷你图片' in self.json_base['技能'][ability[0]]:
                                if self.json_base['技能'][ability[0]]['迷你图片'] == 'Talent.png' and self.json_base['技能'][ability[0]]['技能归属'] in self.json_base['英雄']:
                                    image_name = self.json_base['英雄'][self.json_base['技能'][ability[0]]['技能归属']]['迷你图片']
                                else:
                                    image_name = self.json_base['技能'][ability[0]]['迷你图片']
                            else:
                                raise (editerror('技能', ability[0], '没有找到迷你图片'))
                        else:
                            if '迷你图片' in self.json_base['技能'][ability[0]]:
                                if self.json_base['技能'][ability[0]]['迷你图片'] == 'Talent.png':
                                    image_name = 'Talentb.png'
                                else:
                                    image_name = self.json_base['技能'][ability[0]]['迷你图片']
                            else:
                                raise (editerror('技能', ability[0], '没有找到迷你图片'))
                    else:
                        if '迷你图片' in self.json_base[i][j]:
                            if self.json_base[i][j]['迷你图片'] == 'Talent.png':
                                image_name = self.json_base['英雄'][self.json_base[i][j]['技能归属']]['迷你图片']
                            else:
                                image_name = self.json_base[i][j]['迷你图片']
                        else:
                            raise (editerror(i, j, '没有找到迷你图片'))
                    if image_name != '':
                        temp.setIcon(self.create_icon_by_local_image(image_name))
                    self.mainlayout['列表'][i]['布局']['列表'].addItem(temp)
        except editerror as err:
            self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(err.args[0])
            self.edit_category_selected_changed()
            self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(err.args[1])
            self.edit_target_selected_changed()
            QMessageBox.critical(self.parent(), '发现错误', err.get_error_info())

    # 以下是拥有bot权限的用户在开启软件后才能使用的内容

    # 如果开启软件后未登陆，请在登录了有bot（机器人）权限的账户后重启使用
    def check_test(self):
        self.ml['高级功能'] = {0: self.ml[0].addMenu('高级功能')}
        self.ml['高级功能']['更新数据'] = self.ml['高级功能'][0].addAction('更新数据')
        self.ml['高级功能']['更新数据'].triggered.connect(lambda: self.update_json_base())
        self.ml['高级功能']['更新全部《机制》数据'] = self.ml['高级功能'][0].addAction('更新全部【机制】数据')
        self.ml['高级功能']['更新全部《机制》数据'].triggered.connect(lambda: self.update_json_base_mechanism())
        self.ml['高级功能']['上传基础文件'] = self.ml['高级功能'][0].addAction('上传基础文件')
        self.ml['高级功能']['上传基础文件'].triggered.connect(self.upload_basic_json)
        self.ml['高级功能']['上传'] = self.ml['高级功能'][0].addAction('上传')
        self.ml['高级功能']['上传'].triggered.connect(lambda: self.upload_all())
        self.ml['高级功能']['测试窗口'] = self.ml['高级功能'][0].addAction('测试用，看见了不要点，没用')
        self.ml['高级功能']['测试窗口'].triggered.connect(self.test_inputwindow)
        self.ml['高级功能'][0].addSeparator()
        self.ml['高级功能']['上传《英雄》'] = self.ml['高级功能'][0].addAction('上传《英雄》')
        self.ml['高级功能']['上传《英雄》'].triggered.connect(lambda: self.upload_all('英雄'))
        self.ml['高级功能']['上传《物品》'] = self.ml['高级功能'][0].addAction('上传《物品》')
        self.ml['高级功能']['上传《物品》'].triggered.connect(lambda: self.upload_all('物品'))
        self.ml['高级功能']['上传《非英雄单位》'] = self.ml['高级功能'][0].addAction('上传《非英雄单位》')
        self.ml['高级功能']['上传《非英雄单位》'].triggered.connect(lambda: self.upload_all('非英雄单位'))
        self.ml['高级功能']['上传《技能》'] = self.ml['高级功能'][0].addAction('上传《技能》')
        self.ml['高级功能']['上传《技能》'].triggered.connect(lambda: self.upload_all('技能'))
        self.ml['高级功能']['上传《技能源》'] = self.ml['高级功能'][0].addAction('上传《技能源》')
        self.ml['高级功能']['上传《技能源》'].triggered.connect(lambda: self.upload_all('技能源'))
        self.ml['高级功能']['上传《单位组》'] = self.ml['高级功能'][0].addAction('上传《单位组》')
        self.ml['高级功能']['上传《单位组》'].triggered.connect(lambda: self.upload_all('单位组'))
        self.ml['高级功能']['上传《机制》'] = self.ml['高级功能'][0].addAction('上传《机制》')
        self.ml['高级功能']['上传《机制》'].triggered.connect(lambda: self.upload_all('机制'))
        self.ml['高级功能']['上传《机制源》'] = self.ml['高级功能'][0].addAction('上传《机制源》')
        self.ml['高级功能']['上传《机制源》'].triggered.connect(lambda: self.upload_all('机制源'))
        self.ml['高级功能'][0].addSeparator()
        self.ml['高级功能']['上传所有同单位文件'] = self.ml['高级功能'][0].addAction('上传所有同单位文件')
        self.ml['高级功能']['上传所有同单位文件'].triggered.connect(lambda: self.upload_same_kind())
        self.ml['高级功能'][0].addSeparator()
        self.ml['高级功能']['上传统一页面'] = self.ml['高级功能'][0].addAction('上传统一页面')
        self.ml['高级功能']['上传统一页面'].triggered.connect(lambda: self.upload_common_page())
        self.ml['高级功能']['上传《英雄》页面'] = self.ml['高级功能'][0].addAction('上传《英雄》页面')
        self.ml['高级功能']['上传《英雄》页面'].triggered.connect(lambda: self.upload_common_page('英雄'))
        self.ml['高级功能']['上传《非英雄单位》页面'] = self.ml['高级功能'][0].addAction('上传《非英雄单位》页面')
        self.ml['高级功能']['上传《非英雄单位》页面'].triggered.connect(lambda: self.upload_common_page('非英雄单位'))
        self.ml['高级功能']['上传《物品》页面'] = self.ml['高级功能'][0].addAction('上传《物品》页面')
        self.ml['高级功能']['上传《物品》页面'].triggered.connect(lambda: self.upload_common_page('物品'))
        self.ml['高级功能']['上传《技能链接》页面'] = self.ml['高级功能'][0].addAction('上传《技能链接》页面')
        self.ml['高级功能']['上传《技能链接》页面'].triggered.connect(lambda: self.upload_common_page('技能'))
        self.ml['高级功能']['上传《单位组》页面'] = self.ml['高级功能'][0].addAction('上传《单位组》页面')
        self.ml['高级功能']['上传《单位组》页面'].triggered.connect(lambda: self.upload_common_page('单位组'))
        self.ml['高级功能']['上传《机制》页面'] = self.ml['高级功能'][0].addAction('上传《机制》页面')
        self.ml['高级功能']['上传《机制》页面'].triggered.connect(lambda: self.upload_common_page('机制'))
        self.ml['高级功能'][0].addSeparator()
        self.ml['高级功能']['上传HTML数据页面'] = self.ml['高级功能'][0].addAction('上传HTML数据页面')
        self.ml['高级功能']['上传HTML数据页面'].triggered.connect(lambda: self.upload_html_data_page())
        self.ml['高级功能']['完全上传json+page'] = self.ml['高级功能'][0].addAction('完全上传json+page')
        self.ml['高级功能']['完全上传json+page'].triggered.connect(lambda: self.upload_all_json_and_page())
        """
        下载上传的内容
        """
        self.ml['图片处理'] = {0: self.ml[0].addMenu('图片处理')}
        self.ml['图片处理']['下载图片'] = self.ml['图片处理'][0].addAction('下载图片')
        self.ml['图片处理']['下载图片'].triggered.connect(lambda: self.download_images())
        self.ml['图片处理']['下载单个图片'] = self.ml['图片处理'][0].addAction('下载单个图片')
        self.ml['图片处理']['下载单个图片'].triggered.connect(lambda: self.download_one_json_image())

        """
        制作一个默认的单位统称列表，具体效果见edit_json.py
        """
        self.version_default = edit_json.set_version_default(self.json_base)
        """
        下面是修改tab的页面情况
        """
        self.editWidget = QWidget(self)
        self.centralWidget().addTab(self.editWidget, '修改页面')
        self.editlayout = {0: QHBoxLayout()}
        self.editWidget.setLayout(self.editlayout[0])
        self.editlayout['基础数据'] = {0: QGroupBox('基础数据', self)}
        self.editlayout[0].addWidget(self.editlayout['基础数据'][0], 3)
        self.editlayout['基础数据']['竖布局'] = {0: QVBoxLayout()}
        self.editlayout['基础数据'][0].setLayout(self.editlayout['基础数据']['竖布局'][0])
        self.editlayout['基础数据']['竖布局']['树'] = {0: QTreeWidget(self)}
        self.editlayout['基础数据']['竖布局'][0].addWidget(self.editlayout['基础数据']['竖布局']['树'][0])
        self.editlayout['基础数据']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])
        self.editlayout['基础数据']['竖布局']['树'][0].setColumnWidth(0, 300)

        self.editlayout['修改核心'] = {0: QGroupBox('修改核心', self)}
        self.editlayout[0].addWidget(self.editlayout['修改核心'][0], 4)
        self.editlayout['修改核心']['竖布局'] = {0: QVBoxLayout()}
        self.editlayout['修改核心'][0].setLayout(self.editlayout['修改核心']['竖布局'][0])
        self.editlayout['修改核心']['竖布局']['大分类'] = {0: QComboBox(self)}
        self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['大分类'][0])
        self.editlayout['修改核心']['竖布局']['具体库'] = {0: QComboBox(self)}
        self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['具体库'][0])
        self.editlayout['修改核心']['竖布局']['代码库'] = {0: QComboBox(self)}
        self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['代码库'][0])
        self.editlayout['修改核心']['竖布局']['树'] = {0: QTreeWidget(self)}
        self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['树'][0])
        self.editlayout['修改核心']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])

        self.editlayout['竖布局'] = {0: QVBoxLayout()}
        self.editlayout[0].addLayout(self.editlayout['竖布局'][0])
        self.editlayout['竖布局']['新增'] = QPushButton('新增', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['新增'])
        self.editlayout['竖布局']['新增'].clicked.connect(lambda: self.json_edit_new())
        self.editlayout['竖布局']['下载更新'] = QPushButton('下载更新', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['下载更新'])
        self.editlayout['竖布局']['下载更新'].clicked.connect(self.json_edit_download)
        self.editlayout['竖布局']['删除'] = QPushButton('删除', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['删除'])
        self.editlayout['竖布局']['删除'].clicked.connect(self.json_edit_delete)
        self.editlayout['竖布局']['改名'] = QPushButton('改名', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['改名'])
        self.editlayout['竖布局']['改名'].clicked.connect(self.json_edit_change_name)
        self.update_the_jsons_alreadey = False  # 确认是否经过更新数据，以减少所需耗费的时间
        self.editlayout['竖布局']['简单保存'] = QPushButton('简单保存', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['简单保存'])
        self.editlayout['竖布局']['简单保存'].clicked.connect(self.json_edit_save)
        self.editlayout['竖布局']['保存并更新'] = QPushButton('保存并更新', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['保存并更新'])
        self.editlayout['竖布局']['保存并更新'].clicked.connect(self.json_edit_save_and_update)
        self.editlayout['竖布局'][0].addStretch(1)
        self.editlayout['竖布局']['上传同类'] = QPushButton('上传同类', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['上传同类'])
        self.editlayout['竖布局']['上传同类'].clicked.connect(self.upload_same_kind)
        self.editlayout['竖布局'][0].addStretch(1)
        self.editlayout['竖布局']['修改数据'] = QPushButton('修改数据', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['修改数据'])
        self.editlayout['竖布局']['修改数据'].clicked.connect(self.json_edit_change_value)
        self.editlayout['竖布局']['增加列表'] = QPushButton('增加列表', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['增加列表'])
        self.editlayout['竖布局']['增加列表'].clicked.connect(self.json_edit_add_list)
        self.editlayout['竖布局']['向上移动列表'] = QPushButton('向上移动列表', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['向上移动列表'])
        self.editlayout['竖布局']['向上移动列表'].clicked.connect(lambda: self.json_edit_move_list_item(-1))
        self.editlayout['竖布局']['向下移动列表'] = QPushButton('向下移动列表', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['向下移动列表'])
        self.editlayout['竖布局']['向下移动列表'].clicked.connect(lambda: self.json_edit_move_list_item(1))
        self.editlayout['竖布局']['删除列表'] = QPushButton('删除列表', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['删除列表'])
        self.editlayout['竖布局']['删除列表'].clicked.connect(self.json_edit_delete_list)
        self.editlayout['竖布局']['启用条目'] = QPushButton('启用条目', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['启用条目'])
        self.editlayout['竖布局']['启用条目'].clicked.connect(self.json_edit_tree_use_true)
        self.editlayout['竖布局']['禁用条目'] = QPushButton('禁用条目', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['禁用条目'])
        self.editlayout['竖布局']['禁用条目'].clicked.connect(self.json_edit_tree_use_false)
        self.editlayout['竖布局']['增加新次级条目'] = QPushButton('增加新次级条目', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['增加新次级条目'])
        self.editlayout['竖布局']['增加新次级条目'].clicked.connect(self.json_edit_add_new_item)
        self.editlayout['竖布局']['删除该次级条目'] = QPushButton('删除该次级条目', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['删除该次级条目'])
        self.editlayout['竖布局']['删除该次级条目'].clicked.connect(self.json_edit_delete_item)
        self.editlayout['竖布局']['转换为混合文字'] = QPushButton('转换为混合文字', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['转换为混合文字'])
        self.editlayout['竖布局']['转换为混合文字'].clicked.connect(self.json_edit_text_to_combine)
        self.editlayout['竖布局']['转换为普通文字'] = QPushButton('转换为普通文字', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['转换为普通文字'])
        self.editlayout['竖布局']['转换为普通文字'].clicked.connect(self.json_edit_combine_to_text)
        self.editlayout['竖布局'][0].addStretch(1)
        self.editlayout['竖布局']['传统目标设定'] = QPushButton('传统目标设定', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['传统目标设定'])
        self.editlayout['竖布局']['传统目标设定'].clicked.connect(self.json_edit_target_default)
        self.editlayout['竖布局'][0].addStretch(1)
        self.editlayout['竖布局']['软件内更新'] = QPushButton('软件内更新', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['软件内更新'])
        self.editlayout['竖布局']['软件内更新'].clicked.connect(self.json_edit_loop_update)
        self.editlayout['竖布局'][0].addStretch(5)

        self.editlayout['额外机制'] = {0: QGroupBox('额外机制', self)}
        self.editlayout[0].addWidget(self.editlayout['额外机制'][0], 2)
        self.editlayout['额外机制']['竖布局'] = {0: QVBoxLayout()}
        self.editlayout['额外机制'][0].setLayout(self.editlayout['额外机制']['竖布局'][0])
        self.editlayout['额外机制']['竖布局']['关联技能'] = {0: QTreeWidget(self)}
        self.editlayout['额外机制']['竖布局'][0].addWidget(self.editlayout['额外机制']['竖布局']['关联技能'][0])
        self.editlayout['额外机制']['竖布局']['关联技能'][0].setHeaderLabels(['大分类', '名称'])
        self.editlayout['额外机制']['竖布局']['关联技能'][0].setColumnWidth(0, 150)
        self.editlayout['额外机制']['竖布局']['关联技能'][0].expandAll()
        self.editlayout['额外机制']['竖布局']['关联技能'][0].doubleClicked.connect(self.edit_target_selected_quick_changed)
        self.editlayout['额外机制']['竖布局']['树'] = {0: QTreeWidget(self)}
        self.editlayout['额外机制']['竖布局'][0].addWidget(self.editlayout['额外机制']['竖布局']['树'][0])
        self.editlayout['额外机制']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])
        self.dict_to_tree(self.editlayout['额外机制']['竖布局']['树'], self.mech)
        self.editlayout['额外机制']['竖布局']['树'][0].setColumnWidth(0, 150)
        for i in range(self.editlayout['额外机制']['竖布局']['树'][0].topLevelItemCount()):
            self.editlayout['额外机制']['竖布局']['树'][0].topLevelItem(i).setExpanded(True)

        for i in edit_json.edit:
            self.editlayout['修改核心']['竖布局']['大分类'][0].addItem(i)
        self.editlayout['修改核心']['竖布局']['大分类'][0].activated.connect(self.edit_category_selected_changed)
        self.edit_category_selected_changed()
        self.editlayout['修改核心']['竖布局']['具体库'][0].activated.connect(lambda: self.edit_target_selected_changed())
        self.editlayout['修改核心']['竖布局']['代码库'][0].activated.connect(self.edit_text_base_selected_changed)
        self.editlayout['修改核心']['竖布局']['树'][0].clicked.connect(self.tree_item_clicked)
        self.editlayout['修改核心']['竖布局']['树'][0].doubleClicked.connect(self.tree_item_double_clicked)
        self.editlayout['基础数据']['竖布局']['树'][0].doubleClicked.connect(lambda: self.copy_text_from_tree(0))
        self.editlayout['额外机制']['竖布局']['树'][0].doubleClicked.connect(lambda: self.copy_text_from_tree(1))
        self.mainlayout['列表']['英雄']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('英雄'))
        self.mainlayout['列表']['物品']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('物品'))
        self.mainlayout['列表']['非英雄单位']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('非英雄单位'))
        self.mainlayout['列表']['技能']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('技能'))
        self.mainlayout['列表']['技能源']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('技能源'))
        self.mainlayout['列表']['单位组']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('单位组'))
        self.mainlayout['列表']['机制']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('机制'))
        self.mainlayout['列表']['机制源']['布局']['列表'].clicked.connect(lambda: self.choose_mainlayout_change_edit_target('机制源'))
        for i in self.json_base:
            self.mainlayout['列表'][i]['布局']['列表'].doubleClicked.connect(lambda: self.centralWidget().setCurrentIndex(1))
        """
        以下是版本更新的内容
        """
        self.versionWidget = QWidget(self)
        self.centralWidget().addTab(self.versionWidget, '版本更新')
        self.versionlayout = {0: QHBoxLayout()}
        self.versionWidget.setLayout(self.versionlayout[0])
        self.versionlayout['版本列表'] = {0: QGroupBox('版本列表', self)}
        self.versionlayout[0].addWidget(self.versionlayout['版本列表'][0])
        self.versionlayout['版本列表']['横排版'] = {0: QHBoxLayout()}
        self.versionlayout['版本列表'][0].setLayout(self.versionlayout['版本列表']['横排版'][0])
        self.versionlayout['版本列表']['横排版']['列表'] = QTreeWidget(self)
        self.versionlayout['版本列表']['横排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['列表'])
        self.versionlayout['版本列表']['横排版']['列表'].setHeaderLabels(['名称'])
        self.versionlayout['版本列表']['横排版']['竖排版'] = {0: QVBoxLayout()}
        self.versionlayout['版本列表']['横排版'][0].addLayout(self.versionlayout['版本列表']['横排版']['竖排版'][0])
        self.versionlayout['版本列表']['横排版']['竖排版']['下载'] = QPushButton('下载', self)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['下载'])
        self.versionlayout['版本列表']['横排版']['竖排版']['下载'].clicked.connect(self.download_version_list)
        self.versionlayout['版本列表']['横排版']['竖排版']['上传'] = QPushButton('上传', self)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['上传'])
        self.versionlayout['版本列表']['横排版']['竖排版']['上传'].clicked.connect(self.upload_version_list)
        self.versionlayout['版本列表']['横排版']['竖排版']['向上插入新版本'] = QPushButton('向上插入新版本', self)
        self.versionlayout['版本列表']['横排版']['竖排版']['向上插入新版本'].clicked.connect(lambda: self.add_version_list(0))
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['向上插入新版本'])
        self.versionlayout['版本列表']['横排版']['竖排版']['向下插入新版本'] = QPushButton('向下插入新版本', self)
        self.versionlayout['版本列表']['横排版']['竖排版']['向下插入新版本'].clicked.connect(lambda: self.add_version_list(1))
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['向下插入新版本'])
        self.versionlayout['版本列表']['横排版']['竖排版']['插入次级版本'] = QPushButton('插入次级版本', self)
        self.versionlayout['版本列表']['横排版']['竖排版']['插入次级版本'].clicked.connect(self.add_junior_version_list)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['插入次级版本'])
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addStretch(1)
        self.versionlayout['版本列表']['横排版']['竖排版']['下载全部更新内容'] = QPushButton('下载全部更新内容', self)
        self.versionlayout['版本列表']['横排版']['竖排版']['下载全部更新内容'].clicked.connect(self.download_all_versions)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['下载全部更新内容'])
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addStretch(1)
        self.versionlayout['版本列表']['横排版']['竖排版']['软件内更新'] = QPushButton('软件内更新', self)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['软件内更新'])
        self.versionlayout['版本列表']['横排版']['竖排版']['软件内更新'].clicked.connect(self.version_edit_loop_update)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addStretch(1)
        self.versionlayout['版本列表']['横排版']['竖排版']['群体整理后上传'] = QPushButton('群体整理后上传', self)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本列表']['横排版']['竖排版']['群体整理后上传'])
        self.versionlayout['版本列表']['横排版']['竖排版']['群体整理后上传'].clicked.connect(self.update_and_upload_all_version)
        self.versionlayout['版本列表']['横排版']['竖排版'][0].addStretch(5)

        self.versionlayout['版本内容'] = {0: QGroupBox('版本内容', self)}
        self.versionlayout[0].addWidget(self.versionlayout['版本内容'][0], 1)
        self.versionlayout['版本内容']['横排版'] = {0: QHBoxLayout()}
        self.versionlayout['版本内容'][0].setLayout(self.versionlayout['版本内容']['横排版'][0])
        self.versionlayout['版本内容']['横排版']['树'] = {0: QTreeWidget(self)}
        self.versionlayout['版本内容']['横排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['树'][0])
        self.versionlayout['版本内容']['横排版']['树'][0].setHeaderLabels(['名称', '值'])
        self.versionlayout['版本内容']['横排版']['树'][0].setColumnWidth(0, 350)
        self.versionlayout['版本内容']['横排版']['竖排版'] = {0: QVBoxLayout()}
        self.versionlayout['版本内容']['横排版'][0].addLayout(self.versionlayout['版本内容']['横排版']['竖排版'][0])
        self.versionlayout['版本内容']['横排版']['竖排版']['新建'] = QPushButton('新建', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['新建'])
        self.versionlayout['版本内容']['横排版']['竖排版']['新建'].clicked.connect(self.create_one_version)
        self.versionlayout['版本内容']['横排版']['竖排版']['下载'] = QPushButton('下载', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['下载'])
        self.versionlayout['版本内容']['横排版']['竖排版']['下载'].clicked.connect(self.download_one_version)
        self.versionlayout['版本内容']['横排版']['竖排版']['保存'] = QPushButton('保存', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['保存'])
        self.versionlayout['版本内容']['横排版']['竖排版']['保存'].clicked.connect(self.save_one_version)
        self.versionlayout['版本内容']['横排版']['竖排版']['保存并上传'] = QPushButton('保存并上传', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['保存并上传'])
        self.versionlayout['版本内容']['横排版']['竖排版']['保存并上传'].clicked.connect(lambda: self.upload_one_version(True))
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addStretch(1)
        self.versionlayout['版本内容']['横排版']['竖排版']['修改内容'] = QPushButton('修改内容', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['修改内容'])
        self.versionlayout['版本内容']['横排版']['竖排版']['修改内容'].clicked.connect(self.version_edit_change_value)
        self.versionlayout['版本内容']['横排版']['竖排版']['大分类'] = QPushButton('大分类', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['大分类'])
        self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].clicked.connect(self.version_button_tree1)
        self.versionlayout['版本内容']['横排版']['竖排版']['加中标题'] = QPushButton('加中标题', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['加中标题'])
        self.versionlayout['版本内容']['横排版']['竖排版']['加中标题'].clicked.connect(self.version_button_tree1_add_tree2)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除中标题'] = QPushButton('删除中标题', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['删除中标题'])
        self.versionlayout['版本内容']['横排版']['竖排版']['删除中标题'].clicked.connect(self.version_button_delete_tree_item)
        self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'] = QPushButton('加小分类', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'])
        self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].clicked.connect(self.version_button_tree2_add_tree3)
        self.versionlayout['版本内容']['横排版']['竖排版']['标题分类改名'] = QPushButton('标题分类改名', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['标题分类改名'])
        self.versionlayout['版本内容']['横排版']['竖排版']['标题分类改名'].clicked.connect(self.version_button_tree2_change_name)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'] = QPushButton('删除小分类', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'])
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'].clicked.connect(self.version_button_delete_tree_item)
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'] = QPushButton('加一条新条目', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'])
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'].clicked.connect(self.version_button_tree3_add_tree_list)
        self.versionlayout['版本内容']['横排版']['竖排版']['向上移动题目'] = QPushButton('向上移动题目', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['向上移动题目'])
        self.versionlayout['版本内容']['横排版']['竖排版']['向上移动题目'].clicked.connect(lambda: self.version_button_move_list_item(-1))
        self.versionlayout['版本内容']['横排版']['竖排版']['向下移动题目'] = QPushButton('向下移动题目', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['向下移动题目'])
        self.versionlayout['版本内容']['横排版']['竖排版']['向下移动题目'].clicked.connect(lambda: self.version_button_move_list_item(1))
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该条目'] = QPushButton('删除该条目', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['删除该条目'])
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该条目'].clicked.connect(self.version_button_delete_tree_item)
        self.versionlayout['版本内容']['横排版']['竖排版']['增加新目标'] = QPushButton('增加新目标', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['增加新目标'])
        self.versionlayout['版本内容']['横排版']['竖排版']['增加新目标'].clicked.connect(self.version_button_list_add_list_text)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该目标'] = QPushButton('删除该目标', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['删除该目标'])
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该目标'].clicked.connect(self.version_button_delete_tree_item)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addStretch(5)

        self.check_version()
        self.versionlayout['版本列表']['横排版']['列表'].clicked.connect(self.check_version_content)
        self.versionlayout['版本内容']['横排版']['树'][0].clicked.connect(self.version_edit_all_button_clicked)
        self.version_edit_all_button_default()
        self.versionlayout['版本内容']['横排版']['树'][0].doubleClicked.connect(self.version_item_double_clicked)
        """
        记录曾用名和链接，以及对应页面名+图片的内容
        """

        self.nameWidget = QWidget(self)
        self.centralWidget().addTab(self.nameWidget, '曾用名')
        self.namelayout = {0: QHBoxLayout()}
        self.nameWidget.setLayout(self.namelayout[0])

        self.namelayout['按钮区域'] = {0: QVBoxLayout(self)}
        self.namelayout[0].addLayout(self.namelayout['按钮区域'][0])
        self.namelayout['按钮区域']['下载'] = QPushButton('下载', self)
        self.namelayout['按钮区域'][0].addWidget(self.namelayout['按钮区域']['下载'])
        self.namelayout['按钮区域']['下载'].clicked.connect(self.download_name_base)
        self.namelayout['按钮区域']['保存'] = QPushButton('保存', self)
        self.namelayout['按钮区域'][0].addWidget(self.namelayout['按钮区域']['保存'])
        self.namelayout['按钮区域']['保存'].clicked.connect(self.name_save_name_json)
        self.namelayout['按钮区域']['保存并上传'] = QPushButton('保存并上传', self)
        self.namelayout['按钮区域'][0].addWidget(self.namelayout['按钮区域']['保存并上传'])
        self.namelayout['按钮区域']['保存并上传'].clicked.connect(self.name_save_and_upload_name_json)
        self.namelayout['按钮区域'][0].addStretch(1)
        self.namelayout['按钮区域']['删除该条目'] = QPushButton('删除该条目', self)
        self.namelayout['按钮区域'][0].addWidget(self.namelayout['按钮区域']['删除该条目'])
        self.namelayout['按钮区域']['删除该条目'].clicked.connect(self.name_delete_one_old_name)
        self.namelayout['按钮区域']['删除该条目'].setEnabled(False)
        self.namelayout['按钮区域'][0].addStretch(1)

        self.namelayout['历史曾用名'] = {0: QGroupBox('历史曾用名', self)}
        self.namelayout[0].addWidget(self.namelayout['历史曾用名'][0], 3)
        self.namelayout['历史曾用名']['布局'] = {0: QGridLayout(self)}
        self.namelayout['历史曾用名'][0].setLayout(self.namelayout['历史曾用名']['布局'][0])
        self.namelayout['历史曾用名']['布局']['树'] = {0: QTreeWidget(self)}
        self.namelayout['历史曾用名']['布局'][0].addWidget(self.namelayout['历史曾用名']['布局']['树'][0])
        self.namelayout['历史曾用名']['布局']['树'][0].setHeaderLabels(['名称', '指向页面'])
        self.namelayout['历史曾用名']['布局']['树'][0].setColumnWidth(0, 150)
        self.namelayout['历史曾用名']['布局']['树'][0].clicked.connect(self.name_history_names_tree_widget_clicked)

        self.namelayout['编辑区'] = {0: QGroupBox('编辑区', self)}
        self.namelayout[0].addWidget(self.namelayout['编辑区'][0], 3)
        self.namelayout['编辑区']['布局'] = {0: QVBoxLayout(self)}
        self.namelayout['编辑区'][0].setLayout(self.namelayout['编辑区']['布局'][0])
        self.namelayout['编辑区']['布局']['新建对照'] = {0: QGroupBox('新建对照', self)}
        self.namelayout['编辑区']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['新建对照'][0])
        self.namelayout['编辑区']['布局']['新建对照']['布局'] = {0: QGridLayout(self)}
        self.namelayout['编辑区']['布局']['新建对照'][0].setLayout(self.namelayout['编辑区']['布局']['新建对照']['布局'][0])
        self.namelayout['编辑区']['布局']['新建对照']['布局']['名称'] = QLabel('名称', self)
        self.namelayout['编辑区']['布局']['新建对照']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['新建对照']['布局']['名称'], 0, 0)
        self.namelayout['编辑区']['布局']['新建对照']['布局']['名称输入'] = QLineEdit(self)
        self.namelayout['编辑区']['布局']['新建对照']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['新建对照']['布局']['名称输入'], 0, 1, 1, 3)
        self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面'] = QLabel('指向页面', self)
        self.namelayout['编辑区']['布局']['新建对照']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面'], 1, 0)
        self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面输入'] = QLineEdit(self)
        self.namelayout['编辑区']['布局']['新建对照']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面输入'], 1, 1, 1, 3)
        self.namelayout['编辑区']['布局']['新建对照']['布局']['确认保存'] = QPushButton('确认保存', self)
        self.namelayout['编辑区']['布局']['新建对照']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['新建对照']['布局']['确认保存'], 2, 0)
        self.namelayout['编辑区']['布局']['新建对照']['布局']['确认保存'].clicked.connect(self.name_create_new_name_save)
        self.namelayout['编辑区']['布局']['新建对照']['布局']['重置'] = QPushButton('重置', self)
        self.namelayout['编辑区']['布局']['新建对照']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['新建对照']['布局']['重置'], 2, 2)
        self.namelayout['编辑区']['布局']['新建对照']['布局']['重置'].clicked.connect(self.name_create_new_name_reset)

        self.namelayout['编辑区']['布局']['现存修正'] = {0: QGroupBox('现存修正', self)}
        self.namelayout['编辑区']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['现存修正'][0])
        self.namelayout['编辑区']['布局']['现存修正']['布局'] = {0: QGridLayout(self)}
        self.namelayout['编辑区']['布局']['现存修正'][0].setLayout(self.namelayout['编辑区']['布局']['现存修正']['布局'][0])
        self.namelayout['编辑区']['布局']['现存修正']['布局']['名称'] = QLabel('名称', self)
        self.namelayout['编辑区']['布局']['现存修正']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['现存修正']['布局']['名称'], 0, 0)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['名称输入'] = QLineEdit(self)
        self.namelayout['编辑区']['布局']['现存修正']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['现存修正']['布局']['名称输入'], 0, 1, 1, 3)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['名称输入'].setFocusPolicy(Qt.NoFocus)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['指向页面'] = QLabel('指向页面', self)
        self.namelayout['编辑区']['布局']['现存修正']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['现存修正']['布局']['指向页面'], 1, 0)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['指向页面输入'] = QLineEdit(self)
        self.namelayout['编辑区']['布局']['现存修正']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['现存修正']['布局']['指向页面输入'], 1, 1, 1, 3)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['确认保存'] = QPushButton('确认保存', self)
        self.namelayout['编辑区']['布局']['现存修正']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['现存修正']['布局']['确认保存'], 2, 0)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['确认保存'].setEnabled(False)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['确认保存'].clicked.connect(self.name_change_old_name_save)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['重置'] = QPushButton('重置', self)
        self.namelayout['编辑区']['布局']['现存修正']['布局'][0].addWidget(self.namelayout['编辑区']['布局']['现存修正']['布局']['重置'], 2, 2)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['重置'].setEnabled(False)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['重置'].clicked.connect(self.name_change_old_name_reset)

        self.namelayout['原生页面'] = {0: QGroupBox('原生页面', self)}
        self.namelayout[0].addWidget(self.namelayout['原生页面'][0], 2)
        self.namelayout['原生页面']['布局'] = {0: QGridLayout(self)}
        self.namelayout['原生页面'][0].setLayout(self.namelayout['原生页面']['布局'][0])
        self.namelayout['原生页面']['布局']['树'] = {0: QTreeWidget(self)}
        self.namelayout['原生页面']['布局'][0].addWidget(self.namelayout['原生页面']['布局']['树'][0])
        self.namelayout['原生页面']['布局']['树'][0].setHeaderLabels(['名称页面'])
        self.namelayout['原生页面']['布局']['树'][0].setColumnWidth(0, 200)
        self.namelayout['原生页面']['布局']['树'][0].clicked.connect(self.name_origin_names_tree_widget_clicked)

        self.namelayout['衍生页面'] = {0: QGroupBox('衍生页面', self)}
        self.namelayout[0].addWidget(self.namelayout['衍生页面'][0], 3)
        self.namelayout['衍生页面']['布局'] = {0: QGridLayout(self)}
        self.namelayout['衍生页面'][0].setLayout(self.namelayout['衍生页面']['布局'][0])
        self.namelayout['衍生页面']['布局']['树'] = {0: QTreeWidget(self)}
        self.namelayout['衍生页面']['布局'][0].addWidget(self.namelayout['衍生页面']['布局']['树'][0])
        self.namelayout['衍生页面']['布局']['树'][0].setHeaderLabels(['名称', '指向页面'])
        self.namelayout['衍生页面']['布局']['树'][0].setColumnWidth(0, 200)
        """"""
        self.name_initial_name_base()
        """
        记录一些便捷词条，包括但不限于生成链接、简易的描述性信息
        """
        self.entryWidget = QWidget(self)
        self.centralWidget().addTab(self.entryWidget, '词汇注释')
        self.entrylayout = {0: QHBoxLayout()}
        self.entryWidget.setLayout(self.entrylayout[0])

        self.entrylayout['按钮区域'] = {0: QVBoxLayout(self)}
        self.entrylayout[0].addLayout(self.entrylayout['按钮区域'][0])
        self.entrylayout['按钮区域']['下载'] = QPushButton('下载', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['下载'])
        self.entrylayout['按钮区域']['下载'].clicked.connect(self.download_entry_base)
        self.entrylayout['按钮区域']['保存'] = QPushButton('保存', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['保存'])
        self.entrylayout['按钮区域']['保存'].clicked.connect(self.entry_save_entry_json)
        self.entrylayout['按钮区域']['保存并上传'] = QPushButton('保存并上传', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['保存并上传'])
        self.entrylayout['按钮区域']['保存并上传'].clicked.connect(self.entry_save_and_upload_entry_json)
        self.entrylayout['按钮区域'][0].addStretch(1)
        self.entrylayout['按钮区域']['新增'] = QPushButton('新增', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['新增'])
        self.entrylayout['按钮区域']['新增'].clicked.connect(lambda: self.entry_edit_new())
        self.entrylayout['按钮区域']['删除'] = QPushButton('删除', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['删除'])
        self.entrylayout['按钮区域']['删除'].clicked.connect(lambda: self.entry_edit_delete())
        self.entrylayout['按钮区域'][0].addStretch(1)
        self.entrylayout['按钮区域']['增加条目'] = QPushButton('增加条目', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['增加条目'])
        self.entrylayout['按钮区域']['增加条目'].clicked.connect(lambda: self.entry_edit_change_value())
        self.entrylayout['按钮区域']['改名'] = QPushButton('改名', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['改名'])
        self.entrylayout['按钮区域']['改名'].clicked.connect(lambda: self.entry_edit_change_name())
        self.entrylayout['按钮区域']['修改值'] = QPushButton('修改值', self)
        self.entrylayout['按钮区域'][0].addWidget(self.entrylayout['按钮区域']['修改值'])
        self.entrylayout['按钮区域']['修改值'].clicked.connect(lambda: self.entry_edit_change_value())
        self.entrylayout['按钮区域'][0].addStretch(1)

        self.entrylayout['编辑区'] = {0: QVBoxLayout()}
        self.entrylayout[0].addLayout(self.entrylayout['编辑区'][0])
        self.entrylayout['编辑区']['树'] = {0: QTreeWidget(self)}
        self.entrylayout['编辑区'][0].addWidget(self.entrylayout['编辑区']['树'][0])
        self.entrylayout['编辑区']['树'][0].setHeaderLabels(['名称', '值'])
        self.entrylayout['编辑区']['树'][0].setColumnWidth(0, 300)
        self.entrylayout['编辑区']['树'][0].doubleClicked.connect(lambda: self.entry_edit_change_value())
        self.entrylayout['编辑区']['树'][0].keyPressEvent = self.entry_key_function

        self.entry_refresh_tree()
        """
        下面是重新排序的情况
        """
        self.resort()

    def resort(self):
        for i in self.text_base:
            self.text_base[i] = edit_json.sortedDictValues(self.text_base[i], False)
        for i in self.json_base:
            self.json_base[i] = edit_json.sortedDictValues(self.json_base[i], True)
            self.json_name[i] = edit_json.sortedList(self.json_name[i])
        self.version_base = edit_json.version_sort(self.version_base, self.version_list['版本'])
        self.file_save_all()

    def file_save_all(self):
        self.file_save(os.path.join('database', 'text_base.json'), json.dumps(self.text_base))
        self.file_save(os.path.join('database', 'json_base.json'), json.dumps(self.json_base))
        self.file_save(os.path.join('database', 'json_name.json'), json.dumps(self.json_name))
        self.file_save(os.path.join('database', 'name_base.json'), json.dumps(self.name_base))

    def update_json_base(self, info="更新数据成功！\n您可以选择上传这些数据。"):
        try:
            time_show = time.time()
            self.upgrade_base = {}
            name_dict_list = self.name_create_tree_list_name()
            reversed_name_dict_list = self.reversed_name_create_tree_list_name()

            hero.fulfill_hero_json(self.text_base, self.json_base["英雄"], self.version, reversed_name_dict_list)
            item.fulfill_item_json(self.text_base, self.json_base["物品"], self.version, reversed_name_dict_list)

            ability.fulfill_vpk_data(self.json_base, self.text_base)
            info += ability.autoget_talent_source(self.json_base, self.text_base['英雄'])
            ability.get_source_to_data(self.json_base, self.upgrade_base, self.version, reversed_name_dict_list)  # 花费时间过久16s+
            unit.fulfill_unit_json(self.text_base, self.json_base["非英雄单位"], self.version, reversed_name_dict_list)

            self.file_save(os.path.join('database', 'temp_json_base.json'), json.dumps(self.json_base['技能']))
            with open(os.path.join('database', 'temp_json_base.json'), mode="r", encoding="utf-8") as f:
                self.json_base['技能'] = json.loads(f.read())
            os.remove(os.path.join('database', 'temp_json_base.json'))

            ability.input_upgrade(self.json_base, self.upgrade_base)

            unit.complete_upgrade(self.json_base["非英雄单位"], self.text_base)
            ability.complete_upgrade(self.json_base["技能"], self.json_base["机制"], self.text_base)

            ability.complete_mech(self.json_base["技能"], self.mech)
            # 将图片信息规范化
            for i in self.json_base:
                for j in self.json_base[i]:
                    if '图片' in self.json_base[i][j] and len(self.json_base[i][j]['图片']) > 1:
                        self.json_base[i][j]['图片'] = self.json_base[i][j]['图片'][0].upper() + self.json_base[i][j]['图片'][1:].replace(' ', '_')
                    if '迷你图片' in self.json_base[i][j] and len(self.json_base[i][j]['迷你图片']) > 1:
                        self.json_base[i][j]['迷你图片'] = self.json_base[i][j]['迷你图片'][0].upper() + self.json_base[i][j]['迷你图片'][1:].replace(' ', '_')
            # 结算技能和技能源问题

            for i in self.json_base["技能"]:
                target = ['技能源']
                if '数据来源' in self.json_base["技能"][i] and self.json_base["技能"][i]['数据来源'] in self.json_base["技能源"]:
                    target.append(self.json_base["技能"][i]['数据来源'])
                else:
                    raise (editerror('技能', i, "你没有书写数据来源，请立刻书写"))
                if self.json_base["技能"][i]['应用'] >= 0:
                    ability.loop_check(self.json_base["技能"][i], self.text_base, self.json_base, i, target, self.change_all_template_link_to_html)  # 花费时间过久9s+

            ability.confirm_upgrade_info(self.json_base['技能'])

            for i in ['物品','技能','非英雄单位','单位组']:
                self.loop_check_to_html(self.json_base[i],self.change_all_template_link_to_html)
            # 增加拥有技能

            ability_own = {}
            for i in self.json_base["技能"]:
                if self.json_base["技能"][i]['技能归属'] in ability_own:
                    ability_own[self.json_base["技能"][i]['技能归属']].append([self.json_base["技能"][i]['页面名'], self.json_base["技能"][i]['技能排序']])
                else:
                    ability_own[self.json_base["技能"][i]['技能归属']] = [[self.json_base["技能"][i]['页面名'], self.json_base["技能"][i]['技能排序']]]
            for i in ability_own:
                ability_own[i].sort(key=lambda x: x[1])
            for i in ['英雄', '非英雄单位', '物品']:
                for j in self.json_base[i]:
                    self.json_base[i][j]['技能'] = []
                    if self.json_base[i][j]['页面名'] in ability_own:
                        for k in ability_own[self.json_base[i][j]['页面名']]:
                            if self.json_base[i][j]['应用'] == self.json_base["技能"][k[0]]['应用']:
                                self.json_base[i][j]['技能'].append(k[0])
            unit_own = {}
            for i in self.json_base['非英雄单位']:
                for j in self.json_base['非英雄单位'][i]['源技能']:
                    w = self.json_base['非英雄单位'][i]['源技能'][j].lstrip('#')
                    if w not in unit_own:
                        unit_own[w] = []
                    unit_own[w].append(i)
            for i in self.json_base['技能']:
                if i in unit_own:
                    self.json_base['技能'][i]['技能召唤物'] = unit_own[i]
                else:
                    self.json_base['技能'][i]['技能召唤物'] = []

            hero.fulfil_complex_and_simple_show(self.json_base, self.change_all_template_link_to_html)
            item.fulfil_complex_and_simple_show(self.json_base, self.change_all_template_link_to_html)
            unit.fulfil_complex_and_simple_show(self.json_base, self.change_all_template_link_to_html)
            ability.fulfil_complex_and_simple_show(self.json_base, self.change_all_template_link_to_html)
            hero.fulfil_talent_show(self.json_base, self.change_all_template_link_to_html)

            mechnism.fulfil_labels(self.json_base)

            # 生成单位组信息（怀疑是个时间耗费大户）
            unitgroup.get_source_to_data(self.json_base, self.version, self.text_base, reversed_name_dict_list)
            # self.resort() #这里不resort了就是因为太消耗时间了，而且实际帮助已经不大了
            self.file_save_all()
        except editerror as err:
            self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(err.args[0])
            self.edit_category_selected_changed()
            self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(err.args[1])
            self.edit_target_selected_changed()
            QMessageBox.critical(self.parent(), '发现错误', err.get_error_info())
            return True
        else:
            QMessageBox.information(self, "已完成", info + '\n总耗时：' + str(round(time.time() - time_show, 2)) + '秒')
            return False

    def loop_check_to_html(self,json,function):
        for i in json:
            if isinstance(json[i],dict):
                self.loop_check_to_html(json[i],function)
            elif isinstance(json[i],str):
                json[i]=function(json[i])

    def update_json_base_mechanism(self, target=''):
        try:
            time_show = time.time()
            allupdate = []
            loop_time = 1
            if target == '':
                loop_time = 2
                for i in self.json_base['机制']:
                    if i not in allupdate:
                        allupdate.append(i)
                for i in self.json_base['机制源']:
                    if i not in allupdate:
                        allupdate.append(i)
                self.w = upload_text('开始更新机制')
                self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
                self.w.setWindowIcon(self.icon)
                QApplication.processEvents()
                total_num = len(allupdate) * 2
                self.w.confirm_numbers(total_num)
                self.w.setWindowTitle('机制一共有' + str(total_num) + '个，1~' + str(len(allupdate)) + '，' + str(len(allupdate) + 1) + '~' + str(total_num) + '。')
                reversed_name_dict_list = self.reversed_name_create_tree_list_name()
                mechnism.get_source_to_data(self.json_base, allupdate, self.version, self.text_base, reversed_name_dict_list, self.change_all_template_link_to_html, loop_time, self.w)
                self.loop_check_to_html(self.json_base['机制'], self.change_all_template_link_to_html)
            else:
                allupdate.append(target)
                reversed_name_dict_list = self.reversed_name_create_tree_list_name()
                mechnism.get_source_to_data(self.json_base, allupdate, self.version, self.text_base, reversed_name_dict_list, self.change_all_template_link_to_html, loop_time)
                self.loop_check_to_html(self.json_base['机制'][target], self.change_all_template_link_to_html)
            self.file_save_all()
        except editerror as err:
            self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(err.args[0])
            self.edit_category_selected_changed()
            self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(err.args[1])
            self.edit_target_selected_changed()
            QMessageBox.critical(self.parent(), '发现错误', err.get_error_info())
            return True
        else:
            QMessageBox.information(self, "已完成", '目标【机制】都已经更新完毕\n总耗时：' + str(round(time.time() - time_show, 2)) + '秒')
            return False

    def upload_basic_json(self):
        self.upload_json('text_base.json', self.text_base)
        self.upload_json('json_name.json', self.json_name)
        self.upload_json('图片链接.json', self.name_create_tree_list_name())
        QMessageBox.information(self, "上传完成", '已经上传完毕基础文件')

    def upload_all(self, chosen=''):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json中……')
        QApplication.processEvents()
        all_upload = []
        all_upload.append(['版本.json', {'版本': self.version}])
        if chosen == '':
            for i in self.json_base:
                for j in self.json_base[i]:
                    if i[-1] == '源':
                        all_upload.append([j + '/源.json', self.json_base[i][j]])
                    else:
                        all_upload.append([j + '.json', self.json_base[i][j]])
        else:
            i = chosen
            for j in self.json_base[i]:
                if i[-1] == '源':
                    all_upload.append([j + '/源.json', self.json_base[i][j]])
                else:
                    all_upload.append([j + '.json', self.json_base[i][j]])
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(total_num):
            self.w.addtext(self.upload_json(all_upload[i][0], all_upload[i][1]), i)
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def upload_common_page(self, chosen=''):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传统一制作页面中……')
        self.w.add_info_text('正在分析数据中……')
        QApplication.processEvents()
        all_upload = []
        all_copy_upload = []
        all_redirect = []
        if chosen == '' or chosen == '英雄':
            for i in self.json_base['英雄']:
                all_upload.append([i, common_page.create_page_hero(self.json_base, self.version_base, self.version_list['版本'], i)])
                all_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['英雄'][i], self.json_base), 0)])
            self.w.add_info_text('【英雄】页面已经分析完毕！')
            QApplication.processEvents()
        if chosen == '' or chosen == '非英雄单位':
            for i in self.json_base['非英雄单位']:
                all_upload.append([i, common_page.create_page_unit(self.json_base, self.version_base, self.version_list['版本'], i)])
                all_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['非英雄单位'][i], self.json_base), 0)])
            self.w.add_info_text('【非英雄单位】页面已经分析完毕！')
            QApplication.processEvents()
        if chosen == '' or chosen == '物品':
            for i in self.json_base['物品']:
                all_upload.append([i, common_page.create_page_item(self.json_base, self.version_base, self.version_list['版本'], i)])
                all_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['物品'][i], self.json_base), 0)])
            self.w.add_info_text('【物品】页面已经分析完毕！')
            QApplication.processEvents()
        if chosen == '' or chosen == '单位组':
            for i in self.json_base['单位组']:
                all_upload.append([i, common_page.create_page_unitgroup(self.json_base, self.version_base, self.version_list['版本'], i)])
                all_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['单位组'][i], self.json_base), 0)])
            self.w.add_info_text('【单位组】页面已经分析完毕！')
            QApplication.processEvents()
        if chosen == '技能':
            for i in self.json_base['技能']:
                if self.json_base['技能'][i]['应用'] == 0:
                    all_upload.append([i, common_page.create_page_old_ability(self.json_base, self.version_base, self.version_list['版本'], i)])
                else:
                    page_link_content = '#重定向[[' + self.json_base['技能'][i]['技能归属'] + '#' + i + ']]'
                    all_redirect.append([i, page_link_content])
            self.w.add_info_text('【技能】页面已经分析完毕！')
            QApplication.processEvents()
        if chosen == '' or chosen == '机制':
            for i in self.json_base['机制']:
                if self.json_base['机制'][i]['次级分类'] == '引用机制':
                    all_copy_upload.append([i, common_page.create_page_mechnism(self.json_base, self.version_base, self.version_list['版本'], i)])
                else:
                    all_upload.append([i, common_page.create_page_mechnism(self.json_base, self.version_base, self.version_list['版本'], i)])
                    all_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['机制'][i], self.json_base), 0)])
            self.w.add_info_text('【机制】页面已经分析完毕！')
            QApplication.processEvents()
        self.w.add_info_text('所有页面已经分析完毕！现在开始上传全部内容…………')
        QApplication.processEvents()
        total_num = len(all_upload) + len(all_copy_upload) + len(all_redirect)
        self.w.confirm_numbers(total_num)
        self.w.setWindowTitle('一共需要上传共计' + str(total_num) + '个页面，其中：普通页面' + str(len(all_upload)) + '个（1~' + str(len(all_upload)) + '），'
                              + '引用机制页面' + str(len(all_copy_upload)) + '个（' + str(1 + len(all_upload)) + '~' + str(len(all_upload) + len(all_copy_upload)) + '），'
                              + '重定向页面' + str(len(all_redirect)) + '个（' + str(1 + len(all_upload) + len(all_copy_upload)) + '~' + str(total_num) + '）')
        for i in range(len(all_upload)):
            self.w.addtext(self.upload_page(all_upload[i][0], all_upload[i][1]), i)
            QApplication.processEvents()
        for i in range(len(all_copy_upload)):
            self.w.addtext(self.upload_page(all_copy_upload[i][0], all_copy_upload[i][1], 2), i + len(all_upload))
            QApplication.processEvents()
        for i in range(len(all_redirect)):
            self.w.addtext(self.upload_page(all_redirect[i][0], all_redirect[i][1], 0), i + len(all_upload) + len(all_copy_upload))
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def upload_html_data_page(self, chosen=''):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传统一制作页面中……')
        QApplication.processEvents()
        all_upload = []
        if chosen == '' or chosen == '英雄':
            all_upload.append(['英雄数据', self.change_all_template_link_to_html(hero.create_html_data_page(self.json_base))])
        if chosen == '' or chosen == '物品':
            all_upload.append(['物品数据', self.change_all_template_link_to_html(item.create_html_data_page(self.json_base))])
        # if chosen == '' or chosen == '全数据':
        #     all_upload.append(['数据库数据', self.create_all_json_data()])
        #     print(len(all_upload[-1][1]))
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(len(all_upload)):
            self.w.addtext(self.upload_html(all_upload[i][0], all_upload[i][1]), i)
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def create_all_json_data(self):
        retxt = '<script>\ndota_json_json_data={'
        for i in self.json_base['英雄']:
            retxt += '\n"' + i + '":{"简易展示":"' + self.json_base['英雄'][i]['简易展示'] + '",'
            retxt = retxt.rstrip(',') + '},'
        for i in self.json_base['非英雄单位']:
            retxt += '\n"' + i + '":{"简易展示":"' + self.json_base['非英雄单位'][i]['简易展示'] + '",'
            retxt = retxt.rstrip(',') + '},'
        for i in self.json_base['物品']:
            retxt += '\n"' + i + '":{"简易展示":"' + self.json_base['物品'][i]['简易展示'] + '",'
            retxt = retxt.rstrip(',') + '},'
        retxt = retxt.rstrip(',') + '};\n</script>'
        return retxt

    def upload_all_json_and_page(self):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json+page中……')
        self.w.add_info_text('正在分析数据中……')
        QApplication.processEvents()
        all_json_upload = []
        all_page_upload = []
        all_copy_upload = []
        all_redirect = []
        all_json_upload.append(['版本.json', {'版本': self.version}])
        for i in self.json_base:
            for j in self.json_base[i]:
                if i[-1] == '源':
                    all_json_upload.append([j + '/源.json', self.json_base[i][j]])
                else:
                    all_json_upload.append([j + '.json', self.json_base[i][j]])
        self.w.add_info_text('【json】部分已经生成完毕！')
        QApplication.processEvents()
        for i in self.json_base['英雄']:
            all_page_upload.append([i, common_page.create_page_hero(self.json_base, self.version_base, self.version_list['版本'], i)])
            all_page_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['英雄'][i], self.json_base), 0)])
        self.w.add_info_text('【英雄】页面已经分析完毕！')
        QApplication.processEvents()
        for i in self.json_base['非英雄单位']:
            all_page_upload.append([i, common_page.create_page_unit(self.json_base, self.version_base, self.version_list['版本'], i)])
            all_page_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['非英雄单位'][i], self.json_base), 0)])
        self.w.add_info_text('【非英雄单位】页面已经分析完毕！')
        QApplication.processEvents()
        for i in self.json_base['物品']:
            all_page_upload.append([i, common_page.create_page_item(self.json_base, self.version_base, self.version_list['版本'], i)])
            all_page_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['物品'][i], self.json_base), 0)])
        self.w.add_info_text('【物品】页面已经分析完毕！')
        QApplication.processEvents()
        for i in self.json_base['单位组']:
            all_page_upload.append([i, common_page.create_page_unitgroup(self.json_base, self.version_base, self.version_list['版本'], i)])
            all_page_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['单位组'][i], self.json_base), 0)])
        self.w.add_info_text('【单位组】页面已经分析完毕！')
        QApplication.processEvents()
        for i in self.json_base['技能']:
            if self.json_base['技能'][i]['应用'] == 0:
                all_page_upload.append([i, common_page.create_page_old_ability(self.json_base, self.version_base, self.version_list['版本'], i)])
            else:
                page_link_content = '#重定向[[' + self.json_base['技能'][i]['技能归属'] + '#' + i + ']]'
                all_redirect.append([i, page_link_content])
        self.w.add_info_text('【技能】页面已经分析完毕！')
        QApplication.processEvents()
        for i in self.json_base['机制']:
            if self.json_base['机制'][i]['次级分类'] == '引用机制':
                all_copy_upload.append([i, common_page.create_page_mechnism(self.json_base, self.version_base, self.version_list['版本'], i)])
            else:
                all_page_upload.append([i, common_page.create_page_mechnism(self.json_base, self.version_base, self.version_list['版本'], i)])
                all_page_upload.append([i + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'], common_page.all_the_names(self.json_base['机制'][i], self.json_base), 0)])
        self.w.add_info_text('【机制】页面已经分析完毕！')
        QApplication.processEvents()
        self.w.add_info_text('所有页面已经分析完毕！现在开始上传全部内容…………')
        QApplication.processEvents()
        total_num = len(all_json_upload) + len(all_page_upload) + len(all_copy_upload) + len(all_redirect)
        self.w.confirm_numbers(total_num)
        self.w.setWindowTitle('一共需要上传共计' + str(total_num) + '个页面，其中：json页面' + str(len(all_json_upload)) + '个（1~' + str(len(all_json_upload)) + '），'
                              + '普通页面' + str(len(all_page_upload)) + '个（' + str(1 + len(all_json_upload)) + '~' + str(len(all_json_upload) + len(all_page_upload)) + '），'
                              + '引用机制页面' + str(len(all_copy_upload)) + '个（' + str(1 + len(all_json_upload) + len(all_page_upload)) + '~' + str(len(all_json_upload) + len(all_page_upload) + len(all_copy_upload)) + '），'
                              + '重定向页面' + str(len(all_redirect)) + '个（' + str(1 + len(all_json_upload) + len(all_page_upload) + len(all_copy_upload)) + '~' + str(total_num) + '）')
        QApplication.processEvents()
        for i in range(len(all_json_upload)):
            self.w.addtext(self.upload_json(all_json_upload[i][0], all_json_upload[i][1]), i)
            QApplication.processEvents()
        for i in range(len(all_page_upload)):
            self.w.addtext(self.upload_page(all_page_upload[i][0], all_page_upload[i][1]), i + len(all_json_upload))
            QApplication.processEvents()
        for i in range(len(all_copy_upload)):
            self.w.addtext(self.upload_page(all_copy_upload[i][0], all_copy_upload[i][1], 2), i + len(all_json_upload) + len(all_page_upload))
            QApplication.processEvents()
        for i in range(len(all_redirect)):
            self.w.addtext(self.upload_page(all_redirect[i][0], all_redirect[i][1], 0), i + len(all_json_upload) + len(all_page_upload) + len(all_copy_upload))
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def get_the_wiki_image_with_hashmd5(self, image_name):
        hashmd5 = hashlib.md5(image_name.encode("utf-8")).hexdigest()
        return '/'.join([self.image_url, hashmd5[0], hashmd5[0:2], image_name])

    def download_one_image(self, image_name):
        k = 0
        while True:
            self.time_point_for_iterable_sleep_by_time()
            download_info = self.seesion.get(self.get_the_wiki_image_with_hashmd5(image_name))
            if download_info.status_code < 400:
                with open(os.path.join('material_lib', image_name), "wb") as f:
                    f.write(download_info.content)
                return ['《' + image_name + '》下载成功！', 1]
            elif download_info.status_code == 404:
                return ['《' + image_name + '》名称有误，下载失败！', 0]
            else:
                k += 1
                if k >= 5:
                    return ['《' + image_name + '》下载失败！错误原因为' + download_info.reason, 0]

    def download_one_json_image(self):
        self.w = upload_text('开始下载图片')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6,
                           self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('下载图片中……')
        QApplication.processEvents()
        s1 = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        s2 = self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()
        all_upload = []
        if '图片' in self.json_base[s1][s2] and self.json_base[s1][s2]['图片'] != '' and self.json_base[s1][s2]['图片'] not in all_upload:
            all_upload.append(self.json_base[s1][s2]['图片'])
        if '迷你图片' in self.json_base[s1][s2] and self.json_base[s1][s2]['迷你图片'] != '' and self.json_base[s1][s2]['迷你图片'] not in all_upload:
            all_upload.append(self.json_base[s1][s2]['迷你图片'])
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(total_num):
            self.w.addtext(self.download_one_image(all_upload[i]), i)
            QApplication.processEvents()
        QMessageBox.information(self.w, '下载完毕', "您已下载完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def download_images(self, chosen=''):
        self.w = upload_text('开始下载图片')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6,
                           self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('下载图片中……')
        QApplication.processEvents()
        all_upload = []
        all_upload.append('Talentb.png')
        if chosen in self.json_base:
            for i in self.json_base[chosen]:
                if '图片' in self.json_base[chosen][i] and self.json_base[chosen][i]['图片'] != '' and self.json_base[chosen][i]['图片'] not in all_upload:
                    all_upload.append(self.json_base[chosen][i]['图片'])
                if '迷你图片' in self.json_base[chosen][i] and self.json_base[chosen][i]['迷你图片'] != '' and self.json_base[chosen][i]['迷你图片'] not in all_upload:
                    all_upload.append(self.json_base[chosen][i]['迷你图片'])
        else:
            for i in self.json_base:
                for j in self.json_base[i]:
                    if '图片' in self.json_base[i][j] and self.json_base[i][j]['图片'] != '' and self.json_base[i][j]['图片'] not in all_upload:
                        all_upload.append(self.json_base[i][j]['图片'])
                    if '迷你图片' in self.json_base[i][j] and self.json_base[i][j]['迷你图片'] != '' and self.json_base[i][j]['迷你图片'] not in all_upload:
                        all_upload.append(self.json_base[i][j]['迷你图片'])
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(total_num):
            self.w.addtext(self.download_one_image(all_upload[i]), i)
            QApplication.processEvents()
        QMessageBox.information(self.w, '下载完毕', "您已下载完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def upload_same_kind(self):
        selected = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        selected_name = self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()
        if not self.update_the_jsons_alreadey:
            error_stop = True
            self.json_base[selected][selected_name] = {}
            self.read_tree_to_json(self.editlayout['修改核心']['竖布局']['树'][0], self.json_base[selected][selected_name])
            self.file_save_all()
            if selected[:2] == '机制':
                error_stop = self.update_json_base_mechanism(selected_name)
            else:
                error_stop = self.update_json_base(info='已经保存并更新完毕\n请记得上传。')
            if error_stop:
                return None
            else:
                self.update_the_jsons_alreadey = True
        target_name = []
        if self.json_base[selected][selected_name]['应用'] > 0:
            if selected == '技能':
                target_name.append(self.json_base[selected][selected_name]['技能归属'])
            elif selected == '技能源':
                skill_name = selected_name
                for i in self.json_base['技能']:
                    if self.json_base['技能'][i]['数据来源'] == skill_name:
                        target_name.append(self.json_base['技能'][i]['技能归属'])
            else:
                target_name.append(selected_name)
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6,
                           self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json中……')
        QApplication.processEvents()
        all_upload = []
        all_page = []
        all_redirect = []
        all_copy_page = []
        if len(target_name) == 0:
            if selected[-1] == '源':
                all_upload.append([selected_name + '/源.json', self.json_base[selected][selected_name]])
            else:
                all_upload.append([selected_name + '.json', self.json_base[selected][selected_name]])
        else:
            for k in target_name:
                for i in self.json_base['技能']:
                    if self.json_base['技能'][i]['技能归属'] == k:
                        all_upload.append([i + '.json', self.json_base['技能'][i]])
                        if self.json_base['技能'][i]['应用'] == 0:
                            all_page.append([i, common_page.create_page_old_ability(self.json_base, self.version_base, self.version_list['版本'], i)])
                        else:
                            all_redirect.append([i, '#重定向[[' + k + '#' + i + ']]'])
                        j = self.json_base['技能'][i]['数据来源']
                        if j in self.json_base['技能源']:
                            all_upload.append([j + '/源.json', self.json_base['技能源'][j]])
                if k in self.json_base['英雄']:
                    all_upload.append([k + '.json', self.json_base['英雄'][k]])
                    all_page.append([k, common_page.create_page_hero(self.json_base, self.version_base, self.version_list['版本'], k)])
                    all_page.append([k + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'],
                                                                                common_page.all_the_names(self.json_base['英雄'][k], self.json_base), 0)])
                elif k in self.json_base['物品']:
                    all_upload.append([k + '.json', self.json_base['物品'][k]])
                    all_page.append([k, common_page.create_page_item(self.json_base, self.version_base, self.version_list['版本'], k)])
                    all_page.append([k + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'],
                                                                                common_page.all_the_names(self.json_base['物品'][k], self.json_base), 0)])
                elif k in self.json_base['非英雄单位']:
                    all_upload.append([k + '.json', self.json_base['非英雄单位'][k]])
                    all_page.append([k, common_page.create_page_unit(self.json_base, self.version_base, self.version_list['版本'], k)])
                    all_page.append([k + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'],
                                                                                common_page.all_the_names(self.json_base['非英雄单位'][k], self.json_base), 0)])
                if k in self.json_base['机制源']:
                    all_upload.append([k + '/源.json', self.json_base['机制源'][k]])
                if k in self.json_base['机制']:
                    all_upload.append([k + '.json', self.json_base['机制'][k]])
                    if self.json_base['机制'][k]['次级分类'] == '引用机制':
                        all_copy_page.append([k, common_page.create_page_mechnism(self.json_base, self.version_base, self.version_list['版本'], k)])
                    else:
                        all_page.append([k, common_page.create_page_mechnism(self.json_base, self.version_base, self.version_list['版本'], k)])
                        all_page.append([k + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'],
                                                                                    common_page.all_the_names(self.json_base['机制'][k], self.json_base), 0)])
                if k in self.json_base['单位组']:
                    all_upload.append([k + '.json', self.json_base['单位组'][k]])
                    all_page.append([k, common_page.create_page_unitgroup(self.json_base, self.version_base, self.version_list['版本'], k)])
                    all_page.append([k + '/版本改动', common_page.create_switch_log(self.version_base, self.version_list['版本'],
                                                                                common_page.all_the_names(self.json_base['单位组'][k], self.json_base), 0)])
        total_num = len(all_upload) + len(all_page) + len(all_copy_page) + len(all_redirect)
        self.w.confirm_numbers(total_num)
        for i in range(len(all_upload)):
            self.w.addtext(self.upload_json(all_upload[i][0], all_upload[i][1]), i)
            QApplication.processEvents()
        for i in range(len(all_page)):
            self.w.addtext(self.upload_page(all_page[i][0], all_page[i][1]), i + len(all_upload))
            QApplication.processEvents()
        for i in range(len(all_copy_page)):
            self.w.addtext(self.upload_page(all_copy_page[i][0], all_copy_page[i][1], 2), i + len(all_upload) + len(all_page))
            QApplication.processEvents()
        for i in range(len(all_redirect)):
            self.w.addtext(self.upload_page(all_redirect[i][0], all_redirect[i][1], 0), i + len(all_upload) + len(all_page) + len(all_copy_page))
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def upload_json_1(self, pagename, content):
        return ['暂时不予以上传', 1]

    # 向wiki网站上传对应的信息
    def upload_json(self, pagename, content):
        download_data = {'action': 'jsondata', 'title': pagename, 'format': 'json'}
        k = 0
        while True:
            self.time_point_for_iterable_sleep_by_time()
            download_info = self.seesion.post(self.target_url, headers=self.header, data=download_data)
            if download_info.status_code < 400:
                download_content = download_info.json()
                if 'jsondata' in download_content and download_content['jsondata'] == content:
                    return ['《' + pagename + '》通过校验，不需要修改！', 0]
                break
            else:
                k += 1
                self.time_point_for_iterable_sleep_by_time()
                if k >= 5:
                    break
        pagename = 'Data:' + pagename
        content = json.dumps(content)
        upload_data = {'action': 'edit', 'title': pagename, 'text': content, 'format': 'json', 'token': self.csrf_token}
        k = 0
        while True:
            self.time_point_for_iterable_sleep_by_time()
            upload_info = self.seesion.post(self.target_url, headers=self.header, data=upload_data)
            if upload_info.status_code < 400:
                upload_info_json = upload_info.json()
                break
            else:
                k += 1
                if k >= 10:
                    return ['《' + pagename + '》上传失败，请之后重新上传！上传代码：' + str(upload_info.status_code), 0]
        if 'edit' in upload_info_json and upload_info_json['edit']['result'] == 'Success':
            if 'nochange' in upload_info.json()['edit']:
                return ['没有修改《' + pagename + '》', 0]
            elif 'oldrevid' in upload_info.json()['edit']:
                return ['上传《' + pagename + '》，【' + str(upload_info.json()['edit']['oldrevid']) + '】-->【' + str(
                    upload_info.json()['edit']['newrevid']) + '】', 1]
            else:
                return ['上传《' + pagename + '》内容成功', 1]
        else:
            return [json.dumps(upload_info.json()), 0]

    def upload_page(self, pagename, content, template=1):
        download_data = {'action': 'parse', 'prop': 'wikitext', 'page': pagename, 'format': 'json'}
        # 这里会对文字进行一个提纯操作
        if template == 1:
            upcontent = self.change_all_template_link_to_html(content) + '\n{{全部格式}}'
        elif template == 2:
            upcontent = self.change_all_template_link_to_html(content)
        else:
            upcontent = content
        # 本地处理好后再进行上传
        k = 0
        while True:
            self.time_point_for_iterable_sleep_by_time()
            download_info = self.seesion.post(self.target_url, headers=self.header, data=download_data)
            if download_info.status_code < 400:
                download_content = download_info.json()
                if 'error' in download_content:
                    break
                elif upcontent == download_content['parse']['wikitext']['*']:
                    upload_data = {'action': 'purge', 'titles': pagename, 'format': 'json'}
                    l = 0
                    while True:
                        self.time_point_for_iterable_sleep_by_time()
                        upload_info = self.seesion.post(self.target_url, headers=self.header, data=upload_data)
                        if upload_info.status_code < 400:
                            return ['《' + pagename + '》没有进行任何操作，并且刷新缓存完毕！', 0]
                        else:
                            k += 1
                            if k >= 10:
                                return ['《' + pagename + '》刷新缓存失败，该页面没有进行任何操作！', 0]
                break
            else:
                k += 1
                if k >= 5:
                    break
        upload_data = {'action': 'edit', 'title': pagename, 'text': upcontent, 'format': 'json', 'token': self.csrf_token}
        while True:
            self.time_point_for_iterable_sleep_by_time()
            upload_info = self.seesion.post(self.target_url, headers=self.header, data=upload_data)
            if upload_info.status_code < 400:
                upload_info_json = upload_info.json()
                break
            else:
                k += 1
                if k >= 10:
                    return ['《' + pagename + '》上传失败，请之后重新上传！', 0]
        if 'edit' in upload_info_json and upload_info_json['edit']['result'] == 'Success':
            if 'nochange' in upload_info.json()['edit']:
                return ['没有修改《' + pagename + '》', 0]
            elif 'oldrevid' in upload_info.json()['edit']:
                return ['上传《' + pagename + '》，【' + str(upload_info.json()['edit']['oldrevid']) + '】-->【' + str(
                    upload_info.json()['edit']['newrevid']) + '】', 1]
            else:
                return ['上传《' + pagename + '》内容成功', 1]
        else:
            return [json.dumps(upload_info.json()), 0]

    def upload_html(self, pagename, content):
        upcontent = content
        pagename = 'html:' + pagename
        # 本地处理好后再进行上传
        upload_data = {'action': 'edit', 'title': pagename, 'text': upcontent, 'format': 'json', 'token': self.csrf_token}
        k = 0
        while True:
            self.time_point_for_iterable_sleep_by_time()
            upload_info = self.seesion.post(self.target_url, headers=self.header, data=upload_data)
            if upload_info.status_code < 400:
                upload_info_json = upload_info.json()
                break
            else:
                k += 1
                if k >= 10:
                    return ['《' + pagename + '》上传失败，请之后重新上传！', 0]
        if 'edit' in upload_info_json and upload_info_json['edit']['result'] == 'Success':
            if 'nochange' in upload_info.json()['edit']:
                return ['没有修改《' + pagename + '》', 0]
            elif 'oldrevid' in upload_info.json()['edit']:
                return ['上传《' + pagename + '》，【' + str(upload_info.json()['edit']['oldrevid']) + '】-->【' + str(
                    upload_info.json()['edit']['newrevid']) + '】', 1]
            else:
                return ['上传《' + pagename + '》内容成功', 1]
        else:
            return [json.dumps(upload_info.json()), 0]

    def change_all_template_link_to_html(self, gettxt):
        retxt = gettxt
        findlen = 0
        findnow = 0
        while True:
            findnow = '+'.join(re.findall(r'\{\{([^\{\}]*?)\}\}', retxt))
            if findnow == findlen:
                break
            else:
                findlen = findnow
            retxt = re.sub(r'\{\{([^\{\}]*?)\}\}', lambda x: self.upload_text_template(x), retxt)
        retxt = re.sub(r'\[\[((?!#)[^:]*?)\]\]', lambda x: self.upload_text_link(x), retxt)
        return retxt

    def upload_text_link(self, x):
        retxt = ''
        link = x.group(1).split('|')
        if '#' in link[0]:
            link_index = link[0].index('#') + 1
            link_hex = link[0][link_index:].encode('utf-8')
            link_target = ''
            for i in link_hex:
                link_target += '.' + self.change_256hex_to_str(i)
            real_link = link[0][:link_index] + link_target
        else:
            real_link = link[0]
        if len(link) > 1:
            retxt = '<span class="dota_create_link_to_wiki_page" data-link-page-name="' + real_link + '">' + link[1] + '</span>'
        else:
            retxt = '<span class="dota_create_link_to_wiki_page" data-link-page-name="' + real_link + '">' + link[0] + '</span>'
        return retxt

    def upload_text_template(self, x):
        retxt = ''
        template_args = x.group(1).split('|')
        if template_args[0] in ['H', 'A', 'I', 'h', 'a', 'i']:
            size = ''
            pic_style = ''
            if template_args[1] == '魔晶升级' or template_args[1] == '魔晶技能':
                template_args.insert(2, 'w24')
            for i in range(2, len(template_args)):
                if template_args[i][0] == 'w':
                    size = ' data-image-width="' + template_args[i][1:] + '"'
                elif template_args[i][0] == 'h':
                    size = ' data-image-height="' + template_args[i][1:] + '"'
            if len(template_args[1]) > 2 and template_args[1][-2:] == '天赋':
                pic_style = ''
            elif template_args[0] in ['A', 'a']:
                pic_style += ' data-image-class="ability_icon"'
            elif template_args[0] in ['I', 'i']:
                pic_style += ' data-image-class="item_icon"'
            retxt += '<span class="dota_get_image_by_json_name" data-json-name="' + template_args[1] + '" data-image-mini="1" ' + ' data-image-link="1" data-text-link="1"' + size + pic_style + '></span>'
        elif template_args[0] in ['E', 'e']:
            if template_args[1] in self.entry_base:
                retxt += '<span class="dota_create_link_to_wiki_page" data-link-page-name="' + self.entry_base[template_args[1]]['链接'] + '">' + template_args[1] + '</span>'
            else:
                retxt += '<span class="dota_create_link_to_wiki_page" data-link-page-name="' + template_args[1] + '">' + template_args[1] + '</span>'
        elif template_args[0].lower() in ['b', 'buff']:
            if len(template_args) < 3:
                retxt = '{{错误文字|调用buff应使用2个参数，而您只输入了' + str(len(template_args) - 1) + '个参数}}'
            else:
                if template_args[1] in self.json_base['技能']:
                    v = self.json_base['技能'][template_args[1]]['效果']
                    w = ''
                    tip=True
                    for i in range(3, len(template_args)):
                        if template_args[i] == 'tip':
                            tip=False
                    if template_args[2] in v:
                        w = v[template_args[2]]
                    else:
                        for j in v:
                            if template_args[2]==v[template_args[2]]['名称']:
                                w = v[template_args[2]]
                    if w != '':
                        if tip:
                            retxt += '{{额外信息框|<span class="border_3d_out" style="background-color:#fff">' + w['名称'] + '</span>|'+ability.create_upgrade_buff(w)+'}}'
                        else:
                            retxt+='<span class="" style="border-style:outset;background-color:#fff">' + w['名称'] + '</span>'
                    else:
                        retxt = '{{错误文字|未在《'+template_args[1]+'》中找到对应“'+template_args[2]+'”的buff}}'
        elif '图片' in template_args[0]:
            size = ''
            center = ''
            link = ''
            image_class = ''
            if template_args[1].lower() == 'shard.png':
                template_args.insert(2, 'w24')
            for i in range(2, len(template_args)):
                if template_args[i] == 'left':
                    center = ' data-image-center="left"'
                elif template_args[i] == 'right':
                    center = ' data-image-center="right"'
                elif template_args[i] == 'center':
                    center = ' data-image-center="center"'
                elif template_args[i][0] == 'w':
                    size = ' data-image-width="' + template_args[i][1:] + '"'
                elif template_args[i][0] == 'h':
                    size = ' data-image-height="' + template_args[i][1:] + '"'
                elif template_args[i][:5] == 'link=':
                    link = ' data-image-link="' + template_args[i][5:] + '"'
                elif template_args[i][:5] == 'text=':
                    image_class = ' data-text-link="' + template_args[i][5:] + '"'
                elif template_args[i][:6] == 'class=':
                    image_class = ' data-image-class="' + template_args[i][6:] + '"'
            if template_args[0] == '图片':
                retxt = '<span class="dota_get_image_by_image_name" data-image-name="' + template_args[1] + '"' + size + center + link + image_class + '></span>'
            elif template_args[0] == '大图片':
                retxt = '<span class="dota_get_image_by_json_name" data-json-name="' + template_args[1] + '"' + size + center + link + image_class + '></span>'
            elif template_args[0] == '小图片':
                retxt = '<span class="dota_get_image_by_json_name" data-json-name="' + template_args[1] + '"' + size + center + link + image_class + ' data-image-mini="1"></span>'
        elif template_args[0] in ['et', 'ET', '词汇']:
            if template_args[1] in self.entry_base:
                if len(template_args) > 2 and template_args[2] in self.entry_base[template_args[1]]:
                    retxt += self.entry_base[template_args[1]][template_args[2]]
                else:
                    retxt += self.entry_base[template_args[1]]['文字']
            else:
                retxt += '{{错误文字|错误的词汇名称：' + template_args[1] + '}}'
        elif template_args[0] == 'symbol':
            retxt += '{{图片|' + template_args[1] + '.png'
            if template_args[1] == 'shard':
                retxt += '|w24'
            retxt += '}}'
        elif template_args[0] == '额外信息框':
            retxt += '<span class="dota_click_absolute_additional_infomation_frame">' \
                     + '<span class="dota_click_absolute_additional_infomation_frame_button">' + template_args[1] + '</span>' \
                     + '<span class="dota_click_absolute_additional_infomation_frame_frame">' + template_args[2] + '</span></span> '
        elif template_args[0] == '点击复制':
            td = ''
            if template_args[-1][:3] == 'td=':
                td = ' data-text-decoration="' + template_args[-1][3:] + '"'
                template_args.pop()
            if len(template_args) > 2:
                retxt = '<span class="dota_click_copy_text_html" data-click-copy-text="' + template_args[2] + '"' + td + '>' + template_args[1] + '</span>'
            else:
                retxt = '<span class="dota_click_copy_text_html" data-click-copy-text="' + template_args[1] + '"' + td + '>' + template_args[1] + '</span>'
        elif template_args[0] == '链接':
            if len(template_args) > 2:
                retxt = '<span class="dota_create_link_to_wiki_page" data-link-page-name="' + template_args[1] + '">' + template_args[2] + '</span>'
            else:
                retxt = '<span class="dota_create_link_to_wiki_page" data-link-page-name="' + template_args[1] + '">' + template_args[1] + '</span>'
        elif template_args[0] == '错误文字':
            retxt += '<span class="error_text">' + template_args[1] + '</span>'
        elif template_args[0] == '分类查询':
            post = ''
            dict = ''
            delete = True
            should_be_delete = []
            for i in range(2, len(template_args)):
                if template_args[i][:5] == 'post=':
                    post = template_args[i][5:]
                    should_be_delete.insert(0, i)
                if template_args[i][:5] == 'dict=':
                    dict = template_args[i][5:]
                    should_be_delete.insert(0, i)
                if template_args[i] == 'delete':
                    delete = False
                    should_be_delete.insert(0, i)
            for i in should_be_delete:
                template_args.pop(i)
            if template_args[1] == '英雄':
                retxt = common_page.create_hero_choose_element(self.json_base, template_args[2:], dict, post)
            elif template_args[1] == '物品':
                if delete:
                    retxt = common_page.create_item_choose_element(self.json_base, template_args[2:], dict, post)
                else:
                    retxt = common_page.create_delete_item_choose_element(self.json_base, template_args[2:], post)
            elif template_args[1] == '中立物品':
                if delete:
                    retxt = common_page.create_neutral_item_choose_element(self.json_base, template_args[2:], dict, post)
                else:
                    retxt = common_page.create_delete_neutral_item_choose_element(self.json_base, template_args[2:], post)
        elif template_args[0] == '机制内容':
            if len(template_args) < 4:
                if template_args[1] in self.json_base['机制']:
                    if template_args[2] in self.json_base['机制'][template_args[1]]['内容']:
                        if template_args[3] in self.json_base['机制'][template_args[1]]['内容'][template_args[2]]['内容']:
                            retxt += self.json_base['机制'][template_args[1]]['内容'][template_args[2]]['内容'][template_args[3]]['内容']
                        else:
                            retxt += '{{错误文字|《{{H|' + template_args[1] + '}}》标题下《' + template_args[2] + '》错误标识：' + template_args[3] + '}}'
                    else:
                        retxt += '{{错误文字|《{{H|' + template_args[1] + '}}》错误标题：' + template_args[2] + '}}'
                else:
                    retxt += '{{错误文字|错误机制名：' + template_args[1] + '}}'
            else:
                retxt += '{{错误文字|《机制内容》需要输入3个参数，而您只输入了' + str(len(template_args) - 1) + '个参数}}'
        elif template_args[0] == '翻译':
            lang = ''
            aclass = ''
            for i in range(2, len(template_args)):
                if template_args[i][:5] == 'lang=':
                    lang = template_args[i][5:]
                if template_args[i][:6] == 'style=':
                    if template_args[i][6:] == 'warning':
                        aclass += ' bgc_warning'
            if template_args[1] in self.text_base['翻译']:
                if lang == '':
                    retxt += '<span class="dota_self_switch_content_by_click">'
                    for i in self.text_base['翻译'][template_args[1]]:
                        v = self.text_base['翻译'][template_args[1]][i]
                        retxt += '<span class="dota_self_switch_content_by_click_content' + aclass + '">' + v + '</span>'
                    retxt += '</span>'
                else:
                    if lang in self.text_base['翻译'][template_args[1]]:
                        v = self.text_base['翻译'][template_args[1]][lang]
                        retxt += '<span class="' + aclass + '">' + v + '</span>'
                    else:
                        retxt = '{{错误文字|您输入的代码“' + template_args[1] + '”没有“' + lang + '”语言信息，请检查后重新输入}}'
            else:
                retxt = '{{错误文字|您输入的代码“' + template_args[1] + '”有误，请检查后重新输入}}'
        elif template_args[0] == '游戏报错':
            retxt = '{{翻译'
            for i in range(1, len(template_args)):
                retxt += '|' + template_args[i]
            retxt += '|style=warning}}'
        else:
            return x.group(0)
        return retxt

    def change_256hex_to_str(self, num):
        retxt = ''
        temp = num // 16
        num -= temp * 16
        if temp < 10:
            retxt += chr(48 + temp)
        else:
            retxt += chr(55 + temp)
        if num < 10:
            retxt += chr(48 + num)
        else:
            retxt += chr(55 + num)
        return retxt

    def check_dict_equal(self, d1, d2):
        bool = True
        temp = {}
        temp.update(d1)
        temp.update(d2)
        for i in temp:
            if i in d1 and i in d2:
                if type(d1[i]) == type(d2[i]):
                    if isinstance(d1[i], dict):
                        bool = bool and self.check_dict_equal(d1[i], d2[i])
                    elif isinstance(d1[i], list):
                        bool = bool and self.check_list_equal(d1[i], d2[i])
                    else:
                        bool = bool and d1[i] == d2[i]
                else:
                    if (isinstance(d1[i], int) or isinstance(d1[i], float)) and (
                            isinstance(d2[i], int) or isinstance(d2[i], float)):
                        if float(d1[i]) == float(d2[i]):
                            continue
                        else:
                            bool = False
            else:
                bool = False
            if not bool:
                break
        temp2 = {}
        temp2.update(d2)
        temp2.update(d1)
        for i in temp2:
            if i in d1 and i in d2:
                if type(d1[i]) == type(d2[i]):
                    if isinstance(d1[i], dict):
                        bool = bool and self.check_dict_equal(d1[i], d2[i])
                    elif isinstance(d1[i], list):
                        bool = bool and self.check_list_equal(d1[i], d2[i])
                    else:
                        bool = bool and d1[i] == d2[i]
                else:
                    if (isinstance(d1[i], int) or isinstance(d1[i], float)) and (
                            isinstance(d2[i], int) or isinstance(d2[i], float)):
                        if float(d1[i]) == float(d2[i]):
                            continue
                        else:
                            bool = False
            else:
                bool = False
            if not bool:
                break
        return bool

    def check_list_equal(self, d1, d2):
        bool = True
        for i in range(max(len(d1), len(d2))):
            if i < len(d1) and i < len(d2):
                if type(d1[i]) == type(d2[i]):
                    if isinstance(d1[i], dict):
                        bool = bool and self.check_dict_equal(d1[i], d2[i])
                    elif isinstance(d1[i], list):
                        bool = bool and self.check_list_equal(d1[i], d2[i])
                    else:
                        bool = bool and d1[i] == d2[i]
                else:
                    if isinstance(d1[i], int) or isinstance(d1[i], float) and isinstance(d2[i], int) or isinstance(
                            d2[i], float):
                        if float(d1[i]) == float(d2[i]):
                            continue
                        else:
                            bool = False
            else:
                bool = False
            if not bool:
                break
        return bool

    def dict_to_tree(self, tdict, jdict):
        for j in jdict:
            i = str(j)
            if isinstance(jdict[i], dict):
                tdict[i] = {0: QTreeWidgetItem(tdict[0])}
                tdict[i][0].setText(0, str(i))
                self.dict_to_tree(tdict[i], jdict[i])
            else:
                tdict[i] = QTreeWidgetItem(tdict[0])
                tdict[i].setText(0, str(i))
                tdict[i].setText(1, str(jdict[i]))

    def edit_category_selected_changed(self):
        selected = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        if selected not in self.json_name:
            self.json_name[selected] = []
            self.json_base[selected] = {}
        if len(self.json_name[selected]) == 0:
            self.json_edit_new()
        else:
            selected_name = self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()
            selected_bool = False
            alike_name = ''
            self.editlayout['修改核心']['竖布局']['具体库'][0].clear()
            self.editlayout['修改核心']['竖布局']['代码库'][0].clear()
            for i in self.json_base[selected]:
                self.editlayout['修改核心']['竖布局']['具体库'][0].addItem(i)
                if selected_name != '':
                    if not selected_bool and selected_name == i:
                        selected_bool = True
                    if alike_name == '' and selected_name[0] == i[0]:
                        alike_name = i
            if len(edit_json.edit_source[selected]) > 0:
                for i in self.text_base[edit_json.edit_source[selected][0]]:
                    self.editlayout['修改核心']['竖布局']['代码库'][0].addItem(i)
                QApplication.processEvents()
            if not selected_bool and alike_name != '':
                selected_name = alike_name
            self.edit_target_selected_changed(selected_name)

    def edit_target_selected_changed(self, target_name=''):
        if target_name != '':
            self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(target_name)
        selected = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(),
                    self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
        if len(edit_json.edit_source[selected[0]]) > 0:
            if selected[0] == '非英雄单位':
                target = self.json_base[selected[0]][selected[1]]['代码名']["1"]
            elif selected[0] == '技能源':
                target = self.json_base[selected[0]][selected[1]]['代码']
            else:
                target = self.json_base[selected[0]][selected[1]]['代码名']
            if target in self.text_base[edit_json.edit_source[selected[0]][0]]:
                self.editlayout['修改核心']['竖布局']['代码库'][0].setCurrentText(target)
                self.edit_text_base_selected_changed()
            else:
                for i in self.text_base:
                    if target in self.text_base[i]:
                        self.edit_text_base_selected_changed("", i, target)
        QApplication.processEvents()
        self.editlayout['修改核心']['竖布局']['树'][0].clear()
        self.editlayout['修改核心']['竖布局']['树'] = {0: self.editlayout['修改核心']['竖布局']['树'][0]}
        self.editlayout['修改核心']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])
        self.editlayout['修改核心']['竖布局']['树'][0].setColumnWidth(0, 300)
        self.complex_dict_to_tree(self.editlayout['修改核心']['竖布局']['树'], edit_json.edit[selected[0]], self.json_base[selected[0]][selected[1]])
        if selected[0] == '物品':
            self.item_dict_to_extra_tree(self.editlayout['修改核心']['竖布局']['树'], self.json_base[selected[0]][selected[1]])
        self.edit_json_expand_all()
        self.self_edit_button_default()
        self.edit_target_selected_changed_quick_link_tree()

    def edit_target_selected_changed_quick_link_tree(self):
        selected = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        selected_name = self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()
        target_name = []
        if selected == '技能':
            if len(self.json_base[selected][selected_name]['技能归属']) > 0:
                target_name.append(self.json_base[selected][selected_name]['技能归属'])
        elif selected == '技能源':
            skill_name = selected_name
            for i in self.json_base['技能']:
                if self.json_base['技能'][i]['数据来源'] == skill_name:
                    target_name.append(self.json_base['技能'][i]['技能归属'])
            for i, v in self.json_base['非英雄单位'].items():
                for j in v['源技能']:
                    w = v['源技能'][j]
                    if w == selected_name:
                        target_name.append(i)
        elif selected == '非英雄单位':
            target_name.append(selected_name)
            for i in self.json_base['非英雄单位'][selected_name]['源技能']:
                v = self.json_base['非英雄单位'][selected_name]['源技能'][i]
                if v in self.json_base['技能']:
                    if len(self.json_base['技能'][v]['技能归属']) > 0:
                        target_name.append(self.json_base['技能'][v]['技能归属'])
            for i, v in self.json_base['单位组'].items():
                if selected_name in v['全部单位']:
                    target_name.append(i)
        elif selected == '单位组':
            target_name.append(selected_name)
            if '全部单位' in self.json_base['单位组'][selected_name]:
                for i in self.json_base['单位组'][selected_name]['全部单位']:
                    target_name.append(i)
        else:
            target_name.append(selected_name)
        if len(target_name) > 0:
            self.editlayout['额外机制']['竖布局']['关联技能'][0].clear()
            for k in target_name:
                new0 = QTreeWidgetItem(self.editlayout['额外机制']['竖布局']['关联技能'][0])
                new0.setText(0, k)
                for l in ['英雄', '非英雄单位', '物品', '机制', '机制源', '单位组']:
                    if k in self.json_base[l]:
                        new1 = QTreeWidgetItem(new0)
                        new1.setText(0, l)
                        new1.setText(1, k)
                for i in self.json_base['技能']:
                    if self.json_base['技能'][i]['技能归属'] == k:
                        new2 = QTreeWidgetItem(new0)
                        new2.setText(0, '技能')
                        new2.setText(1, i)
                        j = self.json_base['技能'][i]['数据来源']
                        if j in self.json_base['技能源']:
                            new3 = QTreeWidgetItem(new0)
                            new3.setText(0, '技能源')
                            new3.setText(1, j)
            self.editlayout['额外机制']['竖布局']['关联技能'][0].expandAll()

    def edit_target_selected_quick_changed(self):
        selected = self.editlayout['额外机制']['竖布局']['关联技能'][0].currentItem()
        text0 = selected.text(0)
        text1 = selected.text(1)
        if text0 in self.json_base and text1 in self.json_base[text0]:
            self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(text0)
            self.edit_category_selected_changed()
            self.edit_target_selected_changed(text1)

    def choose_mainlayout_change_edit_target(self, target_base=''):
        self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(target_base)
        self.edit_category_selected_changed()
        ind = self.mainlayout['列表'][target_base]['布局']['列表'].currentItem().text().index('】')
        target_name = self.mainlayout['列表'][target_base]['布局']['列表'].currentItem().text()[ind + 1:]
        self.edit_target_selected_changed(target_name)

    def complex_dict_to_tree(self, tdict, edict, sdict):
        for i in edict:
            if i != 'list':
                if i in sdict:
                    if edict[i][0] == 'tree':
                        tdict[i] = {0: TreeItemEdit(tdict[0], i)}
                        tdict[i][0].set_type(edict[i][0])
                        self.complex_dict_to_tree(tdict[i], edict[i][1], sdict[i])
                        if len(edict[i]) > 2 and edict[i][2]:
                            tdict[i][0].setBackground(1, self.green)
                        tdict[i][0].setExpanded(True)
                    elif edict[i][0] == 'number' or edict[i][0] == 'int':
                        tdict[i] = TreeItemEdit(tdict[0], i)
                        tdict[i].set_type(edict[i][0])
                        tdict[i].set_value(sdict[i])
                    elif edict[i][0] == 'text':
                        if isinstance(sdict[i], dict) and '混合文字' in sdict[i]:
                            tdict[i] = {0: TreeItemEdit(tdict[0], i)}
                            tdict[i][0].set_type('text')
                            self.combine_text_to_tree(tdict[i], sdict[i])
                        else:
                            tdict[i] = TreeItemEdit(tdict[0], i)
                            tdict[i].set_type(edict[i][0])
                            tdict[i].set_value(sdict[i])
                    elif edict[i][0] == 'random_tree':
                        tdict[i] = {0: TreeItemEdit(tdict[0], i)}
                        tdict[i][0].set_type('tree')
                        tdict[i][0].israndom = True
                        self.random_dict_to_tree(tdict[i], sdict[i])
                        tdict[i][0].setExpanded(True)
                else:
                    if edict[i][0] == 'tree':
                        tdict[i] = {0: TreeItemEdit(tdict[0], i)}
                        tdict[i][0].set_type(edict[i][0])
                        if len(edict[i]) > 2 and edict[i][2]:
                            tdict[i][0].setBackground(1, self.red)
                        else:
                            self.add_another_to_json(i, edict[i], sdict)
                        self.complex_dict_to_tree(tdict[i], edict[i][1], {})
                        tdict[i][0].setExpanded(True)
                    else:
                        tdict[i] = TreeItemEdit(tdict[0], i)
                        tdict[i].set_type(edict[i][0])
                        tdict[i].set_value(edict[i][1])
        if 'list' in edict:
            tdict[0].set_kid_list(edict['list'])
            index = tdict[0].listtype[2]
            while True:
                if str(index) not in sdict:
                    if str(index + 1) in sdict:
                        self.add_another_to_json(str(index), edict['list'], sdict)
                    else:
                        break
                i = str(index)
                tdict[0].listtype[2] += 1
                tdict[0].listtype[3] += 1
                if edict['list'][0] == 'tree':
                    tdict[i] = {0: TreeItemEdit(tdict[0], i)}
                    tdict[i][0].set_type(edict['list'][0])
                    tdict[i][0].islist = True
                    self.complex_dict_to_tree(tdict[i], edict['list'][1], sdict[i])
                    tdict[i][0].setExpanded(True)
                else:
                    tdict[i] = TreeItemEdit(tdict[0], i)
                    tdict[i].set_type(edict['list'][0])
                    tdict[i].set_value(sdict[i])
                    tdict[i].islist = True
                index += 1

    def item_dict_to_extra_tree(self, tdict, sdict):
        tempmenu = TreeItemEdit(tdict[0], '物品属性')
        tempmenu.set_type('list')
        tempmenu.set_kid_list(['tree', {'名称': ['text', ''], '代码': ['text', ''], '后缀': ['text', ''], '展示前缀': ['text', ''], '展示后缀': ['text', ''], '叠加': ['text', '']}, 1, 0, False])
        for ii in sdict:
            if isinstance(sdict[ii], dict) and '代码' in sdict[ii] and '后缀' in sdict[ii] and '展示前缀' in sdict[ii] and '展示后缀' in sdict[ii] and '叠加' in sdict[ii]:
                i = str(tempmenu.listtype[2])
                tempmenu.listtype[2] += 1
                tempmenu.listtype[3] += 1
                new0 = TreeItemEdit(tempmenu, str(i))
                new0.set_type('tree')
                new0.islist = True
                new1 = TreeItemEdit(new0, '名称')
                new1.set_type('text')
                new1.set_value(ii)
                new2 = TreeItemEdit(new0, '代码')
                new2.set_type('text')
                new2.set_value(sdict[ii]['代码'])
                new3 = TreeItemEdit(new0, '后缀')
                new3.set_type('text')
                new3.set_value(sdict[ii]['后缀'])
                new4 = TreeItemEdit(new0, '展示前缀')
                new4.set_type('text')
                new4.set_value(sdict[ii]['展示前缀'])
                new5 = TreeItemEdit(new0, '展示后缀')
                new5.set_type('text')
                new5.set_value(sdict[ii]['展示后缀'])
                new6 = TreeItemEdit(new0, '叠加')
                new6.set_type('text')
                new6.set_value(sdict[ii]['叠加'])
                new0.setExpanded(True)

    def combine_text_to_tree(self, tdict, sdict):
        tdict['混合文字'] = {0: TreeItemEdit(tdict[0], '混合文字')}
        tdict['混合文字'][0].set_type('combine_tree')
        tdict['混合文字'][0].set_kid_list(edit_json.edit_adition['混合文字'])
        for i in sdict['混合文字']:
            if isinstance(sdict['混合文字'][i], dict):
                tdict['混合文字'][i] = {0: TreeItemEdit(tdict['混合文字'][0], i)}
                tdict['混合文字'][i][0].set_type('tree')
                self.complex_dict_to_tree(tdict['混合文字'][i], edit_json.edit_adition['混合文字'][1], sdict['混合文字'][i])
                tdict['混合文字'][i][0].islist = True
                tdict['混合文字'][i][0].setExpanded(True)
            else:
                tdict['混合文字'][i] = TreeItemEdit(tdict['混合文字'][0], i)
                tdict['混合文字'][i].set_type('text')
                tdict['混合文字'][i].set_value(sdict['混合文字'][i])
                tdict['混合文字'][i].islist = True
            tdict['混合文字'][0].tree_or_text = not tdict['混合文字'][0].tree_or_text
            tdict['混合文字'][0].listtype[2] += 1
            tdict['混合文字'][0].listtype[3] += 1
        tdict['混合文字'][0].setExpanded(True)

    def random_dict_to_tree(self, tdict, sdict):
        for i in sdict:
            if isinstance(sdict[i], dict):
                tdict[i] = {0: TreeItemEdit(tdict[0], i)}
                tdict[i][0].set_type('tree')
                tdict[i][0].israndom = True
                self.random_dict_to_tree(tdict[i], sdict[i])
                tdict[i][0].setExpanded(True)
            else:
                tdict[i] = TreeItemEdit(tdict[0], i)
                tdict[i].israndom = True
                if isinstance(sdict[i], str):
                    tdict[i].set_type('text')
                else:
                    tdict[i].set_type('number')
                tdict[i].set_value(sdict[i])

    def add_another_to_json(self, name, edict, sdict):
        if name == 'list':
            if edict[4] and edict[3] < edict[2]:
                pass
            else:
                for i in range(edict[2], edict[3] + 1):
                    if edict[0] == 'tree':
                        sdict[str(i)] = {}
                        for j in edict[1]:
                            self.add_another_to_json(j, edict[1][j], sdict[str(i)])
                    else:
                        sdict[str(i)] = edict[1]
        elif len(edict) == 3 and edict[2]:
            pass
        else:
            if edict[0] == 'tree':
                sdict[name] = {}
                for j in edict[1]:
                    self.add_another_to_json(j, edict[1][j], sdict[name])
            elif edict[0] == 'random_tree':
                sdict[name] = {}
            else:
                sdict[name] = edict[1]

    def edit_text_base_selected_changed(self, ss0='', ss1='', ss2=''):
        ss = [ss1, ss2]
        if ss1 == '':
            ss[0] = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        if ss2 == '':
            ss[1] = self.editlayout['修改核心']['竖布局']['代码库'][0].currentText()
        self.editlayout['基础数据']['竖布局']['树'][0].clear()
        self.editlayout['基础数据']['竖布局']['树'] = {0: self.editlayout['基础数据']['竖布局']['树'][0]}
        self.dict_to_tree(self.editlayout['基础数据']['竖布局']['树'], self.text_base[edit_json.edit_source[ss[0]][0]][ss[1]])
        self.editlayout['基础数据']['竖布局']['树'][0].expandAll()

    def json_edit_new(self, default_text=''):
        selected = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        text, ok = MoInputWindow.getText(self, '新增一个' + selected, '请输入你想要的' + selected + '的名称:', default_text)
        if ok:
            if text in self.json_base[selected]:
                QMessageBox.critical(self, '您的输入有问题', '您输入的【' + text + '】已经存在于【' + selected + '】中，请检查是否书写错误。')
                self.json_edit_new(text)
            else:
                self.json_name[selected].append(text)
                self.json_base[selected][text] = {}
                for i in edit_json.edit[selected]:
                    self.add_another_to_json(i, edit_json.edit[selected][i], self.json_base[selected][text])
                self.json_base[selected][text]['页面名'] = text
                self.resort()
                self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(selected)
                self.edit_category_selected_changed()
                self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(text)
                self.edit_target_selected_changed()

    def json_edit_download(self):
        ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(),
              self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
        if ss[0][-1] == '源':
            self.json_base[ss[0]][ss[1]] = self.download_json(ss[1] + '/源.json')
        else:
            self.json_base[ss[0]][ss[1]] = self.download_json(ss[1] + '.json')
        self.file_save(os.path.join('database', 'json_base.json'), json.dumps(self.json_base))
        self.edit_target_selected_changed()
        QMessageBox.information(self, '更新完毕', '更新成功！您成功从wiki下载到' + ss[1] + '的信息。')

    def json_edit_delete(self):
        warning = QMessageBox.warning(self, '删除', '您正试图删除一个库，这个操作将会难以撤销。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if warning == QMessageBox.Yes:
            self.update_json_name(self.download_json('json_name.json'))
            ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(),
                  self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
            upload_data = {'action': 'delete', 'format': 'json', 'token': self.csrf_token}
            if ss[0][-1] == '源':
                upload_data['title'] = 'Data:' + ss[1] + '/源.json'
            else:
                upload_data['title'] = 'Data:' + ss[1] + '.json'
            k = 0
            while True:
                self.time_point_for_iterable_sleep_by_time()
                upload_info = self.seesion.post(self.target_url, headers=self.header, data=upload_data)
                if upload_info.status_code < 400:
                    self.json_base[ss[0]].pop(ss[1])
                    self.json_name[ss[0]].pop(self.json_name[ss[0]].index(ss[1]))
                    self.resort()
                    self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(ss[0])
                    self.edit_category_selected_changed()
                    QMessageBox.information(self, '删除完毕', '删除成功！您将不会再看到这个库。')
                    break
                else:
                    k += 1
                    self.time_point_for_iterable_sleep_by_time(k)
                    if k >= 5:
                        QMessageBox.information(self, '删除失败', '删除失败！错误代码：' + str(upload_info.status_code))
                        break

    def json_edit_change_name(self):
        warning = QMessageBox.warning(self, '改名', '您正改变库的名字，这个操作将会难以撤销。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if warning == QMessageBox.Yes:
            ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(),
                  self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
            text, ok = MoInputWindow.getText(self, '修改名字', '您希望将' + ss[1] + '的名字改为:', ss[1])
            if ok:
                upload_data = {'action': 'delete', 'format': 'json', 'token': self.csrf_token}
                if ss[0][-1] == '源':
                    upload_data['title'] = 'Data:' + ss[1] + '/源.json'
                else:
                    upload_data['title'] = 'Data:' + ss[1] + '.json'
                k = 0
                while True:
                    self.time_point_for_iterable_sleep_by_time()
                    upload_info = self.seesion.post(self.target_url, headers=self.header, data=upload_data)
                    if upload_info.status_code < 400:
                        self.json_base[ss[0]][text] = copy.deepcopy(self.json_base[ss[0]][ss[1]])
                        self.json_name[ss[0]].append(text)
                        self.json_base[ss[0]].pop(ss[1])
                        self.json_name[ss[0]].pop(self.json_name[ss[0]].index(ss[1]))
                        self.resort()
                        self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(ss[0])
                        self.edit_category_selected_changed()
                        self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(text)
                        self.edit_target_selected_changed()
                        QMessageBox.information(self, '改名完毕', '库【' + ss[1] + '】已经被改名为【' + text + '】\n请记得保存后上传')
                        break
                    else:
                        k += 1
                        self.time_point_for_iterable_sleep_by_time(k)
                        if k >= 5:
                            QMessageBox.information(self, '删除失败', '删除失败！错误代码：' + str(upload_info.status_code))
                            break

    def json_edit_save(self):
        ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(),
              self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
        self.json_base[ss[0]][ss[1]] = {}
        self.read_tree_to_json(self.editlayout['修改核心']['竖布局']['树'][0], self.json_base[ss[0]][ss[1]])
        self.file_save_all()
        self.update_the_jsons_alreadey = False
        QMessageBox.information(self, "已完成", '已经保存更改，但没有进行数据更新\n请记得更新数据。')
        self.edit_target_selected_changed()

    def json_edit_save_and_update(self):
        error_stop = False
        ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(),
              self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
        self.json_base[ss[0]][ss[1]] = {}
        self.read_tree_to_json(self.editlayout['修改核心']['竖布局']['树'][0], self.json_base[ss[0]][ss[1]])
        self.file_save_all()
        if ss[0][:2] == '机制':
            error_stop = self.update_json_base_mechanism(ss[1])
        else:
            error_stop = self.update_json_base(info='已经保存并更新完毕\n请记得上传。')
        self.update_the_jsons_alreadey = not error_stop
        self.edit_target_selected_changed()

    def json_edit_loop_update(self):
        ss = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        for i in self.json_base[ss]:
            self.editlayout['修改核心']['竖布局']['树'][0].clear()
            self.editlayout['修改核心']['竖布局']['树'] = {0: self.editlayout['修改核心']['竖布局']['树'][0]}
            self.editlayout['修改核心']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])
            self.editlayout['修改核心']['竖布局']['树'][0].setColumnWidth(0, 300)
            self.complex_dict_to_tree(self.editlayout['修改核心']['竖布局']['树'], edit_json.edit[ss], self.json_base[ss][i])
            self.json_base[ss][i] = {}
            self.read_tree_to_json(self.editlayout['修改核心']['竖布局']['树'][0], self.json_base[ss][i])
            self.file_save_all()
            self.time_point_for_iterable_sleep_by_time()
            QApplication.processEvents()
        self.edit_target_selected_changed()

    def tree_item_clicked(self):
        sender = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        parent = sender.parent()
        self.editlayout['竖布局']['修改数据'].setEnabled(sender.hasvalue)
        self.editlayout['竖布局']['增加列表'].setEnabled(sender.haslist and not sender.israndom)
        self.editlayout['竖布局']['向上移动列表'].setEnabled(sender.islist and not sender.israndom)
        self.editlayout['竖布局']['向下移动列表'].setEnabled(sender.islist and not sender.israndom)
        self.editlayout['竖布局']['删除列表'].setEnabled(sender.islist and not sender.israndom)

        self.editlayout['竖布局']['启用条目'].setEnabled(sender.background(1) == self.red)
        self.editlayout['竖布局']['禁用条目'].setEnabled(sender.background(1) == self.green)

        self.editlayout['竖布局']['增加新次级条目'].setEnabled(sender.israndom and sender.itemtype == 'tree')
        self.editlayout['竖布局']['删除该次级条目'].setEnabled(sender.israndom and parent.israndom)
        self.editlayout['竖布局']['转换为混合文字'].setEnabled(
            sender.itemtype == 'text' and sender.childCount() == 0 and not sender.israndom)
        self.editlayout['竖布局']['转换为普通文字'].setEnabled(
            sender.itemtype == 'text' and sender.childCount() > 0 and not sender.israndom)

        self.editlayout['竖布局']['传统目标设定'].setEnabled(
            sender.text(0) == '不分类' or sender.text(0) == '英雄' or sender.text(0) == '非英雄')

    def tree_item_double_clicked(self):
        sender = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        if sender.hasvalue:
            self.json_edit_change_value()

    def copy_text_from_tree(self, index=0):
        wincld.OpenClipboard()
        wincld.EmptyClipboard()
        wincld.SetClipboardData(win32con.CF_UNICODETEXT, self.sender().currentItem().text(index))
        wincld.CloseClipboard()

    def self_edit_button_default(self, bool=False):
        self.editlayout['竖布局']['修改数据'].setEnabled(bool)
        self.editlayout['竖布局']['增加列表'].setEnabled(bool)
        self.editlayout['竖布局']['向上移动列表'].setEnabled(bool)
        self.editlayout['竖布局']['向下移动列表'].setEnabled(bool)
        self.editlayout['竖布局']['删除列表'].setEnabled(bool)
        self.editlayout['竖布局']['启用条目'].setEnabled(bool)
        self.editlayout['竖布局']['禁用条目'].setEnabled(bool)
        self.editlayout['竖布局']['增加新次级条目'].setEnabled(bool)
        self.editlayout['竖布局']['删除该次级条目'].setEnabled(bool)
        self.editlayout['竖布局']['转换为混合文字'].setEnabled(bool)
        self.editlayout['竖布局']['转换为普通文字'].setEnabled(bool)
        self.editlayout['竖布局']['传统目标设定'].setEnabled(bool)

    def json_edit_change_value(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        if item.itemtype == 'number':
            text, ok = MoInputWindow.getNumber(self, '修改值', '您想将其修改为:', item.text(1))
        elif item.itemtype == 'int':
            text, ok = MoInputWindow.getInt(self, '修改值', '您想将其修改为:', item.text(1))
        else:
            text, ok = MoInputWindow.getText(self, '修改值', '您想将其修改为:', item.text(1))
        if ok:
            item.set_value(text)

    def json_edit_add_list(self):
        category = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        i = str(item.listtype[2])
        item.listtype[2] += 1
        item.listtype[3] += 1
        if item.itemtype == 'combine_tree':
            item.tree_or_text = not item.tree_or_text
        if item.itemtype == 'combine_tree' and item.tree_or_text:
            temp = TreeItemEdit(item, i)
            temp.set_type('text')
            temp.set_value('')
            temp.islist = True
        else:
            sdict = {}
            self.add_another_to_json(i, item.listtype, sdict)
            if item.listtype[0] == 'tree':
                temp = {0: TreeItemEdit(item, i)}
                temp[0].set_type(item.listtype[0])
                temp[0].islist = True
                self.complex_dict_to_tree(temp, item.listtype[1], sdict[i])
                if item.itemtype == 'combine_tree':
                    temp[0].child(2).child(1).set_value('升级属性')
                    temp[0].child(2).child(4).set_value('属性')
                temp[0].setExpanded(True)
            else:
                temp = TreeItemEdit(item, i)
                temp.set_type(item.listtype[0])
                temp.set_value(sdict[i])
                temp.islist = True
        if category == '物品' and item.text(0) == '物品属性':
            choose = ['默认']
            for i in edit_json.edit_adition['物品属性']:
                choose.append(i)
            text1, ok1 = MoInputWindow.getItem(self, "增加新目标", '目标类型', choose)
            if ok1:
                if text1 in edit_json.edit_adition['物品属性']:
                    temp[0].child(0).setText(1, text1)
                    temp[0].child(1).setText(1, edit_json.edit_adition['物品属性'][text1]['代码'])
                    temp[0].child(2).setText(1, edit_json.edit_adition['物品属性'][text1]['后缀'])
                    temp[0].child(3).setText(1, edit_json.edit_adition['物品属性'][text1]['展示前缀'])
                    temp[0].child(4).setText(1, edit_json.edit_adition['物品属性'][text1]['展示后缀'])
        item.setExpanded(True)

    def json_edit_move_list_item(self, move_step=1):
        tree = self.editlayout['修改核心']['竖布局']['树'][0]
        item = tree.currentItem()
        parent = item.parent()
        index = parent.indexOfChild(item)
        counts = parent.childCount()
        parent.removeChild(item)
        targetind = max(counts - parent.listtype[3], min(index + move_step, counts - 1))
        parent.insertChild(targetind, item)
        for i in range(counts - parent.listtype[3], counts):
            parent.child(i).setText(0, str(i - counts + parent.listtype[2]))
        item.setExpanded(True)
        tree.setCurrentItem(item)
        self.tree_item_clicked()

    def json_edit_delete_list(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        ii = int(item.text(0))
        parent = item.parent()
        parent.removeChild(item)
        counts = parent.childCount()
        parent.listtype[2] -= 1
        parent.listtype[3] -= 1
        for i in range(counts - parent.listtype[3], counts):
            parent.child(i).setText(0, str(i - counts + parent.listtype[2]))
        if parent.itemtype == 'combine_tree':
            parent.tree_or_text = not parent.tree_or_text

    def json_edit_tree_use_true(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        item.setBackground(1, self.green)
        self.tree_item_clicked()
        item.setExpanded(True)

    def json_edit_tree_use_false(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        item.setBackground(1, self.red)
        self.tree_item_clicked()
        item.setExpanded(False)

    def json_edit_text_to_combine(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        itemtxt = item.itemvalue
        item.delete_value()
        temp = TreeItemEdit(item, '混合文字')
        temp.set_type('combine_tree')
        temp.set_kid_list(edit_json.edit_adition['混合文字'])
        tree = self.editlayout['修改核心']['竖布局']['树'][0].setCurrentItem(temp)
        self.tree_item_clicked()
        self.json_edit_add_list()
        temp2 = temp.child(0)
        temp2.set_value(itemtxt)
        item.setExpanded(True)

    def json_edit_combine_to_text(self):
        warning = QMessageBox.warning(self, '转换', '您正试图将一串已有的混合文字转换为普通文字。\n内部所有的内容将会消失，这个操作将会难以撤销。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if warning == QMessageBox.Yes:
            item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
            item.removeChild(item.child(0))
            item.set_value('')
            self.tree_item_clicked()

    def json_edit_add_new_item(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        choose = ('文字（可以填入任意信息）', '数字（只能填入有效数字）', '整数（只能填入不含小数点的整数）', '树（可以拥有下属信息，但自身没有值）')
        choose_style = ['text', 'number', 'int', 'text']
        text1, text2, ok = MoInputWindow.get_item_and_content(self, "增加新条目", '条目的类型', choose, choose_style, False)
        if ok:
            temp = TreeItemEdit(item, text2)
            temp.israndom = True
            if choose[0] == text1:
                temp.set_type('text')
                temp.set_value('')
            elif choose[1] == text1:
                temp.set_type('number')
                temp.set_value(0)
            elif choose[2] == text1:
                temp.set_type('int')
                temp.set_value(0)
            elif choose[3] == text1:
                temp.set_type('tree')
        item.setExpanded(True)

    def json_edit_delete_item(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        parent = item.parent()
        parent.removeChild(item)

    def edit_json_expand_2nd(self):
        self.editlayout['修改核心']['竖布局']['树'][0].expandAll()
        tree = self.editlayout['修改核心']['竖布局']['树'][0]
        for i in range(tree.topLevelItemCount()):
            for j in range(tree.topLevelItem(i).childCount()):
                tree.topLevelItem(i).child(j).setExpanded(False)

    def edit_json_expand_all(self):
        self.editlayout['修改核心']['竖布局']['树'][0].expandAll()
        tree = self.editlayout['修改核心']['竖布局']['树'][0]
        for i in range(tree.topLevelItemCount()):
            if tree.topLevelItem(i).background(1) == self.red:
                tree.topLevelItem(i).setExpanded(False)

    def json_edit_target_default(self):
        item = self.editlayout['修改核心']['竖布局']['树'][0].currentItem()
        choose = []
        for i in edit_json.edit_default_category:
            choose.append(i)
        text, ok = MoInputWindow.getItem(self, "增加新条目", '条目的类型', choose)
        if ok:
            for i in range(item.childCount()):
                item.removeChild(item.child(i))
            tdict = {0: item}
            self.complex_dict_to_tree(tdict, edit_json.edit_default_target, edit_json.edit_default_category[text])

    def read_tree_to_json(self, tree, sdict):
        category = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        for i in range(tree.topLevelItemCount()):
            tli = tree.topLevelItem(i)
            if category == '物品' and tli.text(0) == '物品属性':
                for j in range(tli.childCount()):
                    jc = tli.child(j)
                    sdict[jc.child(0).text(1)] = {'代码': jc.child(1).text(1), '后缀': jc.child(2).text(1), '展示前缀': jc.child(3).text(1), '展示后缀': jc.child(4).text(1),
                                                  '叠加': jc.child(5).text(1)}
            else:
                self.read_tree_item_to_json(tli, sdict)

    def read_tree_item_to_json(self, item, sdict):
        if item.childCount() > 0:
            if item.background(1) == self.red:
                return
            else:
                sdict[item.text(0)] = {}
                for i in range(item.childCount()):
                    self.read_tree_item_to_json(item.child(i), sdict[item.text(0)])
        else:
            sdict[item.text(0)] = item.itemvalue

    def check_version(self):
        try:
            version_file = open(os.path.join('database', 'version_base.json'), mode="r", encoding="utf-8")
            self.version_base = json.loads(version_file.read())
            version_file.close()
        except FileNotFoundError:
            self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
        try:
            version_file = open(os.path.join('database', 'version_list.json'), mode="r", encoding="utf-8")
            self.version_list = json.loads(version_file.read())
            version_file.close()
            self.versionlayout['版本列表']['横排版']['列表'].clear()
            for i in self.version_list['版本']:
                for j in range(len(i)):
                    if j == 0:
                        new1 = QTreeWidgetItem(self.versionlayout['版本列表']['横排版']['列表'])
                        new1.setText(0, i[j])
                        if i[j] in self.version_base:
                            new1.setBackground(0, self.green)
                        else:
                            new1.setBackground(0, self.red)
                    else:
                        new2 = QTreeWidgetItem(new1)
                        new2.setText(0, i[j])
                        if i[0] + '/' + i[j] in self.version_base:
                            new2.setBackground(0, self.green)
                        else:
                            new2.setBackground(0, self.red)
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "获取版本数据失败", "请问您是否想要从网络上重新下载？", QMessageBox.NoButton, self)
            buttonWeb = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            messageBox.exec_()
            if messageBox.clickedButton() == buttonWeb:
                self.download_version_list()

    def download_version_list(self):
        self.version_list = self.download_json('版本更新.json')
        self.file_save(os.path.join('database', 'version_list.json'), json.dumps(self.version_list))
        QMessageBox.information(self, '下载成功', '版本信息已经下载保存完毕。')
        self.versionlayout['版本列表']['横排版']['列表'].clear()
        for i in self.version_list['版本']:
            for j in range(len(i)):
                if j == 0:
                    new1 = QTreeWidgetItem(self.versionlayout['版本列表']['横排版']['列表'])
                    new1.setText(0, i[j])
                    if i[j] in self.version_base:
                        new1.setBackground(0, self.green)
                    else:
                        new1.setBackground(0, self.red)
                else:
                    new2 = QTreeWidgetItem(new1)
                    new2.setText(0, i[j])
                    if i[0] + '/' + i[j] in self.version_base:
                        new2.setBackground(0, self.green)
                    else:
                        new2.setBackground(0, self.red)

    def upload_version_list(self):
        self.upload_json('版本更新.json', self.version_list)
        self.file_save(os.path.join('database', 'version_list.json'), json.dumps(self.version_list))
        QMessageBox.information(self, '上传成功', '版本信息已经更新保存完毕。')

    def add_version_list(self, next=0):
        index = self.versionlayout['版本列表']['横排版']['列表'].indexOfTopLevelItem(
            self.versionlayout['版本列表']['横排版']['列表'].currentItem())
        if index == -1:
            if next == 0:
                index = 0
            elif next == 1:
                index = self.versionlayout['版本列表']['横排版']['列表'].topLevelItemCount()
        else:
            index += next
        text, ok = MoInputWindow.getText(self, "增加新版本", '版本号')
        if ok:
            new = QTreeWidgetItem()
            new.setText(0, text)
            new.setBackground(0, self.red)
            self.versionlayout['版本列表']['横排版']['列表'].insertTopLevelItem(index, new)
            self.version_list = {'版本': []}
            for i in range(self.versionlayout['版本列表']['横排版']['列表'].topLevelItemCount()):
                self.version_list['版本'].append([self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).text(0)])
                for j in range(self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).childCount()):
                    self.version_list['版本'][i].append(
                        self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).child(j).text(0))

    def add_junior_version_list(self):
        item = self.versionlayout['版本列表']['横排版']['列表'].currentItem()
        text, ok = MoInputWindow.getText(self, "增加新版本", '次级版本号')
        if ok:
            new = QTreeWidgetItem(item)
            new.setText(0, text)
            new.setBackground(0, self.red)
            self.version_list = {'版本': []}
            for i in range(self.versionlayout['版本列表']['横排版']['列表'].topLevelItemCount()):
                self.version_list['版本'].append([self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).text(0)])
                for j in range(self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).childCount()):
                    self.version_list['版本'][i].append(
                        self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).child(j).text(0))
            item.setExpanded(True)

    def check_version_content(self):
        item = self.versionlayout['版本列表']['横排版']['列表'].currentItem()
        if item.parent() == None:
            title = item.text(0)
        else:
            title = item.parent().text(0) + '/' + item.text(0)
        self.versionlayout['版本列表']['横排版']['竖排版']['插入次级版本'].setEnabled(item.parent() == None)
        if title in self.version_base:
            self.complex_json_to_version_tree()
            self.version_tree_expand_toplevelitem()
            self.version_edit_all_button_default()
        else:
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "您没有这个版本更新的库，请问您准备从哪里获取？", QMessageBox.NoButton,
                                     self)
            button1 = messageBox.addButton('从网络下载', QMessageBox.YesRole)
            button2 = messageBox.addButton('造个新的', QMessageBox.AcceptRole)
            button3 = messageBox.addButton('不创建', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == button1:
                self.download_one_version()
            elif messageBox.clickedButton() == button2:
                self.create_one_version()

    def download_one_version(self):
        item = self.versionlayout['版本列表']['横排版']['列表'].currentItem()
        if item.parent() == None:
            text = item.text(0)
            title = text
        else:
            text = item.text(0)
            title = item.parent().text(0) + '/' + text
        download_data = {'action': 'jsondata', 'title': title + '.json', 'format': 'json'}
        download_info = self.seesion.post(self.target_url, headers=self.header, data=download_data)
        if 'error' in download_info.json() and download_info.json()['error']['code'] == 'invalidtitle':
            messageBox = QMessageBox(QMessageBox.Critical, "下载失败", "网络上没有这个版本更新的库，请问是否自行创建？", QMessageBox.NoButton, self)
            button1 = messageBox.addButton('自行新建', QMessageBox.YesRole)
            button2 = messageBox.addButton('不创建', QMessageBox.NoRole)
            messageBox.exec_()
            if messageBox.clickedButton() == button1:
                self.create_one_version()
        else:
            item.setBackground(0, self.green)
            self.version_base[title] = download_info.json()['jsondata']
            self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
            self.complex_json_to_version_tree()
            QMessageBox.information(self, '下载成功', title + '版本已更新至本地。')

    def download_all_versions(self):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6,
                           self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json中……')
        self.w.confirm_numbers(len(self.version_list['版本']))
        for i in range(len(self.version_list['版本'])):
            for j in range(len(self.version_list['版本'][i])):
                if j == 0:
                    title = self.version_list['版本'][i][j]
                else:
                    title = self.version_list['版本'][i][0] + '/' + self.version_list['版本'][i][j]
                k = 0
                while True:
                    self.time_point_for_iterable_sleep_by_time()
                    download_data = {'action': 'jsondata', 'title': title + '.json', 'format': 'json'}
                    download_info = self.seesion.post(self.target_url, headers=self.header, data=download_data)
                    if download_info.status_code < 400:
                        try:
                            download_info_json = download_info.json()
                            if 'error' in download_info_json and download_info_json['error']['code'] == 'invalidtitle':
                                self.w.addtext([self.version_list['版本'][i][j] + '版本json不存在。', 0], i)
                            else:
                                self.version_base[title] = download_info_json['jsondata']
                                if j == 0:
                                    self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).setBackground(0, self.green)
                                else:
                                    self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).child(j - 1).setBackground(0, self.green)
                                self.w.addtext([title + '版本json下载保存成功。', 1], i)
                            QApplication.processEvents()
                            break
                        except:
                            k += 1
                            self.w.addtext([title + '版本json下载暂时出现了失败。已尝试' + str(k) + '次，正在重新尝试', 2], i)
                    else:
                        k += 1
                        self.w.addtext([title + '版本json下载暂时出现了失败。已尝试' + str(k) + '次，正在重新尝试', 2], i)
                        if k > 10:
                            self.w.addtext([title + '版本json下载失败。请重新检查网络后重新下载', 0], i)
                            break
        self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
        QMessageBox.information(self.w, '下载成功', '所有版本号已经下载并保存完毕。')

    def version_edit_loop_update(self):
        for i in range(self.versionlayout['版本列表']['横排版']['列表'].topLevelItemCount()):
            topitem = self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i)
            if topitem.background(0) == self.green:
                self.versionlayout['版本列表']['横排版']['列表'].setCurrentItem(topitem)
                self.check_version_content()
                self.upload_one_version(False)
                self.time_point_for_iterable_sleep_by_time()
                QApplication.processEvents()
                for j in range(topitem.childCount()):
                    item = topitem.child(j)
                    if item.background(0) == self.green:
                        self.versionlayout['版本列表']['横排版']['列表'].setCurrentItem(item)
                        self.check_version_content()
                        self.upload_one_version(False)
                        self.time_point_for_iterable_sleep_by_time()
                        QApplication.processEvents()

    def version_save_the_version(self):
        item = self.versionlayout['版本列表']['横排版']['列表'].currentItem()
        if item.parent() == None:
            title = item.text(0)
        else:
            title = item.parent().text(0) + '/' + item.text(0)
        self.version_base[title] = {'分类': '版本更新', '版本': title, '图片': 'Patch_' + title + '.png'}
        for i in range(self.versionlayout['版本内容']['横排版']['树'][0].topLevelItemCount()):
            items = self.versionlayout['版本内容']['横排版']['树'][0].topLevelItem(i)
            if items.itemtype == 'text':
                self.version_base[title][items.text(0)] = items.text(1)
            elif items.background(1) == self.green:
                self.version_base[title][items.text(0)] = {}
                if items.text(0) == '开头' or items.text(0) == '结尾':
                    for j in range(items.childCount()):
                        items2 = items.child(j)
                        self.version_base[title][items.text(0)][items2.text(0)] = self.version_tree_to_json(items2)
                else:
                    for j in range(items.childCount()):
                        items2 = items.child(j)
                        self.version_base[title][items.text(0)][items2.text(0)] = edit_json.one_version_name_sort(self.version_tree_to_json(items2))
                temp1 = copy.deepcopy(self.version_base[title][items.text(0)])
                if '无标题' not in self.version_base[title][items.text(0)]:
                    temp1['无标题'] = {'0': ['', '', {'序列级数': 1, '文字': '', '目标': []}]}
                else:
                    temp1['无标题'] = self.version_base[title][items.text(0)]['无标题']
                    self.version_base[title][items.text(0)].pop('无标题')
                temp1.update(self.version_base[title][items.text(0)])
                self.version_base[title][items.text(0)] = copy.deepcopy(temp1)
        if item.parent() == None:
            self.version_base[title]['次级版本'] = []
            for i in range(item.childCount()):
                self.version_base[title]['次级版本'].append(item.text(0) + '/' + item.child(i).text(0))
        self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
        return title

    def save_one_version(self):
        self.version_save_the_version()
        self.complex_json_to_version_tree()
        QMessageBox.information(self, '上传成功', '版本信息已经更新保存完毕。')

    def upload_one_version(self, bools=True):
        title = self.version_save_the_version()
        name_list_tree = self.name_create_tree_list_name()
        self.upload_json(title + '.json', self.version_base[title])
        self.upload_page(title, common_page.create_page_logs(title, self.version_base[title], self.version_list['版本']))
        if bools:
            self.complex_json_to_version_tree()
        QMessageBox.information(self, '上传成功', '版本信息已经更新保存完毕。')

    def update_and_upload_all_version(self):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传version中……')
        QApplication.processEvents()
        all_upload = []
        all_upload_page = []
        name_upload_base = self.name_create_tree_list_name()
        for i in self.version_base:
            for j in self.version_base[i]:
                if isinstance(self.version_base[i][j], dict):
                    temp1 = {}
                    if '无标题' not in self.version_base[i][j]:
                        temp1['无标题'] = {'0': ['', '', {'序列级数': 1, '文字': '', '目标': []}]}
                    else:
                        temp1['无标题'] = self.version_base[i][j]['无标题']
                        self.version_base[i][j].pop('无标题')
                    for k in self.version_base[i][j]:
                        if j == '开头' or j == '结尾':
                            temp1[k] = self.version_base[i][j][k]
                        else:
                            temp1[k] = edit_json.one_version_name_sort(self.version_base[i][j][k])
                    self.version_base[i][j] = copy.deepcopy(temp1)
            all_upload.append([i + '.json', self.version_base[i]])
            all_upload_page.append([i, common_page.create_page_logs(i, self.version_base[i], self.version_list['版本'])])
        name_list_tree = self.name_create_tree_list_name()
        num1 = len(all_upload)
        num2 = len(all_upload_page)
        self.w.confirm_numbers(num1 + num2)
        for i in range(num1):
            self.w.addtext(self.upload_json(all_upload[i][0], all_upload[i][1]), i)
            QApplication.processEvents()
        for i in range(num2):
            self.w.addtext(self.upload_page(all_upload_page[i][0], all_upload_page[i][1]), i + num1)
            QApplication.processEvents()
        self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def version_tree_to_json(self, item):
        re = {}
        for i in range(item.childCount()):
            ii = str(len(re))
            item1 = item.child(i)
            if i == 0:
                re[ii] = ['', '']
            else:
                repeat = False
                for j in range(1, len(re)):
                    if item1.text(0) == item.child(j).text(0):
                        ii = str(j)
                        repeat = True
                        break
                if not repeat:
                    re[ii] = [item1.text(0), item1.text(1)]
            for j in range(item1.childCount()):
                item2 = item1.child(j).child(1)
                item3 = item1.child(j).child(2)
                index = len(re[ii])
                while True:
                    if index > 2 and re[ii][index - 1]['文字'] == '':
                        index -= 1
                        re[ii].pop(index)
                    else:
                        break
                re[ii].append({'序列级数': 1, '文字': '', '目标': []})
                item0 = item1.child(j).child(0)
                try:
                    re[ii][index]['序列级数'] = int(item0.itemvalue)
                except ValueError:
                    QMessageBox.critical(self, '错误的序列级数', '您的【' + item1.text(0) + '】中的【' + item1.child(j).text(0) + '】的第' + str(j) + '个序列级数不为正整数，请修改！')
                    while True:
                        text, ok = MoInputWindow.getInt(self, "序列级数", '请输入一个正整数，否则会报错')
                        if ok:
                            re[ii][index]['序列级数'] = text
                            break
                re[ii][index]['文字'] = '{{upgrade|agha}}' + item2.text(1)[4:] if item2.text(1)[:4] == '神杖升级' or item2.text(1)[:4] == 'agha' else item2.text(1)
                for k in range(item3.childCount()):
                    item4 = item3.child(k)
                    re[ii][index]['目标'].append(item4.text(1))
            if len(re[ii]) == 2 or re[ii][-1]['文字'] != '':
                re[ii].append({'序列级数': 1, '文字': '', '目标': []})
        return re

    def create_one_version(self):
        item = self.versionlayout['版本列表']['横排版']['列表'].currentItem()
        if item.parent() == None:
            title = item.text(0)
        else:
            title = item.parent().text(0) + '/' + item.text(0)
        self.version_base[title] = {}
        for i in edit_json.version:
            if edit_json.version[i][0] == 'text':
                self.version_base[title][i] = edit_json.version[i][1]
        item.setBackground(0, self.green)
        self.complex_json_to_version_tree()

    def complex_json_to_version_tree(self):
        self.versionlayout['版本内容']['横排版']['树'][0].clear()
        item = self.versionlayout['版本列表']['横排版']['列表'].currentItem()
        if item.parent() == None:
            title = item.text(0)
        else:
            title = item.parent().text(0) + '/' + item.text(0)
        for i in edit_json.version:
            if edit_json.version[i][0] == 'text':
                if i not in self.version_base[title]:
                    self.version_base[title][i] = edit_json.version[i][1]
                    self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
                new1 = VersionItemEdit(self.versionlayout['版本内容']['横排版']['树'][0])
                new1.itemtype = 'text'
                new1.setText(0, i)
                if i == '官网链接' and self.version_base[title][i] == '':
                    if item.parent() == None:
                        new1.set_value('http://www.dota2.com/patches/' + title)
                    else:
                        new1.set_value('http://www.dota2.com/news/updates/')
                else:
                    new1.set_value(self.version_base[title][i])
            elif edit_json.version[i][0] == 'tree':
                if i in self.version_base[title] and '无标题' in self.version_base[title][i]:
                    new1 = VersionItemEdit(self.versionlayout['版本内容']['横排版']['树'][0])
                    new1.itemtype = 'tree1'
                    new1.setText(0, i)
                    new1.setBackground(1, self.green)
                    for j in self.version_base[title][i]:
                        new2 = VersionItemEdit(new1)
                        new2.itemtype = 'tree2'
                        new2.setText(0, j)
                        for k in self.version_base[title][i][j]:
                            new3 = VersionItemEdit(new2)
                            new3.itemtype = 'tree3'
                            if self.version_base[title][i][j][k][0] == '':
                                new3.setText(0, '无标题')
                            else:
                                new3.setText(0, self.version_base[title][i][j][k][0])
                            new3.setText(1, self.version_base[title][i][j][k][1])
                            for l in range(2, len(self.version_base[title][i][j][k])):
                                new4 = VersionItemEdit(new3)
                                new4.itemtype = 'tree_list'
                                new4.setText(0, str(l - 1))
                                new5 = VersionItemEdit(new4)
                                new5.itemtype = 'text'
                                new5.setText(0, '序列级数')
                                if '序列级数' in self.version_base[title][i][j][k][l]:
                                    new5.set_value(self.version_base[title][i][j][k][l]['序列级数'])
                                else:
                                    new5.set_value(1)
                                new6 = VersionItemEdit(new4)
                                new6.itemtype = 'text'
                                new6.setText(0, '文字')
                                new6.set_value(self.version_base[title][i][j][k][l]['文字'])
                                new7 = VersionItemEdit(new4)
                                new7.itemtype = 'list'
                                new7.setText(0, '目标')
                                for m in self.version_base[title][i][j][k][l]['目标']:
                                    new8 = VersionItemEdit(new7)
                                    new8.itemtype = 'list_text'
                                    new8.set_value(m)
                else:
                    new1 = VersionItemEdit(self.versionlayout['版本内容']['横排版']['树'][0])
                    new1.itemtype = 'tree1'
                    new1.setText(0, i)
                    new1.setBackground(1, self.red)
        self.version_tree_expand_toplevelitem()

    def version_edit_all_button_clicked(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        self.versionlayout['版本内容']['横排版']['竖排版']['修改内容'].setEnabled(item.hasvalue)
        if item.itemtype == 'tree1':
            if item.background(1) == self.red:
                self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setText('启用大分类')
                self.versionlayout['版本内容']['横排版']['竖排版']['加中标题'].setEnabled(False)
            elif item.background(1) == self.green:
                self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setText('禁用大分类')
                self.versionlayout['版本内容']['横排版']['竖排版']['加中标题'].setEnabled(True)
            self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setEnabled(True)
        else:
            self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setText('大分类')
            self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setEnabled(False)
            self.versionlayout['版本内容']['横排版']['竖排版']['加中标题'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除中标题'].setEnabled(item.itemtype == 'tree2')
        self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].setEnabled(item.itemtype == 'tree2')
        self.versionlayout['版本内容']['横排版']['竖排版']['标题分类改名'].setEnabled(item.itemtype == 'tree2' or item.itemtype == 'tree3')
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'].setEnabled(item.itemtype == 'tree3')
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'].setEnabled(item.itemtype == 'tree3')
        self.versionlayout['版本内容']['横排版']['竖排版']['向上移动题目'].setEnabled(item.itemtype == 'tree2' or item.itemtype == 'tree3' or item.itemtype == 'tree_list')
        self.versionlayout['版本内容']['横排版']['竖排版']['向下移动题目'].setEnabled(item.itemtype == 'tree2' or item.itemtype == 'tree3' or item.itemtype == 'tree_list')
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该条目'].setEnabled(item.itemtype == 'tree_list')
        self.versionlayout['版本内容']['横排版']['竖排版']['增加新目标'].setEnabled(item.itemtype == 'list')
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该目标'].setEnabled(item.itemtype == 'list_text')

    def version_edit_all_button_default(self):
        self.versionlayout['版本内容']['横排版']['竖排版']['修改内容'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setText('大分类')
        self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['加中标题'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除中标题'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['标题分类改名'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['向上移动题目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['向下移动题目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该条目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['增加新目标'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该目标'].setEnabled(False)

    def version_item_double_clicked(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        if item.background(1) == self.green:
            self.version_button_tree1_add_tree2()
            item.setExpanded(False)
        elif item.background(1) == self.red:
            self.version_button_tree1()
            item.setExpanded(False)
        elif item.itemtype == 'tree2':
            self.version_button_tree2_add_tree3()
            item.setExpanded(False)
        elif item.hasvalue:
            self.version_edit_change_value()

    def version_edit_change_value(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        ori_text = item.text(1)
        if item.parent() != None and item.parent().parent() != None:
            hero_text = item.parent().parent().text(0)
        ori_text = re.sub(r'[\[\]【】]', lambda x: '\\' + x.group(0), ori_text)
        text, ok = MoInputWindow.getText(self, '修改值', '您想将其修改为:', ori_text)
        if ok:
            text = re.sub(r'(?<!\\)([\[【]{2})', lambda x: '\\' + x.group(1)[0], text)
            text = re.sub(r'(?<!\\)([\]】]{2})', lambda x: '\\' + x.group(1)[0], text)
            text = re.sub(r'(?<!\\)[\[【](.+?)(?<!\\)[\]】]', lambda x: '{{H|' + x.group(1) + '}}', text)
            text = re.sub(r'(?<!\|)shard(?<!\})', lambda x: '{{H|魔晶升级}}', text)
            text = re.sub(r'(?<!\|)agha(?<!\})', lambda x: '{{H|神杖升级}}', text)
            text = re.sub(r'(?<!\|)SHARD(?<!\})', lambda x: '{{H|魔晶技能}}', text)
            text = re.sub(r'(?<!\|)AGHA(?<!\})', lambda x: '{{H|神杖技能}}', text)
            text = re.sub(r'(?<!\|)talent(?<!\})', lambda x: '{{H|天赋升级}}', text)
            text = re.sub(r'^(.+?)：：', lambda x: '{{H|' + x.group(1) + '}}：', text)
            text = re.sub(r'\{\{([AHI])\|([0-9]+?)\}\}', lambda x: '{{' + x.group(1) + '|' + hero_text + x.group(2) + '级天赋}}', text)
            text = re.sub(r'\\[\(\)（）\[\]【】<>《》]', lambda x: x.group(0)[1], text)
            text = re.sub(r'{{{(.+?)[:：](.+?)}}}', lambda x: self.version_input_text_template_simple_txt(x.group(1), x.group(2)), text)
            text = re.sub(r'{{{{(.+?)}}}}', lambda x: self.version_input_text_simple_introduce(x.group(1)), text)
            item.set_value(text)
            if item.parent() != None and item.parent().parent() != None:
                iparent = item.parent()
                igrandpa = iparent.parent()
                nowindex = igrandpa.indexOfChild(iparent)
                allcount = igrandpa.childCount()

                ipattern = re.compile(r'{{[ahi]\|.+?}}', re.I)
                iresult = ipattern.findall(text)
                ilevel = int(iparent.child(0).text(1))

                for h in range(nowindex, allcount):
                    nowparent = igrandpa.child(h)
                    icount = nowparent.childCount()
                    if int(nowparent.child(0).text(1)) > ilevel or nowindex == h:
                        if nowparent.child(icount - 1).text(0) == '目标':
                            for i in iresult:
                                ibool = True
                                itarget = nowparent.child(icount - 1)
                                for j in range(itarget.childCount()):
                                    if itarget.child(j).text(1) == i[4:-2]:
                                        ibool = False
                                        break
                                if ibool:
                                    new = VersionItemEdit(nowparent.child(icount - 1))
                                    new.itemtype = 'list_text'
                                    new.set_value(i[4:-2])
                    else:
                        break
                if igrandpa.itemtype == 'tree3' and igrandpa.child(allcount - 1).child(1).text(1) != '':
                    self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(igrandpa)
                    self.version_button_tree3_add_tree_list(str(ilevel))
                    self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(item)

    def version_input_text_template_simple_txt(self, trait, name):
        for i in [['英雄', 'H'], ['非英雄单位', 'H'], ['物品', 'I'], ['技能', 'A']]:
            if name in self.json_base[i[0]] and trait in self.json_base[i[0]][name] and isinstance(self.json_base[i[0]][name][trait], str):
                return '{{' + i[1] + '|' + name + '}}：' + self.json_base[i[0]][name][trait]
        return '{{{' + trait + '：' + name + '}}}'

    def version_input_text_simple_introduce(self, name):
        rere = ''
        if name in self.json_base['英雄']:
            db = self.json_base['英雄'][name]
            for i in ['主属性', '近战远程', '阵营']:
                rere += db[i]['1'] + '，'
            for i in [['力量', 'Strength_Icon'], ['敏捷', 'Agility_Icon'], ['智力', 'Intelligence_Icon']]:
                rere += '{{图片|' + i[1] + '.png}}' + common_page.number_to_string(db[i[0]]['1']) + '+' + common_page.number_to_string(db[i[0] + '成长']['1'])
            rere += '，' + common_page.number_to_string(db['生命值']['1'] + db['力量']['1'] * 20) + '血，' + common_page.number_to_string(db['生命恢复']['1'] + db['力量']['1'] * 0.1) + '回血，'
            rere += common_page.number_to_string(db['魔法值']['1'] + db['智力']['1'] * 12) + '蓝，' + common_page.number_to_string(db['魔法恢复']['1'] + db['智力']['1'] * 0.05) + '回蓝，'
            rere += common_page.number_to_string(db['攻击下限']['1'] + db[db['主属性']['1']]['1']) + '~' + common_page.number_to_string(db['攻击上限']['1'] + db[db['主属性']['1']]['1']) + '攻击力，'
            rere += common_page.number_to_string(db['护甲']['1'] + round(db['敏捷']['1'] / 6, 2)) + '护甲，' + common_page.number_to_string(db['移动速度']['1']) + '移速，'
            rere += common_page.number_to_string(db['攻击间隔']['1']) + '基础攻击间隔，' + common_page.number_to_string(db['攻击距离']['1']) + '攻击距离。'
        elif name in self.json_base['非英雄单位']:
            db = self.json_base['非英雄单位'][name]
        elif name in self.json_base['物品']:
            db = self.json_base['物品'][name]
            for i, v in db.items():
                if isinstance(v, dict) and '代码' in v and '后缀' in v and '展示前缀' in v and '展示后缀' in v and '叠加' in v and '1' in v:
                    rere += v['展示前缀'] + common_page.number_to_string(v['1']) + v['后缀'] + v['展示后缀'] + '，'
            if db['价格']['1'] != '中立生物掉落':
                rere += '{{图片|Gold symbol.png}}' + common_page.number_to_string(db['价格']['1'])
            if '卷轴价格' in db and db['卷轴价格']['1'] != 0:
                rere += '{{图片|items recipe.png}}&nbsp;' + common_page.number_to_string(db['卷轴价格']['1'])
            if '可拆分' in db and '组件' in db and db['可拆分'] == 1:
                rere += '，可拆分'
            if rere[-1] == '，':
                rere = rere[:-1]
            rere += '。'
            if '组件' in db:
                rere += '由'
                for i, v in db['组件'].items():
                    if int(i) > 1:
                        rere += '，'
                    rere += '{{I|' + v["物品名"] + '}}'
                if '卷轴价格' in db and db['卷轴价格']['1'] != 0:
                    rere += '，以及' + common_page.number_to_string(db['卷轴价格']['1']) + '元的卷轴'
                rere += '合成。'
            if '升级' in db:
                rere += '可合成为：'
                for i, v in db['升级'].items():
                    if int(i) > 1:
                        rere += '，'
                    rere += '{{I|' + v["物品名"] + '}}'
                rere += '。'
        elif name in self.json_base['技能']:
            rere += '{{H|' + name + '}}：' + self.json_base['技能'][name]['描述']
            for i in self.json_base['技能'][name]['属性']:
                rere += self.json_base['技能'][name]['属性'][i]['名称'] + '：' + common_page.create_upgrade_text(self.json_base['技能'][name]['属性'], i) + '，'
            rere += common_page.create_upgrade_manacost(self.json_base['技能'][name]['魔法消耗'], 'span') + common_page.create_upgrade_cooldown(self.json_base['技能'][name]['冷却时间'],
                                                                                                                                          'span')
        return rere

    def version_button_tree1(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        if item.background(1) == self.red:
            new = VersionItemEdit(item)
            new.setText(0, '无标题')
            new.itemtype = 'tree2'
            new2 = VersionItemEdit(new)
            new2.setText(0, '无标题')
            new2.itemtype = 'tree3'
            self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(new2)
            self.version_button_tree3_add_tree_list()
            item.setBackground(1, self.green)
            item.setExpanded(True)
        elif item.background(1) == self.green:
            clickb = QMessageBox.critical(self, '禁用大分类', '您正试图禁用【' + item.text(0) + '】分类！', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if clickb == QMessageBox.Yes:
                while item.childCount() > 0:
                    item.removeChild(item.child(0))
                item.setBackground(1, self.red)
        self.version_edit_all_button_clicked()

    def version_button_tree1_add_tree2(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        text, ok = MoInputWindow.getText(self, '新增一个中标题', '请输入你想要增加的标题名称:')
        if ok:
            new = VersionItemEdit(item)
            new.setText(0, text)
            new.itemtype = 'tree2'
            new2 = VersionItemEdit(new)
            new2.setText(0, '无标题')
            new2.itemtype = 'tree3'
            item.setExpanded(True)
            for i in range(item.childCount() - 1):
                tempi = item.child(i)
                tempi.setExpanded(False)
            self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(new2)
            self.version_button_tree3_add_tree_list()
            new.setExpanded(True)

    def version_button_tree2_add_tree3(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        text, ok = MoInputWindow.getText(self, '新增一个小分类', '请输入你想要增加的分类名称:')
        if ok:
            new = VersionItemEdit(item)
            new.setText(0, text)
            new.itemtype = 'tree3'
            item.setExpanded(True)
            for i in range(item.childCount() - 1):
                tempi = item.child(i)
                tempi.setExpanded(False)
            item.removeChild(new)
            item.insertChild(1, new)
            self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(new)
            self.version_button_tree3_add_tree_list()
            new.setExpanded(True)

    def version_button_tree2_change_name(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        parent = item.parent()
        text, ok = MoInputWindow.getText(self, '改名', '你现在正试图将【' + parent.text(0) + '】的【' + item.text(0) + '】的名字改为:', item.text(0))
        if ok:
            item.setText(0, text)

    def version_button_move_list_item(self, move_step=1):
        tree = self.versionlayout['版本内容']['横排版']['树'][0]
        item = tree.currentItem()
        parent = item.parent()
        index = parent.indexOfChild(item)
        counts = parent.childCount()
        parent.removeChild(item)
        targetind = max(0, min(index + move_step, counts - 1))
        parent.insertChild(targetind, item)
        if item.itemtype == 'tree_list':
            for i in range(0, counts):
                parent.child(i).setText(0, str(i + 1))
            item.setExpanded(True)
        tree.setCurrentItem(item)
        self.version_edit_all_button_clicked()
        self.expand_all_childs(item)

    def version_button_delete_tree_item(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        parent = item.parent()
        len = parent.childCount()
        index = min(parent.indexOfChild(item), len - 2)
        parent.removeChild(item)
        if len == 1:
            self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(parent)
        else:
            self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(parent.child(index))
        self.version_edit_all_button_clicked()

    def version_button_tree3_add_tree_list(self, level='1'):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        new3 = VersionItemEdit(item)
        new3.itemtype = 'tree_list'
        new3.setText(0, str(item.childCount()))
        new6 = VersionItemEdit(new3)
        new6.itemtype = 'text'
        new6.setText(0, '序列级数')
        new6.set_value(level)
        new4 = VersionItemEdit(new3)
        new4.itemtype = 'text'
        new4.setText(0, '文字')
        new4.set_value('')
        new5 = VersionItemEdit(new3)
        new5.itemtype = 'list'
        new5.setText(0, '目标')
        new3.setExpanded(True)
        item.setExpanded(True)

    def version_button_list_add_list_text(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        choose = ['自行填入']
        for i in self.version_default:
            choose.append(i)
        text1, ok1 = MoInputWindow.getItem(self, "增加新目标", '目标类型', choose)
        if ok1:
            if text1 in self.version_default:
                for i in self.version_default[text1]:
                    new = VersionItemEdit(item)
                    new.itemtype = 'list_text'
                    new.set_value(i)
            else:
                text2, ok2 = MoInputWindow.getText(self, "增加新目标", '目标名称')
                if ok2:
                    new = VersionItemEdit(item)
                    new.itemtype = 'list_text'
                    new.set_value(text2)

    def version_tree_expand_toplevelitem(self):
        for i in range(self.versionlayout['版本内容']['横排版']['树'][0].topLevelItemCount()):
            item = self.versionlayout['版本内容']['横排版']['树'][0].topLevelItem(i)
            if item.itemtype == 'text':
                item.setExpanded(True)
            elif item.background(1) == self.green:
                item.setExpanded(True)
                for j in range(item.childCount()):
                    item.child(j).setExpanded(True)
                    for k in range(item.child(j).childCount()):
                        item.child(j).child(k).setExpanded(False)
                        self.expand_all_childs(item.child(j).child(k))

    def expand_all_childs(self, item):
        for i in range(item.childCount()):
            item.child(i).setExpanded(True)
            self.expand_all_childs(item.child(i))

    def name_initial_name_base(self):
        if isinstance(self.name_base['历史'], dict):
            temp = []
            for i, v in self.name_base['历史'].items():
                tempi = {'名称': i}
                tempi.update(v)
                temp.append(tempi)
            self.name_base['历史'] = copy.deepcopy(temp)
        self.name_base['原生'] = []
        self.name_base['衍生'] = []
        self.name_base['历史'] = edit_json.special_sort_list_by_pinyin(self.name_base['历史'], lambda x, y: x[y]['名称'])
        for i in range(len(self.name_base['历史'])):
            self.name_base['历史'][i]['图片'] = ''
            self.name_base['历史'][i]['迷你图片'] = ''
            for j in range(len(self.name_base['历史'])):
                if self.name_base['历史'][j]['名称'] == self.name_base['历史'][i]['页面名']:
                    self.name_base['历史'][i]['页面名'] = self.name_base['历史'][j]['页面名']
        i = '英雄'
        for j in self.json_base[i]:
            if '图片' in self.json_base[i][j] and '迷你图片' in self.json_base[i][j]:
                self.name_base['原生'].append({'名称': j, '页面名': j, '图片': self.json_base[i][j]['图片'], '迷你图片': self.json_base[i][j]['迷你图片']})
                for k in range(len(self.name_base['历史'])):
                    if j == self.name_base['历史'][k]['页面名']:
                        self.name_base['历史'][k].update({'图片': self.json_base[i][j]['图片'], '迷你图片': self.json_base[i][j]['迷你图片']})
                        for l in ['10', '15', '20', '25']:
                            oname = self.name_base['历史'][k]['名称'] + l + '级天赋'
                            tname = j + l + '级左天赋'
                            if tname in self.json_base['技能'] and '图片' in self.json_base['技能'][tname] and '迷你图片' in self.json_base['技能'][tname]:
                                self.name_base['衍生'].append({'名称': oname, '页面名': tname, '图片': self.json_base['技能'][tname]['图片'], '迷你图片': self.json_base['技能'][tname]['迷你图片']})
        for i in ['物品', '非英雄单位', '机制', '单位组']:
            for j in self.json_base[i]:
                if '图片' in self.json_base[i][j] and '迷你图片' in self.json_base[i][j]:
                    self.name_base['原生'].append({'名称': j, '页面名': j, '图片': self.json_base[i][j]['图片'], '迷你图片': self.json_base[i][j]['迷你图片']})
                    for k in range(len(self.name_base['历史'])):
                        if j == self.name_base['历史'][k]['页面名']:
                            self.name_base['历史'][k].update({'图片': self.json_base[i][j]['图片'], '迷你图片': self.json_base[i][j]['迷你图片']})
        i = '技能'
        for j in self.json_base[i]:
            if '图片' in self.json_base[i][j] and '迷你图片' in self.json_base[i][j]:
                self.name_base['原生'].append({'名称': j, '页面名': j, '图片': self.json_base[i][j]['图片'], '迷你图片': self.json_base[i][j]['迷你图片']})
                for k in range(len(self.name_base['历史'])):
                    if j == self.name_base['历史'][k]['页面名']:
                        self.name_base['历史'][k].update({'图片': self.json_base[i][j]['图片'], '迷你图片': self.json_base[i][j]['迷你图片']})
            if '链接指向' in self.json_base[i][j]:
                for k in self.json_base[i][j]['链接指向']:
                    if k != '':
                        self.name_base['原生'].append({'名称': k, '页面名': j, '图片': self.json_base[i][j]['图片'], '迷你图片': self.json_base[i][j]['迷你图片']})
                    else:
                        print('搞错了？')
        i = '英雄'
        for j in self.json_base[i]:
            for k in ['10', '15', '20', '25']:
                tname = j + k + '级左天赋'
                zyname = j + k + '级天赋'
                if tname in self.json_base['技能'] and '图片' in self.json_base['技能'][tname] and '迷你图片' in self.json_base['技能'][tname]:
                    self.name_base['衍生'].append({'名称': zyname, '页面名': tname, '图片': self.json_base['技能'][tname]['图片'], '迷你图片': self.json_base['技能'][tname]['迷你图片']})
        self.show_name_base_in_widget()

    def show_name_base_in_widget(self):
        self.namelayout['历史曾用名']['布局']['树'][0].clear()
        self.namelayout['原生页面']['布局']['树'][0].clear()
        for i in self.name_base['历史']:
            child = QTreeWidgetItem(self.namelayout['历史曾用名']['布局']['树'][0])
            child.setText(0, i['名称'])
            child.setText(1, i['页面名'])
            if i['迷你图片'] != '':
                child.setIcon(1, self.create_icon_by_local_image(i['迷你图片']))
        for i in self.name_base['原生']:
            child = QTreeWidgetItem(self.namelayout['原生页面']['布局']['树'][0])
            child.setText(0, i['名称'])
            if i['迷你图片'] != '':
                child.setIcon(0, self.create_icon_by_local_image(i['迷你图片'] if i['迷你图片'] != 'Talent.png' else i['图片']))
        for i in self.name_base['衍生']:
            child = QTreeWidgetItem(self.namelayout['衍生页面']['布局']['树'][0])
            child.setText(0, i['名称'])
            child.setText(1, i['页面名'])
            if i['迷你图片'] != '':
                child.setIcon(1, self.create_icon_by_local_image(i['迷你图片'] if i['迷你图片'] != 'Talent.png' else i['图片']))

    def name_create_new_name_save(self):
        name = self.namelayout['编辑区']['布局']['新建对照']['布局']['名称输入'].text()
        page_name = self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面输入'].text()
        if name == '':
            QMessageBox.critical(self, '输入缺失', '您没有输入名称！')
        elif page_name == '':
            QMessageBox.critical(self, '输入缺失', '您没有输入指向页面！')
        else:
            self.name_base['历史'].append({'名称': name, '页面名': page_name})
            self.name_initial_name_base()
            for i in range(self.namelayout['历史曾用名']['布局']['树'][0].topLevelItemCount()):
                child = self.namelayout['历史曾用名']['布局']['树'][0].topLevelItem(i)
                if child.text(0) == name and child.text(1) == page_name:
                    self.namelayout['历史曾用名']['布局']['树'][0].setCurrentItem(child)
            for i in range(self.namelayout['原生页面']['布局']['树'][0].topLevelItemCount()):
                child = self.namelayout['原生页面']['布局']['树'][0].topLevelItem(i)
                if child.text(0) == page_name:
                    self.namelayout['原生页面']['布局']['树'][0].setCurrentItem(child)
            QMessageBox.information(self, '添加成功', '您已经成功添加【' + name + '】→【' + page_name + '】')

    def name_create_new_name_reset(self):
        self.namelayout['编辑区']['布局']['新建对照']['布局']['名称输入'].setText('')
        if self.namelayout['原生页面']['布局']['树'][0].currentItem() == None:
            self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面输入'].setText('')
        else:
            self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面输入'].setText(self.namelayout['原生页面']['布局']['树'][0].currentItem().text(0))

    def name_change_old_name_save(self):
        name = self.namelayout['编辑区']['布局']['现存修正']['布局']['名称输入'].text()
        page_name = self.namelayout['编辑区']['布局']['现存修正']['布局']['指向页面输入'].text()
        if name == '':
            QMessageBox.critical(self, '输入缺失', '您还没有选择待修改项！')
        elif page_name == '':
            QMessageBox.critical(self, '输入缺失', '您没有输入指向页面！')
        else:
            targeti = self.namelayout['现存修正']['布局']['树'][0].currentIndex()
            self.name_base['历史'][targeti] = {'名称': name, '页面名': page_name}
            self.name_initial_name_base()
            for i in range(self.namelayout['现存修正']['布局']['树'][0].topLevelItemCount()):
                child = self.namelayout['现存修正']['布局']['树'][0].topLevelItem(i)
                if child.text(0) == page_name:
                    self.namelayout['现存修正']['布局']['树'][0].setCurrentItem(child)
            QMessageBox.information(self, '添加成功', '您已经成功修改【' + name + '】→【' + page_name + '】')

    def name_change_old_name_reset(self):
        self.namelayout['编辑区']['布局']['现存修正']['布局']['指向页面输入'].setText('')
        if self.namelayout['历史曾用名']['布局']['树'][0].currentItem() == None:
            self.namelayout['编辑区']['布局']['现存修正']['布局']['名称输入'].setText('')
        else:
            self.namelayout['编辑区']['布局']['现存修正']['布局']['名称输入'].setText(self.namelayout['历史曾用名']['布局']['树'][0].currentItem().text(0))

    def name_history_names_tree_widget_clicked(self):
        child = self.namelayout['历史曾用名']['布局']['树'][0].currentItem()
        self.namelayout['编辑区']['布局']['现存修正']['布局']['名称输入'].setText(child.text(0))
        self.namelayout['编辑区']['布局']['现存修正']['布局']['确认保存'].setEnabled(True)
        self.namelayout['编辑区']['布局']['现存修正']['布局']['重置'].setEnabled(True)
        self.namelayout['按钮区域']['删除该条目'].setEnabled(True)

    def name_origin_names_tree_widget_clicked(self):
        child = self.namelayout['原生页面']['布局']['树'][0].currentItem()
        self.namelayout['编辑区']['布局']['新建对照']['布局']['指向页面输入'].setText(child.text(0))

    def name_save_name_json(self):
        self.file_save(os.path.join('database', 'name_base.json'), json.dumps(self.name_base))
        QMessageBox.information(self, "上传完成", '已经保存name_base')

    def name_save_and_upload_name_json(self):
        self.name_initial_name_base()
        self.file_save(os.path.join('database', 'name_base.json'), json.dumps(self.name_base))
        name_base_up = {'历史': self.name_base['历史']}
        self.upload_json('name_base.json', name_base_up)
        self.upload_json('图片链接.json', self.name_create_tree_list_name())
        self.upload_html('图片链接', self.name_create_js_list_name(self.name_create_tree_list_name()))
        QMessageBox.information(self, "上传完成", '已经保存并上传name_base')

    def name_delete_one_old_name(self):
        targeti = self.namelayout['历史曾用名']['布局']['树'][0].currentIndex().row()
        child = self.namelayout['历史曾用名']['布局']['树'][0].currentItem()
        if child == None:
            QMessageBox.critical(self, '错误', '您还没有点选需要删除的曾用名！')
        else:
            name = child.text(0)
            page_name = child.text(1)
            self.name_base['历史'].pop(targeti)
            self.name_initial_name_base()
            QMessageBox.information(self, "删除完成", '已经删除对应的【' + name + '】→【' + page_name + '】')

    def name_create_tree_list_name(self):
        redict = {}
        for i in self.name_base:
            if i != '历史':
                for j in self.name_base[i]:
                    if j['名称'] not in redict:
                        redict[j['名称']] = []
                    redict[j['名称']].append([j['页面名'], j['图片'], j['迷你图片']])
        i = '历史'
        for j in self.name_base[i]:
            if j['名称'] not in redict:
                redict[j['名称']] = []
            redict[j['名称']].append([j['页面名'], j['图片'], j['迷你图片']])
        return redict

    def reversed_name_create_tree_list_name(self):
        redict = {}
        for i in self.name_base:
            if i != '历史':
                for j in self.name_base[i]:
                    if j['页面名'] not in redict:
                        redict[j['页面名']] = []
                    redict[j['页面名']].append(j['名称'])
        i = '历史'
        for j in self.name_base[i]:
            if j['页面名'] not in redict:
                redict[j['页面名']] = []
            redict[j['页面名']].append(j['名称'])
        return redict

    def name_create_js_list_name(self, name_list):
        retxt = '<script>\nvar dota_json_image_link={'
        for i in name_list:
            v = name_list[i]
            retxt += '\n"' + i + '":['
            for j in v:
                retxt += '['
                for k in j:
                    retxt += '"' + k + '",'
                retxt += '],'
            retxt += '],'
        retxt += '};\n</script>'
        return retxt

    def entry_save_entry_json(self):
        self.entry_save_the_edit()
        self.file_save(os.path.join('database', 'entry_base.json'), json.dumps(self.entry_base))
        QMessageBox.information(self, "上传完成", '已经保存entry_base')

    def entry_save_and_upload_entry_json(self):
        self.entry_save_the_edit()
        self.entry_resort()
        self.entry_refresh_tree()
        self.file_save(os.path.join('database', 'entry_base.json'), json.dumps(self.entry_base))
        self.upload_json('entry_base.json', self.entry_base)
        QMessageBox.information(self, "上传完成", '已经整理好，保存并上传entry_base')

    def entry_save_the_edit(self):
        self.entry_base = {}
        for i in range(self.entrylayout['编辑区']['树'][0].topLevelItemCount()):
            item = self.entrylayout['编辑区']['树'][0].topLevelItem(i)
            name = item.text(0)
            self.entry_base[name] = {}
            self.entry_base[name]['链接'] = item.child(0).text(1)
            self.entry_base[name]['文字'] = item.child(1).text(1)
            for j in range(2, item.childCount()):
                child1 = item.child(j)
                self.entry_base[name][item.child(j).text(0)] = item.child(j).text(1)

    def entry_resort(self):
        temp = []
        p = Pinyin()
        for i in self.entry_base:
            temp.append([p.get_pinyin(i), i])
        temp = sorted(temp, key=lambda x: x[0])
        new_base = {}
        for i in temp:
            new_base[i[1]] = self.entry_base[i[1]]
        self.entry_base = new_base

    def entry_refresh_tree(self):
        self.entrylayout['编辑区']['树'][0].clear()
        p = Pinyin()
        for i in self.entry_base:
            tree1 = TreeItemEdit(self.entrylayout['编辑区']['树'][0], i)
            tree1.set_type('tree')
            tree1.setText(1, p.get_pinyin(i))
            tree2 = TreeItemEdit(tree1, '链接')
            tree2.set_type('text')
            tree2.set_value(self.entry_base[i]['链接'])
            tree3 = TreeItemEdit(tree1, '文字')
            tree3.set_type('text')
            tree3.set_value(self.entry_base[i]['文字'])
            for j in self.entry_base[i]:
                if j not in ['链接', '文字']:
                    tree4 = TreeItemEdit(tree1, j)
                    tree4.set_type('text')
                    tree4.set_value(self.entry_base[i][j])

    def entry_edit_new(self):
        text, ok = MoInputWindow.getText(self, '新增一个词汇', '请输入你想要的词汇的名称:', '')
        if ok:
            if text in self.entry_base:
                QMessageBox.critical(self, '您的输入有问题', '您输入的【' + text + '】已经存在于【词汇库】中，已为您跳转至改条目。')
                self.entrylayout['编辑区']['树'][0].setExpanded(False)
                for i in range(self.entrylayout['编辑区']['树'][0].topLevelItemCount()):
                    if self.entrylayout['编辑区']['树'][0].topLevelItem(i).text(0) == text:
                        self.entrylayout['编辑区']['树'][0].setCurrentIndex(i)
                        self.entrylayout['编辑区']['树'][0].topLevelItem(i).setExpanded(True)
            else:
                p = Pinyin()
                tree1 = TreeItemEdit(self.entrylayout['编辑区']['树'][0], text)
                tree1.set_type('tree')
                tree1.setText(1, p.get_pinyin(text))
                tree2 = TreeItemEdit(tree1, '链接')
                tree2.set_type('text')
                tree3 = TreeItemEdit(tree1, '文字')
                tree3.set_type('text')
                tree1.setExpanded(True)

    def entry_edit_delete(self):
        item = self.entrylayout['编辑区']['树'][0].currentItem()
        if item.itemtype == 'tree':
            clickb = QMessageBox.critical(self, '删除一组词汇', '您正试图删除【' + item.text(0) + '】这条词汇！', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if clickb == QMessageBox.Yes:
                self.entrylayout['编辑区']['树'][0].takeTopLevelItem(self.entrylayout['编辑区']['树'][0].indexOfTopLevelItem(item))
        elif item.parent().indexOfChild(item) > 1:
            clickb = QMessageBox.critical(self, '删除一组文字', '您正试图删除【' + item.parent().text(0) + '】这条词汇的【' + item.text(0) + '】！', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if clickb == QMessageBox.Yes:
                item.parent().removeChild(item)

    def entry_edit_change_name(self):
        item = self.entrylayout['编辑区']['树'][0].currentItem()
        if item.itemtype == 'text':
            index = item.parent().indexOfChild(item)
            if index > 1:
                text, ok = MoInputWindow.getText(self, '修改值', '您想将【' + item.text(0) + '】其修改为:', item.text(0))
                if ok:
                    item.setText(0, text)

    def entry_edit_change_value(self, expand=False):
        item = self.entrylayout['编辑区']['树'][0].currentItem()
        if item.itemtype == 'tree':
            text, ok = MoInputWindow.getText(self, '修改值', '您想增加一个条目:', '文字' + str(item.childCount()))
            if ok:
                new = TreeItemEdit(item, text)
                new.set_type('text')
                item.setExpanded(expand)
        elif item.itemtype == 'text':
            text, ok = MoInputWindow.getText(self, '修改值', '您想将【' + item.text(1) + '】修改为:', item.text(1))
            if ok:
                item.set_value(text)

    def entry_key_function(self, event):
        item = self.entrylayout['编辑区']['树'][0].currentItem()
        index = 0
        len = 0
        if item.itemtype == 'text':
            parent = item.parent()
            index = parent.indexOfChild(item)
            len = parent.childCount()
        if event.key() in [Qt.Key_S, Qt.Key_Down]:
            if index > 1 and index < len - 1:
                parent.removeChild(item)
                parent.insertChild(index + 1, item)
                self.entrylayout['编辑区']['树'][0].setCurrentItem(item)
        elif event.key() in [Qt.Key_W, Qt.Key_Up]:
            if index > 2:
                parent.removeChild(item)
                parent.insertChild(index - 1, item)
                self.entrylayout['编辑区']['树'][0].setCurrentItem(item)
        elif event.key() in [Qt.Key_F, Qt.Key_Enter]:
            self.entry_edit_change_value(True)
        elif event.key() in [Qt.Key_Escape, Qt.Key_Backspace]:
            self.entry_edit_delete()
        elif event.key() in [Qt.Key_A, Qt.Key_N, Qt.Key_Space]:
            self.entry_edit_change_name()

    def test_inputwindow(self):
        for i in self.json_base['非英雄单位']:
            v = self.json_base['非英雄单位'][i]
            for j in ['英雄攻击伤害', '非英雄攻击伤害']:
                w = v[j]
                if '1' in w and str(w['1']['1']) == '0' and '2' not in w and '2' not in w['1']:
                    w.pop('1')

    def test_inputwindow_loop_check(self, json):
        for i in self.json_base['非英雄单位']:
            v = self.json_base['非英雄单位'][i]
            for j in ['英雄攻击伤害', '非英雄攻击伤害']:
                w = v[j]
                if '1' in w and w['1']['1'] == '0':
                    v.pop('1')

    def test_inputwindow_change_it(self, json):
        ii = 0
        while True:
            ii += 1
            i = str(ii)
            if i in json:
                if isinstance(json[i], dict) and '1' in json[i] and '0' in json[i]['1'] and json[i]['1']['0'] == '图片链接':
                    text = '{{H|' + json[i]['1']['2'] + '}}'
                    index = ii
                    pops = 0
                    if str(ii - 1) in json and isinstance(json[str(ii - 1)], str):
                        index = ii - 1
                        text = json[str(ii - 1)] + text
                        json.pop(str(ii))
                        pops += 1
                    if str(ii + 1) in json and isinstance(json[str(ii + 1)], str):
                        text += json[str(ii + 1)]
                        json.pop(str(ii + 1))
                        pops += 1
                    json[str(index)] = text
                    if pops > 0:
                        jj = index + pops
                        while True:
                            jj += 1
                            j = str(jj)
                            if j in json:
                                json[str(jj - pops)] = json[j]
                                json.pop(j)
                            else:
                                break
            else:
                break


class upload_text(QWidget):
    def __init__(self, first_txt):
        super().__init__()
        self.b = QTextBrowser(self)
        self.l = QVBoxLayout()
        self.l.addWidget(self.b)
        self.setLayout(self.l)
        self.success = [0, 0, 0]
        thread = threading.Thread(target=self.addtext, args=([first_txt, 0],))
        thread.start()
        self.show()

    def confirm_numbers(self, num):
        self.maxmax = num

    def add_info_text(self, content):
        self.b.append('【' + QTime.currentTime().toString() + '】' + content)
        self.cursor = self.b.textCursor()
        self.b.moveCursor(self.b.textCursor().End)

    def addtext(self, content=['', 0], num=-1, threads=''):
        self.success[content[1]] += 1
        txts = '【' + QTime.currentTime().toString() + '】'
        if num > -1:
            txts += '【' + str(num + 1) + '[' + str(self.success[1]) + ']/' + str(self.maxmax) + ',' + '{:.2%}'.format(
                (num + 1) / self.maxmax) + '[' + '{:.2%}'.format(
                self.success[1] / self.maxmax) + ']】'
        if threads != '':
            txts += '【' + threads + '】'
        txts += content[0]
        self.b.append(txts)
        self.cursor = self.b.textCursor()
        self.b.moveCursor(self.b.textCursor().End)


class TreeItemEdit(QTreeWidgetItem):
    def __init__(self, *args):
        super().__init__(args[0])
        self.itemvalue = ''
        self.itemtype = ''
        self.hasvalue = False  # 是否有值
        self.haslist = False  # 下属有没有list
        self.listtype = []  # 下属list的形式
        self.tree_or_text = False  # 下一个混合文字是文字还是代码
        self.islist = False  # 是不是list
        self.israndom = False
        self.setText(0, args[1])

    def set_type(self, t):
        self.itemtype = t

    def set_value(self, v):
        self.itemvalue = v
        self.setText(1, str(v))
        self.hasvalue = True

    def delete_value(self):
        self.itemvalue = ''
        self.setText(1, '')
        self.hasvalue = False

    def set_kid_list(self, l):
        self.haslist = True
        self.listtype = copy.deepcopy(l)
        self.listtype[3] = 0


class VersionItemEdit(QTreeWidgetItem):
    def __init__(self, *args):
        super().__init__(args[0])
        self.itemvalue = ''
        self.itemtype = ''
        self.hasvalue = False  # 可不可以修改
        self.list = []

    def set_value(self, text=''):
        self.hasvalue = True
        self.itemvalue = text
        if text == 'None':
            self.setText(1, '')
        else:
            self.setText(1, str(text))

    def set_list(self, ll):
        self.list = copy.deepcopy(ll)
        self.setText(1, str(self.list))


class MoInputWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen_rect = QApplication.desktop().screenGeometry()
        self.screen_size = [screen_rect.width(), screen_rect.height()]
        self.icon = QIcon(os.path.join('material_lib', 'DOTA2.jpg'))
        self.setWindowIcon(self.icon)
        self.layout = {"0": QVBoxLayout()}
        self.setLayout(self.layout["0"])
        self.layout["输入区域"] = {"0": QVBoxLayout()}
        self.layout["0"].addLayout(self.layout["输入区域"]["0"])
        self.layout["按钮区域"] = {"0": QHBoxLayout()}
        self.layout["0"].addLayout(self.layout["按钮区域"]["0"])
        self.layout["按钮区域"]["0"].addStretch(1)
        self.layout["按钮区域"]["确认"] = QPushButton("确认修改", self)
        self.layout["按钮区域"]["0"].addWidget(self.layout["按钮区域"]["确认"])
        self.layout["按钮区域"]["确认"].clicked.connect(self.accept)
        self.layout["按钮区域"]["取消"] = QPushButton("放弃修改", self)
        self.layout["按钮区域"]["0"].addWidget(self.layout["按钮区域"]["取消"])
        self.layout["按钮区域"]["取消"].clicked.connect(self.reject)

    @staticmethod
    def getText(parent=None, title='输入文字', tip_str='输入', default_text=''):
        dialog = MoInputWindow(parent)
        dialog.setWindowTitle(title)
        dialog.setGeometry(dialog.screen_size[0] * 0.3, dialog.screen_size[1] * 0.3, dialog.screen_size[0] * 0.4,
                           dialog.screen_size[1] * 0.4)
        dialog.s = QLabel(dialog)
        dialog.s.setText(tip_str + '：')
        dialog.layout["输入区域"]["0"].addWidget(dialog.s)
        dialog.b = QTextEdit(dialog)
        dialog.b.setPlainText(default_text)
        dialog.b.setFocus()
        dialog.b.selectAll()
        dialog.layout["输入区域"]["0"].addWidget(dialog.b)
        result = dialog.exec_()
        return dialog.b.toPlainText(), result

    @staticmethod
    def getNumber(parent=None, title='输入数字', tip_str='输入', default_text=0):
        dialog = MoInputWindow(parent)
        dialog.setWindowTitle(title)
        dialog.setGeometry(dialog.screen_size[0] * 0.45, dialog.screen_size[1] * 0.45, dialog.screen_size[0] * 0.1,
                           dialog.screen_size[1] * 0.1)
        dialog.s = QLabel(dialog)
        dialog.s.setText(tip_str + '：')
        dialog.layout["输入区域"]["0"].addWidget(dialog.s)
        dialog.b = QLineEdit(dialog)
        dialog.b.setText(str(default_text))
        dialog.b.setFocus()
        dialog.b.selectAll()
        dialog.layout["输入区域"]["0"].addWidget(dialog.b)
        while True:
            result = dialog.exec_()
            if result:
                try:
                    re = float(dialog.b.text())
                    if float(int(re)) == re:
                        return int(re), result
                    else:
                        return re, result
                except ValueError:
                    QMessageBox.critical(dialog, '输入格式错误', '您应当输入一串数字！')
            else:
                return 0, False

    @staticmethod
    def getInt(parent=None, title='输入整数', tip_str='输入', default_text=0):
        dialog = MoInputWindow(parent)
        dialog.setWindowTitle(title)
        dialog.setGeometry(dialog.screen_size[0] * 0.45, dialog.screen_size[1] * 0.45, dialog.screen_size[0] * 0.1,
                           dialog.screen_size[1] * 0.1)
        dialog.s = QLabel(dialog)
        dialog.s.setText(tip_str + '：')
        dialog.layout["输入区域"]["0"].addWidget(dialog.s)
        dialog.b = QLineEdit(dialog)
        dialog.b.setText(str(default_text))
        dialog.b.setFocus()
        dialog.b.selectAll()
        dialog.layout["输入区域"]["0"].addWidget(dialog.b)
        while True:
            result = dialog.exec_()
            if result:
                try:
                    re = int(dialog.b.text())
                    return re, result
                except ValueError:
                    QMessageBox.critical(dialog, '输入格式错误', '您应当输入一串整数！')
            else:
                return 0, False

    @staticmethod
    def getItem(parent=None, title='做选择', tip_str='您将选择', iterable=[]):
        dialog = MoInputWindow(parent)
        dialog.setWindowTitle(title)
        lenth = max(1, math.floor(math.sqrt(len(iterable) / 3)))
        dialog.setGeometry(dialog.screen_size[0] * (0.5 - 0.05 * lenth), dialog.screen_size[1] * (0.5 - 0.05 * lenth), dialog.screen_size[0] * 0.1 * lenth,
                           dialog.screen_size[1] * 0.1 * lenth)
        dialog.s = QLabel(dialog)
        dialog.s.setText(tip_str + '：')
        dialog.layout["输入区域"]["0"].addWidget(dialog.s)
        dialog.g = QGridLayout(dialog)
        dialog.layout["输入区域"]["0"].addLayout(dialog.g)
        selects = []
        for i in range(len(iterable)):
            selects.append(QRadioButton(dialog))
            selects[i].setText(str(iterable[i]))
            xx = math.floor(i / lenth)
            yy = i - xx * lenth
            dialog.g.addWidget(selects[i], xx, yy)
        selects[0].setChecked(True)
        result = dialog.exec_()
        re = ''
        for i in selects:
            if i.isChecked():
                re = i.text()
                break
        return re, result

    @staticmethod
    def get_item_and_content(parent=None, title='选择后输入内容', tip_str='选择并输入', iterable=[], style=[], check=True):
        dialog = MoInputWindow(parent)
        dialog.setWindowTitle(title)
        dialog.setGeometry(dialog.screen_size[0] * 0.4, dialog.screen_size[1] * 0.4, dialog.screen_size[0] * 0.2,
                           dialog.screen_size[1] * 0.2)
        dialog.s = QLabel(dialog)
        dialog.s.setText(tip_str + '：')
        dialog.layout["输入区域"]["0"].addWidget(dialog.s)
        selects = []
        for i in range(len(iterable)):
            selects.append(QRadioButton(dialog))
            selects[i].setText(str(iterable[i]))
            dialog.layout["输入区域"]["0"].addWidget(selects[i])
        selects[0].setChecked(True)
        dialog.b = QTextEdit(dialog)
        dialog.b.setFocus()
        dialog.b.selectAll()
        dialog.layout["输入区域"]["0"].addWidget(dialog.b)
        while True:
            ii = 0
            styles = []
            for i in range(len(iterable)):
                if len(style) <= i:
                    if len(style) > 0:
                        styles.append(style[0])
                    else:
                        styles.append('text')
                else:
                    styles.append(style[i])
            result = dialog.exec_()
            for i in range(len(selects)):
                if selects[i].isChecked():
                    ii = i
                    break
            if result:
                if check and styles[ii] == 'int':
                    try:
                        re = int(dialog.b.toPlainText())
                        return iterable[ii], re, result
                    except ValueError:
                        QMessageBox.critical(dialog, '输入格式错误', '您应当输入一串整数！')
                elif check and styles[ii] == 'number':
                    try:
                        re = float(dialog.b.toPlainText())
                        return iterable[ii], re, result
                    except ValueError:
                        QMessageBox.critical(dialog, '输入格式错误', '您应当输入一串数字！')
                else:
                    return iterable[ii], dialog.b.toPlainText(), result
            else:
                return '不选择', '', False
