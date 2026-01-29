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

# === SYSTÈME DE TRANSITIONS PROFESSIONNELLES ===
from transition_system import (
    ProfessionalTransitionSystem, 
    LivingFormationAnimator,
    TransitionState,
    EasingFunctions
)
from formation_choreographer import ShowChoreographer, TransitionPresets

class SimulationCore(QOpenGLWidget):
    def __init__(self, sim_config, vis_config):
        super().__init__()
        self.sim_config = sim_config
        self.vis_config = vis_config
        self.is_playing = False
        
        num_drones = sim_config['simulation']['max_drones']
        
        # Subsystems
        self.drone_manager = DroneManager(sim_config, vis_config)
        self.camera = CameraSystem()
        self.lighting = LightingSystem(vis_config)
        self.formations = FormationLibrary()
        self.audio = AudioSystem()  # New audio system
        self.post_processing = PostProcessingPipeline()  # Bloom/glow shaders
        
        # === SYSTÈME DE TRANSITIONS PROFESSIONNELLES ===
        self.pro_transition = ProfessionalTransitionSystem(num_drones)
        self.living_animator = LivingFormationAnimator()
        self.choreographer = ShowChoreographer(num_drones, self.formations)
        
        # Mode professionnel activé/désactivé
        self.pro_mode_enabled = True  # Active le système pro par défaut
        self.global_light_multiplier = 1.0  # Multiplicateur de lumière global
        
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
        self.target_colors = np.ones((num_drones, 3)) # Default White
        
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
        # Appliquer le multiplicateur de lumière global pour le blackout
        gl.glDepthMask(gl.GL_FALSE)
        gl.glPointSize(12.0)
        
        light_mult = float(self.global_light_multiplier)  # Convertir en float Python
        
        if light_mult > 0.01:  # Ne dessiner que si pas en blackout total
            gl.glBegin(gl.GL_POINTS)
            for i in range(len(positions)):
                col = colors[i]
                # Simple flicker + multiplicateur de lumière
                pulse = (0.2 + 0.05 * math.sin(i*0.13 + self.phase_timer*5.0)) * light_mult
                gl.glColor4f(float(col[0] * light_mult), float(col[1] * light_mult), float(col[2] * light_mult), float(pulse)) 
                gl.glVertex3f(float(positions[i,0]), float(positions[i,1]), float(positions[i,2]))
            gl.glEnd()
        gl.glDepthMask(gl.GL_TRUE)
        
        # 2. Core (White Hot Center) - Draw second, avec multiplicateur de lumière
        gl.glPointSize(4.0)
        light_mult = float(self.global_light_multiplier)  # Convertir en float Python
        
        if light_mult > 0.01:  # Ne dessiner que si pas en blackout total
            gl.glBegin(gl.GL_POINTS)
            for i in range(len(positions)):
                gl.glColor4f(light_mult, light_mult, light_mult, light_mult)
                gl.glVertex3f(float(positions[i,0]), float(positions[i,1]), float(positions[i,2]))
            gl.glEnd()
            
        # Draw Water Surface
        self._draw_grid()

    def _draw_grid(self):
        """Dessine une surface d'eau réfléchissante bleu nuit profond"""
        gl.glDisable(gl.GL_LIGHTING)
        
        # ═══════════════════════════════════════════════════════════════
        # SURFACE D'EAU RÉFLÉCHISSANTE - "Lac de Nuit"
        # ═══════════════════════════════════════════════════════════════
        # Plan d'eau à Y = -5m (sous le niveau du sol visible)
        # Effet de profondeur et reflets subtils
        
        water_level = -5.0
        water_size = 300.0
        
        # Activer le blending pour la transparence
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Surface d'eau principale (bleu nuit profond avec transparence)
        # RGBA: Bleu nuit très sombre avec alpha 0.85
        gl.glColor4f(0.02, 0.04, 0.12, 0.85)
        
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(-water_size, water_level, -water_size)
        gl.glVertex3f(water_size, water_level, -water_size)
        gl.glVertex3f(water_size, water_level, water_size)
        gl.glVertex3f(-water_size, water_level, water_size)
        gl.glEnd()
        
        # Lignes de reflets subtils (simulation de vagues légères)
        # Utiliser le temps de simulation pour animer légèrement
        import time
        t = time.time() * 0.3  # Animation lente
        
        gl.glColor4f(0.05, 0.08, 0.18, 0.4)  # Bleu légèrement plus clair, semi-transparent
        gl.glBegin(gl.GL_LINES)
        
        # Lignes horizontales ondulées (reflets de la lune)
        import math
        for i in range(-10, 11, 2):
            z_base = i * 25
            for x in range(-int(water_size), int(water_size) + 1, 10):
                z_offset = math.sin(x * 0.02 + t) * 3
                gl.glVertex3f(x, water_level + 0.1, z_base + z_offset)
                gl.glVertex3f(x + 10, water_level + 0.1, z_base + math.sin((x + 10) * 0.02 + t) * 3)
        gl.glEnd()
        
        # Cercles concentriques subtils (effet de gouttes de pluie passées)
        gl.glColor4f(0.08, 0.12, 0.22, 0.25)
        gl.glBegin(gl.GL_LINE_LOOP)
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            r = 50 + math.sin(t * 2) * 5
            gl.glVertex3f(math.cos(rad) * r, water_level + 0.1, math.sin(rad) * r)
        gl.glEnd()
        
        gl.glDisable(gl.GL_BLEND)
        gl.glEnable(gl.GL_LIGHTING)

    def set_phase(self, phase_name):
        """Définit une nouvelle phase avec transition professionnelle optionnelle"""
        
        old_phase = self.current_phase
        self.current_phase = phase_name
        self.phase_timer = 0.0
        self.state_timer = 0.0
        self.phase_state = 0 
        
        num_drones = self.sim_config['simulation']['max_drones']
        targets, colors = self.formations.get_phase(phase_name, num_drones)
        
        # === TRANSITION PROFESSIONNELLE (MODE PRO) ===
        # Utilise le système de blackout magique si activé
        if self.pro_mode_enabled and old_phase and old_phase != phase_name:
            # Récupérer les positions/couleurs actuelles
            current_pos, current_cols = self.drone_manager.get_render_data()
            
            # Démarrer une transition professionnelle
            self.pro_transition.start_transition(
                from_positions=current_pos.copy(),
                from_colors=current_cols.copy(),
                to_positions=targets.copy(),
                to_colors=colors.copy()
            )
            
            print(f"[PRO TRANSITION] {old_phase} → {phase_name}")
            print(f"  - Fade Out: {self.pro_transition.timing.fade_out}s")
            print(f"  - Blackout: {self.pro_transition.timing.blackout}s")
            print(f"  - Transit:  {self.pro_transition.timing.transit}s")
            print(f"  - Fade In:  {self.pro_transition.timing.fade_in}s")
        else:
            # Mode normal (pas de transition)
            self.pro_transition.is_active = False
        
        # === MORPHING TRANSITION SETUP (Legacy) ===
        should_transition = phase_name in ["phase10_touareg", "dubai_camel", "phase_touareg_spiral"] or self.sequence_enabled
        
        if should_transition and not self.pro_mode_enabled:
            if self.transition_mode == False:
                self.transition_start_pos = self.drone_manager.positions.copy()
            else:
                self.transition_start_pos = self.drone_manager.positions.copy()
            
            self.transition_target_pos = targets
            self.transition_progress = 0.0
            self.transition_mode = True
            self.transition_duration = 2.0
        else:
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
            
            # === MISE À JOUR DES ANIMATIONS (Living Formations) ===
            self.living_animator.update(dt)
            
            # === AUDIO ANALYSIS UPDATE ===
            if self.audio.audio_loaded:
                self.audio.update(dt)
                self.audio_energy = self.audio.get_audio_energy()
            else:
                # Placeholder: sine wave modulation
                self.audio_energy = 0.5 + 0.5 * np.sin(self.phase_timer * 2.0)
            
            # ═══════════════════════════════════════════════════════════════
            # SYSTÈME DE TRANSITIONS PROFESSIONNELLES
            # ═══════════════════════════════════════════════════════════════
            if self.pro_mode_enabled and self.pro_transition.is_active:
                # Mettre à jour la transition
                self.pro_transition.update(dt)
                
                # Obtenir le multiplicateur de lumière (pour blackout/fade)
                self.global_light_multiplier = self.pro_transition.get_light_multiplier()
                
                # Obtenir les positions pendant le transit (dans le noir)
                positions = self.pro_transition.get_positions()
                colors = self.pro_transition.get_colors()
                
                # Appliquer les intensités individuelles
                intensities = self.pro_transition.get_intensities()
                for i in range(len(colors)):
                    colors[i] = colors[i] * intensities[i]
                
                # Mettre à jour le drone manager
                self.drone_manager.set_formation(positions, colors)
                
                # Afficher l'état de transition pour debug
                state = self.pro_transition.get_state()
                if state == TransitionState.BLACKOUT:
                    # Fond encore plus sombre pendant le blackout
                    pass
                elif state == TransitionState.TRANSIT_DARK:
                    # Les drones bougent mais sont invisibles!
                    pass
                    
            else:
                # Mode normal: pas de transition en cours
                self.global_light_multiplier = 1.0
            
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
            # Use Smart Cinematic for dynamic "living" phases (Act 1 Desert, Act 2, Act 9 Eagle)
            if self.current_phase in ["act1_desert", "act2_desert_seveille", "act9_eagle", "miroir_celeste"]:
                positions, _ = self.drone_manager.get_render_data()
                self.camera.update_smart_cinematic(positions, dt)
            else:
                self.camera.update(dt)
            
            # --- STATE MACHINE LOGIC (seulement si pas en transition pro) ---
            if not (self.pro_mode_enabled and self.pro_transition.is_active):
            
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
                if self.current_phase in ["miroir_celeste", "act1_desert", "act2_desert_seveille", "phase1_pluie", "phase10_touareg", "dubai_camel", "act5_tree_of_life", "act8_finale", "act9_eagle"]:
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
                        if self.current_phase in ["phase11_croix_agadez", "phase1_pluie", "phase7_carte", "act1_desert", "act6_identity", "act8_finale"]:
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
                
                # === MORPHING TRANSITION LOGIC (Legacy) ===
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTÈME DE TRANSITIONS PROFESSIONNELLES - CONTRÔLES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def toggle_pro_mode(self):
        """Active/désactive le mode transitions professionnelles."""
        self.pro_mode_enabled = not self.pro_mode_enabled
        status = "ACTIVÉ" if self.pro_mode_enabled else "DÉSACTIVÉ"
        print(f"[PRO MODE] {status}")
        return self.pro_mode_enabled
    
    def set_transition_timing(self, preset: str = 'dramatic'):
        """
        Définit le timing des transitions.
        Presets: 'quick', 'dramatic', 'instant', 'ethereal'
        """
        from formation_choreographer import TransitionPresets
        
        presets = {
            'quick': TransitionPresets.quick_fade(),
            'dramatic': TransitionPresets.dramatic(),
            'instant': TransitionPresets.instant(),
            'ethereal': TransitionPresets.ethereal()
        }
        
        if preset in presets:
            timing = presets[preset]
            self.pro_transition.timing.fade_out = timing['fade_out']
            self.pro_transition.timing.blackout = timing['blackout']
            self.pro_transition.timing.transit = timing['transit']
            self.pro_transition.timing.fade_in = timing['fade_in']
            print(f"[TIMING] Preset '{preset}' appliqué")
        else:
            print(f"[TIMING] Preset inconnu: {preset}")
    
    def get_transition_info(self) -> dict:
        """Retourne les informations sur la transition en cours."""
        if self.pro_transition.is_active:
            return {
                'active': True,
                'state': self.pro_transition.get_state().name,
                'progress': self.pro_transition.progress,
                'light_multiplier': self.global_light_multiplier,
                'is_blackout': self.pro_transition.is_dark()
            }
        return {
            'active': False,
            'state': 'IDLE',
            'progress': 0.0,
            'light_multiplier': 1.0,
            'is_blackout': False
        }
    
    def force_blackout(self, duration: float = 2.0):
        """Force un blackout immédiat."""
        self.global_light_multiplier = 0.0
        # Programmer le retour de la lumière
        print(f"[BLACKOUT] Forcé pour {duration}s")

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
