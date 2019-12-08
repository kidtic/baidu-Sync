# -*- coding:utf-8 -*-
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import sys
import bypy
import configparser as config
import os
import uiobj.configWin as configWin
import uiobj.logWin as logWin
from threading import Thread,Lock
import time




configini_dir='config/config.ini'
res_dir="./res/"
synclog_dir='config/sync.log'

if os.path.exists("/opt/baiduSync"):
    configini_dir="/opt/baiduSync/config.ini"
    res_dir="/opt/baiduSync/res/"
    synclog_dir='/opt/baiduSync/sync.log'






#主框架在这里
class SystemTray(QtCore.QObject):
    #新建一个信号：用于开启同步与不开启同步切换
    syncFlag_sign=QtCore.pyqtSignal(int)
    #新建一个信号：用于立即同步
    syncnow_sign=QtCore.pyqtSignal()
    # 程序托盘类
    def __init__(self, cfgw,logw):
        super(SystemTray,self).__init__()
        self.app = app
        self.cfgw = cfgw
        self.logw=logw
        QApplication.setQuitOnLastWindowClosed(False)  # 禁止默认的closed方法，只能使用qapp.quit()的方法退出程序
        self.tp = QSystemTrayIcon(self.cfgw)
        self.initUI()
        self.run()
        
    def initUI(self):
        # 设置托盘图标
        self.tp.setIcon(QIcon(res_dir+'cloud.ico'))
        #初始化bypy
        self.mybp=bypy.ByPy()
        infomsg=self.mybp.info()
        print(infomsg)
        #检查本地与远程目录正确性
        self.syncFlag=1      #启用同步，如果是0则是不启用同步
        if not os.path.exists(self.cfgw.localPath):
            QMessageBox.question(self.cfgw,"提示","不存在本地文件夹，请设置本地同步目录")
            self.syncFlag=0
            self.cfgw.show()
        if self.mybp.meta(self.cfgw.remotePath)!=0 :
            QMessageBox.question(self.cfgw,"提示","不存在远程文件夹，请在百度云盘中的bypy文件夹里，建立linux文件夹")
            self.syncFlag=0
        #连接信号槽
        self.cfgw.pushButton_movedir.clicked.connect(self.on_moveLocalPath)

    def quitApp(self):
        # 退出程序
        #self.w.show()  # w.hide() #设置退出时是否显示主窗口
        re = QMessageBox.question(self.cfgw, "提示", "退出系统", QMessageBox.Yes |
                                  QMessageBox.No, QMessageBox.No)
        if re == QMessageBox.Yes:
            self.tp.setVisible(False)  # 隐藏托盘控件，托盘图标刷新不及时，提前隐藏
            self.syncthead.exitflg=0
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
       
    def pauseSync(self):
        if self.syncFlag==1:
            self.syncFlag=0
            self.aswitch.setText("&开启同步")
            self.tp.setIcon(QIcon(res_dir+'cloud_pause.ico'))
        elif self.syncFlag==0:
            self.syncFlag=1
            self.aswitch.setText("&暂停同步")
            self.tp.setIcon(QIcon(res_dir+'cloud.ico'))
        self.syncFlag_sign.emit(self.syncFlag)

    def syncNow(self):
        self.syncnow_sign.emit()

    def run(self):
        a1 = QAction('&设置', triggered=self.cfgw.show)
        a2 = QAction('&显示本地文件',triggered=self.xdgopenFile)
        a3=QAction('&显示日志', triggered=self.logw.show)
        aq = QAction('&退出(Exit)', triggered=self.quitApp)
        actsync=QAction('&立即同步', triggered=self.syncNow)
        if self.syncFlag==0:
            self.aswitch=QAction('&开启同步', triggered=self.pauseSync)
            self.tp.setIcon(QIcon(res_dir+'cloud_pause.ico'))
        elif self.syncFlag==1:
            self.aswitch=QAction('&暂停同步', triggered=self.pauseSync)
            self.tp.setIcon(QIcon(res_dir+'cloud.ico'))
 
        tpMenu = QMenu()
        tpMenu.addAction(a1)
        tpMenu.addAction(a2)
        tpMenu.addAction(a3)
        tpMenu.addSeparator()
        tpMenu.addAction(actsync)
        tpMenu.addAction(self.aswitch)
        tpMenu.addSeparator()
        tpMenu.addAction(aq)
        
        self.tp.setContextMenu(tpMenu)
        self.tp.show()  # 不调用show不会显示系统托盘消息，图标隐藏无法调用
        # 信息提示
        self.tp.showMessage('Hello', '我藏好了', icon=0)
        self.tp.messageClicked.connect(self.message)
        # 绑定托盘菜单点击事件
        self.tp.activated.connect(self.act)

        #开启同步线程
        self.syncthead=syncThread(self.cfgw.localPath,self.cfgw.remotePath,self.cfgw.syncTime,self.syncFlag)
        self.syncFlag_sign.connect(self.syncthead.changFLAG)
        self.cfgw.config_sign.connect(self.syncthead.changCONFIG)
        self.syncnow_sign.connect(self.syncthead.syncupNOW)
        self.syncthead.syncStatus_sign.connect(self.on_changStatusIco)
        self.syncthead.synclog_sign.connect(self.logw.on_signlog)
        #self.syncthead.syncStatus_sign.connect
        self.syncthead.start()                    #启动线程
        
        sys.exit(self.app.exec_())             # 持续对app的连接

    def on_moveLocalPath(self):
        #--移动本地同步盘的位置，如果原来的位置不可用，则创建空的同步盘
        #--如果原来的位置可用，则将所有文件移动到新的同步盘
        #判断新的位置是否可用
        if not os.path.exists(self.cfgw.lineEdit_2.text()):
            QMessageBox.question(self,"提示","不存在本地文件夹，请重新设置本地同步目录")
            return
        #判断原来的本地同步盘是否存在，且满足格式。
        geshi=os.path.split(self.cfgw.localPath)[1]=="SyncPath" or os.path.split(os.path.split(self.cfgw.localPath)[0])[1]=="SyncPath"
        if os.path.exists(self.cfgw.localPath) and geshi :
            localPath_last=self.cfgw.localPath
            #在该目录下创建同步盘：SyncPath,以及同步盘的基本结构
            self.cfgw.localPath=self.cfgw.lineEdit_2.text()+"/SyncPath/"+self.cfgw.remotePath
            try:
                os.makedirs(self.cfgw.localPath)
            except FileExistsError :
                pass
            #复制文件夹
            os.system("cp -r "+localPath_last+'/* '+self.cfgw.localPath)
        else:
            #在该目录下创建同步盘：SyncPath,以及同步盘的基本结构
            self.cfgw.localPath=self.cfgw.lineEdit_2.text()+"/SyncPath/"+self.cfgw.remotePath
            try:
                os.makedirs(self.cfgw.localPath)
            except FileExistsError:
                pass
            #这里由于是个空文件夹，所以为了防止上传空文件夹，先下载一次
            self.mybp.syncdown(self.cfgw.remotePath,self.cfgw.localPath,True)
        #发送同步设置信号，保存设置ini文件
        sendcfglist=[self.cfgw.localPath,self.cfgw.remotePath,self.cfgw.syncTime]
        self.cfgw.config_sign.emit(sendcfglist)
        self.cfgw.cfg.set('SET','localPath',self.cfgw.localPath)
        self.cfgw.cfg.write(open(configini_dir, "w"))
        print("本地同步盘设置成功")
        QMessageBox.question(self.cfgw,"设置成功","本地同步盘设置成功")

    def on_changStatusIco(self,stasstr):
        if stasstr=="upload":
            self.tp.setIcon(QIcon(res_dir+'cloud_upload.ico'))
        elif stasstr=="down":
            self.tp.setIcon(QIcon(res_dir+'cloud_download.ico'))
        elif stasstr=="ok":
            if self.syncFlag==0:
                self.tp.setIcon(QIcon(res_dir+'cloud_pause.ico'))
            elif self.syncFlag==1:
                self.tp.setIcon(QIcon(res_dir+'cloud.ico'))

class syncThread(QtCore.QThread):
    #同步线程，负责进行实时的同步
    #由同步线程发出的信号，告诉主线程同步状态
    syncStatus_sign=QtCore.pyqtSignal(str)
    #告诉主线程，同步日志
    synclog_sign=QtCore.pyqtSignal(list)
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
        self.syncStatus_sign.emit("upload")
        self.mybp.compare(self.remotePath,self.localPath)
        diff=[self.mybp.result['diff'],self.mybp.result['local'],self.mybp.result['remote']]
        diff_len=len(diff[0])+len(diff[1])+len(diff[2])
        print("diff_len:",diff_len)
        if diff_len>0:
            print("[upload file] ", time.asctime()) 
            sync_list=self.mybp.syncup(self.localPath,self.remotePath,True)
            print("finish:   ",self.localPath,self.remotePath)
            if sync_list==bypy.const.ENoError:
                log_list=["upload",diff]
                self.synclog_sign.emit(log_list)
            else:
                log_list=["error",bypy.const.ErrorExplanations[sync_list]]
                self.synclog_sign.emit(log_list)
        self.syncStatus_sign.emit("ok")
    #线程函数
    def run(self):
        ctct=0
        #首先程序开始，先把云端内容下下来
        if self.syncFlag==1:
            self.mybp.compare(self.remotePath,self.localPath)
            diff=[self.mybp.result['diff'],self.mybp.result['local'],self.mybp.result['remote']]
            diff_len=len(diff[0])+len(diff[1])+len(diff[2])
            print("diff_len:",diff_len)
            if diff_len>0:
                self.syncStatus_sign.emit("down")
                sync_list=self.mybp.syncdown(self.remotePath,self.localPath,True)
                print("syncup_result: ",bypy.const.ErrorExplanations[sync_list])
                self.syncStatus_sign.emit("ok")
                print("download file")
                if sync_list==bypy.const.ENoError:
                    log_list=["download",diff]
                    self.synclog_sign.emit(log_list)
                else:
                    log_list=["error",bypy.const.ErrorExplanations[sync_list]]
                    self.synclog_sign.emit(log_list)
        #定时上传
        while self.exitflg:
            if self.syncFlag==1:
                ctct=ctct+1
                self.mybp.compare(self.remotePath,self.localPath)
                diff=[self.mybp.result['diff'],self.mybp.result['local'],self.mybp.result['remote']]
                diff_len=len(diff[0])+len(diff[1])+len(diff[2])
                print("diff_len:",diff_len,"   ctct:",ctct)
                
                if diff_len>0:
                    print("[upload file] ", time.asctime(),"|",ctct) 
                    self.syncStatus_sign.emit("upload")
                    sync_list=self.mybp.syncup(self.localPath,self.remotePath,True)
                    print("syncup_result: ",bypy.const.ErrorExplanations[sync_list])
                    self.syncStatus_sign.emit("ok")
                    print("finish:   ",self.localPath,self.remotePath)
                    if sync_list==bypy.const.ENoError:
                        log_list=["upload",diff]
                        self.synclog_sign.emit(log_list)
                    else:
                        log_list=["error",bypy.const.ErrorExplanations[sync_list]]
                        self.synclog_sign.emit(log_list)
            self.sleep(self.syncTime)


class configWindows(QWidget,configWin.Ui_Form):
    #自定义信号，由主线程发送/由设置窗口发送
    config_sign=QtCore.pyqtSignal(list)                     #配置参数信号，发送该信号可以改变同步线程里的配置参数
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
        self.pushButton_2.clicked.connect(self.On_setsyncTimeConfig)
        #初始化comboBox
        self.syncTime_cBoxlist=['1','2','3','4','5','7','10','20','30','60','90','120']
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

    def On_setsyncTimeConfig(self):
        #槽、回调函数:保存同步时间
        self.syncTime=int(self.comboBox.currentText())
        self.cfg.set('SET','syncTime',str(self.syncTime))
        self.cfg.write(open(configini_dir, "w"))
        #传输信号给同步线程：新的设置文件来了
        sendcfglist=[self.localPath,self.remotePath,self.syncTime]
        self.config_sign.emit(sendcfglist)
        print("应用成功")
        print("syncTime",type(self.syncTime),self.syncTime)
    
    def closeEvent(self, event):
        self.updateShow()

class logWindows(QWidget,logWin.Ui_Form):
    def __init__(self,logdir):
        super(logWindows,self).__init__()
        self.setupUi(self)
        #打开log文件
        self.logfd = open(logdir,"a+")
        print("logfd: ",self.logfd)
        #读取文件
        self.logfd.write("\n"+time.asctime()+"  |   open baiduSync software\n")
        self.logfd.seek(0,0)
        logsline=self.logfd.read()
        self.logfd.seek(0,2)
        self.textBrowser.append(logsline)
        #连接信号槽
        self.pushButton.clicked.connect(self.on_clearlog)

    def on_clearlog(self):
        self.logfd.seek(0,0)
        self.logfd.truncate()
        self.textBrowser.clear()

    def on_signlog(self,signlist):
        if signlist[0]=='upload':
            addstr=time.asctime()+"  |   "+signlist[0]+'   \n'
            for e in signlist[1][0]:#diff
                addstr=addstr+"         ->  "+e[0]+'   '+e[1]+'\n'
            for e in signlist[1][1]:#local
                addstr=addstr+"         +   "+e[0]+'   '+e[1]+'\n'
            for e in signlist[1][2]:#remote
                addstr=addstr+"         -    "+e[0]+'   '+e[1]+'\n'
        elif signlist[0]=='download':
            addstr=time.asctime()+"  |   "+signlist[0]+'   \n'
            for e in signlist[1][0]:#diff
                addstr=addstr+"         ->  "+e[0]+'   '+e[1]+'\n'
            for e in signlist[1][1]:#local
                addstr=addstr+"         -    "+e[0]+'   '+e[1]+'\n'
            for e in signlist[1][2]:#remote
                addstr=addstr+"         +   "+e[0]+'   '+e[1]+'\n'
        elif signlist[0]=='error':
            addstr=time.asctime()+"  |   "+signlist[0]+'   \n'
            addstr=addstr+"          ERROR: "+signlist[1]+'\n'
        
        self.textBrowser.append(addstr)
        self.logfd.write(addstr)

    
        

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    # 创建一个app程序
    app = QApplication(sys.argv)
    # 创建窗口
    #win = Window()
    configww=configWindows()
    logw=logWindows(synclog_dir)
    #logw.show()
    mytray=SystemTray(configww,logw)

    sys.exit(app.exec_()) 
