import sys
import platform
from typing import Optional

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QLineEdit, QVBoxLayout, QFormLayout, QTabWidget,
                             QScrollArea, QLabel, QHBoxLayout, QCheckBox,
                             QMessageBox, QFrame
                             )
from phyether.dac import DAC
from phyether.gui.pam_simulation import PAMSimulationCanvas, PAM16SimulationCanvas
from phyether.gui.rs_register_tab import RSRegisterTab
from phyether.gui.rs_tab import RSTab
from phyether.pam import NRZ, PAM, PAM16, PAM4
from phyether.gui.simulation import (SimulationArgs, SimulationDisplay,
                                     SimulationFormWidget, SimulationInitArgs,
                                     SimulationRunArgs, SimulatorCanvas,
                                     )
from phyether.gui.util import create_msg_box


class EthernetGuiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tabs: Optional[tuple[RSTab, QWidget, QWidget, QWidget, RSRegisterTab]] = None
        self.tp_simulation_forms: list[SimulationFormWidget]
        simulation_enable = self.init_ngspice()
        self.init_ui(simulation_enable)

    def init_ngspice(self):
        init_success = False
        from phyether.main import init, install_libngspice
        try:
            init()
            init_success = True
        except FileNotFoundError as ex:
            if platform.system() == "Windows":
                create_msg_box("Couldn't find ngspice.dll, simulation tab will be disabled",
                               "Error")
            elif platform.system() == "Linux":
                install = create_msg_box("Couldn't find ngspice library. Without it simulation tab will be disabled\nDo you want to install it? (needed sudo privileges)",
                    "Missing ngspice library",
                    icon = QMessageBox.Icon.Warning,
                    buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, # type: ignore
                    )
                try:
                    print(install)
                    if install != QMessageBox.StandardButton.Yes:
                        return False
                    elif install_libngspice():
                        init()
                        init_success = True
                    else:
                        create_msg_box("ngspice installation failed, simulation tab will be disabled",
                               "Error")
                except FileNotFoundError as ex:
                    create_msg_box("Couldn't find ngspice library, try restarting application",
                               "Error")
                except:
                    create_msg_box("Installation error", "Error")
            else:
                create_msg_box("Couldn't find ngspice library, simulation tab will be disabled",
                               "Error")
        return init_success

    def closeEvent(self, a0) -> None:
        if self.tabs is not None:
            self.tabs[0].on_close()
        return super().closeEvent(a0)

    def init_ui(self, enable_simulation_tab):
        self.setWindowTitle("EthernetSimulator")
        from PyQt5.QtCore import Qt
        self.setWindowState(Qt.WindowState.WindowMaximized)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)

        self.tabs = (RSTab(), QWidget(), QWidget(), QWidget(), RSRegisterTab())
        if not enable_simulation_tab:
            self.tabs[3].setDisabled(True)
        self.init_pam16()
        self.init_pam()
        self.init_twisted_pair()
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab:hover {\
                                      background-color: rgba(204, 204, 204, 178);\
                                      }")
        self.tab_widget.addTab(self.tabs[0], "Reed-Solomon")
        self.tab_widget.addTab(self.tabs[4], "Reed-Solomon Shift Register")
        self.tab_widget.addTab(self.tabs[1], "PAM16")
        self.tab_widget.addTab(self.tabs[2], "PAM")
        self.tab_widget.addTab(self.tabs[3], "Twisted-pair simulation")

        self.tab_widget.currentChanged.connect(self.change_tab)
        self.main_layout.addWidget(self.tab_widget)

    def change_tab(self, index):
        self.tab_widget.setCurrentIndex(index)

    def init_pam16(self):
        self.pam16_simulator_data = QLineEdit()
        main_layout = QVBoxLayout()
        top_frame = QFrame()
        top_layout = QVBoxLayout()
        top_frame.setLayout(top_layout)
        top_frame.setFixedHeight(100)
        main_layout.addWidget(top_frame)
        self.tabs[1].setLayout(main_layout)
        top_layout.addWidget(QLabel("Enter data in hexadecimal format"))
        top_layout.addWidget(self.pam16_simulator_data)

        self.pam16_simulate_button = QPushButton("Simulate")
        top_layout.addWidget(self.pam16_simulate_button)
        self.pam16_simulate_button.clicked.connect(self.pam16_simulate)

        self.pam16_canvas = PAM16SimulationCanvas()
        self.pam16_canvas.simulation_stopped_signal.connect(lambda: self.pam16_simulate_button.setDisabled(False))
        self.tabs[1].layout().addWidget(self.pam16_canvas)

    def init_pam(self):
        self.pam_versions: list[PAM] = [NRZ(), PAM4(), PAM16()]

        self.pam_simulator_data = QLineEdit()
        main_layout = QVBoxLayout()
        top_frame = QFrame()
        top_layout = QVBoxLayout()
        top_frame.setLayout(top_layout)
        main_layout.addWidget(top_frame)
        top_frame.setFixedHeight(100)
        self.tabs[2].setLayout(main_layout)
        top_layout.addWidget(QLabel(f"Enter data in hexadecimal format"))
        top_layout.addWidget(self.pam_simulator_data)

        self.pam_simulate_button = QPushButton("Simulate")
        top_layout.addWidget(self.pam_simulate_button)
        self.pam_simulate_button.clicked.connect(self.pam_simulate)

        # Add your canvas
        self.pam_canvas = PAMSimulationCanvas()
        self.pam_canvas.simulation_stopped_signal.connect(lambda: self.pam_simulate_button.setDisabled(False))
        self.tabs[2].layout().addWidget(self.pam_canvas)

    def init_twisted_pair(self):
        self.tabs[3].setLayout(QHBoxLayout())

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

        self.tp_scroll_area.setWidget(self.tp_params_widget)

        options_layout = QVBoxLayout()
        options_layout.addWidget(self.tp_scroll_area)

        checkbox_layout = QHBoxLayout()
        self.plot_checkboxes: list[QCheckBox] = []
        for plot in SimulationDisplay:
            checkbox = QCheckBox(plot.value)
            checkbox.toggled.connect(self.checkbox_toggled)
            self.plot_checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)

        options_layout.addLayout(checkbox_layout)

        self.simulator_signals = QLineEdit()
        signals_layout = QHBoxLayout()
        signals_layout.addWidget(QLabel(f"Twisted pair signals"))
        signals_layout.addWidget(self.simulator_signals)

        options_layout.addLayout(signals_layout)
        options_widget = QWidget()
        options_widget.setLayout(options_layout)
        options_widget.setFixedWidth(450)

        self.tabs[3].layout().addWidget(options_widget)

        self.tp_simulate_button = QPushButton("Simulate")
        options_layout.addWidget(self.tp_simulate_button)
        self.tp_simulate_button.clicked.connect(self.simulate)

        # Add your canvas
        self.tp_canvas = SimulatorCanvas()
        self.tp_canvas.simulation_stopped_signal.connect(lambda: self.tp_simulate_button.setDisabled(False))
        self.tabs[3].layout().addWidget(self.tp_canvas)

    def add_simulation_form(self):
        index = len(self.tp_simulation_forms)
        self.tp_simulation_forms.append(SimulationFormWidget("Simulation parameters", index + 1))
        self.tp_simulation_form.insertRow(index, self.tp_simulation_forms[-1])

        # self.tp_simulation_form.insertRow(input_index - 1, f"{input_index}. simulation parameters:", self.tp_simulation_forms[-1])

    def pam16_simulate(self):
        self.pam16_simulate_button.setDisabled(True)
        simulation_args: list[SimulationArgs] = []
        encoder = PAM16()
        try:
            twisted_pairs_output = encoder.hex_to_signals(hex_data=self.pam16_simulator_data.text(), use_dsq128=True)
        except Exception as ex:
            create_msg_box(f"Simulation failed: {ex}", "Simulation error!")
            self.pam16_simulate_button.setDisabled(False)
            return

        for output in twisted_pairs_output:
            print("Simulating...")
            init = SimulationInitArgs(dac=DAC(1, 2,
                                              high_symbol=encoder.high_symbol,
                                              symbol_step=encoder.symbol_step),
                                      transmission_type="lossless",
                                      transmission_delay=0.1)
            simulation_args.append(
                SimulationArgs(init_args=init,
                               run_args=SimulationRunArgs(presimulation_ratio=0),
                               input=output))

        try:
            self.pam16_canvas.simulate(simulation_args)
        except Exception as ex:
            create_msg_box(f"Simulation failed: {ex}", "Simulation error!")
            self.pam16_simulate_button.setDisabled(False)

    def pam_simulate(self):
        self.pam_simulate_button.setDisabled(True)
        simulation_args: list[SimulationArgs] = []

        for encoder in self.pam_versions:
            try:
                input = encoder.hex_to_signals(self.pam_simulator_data.text())
            except Exception as ex:
                create_msg_box(f"Simulation failed: {ex}", "Simulation error!")
                self.pam_simulate_button.setDisabled(False)
                return

            print("Simulating...")
            init = SimulationInitArgs(dac=DAC(1, 2,
                                              high_symbol=encoder.high_symbol,
                                              symbol_step=encoder.symbol_step),
                                      transmission_type="lossless",
                                      transmission_delay=0.1)
            simulation_args.append(
                SimulationArgs(init_args=init,
                               run_args=SimulationRunArgs(presimulation_ratio=0),
                               input=input))

        try:
            self.pam_canvas.simulate(simulation_args)
        except Exception as ex:
            create_msg_box(f"Simulation failed: {ex}", "Simulation error!")
            self.pam_simulate_button.setDisabled(False)

    def simulate(self):
        print("Simulating...")
        self.tp_simulate_button.setDisabled(True)

        # Fixing forms
        self.tp_simulation_forms = [f for f in self.tp_simulation_forms if f.parent()]

        simulation_args: list[SimulationArgs] = []
        for i, form in enumerate(self.tp_simulation_forms):
            # Fixing labels
            form.name_label.setText(f"{i+1}. Simulation parameters")
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
            self.tp_canvas.simulate(simulation_args)
        except Exception as ex:
            create_msg_box(f"Simulation failed: {ex}", "Simulation error!")
            self.tp_simulate_button.setDisabled(False)

    def checkbox_toggled(self, _):
        self.tp_canvas.set_display_params([SimulationDisplay(checkbox.text())
                                    for checkbox in self.plot_checkboxes
                                    if checkbox.isChecked()])


def main():
    app = QApplication(sys.argv)
    window = EthernetGuiApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
