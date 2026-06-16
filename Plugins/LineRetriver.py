from src.MiddleManKit.MiddleMan import *
util.build()

try:
    import clipboard
except ModuleNotFoundError:
    Render("Clipboard Module Is missing").Show('WARNING')
    util.exit()

line_to_copy="0"
def Lastlines():
    global line_to_copy
    with open(f'{base_folder}/src/history.log', "r") as file:
        for line in (file.readlines() [-1:]):
            line_to_copy=line

base_folder = Data().get_base_folder()
Lastlines()
clipboard.copy(str(line_to_copy))
Render("DONE").Show('OKGREEN')