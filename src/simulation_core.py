from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer, Qt
import OpenGL.GL as gl
import numpy as np
import math

from drone_manager import DroneManager
from camera_system import CameraSystem
from lighting_system import LightingSystem
from formation_library import FormationLibrary
from audio_system import AudioSystem
from shader_system import PostProcessingPipeline

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
        self.audio = AudioSystem()  # New audio system
        self.post_processing = PostProcessingPipeline()  # Bloom/glow shaders
        
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
        
        # === AUDIO REACTIVITY ===
        self.audio_energy = 0.5  # Normalized [0, 1], from FFT or placeholder
        self.audio_bpm = 120.0
        self.transition_mode = False  # Flag for morphing transitions
        self.transition_start_pos = None
        self.transition_target_pos = None
        self.transition_progress = 0.0
        
        # === AUTO-SEQUENCING SYSTEM ===
        self.sequence_enabled = False
        self.sequence_list = ["phase2_anem", "phase_22eme_edition", "phase3_jcn", "phase4_fes"]
        self.sequence_index = 0
        self.sequence_timer = 0.0
        self.sequence_duration = 8.0  # Seconds per phase
        self.sequence_paused = False
        
        # === POST-PROCESSING EFFECTS ===
        self.bloom_enabled = True  # Default: enable bloom
        self.bloom_intensity = 1.5
        self.bloom_threshold = 0.7

    def initializeGL(self):
        gl.glClearColor(0.02, 0.02, 0.05, 1) # DEEP COSMIC BLUE/BLACK
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        
        # --- ENABLE BLENDING FOR GLOW/BLOOM ---
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        self.lighting.setup()
        
        # OPTIMIZATION: USE A SIMPLE QUAD FOR DRONE (BILLBOARD) instead of heavy geometry
        # This Display List will just be a flat square on XY plane
        self.drone_display_list = gl.glGenLists(1)
        gl.glNewList(self.drone_display_list, gl.GL_COMPILE)
        
        # Radius 0.5 quad centered
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0, 0); gl.glVertex3f(-0.5, -0.5, 0)
        gl.glTexCoord2f(1, 0); gl.glVertex3f( 0.5, -0.5, 0)
        gl.glTexCoord2f(1, 1); gl.glVertex3f( 0.5,  0.5, 0)
        gl.glTexCoord2f(0, 1); gl.glVertex3f(-0.5,  0.5, 0)
        gl.glEnd()
        
        gl.glEndList()

    def _draw_sphere(self, radius, slices, stacks):
        # Deprecated / Unused for performance
        pass

    def _draw_drone_model(self):
        # Deprecated logic - Replaced by billboard in paintGL
        pass
        
    def _draw_billboard_texture(self):
        # Procedural Circle Texture Generation (Soft Glow)
        # Ideally we generate a texture once in initGL
        # For this prototype we rely on geometry alpha falloff which is hard without shaders
        # So we stick to simple GL_POINTS with smoothing or lightweight geometry
        pass 

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
        
        # OPTIMIZATION: USE GL_POINT_SPRITES (Fastest possible method for thousands of particles)
        # Instead of looping and drawing spheres
        
        gl.glEnable(gl.GL_POINT_SMOOTH)
        
        # 1. Macro Halo (Background Glow) - Draw first, No Depth Write
        gl.glDepthMask(gl.GL_FALSE)
        gl.glPointSize(12.0)
        gl.glBegin(gl.GL_POINTS)
        for i in range(len(positions)):
            # Halo is colored and transparent
            # Manually simulate pulse here inside loop is costly but acceptable for 1000 points
            # Vectorizing this would be better but requires VBOs which is complex refactor
            col = colors[i]
            # Simple flicker
            pulse = 0.2 + 0.05 * math.sin(i*0.13 + self.phase_timer*5.0)
            gl.glColor4f(col[0], col[1], col[2], pulse) 
            gl.glVertex3f(positions[i,0], positions[i,1], positions[i,2])
        gl.glEnd()
        gl.glDepthMask(gl.GL_TRUE)
        
        # 2. Core (White Hot Center) - Draw second
        gl.glPointSize(4.0)
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_POINTS)
        for i in range(len(positions)):
             gl.glVertex3f(positions[i,0], positions[i,1], positions[i,2])
        gl.glEnd()
            
        # Draw Ground Grid
        self._draw_grid()
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
        
        # === MORPHING TRANSITION SETUP ===
        # Store current positions as start point for smooth morphing
        # Only enable transition for specific phases and autosequence
        should_transition = phase_name in ["phase10_touareg", "phase_touareg_spiral"] or self.sequence_enabled
        
        if should_transition:
            if self.transition_mode == False:  # First time transitioning
                self.transition_start_pos = self.drone_manager.positions.copy()
            else:
                self.transition_start_pos = self.drone_manager.positions.copy()
            
            self.transition_target_pos = targets
            self.transition_progress = 0.0
            self.transition_mode = True
            self.transition_duration = 2.0  # 2 seconds for smooth morphing
        else:
            # No transition for other phases - instant change
            self.transition_mode = False
        
        # --- SCENOGRAPHIC COLOR OVERRIDE IN TRANSIT ---
        self.drone_manager.set_formation(targets, colors)
        
        # Store final colors for reveal
        self.target_colors = colors 
        
        # --- DYNAMIC CAMERA PRESET ---
        self.camera.set_phase_view(phase_name)
        
        self.update()

    def update_simulation(self):
        if self.is_playing:
            dt = 0.016 
            self.phase_timer += dt
            self.state_timer += dt
            
            # === AUDIO ANALYSIS UPDATE ===
            if self.audio.audio_loaded:
                self.audio.update(dt)
                self.audio_energy = self.audio.get_audio_energy()
            else:
                # Placeholder: sine wave modulation
                self.audio_energy = 0.5 + 0.5 * np.sin(self.phase_timer * 2.0)
            
            # === AUTO-SEQUENCING SYSTEM ===
            if self.sequence_enabled and not self.sequence_paused:
                self.sequence_timer += dt
                if self.sequence_timer >= self.sequence_duration:
                    # Advance to next phase
                    self.sequence_timer = 0.0
                    self.sequence_index = (self.sequence_index + 1) % len(self.sequence_list)
                    next_phase = self.sequence_list[self.sequence_index]
                    self.set_phase(next_phase)
            
            # --- LIVING CINEMATIC CAMERA ---
            # Handles smooth transitions, phase-presets, and micro-drifts
            # Use Smart Cinematic for dynamic "living" phases (Act 1 Desert, Act 9 Eagle)
            if self.current_phase in ["act1_desert", "act9_eagle", "miroir_celeste"]:
                positions, _ = self.drone_manager.get_render_data()
                self.camera.update_smart_cinematic(positions, dt)
            else:
                self.camera.update(dt)
            
            # --- STATE MACHINE LOGIC ---
            
            # Constants
            TRANSIT_TIME = 4.0 # Time for travel (Faster)
            BLACKOUT_TIME = 0.5 # Arret/Extinction
            FADE_IN_TIME = 1.0  # Allumage Progressif
            SHOW_TIME = 1.5     # Jeu de lumiere
            
            # Default Targets (Static)
            current_targets, current_colors = self.formations.get_phase(
                self.current_phase, 
                self.sim_config['simulation']['max_drones'],
                t=self.phase_timer,
                audio_energy=self.audio_energy
            )
            
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
            TEXT_PHASES = ["phase2_anem", "phase3_jcn", "phase4_fes", "phase5_niger", "act3_typography"]
            is_text_phase = self.current_phase in TEXT_PHASES
            is_flag_phase = self.current_phase == "phase6_drapeau"
            
            # Force dynamic refresh for specialized cinematic phases
            if self.current_phase in ["miroir_celeste", "act1_desert", "phase1_pluie", "phase10_touareg", "act8_finale", "act9_eagle"]:
                current_targets, current_colors = self.formations.get_phase(self.current_phase, self.drone_manager.num_drones, t=self.phase_timer, audio_energy=self.audio_energy)

            # --- PHASE 6: FLAG LOGIC (Neutral Stars until Reveal) ---
            if is_flag_phase and self.phase_state < 3: # Before Reveal
                # Keep neutral star colors during movement and blackout
                current_colors = np.tile(self.formations.colors["star_white"], (len(current_colors), 1))

            # --- GENERAL SPARKLE (Subtle, for all except Flag Reveal) ---
            # "Ciel étoilé vivant" - Subtle sparkle for elegance
            if not (is_flag_phase and self.phase_state >= 3):
                sparkle_intensity = 0.85 + 0.15 * np.random.uniform(0, 1, len(current_colors))
                current_colors = current_colors * sparkle_intensity[:, np.newaxis]

            if self.phase_state == 0: # TRANSIT (Mouvement)
                if is_text_phase:
                    # TEXT PHASES: Start Alive -> Fade to Stealth -> Invisible Arrival
                    # 0-2s: Visible (Alive)
                    # 2-4s: Fade Out
                    # >4s: Stealth (Near Invisible)
                    fade_start, fade_end = 2.0, 4.0
                    if self.state_timer < fade_start:
                        intensity = 1.0
                    elif self.state_timer < fade_end:
                        progress = (self.state_timer - fade_start) / (fade_end - fade_start)
                        intensity = 1.0 - (0.95 * progress) # Fade to 0.05
                    else:
                        intensity = 0.05 # Stealth mode
                    current_colors = current_colors * intensity
                
                # Update Transit Time
                if self.state_timer > TRANSIT_TIME: 
                    self.phase_state = 1 # ARRIVED
                    self.state_timer = 0
            
            elif self.phase_state == 1: # ARRIVED (PAUSE DANS LE NOIR / STEALTH)
                if is_text_phase:
                    current_colors = current_colors * 0.02 # Almost invisible
                
                if self.state_timer > 0.5:
                    self.phase_state = 2 # Pre-Ignition
                    self.state_timer = 0
                    
            elif self.phase_state == 2: # BLACKOUT (Silence Visuel)
                current_colors = current_colors * 0.0 # Total silence
                if self.state_timer > BLACKOUT_TIME:
                    self.phase_state = 3
                    self.state_timer = 0
                    
            elif self.phase_state == 3: # FADE IN (RÉVÉLATION)
                # For Flag: Colors are already correct (passed the < 3 check)
                # For Text: Fade in to solid letters
                
                brightness = min(1.0, self.state_timer / FADE_IN_TIME)
                current_colors = current_colors * brightness
                
                if self.state_timer > FADE_IN_TIME:
                    if self.current_phase in ["phase11_croix_agadez", "phase1_pluie", "phase7_carte", "act0_pre_opening", "act1_desert", "act6_identity", "act8_finale"]:
                        self.phase_state = 5 # Skip flashy show, go straight to Hold
                    else:
                        self.phase_state = 4 # LIGHT SHOW / Sparkling Birth
                    self.state_timer = 0
                    
            elif self.phase_state == 4: # LIGHT SHOW (Sparkling Birth)
                # No artificial sparkle override, respect original colors + subtle sparkle
                if self.state_timer > SHOW_TIME:
                    self.phase_state = 5 # HOLD
                    self.state_timer = 0
            
            elif self.phase_state == 5: # HOLD (Contemplation)
                # No artificial breathing/sparkle override, respect original colors + subtle sparkle
                
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
            self.drone_manager.update(dt, time_absolute=self.phase_timer)
            
            # === MORPHING TRANSITION LOGIC ===
            # If in transition mode, smoothly interpolate positions toward target formation
            if self.transition_mode:
                self.transition_progress += dt / self.transition_duration
                
                if self.transition_progress < 1.0:
                    # Ease-in-out cubic interpolation for smooth morphing
                    t_ease = self.transition_progress
                    t_ease = t_ease * t_ease * (3.0 - 2.0 * t_ease) if t_ease <= 1.0 else 1.0
                    
                    # Linear interpolation with easing
                    morphed_pos = (1.0 - t_ease) * self.transition_start_pos + t_ease * self.transition_target_pos
                    self.drone_manager.positions[:] = morphed_pos
                else:
                    # Transition complete
                    self.transition_mode = False
                    self.drone_manager.positions[:] = self.transition_target_pos
            
        self.update()

    def play(self):
        self.is_playing = True
        # Play audio if loaded
        if self.audio.audio_loaded:
            self.audio.play()

    def pause(self):
        self.is_playing = False
        # Pause audio if playing
        if self.audio.audio_loaded:
            self.audio.pause()

    def reset(self):
        self.is_playing = False
        # Stop audio playback
        if self.audio.audio_loaded:
            self.audio.stop()
        self.update()
    
    # === AUTO-SEQUENCING CONTROLS ===
    def start_sequence(self, sequence_list=None, duration_per_phase=8.0):
        """Start automatic phase sequencing."""
        if sequence_list:
            self.sequence_list = sequence_list
        self.sequence_duration = duration_per_phase
        self.sequence_index = 0
        self.sequence_timer = 0.0
        self.sequence_paused = False
        self.sequence_enabled = True
        self.is_playing = True
        # Start with first phase
        self.set_phase(self.sequence_list[0])
    
    def stop_sequence(self):
        """Stop automatic sequencing."""
        self.sequence_enabled = False
    
    def pause_sequence(self):
        """Pause/resume automatic sequencing."""
        self.sequence_paused = not self.sequence_paused
    
    def rewind_sequence(self):
        """Reset to first phase in sequence."""
        if self.sequence_enabled:
            self.sequence_index = 0
            self.sequence_timer = 0.0
            self.set_phase(self.sequence_list[0])
    
    def next_phase_in_sequence(self):
        """Manually advance to next phase."""
        if self.sequence_enabled:
            self.sequence_index = (self.sequence_index + 1) % len(self.sequence_list)
            self.sequence_timer = 0.0
            self.set_phase(self.sequence_list[self.sequence_index])
    
    def prev_phase_in_sequence(self):
        """Manually go back to previous phase."""
        if self.sequence_enabled:
            self.sequence_index = (self.sequence_index - 1) % len(self.sequence_list)
            self.sequence_timer = 0.0
            self.set_phase(self.sequence_list[self.sequence_index])
    
    # === BLOOM/GLOW CONTROLS ===
    def toggle_bloom(self):
        """Toggle bloom effect on/off."""
        self.bloom_enabled = not self.bloom_enabled
        return self.bloom_enabled
    
    def set_bloom_intensity(self, intensity):
        """Set bloom intensity (0.0 to 3.0)."""
        self.bloom_intensity = np.clip(intensity, 0.0, 3.0)
    
    def load_audio_file(self, filepath):
        """Load audio file for music reactivity."""
        return self.audio.load_audio(filepath)

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

