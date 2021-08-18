import sys
from cx_Freeze import setup, Executable
setup(
    name = "Econ_Tool",
    version = 1,
    description = "",
    executables = [Executable('qt_gui.py', base = 'Win32GUI')]
)