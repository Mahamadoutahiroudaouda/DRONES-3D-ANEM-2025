from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer, Qt
import OpenGL.GL as gl
import numpy as np
import math

from drone_manager import DroneManager
from camera_system import CameraSystem
from lighting_system import LightingSystem
from formation_library import FormationLibrary

class SimulationCore(QOpenGLWidget):
    def __init__(self, sim_config, vis_config):
        super().__init__()
        self.sim_config = sim_config
        self.vis_config = vis_config
        self.is_playing = False
        
        # Subsystems
        self.drone_manager = DroneManager(sim_config, vis_config)
        self.camera = CameraSystem()
        self.lighting = LightingSystem(vis_config)
        self.formations = FormationLibrary()
        
        # Render Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16) # ~60 FPS
        
        # Interaction
        self.last_mouse_pos = None

        # State Machine Initialization
        self.current_phase = "" # Default none
        self.phase_timer = 0.0
        self.state_timer = 0.0
        self.phase_state = 0
        self.target_colors = np.ones((self.sim_config['simulation']['max_drones'], 3)) # Default White

    def initializeGL(self):
        gl.glClearColor(0, 0, 0, 1) # DEEP BLACK - "beaucoup plus noir, profond"
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        
        self.lighting.setup()
        
        # Initialize display list or VBO for drone model here if needed
        # For now, immediate mode / display lists for simplicity
        self.drone_display_list = gl.glGenLists(1)
        gl.glNewList(self.drone_display_list, gl.GL_COMPILE)
        self._draw_drone_model()
        gl.glEndList()

    def _draw_sphere(self, radius, slices, stacks):
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = math.sin(lat0) * radius
            zr0 = math.cos(lat0) * radius
            
            lat1 = math.pi * (-0.5 + float(i+1) / stacks)
            z1 = math.sin(lat1) * radius
            zr1 = math.cos(lat1) * radius
            
            gl.glBegin(gl.GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                gl.glNormal3f(x * zr0, y * zr0, z0)
                gl.glVertex3f(x * zr0, y * zr0, z0)
                
                gl.glNormal3f(x * zr1, y * zr1, z1)
                gl.glVertex3f(x * zr1, y * zr1, z1)
            gl.glEnd()

    def _draw_drone_model(self):
        # Simple cube/cross representation if OBJ loader not ready
        size = self.vis_config['visuals']['drone']['size']
        gl.glPushMatrix()
        gl.glScalef(size, size, size)
        
        # Body
        self._draw_sphere(0.2, 8, 8)
        
        # Arms
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(-0.5, 0, 0)
        gl.glVertex3f(0.5, 0, 0)
        gl.glVertex3f(0, 0, -0.5)
        gl.glVertex3f(0, 0, 0.5)
        gl.glEnd()
        
        gl.glPopMatrix()

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        import OpenGL.GLU as glu
        aspect = w / h if h > 0 else 1.0
        glu.gluPerspective(45.0, aspect, 0.1, 1000.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        
        self.camera.apply_view()
        
        # Draw Drones
        positions, colors = self.drone_manager.get_render_data()
        
        # Optimization: Use instancing if possible, but loop is fine for 1000 drones in Python if logic is light
        for i in range(len(positions)):
            pos = positions[i]
            col = colors[i]
            
            gl.glPushMatrix()
            gl.glTranslatef(pos[0], pos[1], pos[2])
            
            # Distance based LOD or Size modulation could go here
            
            gl.glColor3f(col[0], col[1], col[2])
            gl.glCallList(self.drone_display_list)
            
            gl.glPopMatrix()
            
        # Draw Ground Grid
        self._draw_grid()

    def _draw_grid(self):
        gl.glDisable(gl.GL_LIGHTING)
        gl.glColor3f(0.2, 0.2, 0.2)
        gl.glBegin(gl.GL_LINES)
        for i in range(-200, 201, 20):
            gl.glVertex3f(i, 0, -200)
            gl.glVertex3f(i, 0, 200)
            gl.glVertex3f(-200, 0, i)
            gl.glVertex3f(200, 0, i)
        gl.glEnd()
        gl.glEnable(gl.GL_LIGHTING)

    def set_phase(self, phase_name):
        self.current_phase = phase_name
        self.phase_timer = 0.0
        self.state_timer = 0.0
        self.phase_state = 0 
        
        num_drones = self.sim_config['simulation']['max_drones']
        targets, colors = self.formations.get_phase(phase_name, num_drones)
        
        # --- SCENOGRAPHIC COLOR OVERRIDE IN TRANSIT ---
        # For Phase 6 (Flag), starting colors must be neutral stars
        if phase_name == "phase6_drapeau":
             # We want to keep the appearance of starry night during transition
             neutral_colors = np.tile(self.formations.colors["star_white"], (num_drones, 1))
             self.drone_manager.set_formation(targets, neutral_colors)
        else:
             self.drone_manager.set_formation(targets, colors)
        
        # Store final colors for reveal
        self.target_colors = colors 
        
        self.update()

    def update_simulation(self):
        if self.is_playing:
            dt = 0.016 
            self.phase_timer += dt
            self.state_timer += dt
            
            # --- STATE MACHINE LOGIC ---
            
            # Constants
            TRANSIT_TIME = 6.0 # Time for travel
            BLACKOUT_TIME = 0.5 # Arret/Extinction
            FADE_IN_TIME = 1.0  # Allumage Progressif
            SHOW_TIME = 1.5     # Jeu de lumiere
            
            # Default Targets (Static)
            current_targets, current_colors = self.formations.get_phase(self.current_phase, self.sim_config['simulation']['max_drones'])
            
            # --- PHASE SPECIFIC OVERRIDES (Animation) ---
            if self.current_phase == "phase1_pluie":
                # Descent Animation: "3 Vagues / Contingents"
                # Split drones into 3 groups based on index
                # Wave 1: 0-333 drops t=0..4
                # Wave 2: 334-666 drops t=4..8
                # Wave 3: 667-1000 drops t=8..12
                # TRANSIT_TIME must be long enough (e.g. 15s)
                
                if self.phase_state == 0: # TRANSIT
                     num_drones = len(current_targets)
                     num_layers = 5 # Matching _phase_1_pluie
                     drones_per_layer = num_drones // num_layers
                     
                     fall_start_h = 100.0 # Height above target
                     wave_duration = 1.2 # How long one wave takes to fall
                     delay_between_waves = 0.8
                     
                     for l in range(num_layers):
                         start_idx = l * drones_per_layer
                         end_idx = (l+1) * drones_per_layer if l < num_layers-1 else num_drones
                         
                         start_time = l * delay_between_waves
                         local_t = self.state_timer - start_time
                         
                         if local_t < 0:
                             current_targets[start_idx:end_idx, 1] += fall_start_h
                         elif local_t < wave_duration:
                             progress = local_t / wave_duration
                             offset = fall_start_h * (1.0 - progress)
                             current_targets[start_idx:end_idx, 1] += offset
                         else:
                             pass # Landed
                
            # --- STATE MACHINE COLOR OVERRIDES ---
            
            # Determine if this is a "Text" or "Narrative" phase for specific logic
            is_text_phase = self.current_phase in ["phase2_anem", "phase3_jcn", "phase4_fes", "phase5_niger", "act3_typography"]
            is_stealth_start = self.current_phase in ["act0_pre_opening"]
            
            # Sparkle / Starry Factor (Stars vivantes)
            # Subtle pulsation with sky-blue tinting
            sparkle_pulse = 0.9 + 0.2 * np.random.uniform(0, 1, len(current_colors))
            star_sparkle = sparkle_pulse[:, np.newaxis]
            
            # Twinkling Sky Blue effect (Rare random blue sparks)
            if self.is_playing:
                blue_odds = np.random.rand(len(current_colors)) > 0.98
                current_colors[blue_odds] = self.formations.colors["star_blue"]
            
            # Force dynamic refresh for specialized cinematic phases
            if self.current_phase == "miroir_celeste":
                targets, colors = self.formations.get_phase("miroir_celeste", self.drone_manager.num_drones, t=self.phase_timer)
                self.target_positions = targets
                self.target_colors = colors

            if self.phase_state == 0: # TRANSIT (Mouvement)
                if is_text_phase or is_stealth_start:
                    # Fade to stealth (2% stars)
                    fade_start, fade_end = 2.0, 4.0
                    intensity = 1.0
                    if self.state_timer < fade_start:
                        intensity = 1.0
                    elif self.state_timer < fade_end:
                         progress = (self.state_timer - fade_start) / (fade_end - fade_start)
                         intensity = 1.0 - (0.98 * progress) if is_text_phase else 1.0 - (0.95 * progress)
                    else:
                         intensity = 0.02 if is_text_phase else 0.05
                    
                    current_colors = current_colors * intensity
                else:
                    # Organic phases (Pluie, Map, etc.)
                    # Keep them visible or subtle organic fade
                    current_colors = current_colors * 0.8 # Slightly dimmed but visible
                
                # Update Transit Time
                if self.state_timer > 6.0: 
                    self.phase_state = 1 # ARRIVED
                    self.state_timer = 0
            
            elif self.phase_state == 1: # ARRIVED (PAUSE DANS LE NOIR / STEALTH)
                if is_text_phase:
                    current_colors = current_colors * 0.0 # Total target blackout for text
                else:
                    current_colors = current_colors * 0.2 # Organic shapes stay slightly active
                
                if self.state_timer > 0.5:
                    self.phase_state = 2 # Pre-Ignition
                    self.state_timer = 0
                    
            elif self.phase_state == 2: # BLACKOUT (Silence Visuel)
                current_colors = current_colors * 0.0
                if self.state_timer > BLACKOUT_TIME:
                    self.phase_state = 3
                    self.state_timer = 0
                    
            elif self.phase_state == 3: # FADE IN (RÉVÉLATION)
                # Apply flag color logic for Phase 6 at the reveal
                if self.current_phase == "phase6_drapeau":
                     # During movement and arrived, it should stay Neutral/Stars
                     # Here it reveals the flag colors
                     pass # current_colors already has the flag colors from get_phase
                
                brightness = min(1.0, self.state_timer / FADE_IN_TIME)
                current_colors = current_colors * brightness
                if self.state_timer > FADE_IN_TIME:
                    if self.current_phase in ["phase11_croix_agadez", "phase1_pluie", "phase7_carte", "act0_pre_opening", "act1_desert", "act6_identity", "act8_finale"]:
                        self.phase_state = 5 # Skip flashy show, go straight to Hold
                    else:
                        self.phase_state = 4 # LIGHT SHOW / Sparkling Birth
                    self.state_timer = 0
                    
            elif self.phase_state == 4: # LIGHT SHOW (Sparkling Birth)
                freq = 15.0
                sparkle = 0.7 + 0.3 * np.abs(np.sin(self.state_timer * freq + np.random.uniform(0, 1, len(current_colors))))
                current_colors = current_colors * sparkle[:, np.newaxis]
                if self.state_timer > SHOW_TIME:
                    self.phase_state = 5 # HOLD
                    self.state_timer = 0
            
            elif self.phase_state == 5: # HOLD (Contemplation)
                # Respiration + Star Sparkle
                if self.current_phase == "phase11_croix_agadez":
                    breath = (np.sin(self.phase_timer * 0.8) + 1.0) * 0.5 * 0.3 + 0.7
                else:
                    breath = (np.sin(self.phase_timer * 1.5) + 1.0) * 0.5 * 0.2 + 0.8
                
                current_colors = current_colors * breath * star_sparkle
                
                # --- DYNAMIC FORMATIONS (HOLD STATE) ---
                if self.current_phase in ["phase6_drapeau", "act7_flag"]:
                    # Realistic Waving: Apply dynamic Z wave
                    wave_speed = 3.0
                    wave_freq = 0.05
                    amp = 8.0 if self.current_phase == "phase6_drapeau" else 15.0 # Act 7 is more majestic
                    
                    for i in range(len(current_targets)):
                         x = current_targets[i, 0]
                         current_targets[i, 2] = amp * np.sin(x * wave_freq + self.phase_timer * wave_speed)
                
                if self.current_phase == "act1_desert":
                    # Slow dune breathing
                    amp = 4.0
                    for i in range(len(current_targets)):
                         x, z = current_targets[i, 0], current_targets[i, 2]
                         current_targets[i, 1] += amp * np.sin(x*0.05 + self.phase_timer*0.5) * np.cos(z*0.05)
                
            # Apply to Manager
            self.drone_manager.set_formation(current_targets, current_colors)
            self.drone_manager.update(dt)
            
        self.update()

    def play(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def reset(self):
        self.is_playing = False
        self.update()

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.last_mouse_pos:
                dx = event.pos().x() - self.last_mouse_pos.x()
                dy = event.pos().y() - self.last_mouse_pos.y()
                self.camera.rotate_orbit(dx * 0.5)
            self.last_mouse_pos = event.pos()
            self.update()

