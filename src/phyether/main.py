import platform
import distro
import subprocess

from PySpice.Spice.NgSpice.Shared import NgSpiceShared

from phyether.gui import gui
import sqlite3

def _galois_sqlite3_fix(cls):
    if cls.singleton is None:
        cls.singleton = super(type(cls), cls).__new__(cls)
        cls.conn = sqlite3.connect(cls.file, check_same_thread=False)
        cls.cursor = cls.conn.cursor()
    return cls.singleton

def init():
    from galois._databases._interface import DatabaseInterface
    DatabaseInterface.__new__ = _galois_sqlite3_fix
    if platform.system() == "Windows":
        from pathlib import Path
        dll_name = "ngspice.dll"
        root_path = Path(__file__).parent.resolve()

        if (dll_path := root_path / dll_name).exists():
            NgSpiceShared.LIBRARY_PATH = str(dll_path)
        elif (dll_path := root_path / ".." / dll_name).exists():
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
    else:
        raise FileNotFoundError("Unsupported system")

def install_libngspice() -> bool:
    packageInstallers = {
        "debian": ("apt-get", "install", "-y", "libngspice0"),
        "rhel fedora": ('rpm', 'yum', 'install', '-y', 'libngspice0'),
        "centos": ('rpm', 'yum', 'install', '-y', 'libngspice0')
    }
    if packageInstallers[distro.like()][0] == "apt-get":
        subprocess.call(('sudo', 'apt-get', 'update'))
    return subprocess.call(('sudo', *packageInstallers[distro.like()])) == 0

def main():
    print("Starting phyether...")
    gui.main()

if __name__ == "__main__":
    main()
