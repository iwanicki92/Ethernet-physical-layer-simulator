import platform

from PySpice.Spice.NgSpice.Shared import NgSpiceShared

def init():
    if platform.system() == "Windows":
        from pathlib import Path
        dll_name = "ngspice.dll"
        root_path = Path(__file__).parent.resolve()

        if (dll_path := root_path / dll_name).exists():
            NgSpiceShared.LIBRARY_PATH = str(dll_path)
        elif (dll_path := root_path / "../../lib" / dll_name).exists():
            NgSpiceShared.LIBRARY_PATH = str(dll_path)
        else:
            raise FileNotFoundError("Couldn't find ngspice.dll!")
    elif platform.system() in {"Linux", "Darwin"}:
        import ctypes.util
        libngspice = ctypes.util.find_library("ngspice")
        if libngspice is None:
            raise FileNotFoundError("Couldn't find libngspice library!")
        else:
            NgSpiceShared.LIBRARY_PATH = libngspice

def main():
    try:
        init()
    except FileNotFoundError as ex:
        # couldn't find ngspice library, do something
        print(ex)

    print("Starting phyether...")
