import os
from os.path import dirname, abspath, join
from ctypes import c_char, c_char_p, POINTER, CDLL

path = os.path.dirname(os.path.realpath(__file__))
dll = CDLL(os.path.join(root, 'target/debug/libspeechtux.so'))

def read(text, **kwargs):
    speed = kwargs.get('speed', -1)
    level = kwargs.get('level', -1)
    volume = kwargs.get('volume', -1)
    dll.read(text, speed, level, volume)
