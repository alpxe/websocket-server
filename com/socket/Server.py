# -*- coding:utf-8 -*-
import socket
import select
import queue
from typing import Dict, Any
from com.socket.UsrPool import UsrPool


class Server:
    __message_queues: Dict[socket.socket, queue.Queue] = {}  # 消息列队

    def __init__(self, port: int):
        self.__master = self.__websocket(port)
        self.__sockets = [self.__master]  # socket管理池
        self.__proclist = []  # 管理待处理的socket
        self.__usrpool = UsrPool()  # 用户池
        pass

    def run(self):
        while True:
            self.__core()
        pass

    def __core(self):
        readable, writable, exceptional = select.select(self.__sockets, self.__proclist, self.__sockets)

        for sock in readable:
            assert isinstance(sock, socket.socket)
            if sock is self.__master:  # 如果是服务端 有新连接
                client, client_addr = sock.accept()  # 接收client
                print("new connection from : ", client_addr)

                client.setblocking(False)  # 不阻塞
                self.__sockets.append(client)  # 将新client 加入 sockets管理池中
                self.__message_queues[client] = queue.Queue()  # 为client 创建它的消息列队
                self.__usrpool.create_usr(client)  # 创建关联用户
            else:
                try:
                    data = sock.recv(2048)
                except Exception as e:
                    print("[Error] sock.recv", e)
                    self.__disconnect(sock)
                else:
                    if len(data) < 9:
                        self.__disconnect(sock)  # websocket协议 报文长度小于9 通常已断线
                    else:
                        self.__message_queues[sock].put(data)  # 将收到的消息 加入消息列队中

                        if sock not in self.__proclist:
                            self.__proclist.append(sock)  # 让带数据的socket 在 wlist中活跃
                    pass
                pass
            pass

        for sock in writable:
            assert isinstance(sock, socket.socket)
            try:
                next_msg = self.__message_queues[sock].get_nowait()  # 从消息列队中取出消息
            except Exception as e:  # 消息取出失败  消息列队为空
                # print("except:", e)
                self.__proclist.remove(sock)
            else:
                self.resolve(sock, next_msg)
                pass
            pass

        for sock in exceptional:
            print("socket 异常")
            self.__disconnect(sock)
            pass

        pass

    @staticmethod
    def __websocket(port: int) -> socket:
        """
        创建 websocket server
        :param port: 端口
        :return: socket server
        """
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind(('', port))
        serv.listen(1024)
        return serv

    def __disconnect(self, sock):
        """
        断开连接
        :param sock:
        :return:
        """
        if sock in self.__proclist:
            self.__proclist.remove(sock)
            pass

        self.__usrpool.delete_usr(sock)
        self.__sockets.remove(sock)
        del self.__message_queues[sock]
        sock.close()

    def resolve(self, client, msg):
        """
        解析消息 (websocket 握手)
        :param client:
        :param msg:
        :return:
        """

        self.__usrpool.message(client, msg)
        pass
