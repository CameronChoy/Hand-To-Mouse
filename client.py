import socket
import struct

class MsgType():
    def hand_coords(x, y):
        return struct.pack('<c2f', *[b'1', x, y])

    def lmouse_on():
        return struct.pack('<c', *[b'2'])
    def lmouse_off():
        return struct.pack('<c', *[b'3'])

    def rmouse_on():
        return struct.pack('<c', *[b'4'])
    def rmouse_off():
        return struct.pack('<c', *[b'5'])

    def scroll_up_on():
        return struct.pack('<c', *[b'6'])
    def scroll_up_off():
        return struct.pack('<c', *[b'7'])

    def scroll_down_on():
        return struct.pack('<c', *[b'8'])
    def scroll_down_off():
        return struct.pack('<c', *[b'9'])


class Client:
    def __init__(self, address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.address = address
        self.connect()
    
    def send(self, data : bytes):
        if not self.connected: return False
       
        self.socket.send(data)
        return True
    
    def recv(self):
        return self.socket.recv(1024)
    
    def connect(self):
        try:
            self.socket.connect(self.address)
            self.connected = True
        except (ConnectionError) as e:
            print(f"Client connection failed {self.address=} {e}")
            return False
        return True

    def __del__(self):
        if self.connected: self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
