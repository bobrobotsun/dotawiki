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
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from text_to_json import hero, ability, item, unit, edit_json, dota_menus, page, common_page
import win32con
import win32clipboard as wincld


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initParam()
        self.initUI()

    def initParam(self):
        self.version = '7.27d'
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
        # 登录用的账号密码
        self.login_file_name = os.path.join('database', 'login.json')
        # 图标
        self.icon = QIcon(os.path.join('material_lib', 'DOTA2.jpg'))
        # 数据库信息
        self.text_base = {"英雄": {}, "非英雄单位": {}, "物品": {}, "技能": {}}
        self.json_base = {"英雄": {}, "非英雄单位": {}, "物品": {}, "技能": {}, '技能源': {}}
        self.json_name = {"英雄": [], "非英雄单位": [], "物品": [], "技能": [], '技能源': []}
        self.upgrade_base = {}
        self.mech = {}
        self.red = QBrush(Qt.red)
        self.green = QBrush(Qt.green)
        # 版本更新的内容
        self.version_list = {}
        self.version_base = {}

    def initUI(self):
        # 设定软件的图标
        self.setWindowIcon(self.icon)
        # 设定窗口大小、位置至0.8倍屏幕长宽，且边缘为0.1倍长宽
        self.setGeometry(self.screen_size[0] * 0.05, self.screen_size[1] * 0.1, self.screen_size[0] * 0.9, self.screen_size[1] * 0.8)
        # 创建一个菜单栏
        self.create_menubar()
        self.main_layout()
        self.checklogin()
        self.show()
        self.load_data()
        self.check_test()
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
        # 获取登录令牌
        login_token = self.seesion.post(self.target_url, data=self.get_login_token_data)
        # 使用登录令牌登录
        self.login_data['username'] = password['用户名']
        self.login_data['password'] = password['密码']
        self.login_data['logintoken'] = login_token.json()['query']['tokens']['logintoken']
        login_info = self.seesion.post(self.target_url, data=self.login_data)
        # 判断登录效果
        if login_info.json()["clientlogin"]["status"] == "FAIL":
            messageBox = QMessageBox(QMessageBox.Critical, "登录失败", login_info.json()["clientlogin"]["message"] + "\n请问是否重新登录？", QMessageBox.NoButton, self)
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
        else:
            self.csrf_token = self.seesion.post(self.target_url, data=self.get_csrf_token_data).json()['query']['tokens']['csrftoken']
            self.login_success(True, username=login_info.json()["clientlogin"]["username"], password=password['密码'])
            if window:
                kwargs['window'].close()

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
        logout_info = self.seesion.post(self.target_url, data=self.logout_data)
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
        self.mainlayout['加载信息']['信息'][0].addStretch(1)
        self.mainlayout['加载信息']['信息']['英雄'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['英雄'].setText('【英雄】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['英雄'])
        self.mainlayout['加载信息']['信息'][0].addStretch(2)
        self.mainlayout['加载信息']['信息']['非英雄单位'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['非英雄单位'].setText('【非英雄单位】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['非英雄单位'])
        self.mainlayout['加载信息']['信息'][0].addStretch(2)
        self.mainlayout['加载信息']['信息']['技能'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['技能'].setText('【技能】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['技能'])
        self.mainlayout['加载信息']['信息'][0].addStretch(2)
        self.mainlayout['加载信息']['信息']['技能源'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['技能源'].setText('【技能源】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['技能源'])
        self.mainlayout['加载信息']['信息'][0].addStretch(2)
        self.mainlayout['加载信息']['信息']['物品'] = QLabel(self)
        self.mainlayout['加载信息']['信息']['物品'].setText('【物品】')
        self.mainlayout['加载信息']['信息'][0].addWidget(self.mainlayout['加载信息']['信息']['物品'])
        self.mainlayout['加载信息']['信息'][0].addStretch(1)

        self.mainlayout['加载按钮'] = {0: QHBoxLayout()}
        self.mainlayout[0].addLayout(self.mainlayout['加载按钮'][0])
        self.mainlayout['加载按钮']['重新加载数据'] = QPushButton('重新加载数据', self)
        self.mainlayout['加载按钮']['重新加载数据'].clicked.connect(self.load_data)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['重新加载数据'])
        self.mainlayout['加载按钮']['重新读取DOTA2文件'] = QPushButton('重新读取DOTA2文件', self)
        self.mainlayout['加载按钮']['重新读取DOTA2文件'].clicked.connect(self.get_data_from_text)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['重新读取DOTA2文件'])
        self.mainlayout['加载按钮']['从wiki重新下载基础数据'] = QPushButton('从wiki重新下载基础数据', self)
        self.mainlayout['加载按钮']['从wiki重新下载基础数据'].clicked.connect(self.download_text_base)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载基础数据'])
        self.mainlayout['加载按钮']['从wiki重新下载合成数据'] = QPushButton('从wiki重新下载合成数据', self)
        self.mainlayout['加载按钮']['从wiki重新下载合成数据'].clicked.connect(self.download_json_base)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载合成数据'])
        self.mainlayout['加载按钮']['从wiki重新下载合成数据列表'] = QPushButton('从wiki重新下载合成数据列表', self)
        self.mainlayout['加载按钮']['从wiki重新下载合成数据列表'].clicked.connect(self.download_json_name)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载合成数据列表'])
        self.mainlayout['加载按钮']['从wiki重新下载机制定义'] = QPushButton('从wiki重新下载机制定义', self)
        self.mainlayout['加载按钮']['从wiki重新下载机制定义'].clicked.connect(self.download_mech)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['从wiki重新下载机制定义'])
        self.mainlayout['加载按钮']['将wiki目录进行更新（不要乱点）'] = QPushButton('将wiki目录进行更新（不要乱点）', self)
        self.mainlayout['加载按钮']['将wiki目录进行更新（不要乱点）'].clicked.connect(self.download_and_upload_wiki_menu)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['将wiki目录进行更新（不要乱点）'])
        self.mainlayout['加载按钮']['更新独立的页面（不要乱点）'] = QPushButton('更新独立的页面（不要乱点）', self)
        self.mainlayout['加载按钮']['更新独立的页面（不要乱点）'].clicked.connect(self.download_and_upload_single_pages)
        self.mainlayout['加载按钮'][0].addWidget(self.mainlayout['加载按钮']['更新独立的页面（不要乱点）'])
        self.mainlayout['加载按钮'][0].addStretch(1)

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
            self.fix_window_with_json_data()
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

    def get_data_from_text(self):
        try:
            basefile = open(os.path.join('database', 'dota2_address.json'), mode="r", encoding="utf-8")
            address = basefile.read()
            basefile.close()
            self.catch_file_from_dota2(address)
        except FileNotFoundError:
            self.find_dota2_folder()

    def find_dota2_folder(self):
        folders = ['steamapps', 'common', 'dota 2 beta', 'game', 'dota', 'scripts', 'npc']
        nowaddress = QFileDialog.getExistingDirectory(self, '请选择Steam的安装路径（使用完美启动器的用户请选择DOTA2目录下的steam文件夹）', '/home')
        for i in range(len(folders)):
            if folders[i] in os.listdir(nowaddress):
                nowaddress = os.path.join(nowaddress, folders[i])
            else:
                messageBox = QMessageBox(QMessageBox.Critical, '错误的路径', '您选择的路径下的' + nowaddress + '没有发现文件夹' + folders[i] + '\n请问是否重新重新选择Steam的安装路径？', QMessageBox.NoButton, self)
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

    def catch_file_from_dota2(self, address):
        has_text = [['英雄', '技能', '非英雄单位', '物品'],
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
        ttt += '\n已经从vpk处提取物品文件'
        if has_text[2][0] or has_text[2][1] or has_text[2][2]:
            if has_text[2][0]:
                hero.get_hero_data_from_txt(self.text_base['英雄'], os.path.join(address, has_text[1][0]))
            if has_text[2][1]:
                ability.get_hero_data_from_txt(self.text_base['技能'], os.path.join(address, has_text[1][1]))
            if has_text[2][2]:
                unit.get_hero_data_from_txt(self.text_base['非英雄单位'], os.path.join(address, has_text[1][2]))
            pak1 = vpk.open(address.replace('scripts\\npc', "pak01_dir.vpk"))
            pakfile = pak1.get_file("scripts/npc/items.txt")
            item.get_hero_data_from_txt(self.text_base['物品'], pakfile)
            self.file_save(os.path.join('database', 'dota2_address.json'), address)
            self.file_save(os.path.join('database', 'text_base.json'), json.dumps(self.text_base))
            messagebox = QMessageBox(QMessageBox.Information, '文件抓取', ttt, QMessageBox.NoButton, self)
            messagebox.setStandardButtons(QMessageBox.Ok)
            messagebox.exec_()
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
        download_info = self.seesion.post(self.target_url, data=download_data)
        time.sleep(0.01)
        return download_info.json()['jsondata']

    def download_text_base(self):
        self.text_base = self.download_json('text_base.json')
        self.file_save(os.path.join('database', 'text_base.json'), json.dumps(self.text_base))

    def download_json_name(self):
        for i in self.json_name:
            temp = self.seesion.post(self.target_url, data={'action': 'parse', 'text': '{{#invoke:json|api_all_page_names|' + i + '}}', 'contentmodel': 'wikitext', 'prop': 'text',
                                                            'disablelimitreport': 'false', 'format': 'json'}).json()['parse']['text']['*']
            texttemp = re.sub('<.*?>', '', temp)[:-1]
            tempjson = json.loads(texttemp)
            self.json_name.update(tempjson)
        print(self.json_name)
        self.file_save(os.path.join('database', 'json_name.json'), json.dumps(self.json_name))

    def update_json_name(self, list):
        for i in list:
            for j in list[i]:
                if j not in self.json_name[i]:
                    self.json_name[i].append(j)

    def download_mech(self):
        self.mech = self.download_json('机制检索.json')
        self.file_save(os.path.join('database', 'mech.json'), json.dumps(self.mech))

    def download_and_upload_wiki_menu(self):
        wiki_result = self.seesion.post(self.target_url, data={'action': 'jsondata', 'title': '机制.json', 'format': 'json'}).json()
        wiki_menu = dota_menus.menu_init(wiki_result['jsondata'])
        for i in self.json_base['英雄']:
            wiki_menu['单位']['英雄'].append(i)

        for i in self.json_base['非英雄单位']:
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
        info_txt += page.ability_cast_point_and_backswing(self.seesion, self.json_base, self.csrf_token)
        info_txt += common_page.page_hero(self.seesion, self.json_base, self.version_base, self.csrf_token)
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
                    if i == '技能源':
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
                self.local.download_info = self.local.seesion.post(self.local.target_url, data=self.local.download_data)
                self.lock.acquire()
                if self.local.download_info.status_code == 200:
                    try:
                        self.local.jsons = self.local.download_info.json()
                    except Exception as xx:
                        print(self.download_json_list[self.local.current_num],
                              '：下载出现错误，原因为：' + str(xx))
                        continue
                    else:
                        if self.local.jsons['jsondata']['应用'] == 1:
                            self.json_base[self.download_json_list[self.local.current_num][0]][
                                self.download_json_list[self.local.current_num][1]] = self.local.jsons[
                                'jsondata']
                        else:
                            self.json_name[self.download_json_list[self.local.current_num][0]].pop(
                                self.json_name[self.download_json_list[self.local.current_num][0]].index(
                                    self.download_json_list[self.local.current_num][1]))
                        self.progress.addtext(['下载《' + self.download_json_list[self.local.current_num][2] + '》内容成功', 1],
                                              self.current_num[0], threading.current_thread().name)
                        self.current_num[0] += 1
                        break
                    finally:
                        time.sleep(0.02)
                        self.lock.release()
                else:
                    self.local.k += 1
                    time.sleep(self.local.k * 0.1)
                    if self.local.k >= 10:
                        print(self.download_json_list[self.local.current_num], '：下载出现错误，原因为：联网失败')
                        self.lock.release()
                        break
                    self.lock.release()
        self.lock.acquire()
        if (threading.activeCount() <= self.startactiveCount+1):
            self.file_save(os.path.join('database', 'json_base.json'), json.dumps(self.json_base))
            self.fix_window_with_json_data()
            self.progress.addtext(['下载完毕，已为您下载合成数据，并已保存。您可以关闭本窗口',0])
        self.lock.release()


    def fix_window_with_json_data(self):
        names = ['英雄', '非英雄单位', '技能', '技能源', '物品']
        for i in names:
            self.mainlayout['加载信息']['信息'][i].setText('【' + i + '】数据已加载' + str(len(self.json_base[i])) + '个')
            self.mainlayout['列表'][i]['布局']['列表'].clear()
            for j in self.json_base[i]:
                self.mainlayout['列表'][i]['布局']['列表'].addItem(j)

    # 以下是拥有bot权限的用户在开启软件后才能使用的内容

    # 如果开启软件后未登陆，请在登录了有bot（机器人）权限的账户后重启使用
    def check_test(self):
        self.ml['高级功能'] = {0: self.ml[0].addMenu('高级功能')}
        self.ml['高级功能']['更新数据'] = self.ml['高级功能'][0].addAction('更新数据')
        self.ml['高级功能']['更新数据'].triggered.connect(lambda: self.update_json_base())
        self.ml['高级功能']['上传基础文件'] = self.ml['高级功能'][0].addAction('上传基础文件')
        self.ml['高级功能']['上传基础文件'].triggered.connect(self.upload_basic_json)
        self.ml['高级功能']['上传'] = self.ml['高级功能'][0].addAction('上传')
        self.ml['高级功能']['上传'].triggered.connect(lambda: self.upload_all())
        self.ml['高级功能']['上传统一页面'] = self.ml['高级功能'][0].addAction('上传统一页面')
        self.ml['高级功能']['上传统一页面'].triggered.connect(lambda: self.upload_common_page())
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
        self.ml['高级功能'][0].addSeparator()
        self.ml['高级功能']['上传所有同单位文件'] = self.ml['高级功能'][0].addAction('上传所有同单位文件')
        self.ml['高级功能']['上传所有同单位文件'].triggered.connect(lambda: self.upload_same_kind())
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
        self.editlayout['竖布局']['新增'].clicked.connect(self.json_edit_new)
        self.editlayout['竖布局']['下载更新'] = QPushButton('下载更新', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['下载更新'])
        self.editlayout['竖布局']['下载更新'].clicked.connect(self.json_edit_download)
        self.editlayout['竖布局']['删除'] = QPushButton('删除', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['删除'])
        self.editlayout['竖布局']['删除'].clicked.connect(self.json_edit_delete)
        self.editlayout['竖布局']['改名'] = QPushButton('改名', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['改名'])
        self.editlayout['竖布局']['改名'].clicked.connect(self.json_edit_change_name)
        self.editlayout['竖布局']['保存'] = QPushButton('保存', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['保存'])
        self.editlayout['竖布局']['保存'].clicked.connect(self.json_edit_save)
        self.editlayout['竖布局']['保存并上传'] = QPushButton('保存并上传', self)
        self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['保存并上传'])
        self.editlayout['竖布局']['保存并上传'].clicked.connect(self.json_edit_save_and_upload)
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
        self.editlayout['额外机制']['竖布局']['树'] = {0: QTreeWidget(self)}
        self.editlayout['额外机制']['竖布局'][0].addWidget(self.editlayout['额外机制']['竖布局']['树'][0])
        self.editlayout['额外机制']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])
        self.dict_to_tree(self.editlayout['额外机制']['竖布局']['树'], self.mech)
        self.editlayout['额外机制']['竖布局']['树'][0].setColumnWidth(0, 150)
        self.editlayout['额外机制']['竖布局']['树'][0].expandAll()

        for i in edit_json.edit:
            self.editlayout['修改核心']['竖布局']['大分类'][0].addItem(i)
        self.editlayout['修改核心']['竖布局']['大分类'][0].activated.connect(self.edit_category_selected_changed)
        self.edit_category_selected_changed()
        self.editlayout['修改核心']['竖布局']['具体库'][0].activated.connect(lambda: self.edit_target_selected_changed())
        self.editlayout['修改核心']['竖布局']['代码库'][0].activated.connect(self.edit_text_base_selected_changed)
        self.editlayout['修改核心']['竖布局']['树'][0].clicked.connect(self.tree_item_clicked)
        self.editlayout['修改核心']['竖布局']['树'][0].doubleClicked.connect(self.tree_item_double_clicked)
        self.editlayout['基础数据']['竖布局']['树'][0].doubleClicked.connect(lambda: self.copy_text_from_tree(0))
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
        self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'] = QPushButton('加小分类', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'])
        self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].clicked.connect(self.version_button_tree1_add_tree2)
        self.versionlayout['版本内容']['横排版']['竖排版']['小分类改名'] = QPushButton('小分类改名', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['小分类改名'])
        self.versionlayout['版本内容']['横排版']['竖排版']['小分类改名'].clicked.connect(self.version_button_tree2_change_name)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'] = QPushButton('删除小分类', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'])
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'].clicked.connect(self.version_button_delete_tree_item)
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'] = QPushButton('加一条新条目', self)
        self.versionlayout['版本内容']['横排版']['竖排版'][0].addWidget(self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'])
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'].clicked.connect(self.version_button_tree2_add_tree_list)
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
        下面是重新排序的情况
        """
        self.resort()

    def resort(self):
        for i in self.text_base:
            self.text_base[i] = edit_json.sortedDictValues(self.text_base[i], False)
        for i in self.json_base:
            self.json_base[i] = edit_json.sortedDictValues(self.json_base[i], True)
            self.json_name[i] = edit_json.sortedList(self.json_name[i])
        self.version_base=edit_json.version_sort(self.version_base,self.version_list['版本'])
        self.file_save_all()

    def file_save_all(self):
        self.file_save(os.path.join('database', 'text_base.json'), json.dumps(self.text_base))
        self.file_save(os.path.join('database', 'json_base.json'), json.dumps(self.json_base))
        self.file_save(os.path.join('database', 'json_name.json'), json.dumps(self.json_name))

    def update_json_base(self, info="更新数据成功！\n您可以选择上传这些数据。"):
        self.resort()
        hero.fulfill_hero_json(self.text_base, self.json_base["英雄"], self.version)
        item.fulfill_item_json(self.text_base, self.json_base["物品"], self.version)

        info += ability.autoget_talent_source(self.json_base, self.text_base['英雄'])
        ability.get_source_to_data(self.json_base, self.upgrade_base, self.version)
        unit.fulfill_unit_json(self.text_base, self.json_base["非英雄单位"], self.version)

        ability.input_upgrade(self.json_base, self.upgrade_base)

        unit.complete_upgrade(self.json_base["非英雄单位"], self.text_base)
        ability.complete_upgrade(self.json_base["技能"], self.text_base)

        ability.complete_mech(self.json_base["技能"], self.mech)

        for i in self.json_base["技能"]:
            ability.loop_check(self.json_base["技能"][i], self.text_base, self.json_base, i)

        ability.confirm_upgrade_info(self.json_base['技能'])

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
                self.json_base[i][j]['技能'] = {}
                if self.json_base[i][j]['页面名'] in ability_own:
                    for k in range(len(ability_own[self.json_base[i][j]['页面名']])):
                        self.json_base[i][j]['技能'][str(k + 1)] = ability_own[self.json_base[i][j]['页面名']][k][0]

        self.resort()
        QMessageBox.information(self, "已完成", info)

    def upload_basic_json(self):
        self.upload_json('text_base.json', self.text_base)
        self.upload_json('json_name.json', self.json_name)
        QMessageBox.information(self, "上传完成", '已经上传完毕基础文件')

    def upload_all(self, chosen=''):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json中……')
        all_upload = []
        all_upload.append(['版本.json', {'版本': self.version}])
        all_upload.append(['text_base.json', self.text_base])
        all_upload.append(['json_name.json', self.json_name])
        if chosen == '':
            for i in self.json_base:
                for j in self.json_base[i]:
                    if i == '技能源':
                        all_upload.append([j + '/源.json', self.json_base[i][j]])
                    else:
                        all_upload.append([j + '.json', self.json_base[i][j]])
        else:
            i = chosen
            for j in self.json_base[i]:
                if i == '技能源':
                    all_upload.append([j + '/源.json', self.json_base[i][j]])
                else:
                    all_upload.append([j + '.json', self.json_base[i][j]])
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(total_num):
            self.w.addtext(self.upload_json(all_upload[i][0], all_upload[i][1], True), i)
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def upload_common_page(self):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传统一制作页面中……')
        QApplication.processEvents()
        all_upload = []
        for i in self.json_base['英雄']:
            all_upload.append([i, common_page.create_page_hero(self.json_base, self.version_base, self.version_list['版本'], i)])
            all_upload.append([i + '/版本改动', common_page.create_2nd_logs(self.json_base, self.version_base, self.version_list['版本'], i, 0)])
        for i in self.json_base['非英雄单位']:
            all_upload.append([i, common_page.create_page_unit(self.json_base, self.version_base, self.version_list['版本'], i)])
            all_upload.append([i + '/版本改动', common_page.create_2nd_logs(self.json_base, self.version_base, self.version_list['版本'], i, 0)])
        for i in self.json_base['物品']:
            all_upload.append([i, common_page.create_page_item(self.json_base, self.version_base, self.version_list['版本'], i)])
            all_upload.append([i + '/版本改动', common_page.create_2nd_logs(self.json_base, self.version_base, self.version_list['版本'], i, 0)])
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(total_num):
            self.w.addtext(self.upload_page(all_upload[i][0], all_upload[i][1], True), i)
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    def upload_same_kind(self):
        selected = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        selected_name = self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()
        target_name = []
        if selected == '技能':
            target_name = self.json_base[selected][selected_name]['技能归属']
        elif selected == '技能源':
            skill_name = selected_name
            for i in self.json_base['技能']:
                if self.json_base['技能'][i]['数据来源'] == skill_name:
                    target_name.append(self.json_base['技能'][i]['技能归属'])
        else:
            target_name.append(selected_name)
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json中……')
        QApplication.processEvents()
        all_upload = []
        if len(target_name) == 0:
            if selected == '技能源':
                all_upload.append([selected_name + '/源.json', self.json_base[selected][selected_name]])
            else:
                all_upload.append([selected_name + '.json', self.json_base[selected][selected_name]])
        else:
            for k in target_name:
                for i in self.json_base['技能']:
                    if self.json_base['技能'][i]['技能归属'] == k:
                        all_upload.append([i + '.json', self.json_base['技能'][i]])
                        j = self.json_base['技能'][i]['数据来源']
                        if j in self.json_base['技能源']:
                            all_upload.append([j + '/源.json', self.json_base['技能源'][j]])
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(total_num):
            self.w.addtext(self.upload_json(all_upload[i][0], all_upload[i][1], True), i)
            QApplication.processEvents()
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    # 向wiki网站上传对应的信息
    def upload_json(self, pagename, content, bot=False):
        download_data = {'action': 'jsondata', 'title': pagename, 'format': 'json'}
        k = 0
        while True:
            download_info = self.seesion.post(self.target_url, data=download_data)
            if download_info.status_code == 200:
                download_content = download_info.json()
                if 'jsondata' in download_content and self.check_dict_equal(download_content['jsondata'], content):
                    return ['《' + pagename + '》通过校验，不需要修改！', 0]
                break
            else:
                k += 1
                time.sleep(0.2)
                if k >= 5:
                    break
        pagename = 'Data:' + pagename
        content = json.dumps(content)
        upload_data = {'action': 'edit', 'title': pagename, 'text': content, 'format': 'json', 'token': self.csrf_token}
        if bot:
            upload_data['bot'] = 1
        k = 0
        while True:
            upload_info = self.seesion.post(self.target_url, data=upload_data)
            if upload_info.status_code == 200:
                upload_info_json = upload_info.json()
                break
            else:
                k += 1
                time.sleep(0.2)
                if k >= 5:
                    return ['《' + pagename + '》上传失败，请之后重新上传！', 10000]
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

    def upload_page(self, pagename, content, bot=False):
        download_data = {'action': 'parse', 'prop': 'wikitext', 'page': pagename, 'format': 'json'}
        k = 0
        while True:
            download_info = self.seesion.post(self.target_url, data=download_data)
            if download_info.status_code == 200:
                download_content = download_info.json()
                if 'error' in download_content:
                    break
                elif content == download_content['parse']['wikitext']['*']:
                    return ['《' + pagename + '》通过校验，不需要修改！', 0]
                break
            else:
                k += 1
                time.sleep(0.2)
                if k >= 5:
                    break
        upload_data = {'action': 'edit', 'title': pagename, 'text': content, 'format': 'json', 'token': self.csrf_token}
        if bot:
            upload_data['bot'] = 1
        k = 0
        while True:
            upload_info = self.seesion.post(self.target_url, data=upload_data)
            if upload_info.status_code == 200:
                upload_info_json = upload_info.json()
                break
            else:
                k += 1
                time.sleep(0.2)
                if k >= 5:
                    return ['《' + pagename + '》上传失败，请之后重新上传！', 10000]
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
                    if (isinstance(d1[i], int) or isinstance(d1[i], float)) and (isinstance(d2[i], int) or isinstance(d2[i], float)):
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
                    if isinstance(d1[i], int) or isinstance(d1[i], float) and isinstance(d2[i], int) or isinstance(d2[i], float):
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
        selected = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(), self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
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
        self.edit_json_expand_all()
        self.self_edit_button_default()

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

    def combine_text_to_tree(self, tdict, sdict):
        tdict['混合文字'] = {0: TreeItemEdit(tdict[0], '混合文字')}
        tdict['混合文字'][0].set_type('combine_tree')
        tdict['混合文字'][0].set_kid_list(['tree', {"后缀": ['text', ''], "list": ['tree', {"符号": ['text', ''], "list": ['text', '', 0, 3, False]}, 1, 1, False]}, 1, 0, False])
        for i in sdict['混合文字']:
            if isinstance(sdict['混合文字'][i], dict):
                tdict['混合文字'][i] = {0: TreeItemEdit(tdict['混合文字'][0], i)}
                tdict['混合文字'][i][0].set_type('tree')
                self.complex_dict_to_tree(tdict['混合文字'][i], {"后缀": ['text', ''], "list": ['tree', {"符号": ['text', ''], "list": ['text', '', 0, 3, False]}, 1, 1, False]},
                                          sdict['混合文字'][i])
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

    def json_edit_new(self):
        selected = self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        text, ok = MoInputWindow.getText(self, '新增一个' + selected, '请输入你想要的' + selected + '的名称:')
        if ok:
            self.update_json_name(self.download_json('json_name.json'))
            self.json_name[selected].append(text)
            self.json_base[selected][text] = {}
            for i in edit_json.edit[selected]:
                self.add_another_to_json(i, edit_json.edit[selected][i], self.json_base[selected][text])
            self.json_base[selected][text]['页面名'] = text
            self.resort()
            self.upload_json('json_name.json', self.json_name)
            self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(selected)
            self.edit_category_selected_changed()
            self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(text)
            self.edit_target_selected_changed()

    def json_edit_download(self):
        ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(), self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
        if ss[0] == '技能源':
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
            ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(), self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
            self.json_base[ss[0]][ss[1]]['应用'] = 0
            if ss[0] == '技能源':
                self.upload_json(ss[1] + '/源.json', self.json_base[ss[0]][ss[1]])
            else:
                self.upload_json(ss[1] + '.json', self.json_base[ss[0]][ss[1]])
            self.json_base[ss[0]].pop(ss[1])
            self.json_name[ss[0]].pop(self.json_name[ss[0]].index(ss[1]))
            self.resort()
            self.upload_json('json_name.json', self.json_name)
            self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(ss[0])
            self.edit_category_selected_changed()
            self.upload_json('json_name.json', self.json_name)
            QMessageBox.information(self, '删除完毕', '删除成功！您将不会再看到这个库。')

    def json_edit_change_name(self):
        warning = QMessageBox.warning(self, '改名', '您正改变库的名字，这个操作将会难以撤销。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if warning == QMessageBox.Yes:
            ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(), self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
            text, ok = MoInputWindow.getText(self, '修改名字', '您希望将' + ss[1] + '的名字改为:')
            if ok:
                self.update_json_name(self.download_json('json_name.json'))
                self.json_base[ss[0]][text] = copy.deepcopy(self.json_base[ss[0]][ss[1]])
                self.json_base[ss[0]][ss[1]]['应用'] = '改名'
                if ss[0] == '技能源':
                    self.upload_json(ss[1] + '/源.json', self.json_base[ss[0]][ss[1]])
                else:
                    self.upload_json(ss[1] + '.json', self.json_base[ss[0]][ss[1]])
                self.json_base[ss[0]].pop(ss[1])
                self.json_name[ss[0]].pop(self.json_name[ss[0]].index(ss[1]))
                self.json_name[ss[0]].append(text)
                self.resort()
                self.upload_json('json_name.json', self.json_name)
                self.editlayout['修改核心']['竖布局']['大分类'][0].setCurrentText(ss[0])
                self.edit_category_selected_changed()
                self.editlayout['修改核心']['竖布局']['具体库'][0].setCurrentText(text)
                self.edit_target_selected_changed()
                QMessageBox.information(self, '改名完毕', '库【' + ss[1] + '】已经被改名为【' + text + '】\n请记得保存后上传')

    def json_edit_save(self):
        ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(), self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
        self.json_base[ss[0]][ss[1]] = {}
        self.read_tree_to_json(self.editlayout['修改核心']['竖布局']['树'][0], self.json_base[ss[0]][ss[1]])
        self.file_save_all()
        self.update_json_base(info='已经保存更改并更新完毕\n您可以选择统一上传或继续编辑。')
        self.edit_target_selected_changed()

    def json_edit_save_and_upload(self):
        ss = [self.editlayout['修改核心']['竖布局']['大分类'][0].currentText(), self.editlayout['修改核心']['竖布局']['具体库'][0].currentText()]
        self.json_base[ss[0]][ss[1]] = {}
        self.read_tree_to_json(self.editlayout['修改核心']['竖布局']['树'][0], self.json_base[ss[0]][ss[1]])
        self.file_save_all()
        self.update_json_base(info='已经保存并更新完毕\n确认后会上传本次修改内容\n如果您的修改影响了其他库内容，请之后进行一次统一更新。')
        if ss[0] == '技能源':
            self.upload_json(ss[1] + '/源.json', self.json_base[ss[0]][ss[1]])
        else:
            self.upload_json(ss[1] + '.json', self.json_base[ss[0]][ss[1]])
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
            time.sleep(0.1)
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
        self.editlayout['竖布局']['转换为混合文字'].setEnabled(sender.itemtype == 'text' and sender.childCount() == 0 and not sender.israndom)
        self.editlayout['竖布局']['转换为普通文字'].setEnabled(sender.itemtype == 'text' and sender.childCount() > 0 and not sender.israndom)

        self.editlayout['竖布局']['传统目标设定'].setEnabled(sender.text(0) == '不分类' or sender.text(0) == '英雄' or sender.text(0) == '非英雄')

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
                temp[0].setExpanded(True)
            else:
                temp = TreeItemEdit(item, i)
                temp.set_type(item.listtype[0])
                temp.set_value(sdict[i])
                temp.islist = True
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
        item.delete_value()
        temp = TreeItemEdit(item, '混合文字')
        temp.set_type('combine_tree')
        temp.set_kid_list(['tree', {"后缀": ['text', ''], "list": ['tree', {"符号": ['text', ''], "list": ['text', '', 0, 4, False]}, 1, 1, False]}, 1, 0, False])
        self.tree_item_clicked()
        item.setExpanded(True)

    def json_edit_combine_to_text(self):
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
        for i in range(tree.topLevelItemCount()):
            self.read_tree_item_to_json(tree.topLevelItem(i), sdict)

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
        index = self.versionlayout['版本列表']['横排版']['列表'].indexOfTopLevelItem(self.versionlayout['版本列表']['横排版']['列表'].currentItem())
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
                    self.version_list['版本'][i].append(self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).child(j).text(0))

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
                    self.version_list['版本'][i].append(self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).child(j).text(0))
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
            messageBox = QMessageBox(QMessageBox.Critical, "获取数据失败", "您没有这个版本更新的库，请问您准备从哪里获取？", QMessageBox.NoButton, self)
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
        download_info = self.seesion.post(self.target_url, data=download_data)
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
        self.w.setGeometry(self.screen_size[0] * 0.2, self.screen_size[1] * 0.15, self.screen_size[0] * 0.6, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json中……')
        self.w.confirm_numbers(len(self.version_list['版本']))
        for i in range(len(self.version_list['版本'])):
            for j in range(len(self.version_list['版本'][i])):
                if j == 0:
                    title = self.version_list['版本'][i][j]
                else:
                    title = self.version_list['版本'][i][0] + '/' + self.version_list['版本'][i][j]
                download_data = {'action': 'jsondata', 'title': title + '.json', 'format': 'json'}
                download_info = self.seesion.post(self.target_url, data=download_data)
                if 'error' in download_info.json() and download_info.json()['error']['code'] == 'invalidtitle':
                    self.w.addtext([self.version_list['版本'][i][j] + '版本json不存在。', 0], i)
                    QApplication.processEvents()
                    time.sleep(0.1)
                else:
                    self.version_base[title] = download_info.json()['jsondata']
                    if j == 0:
                        self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).setBackground(0, self.green)
                    else:
                        self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i).child(j - 1).setBackground(0, self.green)
                    self.w.addtext([title + '版本json下载保存成功。', 1], i)
                    QApplication.processEvents()
                    time.sleep(0.1)
        self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
        QMessageBox.information(self, '下载成功', '所有版本号已经下载并保存完毕。')

    def version_edit_loop_update(self):
        for i in range(self.versionlayout['版本列表']['横排版']['列表'].topLevelItemCount()):
            topitem = self.versionlayout['版本列表']['横排版']['列表'].topLevelItem(i)
            if topitem.background(0) == self.green:
                self.versionlayout['版本列表']['横排版']['列表'].setCurrentItem(topitem)
                self.check_version_content()
                self.upload_one_version(False)
                time.sleep(0.1)
                QApplication.processEvents()
                for j in range(topitem.childCount()):
                    item = topitem.child(j)
                    if item.background(0) == self.green:
                        self.versionlayout['版本列表']['横排版']['列表'].setCurrentItem(item)
                        self.check_version_content()
                        self.upload_one_version(False)
                        time.sleep(0.1)
                        QApplication.processEvents()

    def upload_one_version(self, bool=True):
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
                self.version_base[title][items.text(0)] = self.version_tree_to_json(items)
        if item.parent() == None:
            self.version_base[title]['次级版本'] = []
            for i in range(item.childCount()):
                self.version_base[title]['次级版本'].append(item.text(0) + '/' + item.child(i).text(0))
        self.upload_json(title + '.json', self.version_base[title])
        self.file_save(os.path.join('database', 'version_base.json'), json.dumps(self.version_base))
        if bool:
            self.complex_json_to_version_tree()
            QMessageBox.information(self, '上传成功', '版本信息已经更新保存完毕。')

    def version_tree_to_json(self, item):
        re = {}
        for i in range(item.childCount()):
            item1 = item.child(i)
            if i == 0:
                re[str(i)] = ['', '']
            else:
                re[str(i)] = [item1.text(0), item1.text(1)]
            for j in range(item1.childCount()):
                item2 = item1.child(j).child(1)
                item3 = item1.child(j).child(2)
                index = len(re[str(i)])
                re[str(i)].append({'序列级数': 1, '文字': [], '目标': []})
                item0 = item1.child(j).child(0)
                try:
                    re[str(i)][index]['序列级数'] = int(item0.itemvalue)
                except ValueError:
                    QMessageBox.critical(self, '错误的序列级数', '您的【' + item1.text(0) + '】中的【' + item1.child(j).text(0) + '】的第' + str(j) + '个序列级数不为正整数，请修改！')
                    while True:
                        text, ok = MoInputWindow.getInt(self, "序列级数", '请输入一个正整数，否则会报错')
                        if ok:
                            re[str(i)][index]['序列级数'] = text
                re[str(i)][index]['文字'] = item2.text(1)
                if re[str(i)][index]['文字'][2:5] == '级天赋':
                    temp = item1.text(0) + re[str(i)][index]['文字'][:5]
                    re[str(i)][index]['目标'].append(temp)
                    re[str(i)][index]['文字'] = re[str(i)][index]['文字'].replace(re[str(i)][index]['文字'][:5], '{{A|' + temp + '}}')
                for k in range(item3.childCount()):
                    item4 = item3.child(k)
                    re[str(i)][index]['目标'].append(item4.text(1))
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
                if i in self.version_base[title] and '0' in self.version_base[title][i]:
                    new1 = VersionItemEdit(self.versionlayout['版本内容']['横排版']['树'][0])
                    new1.itemtype = 'tree1'
                    new1.setText(0, i)
                    new1.setBackground(1, self.green)
                    for j in self.version_base[title][i]:
                        new2 = VersionItemEdit(new1)
                        new2.itemtype = 'tree2'
                        if self.version_base[title][i][j][0] == '':
                            new2.setText(0, '无标题')
                        else:
                            new2.setText(0, self.version_base[title][i][j][0])
                        new2.set_value(self.version_base[title][i][j][1])
                        for k in range(len(self.version_base[title][i][j])):
                            if k > 1:
                                new3 = VersionItemEdit(new2)
                                new3.itemtype = 'tree_list'
                                new3.setText(0, str(k - 1))
                                new0 = VersionItemEdit(new3)
                                new0.itemtype = 'text'
                                new0.setText(0, '序列级数')
                                if '序列级数' in self.version_base[title][i][j][k]:
                                    new0.set_value(self.version_base[title][i][j][k]['序列级数'])
                                else:
                                    new0.set_value(1)
                                new4 = VersionItemEdit(new3)
                                new4.itemtype = 'text'
                                new4.setText(0, '文字')
                                new4.set_value(self.version_base[title][i][j][k]['文字'])
                                new5 = VersionItemEdit(new3)
                                new5.itemtype = 'list'
                                new5.setText(0, '目标')
                                for l in self.version_base[title][i][j][k]['目标']:
                                    new6 = VersionItemEdit(new5)
                                    new6.itemtype = 'list_text'
                                    new6.set_value(l)
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
                self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].setEnabled(False)
            elif item.background(1) == self.green:
                self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setText('禁用大分类')
                self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].setEnabled(True)
            self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setEnabled(True)
        else:
            self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setText('大分类')
            self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setEnabled(False)
            self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['小分类改名'].setEnabled(item.itemtype == 'tree2')
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'].setEnabled(item.itemtype == 'tree2')
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'].setEnabled(item.itemtype == 'tree2')
        self.versionlayout['版本内容']['横排版']['竖排版']['向上移动题目'].setEnabled(item.itemtype == 'tree_list')
        self.versionlayout['版本内容']['横排版']['竖排版']['向下移动题目'].setEnabled(item.itemtype == 'tree_list')
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该条目'].setEnabled(item.itemtype == 'tree_list')
        self.versionlayout['版本内容']['横排版']['竖排版']['增加新目标'].setEnabled(item.itemtype == 'list')
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该目标'].setEnabled(item.itemtype == 'list_text')

    def version_edit_all_button_default(self):
        self.versionlayout['版本内容']['横排版']['竖排版']['修改内容'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setText('大分类')
        self.versionlayout['版本内容']['横排版']['竖排版']['大分类'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['加小分类'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['小分类改名'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除小分类'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['加一条新条目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['向上移动题目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['向下移动题目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该条目'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['增加新目标'].setEnabled(False)
        self.versionlayout['版本内容']['横排版']['竖排版']['删除该目标'].setEnabled(False)

    def version_item_double_clicked(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        if item.hasvalue:
            self.version_edit_change_value()

    def version_edit_change_value(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        ori_text = item.text(1)
        if item.parent() != None and item.parent().parent() != None:
            hero_text = item.parent().parent().text(0)
        ori_text = re.sub(r'[\(\)（）\[\]【】<>《》]', lambda x: '\\' + x.group(0), ori_text)
        text, ok = MoInputWindow.getText(self, '修改值', '您想将其修改为:', ori_text)
        if ok:
            text = re.sub(r'(?<!\\)[\(（](.+?)(?<!\\)[\)）]', lambda x: '{{H|' + x.group(1) + '}}', text)
            text = re.sub(r'(?<!\\)[\[【](.+?)(?<!\\)[\]】]', lambda x: '{{A|' + x.group(1) + '}}', text)
            text = re.sub(r'(?<!\\)[<《](.+?)(?<!\\)[>》]', lambda x: '{{I|' + x.group(1) + '}}', text)
            text = re.sub(r'\{\{A\|([0-9]+?)\}\}', lambda x: '{{A|' + hero_text + x.group(1) + '级天赋}}', text)
            text = re.sub(r'\\[\(\)（）\[\]【】<>《》]', lambda x: x.group(0)[1], text)
            item.set_value(text)
            if item.parent() != None:
                iparent = item.parent()
                icount = iparent.childCount()
                if iparent.child(icount - 1).text(0) == '目标':
                    ipattern = re.compile(r'{{[ahi]\|.+?}}', re.I)
                    iresult = ipattern.findall(text)
                    for i in iresult:
                        ibool = True
                        itarget = iparent.child(icount - 1)
                        for j in range(itarget.childCount()):
                            if itarget.child(j).text(1) == i[4:-2]:
                                ibool = False
                                break
                        if ibool:
                            new = VersionItemEdit(iparent.child(icount - 1))
                            new.itemtype = 'list_text'
                            new.set_value(i[4:-2])
                if item.parent() != None and item.parent().parent() != None:
                    ipp = item.parent().parent()
                    if ipp.itemtype == 'tree2' and ipp.child(ipp.childCount() - 1).child(1).text(1) != '':
                        self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(ipp)
                        self.version_button_tree2_add_tree_list()
                        self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(item)

    def version_button_tree1(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        if item.background(1) == self.red:
            new = VersionItemEdit(item)
            new.setText(0, '0')
            new.itemtype = 'tree2'
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
        text, ok = MoInputWindow.getText(self, '新增一个小分类', '请输入你想要增加的分类名称:')
        if ok:
            new = VersionItemEdit(item)
            new.setText(0, text)
            new.itemtype = 'tree2'
            item.setExpanded(True)
            self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(new)
            self.version_button_tree2_add_tree_list()
            new.setExpanded(False)
            self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(item)

    def version_button_tree2_change_name(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        parent = item.parent()
        text, ok = MoInputWindow.getText(self, '小分类改名', '你现在正试图将【' + parent.text(0) + '】的【' + item.text(0) + '】的名字改为:', item.text(0))
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
        for i in range(0, counts):
            parent.child(i).setText(0, str(i + 1))
        item.setExpanded(True)
        tree.setCurrentItem(item)
        self.version_edit_all_button_clicked()
        self.expand_all_childs(item)

    def version_button_delete_tree_item(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        parent = item.parent()
        parent.removeChild(item)
        self.versionlayout['版本内容']['横排版']['树'][0].setCurrentItem(parent)
        self.version_edit_all_button_clicked()

    def version_button_tree2_add_tree_list(self):
        item = self.versionlayout['版本内容']['横排版']['树'][0].currentItem()
        new3 = VersionItemEdit(item)
        new3.itemtype = 'tree_list'
        new3.setText(0, str(item.childCount()))
        new6 = VersionItemEdit(new3)
        new6.itemtype = 'text'
        new6.setText(0, '序列级数')
        new6.set_value('1')
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
                self.expand_all_childs(item.child(j))

    def expand_all_childs(self, item):
        for i in range(item.childCount()):
            item.child(i).setExpanded(True)
            self.expand_all_childs(item.child(i))

    def test_inputwindow(self):
        print(MoInputWindow.get_item_and_content(self, [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], ['int', 'number']))


class upload_text(QWidget):
    def __init__(self, first_txt):
        super().__init__()
        self.b = QTextBrowser(self)
        self.l = QVBoxLayout()
        self.l.addWidget(self.b)
        self.setLayout(self.l)
        self.success = [0, 0]
        thread = threading.Thread(target=self.addtext, args=([first_txt, 0],))
        thread.start()
        self.show()

    def confirm_numbers(self, num):
        self.maxmax = num

    def addtext(self, content=['', 0], num=-1, threads=''):
        self.success[content[1]] += 1
        txts = '【' + QTime.currentTime().toString() + '】'
        if num > -1:
            txts += '【' + str(num + 1) + '[' + str(self.success[1]) + ']/' + str(self.maxmax) + ',' + '{:.2%}'.format((num + 1) / self.maxmax) + '[' + '{:.2%}'.format(
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
        dialog.setGeometry(dialog.screen_size[0] * 0.3, dialog.screen_size[1] * 0.3, dialog.screen_size[0] * 0.4, dialog.screen_size[1] * 0.4)
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
        dialog.setGeometry(dialog.screen_size[0] * 0.45, dialog.screen_size[1] * 0.45, dialog.screen_size[0] * 0.1, dialog.screen_size[1] * 0.1)
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
        dialog.setGeometry(dialog.screen_size[0] * 0.45, dialog.screen_size[1] * 0.45, dialog.screen_size[0] * 0.1, dialog.screen_size[1] * 0.1)
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
        dialog.setGeometry(dialog.screen_size[0] * 0.45, dialog.screen_size[1] * 0.45, dialog.screen_size[0] * 0.1, dialog.screen_size[1] * 0.1)
        dialog.s = QLabel(dialog)
        dialog.s.setText(tip_str + '：')
        dialog.layout["输入区域"]["0"].addWidget(dialog.s)
        selects = []
        for i in range(len(iterable)):
            selects.append(QRadioButton(dialog))
            selects[i].setText(str(iterable[i]))
            dialog.layout["输入区域"]["0"].addWidget(selects[i])
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
        dialog.setGeometry(dialog.screen_size[0] * 0.4, dialog.screen_size[1] * 0.4, dialog.screen_size[0] * 0.2, dialog.screen_size[1] * 0.2)
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
