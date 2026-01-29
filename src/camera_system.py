import numpy as np
import math
from OpenGL.GLU import gluLookAt

class CameraSystem:
    def __init__(self):
        # --- NARRATIVE ANCHORS CONFIGURATION ---
        self.presets = {
            # Ground Intent: Human/Crane perspective (8-15m)
            "ground": {"dist": 200.0, "yaw": 12.0, "pitch": -10.0, "target_y": 55.0, "intent": "human"},
            "desert": {"dist": 180.0, "yaw": -30.0, "pitch": -25.0, "target_y": 30.0, "intent": "plongee"},
            
            # Interaction Intent: Relationship/Flow perspective (30-50m)
            "interaction": {"dist": 220.0, "yaw": 18.0, "pitch": -12.0, "target_y": 65.0, "intent": "observer"},
            "intimate": {"dist": 170.0, "yaw": 10.0, "pitch": -11.0, "target_y": 50.0, "intent": "observer"},
            
            # Drones Intent: Coverage/Monumental (50-70m)
            "monument": {"dist": 200.0, "yaw": 12.0, "pitch": -14.0, "target_y": 75.0, "intent": "monumental"},
            "text": {"dist": 240.0, "yaw": 18.0, "pitch": -13.0, "target_y": 80.0, "intent": "monumental"},
            "heritage": {"dist": 190.0, "yaw": 20.0, "pitch": -14.0, "target_y": 85.0, "intent": "monumental"},
            "science": {"dist": 220.0, "yaw": 18.0, "pitch": -13.0, "target_y": 75.0, "intent": "monumental"},
            
            # Global Intent: Vision System (70-120m)
            "flag": {"dist": 350.0, "yaw": 20.0, "pitch": -8.0, "target_y": 90.0, "intent": "vision"},
            "wide": {"dist": 360.0, "yaw": 20.0, "pitch": -7.0, "target_y": 95.0, "intent": "vision"},
            "wide_opening": {"dist": 150.0, "yaw": 0.0, "pitch": -25.0, "target_y": 30.0, "intent": "vision"},
            
            # Africa Map - direct overhead view (drone view)
            "africa_map": {"dist": 150.0, "yaw": 0.0, "pitch": -89.0, "target_y": 50.0, "intent": "vision"},
        }

        # Mapping phases to presets
        self.phase_map = {
            "phase1_pluie": "pluie",
            "act0_pre_opening": "wide_opening",
            "act1_desert": "desert",
            "act2_sacred_rain": "ground",
            "act3_typography": "text",
            "act4_science": "science",
            "act5_wildlife": "interaction",
            "act5_african_soul": "africa_map",  # Aerial view of Africa
            "act6_identity": "heritage",
            "act7_flag": "flag",
            "act8_finale": "wide",
            "phase9_agadez": "monument",
            "phase10_touareg": "intimate",
            "phase_touareg_spiral": "monument",  # NEW: Spiral from above
            "miroir_celeste": "monument",
            "phase11_croix_agadez": "heritage",
            "phase2_anem": "text",
            "phase3_jcn": "text",
            "phase4_fes": "text",
            "phase5_niger": "text",
            "phase6_drapeau": "flag",
            "phase7_carte": "desert", # Use 'desert' preset settings which is 'plongee' intent
            "phase_22eme_edition": "text",
        }

        # New preset for Phase 1
        self.presets["pluie"] = {"dist": 280.0, "yaw": 12.0, "pitch": -3.0, "target_y": 60.0, "intent": "observer"}

        # --- STATE ---
        self.current_dist = self.presets["ground"]["dist"]
        self.current_yaw = self.presets["ground"]["yaw"]
        self.current_pitch = self.presets["ground"]["pitch"]
        self.current_target_y = self.presets["ground"]["target_y"]
        
        self.target_dist = self.current_dist
        self.target_yaw = self.current_yaw
        self.target_pitch = self.current_pitch
        self.target_target_y = self.current_target_y
        
        self.current_intent = "human"
        self.prev_intent = "human"
        
        self.lerp_speed = 0.5 # Default cinematic speed
        self.drift_time = 0.0
        self.current_phase = "default"
        self.phase_time = 0.0
        
        self.position = np.array([0.0, 0.0, 0.0])
        self.target = np.array([0.0, 50.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])
        self.fov = 45.0
        
        self.update_position()

    def set_phase_view(self, phase_name):
        self.prev_intent = self.current_intent
        self.current_phase = phase_name
        self.phase_time = 0.0
        
        preset_key = self.phase_map.get(phase_name, "ground")
        p = self.presets[preset_key]
        
        self.target_dist = p["dist"]
        self.target_yaw = p["yaw"]
        self.target_pitch = p["pitch"]
        self.target_target_y = p["target_y"]
        self.current_intent = p["intent"]
        
        # --- NARRATIVE TRANSITION LOGIC ---
        # 1. "Return to Earth" Rule:
        # If we come from a 'vision' (global) or high altitude view, we slow down the transition
        # to create a "Sacred Descent" feel.
        if self.prev_intent == "vision" and self.current_intent in ["human", "observer"]:
            self.lerp_speed = 0.25 # Slower for the return to earth
        else:
            self.lerp_speed = 0.8 # Faster normal transitions for responsiveness

    def update_smart_cinematic(self, positions, dt, mode="auto"):
        """
        AI Camera Pilot: Analyzes scene geometry to choose best angles dynamically.
        Priority: Peak Following -> Center Orbit -> Top Down -> Ground Hero
        """
        if positions is None or len(positions) == 0: 
            self.update(dt) # Fallback to standard
            return

        self.phase_time += dt          

        # 1. Feature Extraction (Real-time Scene Analysis)
        # Find highest drone (Peak)
        idx_highest = np.argmax(positions[:, 1])
        peak_pos = positions[idx_highest]
        
        # Calculate Cloud Center
        center_mass = np.mean(positions, axis=0)
        
        # Calculate formation bounds (for better framing)
        min_pos = np.min(positions, axis=0)
        max_pos = np.max(positions, axis=0)
        formation_radius = np.max(max_pos - min_pos) * 0.5
        
        # 2. State Cycle (20s loop)
        cycle_time = (self.phase_time % 20.0) 
        
        target_cam_pos = np.array([0.0, 0.0, 0.0])
        target_look_at = center_mass
        
        if cycle_time < 5.0: 
            # PHASE A: GLOBAL ORBIT (Majestic Overview)
            angle = self.phase_time * 0.15
            dist = 320.0 + formation_radius * 0.5  # Scale with formation
            target_cam_pos = center_mass + np.array([np.cos(angle)*dist, 140.0, np.sin(angle)*dist])
            target_look_at = center_mass

        elif cycle_time < 10.0:
            # PHASE B: "THE SKIM" (Dynamic Peak Chasing)
            # Follow just behind the highest point, more responsive
            target_cam_pos = peak_pos + np.array([-35.0, 25.0, 35.0])
            target_look_at = peak_pos + np.array([5, 10, -5])  # Look slightly ahead

        elif cycle_time < 15.0:
            # PHASE C: TOP DOWN (Technical/Map View) - better framing
            target_cam_pos = center_mass + np.array([0.0, 300.0 + formation_radius * 0.3, 0.1])
            target_look_at = center_mass + np.array([0, 30, 0])

        else:
            # PHASE D: GROUND UP (Heroic Scale) - closer and more dramatic
            target_cam_pos = np.array([center_mass[0] + 40, 5.0, center_mass[2] + 200.0])
            target_look_at = center_mass + np.array([0, 70, 0])

        # 3. Cinematic Smoothing (Faster lerp for more responsive camera)
        smooth = 3.0 * dt  # Increased from 2.0 for snappier response
        self.position = self.position * (1 - smooth) + target_cam_pos * smooth
        self.target = self.target * (1 - smooth) + target_look_at * smooth

    def update(self, dt):
        """Narrative update: Respects Hierarchy, Ground, and Parallax."""
        self.drift_time += dt
        self.phase_time += dt
        
        # ═══════════════════════════════════════════════════════════════
        # ACTE 0: NAISSANCE COSMIQUE - Séquence Cinématique "CIEL RÉALISTE"
        # ═══════════════════════════════════════════════════════════════
        # Nouvelles altitudes réalistes:
        # - Étoiles: 20-40m (visible depuis le sol)
        # - ANEM: 35m (grand texte dans le ciel)
        # - Sphère: 60m (point culminant)
        # - Arc-en-ciel: 20-50m (arc bas et majestueux)
        # - Horizon spectateur: 0m (niveau du sol)
        # ═══════════════════════════════════════════════════════════════
        if self.current_phase == "act0_pre_opening":
            
            if self.phase_time < 3.0:
                # PHASE 1: NUIT PRIMORDIALE (0-3s)
                # Vue depuis le sol, regardant vers le ciel où les étoiles apparaissent (20-40m)
                progress = self.phase_time / 3.0
                
                # Caméra près du sol, regard vers le haut
                self.target_dist = 80.0 + progress * 40.0    # 80 → 120m (proche pour intimité)
                self.target_pitch = -20.0 - progress * 10.0  # -20 → -30 (fort regard vers le haut)
                self.target_yaw = progress * 10.0             # Légère rotation panoramique
                self.target_target_y = 30.0                   # Centre des étoiles (~30m)
                self.lerp_speed = 0.5
                
            elif self.phase_time < 8.0:
                # PHASE 2: CONSTELLATION ANEM (3-8s)
                # Le texte ANEM se forme à 35m d'altitude, large de 120m
                progress = (self.phase_time - 3.0) / 5.0
                
                # Recul progressif pour voir le texte complet
                self.target_dist = 120.0 + progress * 100.0   # 120 → 220m (voir ANEM en entier)
                self.target_pitch = -15.0 - progress * 5.0    # -15 → -20 (vue vers le haut)
                self.target_yaw = 10.0 + progress * 8.0       # Lent panoramique (10 → 18)
                self.target_target_y = 35.0                   # Centre du texte ANEM
                self.lerp_speed = 0.6
                
            elif self.phase_time < 12.0:
                # PHASE 3: CŒUR COSMIQUE (8-12s)
                # La sphère dorée pulse à 60m d'altitude
                progress = (self.phase_time - 8.0) / 4.0
                
                # Rapprochement vers la sphère avec orbite
                self.target_dist = 100.0 - progress * 30.0    # 100 → 70m (proche de la sphère)
                
                # Orbite autour de la sphère
                orbit_angle = progress * 50.0
                self.target_yaw = 18.0 + orbit_angle
                
                # Montée pour voir la sphère en contre-plongée
                self.target_pitch = -20.0 + progress * 25.0   # -20 → +5 (passe au-dessus)
                self.target_target_y = 60.0                   # Centre de la sphère
                
                # Accélération sur la dernière pulsation
                if self.phase_time > 11.0:
                    self.lerp_speed = 1.5
                else:
                    self.lerp_speed = 0.8
                
            else:
                # PHASE 4: ÉCLOSION FINALE (12-20s)
                # Arc-en-ciel entre 20m et 50m d'altitude
                
                if self.phase_time < 12.5:
                    # Explosion initiale (12-12.5s)
                    explosion_progress = (self.phase_time - 12.0) / 0.5
                    self.target_dist = 70.0 + explosion_progress * 130.0   # 70 → 200m (recul rapide)
                    self.target_pitch = 5.0 - explosion_progress * 20.0    # +5 → -15 (bascule vers le haut)
                    self.target_yaw = 68.0 - explosion_progress * 58.0     # Recentrage vers 10
                    self.target_target_y = 40.0                            # Centre de l'explosion
                    self.lerp_speed = 2.5
                    
                elif self.phase_time < 14.0:
                    # Formation arc-en-ciel (12.5-14s)
                    form_progress = (self.phase_time - 12.5) / 1.5
                    self.target_dist = 200.0 + form_progress * 30.0        # 200 → 230m
                    self.target_pitch = -15.0 - form_progress * 5.0        # -15 → -20 (contre-plongée)
                    self.target_yaw = 10.0 - form_progress * 3.0           # Stable autour de 7
                    self.target_target_y = 35.0                            # Centre de l'arc
                    self.lerp_speed = 1.2
                    
                elif self.phase_time < 18.0:
                    # Arc-en-ciel stable (14-18s)
                    hold_progress = (self.phase_time - 14.0) / 4.0
                    self.target_dist = 230.0                               # Distance stable
                    self.target_pitch = -20.0                              # Contre-plongée pour voir l'arc
                    self.target_yaw = 7.0 + hold_progress * 12.0           # Lent panoramique (7 → 19)
                    self.target_target_y = 35.0                            # Centre de l'arc
                    self.lerp_speed = 0.5
                    
                else:
                    # Transition vers Acte 1 (18-20s)
                    trans_progress = (self.phase_time - 18.0) / 2.0
                    self.target_dist = 230.0 + trans_progress * 30.0       # Léger recul
                    self.target_pitch = -20.0 + trans_progress * 10.0      # -20 → -10
                    self.target_yaw = 19.0 - trans_progress * 9.0          # 19 → 10
                    self.target_target_y = 35.0 - trans_progress * 15.0    # 35 → 20 (descente vers les dunes)
                    self.lerp_speed = 0.6
        
        # ═══════════════════════════════════════════════════════════════
        # ACTE 1: LE DÉSERT S'ÉVEILLE - Expérience Saharienne (15s)
        # ═══════════════════════════════════════════════════════════════
        # NOUVELLE CHORÉGRAPHIE:
        # - Partie 1 (0-4s)   : Naissance du sable - Vue satellite → micro
        # - Partie 2 (4-9s)   : Croissance des dunes - Chevauchement
        # - Partie 3 (9-13s)  : Vie du désert - Avec caravane + vent
        # - Partie 4 (13-15s) : Transition - Adieu au désert
        # ═══════════════════════════════════════════════════════════════
        elif self.current_phase == "act1_desert":
            
            if self.phase_time < 1.5:
                # PLAN 1a: VUE SATELLITE (0-1.5s)
                # Démarrage très haut, comme Google Earth
                progress = self.phase_time / 1.5
                
                self.target_dist = 350.0 - progress * 100.0     # 350 → 250 (zoom avant)
                self.target_pitch = 70.0 - progress * 20.0      # 70 → 50 (vue plongeante)
                self.target_yaw = 0.0                           # Face au désert
                self.target_target_y = 30.0                     # Centre de la formation
                self.lerp_speed = 1.2
                
            elif self.phase_time < 4.0:
                # PLAN 1b: ZOOM VERS LE SABLE (1.5-4s)
                # Plongée rapide vers le niveau du sable (comme fourmi)
                progress = (self.phase_time - 1.5) / 2.5
                
                self.target_dist = 250.0 - progress * 150.0     # 250 → 100 (rapprochement rapide)
                self.target_pitch = 50.0 - progress * 60.0      # 50 → -10 (bascule vers horizontal)
                self.target_yaw = progress * 20.0               # 0 → 20 (légère rotation)
                self.target_target_y = 30.0 - progress * 10.0   # 30 → 20 (descend vers le sol)
                self.lerp_speed = 1.5
                
            elif self.phase_time < 6.0:
                # PLAN 2a: MONTÉE SUR DUNE (4-6s)
                # Caméra "grimpe" une dune (mouvement vertical)
                progress = (self.phase_time - 4.0) / 2.0
                
                self.target_dist = 100.0 - progress * 20.0      # 100 → 80 (très proche)
                self.target_pitch = -10.0 - progress * 15.0     # -10 → -25 (regarde vers le haut)
                self.target_yaw = 20.0 + progress * 15.0        # 20 → 35
                self.target_target_y = 20.0 + progress * 20.0   # 20 → 40 (monte vers les crêtes)
                self.lerp_speed = 0.8
                
            elif self.phase_time < 9.0:
                # PLAN 2b: TRAVELLING LE LONG DES CRÊTES (6-9s)
                # Vue rasante, angle bas pour exagérer la hauteur
                progress = (self.phase_time - 6.0) / 3.0
                
                self.target_dist = 80.0 + progress * 40.0       # 80 → 120
                self.target_pitch = -25.0 + progress * 10.0     # -25 → -15
                self.target_yaw = 35.0 + progress * 45.0        # 35 → 80 (grand travelling)
                self.target_target_y = 40.0 - progress * 10.0   # 40 → 30 (suit la crête)
                self.lerp_speed = 0.6
                
                # Tremblement léger (simulation vent)
                if self.phase_time > 7.0:
                    shake = 0.3 * (1.0 + 0.5 * (self.phase_time - 7.0))
                    self.target_pitch += shake * (0.5 - ((self.phase_time * 7) % 1.0))
                
            elif self.phase_time < 11.0:
                # PLAN 3a: AVEC LA CARAVANE (9-11s)
                # Recul pour garder la caravane cadrée, profondeur de champ
                progress = (self.phase_time - 9.0) / 2.0
                
                self.target_dist = 120.0 + progress * 30.0      # 120 → 150
                self.target_pitch = -15.0 - progress * 5.0      # -15 → -20
                self.target_yaw = 80.0 - progress * 50.0        # 80 → 30 (suit la caravane)
                self.target_target_y = 30.0 + progress * 5.0    # 30 → 35
                self.lerp_speed = 0.5
                
            elif self.phase_time < 13.0:
                # PLAN 3b: SPECTACLE DU VENT + VAGUE (11-13s)
                # Caméra fixe sur crête pendant vague de sable
                progress = (self.phase_time - 11.0) / 2.0
                
                self.target_dist = 150.0                        # Distance fixe
                self.target_pitch = -20.0 + progress * 5.0      # -20 → -15
                self.target_yaw = 30.0 + progress * 60.0        # 30 → 90 (rotation rapide avec vague)
                self.target_target_y = 35.0                     # Centre du spectacle
                self.lerp_speed = 0.8
                
                # Tremblement pour simuler le vent fort
                shake_intensity = 0.8 + progress * 0.5
                self.target_pitch += shake_intensity * (0.5 - ((self.phase_time * 5) % 1.0))
                self.target_yaw += shake_intensity * 0.3 * (0.5 - ((self.phase_time * 7) % 1.0))
                
            else:
                # PLAN 4: ADIEU AU DÉSERT (13-15s)
                # Montée en hélicoptère pour vue d'ensemble
                progress = (self.phase_time - 13.0) / 2.0
                progress = min(1.0, progress)
                
                self.target_dist = 150.0 + progress * 100.0     # 150 → 250 (grand recul)
                self.target_pitch = -15.0 + progress * 45.0     # -15 → 30 (passe au-dessus)
                self.target_yaw = 90.0 - progress * 70.0        # 90 → 20 (recentrage)
                self.target_target_y = 35.0 - progress * 10.0   # 35 → 25 (préparation fleuve)
                self.lerp_speed = 0.9
        
        # ═══════════════════════════════════════════════════════════════
        # ACTE 2: LE DÉSERT S'ÉVEILLE - Expérience Saharienne (15s)
        # ═══════════════════════════════════════════════════════════════
        elif self.current_phase == "act2_desert_seveille":
            
            if self.phase_time < 1.5:
                # VUE SATELLITE
                progress = self.phase_time / 1.5
                self.target_dist = 350.0 - progress * 100.0
                self.target_pitch = 70.0 - progress * 20.0
                self.target_yaw = 0.0
                self.target_target_y = 30.0
                self.lerp_speed = 1.2
                
            elif self.phase_time < 4.0:
                # PLONGÉE VERS LE SABLE
                progress = (self.phase_time - 1.5) / 2.5
                self.target_dist = 250.0 - progress * 150.0
                self.target_pitch = 50.0 - progress * 60.0
                self.target_yaw = progress * 20.0
                self.target_target_y = 30.0 - progress * 10.0
                self.lerp_speed = 1.5
                
            elif self.phase_time < 9.0:
                # TRAVELLING LE LONG DES DUNES
                progress = (self.phase_time - 4.0) / 5.0
                self.target_dist = 100.0 + progress * 50.0
                self.target_pitch = -10.0 - progress * 15.0
                self.target_yaw = 20.0 + progress * 60.0
                self.target_target_y = 25.0 + progress * 15.0
                self.lerp_speed = 0.6
                
            elif self.phase_time < 13.0:
                # VIE DU DÉSERT + VAGUE
                progress = (self.phase_time - 9.0) / 4.0
                self.target_dist = 150.0
                self.target_pitch = -20.0 + progress * 5.0
                self.target_yaw = 80.0 - progress * 50.0
                self.target_target_y = 35.0
                self.lerp_speed = 0.7
                
            else:
                # TRANSITION
                progress = (self.phase_time - 13.0) / 2.0
                self.target_dist = 150.0 + progress * 100.0
                self.target_pitch = -15.0 + progress * 35.0
                self.target_yaw = 30.0 - progress * 20.0
                self.target_target_y = 35.0 - progress * 10.0
                self.lerp_speed = 0.8
        
        # --- PHASE 1 CINEMATIC SEQUENCE (Three Lectures) ---
        elif self.current_phase == "phase1_pluie":
            # 1. Plane View (0-15s): Subtle Discovery
            if self.phase_time < 15.0:
                self.target_pitch = -3.0
                self.target_dist = 280.0
            # 2. Oblique Discovery (15-35s): Volume Reveal & Panoramic discovery
            elif self.phase_time < 35.0:
                progress = (self.phase_time - 15.0) / 20.0
                self.target_pitch = -3.0 + (-7.0 * progress) # Smoothly to -10
                self.target_yaw = 12.0 + (8.0 * progress) # Pan 8 degrees
                self.target_dist = 280.0 + (20.0 * progress)
            # 3. Structural Height (35s+): Systemic Vision
            else:
                self.target_pitch = -12.0
                self.target_dist = 320.0
                # Continue very slow panoramic rotation
                self.target_yaw += 0.2 * dt 

        # --- PHASE 7 CINEMATIC SEQUENCE (Far -> Zoom -> Orbit) ---
        if self.current_phase == "phase7_carte":
            # 1. Establish Far (0-8s): Observation of the whole map appearing
            if self.phase_time < 8.0:
                self.target_dist = 450.0
                self.target_pitch = 12.0 # View from above
                self.target_target_y = 65.0
            # 2. The Dive / Zoom (8-20s): Plongee spectaculaire vers la carte
            elif self.phase_time < 20.0:
                progress = (self.phase_time - 8.0) / 12.0
                self.target_dist = 450.0 - (170.0 * progress) # Down to 280
                self.target_pitch = 12.0 + (10.0 * progress) # Up to 22 (more plunge)
            # 3. The Orbit (20s+): Majestueuse rotation d'en haut
            else:
                self.target_dist = 280.0
                self.target_pitch = 22.0
                self.target_yaw += 0.8 * dt # Smooth orbital rotation around the map

        # --- DYNAMIC TEXT PHASES (2-5) ---
        if self.current_phase in ["phase2_anem", "phase3_jcn", "phase4_fes", "phase5_niger"]:
            # Continuous slow orbit to show 3D depth
            self.target_yaw += 3.0 * dt 
            
            # Gentle zoom in/out breathing
            breath = 20.0 * math.sin(self.phase_time * 0.4)
            # Find base viewing distance (approx 260 from preset)
            base_dist = 260.0
            if self.current_phase == "phase5_niger": base_dist = 300.0 # Bigger for big logo
            
            self.target_dist = base_dist + breath

        # 1. Smooth Interpolation to Targets
        self.current_dist += (self.target_dist - self.current_dist) * self.lerp_speed * dt
        self.current_yaw += (self.target_yaw - self.current_yaw) * self.lerp_speed * dt
        self.current_pitch += (self.target_pitch - self.current_pitch) * self.lerp_speed * dt
        self.current_target_y += (self.target_target_y - self.current_target_y) * self.lerp_speed * dt
        
        # 2. Living Camera Micro-Drift (Limited to 1-3m for realism)
        # Slow oscillations reflecting human scale witness
        drift_yaw = 1.2 * math.sin(self.drift_time * 0.08)
        drift_pitch = 0.6 * math.cos(self.drift_time * 0.12)
        drift_dist = 1.5 * math.sin(self.drift_time * 0.06)
        
        # 3. Position Calculation
        final_yaw = self.current_yaw + drift_yaw
        final_pitch = self.current_pitch + drift_pitch
        final_dist = self.current_dist + drift_dist
        
        rad_yaw = math.radians(final_yaw)
        rad_pitch = math.radians(final_pitch)
        
        self.target[1] = self.current_target_y
        
        x = final_dist * math.sin(rad_yaw) * math.cos(rad_pitch)
        y = self.target[1] + final_dist * math.sin(rad_pitch)
        z = final_dist * math.cos(rad_yaw) * math.cos(rad_pitch)
        
        # --- NARRATIVE CONSTRAINTS ---
        
        # Constraint A: NEVER go underground
        y = max(5.0, y)
        
        # Constraint B: Observer Hierarchy (Drones > Camera > Ground)
        # Except for 'plongee' (Act 1), camera should stay visually below the formation center
        if self.current_intent != "plongee":
             if y > self.current_target_y - 5.0: # Keep a 5m margin below the drones
                 y = self.current_target_y - 5.0
                 y = max(5.0, y) # Re-enforce ground safety
        
        self.position = np.array([x, y, z])

    def update_position(self):
        self.update(0.0)

    def apply_view(self):
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            self.target[0], self.target[1], self.target[2],
            self.up[0], self.up[1], self.up[2]
        )

    def rotate_orbit(self, dx):
        """User control override."""
        self.target_yaw += dx * 0.1
