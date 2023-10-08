from ..Simulation import CircuitSimulator as CircuitSimulator
from .Server import SpiceServer as SpiceServer
from .Shared import NgSpiceShared as NgSpiceShared

class NgSpiceCircuitSimulator(CircuitSimulator):
    SIMULATOR: str
    def __init__(self, circuit, **kwargs) -> None: ...

class NgSpiceSubprocessCircuitSimulator(NgSpiceCircuitSimulator):
    def __init__(self, circuit, **kwargs) -> None: ...

class NgSpiceSharedCircuitSimulator(NgSpiceCircuitSimulator):
    def __init__(self, circuit, **kwargs) -> None: ...
    @property
    def ngspice(self): ...
