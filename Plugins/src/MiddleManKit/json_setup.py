from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore.JSONhander import JSONhandle
from Makro.MakroCore.utils import clear_screen

def json_setup(path, name):
    clear_screen()
    RD.CommandShow(f"Welcome To The {name} Plugin Setup").Show('OKGREEN')
    if RD.CommandShow("Do you want to give access to your filesystem?").Choice() == "Yes":
        JSONhandle(path).edit_json('premisions', 'Filesystem', 'true')
    if RD.CommandShow("Do you want to recieve notifications from the plugin?").Choice() == "Yes":
        JSONhandle(path).edit_json('premisions', 'Notifications', 'true')
    if RD.CommandShow("Do you want to give access to your Personal Data?").Choice() == "Yes":
        JSONhandle(path).edit_json('premisions', 'Personal_Data', 'true')
    