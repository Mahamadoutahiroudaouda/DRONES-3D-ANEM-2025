"""
═══════════════════════════════════════════════════════════════════════════════
              SYSTÈME DE TRANSITIONS PROFESSIONNELLES - ANEM 2025
═══════════════════════════════════════════════════════════════════════════════
Implémente les 4 principes fondamentaux des shows de drones professionnels:
1. Blackout Magique - On ne voit JAMAIS les drones bouger
2. Swarm Intelligence - Mouvements organiques comme des essaims
3. Fading Professionnel - Transitions lumineuses progressives
4. Living Formations - Formations jamais complètement statiques
═══════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import time as time_module


class TransitionState(Enum):
    """Machine à états professionnelle pour les transitions"""
    FORMATION_HOLD = auto()      # Formation visible, stable avec micro-mouvements
    FADE_OUT = auto()            # Éteint progressivement (0.5s)
    BLACKOUT = auto()            # Noir complet - suspense (2-3s)
    TRANSIT_DARK = auto()        # Mouvement dans le noir (4-6s)
    FADE_IN = auto()             # Allume progressivement (0.5-1s)
    IDLE = auto()                # En attente


@dataclass
class TransitionTiming:
    """Timing professionnel pour les transitions"""
    fade_out: float = 0.5        # Durée du fade out
    blackout: float = 2.5        # Durée du noir complet
    transit: float = 5.0         # Durée du mouvement dans le noir
    fade_in: float = 0.8         # Durée du fade in
    hold_min: float = 3.0        # Durée minimum d'une formation
    
    
@dataclass
class DroneTrajectory:
    """Trajectoire individuelle d'un drone"""
    start: np.ndarray
    end: np.ndarray
    control_point: np.ndarray
    delay: float                 # Délai de démarrage (staggered)
    duration: float
    

class EasingFunctions:
    """Fonctions d'easing pour mouvements naturels"""
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Accélération quadratique"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Décélération quadratique"""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Accélération puis décélération"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Accélération cubique (plus douce)"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Décélération cubique"""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Transition cubique complète"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def smoothstep(t: float) -> float:
        """Transition très douce (Hermite)"""
        t = np.clip(t, 0, 1)
        return t * t * (3 - 2 * t)
    
    @staticmethod
    def smootherstep(t: float) -> float:
        """Transition encore plus douce"""
        t = np.clip(t, 0, 1)
        return t * t * t * (t * (6 * t - 15) + 10)


class BezierCurve:
    """Calcul de courbes de Bézier pour trajectoires organiques"""
    
    @staticmethod
    def quadratic(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, t: float) -> np.ndarray:
        """Courbe de Bézier quadratique (3 points)"""
        return (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2
    
    @staticmethod
    def cubic(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, t: float) -> np.ndarray:
        """Courbe de Bézier cubique (4 points)"""
        return ((1-t)**3 * p0 + 
                3*(1-t)**2*t * p1 + 
                3*(1-t)*t**2 * p2 + 
                t**3 * p3)


class ProfessionalLighting:
    """Contrôle d'éclairage professionnel"""
    
    def __init__(self):
        self.time = 0.0
        self.twinkle_frequencies = None
        self.twinkle_phases = None
        
    def initialize(self, num_drones: int):
        """Initialise les fréquences de scintillement uniques par drone"""
        rng = np.random.RandomState(42)
        self.twinkle_frequencies = 3.0 + rng.uniform(0, 2, num_drones)
        self.twinkle_phases = rng.uniform(0, 2 * np.pi, num_drones)
        
    def update(self, dt: float):
        """Met à jour le temps"""
        self.time += dt
    
    def calculate_intensities(self, num_drones: int, state: TransitionState, 
                             progress: float) -> np.ndarray:
        """Calcule l'intensité lumineuse de chaque drone"""
        
        if self.twinkle_frequencies is None:
            self.initialize(num_drones)
        
        intensities = np.ones(num_drones)
        
        if state == TransitionState.FORMATION_HOLD:
            # Lumière pleine + scintillement subtil
            for i in range(num_drones):
                freq = self.twinkle_frequencies[i]
                phase = self.twinkle_phases[i]
                twinkle = np.sin(self.time * freq + phase) * 0.08
                intensities[i] = 1.0 + twinkle
                
                # Occasionnellement, un scintillement plus fort (comme une étoile)
                if np.random.random() < 0.0005:
                    intensities[i] += np.random.uniform(0.1, 0.25)
        
        elif state == TransitionState.FADE_OUT:
            # Éteint progressivement avec easing quadratique
            ease_out = EasingFunctions.ease_out_quad(1 - progress)
            intensities *= ease_out
            
        elif state in [TransitionState.BLACKOUT, TransitionState.TRANSIT_DARK]:
            # COMPLÈTEMENT ÉTEINT - c'est le secret!
            intensities *= 0.0
            
        elif state == TransitionState.FADE_IN:
            # Allume progressivement avec easing cubique
            ease_in = EasingFunctions.ease_in_cubic(progress)
            intensities *= ease_in
            
            # Staggered fade-in (les drones proches du centre s'allument en premier)
            # Optionnel: peut être activé selon la formation
            
        elif state == TransitionState.IDLE:
            # Pulsation très subtile
            pulse = 0.95 + 0.05 * np.sin(self.time * 0.5)
            intensities *= pulse
        
        return np.clip(intensities, 0, 1.2)
    
    def apply_color_fade(self, color_a: np.ndarray, color_b: np.ndarray, 
                        progress: float, mode: str = 'smooth') -> np.ndarray:
        """Transition de couleur professionnelle"""
        
        if mode == 'smooth':
            # Interpolation avec smoothstep
            t = EasingFunctions.smoothstep(progress)
        elif mode == 'ease':
            t = EasingFunctions.ease_in_out_cubic(progress)
        else:
            t = progress
            
        return color_a * (1 - t) + color_b * t


class BioSwarmEngine:
    """Moteur de mouvement organique type essaim"""
    
    def __init__(self, num_drones: int):
        self.num_drones = num_drones
        self.velocities = np.zeros((num_drones, 3))
        self.rng = np.random.RandomState(123)
        
        # Paramètres de l'essaim
        self.max_speed = 8.0           # m/s
        self.max_acceleration = 3.0     # m/s²
        self.alignment_weight = 0.3
        self.separation_weight = 2.0
        self.cohesion_weight = 0.1
        self.target_weight = 1.0
        
        # Rayon de perception
        self.perception_radius = 15.0
        self.separation_radius = 3.0
        
    def calculate_movement(self, current_positions: np.ndarray, 
                          target_positions: np.ndarray, 
                          time: float, dt: float) -> np.ndarray:
        """Calcule le mouvement naturel d'essaim vers les cibles"""
        
        new_positions = current_positions.copy()
        
        for i in range(self.num_drones):
            # 1. VECTEUR VERS LA CIBLE
            to_target = target_positions[i] - current_positions[i]
            distance = np.linalg.norm(to_target)
            
            if distance < 0.1:
                continue  # Déjà à destination
                
            # 2. VITESSE ADAPTATIVE
            if distance > 50:
                target_speed = self.max_speed
            elif distance > 20:
                target_speed = 5.0
            elif distance > 5:
                target_speed = 2.0
            else:
                target_speed = distance * 0.5  # Ralentit en approche
            
            # Direction vers la cible
            if distance > 0:
                direction = to_target / distance
            else:
                direction = np.array([0, 0, 0])
            
            # 3. FORCE D'ALIGNEMENT (avec voisins)
            alignment_force = self._calculate_alignment(i, current_positions)
            
            # 4. FORCE DE SÉPARATION (évitement)
            separation_force = self._calculate_separation(i, current_positions)
            
            # 5. TURBULENCE NATURELLE
            turbulence = np.array([
                np.sin(time * 0.8 + i * 0.1) * 0.5,
                np.cos(time * 0.6 + i * 0.15) * 0.3,
                np.sin(time * 0.9 + i * 0.12) * 0.4
            ])
            
            # 6. COMBINAISON DES FORCES
            desired_velocity = (
                direction * target_speed * self.target_weight +
                alignment_force * self.alignment_weight +
                separation_force * self.separation_weight +
                turbulence * 0.3
            )
            
            # 7. ACCÉLÉRATION DOUCE (pas de changements brusques)
            acceleration = (desired_velocity - self.velocities[i])
            accel_magnitude = np.linalg.norm(acceleration)
            if accel_magnitude > self.max_acceleration:
                acceleration = acceleration / accel_magnitude * self.max_acceleration
            
            self.velocities[i] += acceleration * dt
            
            # 8. LIMITE DE VITESSE
            speed = np.linalg.norm(self.velocities[i])
            if speed > self.max_speed:
                self.velocities[i] = self.velocities[i] / speed * self.max_speed
            
            # 9. INTÉGRATION DE POSITION
            new_positions[i] += self.velocities[i] * dt
            
            # 10. MICRO-VIBRATIONS (anti-robot)
            new_positions[i] += np.array([
                np.sin(time * 10 + i) * 0.03,
                np.cos(time * 8 + i * 0.7) * 0.02,
                np.sin(time * 12 + i * 0.5) * 0.03
            ])
        
        return new_positions
    
    def _calculate_alignment(self, drone_idx: int, positions: np.ndarray) -> np.ndarray:
        """Calcule la force d'alignement avec les voisins"""
        avg_velocity = np.zeros(3)
        count = 0
        
        for j in range(self.num_drones):
            if j == drone_idx:
                continue
            
            dist = np.linalg.norm(positions[j] - positions[drone_idx])
            if dist < self.perception_radius:
                avg_velocity += self.velocities[j]
                count += 1
        
        if count > 0:
            avg_velocity /= count
        
        return avg_velocity
    
    def _calculate_separation(self, drone_idx: int, positions: np.ndarray) -> np.ndarray:
        """Calcule la force de séparation pour éviter les collisions"""
        separation = np.zeros(3)
        
        for j in range(self.num_drones):
            if j == drone_idx:
                continue
            
            diff = positions[drone_idx] - positions[j]
            dist = np.linalg.norm(diff)
            
            if dist < self.separation_radius and dist > 0:
                # Plus proche = plus forte répulsion
                separation += diff / (dist * dist)
        
        return separation


class ProfessionalTransitionSystem:
    """Système de transition complet niveau professionnel"""
    
    def __init__(self, num_drones: int = 1000):
        self.num_drones = num_drones
        self.state = TransitionState.IDLE
        self.progress = 0.0
        self.total_time = 0.0
        
        # Composants
        self.timing = TransitionTiming()
        self.lighting = ProfessionalLighting()
        self.swarm = BioSwarmEngine(num_drones)
        
        # Données de transition
        self.current_positions = np.zeros((num_drones, 3))
        self.current_colors = np.ones((num_drones, 3))
        self.target_positions = np.zeros((num_drones, 3))
        self.target_colors = np.ones((num_drones, 3))
        
        # Trajectoires pré-calculées
        self.trajectories: List[DroneTrajectory] = []
        
        # État actif
        self.is_active = False
        
        # Random generator pour reproductibilité
        self.rng = np.random.RandomState(42)
        
    def start_transition(self, from_positions: np.ndarray, from_colors: np.ndarray,
                        to_positions: np.ndarray, to_colors: np.ndarray,
                        transit_duration: float = None):
        """Démarre une transition professionnelle"""
        
        self.current_positions = from_positions.copy()
        self.current_colors = from_colors.copy()
        self.target_positions = to_positions.copy()
        self.target_colors = to_colors.copy()
        
        if transit_duration:
            self.timing.transit = transit_duration
        
        # Pré-calculer toutes les trajectoires
        self._calculate_trajectories()
        
        # Démarrer la machine à états
        self.state = TransitionState.FADE_OUT
        self.progress = 0.0
        self.is_active = True
        
        print(f"[TRANSITION] Démarrage: FADE_OUT ({self.timing.fade_out}s)")
        
    def _calculate_trajectories(self):
        """Pré-calcule toutes les trajectoires avec courbes de Bézier"""
        
        self.trajectories = []
        
        # Calculer les distances pour le staggered start
        distances = np.linalg.norm(self.target_positions - self.current_positions, axis=1)
        
        # Trier par distance (les plus proches partent en premier)
        sorted_indices = np.argsort(distances)
        delays = np.zeros(self.num_drones)
        
        for rank, idx in enumerate(sorted_indices):
            delays[idx] = rank * 0.012  # 12ms entre chaque drone
        
        for i in range(self.num_drones):
            start = self.current_positions[i]
            end = self.target_positions[i]
            
            # Point de contrôle pour courbe de Bézier
            # Monte légèrement au milieu pour éviter les croisements
            mid_point = (start + end) / 2
            height_boost = 10 + self.rng.uniform(5, 15)
            lateral_offset = self.rng.uniform(-8, 8, 2)
            
            control_point = np.array([
                mid_point[0] + lateral_offset[0],
                mid_point[1] + height_boost,
                mid_point[2] + lateral_offset[1]
            ])
            
            traj = DroneTrajectory(
                start=start.copy(),
                end=end.copy(),
                control_point=control_point,
                delay=delays[i],
                duration=self.timing.transit
            )
            
            self.trajectories.append(traj)
    
    def update(self, dt: float) -> bool:
        """Met à jour l'état de transition. Retourne True si actif."""
        
        if not self.is_active:
            return False
        
        self.total_time += dt
        self.lighting.update(dt)
        
        # Déterminer la durée de l'état actuel
        current_duration = self._get_current_duration()
        
        # Progresser
        self.progress += dt / current_duration
        
        # Transition d'état si nécessaire
        if self.progress >= 1.0:
            self._advance_state()
            
        return self.is_active
    
    def _get_current_duration(self) -> float:
        """Retourne la durée de l'état actuel"""
        durations = {
            TransitionState.FADE_OUT: self.timing.fade_out,
            TransitionState.BLACKOUT: self.timing.blackout,
            TransitionState.TRANSIT_DARK: self.timing.transit,
            TransitionState.FADE_IN: self.timing.fade_in,
            TransitionState.FORMATION_HOLD: self.timing.hold_min,
            TransitionState.IDLE: 1.0
        }
        return durations.get(self.state, 1.0)
    
    def _advance_state(self):
        """Passe à l'état suivant"""
        
        transitions = {
            TransitionState.FADE_OUT: TransitionState.BLACKOUT,
            TransitionState.BLACKOUT: TransitionState.TRANSIT_DARK,
            TransitionState.TRANSIT_DARK: TransitionState.FADE_IN,
            TransitionState.FADE_IN: TransitionState.FORMATION_HOLD,
            TransitionState.FORMATION_HOLD: TransitionState.IDLE,
        }
        
        old_state = self.state
        self.state = transitions.get(self.state, TransitionState.IDLE)
        self.progress = 0.0
        
        if self.state == TransitionState.IDLE:
            self.is_active = False
            # Mettre à jour les positions courantes avec les cibles
            self.current_positions = self.target_positions.copy()
            self.current_colors = self.target_colors.copy()
            
        print(f"[TRANSITION] {old_state.name} → {self.state.name}")
    
    def get_positions(self) -> np.ndarray:
        """Retourne les positions actuelles des drones"""
        
        if self.state == TransitionState.TRANSIT_DARK:
            # Calcule les positions pendant le transit (mais drones éteints!)
            positions = np.zeros_like(self.current_positions)
            
            for i, traj in enumerate(self.trajectories):
                # Appliquer le délai individualisé (staggered)
                effective_progress = self.progress - (traj.delay / traj.duration)
                effective_progress = np.clip(effective_progress, 0, 1)
                
                # Appliquer easing
                eased_progress = EasingFunctions.ease_in_out_cubic(effective_progress)
                
                # Calculer position sur courbe de Bézier
                positions[i] = BezierCurve.quadratic(
                    traj.start, traj.control_point, traj.end, eased_progress
                )
            
            return positions
            
        elif self.state == TransitionState.FADE_IN:
            # Pendant fade-in, on est déjà aux positions cibles
            return self.target_positions.copy()
            
        elif self.state == TransitionState.FORMATION_HOLD:
            # Position cible avec micro-mouvements
            return self._apply_living_formation(self.target_positions)
            
        else:
            # FADE_OUT, BLACKOUT : rester aux positions courantes
            return self.current_positions.copy()
    
    def _apply_living_formation(self, positions: np.ndarray) -> np.ndarray:
        """Ajoute des micro-mouvements pour donner vie à la formation"""
        
        living_positions = positions.copy()
        t = self.total_time
        
        for i in range(len(positions)):
            # 1. Respiration subtile (mouvement vertical)
            breath = np.sin(t * 0.3 + i * 0.01) * 0.15
            
            # 2. Légère oscillation latérale
            sway_x = np.sin(t * 0.2 + i * 0.02) * 0.1
            sway_z = np.cos(t * 0.25 + i * 0.015) * 0.1
            
            living_positions[i, 0] += sway_x
            living_positions[i, 1] += breath
            living_positions[i, 2] += sway_z
        
        return living_positions
    
    def get_colors(self) -> np.ndarray:
        """Retourne les couleurs actuelles des drones"""
        
        if self.state in [TransitionState.FADE_OUT, TransitionState.BLACKOUT, 
                          TransitionState.TRANSIT_DARK]:
            return self.current_colors.copy()
            
        elif self.state == TransitionState.FADE_IN:
            # Transition de couleur progressive
            progress = EasingFunctions.smoothstep(self.progress)
            return self.current_colors * (1 - progress) + self.target_colors * progress
            
        else:
            return self.target_colors.copy()
    
    def get_intensities(self) -> np.ndarray:
        """Retourne les intensités lumineuses"""
        return self.lighting.calculate_intensities(self.num_drones, self.state, self.progress)
    
    def get_state(self) -> TransitionState:
        """Retourne l'état actuel"""
        return self.state
    
    def is_dark(self) -> bool:
        """Retourne True si les drones doivent être éteints"""
        return self.state in [TransitionState.BLACKOUT, TransitionState.TRANSIT_DARK]
    
    def get_light_multiplier(self) -> float:
        """Retourne le multiplicateur global de lumière"""
        if self.state == TransitionState.FADE_OUT:
            return 1.0 - EasingFunctions.ease_out_quad(self.progress)
        elif self.state in [TransitionState.BLACKOUT, TransitionState.TRANSIT_DARK]:
            return 0.0
        elif self.state == TransitionState.FADE_IN:
            return EasingFunctions.ease_in_cubic(self.progress)
        else:
            return 1.0


class LivingFormationAnimator:
    """Anime les formations pour qu'elles ne soient jamais statiques"""
    
    def __init__(self):
        self.time = 0.0
        
    def update(self, dt: float):
        self.time += dt
    
    def animate(self, positions: np.ndarray, colors: np.ndarray, 
                formation_type: str = 'default') -> Tuple[np.ndarray, np.ndarray]:
        """Anime une formation avec des micro-mouvements"""
        
        animated_positions = positions.copy()
        animated_colors = colors.copy()
        num = len(positions)
        t = self.time
        
        # Calculer le centre de la formation
        center = np.mean(positions, axis=0)
        
        for i in range(num):
            # Distance au centre
            dist_to_center = np.linalg.norm(positions[i] - center)
            
            # 1. RESPIRATION GLOBALE
            breath_scale = 1.0 + 0.02 * np.sin(t * 0.4)
            vector_from_center = positions[i] - center
            animated_positions[i] = center + vector_from_center * breath_scale
            
            # 2. ONDULATION VERTICALE
            wave = np.sin(t * 0.5 + positions[i, 0] * 0.05 + positions[i, 2] * 0.03) * 0.2
            animated_positions[i, 1] += wave
            
            # 3. MICRO-ROTATION autour du centre (très lent)
            if dist_to_center > 5:
                angle = np.sin(t * 0.1) * 0.005
                rx = vector_from_center[0]
                rz = vector_from_center[2]
                animated_positions[i, 0] = center[0] + rx * np.cos(angle) - rz * np.sin(angle)
                animated_positions[i, 2] = center[2] + rx * np.sin(angle) + rz * np.cos(angle)
            
            # 4. SCINTILLEMENT DE COULEUR
            twinkle = 1.0 + 0.08 * np.sin(t * 3 + i * 0.1)
            animated_colors[i] = np.clip(colors[i] * twinkle, 0, 1.5)
        
        return animated_positions, animated_colors
    
    def apply_wind_effect(self, positions: np.ndarray, wind_strength: float = 0.5,
                         wind_direction: Tuple[float, float] = (1, 0)) -> np.ndarray:
        """Applique un effet de vent sur les positions"""
        
        animated = positions.copy()
        t = self.time
        
        # Normaliser la direction du vent
        wind_dir = np.array([wind_direction[0], 0, wind_direction[1]])
        wind_dir = wind_dir / (np.linalg.norm(wind_dir) + 0.001)
        
        for i in range(len(positions)):
            # Les drones plus hauts sont plus affectés par le vent
            height_factor = np.clip((positions[i, 1] - 10) / 50, 0, 1)
            
            # Rafales variables
            gust = wind_strength * (1 + 0.5 * np.sin(t * 2 + i * 0.05))
            
            # Appliquer le déplacement
            displacement = wind_dir * gust * height_factor
            displacement += np.array([
                np.sin(t * 3 + i * 0.1) * 0.2,
                np.cos(t * 2.5 + i * 0.08) * 0.1,
                np.sin(t * 2.8 + i * 0.12) * 0.2
            ]) * height_factor
            
            animated[i] += displacement
        
        return animated


# ═══════════════════════════════════════════════════════════════════════════════
#                          EXPORT DES CLASSES PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'TransitionState',
    'TransitionTiming', 
    'ProfessionalTransitionSystem',
    'ProfessionalLighting',
    'BioSwarmEngine',
    'LivingFormationAnimator',
    'EasingFunctions',
    'BezierCurve'
]
