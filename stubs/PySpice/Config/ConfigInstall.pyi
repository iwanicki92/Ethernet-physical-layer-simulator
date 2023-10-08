from _typeshed import Incomplete

class OsFactory:
    def __init__(self) -> None: ...
    @property
    def name(self): ...
    @property
    def on_linux(self): ...
    @property
    def on_windows(self): ...
    @property
    def on_osx(self): ...

OS: Incomplete

class Path:
    pyspice_module_directory: Incomplete
    config_directory: Incomplete

class Logging:
    default_config_file: str
    directories: Incomplete
    @staticmethod
    def find(config_file): ...
