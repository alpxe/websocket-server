# -*- coding:utf-8 -*-
import socket
import uuid
import struct
from typing import Dict, Any
from com.socket.UsrInfo import UsrInfo
from com.socket.Method import Method


class UsrPool:
    __usrlist: Dict[uuid.UUID, UsrInfo] = {}  # 用户列表

    def __init__(self):
        print("start usr pool")
        pass

    def message(self, sock: socket.socket, msg):
        usr = self.search_usr(sock)

        if usr.shaking is False:
            upgrade = Method.perform_handshaking(msg)
            usr.sock.send(upgrade)
            usr.shaking = True
        else:
            # Method.decode() 返回 arraybytes
            recvbytes = Method.decode(msg)

            # print(recvbytes)

            # 如果是字符串
            # print(recvbytes.decode(encoding="utf-8"))

            # 如果是数字 遵守 struct.unpack
            total = struct.unpack("<I", recvbytes[0:4])[0]  # 字节总长度
            print(total)

            # usr.sock.send(Method.encode(sendbytes))
        pass

    def create_usr(self, sock: socket.socket):
        """
        通过socket 创建一个用户信息
        :param sock:
        :return:
        """
        key = uuid.uuid1()
        self.__usrlist[key] = UsrInfo(key, sock)
        pass

    def delete_usr(self, sock: socket.socket):
        usr = self.search_usr(sock)
        key = usr.key
        usr.dispose()
        del self.__usrlist[key]
        pass

    def search_usr(self, sock: socket.socket) -> UsrInfo:
        """
        通过socket 查找用户
        :param sock:
        :return:
        """

        for key, usr in self.__usrlist.items():
            if usr.sock is sock:
                return self.__usrlist[key]
            pass

        return None

    pass
