from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore import runtimebridge
from Makro.MakroCore import flags
import readline
import atexit
import os

# Arrow Up functionality
kernel = runtimebridge.get_kernel()
# if flags.FTU == '1':
if kernel.get_state('FTU') == '1':
    HISTORY_FILE = os.path.expanduser("~/.my_python_history")
    if os.path.exists(HISTORY_FILE):
        readline.read_history_file(HISTORY_FILE)
    atexit.register(readline.write_history_file, HISTORY_FILE)


def CommandAsk(Module=str):
    kernel = runtimebridge.get_kernel()
    flags.MODE = kernel.get_state('mode')
    flags.USERNAME = kernel.get_state('username')
    flags.sys_detect = kernel.get_state('sys_detect')
    if kernel.get_state('Module') == bool:
    # if isinstance(kernel.get_state('Module'), bool):
    # if flags.Module == bool:
        import Makro.MakroCore.commands as cmd
        # flags.Module = cmd.CommandList
        kernel.request_change('Module', cmd.CommandList)
    else:
        # Mode 2
        if kernel.get_state("mode") == "2":
            # prompt = f"{flags.MD2} | {RD.bcolors.OKBLUE}{flags.USERNAME.capitalize()}{RD.bcolors.WHITE} % "
            prompt = f"{flags.MD2} | {RD.bcolors.OKBLUE}{kernel.get_state('username').capitalize()}{RD.bcolors.WHITE} % "
            return Module(Command=input(prompt).lower())

        # Mode 9
        # if flags.MODE == "9" and not flags.BuildReseted:
        if kernel.get_state("mode") == "9" and not kernel.get_state("BuildReseted"):
            # prompt = f"{flags.MD9} {flags.sys_detect.system} | {flags.sys_detect.machine} | Module Name: {RD.bcolors.OKGREEN}{flags.Module.__name__}{RD.bcolors.WHITE} % "
            prompt = f"{flags.MD9} {kernel.get_state('sys_detect').system} | {kernel.get_state('sys_detect').machine} | Module Name: {RD.bcolors.OKGREEN}{kernel.get_state('Module').__name__}{RD.bcolors.WHITE} % "
            # if flags.Run_Straight_Builtin:
            if kernel.get_state('Run_Straight_Builtin'):
                msg = f"{RD.bcolors.WARNING}Run-Straight-Builtin Enabled{RD.bcolors.WHITE} | {prompt}"
                return Module(Command=input(msg).lower())
            # if flags.Fully_GUI:
            if kernel.get_state('Fully_GUI'):
                RD.CommandShow(msg=f"{flags.MD9} {flags.sys_detect.system} | {flags.sys_detect.machine} | Expreimental GUI").Input()
                try:
                    return Module(Command=RD.Quest_result.lower())
                except AttributeError:
                    return RD.CommandShow('\n').Show()
            return Module(Command=input(prompt).lower())

        # Safe Mode 3
        if flags.MODE == "3":
            prompt = f'{RD.bcolors.WARNING}{flags.MD3}{RD.bcolors.WHITE}'
            # flags.safe_md = True
            kernel.request_change('safe_md', True)
            return Module(Command=input(prompt).lower())

        # Default Mode 1
        prompt = f"{flags.Default_text} | {RD.bcolors.OKCYAN}{flags.USERNAME.capitalize()}{RD.bcolors.WHITE} $ "
        return Module(Command=input(prompt).lower())