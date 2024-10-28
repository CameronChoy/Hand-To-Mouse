import ctypes
from ctypes import wintypes
from enum import Flag
import sys

# Same as winuser.h MOUSEEVENTF
class MouseStatus(wintypes.DWORD):
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

'''
    Win32 mouse_event function
    flags: MouseStatus flags
    dx,dy: Normalized absolute position on screen
    data: MouseWheel movement or X button if flags specified either
    extraInfo: additional info about mouse event
'''
def mouse_event(flags : MouseStatus, dx : wintypes.LONG, dy : wintypes.LONG, data : wintypes.DWORD, extraInfo = 0):
    ctypes.windll.user32.mouse_event(flags, dx,  dy, data, extraInfo)
