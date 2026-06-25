from Makro.MakroCore.RendererKit import Renderer as RD
from src.MiddleManKit import flags as middle_flags
from Makro.MakroCore.JSONhander import JSONhandle
from Makro.MakroCore import utils, flags

def json_setup(path, name):
    utils.clear_screen()
    RD.CommandShow(f"Welcome To The {name} Plugin Setup").Show('OKGREEN')
    if RD.CommandShow("Do you want to give access to your filesystem?").Choice() == "Yes":
        JSONhandle(path).edit_json('premisions', 'Filesystem', True)
    if RD.CommandShow("Do you want to recieve notifications from the plugin?").Choice() == "Yes":
        JSONhandle(path).edit_json('premisions', 'Notifications', True)
    if RD.CommandShow("Do you want to give access to your Personal Data?").Choice() == "Yes":
        JSONhandle(path).edit_json('premisions', 'Personal_data', True)

def gen_file(filename=str):
    with open(f'{flags.base_folder}/../Plugins/{filename}.json', 'w+') as recover:
        recover.write('''{
        "premisions": {
            "Filesystem": false,
            "Notifications": false,
            "Personal_data": false
        }
    }''')
        
def ask_perm(perm_name):
    ''''
    UNDER CONSTRUCTION - NOT ENABLED YET
    '''
    RD.CommandShow(f"Plugin: {middle_flags.caller_file} requested access to {perm_name}\n do you want to give it?").Choice()
    if RD.Quest_result == "Yes":
        JSONhandle