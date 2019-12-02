#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
启动页面


作者: 莫无煜
网站: https://dota.huijiwiki.com
"""
from mainwindow import Main
import sys
from PyQt5.QtWidgets import QApplication
"""
"""
app = QApplication(sys.argv)
ex = Main()
sys.exit(app.exec_())