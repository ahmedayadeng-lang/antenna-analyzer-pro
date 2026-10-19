import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QGroupBox, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QComboBox, QTextEdit,
                             QDoubleSpinBox, QSpinBox, QSplitter, QMessageBox, QFileDialog,
                             QFormLayout, QHeaderView, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, polar=False):
        if polar:
            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.fig.add_subplot(111, polar=True)
        else:
            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)

class AnalyzerDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.measurement_data = []
        
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left panel for data input
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Data input group
        input_group = QGroupBox("Measurement Data Input")
        input_layout = QFormLayout()
        
        self.frequency_input = QDoubleSpinBox()
        self.frequency_input.setRange(1, 100000)
        self.frequency_input.setValue(2400)
        self.frequency_input.setSuffix(" MHz")
        
        self.distance_input = QDoubleSpinBox()
        self.distance_input.setRange(0.1, 10000)
        self.distance_input.setValue(10)
        self.distance_input.setSuffix(" m")
        
        self.angle_input = QDoubleSpinBox()
        self.angle_input.setRange(0, 360)
        self.angle_input.setValue(0)
        self.angle_input.setSuffix(" °")
        
        self.tx_power_input = QDoubleSpinBox()
        self.tx_power_input.setRange(-100, 100)
        self.tx_power_input.setValue(20)
        self.tx_power_input.setSuffix(" dBm")
        
        self.rx_power_input = QDoubleSpinBox()
        self.rx_power_input.setRange(-100, 100)
        self.rx_power_input.setValue(-45)
        self.rx_power_input.setSuffix(" dBm")
        
        input_layout.addRow("Frequency:", self.frequency_input)
        input_layout.addRow("Distance:", self.distance_input)
        input_layout.addRow("Angle:", self.angle_input)
        input_layout.addRow("Transmitted Power:", self.tx_power_input)
        input_layout.addRow("Received Power:", self.rx_power_input)
        
        input_group.setLayout(input_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Measurement")
        self.add_btn.clicked.connect(self.add_measurement)
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.clicked.connect(self.import_csv)
        self.clear_btn = QPushButton("Clear Data")
        self.clear_btn.clicked.connect(self.clear_data)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.clear_btn)
        
        # Results display
        results_group = QGroupBox("Calculated Results")
        results_layout = QFormLayout()
        
        self.path_loss_label = QLabel("0 dB")
        self.efficiency_label = QLabel("0 %")
        
        results_layout.addRow("Path Loss:", self.path_loss_label)
        results_layout.addRow("Efficiency:", self.efficiency_label)
        results_group.setLayout(results_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(7)
        self.data_table.setHorizontalHeaderLabels(["Freq (MHz)", "Dist (m)", "Angle (°)", "Tx (dBm)", "Rx (dBm)", "Path Loss (dB)", "Efficiency (%)"])
        
        left_layout.addWidget(input_group)
        left_layout.addLayout(button_layout)
        left_layout.addWidget(results_group)
        left_layout.addWidget(QLabel("Measurement Data:"))
        left_layout.addWidget(self.data_table)
        left_panel.setLayout(left_layout)
        
        # Right panel for graphs
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Graph selection
        graph_select_layout = QHBoxLayout()
        graph_select_layout.addWidget(QLabel("Plot Type:"))
        self.graph_combo = QComboBox()
        self.graph_combo.addItems(["Power vs Distance", "Power vs Angle", "Power vs Frequency", "Power Loss vs Frequency"])
        self.plot_btn = QPushButton("Update Plots")
        self.plot_btn.clicked.connect(self.update_plots)
        
        graph_select_layout.addWidget(self.graph_combo)
        graph_select_layout.addWidget(self.plot_btn)
        graph_select_layout.addStretch()
        
        # Graph area
        self.graph_canvas = MplCanvas(self, width=8, height=6, dpi=100)
        
        right_layout.addLayout(graph_select_layout)
        right_layout.addWidget(self.graph_canvas)
        right_panel.setLayout(right_layout)
        
        # Split main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def add_measurement(self):
        freq = self.frequency_input.value()
        dist = self.distance_input.value()
        angle = self.angle_input.value()
        tx_power = self.tx_power_input.value()
        rx_power = self.rx_power_input.value()
        
        # Calculate path loss and efficiency
        path_loss = tx_power - rx_power
        # Fraction of transmitted power that reaches the receiver (linear scale)
        efficiency = 100 * 10 ** ((rx_power - tx_power) / 10)
        
        # Add to data
        self.measurement_data.append({
            'frequency': freq, 'distance': dist, 'angle': angle,
            'tx_power': tx_power, 'rx_power': rx_power,
            'path_loss': path_loss, 'efficiency': efficiency
        })
        
        # Update table
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, QTableWidgetItem(f"{freq:.2f}"))
        self.data_table.setItem(row, 1, QTableWidgetItem(f"{dist:.2f}"))
        self.data_table.setItem(row, 2, QTableWidgetItem(f"{angle:.2f}"))
        self.data_table.setItem(row, 3, QTableWidgetItem(f"{tx_power:.2f}"))
        self.data_table.setItem(row, 4, QTableWidgetItem(f"{rx_power:.2f}"))
        self.data_table.setItem(row, 5, QTableWidgetItem(f"{path_loss:.2f}"))
        self.data_table.setItem(row, 6, QTableWidgetItem(f"{efficiency:.3g}"))
        
        # Update results
        self.path_loss_label.setText(f"{path_loss:.2f} dB")
        self.efficiency_label.setText(f"{efficiency:.3g} %")
        
    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.read_csv(file_path)
                # Simple CSV parsing - can be enhanced based on specific format
                for _, row in df.iterrows():
                    if len(row) >= 5:
                        self.frequency_input.setValue(float(row.iloc[0]))
                        self.distance_input.setValue(float(row.iloc[1]))
                        self.angle_input.setValue(float(row.iloc[2]))
                        self.tx_power_input.setValue(float(row.iloc[3]))
                        self.rx_power_input.setValue(float(row.iloc[4]))
                        self.add_measurement()
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Could not import CSV: {str(e)}")
    
    def clear_data(self):
        self.measurement_data = []
        self.data_table.setRowCount(0)
        self.path_loss_label.setText("0 dB")
        self.efficiency_label.setText("0 %")
        self.graph_canvas.axes.clear()
        self.graph_canvas.draw()
    
    def update_plots(self):
        if not self.measurement_data:
            return
            
        self.graph_canvas.axes.clear()
        
        plot_type = self.graph_combo.currentText()
        data = self.measurement_data
        
        if plot_type == "Power vs Distance":
            distances = [d['distance'] for d in data]
            rx_powers = [d['rx_power'] for d in data]
            self.graph_canvas.axes.plot(distances, rx_powers, 'bo-', linewidth=2, markersize=6)
            self.graph_canvas.axes.set_xlabel('Distance (m)')
            self.graph_canvas.axes.set_ylabel('Received Power (dBm)')
            self.graph_canvas.axes.set_title('Received Power vs Distance')
            self.graph_canvas.axes.grid(True, alpha=0.3)
            
        elif plot_type == "Power vs Angle":
            angles = [d['angle'] for d in data]
            rx_powers = [d['rx_power'] for d in data]
            self.graph_canvas.axes.plot(angles, rx_powers, 'ro-', linewidth=2, markersize=6)
            self.graph_canvas.axes.set_xlabel('Angle (°)')
            self.graph_canvas.axes.set_ylabel('Received Power (dBm)')
            self.graph_canvas.axes.set_title('Received Power vs Angle')
            self.graph_canvas.axes.grid(True, alpha=0.3)
            
        elif plot_type == "Power vs Frequency":
            freqs = [d['frequency'] for d in data]
            rx_powers = [d['rx_power'] for d in data]
            self.graph_canvas.axes.plot(freqs, rx_powers, 'go-', linewidth=2, markersize=6)
            self.graph_canvas.axes.set_xlabel('Frequency (MHz)')
            self.graph_canvas.axes.set_ylabel('Received Power (dBm)')
            self.graph_canvas.axes.set_title('Received Power vs Frequency')
            self.graph_canvas.axes.grid(True, alpha=0.3)
            
        elif plot_type == "Power Loss vs Frequency":
            freqs = [d['frequency'] for d in data]
            path_losses = [d['path_loss'] for d in data]
            self.graph_canvas.axes.plot(freqs, path_losses, 'mo-', linewidth=2, markersize=6)
            self.graph_canvas.axes.set_xlabel('Frequency (MHz)')
            self.graph_canvas.axes.set_ylabel('Path Loss (dB)')
            self.graph_canvas.axes.set_title('Path Loss vs Frequency')
            self.graph_canvas.axes.grid(True, alpha=0.3)
        
        self.graph_canvas.fig.tight_layout()
        self.graph_canvas.draw()

class PowerLossSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left panel - inputs
        left_panel = QWidget()
        left_layout = QFormLayout()
        
        # Input parameters
        self.tx_power = QDoubleSpinBox()
        self.tx_power.setRange(-100, 100)
        self.tx_power.setValue(20)
        self.tx_power.setSuffix(" dBm")
        
        self.tx_gain = QDoubleSpinBox()
        self.tx_gain.setRange(-50, 50)
        self.tx_gain.setValue(2)
        self.tx_gain.setSuffix(" dBi")
        
        self.rx_gain = QDoubleSpinBox()
        self.rx_gain.setRange(-50, 50)
        self.rx_gain.setValue(2)
        self.rx_gain.setSuffix(" dBi")
        
        self.frequency = QDoubleSpinBox()
        self.frequency.setRange(1, 100000)
        self.frequency.setValue(2400)
        self.frequency.setSuffix(" MHz")
        
        self.distance = QDoubleSpinBox()
        self.distance.setRange(0.1, 10000)
        self.distance.setValue(100)
        self.distance.setSuffix(" m")
        
        left_layout.addRow("Transmit Power:", self.tx_power)
        left_layout.addRow("Transmit Antenna Gain:", self.tx_gain)
        left_layout.addRow("Receive Antenna Gain:", self.rx_gain)
        left_layout.addRow("Frequency:", self.frequency)
        left_layout.addRow("Distance:", self.distance)
        
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self.calculate_friis)
        left_layout.addRow(self.calculate_btn)
        
        # Results
        left_layout.addRow(QLabel("<b>Results:</b>"))
        
        self.rx_power_label = QLabel("-- dBm")
        self.path_loss_label = QLabel("-- dB")
        
        left_layout.addRow("Received Power:", self.rx_power_label)
        left_layout.addRow("Free-space Path Loss:", self.path_loss_label)
        
        left_panel.setLayout(left_layout)
        
        # Right panel - suggestions and info
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Suggestions
        suggestions_group = QGroupBox("Link Improvement Suggestions")
        self.suggestions_text = QTextEdit()
        self.suggestions_text.setReadOnly(True)
        suggestions_layout = QVBoxLayout()
        suggestions_layout.addWidget(self.suggestions_text)
        suggestions_group.setLayout(suggestions_layout)
        
        # Friis equation info
        info_group = QGroupBox("Friis Transmission Equation")
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <h3>Friis Transmission Equation</h3>
        <p>P<sub>r</sub> = P<sub>t</sub> + G<sub>t</sub> + G<sub>r</sub> - L<sub>fs</sub></p>
        <p>Where:</p>
        <ul>
        <li>P<sub>r</sub>: Received Power (dBm)</li>
        <li>P<sub>t</sub>: Transmitted Power (dBm)</li>
        <li>G<sub>t</sub>: Transmit Antenna Gain (dBi)</li>
        <li>G<sub>r</sub>: Receive Antenna Gain (dBi)</li>
        <li>L<sub>fs</sub>: Free-space Path Loss (dB)</li>
        </ul>
        <p>L<sub>fs</sub> = 20log<sub>10</sub>(d) + 20log<sub>10</sub>(f) + 20log<sub>10</sub>(4π/c)</p>
        """)
        info_layout = QVBoxLayout()
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        
        right_layout.addWidget(suggestions_group)
        right_layout.addWidget(info_group)
        right_panel.setLayout(right_layout)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        self.setLayout(main_layout)
        
    def calculate_friis(self):
        # Get input values
        Pt = self.tx_power.value()  # dBm
        Gt = self.tx_gain.value()   # dBi
        Gr = self.rx_gain.value()   # dBi
        f = self.frequency.value() * 1e6  # Convert to Hz
        d = self.distance.value()   # meters
        
        # Calculate free-space path loss in dB
        # Lfs = 20*log10(d) + 20*log10(f) + 20*log10(4*pi/c) - Gt - Gr
        c = 3e8  # speed of light m/s
        Lfs = 20 * np.log10(d) + 20 * np.log10(f) + 20 * np.log10(4 * np.pi / c)
        
        # Calculate received power
        Pr = Pt + Gt + Gr - Lfs
        
        # Update results
        self.rx_power_label.setText(f"{Pr:.2f} dBm")
        self.path_loss_label.setText(f"{Lfs:.2f} dB")
        
        # Generate suggestions
        self.generate_suggestions(Pr, Lfs, d)
    
    def generate_suggestions(self, Pr, Lfs, current_distance):
        suggestions = []
        
        if Pr < -80:
            suggestions.append("⚠️ <b>Weak signal detected!</b> Consider:")
            
            # Distance improvement
            new_dist = current_distance * 0.5
            improvement = Lfs - (20 * np.log10(new_dist) + 20 * np.log10(self.frequency.value() * 1e6) + 20 * np.log10(4 * np.pi / 3e8))
            suggestions.append(f"• Reduce distance to {new_dist:.1f}m to gain ~{improvement:.1f}dB")
            
            # Gain improvement
            suggestions.append("• Increase antenna gains (higher gain antennas)")
            suggestions.append("• Use directional antennas for better focus")
            
        elif Pr < -60:
            suggestions.append("📶 <b>Moderate signal strength</b>")
            suggestions.append("• Signal is acceptable but could be improved")
            suggestions.append("• Consider antenna alignment optimization")
            
        else:
            suggestions.append("✅ <b>Strong signal</b>")
            suggestions.append("• Link performance is good")
            suggestions.append("• Maintain current configuration")
        
        # General suggestions
        suggestions.append("")
        suggestions.append("<b>General Tips:</b>")
        suggestions.append("• Ensure clear line-of-sight")
        suggestions.append("• Minimize obstacles and reflections")
        suggestions.append("• Use appropriate frequency for application")
        suggestions.append("• Consider environmental factors (weather, interference)")
        
        self.suggestions_text.setHtml("<br>".join(suggestions))

class RadiationPatternVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.current_pattern = None
        self.current_theta = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left panel - controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Pattern type selection
        pattern_group = QGroupBox("Radiation Pattern Type")
        pattern_layout = QVBoxLayout()
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Omnidirectional", "Dipole", "Yagi (Directional)", "Parabolic", "Custom Import"])
        self.pattern_combo.currentTextChanged.connect(self.update_pattern)
        pattern_layout.addWidget(self.pattern_combo)
        
        # Parameters for theoretical patterns
        self.params_group = QGroupBox("Pattern Parameters")
        params_layout = QFormLayout()
        
        self.gain_input = QDoubleSpinBox()
        self.gain_input.setRange(0, 30)
        self.gain_input.setValue(2)
        self.gain_input.setSuffix(" dBi")
        
        self.beamwidth_input = QDoubleSpinBox()
        self.beamwidth_input.setRange(10, 360)
        self.beamwidth_input.setValue(60)
        self.beamwidth_input.setSuffix(" °")
        
        self.front_back_input = QDoubleSpinBox()
        self.front_back_input.setRange(0, 50)
        self.front_back_input.setValue(20)
        self.front_back_input.setSuffix(" dB")
        
        params_layout.addRow("Gain:", self.gain_input)
        params_layout.addRow("Beamwidth:", self.beamwidth_input)
        params_layout.addRow("Front-to-Back Ratio:", self.front_back_input)
        
        self.params_group.setLayout(params_layout)
        
        # Import controls
        self.import_group = QGroupBox("Import Data")
        import_layout = QVBoxLayout()
        self.import_btn = QPushButton("Import Angle-Power Data")
        self.import_btn.clicked.connect(self.import_pattern_data)
        import_layout.addWidget(self.import_btn)
        self.import_group.setVisible(False)
        self.import_group.setLayout(import_layout)
        
        # Rotation control
        rotation_group = QGroupBox("Antenna Rotation")
        rotation_layout = QFormLayout()
        
        self.rotation_input = QDoubleSpinBox()
        self.rotation_input.setRange(0, 360)
        self.rotation_input.setValue(0)
        self.rotation_input.setSuffix(" °")
        self.rotation_input.valueChanged.connect(self.update_pattern_display)
        
        rotation_layout.addRow("Rotation Angle:", self.rotation_input)
        rotation_group.setLayout(rotation_layout)
        
        pattern_layout.addWidget(self.params_group)
        pattern_layout.addWidget(self.import_group)
        pattern_layout.addWidget(rotation_group)
        pattern_group.setLayout(pattern_layout)
        
        left_layout.addWidget(pattern_group)
        left_layout.addStretch()
        
        left_panel.setLayout(left_layout)
        
        # Right panel - plot
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.polar_canvas = MplCanvas(self, width=8, height=8, dpi=100, polar=True)
        right_layout.addWidget(self.polar_canvas)
        
        right_panel.setLayout(right_layout)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        self.setLayout(main_layout)
        
        # Initial pattern
        self.update_pattern()
        
    def update_pattern(self):
        pattern_type = self.pattern_combo.currentText()
        
        # Show/hide appropriate controls
        if pattern_type == "Custom Import":
            self.params_group.setVisible(False)
            self.import_group.setVisible(True)
        else:
            self.params_group.setVisible(True)
            self.import_group.setVisible(False)
            
        self.update_pattern_display()
    
    def update_pattern_display(self):
        pattern_type = self.pattern_combo.currentText()
        rotation = np.radians(self.rotation_input.value())
        
        theta = np.linspace(0, 2*np.pi, 360)
        
        if pattern_type == "Omnidirectional":
            gain = self.gain_input.value()
            pattern = np.ones_like(theta) * gain
            
        elif pattern_type == "Dipole":
            # Classic dipole pattern (doughnut-shaped)
            pattern = self.gain_input.value() * np.abs(np.sin(theta + rotation))
            
        elif pattern_type == "Yagi (Directional)":
            beamwidth = np.radians(self.beamwidth_input.value())
            fbr = self.front_back_input.value()
            
            # Create directional pattern
            pattern = np.ones_like(theta) * (-fbr)  # Start with back lobe
            main_lobe_center = rotation
            main_lobe_width = beamwidth / 2
            
            # Create main lobe
            for i, angle in enumerate(theta):
                diff = abs(angle - main_lobe_center)
                if diff > np.pi:
                    diff = 2*np.pi - diff
                if diff <= main_lobe_width:
                    pattern[i] = self.gain_input.value() * (1 - (diff / main_lobe_width)**2)
                    
        elif pattern_type == "Parabolic":
            beamwidth = np.radians(self.beamwidth_input.value())
            pattern = np.ones_like(theta) * (-30)  # Very low side lobes
            
            main_lobe_center = rotation
            main_lobe_width = beamwidth / 2
            
            # Create very directional main lobe
            for i, angle in enumerate(theta):
                diff = abs(angle - main_lobe_center)
                if diff > np.pi:
                    diff = 2*np.pi - diff
                if diff <= main_lobe_width:
                    pattern[i] = self.gain_input.value() * np.cos((diff / main_lobe_width) * (np.pi/2))
        
        else:  # Custom or fallback to omnidirectional
            if self.current_pattern is not None:
                theta = self.current_theta + rotation
                pattern = self.current_pattern
            else:
                pattern = np.ones_like(theta) * 2
        
        # Convert to linear scale for plotting (assuming dBi is logarithmic)
        pattern_linear = 10**(pattern / 10)
        
        # Plot
        self.polar_canvas.axes.clear()
        self.polar_canvas.axes.plot(theta, pattern_linear, linewidth=2, color='cyan')
        self.polar_canvas.axes.set_theta_zero_location('N')
        self.polar_canvas.axes.set_theta_direction(-1)
        self.polar_canvas.axes.set_title('Radiation Pattern', pad=20, color='white')
        self.polar_canvas.axes.grid(True, alpha=0.3)
        self.polar_canvas.fig.tight_layout()
        self.polar_canvas.draw()
    
    def import_pattern_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Pattern Data", "", "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.read_csv(file_path)
                if len(df.columns) >= 2:
                    angles = df.iloc[:, 0].values
                    gains = df.iloc[:, 1].values
                    
                    # Convert to radians and normalize
                    self.current_theta = np.radians(angles)
                    self.current_pattern = gains
                    
                    self.update_pattern_display()
                    QMessageBox.information(self, "Success", "Pattern data imported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Could not import pattern data: {str(e)}")

class AntennaAnalyzerPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Antenna Analyzer Pro')
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create central widget and tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create different sections
        self.dashboard = AnalyzerDashboard()
        self.simulator = PowerLossSimulator()
        self.pattern_viewer = RadiationPatternVisualizer()
        
        # Add tabs
        self.tabs.addTab(self.dashboard, "📊 Analyzer Dashboard")
        self.tabs.addTab(self.simulator, "🔧 Power Loss Simulator")
        self.tabs.addTab(self.pattern_viewer, "📡 Radiation Pattern Visualizer")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage('Antenna Analyzer Pro Ready')
        
    def apply_dark_theme(self):
        # Set dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 40))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(20, 20, 30))
        dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 40))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(120, 80, 200))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(50, 40, 70))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(120, 80, 200))
        dark_palette.setColor(QPalette.Highlight, QColor(120, 80, 200))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        # Set style sheet for additional styling
        self.setStyleSheet("""
            QLabel {
                color: #e6e6f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #7850c8;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #b8a2e0;
            }
            QPushButton {
                background-color: #7850c8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8a68d0;
            }
            QPushButton:pressed {
                background-color: #5a3c9c;
            }
            QTabWidget::pane {
                border: 2px solid #7850c8;
                background-color: #1e1e28;
            }
            QTabBar::tab {
                background-color: #2d2d3d;
                color: white;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #7850c8;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3d3d4d;
            }
            QTableWidget {
                gridline-color: #3d3d4d;
                background-color: #1a1a24;
            }
            QHeaderView::section {
                background-color: #2d2d3d;
                color: white;
                padding: 4px;
                border: 1px solid #3d3d4d;
            }
        """)

def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = AntennaAnalyzerPro()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()