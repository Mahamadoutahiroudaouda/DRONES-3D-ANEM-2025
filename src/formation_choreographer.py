"""
═══════════════════════════════════════════════════════════════════════════════
            CHORÉGRAPHE DE FORMATIONS - ANEM 2025
═══════════════════════════════════════════════════════════════════════════════
Gère l'enchaînement complet du show avec:
- Séquence des formations par acte
- Transitions professionnelles automatiques
- Timing précis synchronisé avec l'audio
- Blackouts magiques entre chaque formation
═══════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum, auto

from transition_system import (
    ProfessionalTransitionSystem,
    LivingFormationAnimator,
    TransitionState,
    EasingFunctions
)


class FormationType(Enum):
    """Types de formations disponibles"""
    # Acte 0 - Naissance Cosmique
    STARS = auto()
    ANEM_LOGO = auto()
    SPHERE = auto()
    RAINBOW = auto()
    
    # Acte 1 - Dunes du Sahara
    SIMPLE_DUNES = auto()
    
    # Acte 2 - Le Désert S'éveille
    DESERT_GENESIS = auto()
    DESERT_GROWTH = auto()
    DESERT_LIFE = auto()
    DESERT_TRANSITION = auto()
    
    # Acte 3 - Fleuve Niger
    RIVER_HEART = auto()
    RIVER_FLOW = auto()
    
    # Transitions
    BLACKOUT = auto()


@dataclass
class FormationSequenceItem:
    """Un élément de la séquence du show"""
    formation_type: FormationType
    duration: float                    # Durée en secondes
    phase_name: str                    # Nom de la phase pour formation_library
    transition_to_next: bool = True    # Faire une transition vers la suivante?
    hold_after: float = 2.0            # Pause après la formation
    description: str = ""              # Description pour debug


@dataclass 
class ActSequence:
    """Séquence complète d'un acte"""
    name: str
    formations: List[FormationSequenceItem] = field(default_factory=list)
    total_duration: float = 0.0
    
    def calculate_duration(self):
        """Calcule la durée totale de l'acte"""
        self.total_duration = sum(f.duration + f.hold_after for f in self.formations)
        # Ajouter le temps des transitions (environ 8s chacune)
        num_transitions = sum(1 for f in self.formations if f.transition_to_next)
        self.total_duration += num_transitions * 8.0


class ShowChoreographer:
    """Chorégraphe principal du show"""
    
    def __init__(self, num_drones: int = 1000, formation_library = None):
        self.num_drones = num_drones
        self.formation_library = formation_library
        
        # Système de transitions
        self.transition_system = ProfessionalTransitionSystem(num_drones)
        self.living_animator = LivingFormationAnimator()
        
        # Séquences par acte
        self.acts: Dict[str, ActSequence] = {}
        self._build_show_sequence()
        
        # État courant
        self.current_act: str = "act0"
        self.current_formation_idx: int = 0
        self.act_start_time: float = 0.0
        self.formation_start_time: float = 0.0
        self.show_time: float = 0.0
        
        # Cache des formations
        self.current_positions = np.zeros((num_drones, 3))
        self.current_colors = np.ones((num_drones, 3))
        self.next_positions = np.zeros((num_drones, 3))
        self.next_colors = np.ones((num_drones, 3))
        
        # État
        self.is_in_transition = False
        self.is_playing = False
        
    def _build_show_sequence(self):
        """Construit la séquence complète du show"""
        
        # ═══════════════════════════════════════════════════════════════
        # ACTE 0 : NAISSANCE COSMIQUE
        # ═══════════════════════════════════════════════════════════════
        act0 = ActSequence(name="Naissance Cosmique")
        act0.formations = [
            FormationSequenceItem(
                formation_type=FormationType.STARS,
                duration=8.0,
                phase_name="act0_stars",
                hold_after=2.0,
                description="Ciel étoilé réaliste"
            ),
            FormationSequenceItem(
                formation_type=FormationType.ANEM_LOGO,
                duration=10.0,
                phase_name="act0_anem",
                hold_after=3.0,
                description="Logo ANEM lumineux"
            ),
            FormationSequenceItem(
                formation_type=FormationType.SPHERE,
                duration=8.0,
                phase_name="act0_sphere",
                hold_after=2.0,
                description="Sphère pulsante"
            ),
            FormationSequenceItem(
                formation_type=FormationType.RAINBOW,
                duration=6.0,
                phase_name="act0_rainbow",
                hold_after=2.0,
                transition_to_next=True,
                description="Arc-en-ciel final"
            ),
        ]
        act0.calculate_duration()
        self.acts["act0"] = act0
        
        # ═══════════════════════════════════════════════════════════════
        # ACTE 1 : DUNES DU SAHARA (Version Simple)
        # ═══════════════════════════════════════════════════════════════
        act1 = ActSequence(name="Dunes du Sahara")
        act1.formations = [
            FormationSequenceItem(
                formation_type=FormationType.SIMPLE_DUNES,
                duration=20.0,
                phase_name="act1_desert",
                hold_after=3.0,
                transition_to_next=True,
                description="Dunes respirantes simples"
            ),
        ]
        act1.calculate_duration()
        self.acts["act1"] = act1
        
        # ═══════════════════════════════════════════════════════════════
        # ACTE 2 : LE DÉSERT S'ÉVEILLE (Version Complexe)
        # ═══════════════════════════════════════════════════════════════
        act2 = ActSequence(name="Le Désert S'éveille")
        act2.formations = [
            FormationSequenceItem(
                formation_type=FormationType.DESERT_GENESIS,
                duration=4.0,
                phase_name="act2_desert_seveille",  # t=0-4
                hold_after=0.0,
                transition_to_next=False,  # Pas de blackout, transition fluide
                description="Genèse du sable"
            ),
            FormationSequenceItem(
                formation_type=FormationType.DESERT_GROWTH,
                duration=5.0,
                phase_name="act2_desert_seveille",  # t=4-9
                hold_after=0.0,
                transition_to_next=False,
                description="Croissance des dunes"
            ),
            FormationSequenceItem(
                formation_type=FormationType.DESERT_LIFE,
                duration=4.0,
                phase_name="act2_desert_seveille",  # t=9-13
                hold_after=0.0,
                transition_to_next=False,
                description="Vie du désert + caravane"
            ),
            FormationSequenceItem(
                formation_type=FormationType.DESERT_TRANSITION,
                duration=2.0,
                phase_name="act2_desert_seveille",  # t=13-15
                hold_after=2.0,
                transition_to_next=True,
                description="Transition magique vers fleuve"
            ),
        ]
        act2.calculate_duration()
        self.acts["act2"] = act2
        
        # ═══════════════════════════════════════════════════════════════
        # ACTE 3 : FLEUVE NIGER
        # ═══════════════════════════════════════════════════════════════
        act3 = ActSequence(name="Fleuve Niger")
        act3.formations = [
            FormationSequenceItem(
                formation_type=FormationType.RIVER_HEART,
                duration=15.0,
                phase_name="act3_fleuve_niger",
                hold_after=3.0,
                transition_to_next=True,
                description="Cœur rouge + contour fleuve"
            ),
        ]
        act3.calculate_duration()
        self.acts["act3"] = act3
        
    def set_formation_library(self, library):
        """Définit la bibliothèque de formations"""
        self.formation_library = library
        
    def start_act(self, act_name: str, start_time: float = 0.0):
        """Démarre un acte spécifique"""
        
        if act_name not in self.acts:
            print(f"[CHOREOGRAPHER] Acte inconnu: {act_name}")
            return False
            
        self.current_act = act_name
        self.current_formation_idx = 0
        self.act_start_time = start_time
        self.formation_start_time = start_time
        self.is_playing = True
        self.is_in_transition = False
        
        # Charger la première formation
        self._load_current_formation()
        
        print(f"[CHOREOGRAPHER] Démarrage de l'acte: {self.acts[act_name].name}")
        return True
    
    def _load_current_formation(self):
        """Charge la formation courante depuis la bibliothèque"""
        
        if not self.formation_library:
            return
            
        act = self.acts[self.current_act]
        if self.current_formation_idx >= len(act.formations):
            return
            
        formation = act.formations[self.current_formation_idx]
        
        # Obtenir les positions/couleurs de la formation
        pos, cols = self.formation_library.generate_formation(
            formation.phase_name, 
            self.num_drones,
            t=0.0
        )
        
        self.current_positions = pos.copy()
        self.current_colors = cols.copy()
        
        print(f"[CHOREOGRAPHER] Formation chargée: {formation.description}")
    
    def _load_next_formation(self):
        """Pré-charge la formation suivante"""
        
        if not self.formation_library:
            return
            
        act = self.acts[self.current_act]
        next_idx = self.current_formation_idx + 1
        
        if next_idx >= len(act.formations):
            # Fin de l'acte - charger la première formation de l'acte suivant?
            return
            
        formation = act.formations[next_idx]
        
        pos, cols = self.formation_library.generate_formation(
            formation.phase_name,
            self.num_drones,
            t=0.0
        )
        
        self.next_positions = pos.copy()
        self.next_colors = cols.copy()
    
    def update(self, dt: float, current_time: float) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Met à jour la chorégraphie.
        
        Returns:
            Tuple[positions, colors, light_multiplier]
        """
        
        self.show_time = current_time
        self.living_animator.update(dt)
        
        # Si on est en transition
        if self.is_in_transition:
            still_active = self.transition_system.update(dt)
            
            if not still_active:
                # Transition terminée
                self.is_in_transition = False
                self.current_formation_idx += 1
                self.formation_start_time = current_time
                self._load_current_formation()
                
            # Retourner les données de transition
            positions = self.transition_system.get_positions()
            colors = self.transition_system.get_colors()
            light_mult = self.transition_system.get_light_multiplier()
            
            return positions, colors, light_mult
        
        # Mode formation normale
        act = self.acts.get(self.current_act)
        if not act or self.current_formation_idx >= len(act.formations):
            return self.current_positions, self.current_colors, 1.0
            
        formation = act.formations[self.current_formation_idx]
        
        # Temps écoulé dans cette formation
        formation_time = current_time - self.formation_start_time
        
        # Mettre à jour les positions avec animation
        if self.formation_library:
            pos, cols = self.formation_library.generate_formation(
                formation.phase_name,
                self.num_drones,
                t=formation_time
            )
            self.current_positions = pos
            self.current_colors = cols
        
        # Appliquer les micro-mouvements (living formation)
        animated_pos, animated_cols = self.living_animator.animate(
            self.current_positions, 
            self.current_colors,
            formation.phase_name
        )
        
        # Vérifier si on doit passer à la formation suivante
        if formation_time >= formation.duration + formation.hold_after:
            if formation.transition_to_next and self.current_formation_idx < len(act.formations) - 1:
                # Démarrer une transition
                self._start_transition_to_next()
            else:
                # Passer directement à la suivante (pas de blackout)
                self.current_formation_idx += 1
                self.formation_start_time = current_time
                self._load_current_formation()
        
        return animated_pos, animated_cols, 1.0
    
    def _start_transition_to_next(self):
        """Démarre une transition professionnelle vers la formation suivante"""
        
        # Charger la prochaine formation
        self._load_next_formation()
        
        # Démarrer la transition
        self.transition_system.start_transition(
            self.current_positions,
            self.current_colors,
            self.next_positions,
            self.next_colors
        )
        
        self.is_in_transition = True
        
        act = self.acts[self.current_act]
        current_form = act.formations[self.current_formation_idx]
        next_form = act.formations[self.current_formation_idx + 1] if self.current_formation_idx + 1 < len(act.formations) else None
        
        print(f"[CHOREOGRAPHER] Transition: {current_form.description} → {next_form.description if next_form else 'FIN'}")
    
    def force_transition(self, to_phase: str):
        """Force une transition vers une phase spécifique"""
        
        if not self.formation_library:
            return
            
        # Obtenir la formation cible
        pos, cols = self.formation_library.generate_formation(
            to_phase,
            self.num_drones,
            t=0.0
        )
        
        self.next_positions = pos.copy()
        self.next_colors = cols.copy()
        
        # Démarrer la transition
        self.transition_system.start_transition(
            self.current_positions,
            self.current_colors,
            self.next_positions,
            self.next_colors
        )
        
        self.is_in_transition = True
        print(f"[CHOREOGRAPHER] Transition forcée vers: {to_phase}")
    
    def get_transition_state(self) -> Optional[TransitionState]:
        """Retourne l'état de transition actuel"""
        if self.is_in_transition:
            return self.transition_system.get_state()
        return None
    
    def is_in_blackout(self) -> bool:
        """Retourne True si on est en blackout"""
        return self.is_in_transition and self.transition_system.is_dark()
    
    def get_current_info(self) -> Dict:
        """Retourne les informations sur l'état actuel"""
        
        act = self.acts.get(self.current_act)
        formation = None
        if act and self.current_formation_idx < len(act.formations):
            formation = act.formations[self.current_formation_idx]
        
        return {
            'act_name': act.name if act else "Unknown",
            'formation_name': formation.description if formation else "Unknown",
            'formation_index': self.current_formation_idx,
            'is_transitioning': self.is_in_transition,
            'transition_state': self.transition_system.get_state().name if self.is_in_transition else None,
            'show_time': self.show_time
        }


class TransitionPresets:
    """Presets de transitions pour différents effets"""
    
    @staticmethod
    def quick_fade():
        """Transition rapide (pour même acte)"""
        return {
            'fade_out': 0.3,
            'blackout': 1.0,
            'transit': 3.0,
            'fade_in': 0.5
        }
    
    @staticmethod
    def dramatic():
        """Transition dramatique (entre actes)"""
        return {
            'fade_out': 0.8,
            'blackout': 3.0,
            'transit': 5.0,
            'fade_in': 1.0
        }
    
    @staticmethod
    def instant():
        """Transition quasi-instantanée"""
        return {
            'fade_out': 0.2,
            'blackout': 0.5,
            'transit': 2.0,
            'fade_in': 0.3
        }
    
    @staticmethod
    def ethereal():
        """Transition éthérée/magique"""
        return {
            'fade_out': 1.0,
            'blackout': 2.0,
            'transit': 6.0,
            'fade_in': 1.5
        }


# ═══════════════════════════════════════════════════════════════════════════════
#                                EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'ShowChoreographer',
    'FormationType',
    'FormationSequenceItem',
    'ActSequence',
    'TransitionPresets'
]
