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
        gl.glClearColor(*self.vis_config['visuals']['background_color'])
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
        # State Machine: 
        # 0: TRANSIT (Moving to target)
        # 1: ARRIVED_WAIT (Short pause before effect)
        # 2: BLACKOUT (Extinction)
        # 3: FADE_IN (Allumage progressif)
        # 4: LIGHT_SHOW (Jeu de lumière)
        # 5: HOLD (Maintien + Respiration)
        self.phase_state = 0 
        self.state_timer = 0.0
        
        num_drones = self.sim_config['simulation']['max_drones']
        targets, colors = self.formations.get_phase(phase_name, num_drones)
        
        # In TRANSIT, we update targets in manager
        self.drone_manager.set_formation(targets, colors)
        
        # Store final colors for the fade/show effects
        self.target_colors = colors 
        
        self.update()

    def update_simulation(self):
        if self.is_playing:
            dt = 0.016 
            self.phase_timer += dt
            self.state_timer += dt
            
            # --- STATE MACHINE LOGIC ---
            
            # Constants
            TRANSIT_TIME = 10.0 # Time for descent (Phase 1) or travel
            BLACKOUT_TIME = 1.0 # Arret/Extinction
            FADE_IN_TIME = 2.0  # Allumage Progressif
            SHOW_TIME = 3.0     # Jeu de lumiere
            
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
                     third = num_drones // 3
                     
                     fall_start_h = 40.0 # Height above target to start falling from
                     move_duration = 4.0 # How long one wave takes to fall
                     
                     # Wave 1
                     # Time window: 0 to 4
                     # If time < 0, it's high. If time > 4, it's landed.
                     
                     def apply_wave(start_idx, end_idx, start_time):
                         local_t = self.state_timer - start_time
                         if local_t < 0:
                             # Haven't started falling yet -> Stay High
                             current_targets[start_idx:end_idx, 1] += fall_start_h
                         elif local_t < move_duration:
                             # Falling
                             progress = local_t / move_duration
                             # Linear interp from fall_start_h to 0
                             offset = fall_start_h * (1.0 - progress)
                             current_targets[start_idx:end_idx, 1] += offset
                         else:
                             # Landed (Offset 0)
                             pass
                     
                     apply_wave(0, third, 0.0)
                     apply_wave(third, 2*third, 4.0)
                     apply_wave(2*third, num_drones, 8.0)
                
            # --- STATE MACHINE COLOR OVERRIDES ---
            
            if self.phase_state == 0: # TRANSIT (Mouvement / Chute)
                # Drones move to current_targets
                # Colors are Standard (White)
                
                # Update Transit Time to accommodate 3 waves
                if self.state_timer > 13.0: # 3 waves * 4s + 1s buffer
                    self.phase_state = 1 # ARRIVED
                    self.state_timer = 0
            
            elif self.phase_state == 1: # ARRIVED / PRE-BLACKOUT
                 if self.state_timer > 0.5: # Short stabilization
                     self.phase_state = 2 # BLACKOUT
                     self.state_timer = 0
            
            elif self.phase_state == 2: # BLACKOUT (Extinction)
                # Force Black
                current_colors = np.zeros_like(current_colors)
                if self.state_timer > BLACKOUT_TIME:
                    self.phase_state = 3 # FADE IN
                    self.state_timer = 0
            
            elif self.phase_state == 3: # FADE IN (Allumage progressif)
                # Interpolate Black -> Base Color
                progress = min(1.0, self.state_timer / FADE_IN_TIME)
                current_colors = current_colors * progress
                if self.state_timer > FADE_IN_TIME:
                    self.phase_state = 4 # LIGHT SHOW
                    self.state_timer = 0
            
            elif self.phase_state == 4: # LIGHT SHOW (Jeu de lumière court)
                # Sparkle / Flash effect
                freq = 20.0
                sparkle = np.abs(np.sin(self.state_timer * freq + np.random.uniform(0, 1, len(current_colors))))
                # Mix
                current_colors = current_colors * sparkle[:, np.newaxis]
                if self.state_timer > SHOW_TIME:
                    self.phase_state = 5 # HOLD
                    self.state_timer = 0
            
            elif self.phase_state == 5: # HOLD (Maintien + Respiration)
                # Permanent Breathing
                breath = (np.sin(self.phase_timer * 1.5) + 1.0) * 0.5 * 0.4 + 0.6
                current_colors = current_colors * breath
                
                # --- DYNAMIC FORMATIONS (HOLD STATE) ---
                if self.current_phase == "phase6_drapeau":
                    # Realistic Waving: Apply dynamic Z wave
                    # Wave front moves over time
                    wave_speed = 3.0
                    wave_freq = 0.05
                    amp = 8.0
                    
                    for i in range(len(current_targets)):
                         x = current_targets[i, 0]
                         current_targets[i, 2] = amp * np.sin(x * wave_freq + self.phase_timer * wave_speed)
                
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

