try:
    if not __name__ == '__main__':
        from Makro.MakroCore import Input_Output as IO, flags
        from Makro.MakroCore.SystemCalls import SystemCalls
        from Makro.MakroCore import runtimebridge

    def core():
        kernel = runtimebridge.get_kernel()
        # if flags.MODE in flags.ModeList or flags.MODE == '3':
        if kernel.get_state('mode') in flags.ModeList or kernel.get_state('mode') == '3':
            # IO.CommandAsk(Module=flags.Module)
            IO.CommandAsk(Module=kernel.get_state('Module'))
            # if not flags.MODE == '3' or flags.MODE == '9':
            #    SystemCalls.append_to_history(flags.LCommand)
        else:
            raise IndexError

except:
    from Makro.MakroCore.utils import Exit
    Exit.error_exit()
