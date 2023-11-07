import tkinter

from PySpice.Probe.WaveForm import WaveForm

import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import EngFormatter

from phyether.twisted_pair import TwistedPair
from phyether.dac import DAC

root = tkinter.Tk()
root.wm_title("Simulation")
root.bind("<Escape>", lambda _: root.destroy())

pair = TwistedPair(dac=DAC(1, 3, 4), characteristic_impedance=90,
                   output_impedance=105, transmission_delay=5)

fig = plt.figure(figsize=(18, 6))
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea
canvas.draw()

toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

input_field = tkinter.Entry(master=root)


def update_simulation():
    analysis = pair.simulate([int(symbol) for symbol in "1 5 -2 3".split()
                              if symbol.removeprefix('-').isdecimal()])
    v_in: WaveForm = analysis['vin+'] - analysis['vin-']
    v_out: WaveForm = analysis['vout+'] - analysis['vout-']

    plt.cla()
    _, ax2 = plt.plot(v_in.abscissa, v_in.tolist(), v_out.abscissa, v_out.tolist())
    axes = ax2.axes
    if axes is not None:
        axes.xaxis.set_major_formatter(EngFormatter(unit='s'))
    plt.xlabel('Time')
    plt.ylabel('Voltage (V)')
    plt.grid()
    plt.legend(['v(in+, in-)', 'v(out+, out-)'], loc='upper right')
    canvas.draw()


update_simulation()
button_simulate = tkinter.Button(master=root, text="Simulate", command=update_simulation)

label = tkinter.Label(master=root, text="Wpisz symbole oddzielone spacjami <-4,4> np.: -1 0 4 -3 2")
label.pack(side=tkinter.TOP, fill='x')
input_field.pack(side=tkinter.TOP, fill='x')
button_simulate.pack(side=tkinter.TOP)
toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()
