from PyQt4 import QtGui, QtCore
import sys
import paramiko
import os
import icon_rc
import win32com.client


class Begin(QtCore.QThread):

    def __init__(self):
        super(Begin, self).__init__()
        self.statu_run = 0
        self.StopMember = []

    def run(self):
        if self.statu_run == 1:
            connect.vwan = []
            a = self.Login()
            if a :
                a = self.CheckUse()
                if a :
                    a = self.ConnectLine()
                    if a :
                        self.sleep(10)
                        self.channel.close()
                        self.trans.close()
                        connect.thread_CheckNet.Member = connect.vwan
                        connect.thread_CheckNet.k = 1
                        connect.thread_CheckNet.start()
            else:
                self.channel.close()
                self.trans.close()
            connect.pushButton_Connect.setEnabled(1)
            self.statu_run = 0
        elif self.statu_run == 2:
            self.Reset()
            self.statu_run = 0
        elif self.statu_run == 3:
            self.Stop()
            self.statu_run = 0

    def Login(self):
        hostname = connect.lineEdit_Host.text()
        port = 22
        username = connect.lineEdit_Username.text()
        password = connect.lineEdit_Password.text()

        try:
            self.trans = paramiko.Transport((hostname, port))
            self.trans.start_client()
            self.trans.auth_password(username=username, password=password)
            self.channel = self.trans.open_session()
            self.channel.get_pty()
            self.channel.invoke_shell()
            connect.Signal_SetStatu.emit('Login Done')
            return 1
        except:
            connect.Signal_Warning.emit(1)
            connect.Signal_SetStatu.emit('Login Fail')
            return 0

    def CheckUse(self):
        connect.Signal_SetStatu.emit('CheckUse Start')
        self.channel.sendall('sh CheckUse.sh %d'%(int(connect.lineEdit_LogNumber.text())))
        self.channel.sendall('\n')
        while True:
            readlist, writelist, errlist = [self.channel, sys.stdin, ], [], []
            if self.channel in readlist:
                result = self.channel.recv(1024)
                # 断开连接后退出
                if len(result) == 0:
                    print("\r\n**** EOF **** \r\n")
                    return 0
                if result.decode() == u'Wan is using\r\n':
                    connect.Signal_Warning.emit(2)
                    return 0
                elif 'vwan' in result.decode():
                    connect.vwan.append(result.decode().split('\r\n')[0])
                elif 'Done' in result.decode():
                    if len(connect.vwan) == int(connect.lineEdit_LogNumber.text()):
                        connect.Signal_SetStatu.emit('Check Allright')
                        return 1
                    else:
                        self.channel.sendall('uci set network.wan.ok="0"')
                        self.channel.sendall('\n')
                        self.msleep(500)
                        self.channel.sendall('uci commit')
                        self.channel.sendall('\n')
                        connect.Signal_SetStatu.emit('Check wrong')
                        connect.Signal_Warning.emit(3)
                        return 0

    def ConnectLine(self):
        connect.Signal_SetStatu.emit('Connect Start')
        connect.Signal_Warning.emit(4)
        command = 'sh Connect.sh'
        for i in connect.vwan:
            command = command + ' ' + i
        self.channel.sendall(command)
        self.channel.sendall('\n')
        while True:
            readlist, writelist, errlist = [self.channel, sys.stdin, ], [], []
            if self.channel in readlist:
                result = self.channel.recv(1024)
                # 断开连接后退出
                if len(result) == 0:
                    print("\r\n**** EOF **** \r\n")
                    return 0
                if 'vwan' in result.decode():
                    connect.Signal_SetStatu.emit('Login %s'% (result.decode()))
                if 'Done' in result.decode():
                    connect.Signal_SetStatu.emit('Get Ready')
                    return 1

    def Stop(self):
        self.Login()
        command = 'sh Stop.sh'
        for i in self.StopMember:
            command = command + ' ' + i
        self.channel.sendall(command)
        self.channel.sendall('\n')
        while True:
            readlist, writelist, errlist = [self.channel, sys.stdin, ], [], []
            if self.channel in readlist:
                result = self.channel.recv(1024)
                # 断开连接后退出
                if len(result) == 0:
                    print("\r\n**** EOF **** \r\n")
                    return 0
                if 'Done' in result.decode():
                    connect.Signal_SetStatu.emit('Stop Succeed')
                    break

    def Reset(self):
        self.Login()
        self.channel.sendall("sh Reset.sh")
        self.channel.sendall('\n')
        while True:
            readlist, writelist, errlist = [self.channel, sys.stdin, ], [], []
            if self.channel in readlist:
                result = self.channel.recv(1024)
                # 断开连接后退出
                if len(result) == 0:
                    print("\r\n**** EOF **** \r\n")
                    return 0
                if 'Done' in result.decode():
                    connect.Signal_SetStatu.emit('Reset Succeed')
                    break

class CheckNet(QtCore.QThread):

    def __init__(self):
        super(CheckNet, self).__init__()
        self.Member = []
        self.k = 0

    def run(self):
        self.CheckConnect()

    def Login(self):
        hostname = connect.lineEdit_Host.text()
        port = 22
        username = connect.lineEdit_Username.text()
        password = connect.lineEdit_Password.text()

        try:
            self.trans = paramiko.Transport((hostname, port))
            self.trans.start_client()
            self.trans.auth_password(username=username, password=password)
            self.channel = self.trans.open_session()
            self.channel.get_pty()
            self.channel.invoke_shell()
            connect.Signal_SetStatu.emit('Login Done')
            return 1
        except:
            connect.Signal_Warning.emit(1)
            connect.Signal_SetStatu.emit('Login Fail')
            return 0

    def CheckConnect(self):
        self.Login()
        self.OK = 0
        for ii in range(3):
            text = ''
            command = "sh CheckConnect.sh"
            for i in self.Member:
                command = command + ' ' + i
            self.channel.sendall(command)
            self.channel.sendall('\n')
            self.sleep(10)
            while True:
                readlist, writelist, errlist = [self.channel, sys.stdin, ], [], []
                if self.channel in readlist:
                    result = self.channel.recv(1024)
                    text = text + result.decode()
                    # 断开连接后退出
                    if len(result) == 0:
                        print("\r\n**** EOF **** \r\n")
                        self.Member = []
                        return 0
                    if 'Done'in result.decode():
                        connect.Signal_SetStatu.emit('Check Done')
                        text1 = text.split('\r\n')
                        text2 = ''
                        for i in text1:
                            if 'vwan' in i:
                                if 'Check' in i:
                                    continue
                                else:
                                    text2 = text2 + '\n' + '\n' + i
                        connect.Signal_Change.emit(text2 ,self.k)
                        self.channel.close()
                        self.trans.close()
                        self.Member = []
                        return 1
        self.channel.close()
        self.trans.close()

class Connect(QtGui.QMainWindow):

    Signal_Warning = QtCore.pyqtSignal(int)
    Signal_Change = QtCore.pyqtSignal(str, int)
    Signal_SetStatu = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Connect, self).__init__()

        self.initUI()
        self.thread_Begin = Begin()
        self.thread_CheckNet = CheckNet()
        self.vwan = []

    def initUI(self):
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)

        self.groupBox_Statu = QtGui.QGroupBox(u'连接状态')
        self.groupBox_Login = QtGui.QGroupBox(u'登录信息')
        self.groupBox_Selfing = QtGui.QGroupBox(u'自助板块')

        self.label_Statu = QtGui.QLabel(u'未配端口')
        self.label_Host =QtGui.QLabel(u'路由器后台网址')
        self.label_Username = QtGui.QLabel(u'登录用户名')
        self.label_Password = QtGui.QLabel(u'登录密码')
        self.label_LogNumber = QtGui.QLabel(u'登录账号数量')
        self.label_Check = QtGui.QLabel(u'无查询内容')

        self.pushButton_Connect = QtGui.QPushButton(u'准备拦截')
        self.pushButton_Stop = QtGui.QPushButton(u'退出账号')
        self.pushButton_Refresh = QtGui.QPushButton(u'刷新状态')
        self.pushButton_Check = QtGui.QPushButton(u'手动查询状态')
        self.pushButton_SelfStop = QtGui.QPushButton(u'手动关闭网口')
        self.pushButton_ResetOk = QtGui.QPushButton(u'重置网口标志位')

        self.lineEdit_Host = QtGui.QLineEdit('192.168.1.1')
        self.lineEdit_Username = QtGui.QLineEdit('root')
        self.lineEdit_Password = QtGui.QLineEdit('admin')
        self.lineEdit_LogNumber = QtGui.QLineEdit('0')
        self.lineEdit_Vwan = QtGui.QLineEdit('vwan?')
        self.statusBar().showMessage(' ')

        self.layout_gB_S = QtGui.QVBoxLayout(self.groupBox_Statu)
        self.layout_gB_S.addWidget(self.label_Statu)

        self.layout_pB = QtGui.QHBoxLayout()
        self.layout_pB.addWidget(self.pushButton_Connect)
        self.layout_pB.addWidget(self.pushButton_Stop)

        self.layout_gB_L = QtGui.QVBoxLayout(self.groupBox_Login)
        self.layout_gB_L.addWidget(self.label_Host)
        self.layout_gB_L.addWidget(self.lineEdit_Host)
        self.layout_gB_L.addWidget(self.label_Username)
        self.layout_gB_L.addWidget(self.lineEdit_Username)
        self.layout_gB_L.addWidget(self.label_Password)
        self.layout_gB_L.addWidget(self.lineEdit_Password)
        self.layout_gB_L.addWidget(self.label_LogNumber)
        self.layout_gB_L.addWidget(self.lineEdit_LogNumber)

        self.layout_connect = QtGui.QVBoxLayout()
        self.layout_connect.addWidget(self.groupBox_Statu)
        self.layout_connect.addLayout(self.layout_pB)
        self.layout_connect.addWidget(self.pushButton_Refresh)

        self.layout_gB_Self = QtGui.QVBoxLayout(self.groupBox_Selfing)
        self.layout_gB_Self.addWidget(self.label_Check)
        self.layout_gB_Self.addWidget(self.lineEdit_Vwan)
        self.layout_gB_Self.addWidget(self.pushButton_Check)
        self.layout_gB_Self.addWidget(self.pushButton_SelfStop)
        self.layout_gB_Self.addWidget(self.pushButton_ResetOk)

        self.layout_all = QtGui.QHBoxLayout()
        self.layout_all.addWidget(self.groupBox_Login)
        self.layout_all.addLayout(self.layout_connect)
        self.layout_all.addWidget(self.groupBox_Selfing)

        self.widget.setLayout(self.layout_all)

        self.TuoPan = QtGui.QSystemTrayIcon(self)
        self.TuoPan.setIcon(QtGui.QIcon(':icon.jpg'))
        self.TuoPan.show()

        self.groupBox_Statu.setMinimumHeight(200)
        self.label_Statu.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_Login.setMaximumWidth(115)
        self.setFixedSize(self.sizeHint())
        self.setMinimumWidth(300)

        self.pushButton_Connect.clicked.connect(self.Start)
        self.pushButton_Stop.clicked.connect(self.Stop1)
        self.pushButton_Refresh.clicked.connect(self.Check1)
        self.pushButton_Check.clicked.connect(self.Check2)
        self.pushButton_SelfStop.clicked.connect(self.Stop2)
        self.pushButton_ResetOk.clicked.connect(self.Reset)
        self.Signal_Warning.connect(self.Warning)
        self.Signal_SetStatu.connect(self.SetStatu)
        self.Signal_Change.connect(self.Change)
        self.TuoPan.activated.connect(self.trayClick)

        self.setWindowIcon(QtGui.QIcon(':icon.jpg'))
        self.setWindowTitle('Connect')

    def trayClick(self, reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:  # 双击
            self.setVisible(True)
            self.setWindowFlags(QtCore.Qt.Window)
            self.show()
            self.activateWindow()
            self.showNormal()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange and self.isMinimized():
            self.setVisible(False)
            self.setWindowFlags(QtCore.Qt.Tool)

    def Warning(self, n):
        if n == 1:
            QtGui.QMessageBox().warning(self, 'Warning', u"连接路由器失败！\n请检查信息是否正确！",
                                        QtGui.QMessageBox.Yes)
        if n == 2:
            QtGui.QMessageBox().warning(self, 'Warning', u"拨号占用！请稍后再试！",
                                        QtGui.QMessageBox.Yes)

        if n == 3:
            QtGui.QMessageBox().warning(self, 'Warning', u"虚拟端口不足！",
                                        QtGui.QMessageBox.Yes)

        if n == 4:
            QtGui.QMessageBox().warning(self, 'Warning', u"请依次登录账号！",
                                        QtGui.QMessageBox.Yes)

    def SetStatu(self, message):
        self.statusBar().showMessage(message)

    def Start(self):
        if int(self.lineEdit_LogNumber.text()) == 0:
            QtGui.QMessageBox().warning(self, 'Warning', u"请设置正确的登录数量！",
                                        QtGui.QMessageBox.Yes)
        else:
            self.pushButton_Connect.setEnabled(0)
            self.thread_Begin.statu_run = 1
            self.thread_Begin.start()

    def Change(self, statu, k):
        if k == 1:
            self.label_Statu.setText(statu)
        elif k == 2:
            self.label_Check.setText(statu)

    def Stop1(self):
        if not self.thread_Begin.isRunning():
            if self.vwan != []:
                self.thread_Begin.StopMember = self.vwan
                self.thread_Begin.statu_run = 3
                self.thread_Begin.start()
        else:
            QtGui.QMessageBox().warning(self, 'Warning', u"正在操作中，请稍等！",
                                        QtGui.QMessageBox.Yes)

    def Stop2(self):
        if not self.thread_Begin.isRunning():
            self.thread_Begin.StopMember.append(self.lineEdit_Vwan.text())
            self.thread_Begin.statu_run = 3
            self.thread_Begin.start()
        else:
            QtGui.QMessageBox().warning(self, 'Warning', u"正在操作中，请稍等！",
                                        QtGui.QMessageBox.Yes)

    def Check1(self):
        if not self.thread_CheckNet.isRunning():
            if self.vwan != []:
                self.thread_CheckNet.Member = self.vwan
                self.thread_CheckNet.k = 1
                self.thread_CheckNet.start()
            else:
                QtGui.QMessageBox().warning(self, 'Warning', u"无可查询对象！",
                                            QtGui.QMessageBox.Yes)
        else:
            QtGui.QMessageBox().warning(self, 'Warning', u"查询进行中！\n请稍等！",
                                        QtGui.QMessageBox.Yes)

    def Check2(self):
        if self.lineEdit_Vwan.text() == 'vwan?':
            QtGui.QMessageBox().warning(self, 'Warning', u"请给出正确的网口名称！",
                                        QtGui.QMessageBox.Yes)
        else:
            if not self.thread_CheckNet.isRunning():
                self.thread_CheckNet.Member.append(self.lineEdit_Vwan.text())
                self.thread_CheckNet.k = 2
                self.thread_CheckNet.start()
            else:
                QtGui.QMessageBox().warning(self, 'Warning', u"查询进行中！\n请稍等！",
                                            QtGui.QMessageBox.Yes)

    def Reset(self):
        if not self.thread_Begin.isRunning():
            self.thread_Begin.statu_run = 2
            self.thread_Begin.start()
        else:
            QtGui.QMessageBox().warning(self, 'Warning', u"正在操作中，请稍等！",
                                        QtGui.QMessageBox.Yes)

    def closeEvent(self, event):
        if self.vwan != []:
            reply = QtGui.QMessageBox().warning(self, 'Warning', u"关闭软件是否退出路由器上的账号？",
                                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if reply == 16384:
                try :
                    self.thread_Begin.Stop()
                    self.thread_Begin.terminate()
                    self.thread_CheckNet.terminate()
                except:
                    pass
                event.accept()
        elif reply == 65536:
            event.accept()
        elif reply == 4194304:
            event.ignore()



if __name__ == '__main__':
    WMI = win32com.client.GetObject('winmgmts:')
    processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % 'Connect.exe')
    app = QtGui.QApplication(sys.argv)
    connect = Connect()
    if len(processCodeCov) > 1 :
        QtGui.QMessageBox().warning(connect, 'Warning', u"程序已开启！",
                                    QtGui.QMessageBox.Yes)
    else:
        connect.show()
        connect.showNormal()
        connect.activateWindow()
        sys.exit(app.exec_())