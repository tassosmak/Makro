from Makro.MakroCore.LoginKit.login_handler import LoginHandler
from Makro.MakroCore import runtimebridge
from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore import credentials as cred, flags
from Makro.MakroCore.utils import clear_gui, pl_finder
from Makro.MakroCore.SystemCalls import SystemCalls
# from Makro.Drivers.AudioKit import Audio
from Makro.MakroCore.FTU import FTU_init
import sys


def loader(run=True):
    global kernel
    
    SystemCalls().get_folder()
    kernel = runtimebridge.get_kernel("default", True)
    pl_finder()
    clear_gui()
    # if not flags.EnableIntSoft:
    #     Audio.play('MakroCore/AudioKit/src/Boot.mp3')
    if cred._get_propiatery():
        # if flags.UserLess_Connection and run:
        if kernel.get_state('UserLess_Connection') and run:
            advanced_init()
        # elif flags.GO_TO_FTU and run:
        elif kernel.get_state('GO TO FTU') and run:
            FTU = FTU_init(False)
            FTU.run()
        else:
            if run:
                LoginHandler.run()
                init()
            else:
                # cred.get_credentials(False, f'{flags.base_folder}/users/default.json')
                kernel = runtimebridge.get_kernel("default", True)
    else:
        if run:
            LoginHandler.run()
            init()
        else:
            # cred.get_credentials(False, f'{flags.base_folder}/users/default.json')
            kernel = runtimebridge.get_kernel("default", True)
        
def init():
    try:
        with open(f'{kernel.get_folder()}/src/history.log', 'a') as f:
            f.write(f'\n{SystemCalls.get_time()}')
    except FileNotFoundError:
        from os import mkdir
        mkdir(f'{flags.base_folder}/src')
        with open('src/history.log', 'w+') as f:
            f.write(f'\n{SystemCalls.get_time()}')

        
def advanced_init():
    # if flags.pl == '1':
        # flags.EnableGUI = True
    # flags.EnableIntSoft = True
    # flags.USERNAME = "Lets Keep It Private"
    # flags.MODE = '9'
    # flags.FTU = '1'
    # RD.CommandShow(sys.version).Show('GREEN')
    # RD.CommandShow(msg="Lets keep it private").Push()
    if kernel.get_state('pl') == '1':
        kernel.request_change('enable_gui', True)
    kernel.request_change("IntSoft", True)
    kernel.request_change('username', "Lets Keep It Private")
    kernel.request_change('mode', '9')
    kernel.request_change('FTU', '1')
    RD.CommandShow(sys.version).Show('GREEN')
    RD.CommandShow(msg="Lets keep it private").Push()