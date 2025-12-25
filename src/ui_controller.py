from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDockWidget
from PyQt6.QtCore import Qt, QTimer
# Placeholder import for SimulationCore - to be implemented next
from simulation_core import SimulationCore

class MainWindow(QMainWindow):
    def __init__(self, sim_config, vis_config):
        super().__init__()
        self.sim_config = sim_config
        self.vis_config = vis_config
        
        self.setWindowTitle(sim_config['simulation']['title'])
        self.resize(1280, 720) # Default size, can go fullscreen

        self.init_ui()

    def init_ui(self):
        # Central Widget - OpenGL Simulation
        self.simulation_widget = SimulationCore(self.sim_config, self.vis_config)
        self.setCentralWidget(self.simulation_widget)

        # Control Panel (Dock Widget)
        self.control_dock = QDockWidget("Controls", self)
        self.control_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.control_widget = QWidget()
        self.control_layout = QVBoxLayout()
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_playback)
        self.control_layout.addWidget(self.play_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.control_layout.addWidget(self.reset_btn)

        self.phase_label = QLabel("Phases:")
        self.control_layout.addWidget(self.phase_label)

        phases = [
            ("Phase 1: Pluie", "phase1_pluie"),
            ("Phase 2: ANEM", "phase2_anem"),
            ("Phase 3: JCN2026", "phase3_jcn"),
            ("Phase 4: FEZ-MEKNES", "phase4_fes"),
            ("Phase 5: NIGER", "phase5_niger"),
            ("Phase 6: Drapeau", "phase6_drapeau"),
            ("Phase 7: Carte", "phase7_carte"),
            ("Phase 8: Finale", "phase8_finale"),
            ("Phase 9: Agadez", "phase9_agadez"),
            ("Phase 10: Touareg", "phase10_touareg"),
        ]

        for label, code in phases:
            btn = QPushButton(label)
            # Use closure to capture loop variable
            btn.clicked.connect(lambda checked, c=code: self.change_phase(c))
            self.control_layout.addWidget(btn)

        self.control_layout.addStretch()
        
        self.control_widget.setLayout(self.control_layout)
        self.control_dock.setWidget(self.control_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.control_dock)

    def change_phase(self, phase_code):
        print(f"Switching to phase: {phase_code}")
        self.simulation_widget.set_phase(phase_code)


    def toggle_playback(self):
        if self.simulation_widget.is_playing:
            self.simulation_widget.pause()
            self.play_btn.setText("Play")
        else:
            self.simulation_widget.play()
            self.play_btn.setText("Pause")

    def reset_simulation(self):
        self.simulation_widget.reset()
        self.play_btn.setText("Play")
