import tkinter
from typing import Mapping, cast

from PySpice.Probe.WaveForm import WaveForm
from matplotlib.axes import Axes

import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import EngFormatter

import numpy

from phyether import main
from phyether.dac import DAC
from phyether.twisted_pair import TwistedPair

from bitarray import bitarray

def _bits_to_dsq128(bits : bitarray) -> tuple[int, int]:
    """
    converts 7-bit frame into 2D DSQ128 symbol
    """

    assert(len(bits) == 7)
    u = bits[0:3]
    c = bits[3:]

    # Step 1
    x13 = -u[0] & u[2]
    x12 = u[0] ^ u[2]
    x11 = c[0]
    x10 = c[0] ^ c[1]
    x23 = (u[1] & u[2]) + (u[0] & -u[1])
    x22 = u[1] ^ u[2]
    x21 = c[2]
    x20 = c[2] ^ c[3]

    # Step 2
    x1 = 8*x13 + 4*x12 + 2*x11 + x10
    x2 = 8*x23 + 4*x22 + 2*x21 + x20

    # Step 3
    y1 = (x1 + x2) % 16
    y2 = (-x1 + x2) % 16

    # Step 4

    return 2*y1 - 15, 2*y2 - 15



root = tkinter.Tk()
root.wm_title("Simulation")
root.bind("<Escape>", lambda _: root.destroy())

main.init()
pairs = [
    TwistedPair(dac=DAC(1, 3, high_symbol=15, symbol_step=2, max_voltage=2.5), output_impedance=85, length=30, resistance=0.5, transmission_type='lossy'),
    TwistedPair(dac=DAC(1, 3, high_symbol=15, symbol_step=2, max_voltage=2.5), output_impedance=85, length=30, resistance=0.5, transmission_type='lossy'),
    TwistedPair(dac=DAC(1, 3, high_symbol=15, symbol_step=2, max_voltage=2.5), output_impedance=85, length=30, resistance=0.5, transmission_type='lossy'),
    TwistedPair(dac=DAC(1, 3, high_symbol=15, symbol_step=2, max_voltage=2.5), output_impedance=85, length=30, resistance=0.5, transmission_type='lossy')
]

fig, axs = plt.subplots(2, 2, figsize=(18, 8), sharex=True, sharey=True)
plt.figure(figsize=(36, 12))
ax_indexes: list[tuple[int, int]] = [
    (0,0),
    (1,0),
    (0,1),
    (1,1)
]

def _prep_plots(axs: Mapping[tuple[int, int], Axes]):
    for i, ax_index in enumerate(ax_indexes):
        axs[ax_index].cla()
        axs[ax_index].set_title("Pair {}".format(str(i+1)))
        axs[ax_index].grid()
        axs[ax_index].set(xlabel="Time")
        axs[ax_index].set(ylabel="Voltage (V)")
        axs[ax_index].set_ylim(-3, 3)
        axs[ax_index].xaxis.set_major_formatter(EngFormatter(unit='s'))


_prep_plots(axs)

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea
toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

input_field = tkinter.Entry(master=root)

def update_simulation():
    bits = input_field.get().split()
    _prep_plots(axs)
    for i, pair in enumerate(pairs):
        symbols = _bits_to_dsq128(bitarray([int(bit, 2) for bit in bits[0+i:7+i]]))
        analysis = pair.simulate(list(symbols))
        v_in: WaveForm = analysis['vin+'] - analysis['vin-']
        v_out: WaveForm = analysis['vout+'] - analysis['vout-']

        vx_out_transformed = cast(numpy.ndarray, analysis.time - pair.transmission_delay)
        vx_out_transformed = vx_out_transformed[vx_out_transformed>=0]
        # trim v_in where nothing happens after shifting v_out
        vx_in_transformed = analysis.time[analysis.time<(analysis.time[-1] - pair.transmission_delay)]

        axs[ax_indexes[i]].plot(
            vx_in_transformed,
            v_in[:len(vx_in_transformed)],
            'blue',
            vx_out_transformed,
            v_out[-len(vx_out_transformed):],
            'red'
        )
        fig.legend(['v(in+, in-)', 'v(out+, out-)'], loc='upper left')
        canvas.draw()

plt.plot()
canvas.draw()

button_simulate = tkinter.Button(master=root, text="Simulate", command=update_simulation)

label = tkinter.Label(master=root, text="Wpisz 28 bitów oddzielonych spacjami np.: 1 0 1 0 1 1 0 1 0 1 0 1 1 0 1 0 1 0 1 1 0 1 0 1 0 1 1 0")
label.pack(side=tkinter.TOP, fill='x')
input_field.pack(side=tkinter.TOP, fill='x')
button_simulate.pack(side=tkinter.TOP)
toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()
