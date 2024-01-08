from ..Simulation import CircuitSimulator as CircuitSimulator
from .Server import XyceServer as XyceServer

class XyceCircuitSimulator(CircuitSimulator):
    SIMULATOR: str
    def __init__(self, circuit, **kwargs) -> None: ...
    def str_options(self): ...
