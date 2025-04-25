#Lua implementation in Wikiduction
import os, sys
from main import *

lua_dir = "include"
class Lua_Ext:
    def load_lua_ext(self):
        for i in os.listdir(lua_dir):
            ext = open(i, 'r')
            lua.execute(ext.read())