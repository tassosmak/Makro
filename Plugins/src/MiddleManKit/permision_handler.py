from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore.JSONhander import JSONhandle
from Makro.Plugins.src.MiddleManKit import info
from Makro.MakroCore import flags
# from pathlib import Path


def get_permisions(show=False):

    # info.plugin_name = Path(info.filename).stem
    info.path = f'{flags.base_folder}/../Plugins/{info.filename}.json'

    # RD.CommandShow(f"Plugin: {info.filename} is requesting access to your system., {info.path}").Info() # TODO: DELETE IT
    # Plugin: test is requesting access to your system., /Users/tassosmak/Downloads/PyTerminal/Makro/MakroCore/../Plugins/test.json
    # RD.CommandShow(f"1): {info.plugin_name} 2){info.filename}").Info() # TODO: DELETE IT

    try:
        info.filesystem = JSONhandle(info.path).read_file('premisions', 'Filesystem')
        if show:
            print("Filesystem: ", info.filesystem)

        info.notifications = JSONhandle(info.path).read_file('premisions', 'Notifications')
        if show:
            print("Notifications: ", info.notifications)

        info.personal_data = JSONhandle(info.path).read_file('premisions', 'Personal_data')
        if show:
            print("Personal_data: ", info.personal_data)
    except:
        from src.MiddleManKit.file_handler import gen_file, json_setup
        gen_file()
        json_setup(info.path, info.filename)
        get_permisions()