from Makro.MakroCore.JSONhander import JSONhandle
from Makro.MakroCore import flags
from pathlib import Path

def get_permisions(file_name, show=False):
    global filesystem, notifications, personal_data

    plugin_name = Path(file_name).stem
    path = f'{flags.base_folder}/../Plugins/{plugin_name}.json'
    # while True: print(path)

    try:
        filesystem = JSONhandle(path).read_file('premisions', 'Filesystem')
        if show:
            print("Filesystem: ", filesystem)

        notifications = JSONhandle(path).read_file('premisions', 'Notifications')
        if show:
            print("Notifications: ", notifications)

        personal_data = JSONhandle(path).read_file('premisions', 'Personal_data')
        if show:
            print("Personal_data: ", personal_data)
    except:
        # from Makro.MakroCore.RendererKit import Renderer as RD
        # RD.CommandShow(f"The {file_name} plugin is missing the premisions key in the json file.", "Plugin System").Info()
        from src.MiddleManKit.file_handler import gen_file, json_setup
        gen_file(file_name)
        json_setup(path, file_name)
        get_permisions(file_name, show)