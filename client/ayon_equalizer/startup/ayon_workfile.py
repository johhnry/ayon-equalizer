#
# 3DE4.script.name:     Work files ...
# 3DE4.script.gui:      Main Window::Ayon
# 3DE4.script.comment:  Open AYON Publisher tool
#

from ayon_core.pipeline import install_host, is_installed
from ayon_equalizer.api import EqualizerHost
from ayon_core.tools.utils import host_tools


def install_3de_host():
    print("Running AYON integration ...")
    install_host(EqualizerHost())


if not is_installed():
    install_3de_host()

# show the UI
print("Opening Workfile tool window ...")
host_tools.show_workfiles(
    parent=EqualizerHost.get_host().get_main_window())