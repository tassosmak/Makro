from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore.utils import is_gui
# from Makro.MakroCore import flags
from Makro.MakroCore import runtimebridge
import subprocess

def SecondaryTask(file_name="0", stay_end=False):
    kernel = runtimebridge.get_kernel()
    # if not flags.safe_md:
    if not kernel.get_state('safe_md'):
        if not file_name=='0':
            import os
            # if not flags.Inside_Thread and is_gui():
            if not kernel.get_state('Inside_Thread') and is_gui():
                # if flags.pl == "1":
                if kernel.get_state('pl') == "1":
                    subprocess.run(f"""osascript -e 'tell application "Terminal" to do script "python3 {str(kernel.get_state('base_folder'))}/../Plugins/{file_name}.py {str(kernel.get_state('base_folder'))}"'""", shell=True, capture_output=True, check=True, encoding="utf-8")
                # elif flags.pl == "2":
                elif kernel.get_state('pl') == "2":
                    if stay_end:
                        os.system(f"start cmd /k py  {kernel.get_state('base_folder')}/../Plugins/{file_name}.py {str(kernel.get_state('base_folder'))}")
                    else:
                        os.system(f"start cmd /c py  {kernel.get_state('base_folder')}/../Plugins/{file_name}.py {str(kernel.get_state('base_folder'))}")
                else:
                    # os.system(f"python3 {flags.base_folder}/../plugins/{file_name}.py {str(flags.base_folder)}")
                    subprocess.run(f"python3 {kernel.get_state('base_folder')}/../Plugins/{file_name}.py {str(kernel.get_state('base_folder'))}", shell=True, capture_output=True, check=True, encoding="utf-8")
            else:
                os.system(f"python3 {kernel.get_state('base_folder')}/../Plugins/{file_name}.py {str(kernel.get_state('base_folder'))}")
    else:
        RD.CommandShow(msg="Safe Mode is enabled, cannot run secondary tasks.").Show("WARNING")