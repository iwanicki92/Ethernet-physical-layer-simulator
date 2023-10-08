from ..Math import amplitude_to_rms as amplitude_to_rms, rms_to_amplitude as rms_to_amplitude
from ..Tools.StringTools import join_dict as join_dict, join_list as join_list, str_spice as str_spice, str_spice_list as str_spice_list
from ..Unit import as_A as as_A, as_Hz as as_Hz, as_V as as_V, as_s as as_s
from .BasicElement import CurrentSource as CurrentSource, VoltageSource as VoltageSource
from _typeshed import Incomplete

class SourceMixinAbc:
    AS_UNIT: Incomplete

class VoltageSourceMixinAbc:
    AS_UNIT = as_V

class CurrentSourceMixinAbc:
    AS_UNIT = as_A

class SinusoidalMixin(SourceMixinAbc):
    dc_offset: Incomplete
    ac_magnitude: Incomplete
    offset: Incomplete
    amplitude: Incomplete
    frequency: Incomplete
    delay: Incomplete
    damping_factor: Incomplete
    def __init__(self, dc_offset: int = ..., ac_magnitude: int = ..., offset: int = ..., amplitude: int = ..., frequency: int = ..., delay: int = ..., damping_factor: int = ...) -> None: ...
    @property
    def rms_voltage(self): ...
    @property
    def period(self): ...
    def format_spice_parameters(self): ...

class PulseMixin(SourceMixinAbc):
    dc_offset: Incomplete
    initial_value: Incomplete
    pulsed_value: Incomplete
    delay_time: Incomplete
    rise_time: Incomplete
    fall_time: Incomplete
    pulse_width: Incomplete
    period: Incomplete
    phase: Incomplete
    def __init__(self, initial_value, pulsed_value, pulse_width, period, delay_time: int = ..., rise_time: int = ..., fall_time: int = ..., phase: Incomplete | None = ..., dc_offset: int = ...) -> None: ...
    @property
    def frequency(self): ...
    def format_spice_parameters(self): ...

class ExponentialMixin(SourceMixinAbc):
    initial_value: Incomplete
    pulsed_value: Incomplete
    rise_delay_time: Incomplete
    rise_time_constant: Incomplete
    fall_delay_time: Incomplete
    fall_time_constant: Incomplete
    def __init__(self, initial_value, pulsed_value, rise_delay_time: float = ..., rise_time_constant: Incomplete | None = ..., fall_delay_time: Incomplete | None = ..., fall_time_constant: Incomplete | None = ...) -> None: ...
    def format_spice_parameters(self): ...

class PieceWiseLinearMixin(SourceMixinAbc):
    values: Incomplete
    repeat_time: Incomplete
    delay_time: Incomplete
    dc: Incomplete
    def __init__(self, values, repeat_time: Incomplete | None = ..., delay_time: Incomplete | None = ..., dc: Incomplete | None = ...) -> None: ...
    def format_spice_parameters(self): ...

class SingleFrequencyFMMixin(SourceMixinAbc):
    offset: Incomplete
    amplitude: Incomplete
    carrier_frequency: Incomplete
    modulation_index: Incomplete
    signal_frequency: Incomplete
    def __init__(self, offset, amplitude, carrier_frequency, modulation_index, signal_frequency) -> None: ...
    def format_spice_parameters(self): ...

class AmplitudeModulatedMixin(SourceMixinAbc):
    offset: Incomplete
    amplitude: Incomplete
    carrier_frequency: Incomplete
    modulating_frequency: Incomplete
    signal_delay: Incomplete
    def __init__(self, offset, amplitude, modulating_frequency, carrier_frequency, signal_delay) -> None: ...
    def format_spice_parameters(self): ...

class RandomMixin(SourceMixinAbc):
    random_type: Incomplete
    duration: Incomplete
    time_delay: Incomplete
    parameter1: Incomplete
    parameter2: Incomplete
    def __init__(self, random_type, duration: int = ..., time_delay: int = ..., parameter1: int = ..., parameter2: int = ...) -> None: ...
    def format_spice_parameters(self): ...

class SinusoidalVoltageSource(VoltageSource, VoltageSourceMixinAbc, SinusoidalMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class SinusoidalCurrentSource(CurrentSource, CurrentSourceMixinAbc, SinusoidalMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class AcLine(SinusoidalVoltageSource):
    def __init__(self, netlist, name, node_plus, node_minus, rms_voltage: int = ..., frequency: int = ...) -> None: ...

class PulseVoltageSource(VoltageSource, VoltageSourceMixinAbc, PulseMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class PulseCurrentSource(CurrentSource, CurrentSourceMixinAbc, PulseMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class ExponentialVoltageSource(VoltageSource, VoltageSourceMixinAbc, ExponentialMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class ExponentialCurrentSource(CurrentSource, CurrentSourceMixinAbc, ExponentialMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class PieceWiseLinearVoltageSource(VoltageSource, VoltageSourceMixinAbc, PieceWiseLinearMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class PieceWiseLinearCurrentSource(CurrentSource, CurrentSourceMixinAbc, PieceWiseLinearMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class SingleFrequencyFMVoltageSource(VoltageSource, VoltageSourceMixinAbc, SingleFrequencyFMMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class SingleFrequencyFMCurrentSource(CurrentSource, CurrentSourceMixinAbc, SingleFrequencyFMMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class AmplitudeModulatedVoltageSource(VoltageSource, VoltageSourceMixinAbc, AmplitudeModulatedMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class AmplitudeModulatedCurrentSource(CurrentSource, CurrentSourceMixinAbc, AmplitudeModulatedMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class RandomVoltageSource(VoltageSource, VoltageSourceMixinAbc, RandomMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete

class RandomCurrentSource(CurrentSource, CurrentSourceMixinAbc, RandomMixin):
    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs) -> None: ...
    format_spice_parameters: Incomplete
