import tkinter
from typing import cast

from PySpice.Probe.WaveForm import WaveForm

import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import EngFormatter
import numpy

from phyether import main
from phyether.dac import DAC
from phyether.twisted_pair import TwistedPair

root = tkinter.Tk()
root.wm_title("Simulation")
root.bind("<Escape>", lambda _: root.destroy())

main.init()
pair = TwistedPair(dac=DAC(1, 3, 4), output_impedance=85, length=50, resistance=0.5, transmission_type='lossy')

fig = plt.figure(figsize=(18, 6))
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea
canvas.draw()

toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

input_field = tkinter.Entry(master=root)

def update_simulation():
    analysis = pair.simulate([int(symbol) for symbol in input_field.get().split()
                              if symbol.removeprefix('-').isdecimal()], 2)
    v_in: WaveForm = analysis['vin+'] - analysis['vin-']
    v_out: WaveForm = analysis['vout+'] - analysis['vout-']

    vx_out_transformed = cast(numpy.ndarray, analysis.time - pair.transmission_delay)
    vx_out_transformed = vx_out_transformed[vx_out_transformed>=0]
    # trim v_in where nothing happens after shifting v_out
    vx_in_transformed = analysis.time[analysis.time<(analysis.time[-1] - pair.transmission_delay)]

    plt.cla()
    _, ax2 = plt.plot(
        vx_in_transformed,
        v_in[:len(vx_in_transformed)],
        vx_out_transformed,
        v_out[-len(vx_out_transformed):]
        )
    axes = ax2.axes
    if axes is not None:
        axes.xaxis.set_major_formatter(EngFormatter(unit='s'))
    plt.xlabel('Time')
    plt.ylabel('Voltage (V)')
    plt.grid()
    plt.legend(['v(in+, in-)', 'v(out+, out-)'], loc='upper right')
    canvas.draw()

plt.plot()
plt.grid()
canvas.draw()

button_simulate = tkinter.Button(master=root, text="Simulate", command=update_simulation)

label = tkinter.Label(master=root, text="Wpisz symbole oddzielone spacjami <-4,4> np.: -1 0 4 -3 2")
label.pack(side=tkinter.TOP, fill='x')
input_field.pack(side=tkinter.TOP, fill='x')
button_simulate.pack(side=tkinter.TOP)
toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()
