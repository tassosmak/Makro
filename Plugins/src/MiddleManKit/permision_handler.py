from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore.JSONhander import JSONhandle
from Makro.MakroCore import flags, utils
from pathlib import Path
import os


def Verify_File_Exist(file_name):
    global filesystem, notifications, personal_data
    plugin_name = Path(file_name).stem
    path = f'{flags.base_folder}/../Plugins/{plugin_name}.json'

    try:
        # JSONhandle.read_file(f'{flags.base_folder}/../Plugins/{plugin_name}.json')
        open(path, 'r')
    except FileNotFoundError:
        from src.MiddleManKit.file_handler import gen_file, json_setup
        gen_file(plugin_name)
        json_setup(path, plugin_name)
        
    
    filesystem = JSONhandle(path).read_file('premisions', 'Filesystem')
    print("Filesystem: ", filesystem)
    
    notifications = JSONhandle(path).read_file('premisions', 'Notifications')
    print("Notifications: ", notifications)
    
    personal_data = JSONhandle(path).read_file('premisions', 'Personal_data')
    print("Personal_data: ", personal_data)