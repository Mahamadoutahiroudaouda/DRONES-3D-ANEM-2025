import numpy as np
import math
from OpenGL.GLU import gluLookAt

class CameraSystem:
    def __init__(self):
        # --- NARRATIVE ANCHORS CONFIGURATION ---
        self.presets = {
            # Ground Intent: Human/Crane perspective (8-15m)
            "ground": {"dist": 200.0, "yaw": 12.0, "pitch": -10.0, "target_y": 55.0, "intent": "human"},
            "desert": {"dist": 300.0, "yaw": 15.0, "pitch": 10.0, "target_y": 2.0, "intent": "plongee"},
            
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
            
            # Africa Map - direct overhead view (drone view)
            "africa_map": {"dist": 150.0, "yaw": 0.0, "pitch": -89.0, "target_y": 50.0, "intent": "vision"},
        }

        # Mapping phases to presets
        self.phase_map = {
            "phase1_pluie": "pluie",
            "act0_pre_opening": "wide",
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
        
        # --- PHASE 1 CINEMATIC SEQUENCE (Three Lectures) ---
        if self.current_phase == "phase1_pluie":
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
