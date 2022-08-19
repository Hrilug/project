'''
将采用多线程模式进行主机和从机的数据交换处理
完善bug报错的模式
解决了sock.recv()的阻塞
'''
import socket
import threading
import queue
import time


class client(socket.socket):
    def __init__(self, name, port, key):
        # TCP通道创建，self为服务对象，self.sock为服务的套接字对象
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", port))  # 服务端口
        self.sock.listen(1)      # 设置监听数量
        self.state = 0  # 连接状态
        self.name = name  # 服务名称
        self.port = port
        self.key = key  # TCP连接密码设置
        print("TCP服务初始化完毕,TCP服务:%s,TCP端口:%d.\n" %
              (self.name, self.port), "..................................\n")

    def tcp_connect(self):
        newsock, (remhost, remport) = self.sock.accept()    # 接收请求
        get_key = str(newsock.recv(1024).decode('utf8'))
        print('%s有一个连接请求 %s:%s' % (self.name, remhost, remport))
        if (get_key == self.key):      # 添加连接
            newsock.send("Succeed to connect.\n".encode('utf8'))
            print(f"{self.name}成功连接.\n")
            self.server = newsock
            self.state = 1
            return 1
        else:
            newsock.send("Failed to connect.\n".encode('utf8'))
            print(f"{self.name}连接失败.\n")
            self.tcp_connect()  # 重新连服务
            return 0


# 使用queue模块，可以方便再两个线程中进行数据的交换
host_msg = queue.Queue(1000)   # 先进先出的跨线程数据，来自host的数据包
slave_msg = queue.Queue(1000)  # 先进先出的跨线程数据，来自slave的数据包


def host_tcp():
    host = client("host", 1000, "1234")
    host.tcp_connect()
    while True:
        if (slave_msg.empty() == False):  # 存在待发送的数据
            data = slave_msg.get()
            print("slave发送接收到的信息%s\n" % data)
            host.server.send(data.encode('utf8'))

        else:
            host.server.setblocking(0)  # 更改为非阻塞模式避免在server.recv()步发生阻塞
            while True:  # 循环接收，知道单次数据完成接受
                try:
                    message = host.server.recv(1024).decode('utf8')
                    if message == "":
                        print("host掉线重连!\n")
                        host.tcp_connect()
                        break
                    else:
                        time.sleep(0.001)
                        host_msg.put(message)
                        print("host发送消息:%s\n" % message)
                except BlockingIOError as e:  # 如果没有数据则,退出循环
                    break
            host.server.setblocking(1)  # 恢复阻塞模式,避免后续socket操作报错


def slave_tcp():
    slave = client("slave", 2000, "5678")
    slave.tcp_connect()
    while True:
        if (host_msg.empty() == False):
            data = host_msg.get()
            print("host发送接收到的信息%s\n" % data)
            slave.server.send(data.encode('utf8'))

        else:
            slave.server.setblocking(0)  # 更改为非阻塞模式避免在server.recv()步发生阻塞
            while True:  # 循环接收，知道单次数据完成接受
                try:
                    message = slave.server.recv(1024).decode('utf8')
                    if message == "":
                        print("slave掉线重连!\n")
                        slave.tcp_connect()
                        break
                    else:
                        time.sleep(0.001)
                        slave_msg.put(message)
                        print("slave发送消息:%s\n" % message)
                except BlockingIOError as e:  # 如果没有数据则,退出循环
                    break
            slave.server.setblocking(1)  # 恢复阻塞模式,避免后续socket操作报错


host_thread = threading.Thread(target=host_tcp, name="host_thread")
slave_thread = threading.Thread(target=slave_tcp, name="slave_thread")

host_thread.start()
slave_thread.start()
host_thread.join()
slave_thread.join()
