import ctypes
from ctypes import cdll
lib = cdll.LoadLibrary('./netbase.so')
print(lib._version())

