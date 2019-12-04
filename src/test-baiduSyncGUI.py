# -*- coding:utf-8 -*-
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import sys
import bypy
import configparser as config
import os
import uiobj.configWin as configWin
from threading import Thread,Lock


configini_dir='src/config.ini'


#主框架在这里
class SystemTray(object):
    # 程序托盘类
    def __init__(self, cfgw):
        self.app = app
        self.cfgw = cfgw
        QApplication.setQuitOnLastWindowClosed(False)  # 禁止默认的closed方法，只能使用qapp.quit()的方法退出程序
        self.tp = QSystemTrayIcon(self.cfgw)
        self.initUI()
        self.run()

    def initUI(self):
        # 设置托盘图标
        self.tp.setIcon(QIcon('./res/cloud.ico'))
        #初始化bypy
        self.mybp=bypy.ByPy()
        infomsg=self.mybp.info()
        print(infomsg)
        #检查本地与远程目录正确性
        self.syncFlag=1      #启用同步，如果是0则是不启用同步
        if not os.path.exists(self.cfgw.localPath):
            QMessageBox.question(self.cfgw,"提示","不存在本地文件夹，请设置本地同步目录")
            self.syncFlag=0
        if self.mybp.meta(self.cfgw.remotePath)!=0 :
            QMessageBox.question(self.cfgw,"提示","不存在远程文件夹，请设置远程同步目录")
            self.syncFlag=0

    def quitApp(self):
        # 退出程序
        #self.w.show()  # w.hide() #设置退出时是否显示主窗口
        re = QMessageBox.question(self.cfgw, "提示", "退出系统", QMessageBox.Yes |
                                  QMessageBox.No, QMessageBox.No)
        if re == QMessageBox.Yes:
            self.tp.setVisible(False)  # 隐藏托盘控件，托盘图标刷新不及时，提前隐藏
            qApp.quit()  # 退出程序

    def message(self):
        # 提示信息被点击方法
        print("弹出的信息被点击了")

    def act(self, reason):
        # 主界面显示方法
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2:
            self.xdgopenFile()

    def xdgopenFile(self):
        rn=os.system("xdg-open "+self.cfgw.localPath)
        print(rn)
       

    def run(self):

        a1 = QAction('&设置(Show)', triggered=self.cfgw.show)
        a2 = QAction('&显示本地文件',triggered=self.xdgopenFile)
        aq = QAction('&退出(Exit)', triggered=self.quitApp)
        
        tpMenu = QMenu()
        tpMenu.addAction(a1)
        tpMenu.addAction(a2)
        tpMenu.addAction(aq)
        self.tp.setContextMenu(tpMenu)
        self.tp.show()  # 不调用show不会显示系统托盘消息，图标隐藏无法调用
        # 信息提示
        # 参数1：标题
        # 参数2：内容
        # 参数3：图标（0没有图标 1信息图标 2警告图标 3错误图标），0还是有一个小图标
        self.tp.showMessage('Hello', '我藏好了', icon=0)
        # 绑定提醒信息点击事件
        self.tp.messageClicked.connect(self.message)
        # 绑定托盘菜单点击事件
        self.tp.activated.connect(self.act)

        #开启同步线程


        sys.exit(self.app.exec_())  # 持续对app的连接

   
class syncThread(QtCore.QThread):
    #同步线程，负责进行实时的同步
    #由同步线程发出的信号，告诉主线程同步状态
    syncStatus_sign=QtCore.pyqtSignal(str)
    def __init__(self,localPath,remotePath,syncTime,syncFlag):
        super(syncThread,self).__init__()
        #关键参数，由主线程告诉同步线程
        self.localPath=localPath                                  #本地目录
        self.remotePath=remotePath                        #远程目录
        self.syncTime=syncTime                                 #自动同步时间
        self.syncFlag=syncFlag 
        self.mybp=bypy.ByPy()                                   #是否同步的标志位
        self.exitflg=1                                                        #退出线程标志位，0时退出线程

    #槽函数，由主线程发出信号触发的函数
    def changFLAG(self,flg):
        self.syncFlag=flg
    def changCONFIG(self,cfglist):
        self.localPath=cfglist[0]
        self.remotePath=cfglist[1]
        self.syncTime=cfglist[2]
    def syncupNOW(self):
        #只要有信号过来，立马同步上传
        self.mybp.syncup(self.localPath,self.remotePath,True)

    #线程函数
    def run(self):
        #首先程序开始，先把云端内容下下来
        if self.syncFlag==1:
            self.mybp.syncdown(self.remotePath,self.localPath,True)
        #定时上传
        while self.exitflg:
            if self.syncFlag==1:
                self.mybp.syncup(self.localPath,self.remotePath,True)
            
            self.sleep(60*self.syncTime)


class configWindows(QWidget,configWin.Ui_Form):
    # 设置界面窗口类
    def __init__(self):
        super(configWindows,self).__init__()
        self.setupUi(self)
        #读取配置文件
        self.cfg = config.ConfigParser()
        self.cfg.read(configini_dir)
        self.localPath=self.cfg.get("SET","localPath")
        self.remotePath=self.cfg.get("SET","remotePath")
        self.syncTime=int(self.cfg.get("SET","syncTime"))
        print("读取配置文件\n本地："+self.localPath+"\n远程："+self.remotePath)
        print("同步时间：",self.syncTime)
        #连接信号与槽
        self.pushButton.clicked.connect(self.On_selectPath)
        self.pushButton_2.clicked.connect(self.On_saveConfig)
        #自定义信号，由主线程发送/由设置窗口发送
        self.config_sign=QtCore.pyqtSignal(list)                     #配置参数信号，发送该信号可以改变同步线程里的配置参数
        #初始化comboBox
        self.syncTime_cBoxlist=['1','2','3','4','5','7','10','20','30']
        self.comboBox.addItems(self.syncTime_cBoxlist)
         #更新设置界面的显示
        self.updateShow()
        
        
        
        
    def updateShow(self):
        # 更新设置界面的显示
        self.lineEdit_2.setText(self.localPath)
        self.lineEdit.setText(self.remotePath)
        self.comboBox.setCurrentIndex(self.syncTime_cBoxlist.index(str(self.syncTime)))

    def On_selectPath(self):
        #槽、回调函数:选择本地文件夹
        local_dir=QFileDialog.getExistingDirectory(self,'选择文件夹')
        if len(local_dir)!=0 :
            self.lineEdit_2.setText(local_dir)
    def On_saveConfig(self):
         #检查本地与远程目录正确性
        if not os.path.exists(self.lineEdit_2.text()):
            QMessageBox.question(self,"提示","不存在本地文件夹，请重新设置本地同步目录")
            return
        #槽、回调函数:保存设置
        self.localPath=self.lineEdit_2.text()
        self.remotePath=self.lineEdit.text()
        self.syncTime=int(self.comboBox.currentText())
        self.cfg.set('SET','localPath',self.localPath)
        self.cfg.set('SET','remotePath',self.remotePath)
        self.cfg.set('SET','syncTime',str(self.syncTime))
        self.cfg.write(open(configini_dir, "w"))
        print("应用成功")
        print("localPath",type(self.localPath),self.localPath)
        print("remotePath",type(self.remotePath),self.remotePath)
        print("syncTime",type(self.syncTime),self.syncTime)
    
    def closeEvent(self, event):
        self.updateShow()

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    # 创建一个app程序
    app = QApplication(sys.argv)
    # 创建窗口
    #win = Window()
    configww=configWindows()
    mytray=SystemTray(configww)

    sys.exit(app.exec_()) 