import tkinter
from typing import Mapping, cast

from PySpice.Probe.WaveForm import WaveForm
from matplotlib.axes import Axes

import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import EngFormatter

import numpy
from numpy.typing import NDArray

from phyether import main
from phyether.dac import DAC
from phyether.ethernet_cable import EthernetCable

root = tkinter.Tk()
root.wm_title("Simulation")
root.bind("<Escape>", lambda _: root.destroy())

main.init()
cable = EthernetCable(dac=DAC(1, 3, 4), output_impedance=85, length=50, resistance=0.5, transmission_type='lossy')

fig = plt.figure(figsize=(18, 6))
axs: Mapping[int, Axes]
fig, axs = plt.subplots(4, 1, figsize=(18, 8), sharex=True, sharey=False)
fig.text(0.5, 0.04, 'Time', ha='center')
fig.text(0.04, 0.5, 'Voltage (V)', va='center', rotation='vertical')
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea

toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

input_field = tkinter.Entry(master=root)

def _prep_plots(axs: Mapping[int, Axes]):
    for ax_index, pair in enumerate({'A', 'B', 'C', 'D'}):
        axs[ax_index].cla()
        axs[ax_index].text(0, 1, f"Pair {pair}")
        axs[ax_index].grid()
        axs[ax_index].set_ylim(-3, 3)
        axs[ax_index].xaxis.set_major_formatter(EngFormatter(unit='s'))

def update_simulation():
    a = [int(symbol) for symbol in input_field.get().split()
                    if symbol.removeprefix('-').isdecimal()]
    b = [-int(symbol) for symbol in input_field.get().split()
                    if symbol.removeprefix('-').isdecimal()]
    c = [(-int(symbol) + int(int(symbol)/2)) for symbol in input_field.get().split()
                    if symbol.removeprefix('-').isdecimal()]
    d = [(int(symbol) - int(int(symbol)/2)) for symbol in input_field.get().split()
                    if symbol.removeprefix('-').isdecimal()]

    analysis = cable.simulate((a,b,c,d), 0)

    _prep_plots(axs)

    for index, pair in enumerate({'A', 'B', 'C', 'D'}):
        v_in: WaveForm = analysis[f'{pair}_vin+'] - analysis[f'{pair}_vin-']
        v_out: WaveForm = analysis[f'{pair}_vout+'] - analysis[f'{pair}_vout-']

        vx_out_transformed = cast(numpy.ndarray, analysis.time - cable.transmission_delay)
        vx_out_transformed = vx_out_transformed[vx_out_transformed>=0]
        # trim v_in where nothing happens after shifting v_out
        vx_in_transformed = analysis.time[analysis.time<(analysis.time[-1] - cable.transmission_delay)]

        axs[index].plot(
            vx_in_transformed,
            v_in[:len(vx_in_transformed)],
            'blue',
            vx_out_transformed,
            v_out[-len(vx_out_transformed):],
            'red'
        )

        fig.legend(['v(in+, in-)', 'v(out+, out-)'], loc='upper right')

    canvas.draw()

for i in range(4):
    axs[i].plot()
    axs[i].grid()
canvas.draw()

button_simulate = tkinter.Button(master=root, text="Simulate", command=update_simulation)

label = tkinter.Label(master=root, text="Wpisz symbole oddzielone spacjami <-4,4> np.: -1 0 4 -3 2")
label.pack(side=tkinter.TOP, fill='x')
input_field.pack(side=tkinter.TOP, fill='x')
button_simulate.pack(side=tkinter.TOP)
toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()
