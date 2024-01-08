from .RawFile import RawFile as RawFile
from PySpice.Config import ConfigInstall as ConfigInstall

class XyceServer:
    XYCE_COMMAND: str
    def __init__(self, **kwargs) -> None: ...
    def __call__(self, spice_input): ...
