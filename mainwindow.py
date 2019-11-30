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
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from text_to_json import hero, ability, item, unit, edit_json


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initParam()
        self.initUI()

    def initParam(self):
        self.version = '7.23b'
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
            for i in
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
            self.json_base = edit_json.sortedDictValues(json.loads(basefile.read()))
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
                    [False, False, False, False]]
        ttt = ''
        for i in range(4):
            if i > 0:
                ttt += '\n'
            ttt += has_text[0][i] + '数据：'
            if has_text[1][i] in os.listdir(address):
                ttt += '文件存在，成功读取'
                has_text[2][i] = True
            else:
                ttt += has_text[1][i] + '文件不存在，读取失败'
        if has_text[2][0] and has_text[2][1] and has_text[2][2] and has_text[2][3]:
            messagebox = QMessageBox(QMessageBox.Information, '文件抓取', ttt, QMessageBox.NoButton, self)
            messagebox.setStandardButtons(QMessageBox.Ok)
            messagebox.button(QMessageBox.Ok).animateClick(1000)
            messagebox.exec_()
            if has_text[2][0]:
                hero.get_hero_data_from_txt(self.text_base['英雄'], os.path.join(address, has_text[1][0]))
            if has_text[2][1]:
                ability.get_hero_data_from_txt(self.text_base['技能'], os.path.join(address, has_text[1][1]))
            if has_text[2][2]:
                unit.get_hero_data_from_txt(self.text_base['非英雄单位'], os.path.join(address, has_text[1][2]))
            if has_text[2][3]:
                item.get_hero_data_from_txt(self.text_base['物品'], os.path.join(address, has_text[1][3]))
            self.file_save(os.path.join('database', 'dota2_address.json'), address)
            self.file_save(os.path.join('database', 'text_base.json'), json.dumps(self.text_base))
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
        self.json_name = self.download_json('json_name.json')
        self.file_save(os.path.join('database', 'json_name.json'), json.dumps(self.json_name))

    def download_mech(self):
        self.mech = self.download_json('机制检索.json')
        self.file_save(os.path.join('database', 'mech.json'), json.dumps(self.mech))

    def download_json_base(self):
        try:
            namefile = open(os.path.join('database', 'json_name.json'), mode="r", encoding="utf-8")
            self.json_name = json.loads(namefile.read())
            namefile.close()
            total_num = 0
            for i in self.json_name:
                total_num += len(self.json_name[i])
            self.progress = upload_text('开始下载json')
            self.progress.setGeometry(self.screen_size[0] * 0.3, self.screen_size[1] * 0.15, self.screen_size[0] * 0.4, self.screen_size[1] * 0.7)
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
                        self.download_json_list.append([i, j[:-7], j])
                    else:
                        self.download_json_list.append([i, j[:-5], j])
            self.progress.confirm_numbers(len(self.download_json_list))
            for i in range(10):
                t = threading.Thread(target=self.download_json_thread, name='线程-' + str(i + 1))
                t.start()
            while (threading.activeCount() > 1):
                QApplication.processEvents()
                time.sleep(0.5)

            self.file_save(os.path.join('database', 'json_base.json'), json.dumps(self.json_base))
            self.fix_window_with_json_data()
        except FileNotFoundError:
            mb = QMessageBox(QMessageBox.Critical, "获取名称集失败", "请问您是否准备从wiki下载合成数据列表？", QMessageBox.NoButton, self)
            button1 = mb.addButton('从网络下载', QMessageBox.YesRole)
            button2 = mb.addButton('没有网络，没法下载', QMessageBox.NoRole)
            mb.exec_()
            if mb.clickedButton() == button1:
                self.download_json_name()

    def download_json_thread(self):
        while True:
            self.local.current_num = self.current_num[1]
            self.lock.acquire()
            try:
                self.current_num[1] += 1
                if self.local.current_num >= len(self.download_json_list):
                    break
            finally:
                self.lock.release()
            self.local.download_data = {'action': 'jsondata', 'title': self.download_json_list[self.local.current_num][2], 'format': 'json'}
            self.local.seesion = self.seesion
            self.local.target_url = self.target_url
            self.local.download_info = self.local.seesion.post(self.local.target_url, data=self.local.download_data)
            self.lock.acquire()
            try:
                self.json_base[self.download_json_list[self.local.current_num][0]][self.download_json_list[self.local.current_num][1]] = self.local.download_info.json()['jsondata']
                print(self.json_base[self.download_json_list[self.local.current_num][0]][self.download_json_list[self.local.current_num][1]])
                self.progress.addtext(
                    '【' + QTime.currentTime().toString() + '】【' + threading.current_thread().name + '】下载《' + self.download_json_list[self.local.current_num][2] + '》内容成功')
                self.current_num[0] += 1
                self.progress.set_progress(self.current_num[0])
            finally:
                self.lock.release()
                time.sleep(1)

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
        has_bot = self.seesion.post(self.target_url, data={'action': 'query', 'meta': 'userinfo', 'uiprop': 'rights', 'format': 'json'})
        if 'bot' in has_bot.json()['query']['userinfo']['rights']:
            self.ml['高级功能'] = {0: self.ml[0].addMenu('高级功能')}
            self.ml['高级功能']['更新数据'] = self.ml['高级功能'][0].addAction('更新数据')
            self.ml['高级功能']['更新数据'].triggered.connect(self.update_json_base)
            self.ml['高级功能']['上传'] = self.ml['高级功能'][0].addAction('上传')
            self.ml['高级功能']['上传'].triggered.connect(self.upload_all)
            """
            下面是修改tab的页面情况
            """
            self.editWidget = QWidget(self)
            self.centralWidget().addTab(self.editWidget, '修改页面')
            self.editlayout = {0: QHBoxLayout()}
            self.editWidget.setLayout(self.editlayout[0])
            self.editlayout['基础数据'] = {0: QGroupBox('基础数据', self)}
            self.editlayout[0].addWidget(self.editlayout['基础数据'][0])
            self.editlayout['基础数据']['竖布局'] = {0: QVBoxLayout()}
            self.editlayout['基础数据'][0].setLayout(self.editlayout['基础数据']['竖布局'][0])
            self.editlayout['基础数据']['竖布局']['树'] = {0: QTreeWidget(self)}
            self.editlayout['基础数据']['竖布局'][0].addWidget(self.editlayout['基础数据']['竖布局']['树'][0])
            self.editlayout['基础数据']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])

            self.editlayout['修改核心'] = {0: QGroupBox('修改核心', self)}
            self.editlayout[0].addWidget(self.editlayout['修改核心'][0])
            self.editlayout['修改核心']['竖布局'] = {0: QVBoxLayout()}
            self.editlayout['修改核心'][0].setLayout(self.editlayout['修改核心']['竖布局'][0])
            self.editlayout['修改核心']['竖布局']['大分类']={0:QComboBox(self)}
            self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['大分类'][0])
            self.editlayout['修改核心']['竖布局']['具体库']={0:QComboBox(self)}
            self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['具体库'][0])
            self.editlayout['修改核心']['竖布局']['代码库']={0:QComboBox(self)}
            self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['代码库'][0])
            self.editlayout['修改核心']['竖布局']['大分类']['内容']=[]
            self.editlayout['修改核心']['竖布局']['具体库']['内容']=[]
            self.editlayout['修改核心']['竖布局']['代码库']['内容']=[]
            for i in edit_json.edit:
                self.editlayout['修改核心']['竖布局']['大分类'][0].addItem(i)
                self.editlayout['修改核心']['竖布局']['大分类']['内容'].append(i)
            self.editlayout['修改核心']['竖布局']['大分类'][0].activated.connect(self.edit_category_selected_changed)
            self.edit_category_selected_changed()
            self.editlayout['修改核心']['竖布局']['具体库'][0].activated.connect(self.edit_target_selected_changed)

            self.editlayout['修改核心']['竖布局']['树'] = {0: QTreeWidget(self)}
            self.editlayout['修改核心']['竖布局'][0].addWidget(self.editlayout['修改核心']['竖布局']['树'][0])
            self.editlayout['修改核心']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])

            self.editlayout['竖布局'] = {0: QVBoxLayout()}
            self.editlayout[0].addLayout(self.editlayout['竖布局'][0])
            self.editlayout['竖布局']['新增'] = QPushButton('新增', self)
            self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['新增'])
            self.editlayout['竖布局']['下载'] = QPushButton('下载', self)
            self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['下载'])
            self.editlayout['竖布局']['上传'] = QPushButton('上传', self)
            self.editlayout['竖布局'][0].addWidget(self.editlayout['竖布局']['上传'])
            self.editlayout['竖布局'][0].addStretch(1)

            self.editlayout['额外机制'] = {0: QGroupBox('额外机制', self)}
            self.editlayout[0].addWidget(self.editlayout['额外机制'][0])
            self.editlayout['额外机制']['竖布局'] = {0: QVBoxLayout()}
            self.editlayout['额外机制'][0].setLayout(self.editlayout['额外机制']['竖布局'][0])
            self.editlayout['额外机制']['竖布局']['树'] = {0: QTreeWidget(self)}
            self.editlayout['额外机制']['竖布局'][0].addWidget(self.editlayout['额外机制']['竖布局']['树'][0])
            self.editlayout['额外机制']['竖布局']['树'][0].setHeaderLabels(['名称', '值'])
            self.dict_to_tree(self.editlayout['额外机制']['竖布局']['树'], self.mech)
            self.editlayout['额外机制']['竖布局']['树'][0].setColumnWidth(0, 150)
            self.editlayout['额外机制']['竖布局']['树'][0].expandAll()

    def update_json_base(self):
        hero.fulfill_hero_json(self.text_base, self.json_base["英雄"], self.version)
        item.fulfill_item_json(self.text_base, self.json_base["物品"], self.version)

        ability.get_source_to_data(self.json_base, self.upgrade_base, self.version)
        unit.fulfill_unit_json(self.text_base, self.json_base["非英雄单位"], self.version)

        ability.input_upgrade(self.json_base, self.upgrade_base)

        unit.complete_upgrade(self.json_base["非英雄单位"], self.text_base)
        ability.complete_upgrade(self.json_base["技能"], self.text_base)

        ability.complete_mech(self.json_base["技能"], self.mech)

        for i in self.json_base["技能"]:
            ability.loop_check(self.json_base["技能"][i], self.text_base, self.json_base, i)

        self.file_save(os.path.join('database', 'json_base.json'), json.dumps(self.json_base))
        QMessageBox.information(self, "已完成", "更新数据成功！\n您可以选择上传这些数据。")

    def upload_all(self):
        self.w = upload_text('开始上传数据')
        self.w.setGeometry(self.screen_size[0] * 0.3, self.screen_size[1] * 0.15, self.screen_size[0] * 0.4, self.screen_size[1] * 0.7)
        self.w.setWindowIcon(self.icon)
        self.w.setWindowTitle('上传json中……')
        all_upload = []
        all_upload.append(['Data:版本.json', json.dumps({'版本': self.version})])
        all_upload.append(['Data:text_base.json', json.dumps(self.text_base)])
        all_upload.append(['Data:json_name.json', json.dumps(self.json_name)])
        for i in self.json_base:
            for j in self.json_base[i]:
                if i == '技能源':
                    all_upload.append(['Data:' + j + '/源.json', json.dumps(self.json_base[i][j])])
                else:
                    all_upload.append(['Data:' + j + '.json', json.dumps(self.json_base[i][j])])
        total_num = len(all_upload)
        self.w.confirm_numbers(total_num)
        for i in range(total_num):
            self.w.addtext(self.upload_json(all_upload[i][0], all_upload[i][1]))
            self.w.set_progress(i + 1)
            QApplication.processEvents()
            time.sleep(0.1)
        QMessageBox.information(self.w, '上传完毕', "您已上传完毕，可以关闭窗口", QMessageBox.Yes, QMessageBox.Yes)

    # 向wiki网站上传对应的信息
    def upload_json(self, pagename, content):
        upload_data = {'action': 'edit', 'title': pagename, 'text': content, 'format': 'json', 'token': self.csrf_token}
        upload_info = self.seesion.post(self.target_url, data=upload_data)
        if upload_info.json()['edit']['result'] == 'Success':
            return '【' + QTime.currentTime().toString() + '】上传《' + pagename + '》内容成功'
        else:
            return json.dumps(upload_info.json())

    def dict_to_tree(self, tdict, jdict):
        for j in jdict:
            i = str(j)
            if isinstance(jdict[i], dict):
                tdict[i] = {0: QTreeWidgetItem(tdict[0])}
                tdict[i][0].setText(0, i)
                self.dict_to_tree(tdict[i], jdict[i])
            else:
                tdict[i] = QTreeWidgetItem(tdict[0])
                tdict[i].setText(0, i)
                tdict[i].setText(1, jdict[i])

    def edit_category_selected_changed(self):
        selected=self.editlayout['修改核心']['竖布局']['大分类'][0].currentText()
        self.editlayout['修改核心']['竖布局']['具体库'][0].clear()
        self.editlayout['修改核心']['竖布局']['具体库']['内容']=[]
        self.editlayout['修改核心']['竖布局']['代码库']['内容']=[]
        for i in self.json_base[selected]:
            self.editlayout['修改核心']['竖布局']['具体库'][0].addItem(i)
            self.editlayout['修改核心']['竖布局']['具体库']['内容'].append(i)
        for i in self.text_base[selected]:
            self.editlayout['修改核心']['竖布局']['代码库'][0].addItem(i)
            self.editlayout['修改核心']['竖布局']['代码库']['内容'].append(i)

    def edit_target_selected_changed(self):
        self.editlayout['修改核心']['竖布局']['代码库'][0].setCurrentText(self.json_base[selected])


class upload_text(QWidget):
    def __init__(self, first_txt):
        super().__init__()
        self.b = QTextBrowser(self)
        self.l = QVBoxLayout()
        self.l.addWidget(self.b)
        self.p = QProgressBar(self)
        self.setLayout(self.l)
        thread = threading.Thread(target=self.addtext, args=(first_txt,))
        thread.start()
        self.show()

    def confirm_numbers(self, num):
        self.p.setRange(0, num)
        self.l.addWidget(self.p)

    def set_progress(self, num):
        self.p.setValue(num)

    def addtext(self, content):
        self.b.append(content)
        self.cursor = self.b.textCursor()
        self.b.moveCursor(self.b.textCursor().End)
