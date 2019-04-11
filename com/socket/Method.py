# -*- coding:utf8 -*-
import base64
import hashlib
import struct
import math


class Method:
    @staticmethod
    def perform_handshaking(hander):
        """
        websocket 协议升级消息
        :param hander:
        :return:
        """
        headers = Method.__parse_headers(hander)
        token = Method.__generate_token(headers['Sec-WebSocket-Key'])
        token = token.decode('utf-8')  # 先转换成字符串
        upgrade = "HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n" \
                  "Upgrade: WebSocket\r\n" \
                  "Connection: Upgrade\r\n" \
                  "Sec-WebSocket-Accept: %s\r\n\r\n" % token

        upgrade = upgrade.encode('utf8')  # 把整个header信息转换成二进制
        return upgrade
        pass

    @staticmethod
    def __parse_headers(msg):
        headers = {}
        msg = msg.decode('utf-8')
        # print(msg)
        header, data = msg.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, value = line.split(': ', 1)
            headers[key] = value
        headers['data'] = data
        return headers

    @staticmethod
    def __generate_token(msg):
        # 通过客户端的 header 的Sec-WebSocket-Key和固定串生成Sec-WebSocket-Accept 进行握手
        key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        key = key.encode("utf-8")
        ser_key = hashlib.sha1(key).digest()
        return base64.b64encode(ser_key)

    @staticmethod
    def decode(data) -> bytearray:
        """
        解码
        """
        v = data[1] & 0x7f  # 127
        # print('v',v)
        if v == 0x7e:
            p = 4
        elif v == 0x7f:
            p = 10
        else:
            p = 2

        mask = data[p:p + 4]
        decoded = data[p + 4:]
        bytes_list = bytearray()
        for i in range(len(decoded)):
            chunk = decoded[i] ^ mask[i % 4]
            bytes_list.append(chunk)

        return bytes_list

    @staticmethod
    def encode(msg) -> bytes:
        msg_len = len(msg)

        back_msg_list = []

        back_msg_list.append(struct.pack('B', 130))  # 写入固定的head 129(0x18 表示文本格式) 130(0x82 表示二进制)
        # 对消息的固定处理方式开始:
        if msg_len <= 125:  # 报文长度小于126 直接写入长度
            back_msg_list.append(struct.pack('b', msg_len))
        elif msg_len <= 65535:  # 长度小于 2^16-1 需要填充一个字节的数字126 再写入报文长度
            back_msg_list.append(struct.pack('b', 126))  # 填充字节
            back_msg_list.append(struct.pack('>H', msg_len))  # 写入长度 大端格式的unsigned short(16位 2个字节)
        elif msg_len <= (math.pow(2, 64) - 1):  # 报文的最大长度2^64-1
            back_msg_list.append(struct.pack('b', 127))  # 填充字节
            back_msg_list.append(struct.pack('>Q', msg_len))  # 写入长度 大端格式的 unsigned long long (64位 8个字节)
        else:
            print("the message is too long to send in a time")
            return bytes()

        message = bytes()
        for c in back_msg_list:
            message += c

        message += msg
        return message
