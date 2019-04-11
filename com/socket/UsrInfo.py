# -*- coding:utf-8 -*-
import socket
import uuid


class UsrInfo:
    shaking: bool = False
    key: uuid.UUID = None
    sock: socket.socket = None

    def __init__(self, key, sock):
        self.key = key
        self.sock = sock
        pass

    def dispose(self):
        self.key = None
        self.sock = None
        self.shaking = False
        pass

    pass
