from ..Tools.StringTools import join_dict as join_dict, join_list as join_list, str_spice as str_spice
from ..Unit import U_A as U_A, U_Degree as U_Degree, U_F as U_F, U_H as U_H, U_Hz as U_Hz, U_V as U_V, U_m as U_m, U_s as U_s, U_Ω as U_Ω
from .ElementParameter import BoolKeyParameter as BoolKeyParameter, ElementNamePositionalParameter as ElementNamePositionalParameter, ExpressionKeyParameter as ExpressionKeyParameter, ExpressionPositionalParameter as ExpressionPositionalParameter, FlagParameter as FlagParameter, FloatKeyParameter as FloatKeyParameter, FloatPairKeyParameter as FloatPairKeyParameter, FloatPositionalParameter as FloatPositionalParameter, FloatTripletKeyParameter as FloatTripletKeyParameter, InitialStatePositionalParameter as InitialStatePositionalParameter, IntKeyParameter as IntKeyParameter, ModelPositionalParameter as ModelPositionalParameter
from .Netlist import AnyPinElement as AnyPinElement, Element as Element, FixedPinElement as FixedPinElement, NPinElement as NPinElement, OptionalPin as OptionalPin
from _typeshed import Incomplete

class DipoleElement(FixedPinElement):
    PINS: Incomplete

class TwoPortElement(FixedPinElement):
    PINS: Incomplete

class SubCircuitElement(NPinElement):
    ALIAS: str
    PREFIX: str
    subcircuit_name: Incomplete
    parameters: Incomplete
    def __init__(self, netlist, name, subcircuit_name, *nodes, **parameters) -> None: ...
    def copy_to(self, netlist): ...
    def format_spice_parameters(self): ...

class Resistor(DipoleElement):
    ALIAS: str
    PREFIX: str
    resistance: Incomplete
    ac: Incomplete
    multiplier: Incomplete
    scale: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete
    noisy: Incomplete

class SemiconductorResistor(DipoleElement):
    ALIAS: str
    PREFIX: str
    resistance: Incomplete
    model: Incomplete
    length: Incomplete
    width: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete
    multiplier: Incomplete
    ac: Incomplete
    scale: Incomplete
    noisy: Incomplete

class BehavioralResistor(DipoleElement):
    ALIAS: str
    PREFIX: str
    resistance_expression: Incomplete
    tc1: Incomplete
    tc2: Incomplete

class Capacitor(DipoleElement):
    ALIAS: str
    PREFIX: str
    capacitance: Incomplete
    model: Incomplete
    multiplier: Incomplete
    scale: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete
    initial_condition: Incomplete

class SemiconductorCapacitor(DipoleElement):
    ALIAS: str
    PREFIX: str
    capacitance: Incomplete
    model: Incomplete
    length: Incomplete
    width: Incomplete
    multiplier: Incomplete
    scale: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete
    initial_condition: Incomplete

class BehavioralCapacitor(DipoleElement):
    ALIAS: str
    PREFIX: str
    capacitance_expression: Incomplete
    tc1: Incomplete
    tc2: Incomplete

class Inductor(DipoleElement):
    ALIAS: str
    PREFIX: str
    inductance: Incomplete
    model: Incomplete
    nt: Incomplete
    multiplier: Incomplete
    scale: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete
    initial_condition: Incomplete

class BehavioralInductor(DipoleElement):
    ALIAS: str
    PREFIX: str
    inductance_expression: Incomplete
    tc1: Incomplete
    tc2: Incomplete

class CoupledInductor(AnyPinElement):
    ALIAS: str
    PREFIX: str
    inductor1: Incomplete
    inductor2: Incomplete
    coupling_factor: Incomplete
    def __init__(self, name, *args, **kwargs) -> None: ...

class VoltageControlledSwitch(TwoPortElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    model: Incomplete
    initial_state: Incomplete

class CurrentControlledSwitch(DipoleElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    source: Incomplete
    model: Incomplete
    initial_state: Incomplete

class VoltageSource(DipoleElement):
    ALIAS: str
    PREFIX: str
    dc_value: Incomplete

class CurrentSource(DipoleElement):
    ALIAS: str
    PREFIX: str
    dc_value: Incomplete

class VoltageControlledCurrentSource(TwoPortElement):
    ALIAS: str
    PREFIX: str
    transconductance: Incomplete
    multiplier: Incomplete

class VoltageControlledVoltageSource(TwoPortElement):
    ALIAS: str
    PREFIX: str
    voltage_gain: Incomplete

class CurrentControlledCurrentSource(DipoleElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    source: Incomplete
    current_gain: Incomplete
    multiplier: Incomplete

class CurrentControlledVoltageSource(DipoleElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    source: Incomplete
    transresistance: Incomplete

class BehavioralSource(DipoleElement):
    ALIAS: str
    PREFIX: str
    current_expression: Incomplete
    voltage_expression: Incomplete
    tc1: Incomplete
    tc2: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete

class NonLinearVoltageSource(DipoleElement):
    ALIAS: str
    PREFIX: str
    VALID_KWARGS: Incomplete
    expression: Incomplete
    table: Incomplete
    def __init__(self, name, *args, **kwargs) -> None: ...

class NonLinearCurrentSource(DipoleElement):
    ALIAS: str
    PREFIX: str
    transconductance: Incomplete

class Diode(FixedPinElement):
    ALIAS: str
    PREFIX: str
    PINS: Incomplete
    model: Incomplete
    area: Incomplete
    multiplier: Incomplete
    pj: Incomplete
    off: Incomplete
    ic: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete

class BipolarJunctionTransistor(FixedPinElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    PINS: Incomplete
    model: Incomplete
    area: Incomplete
    areac: Incomplete
    areab: Incomplete
    multiplier: Incomplete
    off: Incomplete
    ic: Incomplete
    temperature: Incomplete
    device_temperature: Incomplete

class JfetElement(FixedPinElement):
    PINS: Incomplete

class JunctionFieldEffectTransistor(JfetElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    model: Incomplete
    area: Incomplete
    multiplier: Incomplete
    off: Incomplete
    ic: Incomplete
    temperature: Incomplete

class Mesfet(JfetElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    model: Incomplete
    area: Incomplete
    multiplier: Incomplete
    off: Incomplete
    ic: Incomplete

class Mosfet(FixedPinElement):
    ALIAS: str
    LONG_ALIAS: str
    PREFIX: str
    PINS: Incomplete
    model: Incomplete
    multiplier: Incomplete
    length: Incomplete
    width: Incomplete
    drain_area: Incomplete
    source_area: Incomplete
    drain_perimeter: Incomplete
    source_perimeter: Incomplete
    drain_number_square: Incomplete
    source_number_square: Incomplete
    off: Incomplete
    ic: Incomplete
    temperature: Incomplete
    nfin: Incomplete

class LosslessTransmissionLine(TwoPortElement):
    ALIAS: str
    PREFIX: str
    impedance: Incomplete
    time_delay: Incomplete
    frequency: Incomplete
    normalized_length: Incomplete
    def __init__(self, name, *args, **kwargs) -> None: ...

class LossyTransmission(TwoPortElement):
    ALIAS: str
    PREFIX: str
    model: Incomplete

class CoupledMulticonductorLine(NPinElement):
    ALIAS: str
    PREFIX: str
    model: Incomplete
    length: Incomplete
    def __init__(self, netlist, name, *nodes, **parameters) -> None: ...

class UniformDistributedRCLine(FixedPinElement):
    ALIAS: str
    PREFIX: str
    PINS: Incomplete
    model: Incomplete
    length: Incomplete
    number_of_lumps: Incomplete

class SingleLossyTransmissionLine(TwoPortElement):
    ALIAS: str
    PREFIX: str
    model: Incomplete
    length: Incomplete

class XSpiceElement(NPinElement):
    ALIAS: str
    PREFIX: str
    model: Incomplete
    def __init__(self, netlist, name, *nodes, **parameters) -> None: ...

class GSSElement(NPinElement):
    ALIAS: str
    PREFIX: str
    def __init__(self) -> None: ...
