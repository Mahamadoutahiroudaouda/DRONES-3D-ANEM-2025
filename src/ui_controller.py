from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDockWidget, QScrollArea
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
        self.control_dock = QDockWidget("Contrôles du Show", self)
        self.control_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Scroll Area to handle many buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.control_widget = QWidget()
        self.control_layout = QVBoxLayout()
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_playback)
        self.control_layout.addWidget(self.play_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.control_layout.addWidget(self.reset_btn)

        # 1. NEW NARRATIVE ACTS (OPENING CEREMONY)
        opening_acts = [
            ("--- OUVERTURE (ACTES) ---", None),
            ("Acte 0: Silence Sacred", "act0_pre_opening"),
            ("Acte I: Naissance (Dunes)", "act1_desert"),
            ("Acte II: La Pluie Sacrée", "act2_sacred_rain"),
            ("Acte III: Typographie", "act3_typography"),
            ("Acte IV: Science & Beauté", "act4_science"),
            ("Acte V: L'Ame Africaine", "act5_wildlife"),
            ("Acte VI: Identité Sacrée", "act6_identity"),
            ("Acte VII: Drapeau Géant", "act7_flag"),
            ("Acte VIII: Finale Unity", "act8_finale"),
            ("Acte IX: Eagle", "act9_eagle"),
        ]

        # 2. ORIGINAL PHASES (RECAP)
        original_phases = [
            ("--- PHASES ORIGINALES ---", None),
            ("Phase 1: Pluie", "phase1_pluie"),
            ("Phase 2: ANEM", "phase2_anem"),
            ("Phase 3: JCN2026", "phase3_jcn"),
            ("Phase 4: FEZ-MEKNES", "phase4_fes"),
            ("Phase 5: NIGER", "phase5_niger"),
            ("Phase 6: Drapeau", "phase6_drapeau"),
            ("Phase 7: Carte Precise", "phase7_carte"),
            ("Phase 8: Finale Org.", "phase8_finale"),
        ]

        # 3. HERITAGE & MODELS
        heritage_phases = [
            ("--- HÉRITAGE & SPÉCIAL ---", None),
            ("✨ MIROIR CÉLESTE (45s) ✨", "miroir_celeste"),
            ("Phase 9: Gde Mosquée", "phase9_agadez"),
            ("Phase 10: Touareg", "phase10_touareg"),
            ("Phase 11: Croix d'Agadez", "phase11_croix_agadez"),
        ]

        all_phases = opening_acts + original_phases + heritage_phases

        for label, code in all_phases:
            if code is None:
                lbl = QLabel(label)
                lbl.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px; background: #eee; padding: 2px;")
                self.control_layout.addWidget(lbl)
                continue
            btn = QPushButton(label)
            # Special Styling for High-End project
            if code == "miroir_celeste":
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffd700, stop:1 #b8860b);
                        color: black;
                        font-weight: bold;
                        border: 1px solid #daa520;
                        border-radius: 4px;
                        padding: 6px;
                    }
                    QPushButton:hover { background: #daa520; }
                """)
                print("DEBUG: MIROIR CÉLESTE button created.")

            btn.clicked.connect(lambda checked, c=code: self.change_phase(c))
            self.control_layout.addWidget(btn)

        self.control_layout.addStretch()
        self.control_widget.setLayout(self.control_layout)
        
        scroll.setWidget(self.control_widget)
        self.control_dock.setWidget(scroll)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.control_dock)

    def change_phase(self, phase_code):
        print(f"Switching to phase: {phase_code}")
        self.simulation_widget.set_phase(phase_code)
        self.simulation_widget.is_playing = True

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
