import sys
import socket
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from client import Ui_client  # 这个是main   主窗口
from succeed import Ui_succeed  # 这个是widget 子窗口
from failed import Ui_failed


class MyMain(QMainWindow, Ui_client):  # 继承主窗口函数的类, 继承编写的主函数
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化运行A窗口类下的 setupUi 函数


class succeed(QWidget, Ui_succeed):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化运行B窗口类下的 setupUi 函数
        self.toolButton.clicked.connect(lambda:self.close)  # 窗口2 中的关闭按钮


class failed(QWidget, Ui_failed):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化运行B窗口类下的 setupUi 函数
        self.toolButton.clicked.connect(lambda:self.close)  # 窗口2 中的关闭按钮


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_window = MyMain()

    def tcp_connect():    
        host = client_window.server_address.text()
        port = client_window.server_port.text()
        print(host, port)
        client = socket.socket()
        try:
            client.connect((host, int(port)))
            succeed().show()
            message = "1234"
            client.send(message.encode())
            data = client.recv(1024)
            print(data.decode())
            print("connect success")
        except socket.error:
            print("Failed to connect.")
            failed().show()
        
        
    client_window.server_connect.clicked.connect(lambda:tcp_connect())

    client_window.show()
    sys.exit(app.exec_())
