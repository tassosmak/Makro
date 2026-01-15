import sys

kernel = None

def add_depend(path):
    global kernel
    substring = "Makro/MakroCore"
    fix_path = ""
    str_list = path.split(substring)
    for element in str_list:
        fix_path += element    
    
    sys.path.insert(0, fix_path)
    
    from Makro.MakroCore import credentials as cred, utils, SystemCalls, runtimebridge
    kernel = runtimebridge.get_kernel('default', True)
    utils.pl_finder()
    SystemCalls.SystemCalls.get_folder()
    cred.get_credentials(False, f'{path}/users/default.json')
    utils.clear_screen()
    