from src.utils import add_makro
add_makro()

from Makro.MakroCore.CryptographyKit import EncryptPassword as EP, decrypt
from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore import JSONhander, flags, utils

from src.MiddleManKit import permision_handler

import inspect, os

class Render:
    
    Quest_result = ''
    
    def __init__(self, text="", header=""):
        self.text = text
        self.header = header
    
    def Show(self, color=""):
        RD.CommandShow(self.text).Show(color)
    
    def Push(self):
        if permision_handler.notifications:
            RD.CommandShow(self.text, self.header).Push()
    
    def Choice(self, Button1="No", Button2="Yes"):
        Render.Quest_result = RD.CommandShow(self.text).Choice(Button1, Button2)
        return Render.Quest_result
        
    def b3_Choice(self, Button1="No", Button2="Yes", Button3=None):
        Render.Quest_result = RD.CommandShow(self.text).Choice(Button1, Button2, Button3)
        return Render.Quest_result
    
    def Info(self):
        return RD.CommandShow(self.text).Info()
        # return value
    
    def Input(self):
        Render.Quest_result =  RD.CommandShow(self.text, self.header).Input()
        return Render.Quest_result
            
class Data:

    def __init__(self):
        pass
    
    def get_mode(self):
        return flags.MODE
    
    def get_username(self):
        if permision_handler.personal_data:
            return flags.USERNAME
    
    def get_pl(self):
        return flags.pl
    
    def get_ftu(self):
        return flags.FTU
    
    def get_base_folder(self):
        return flags.base_folder
    
    def get_module(self):
        if flags.EnableIntSoft:
            return flags.Module
        else: RD.CommandShow(msg='Call Not Allowed').Show('WARNING')
        
    def IntSoft(self):
        if flags.EnableIntSoft:
            return True
        else:
            RD.CommandShow(msg='Call Not Allowed').Show('WARNING')
            return False

class Cryptography:
    def __init__(self, value):
        self.value = value
    
    def Encrypt(self):
        return EP.encrypt_password(self.value, False)
    
    def decryptor(self):
        return decrypt.Decryptor(self.value).decrypt_password()

class JSON:
    
    def __init__(self, path):
        self.path = path
    
    def json_read(self, filename, parameter):
        return JSONhander.JSONhandle(self.path).read_file(filename, parameter)
    def json_delete(self, array):
        return (JSONhander.JSONhandle(self.path).del_contents(array))
    
class util:    
    
    def build():
        call = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
        permision_handler.Verify_File_Exist(call)
    
    def exit():
        utils.Exit().exit()