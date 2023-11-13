import sys
from typing import Optional
from PyQt5 import QtGui

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QLineEdit, QVBoxLayout, QFormLayout, QTabWidget,
                             QScrollArea, QLabel,
                             )

from phyether.dac import DAC
from phyether.gui.rs_tab import RSTab
from phyether.gui.simulation import (SimulationArgs, SimulationDisplay,
                                     SimulationFormWidget, SimulationInitArgs,
                                     SimulationRunArgs, SimulatorCanvas,
                                     )
from phyether.gui.util import create_msg_box


class EthernetGuiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tabs: Optional[tuple[RSTab, QWidget, QWidget, QWidget]] = None
        self.tp_simulation_forms: list[SimulationFormWidget]
        self.init_ui()

    def closeEvent(self, a0) -> None:
        if self.tabs is not None:
            self.tabs[0].on_close()
        return super().closeEvent(a0)

    def init_ui(self):
        self.setWindowTitle("Simple Encoder/Decoder")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.change_tab(0)

    def clear_main_layout(self, index=0):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        if self.tabs is not None:
            self.tabs[0].on_close()
        self.tabs = (RSTab(), QWidget(), QWidget(), QWidget())
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab:hover {\
                                      background-color: rgba(204, 204, 204, 178);\
                                      }")
        self.tab_widget.addTab(self.tabs[0], "Reed-Solomon")
        self.tab_widget.addTab(self.tabs[1], "PAM16")
        self.tab_widget.addTab(self.tabs[2], "PAM")
        self.tab_widget.addTab(self.tabs[3], "Twisted-pair simulation")

        if index != 0:
            self.content_layout = QVBoxLayout(self.tabs[index])
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self.change_tab)
        self.main_layout.addWidget(self.tab_widget)

    def change_tab(self, index):
        print("Changed tab:", index)
        self.clear_main_layout(index)
        if index == 1:
            self.init_pam16()
        elif index == 2:
            self.init_pam()
        elif index == 3:
            self.init_twisted_pair()

    def init_pam16(self):
        self.pam_input_field = QLineEdit()
        pam16_form = QFormLayout()
        pam16_form.addRow("PAM16 parameters:", self.pam_input_field)

    def init_pam(self):
        pass

    def init_twisted_pair(self):
        self.tp_simulation_forms = [SimulationFormWidget("Simulation parameters", 1)]
        self.tp_scroll_area = QScrollArea()
        self.tp_scroll_area.setWidgetResizable(True)

        # Create a widget to hold your simulation parameters
        self.tp_params_widget = QWidget()
        self.tp_simulation_form = QFormLayout(self.tp_params_widget)

        self.tp_add_button = QPushButton("Add")
        self.tp_simulation_form.addWidget(self.tp_add_button)
        self.tp_add_button.clicked.connect(self.add_simulation_form)

        for i, sim_form in enumerate(self.tp_simulation_forms):
            self.tp_simulation_form.insertRow(i, sim_form)

        # Set the widget for the scroll area
        self.tp_scroll_area.setWidget(self.tp_params_widget)

        # Add the scroll area to the content layout
        self.content_layout.addWidget(self.tp_scroll_area)

        self.simulator_signals = QLineEdit()
        self.content_layout.addWidget(QLabel(f"Twisted pair signals"))
        self.content_layout.addWidget(self.simulator_signals)

        self.tp_simulate_button = QPushButton("Simulate")
        self.content_layout.addWidget(self.tp_simulate_button)
        self.tp_simulate_button.clicked.connect(self.simulate)

        # Add your canvas
        self.tp_canvas = SimulatorCanvas()
        self.tp_canvas.simulation_stopped_signal.connect(lambda: self.tp_simulate_button.setDisabled(False))
        self.content_layout.addWidget(self.tp_canvas)

    def add_simulation_form(self):
        index = len(self.tp_simulation_forms)
        self.tp_simulation_forms.append(SimulationFormWidget("Simulation parameters", index + 1))
        self.tp_simulation_form.insertRow(index, self.tp_simulation_forms[-1])

        # self.tp_simulation_form.insertRow(input_index - 1, f"{input_index}. simulation parameters:", self.tp_simulation_forms[-1])

    def simulate(self):
        print("Simulating...")
        self.tp_simulate_button.setDisabled(True)
        simulation_args: list[SimulationArgs] = []
        for i, form in enumerate(self.tp_simulation_forms):
            args = {key: val.value() for key, val in form.number_inputs.items() }
            init = SimulationInitArgs(dac=DAC(1, 2, 15),
                                        transmission_type="lossy",
                                        output_impedance=args["output_impedance"],
                                        length=args["length"], # type: ignore
                                        resistance=args["resistance"],
                                        inductance=args["inductance"],
                                        capacitance=args["capacitance"])
            run = SimulationRunArgs(voltage_offset=args["voltage_offset"]) # type: ignore
            simulation_args.append(SimulationArgs(init_args=init,
                                                  run_args=run,
                                                  input=self.simulator_signals.text()))

        try:
            self.tp_canvas.set_display_params({
                0: {SimulationDisplay.VOUT_PLUS, SimulationDisplay.VOUT_MINUS, SimulationDisplay.VOUT},
                1: {SimulationDisplay.VOUT}
                })
            self.tp_canvas.simulate(simulation_args)
        except Exception as ex:
            create_msg_box(f"Simulation failed: {ex}", "Simulation error!")
            self.tp_simulate_button.setDisabled(False)


def main():
    app = QApplication(sys.argv)
    window = EthernetGuiApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
