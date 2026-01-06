from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDockWidget, QScrollArea, QFileDialog
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
        
        # === AUTO-SEQUENCING BUTTONS ===
        seq_label = QLabel("═══ AUTO-SEQUENCE ═══")
        seq_label.setStyleSheet("font-weight: bold; color: #d4a574; background: #1a1a1a; padding: 5px; border: 1px solid #d4a574; border-radius: 3px;")
        self.control_layout.addWidget(seq_label)
        
        self.start_seq_btn = QPushButton("▶ Start Sequence")
        self.start_seq_btn.setStyleSheet("""
            QPushButton {
                background: #2d5016;
                color: #90EE90;
                font-weight: bold;
                border: 1px solid #90EE90;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover { background: #3d6b1f; }
        """)
        self.start_seq_btn.clicked.connect(self.start_sequence)
        self.control_layout.addWidget(self.start_seq_btn)
        
        self.pause_seq_btn = QPushButton("⏸ Pause")
        self.pause_seq_btn.setStyleSheet("""
            QPushButton {
                background: #4d3b16;
                color: #FFD700;
                font-weight: bold;
                border: 1px solid #FFD700;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover { background: #5d4b26; }
        """)
        self.pause_seq_btn.clicked.connect(self.pause_sequence)
        self.control_layout.addWidget(self.pause_seq_btn)
        
        seq_nav_layout = QHBoxLayout()
        
        self.prev_phase_btn = QPushButton("◀ Prev")
        self.prev_phase_btn.clicked.connect(self.prev_phase_in_sequence)
        seq_nav_layout.addWidget(self.prev_phase_btn)
        
        self.next_phase_btn = QPushButton("Next ▶")
        self.next_phase_btn.clicked.connect(self.next_phase_in_sequence)
        seq_nav_layout.addWidget(self.next_phase_btn)
        
        self.rewind_seq_btn = QPushButton("⏮ Rewind")
        self.rewind_seq_btn.clicked.connect(self.rewind_sequence)
        seq_nav_layout.addWidget(self.rewind_seq_btn)
        
        self.control_layout.addLayout(seq_nav_layout)
        
        # === AUDIO SYSTEM ===
        audio_label = QLabel("═══ AUDIO REACTIVITY ═══")
        audio_label.setStyleSheet("font-weight: bold; color: #88c999; background: #1a1a1a; padding: 5px; border: 1px solid #88c999; border-radius: 3px;")
        self.control_layout.addWidget(audio_label)
        
        self.load_audio_btn = QPushButton("🎵 Load Audio File")
        self.load_audio_btn.setStyleSheet("""
            QPushButton {
                background: #1a3a2e;
                color: #88c999;
                font-weight: bold;
                border: 1px solid #88c999;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover { background: #2a4a3e; }
        """)
        self.load_audio_btn.clicked.connect(self.load_audio_file)
        self.control_layout.addWidget(self.load_audio_btn)
        
        self.audio_status_label = QLabel("No audio loaded")
        self.audio_status_label.setStyleSheet("color: #999; font-size: 10px;")
        self.control_layout.addWidget(self.audio_status_label)
        
        # === AUDIO PLAYBACK CONTROLS ===
        audio_controls_layout = QHBoxLayout()
        
        self.audio_play_btn = QPushButton("▶ Play Audio")
        self.audio_play_btn.setStyleSheet("""
            QPushButton {
                background: #1a3a2e;
                color: #88c999;
                font-weight: bold;
                border: 1px solid #88c999;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover { background: #2a4a3e; }
        """)
        self.audio_play_btn.clicked.connect(self.audio_play)
        audio_controls_layout.addWidget(self.audio_play_btn)
        
        self.audio_pause_btn = QPushButton("⏸ Pause")
        self.audio_pause_btn.setStyleSheet("""
            QPushButton {
                background: #4d3b16;
                color: #FFD700;
                font-weight: bold;
                border: 1px solid #FFD700;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover { background: #5d4b26; }
        """)
        self.audio_pause_btn.clicked.connect(self.audio_pause)
        audio_controls_layout.addWidget(self.audio_pause_btn)
        
        self.audio_stop_btn = QPushButton("■ Stop")
        self.audio_stop_btn.setStyleSheet("""
            QPushButton {
                background: #3a1a1a;
                color: #ff6b6b;
                font-weight: bold;
                border: 1px solid #ff6b6b;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover { background: #4a2a2a; }
        """)
        self.audio_stop_btn.clicked.connect(self.audio_stop)
        audio_controls_layout.addWidget(self.audio_stop_btn)
        
        self.control_layout.addLayout(audio_controls_layout)
        
        # === POST-PROCESSING EFFECTS ===
        effects_label = QLabel("═══ VISUAL EFFECTS ═══")
        effects_label.setStyleSheet("font-weight: bold; color: #ff9f43; background: #1a1a1a; padding: 5px; border: 1px solid #ff9f43; border-radius: 3px;")
        self.control_layout.addWidget(effects_label)
        
        self.bloom_btn = QPushButton("✨ Bloom/Glow ON")
        self.bloom_btn.setStyleSheet("""
            QPushButton {
                background: #ff9f43;
                color: white;
                font-weight: bold;
                border: 1px solid #ff7f00;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover { background: #ffc857; }
        """)
        self.bloom_btn.clicked.connect(self.toggle_bloom)
        self.control_layout.addWidget(self.bloom_btn)
        
        # 1. NEW NARRATIVE ACTS (OPENING CEREMONY)
        opening_acts = [
            ("--- OUVERTURE (ACTES) ---", None),
            ("Acte 0: Silence Sacred", "act0_pre_opening"),
            ("Acte I: Naissance (Dunes)", "act1_desert"),
            ("Acte II: La Pluie Sacrée", "act2_sacred_rain"),
            ("Acte III: Typographie", "act3_typography"),
            ("Acte IV: Science & Beauté", "act4_science"),
            ("Acte V: L'Ame Africaine", "act5_african_soul"),
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
            ("🔥 22ème ÉDITION 🔥", "phase_22eme_edition"),
        ]

        # 3. HERITAGE & MODELS
        heritage_phases = [
            ("--- HÉRITAGE & SPÉCIAL ---", None),
            ("🌀 Spirale Touareg 🌀", "phase_touareg_spiral"),
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
            elif code == "phase_22eme_edition":
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff6b35, stop:1 #004e89);
                        color: white;
                        font-weight: bold;
                        border: 2px solid #ff6b35;
                        border-radius: 4px;
                        padding: 8px;
                    }
                    QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff8555, stop:1 #006bb3); }
                """)
                print("DEBUG: 22EMEEDITION button created.")

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
            if self.simulation_widget.audio.audio_loaded:
                self.simulation_widget.audio.pause()
            self.play_btn.setText("Play")
        else:
            self.simulation_widget.play()
            if self.simulation_widget.audio.audio_loaded:
                self.simulation_widget.audio.unpause()
            self.play_btn.setText("Pause")

    def reset_simulation(self):
        self.simulation_widget.reset()
        self.play_btn.setText("Play")
    
    # === AUTO-SEQUENCING METHODS ===
    def start_sequence(self):
        """Start the automatic phase sequence."""
        sequence = ["phase2_anem", "phase_22eme_edition", "phase3_jcn", "phase4_fes"]
        self.simulation_widget.start_sequence(sequence, duration_per_phase=8.0)
        self.start_seq_btn.setText("▶ Running...")
        self.start_seq_btn.setEnabled(False)
    
    def pause_sequence(self):
        """Pause/resume sequence."""
        self.simulation_widget.pause_sequence()
        if self.simulation_widget.sequence_paused:
            self.pause_seq_btn.setText("▶ Resume")
        else:
            self.pause_seq_btn.setText("⏸ Pause")
    
    def rewind_sequence(self):
        """Rewind to first phase."""
        self.simulation_widget.rewind_sequence()
        self.start_seq_btn.setEnabled(True)
        self.start_seq_btn.setText("▶ Start Sequence")
    
    def next_phase_in_sequence(self):
        """Go to next phase manually."""
        self.simulation_widget.next_phase_in_sequence()
    
    def prev_phase_in_sequence(self):
        """Go to previous phase manually."""
        self.simulation_widget.prev_phase_in_sequence()
    
    def audio_play(self):
        """Play audio file."""
        if self.simulation_widget.audio.audio_loaded:
            self.simulation_widget.audio.play()
            self.audio_play_btn.setEnabled(False)
            self.audio_pause_btn.setEnabled(True)
            self.audio_stop_btn.setEnabled(True)
        else:
            print("ERROR: No audio loaded")
    
    def audio_pause(self):
        """Pause audio playback."""
        if self.simulation_widget.audio.audio_loaded:
            self.simulation_widget.audio.pause()
            self.audio_play_btn.setEnabled(True)
            self.audio_pause_btn.setEnabled(False)
            self.audio_stop_btn.setEnabled(True)
    
    def audio_stop(self):
        """Stop audio playback."""
        if self.simulation_widget.audio.audio_loaded:
            self.simulation_widget.audio.stop()
            self.audio_play_btn.setEnabled(True)
            self.audio_pause_btn.setEnabled(False)
            self.audio_stop_btn.setEnabled(False)
    
    def load_audio_file(self):
        """Open file dialog to load audio file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Audio File", 
            "", 
            "Audio Files (*.mp3 *.wav *.flac);;All Files (*)"
        )
        if filepath:
            success = self.simulation_widget.load_audio_file(filepath)
            if success:
                import os
                filename = os.path.basename(filepath)
                self.audio_status_label.setText(f"✓ Loaded: {filename}")
                self.audio_status_label.setStyleSheet("color: #88c999; font-size: 10px; font-weight: bold;")
            else:
                self.audio_status_label.setText("✗ Failed to load audio")
                self.audio_status_label.setStyleSheet("color: #ff6b6b; font-size: 10px; font-weight: bold;")
    
    def toggle_bloom(self):
        """Toggle bloom/glow effect."""
        is_enabled = self.simulation_widget.toggle_bloom()
        if is_enabled:
            self.bloom_btn.setText("✨ Bloom/Glow ON")
            self.bloom_btn.setStyleSheet("""
                QPushButton {
                    background: #ff9f43;
                    color: white;
                    font-weight: bold;
                    border: 1px solid #ff7f00;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover { background: #ffc857; }
            """)
        else:
            self.bloom_btn.setText("✨ Bloom/Glow OFF")
            self.bloom_btn.setStyleSheet("""
                QPushButton {
                    background: #333;
                    color: #999;
                    font-weight: bold;
                    border: 1px solid #666;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover { background: #444; }
            """)
