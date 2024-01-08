import subprocess
import platform

shared = ("pyinstaller", "src/phyether/main.py", "-n", "phyether", "--noconfirm", "--exclude-module", "PyQt6", "--collect-all", "phyether", "--collect-all", "PySpice", "--collect-data", "galois")

if platform.system() == "Windows":
    subprocess.call(shared + ("--add-data", "lib:.", "-w"))
elif platform.system() == "Linux":
    subprocess.call(shared)
else:
    print("System not supported")
