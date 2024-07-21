import socket
import struct
from enum import Flag

# Same as winuser.h MOUSEEVENTF
class MouseStatus(Flag):
    IDLE = 0
    ABSOLUTE = 32768
    MOVE = 1
    LMOUSE_DOWN = 2
    LMOUSE_UP = 4
    RMOUSE_DOWN = 8
    RMOUSE_UP = 16
    MIDDLE_DOWN = 32
    MIDDLE_UP = 64
    WHEEL = 2048
    X_DOWN = 128
    X_UP = 256
    HWHEEL = 4096

class MsgType():
    
    def hand_update(x : float, y : float, mouse_status : MouseStatus):
        return b'\x41' + mouse_status.value.to_bytes(4, "little") + struct.pack('<2f', *[x, y])


class Client:
    def __init__(self, address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.address = address
        self.connect()
    
    def send(self, data : bytes):
        print("sending", data)
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
