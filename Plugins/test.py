from src.utils import add_depend, sys, kernel
add_depend(str(sys.argv[1]))

from Makro.MakroCore.RendererKit import Renderer as RD

RD.CommandShow(kernel.get_state("enable_audio")).Show()