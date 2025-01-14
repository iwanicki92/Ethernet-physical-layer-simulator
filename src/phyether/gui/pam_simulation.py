from typing import Tuple, cast, List
from PySpice.Probe.WaveForm import TransientAnalysis
from matplotlib.axes import Axes
from matplotlib.ticker import EngFormatter
import numpy

from phyether.gui.simulation import SimulationDisplay, SimulatorCanvas

from phyether.pam import PAM

class PAM16SimulationCanvas(SimulatorCanvas):
    def __init__(self):
        super().__init__(init_axes=False)
        self.subplot_axes: List[Axes] = cast(
            List[Axes],
            self.figure.subplots(4, 1, sharex=True, sharey=True))
        for ax in self.subplot_axes:
            ax.grid(True)
        self.draw()
        self.display_legend = ["1st Pair", "2nd Pair", "3rd Pair", "4th Pair"]

        self._display_params.append(SimulationDisplay.VOUT)

    def _draw_add(self,
                  simulation: Tuple[TransientAnalysis, float],
                  index: int):
        analysis, transmission_delay = simulation
        plot_x = cast(numpy.ndarray, analysis.time - transmission_delay)
        plot_x = plot_x[plot_x>=0]
        plot_y = (analysis['vout+'] - analysis['vout-'])[-len(plot_x):]
        plot_y = plot_y[:len(plot_x)]
        self.subplot_axes[index].plot(
            plot_x, plot_y,
            label=self.display_legend[index])

        for ax in self.subplot_axes:
           ax.legend()
        self.draw()

    def clear_plot(self):
        print("Canvas clearing...")
        for ax in self.subplot_axes:
            ax.cla()
            ax.grid()
            ax.set_ylim(-2.5, 2.5)
            ax.xaxis.set_major_formatter(EngFormatter(unit='s'))


class PAMSimulationCanvas(SimulatorCanvas):
    def __init__(self):
        super().__init__(init_axes=False)
        self.subplot_axes: List[Axes] = cast(
            List[Axes],
            self.figure.subplots(len(PAM.__subclasses__()), 1, sharex=True, sharey=True))
        for ax in self.subplot_axes:
            ax.grid(True)
        self.draw()
        self.display_legend = [subclass.__name__ for subclass in PAM.__subclasses__()]

        self._display_params.append(SimulationDisplay.VOUT)

    def _draw_add(self,
                  simulation: Tuple[TransientAnalysis, float],
                  index: int):
        analysis, transmission_delay = simulation
        plot_x = cast(numpy.ndarray, analysis.time - transmission_delay)
        plot_x = plot_x[plot_x>=0]
        plot_y = (analysis['vout+'] - analysis['vout-'])[-len(plot_x):]
        plot_y = plot_y[:len(plot_x)]
        self.subplot_axes[index].plot(
            plot_x, plot_y,
            label=self.display_legend[index])

        for ax in self.subplot_axes:
           ax.legend()
        self.draw()

    def clear_plot(self):
        print("Canvas clearing...")
        for ax in self.subplot_axes:
            ax.cla()
            ax.grid()
            ax.set_ylim(-2.5, 2.5)
            ax.xaxis.set_major_formatter(EngFormatter(unit='s'))
