#!/usr/bin/env PYTHONIOENCODING="utf-8" python

#  native interface for netbase if you want to run the server locally

#  TODO!

from ctypes import cdll
netbase = cdll.LoadLibrary('netbase')
netbase.init()
# netbase.execute(":c")
netbase.execute("test")
# netbase.query("test")