# 📋 CAHIER DES CHARGES COMPLET
## Simulateur de Spectacle de Drones 3D - ANEM 2025

**Version :** 1.0  
**Date :** 29 Janvier 2026  
**Projet :** DRONES-3D-ANEM-2025  
**Client :** Cérémonie d'Ouverture ANEM 2025 (Association Nigérienne des Étudiants au Maroc)

---

## 📑 TABLE DES MATIÈRES

1. [Présentation du Projet](#1-présentation-du-projet)
2. [Objectifs et Contexte](#2-objectifs-et-contexte)
3. [Spécifications Techniques](#3-spécifications-techniques)
4. [Architecture Logicielle](#4-architecture-logicielle)
5. [Fonctionnalités Détaillées](#5-fonctionnalités-détaillées)
6. [Chorégraphie et Formations](#6-chorégraphie-et-formations)
7. [Interface Utilisateur](#7-interface-utilisateur)
8. [Systèmes Audio et Visuels](#8-systèmes-audio-et-visuels)
9. [Performance et Optimisation](#9-performance-et-optimisation)
10. [Dépendances et Installation](#10-dépendances-et-installation)
11. [Livrables](#11-livrables)
12. [Évolutions Futures](#12-évolutions-futures)

---

## 1. PRÉSENTATION DU PROJET

### 1.1 Description Générale

Le projet **DRONES-3D-ANEM-2025** est un simulateur 3D temps réel de spectacle de drones lumineux conçu pour visualiser et prévisualiser la cérémonie d'ouverture de l'événement ANEM 2025. Cette application permet de créer, tester et perfectionner des chorégraphies de drones en 3D avant leur déploiement réel.

### 1.2 Nom du Projet
- **Titre officiel :** ANEM 2025 Drone Show Simulator
- **Nom technique :** DRONES-3D-ANEM-2025

### 1.3 Domaine d'Application
- Simulation événementielle
- Spectacle lumineux aérien
- Art numérique et performance
- Cérémonie d'ouverture culturelle

---

## 2. OBJECTIFS ET CONTEXTE

### 2.1 Objectifs Principaux

| # | Objectif | Description |
|---|----------|-------------|
| 1 | **Visualisation 3D** | Rendu temps réel d'un essaim de 1000 drones lumineux |
| 2 | **Chorégraphie** | Création de formations complexes (textes, symboles, formes) |
| 3 | **Narration** | Séquençage automatique d'actes pour raconter une histoire |
| 4 | **Audio-Réactivité** | Synchronisation des animations avec la musique |
| 5 | **Prévisualisation** | Validation des séquences avant le spectacle réel |

### 2.2 Contexte Culturel

Le spectacle célèbre :
- **L'identité nigérienne** : Drapeau, carte du Niger, croix d'Agadez
- **Le patrimoine Touareg** : Motifs géométriques, symboles traditionnels
- **La culture africaine** : Arbre de vie, aigle, motifs sahéliens
- **L'événement ANEM** : 22ème édition, JCN 2026, FES-MEKNES

### 2.3 Public Cible
- Organisateurs de l'événement ANEM
- Équipes techniques de production
- Artistes et chorégraphes numériques
- Spectateurs (prévisualisation)

---

## 3. SPÉCIFICATIONS TECHNIQUES

### 3.1 Configuration Matérielle Minimale

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| Processeur | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 |
| RAM | 8 Go | 16 Go |
| GPU | OpenGL 3.3+ compatible | NVIDIA GTX 1060+ / AMD RX 580+ |
| Stockage | 500 Mo | 1 Go |
| OS | Windows 10/11, Linux, macOS | Windows 11 |

### 3.2 Configuration de Simulation

```yaml
simulation:
  max_drones: 1000          # Nombre maximum de drones
  initial_drones: 1000      # Drones actifs au démarrage
  fps_target: 60            # Images par seconde cible
  time_scale: 1.0           # Vitesse de simulation

espace_3d:
  x_range: [-200, 200]      # 400m de largeur
  y_range: [0, 150]         # 150m de hauteur
  z_range: [-200, 200]      # 400m de profondeur

physique:
  max_speed_m_s: 60.0       # Vitesse max (60 m/s = 216 km/h)
  acceleration_m_s2: 12.0   # Accélération (12 m/s²)
  collision_radius_m: 1.5   # Rayon anti-collision
  min_separation_m: 3.0     # Distance minimale inter-drones
```

### 3.3 Configuration Visuelle

```yaml
visuals:
  background_color: [0.0, 0.0, 0.02, 1.0]  # Noir profond/Bleu nuit
  drone:
    size: 2.5                               # Taille visuelle
    default_color: [1.0, 1.0, 1.0]          # Blanc par défaut
  lighting:
    ambient_intensity: 0.1
    diffuse_intensity: 0.8
    specular_intensity: 0.5
  bloom:
    enabled: true
    threshold: 0.9
    intensity: 1.5
```

---

## 4. ARCHITECTURE LOGICIELLE

### 4.1 Structure du Projet

```
DRONES-3D-ANEM-2025/
│
├── config/                     # Fichiers de configuration
│   ├── simulation.yaml         # Paramètres de simulation
│   ├── visuals.yaml            # Paramètres visuels
│   └── performance.yaml        # Paramètres de performance
│
├── data/                       # Données et ressources
│   └── assets/                 # Images, modèles, textures
│
├── src/                        # Code source
│   ├── main.py                 # Point d'entrée principal
│   ├── simulation_core.py      # Moteur de simulation OpenGL
│   ├── drone_manager.py        # Gestionnaire d'essaim de drones
│   ├── formation_library.py    # Bibliothèque de formations (3300+ lignes)
│   ├── camera_system.py        # Système de caméra cinématique
│   ├── physics_engine.py       # Moteur physique (mouvement, collision)
│   ├── lighting_system.py      # Système d'éclairage OpenGL
│   ├── audio_system.py         # Analyse audio FFT + lecture
│   ├── shader_system.py        # Pipeline post-processing (bloom)
│   ├── ui_controller.py        # Interface utilisateur PyQt6
│   └── africa_map_generator.py # Générateur de carte d'Afrique
│
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation rapide
└── CAHIER_DES_CHARGES.md       # Ce document
```

### 4.2 Diagramme des Modules

```
┌─────────────────────────────────────────────────────────────────┐
│                         MAIN.PY                                 │
│                    (Point d'entrée)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UI_CONTROLLER                              │
│              (Interface PyQt6 - MainWindow)                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ Contrôles Play   │  │ Boutons Phases   │  │ Audio Controls│  │
│  │ Pause / Reset    │  │ (25+ formations) │  │ Load/Play/Stop│  │
│  └──────────────────┘  └──────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SIMULATION_CORE                             │
│               (Moteur OpenGL - QOpenGLWidget)                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  - Boucle de rendu 60 FPS                               │    │
│  │  - Machine d'états (Transit → Blackout → Fade In → Hold)│    │
│  │  - Gestion des transitions morphing                     │    │
│  │  - Contrôle audio-réactivité                            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│DRONE_MANAGER │ │CAMERA_SYSTEM │ │FORMATION_LIB │ │AUDIO_SYSTEM  │
│              │ │              │ │              │ │              │
│- 1000 drones │ │- 15+ presets │ │- 25+ phases  │ │- FFT analysis│
│- Positions   │ │- Transitions │ │- Texte 3D    │ │- Lecture MP3 │
│- Couleurs    │ │- Smart AI    │ │- Formes      │ │- BPM detect  │
│- Targets     │ │- Orbite      │ │- Animations  │ │- Réactivité  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
       │                                                   
       ▼                                                   
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│PHYSICS_ENGINE│ │LIGHTING_SYS  │ │SHADER_SYSTEM │
│              │ │              │ │              │
│- Bio-Swarm   │ │- OpenGL Light│ │- Bloom/Glow  │
│- Turbulence  │ │- Ambient     │ │- Post-process│
│- Collision   │ │- Diffuse     │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 4.3 Technologies Utilisées

| Catégorie | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Langage** | Python | 3.13+ | Langage principal |
| **GUI** | PyQt6 | 6.6+ | Interface utilisateur |
| **Rendu 3D** | PyOpenGL | 3.1.7+ | Graphiques OpenGL |
| **Calcul** | NumPy | 1.26+ | Calculs vectoriels |
| **Config** | PyYAML | 6.0+ | Fichiers YAML |
| **Images** | Pillow | 10.0+ | Traitement images |
| **Audio** | librosa | 0.10+ | Analyse FFT |
| **Audio** | pygame | 2.1+ | Lecture audio |
| **Audio** | soundfile | 0.12+ | I/O fichiers audio |

---

## 5. FONCTIONNALITÉS DÉTAILLÉES

### 5.1 Moteur de Simulation (SimulationCore)

#### 5.1.1 Boucle de Rendu
- **Fréquence :** 60 FPS (16ms par frame)
- **Double buffering** pour éviter le tearing
- **Depth testing** pour l'ordre de profondeur
- **Blending** pour les effets de transparence/glow

#### 5.1.2 Machine d'États des Phases

```
┌─────────────────────────────────────────────────────────────┐
│                    MACHINE D'ÉTATS                          │
│                                                             │
│  ┌──────────┐   4s    ┌──────────┐   0.5s   ┌──────────┐   │
│  │  TRANSIT │ ──────► │ ARRIVED  │ ───────► │ BLACKOUT │   │
│  │(Mouvement)│        │ (Pause)  │          │(Silence) │   │
│  └──────────┘         └──────────┘          └──────────┘   │
│       │                                          │          │
│       │                                     0.5s │          │
│       │                                          ▼          │
│       │               ┌──────────┐         ┌──────────┐    │
│       │               │   HOLD   │ ◄─────  │ FADE IN  │    │
│       │               │(Contempl)│   1.5s  │(Révélat.)│    │
│       │               └──────────┘         └──────────┘    │
│       │                    │                    │          │
│       │               1.5s │                    │ 1s       │
│       │                    ▼                    │          │
│       │               ┌──────────┐              │          │
│       └───────────────│LIGHT SHOW│◄─────────────┘          │
│                       │(Sparkles)│                         │
│                       └──────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

| État | Durée | Description |
|------|-------|-------------|
| **TRANSIT** | 4.0s | Mouvement des drones vers la formation cible |
| **ARRIVED** | 0.5s | Pause dans l'obscurité (stealth mode) |
| **BLACKOUT** | 0.5s | Silence visuel total |
| **FADE IN** | 1.0s | Révélation progressive (allumage) |
| **LIGHT SHOW** | 1.5s | Jeu de lumière (scintillement) |
| **HOLD** | ∞ | Contemplation de la formation finale |

#### 5.1.3 Transitions Morphing

Interpolation fluide entre formations :
```python
# Interpolation cubique ease-in-out
t_ease = t * t * (3.0 - 2.0 * t)
morphed_pos = (1 - t_ease) * start_pos + t_ease * target_pos
```

- **Durée :** 2.0 secondes
- **Phases concernées :** Touareg, Chameau Dubaï, Spirale, Auto-séquence

### 5.2 Gestionnaire de Drones (DroneManager)

#### 5.2.1 Structure de Données
```python
# Structure of Arrays (SoA) pour performance
positions = np.zeros((1000, 3), dtype=np.float32)  # X, Y, Z
colors = np.ones((1000, 3), dtype=np.float32)       # R, G, B
targets = np.zeros((1000, 3), dtype=np.float32)     # Cibles
```

#### 5.2.2 Méthodes Principales

| Méthode | Description |
|---------|-------------|
| `update(dt)` | Mise à jour physique de tous les drones |
| `set_formation(targets, colors)` | Définir une nouvelle formation |
| `get_render_data()` | Récupérer positions/couleurs pour le rendu |

### 5.3 Moteur Physique (PhysicsEngine)

#### 5.3.1 Modèle de Mouvement "Bio-Swarm"

Le mouvement des drones simule un comportement organique vivant :

1. **Force vers la cible (Spring/Elastic)**
   ```python
   to_target = target_positions - current_positions
   desired_speed = min(distance * 2.0, max_speed)
   ```

2. **Turbulence Organique (Curl Noise)**
   ```python
   noise_x = sin(y * freq) * cos(z * freq)
   noise_y = sin(x * freq) * cos(z * freq)
   noise_z = cos(x * freq) * sin(y * freq)
   turbulence = noise * 2.0  # Intensité
   ```

3. **Micro-Jitter (Anti-Robot)**
   ```python
   jitter = sin(index * 0.1 + time) * 0.5
   ```

4. **Intégration Euler**
   ```python
   new_position = position + velocity * dt
   ```

### 5.4 Système de Caméra (CameraSystem)

#### 5.4.1 Presets Cinématographiques

| Preset | Distance | Pitch | Intent | Usage |
|--------|----------|-------|--------|-------|
| **ground** | 200m | -10° | human | Vue spectateur |
| **desert** | 300m | +10° | plongée | Vue aérienne dunes |
| **intimate** | 170m | -11° | observer | Plans rapprochés |
| **monument** | 200m | -14° | monumental | Formations grandes |
| **text** | 240m | -13° | monumental | Typographie |
| **flag** | 350m | -8° | vision | Drapeau géant |
| **wide** | 360m | -7° | vision | Vue d'ensemble |
| **africa_map** | 150m | -89° | vision | Vue directe dessus |

#### 5.4.2 Caméra IA "Smart Cinematic"

Pour les phases dynamiques (Désert, Aigle, Miroir Céleste) :

```
Cycle de 20 secondes :
├── 0-5s   : GLOBAL ORBIT (Vue majestueuse)
├── 5-10s  : THE SKIM (Poursuite des pics)
├── 10-15s : CLOSE-UP (Plan serré centre)
└── 15-20s : DOLLY BACK (Recul dramatique)
```

---

## 6. CHORÉGRAPHIE ET FORMATIONS

### 6.1 Palette de Couleurs Officielle

| Nom | Code RGB | Hex | Usage |
|-----|----------|-----|-------|
| **Orange Niger** | (1.0, 0.5, 0.0) | #FF8000 | Sable/Désert |
| **Blanc Pur** | (1.0, 1.0, 1.0) | #FFFFFF | Lumière/Étoiles |
| **Vert Niger** | (0.0, 0.6, 0.2) | #009933 | Drapeau |
| **Soleil Or** | (1.0, 0.84, 0.0) | #FFD700 | Soleil/Prestige |
| **Bleu Nuit** | (0.0, 0.12, 0.25) | #001F3F | Ciel profond |
| **Turquoise** | (0.22, 0.8, 0.8) | #39CCCC | Eau/Spiritualité |
| **Star White** | (0.95, 0.95, 1.0) | #F2F2FF | Étoiles froides |
| **Star Blue** | (0.7, 0.85, 1.0) | #B3D9FF | Ciel scintillant |

### 6.2 Catalogue des Formations

#### 6.2.1 ACTES D'OUVERTURE (Narratif)

| # | Acte | Code | Description | Durée |
|---|------|------|-------------|-------|
| 0 | Naissance Cosmique | `act0_pre_opening` | Du néant aux étoiles → ANEM → Explosion arc-en-ciel | **20s** |
| 1 | Naissance | `act1_desert` | Dunes respirantes du Sahara | 15s |
| 2 | Pluie Sacrée | `act2_sacred_rain` | Fleuve Niger ondulant | 12s |
| 3 | Typographie | `act3_typography` | "NIGER" géant blanc | 10s |
| 4 | Science & Beauté | `act4_science` | Double hélice ADN animée | 15s |
| 5 | L'Âme Africaine | `act5_african_soul` | Carte d'Afrique | 12s |
| 6 | Identité Sacrée | `act6_identity` | Croix d'Agadez argentée | 10s |
| 7 | Drapeau Géant | `act7_flag` | Drapeau nigérien ondulant | 15s |
| 8 | Finale Unity | `act8_finale` | Constellation finale | 20s |
| 9 | Aigle | `act9_eagle` | Aigle majestueux | 12s |

---

### 6.3 ACTE 0 : NAISSANCE COSMIQUE - Documentation Détaillée

> *"Dans le silence du désert nigérien, avant l'aube... Du néant cosmique naît la lumière, qui s'organise en une constellation pour finalement exploser en une promesse de beauté."*

#### 6.3.1 Concept Artistique

L'Acte 0 est **l'ouverture magique** du spectacle ANEM 2025. Il représente la **genèse** : du néant cosmique naît la lumière, qui s'organise en une constellation pour finalement exploser en une promesse de beauté. C'est **la métaphore parfaite** pour une cérémonie d'ouverture : du vide émerge l'événement.

```
PHASE 1 (0-3s)        PHASE 2 (3-8s)         PHASE 3 (8-12s)       PHASE 4 (12-20s)
                                              
    ✧                    A N E M                  ●●●●●              🌈🌈🌈🌈🌈🌈🌈
  ✧   ✧                                          ●●●●●●             🌈🌈🌈🌈🌈🌈🌈
    ✧                  Blanc Orange              ●●●●●●●            🌈🌈🌈🌈🌈🌈🌈
      ✧                      Vert Blanc           ●●●●●●
                                                   ●●●●●
  NUIT ÉTOILÉE         CONSTELLATION ANEM       SPHÈRE DORÉE        ARC-EN-CIEL
```

#### 6.3.2 Timeline Détaillée (20 secondes)

| Phase | Temps | Description | Événement Clé | Couleur |
|-------|-------|-------------|---------------|---------|
| **NUIT PRIMORDIALE** | 0.0-3.0s | Étoiles apparaissent progressivement | 0→100 étoiles | Blanc scintillant |
| **CONSTELLATION ANEM** | 3.0-8.0s | Formation texte "ANEM" | 4 lettres séquentielles | Blanc/Orange/Vert |
| **CŒUR COSMIQUE** | 8.0-12.0s | Sphère dorée pulsante | 3 battements de cœur | Or soleil (#FFD700) |
| **ÉCLOSION FINALE** | 12.0-20.0s | Explosion → Arc-en-ciel → Désert | Big Bang visuel | 7 couleurs arc-en-ciel |

#### 6.3.3 PHASE 1 : La Nuit Primordiale (0-3s)

**Concept** : Le ciel passe du noir total à un champ d'étoiles scintillantes.

| Temps | Étoiles visibles | Événement |
|-------|------------------|-----------|
| 0.0s | 0 | Ciel noir total |
| 0.5s | 1 | Alpha Centauri (étoile du berger) |
| 1.0s | 3 | Triangle d'été |
| 1.5s | 8 | Constellation naissante |
| 2.0s | 20 | Essaim apparaît |
| 2.5s | 50 | Ciel qui s'étoile |
| 3.0s | 100 | Nuit étoilée complète |

**Spécifications techniques** :
- Distribution : Sphère de rayon 200m, distribution uniforme
- Effet : Scintillement sinusoïdal (amplitude 30%, fréquence 5 Hz)
- Première étoile : Intensité 150% (plus brillante)

#### 6.3.4 PHASE 2 : Constellation ANEM (3-8s)

**Concept** : Les étoiles convergent pour former le texte "ANEM" avec effet "stroke drawing".

| Lettre | Temps | Drones | Couleur | Code Hex |
|--------|-------|--------|---------|----------|
| **A** | t=3.5s | 200 | Blanc Pur | #FFFFFF |
| **N** | t=4.5s | 200 | Orange Niger | #FF8000 |
| **E** | t=5.5s | 200 | Vert Niger | #009933 |
| **M** | t=6.5s | 200 | Blanc Pur | #FFFFFF |
| *Fond* | - | 200 | Blanc scintillant | - |

**Dimensions du texte** :
- Largeur totale : 80 mètres
- Hauteur des lettres : 40 mètres
- Espacement : 20 mètres entre lettres
- Position : Centre scène, altitude 80m

**Animation** :
- Durée formation par lettre : 0.8s
- Interpolation : Ease-out cubic
- Pulsation après formation : 1 Hz (battement de cœur)

#### 6.3.5 PHASE 3 : Cœur Cosmique (8-12s)

**Concept** : Tous les drones convergent en spirale vers le centre pour former une sphère dorée pulsante.

**Convergence spirale (8-9s)** :
- 4 tours complets de spirale
- Direction : extérieur → centre
- Couleur : Transition progressive vers Or

**Sphère pulsante (9-12s)** :

| Temps | Pulsation | Intensité | Rayon |
|-------|-----------|-----------|-------|
| t=9.5s | 1ère | Forte | 30m → 35m |
| t=10.5s | 2ème | Plus forte | 30m → 38m |
| t=11.5s | 3ème (pré-explosion) | Très forte | 30m → 42m |

**Spécifications** :
- Rayon de base : 30 mètres
- Centre : (0, 100, 0)
- Couleur : Or Soleil #FFD700
- Distribution : Uniforme sur la surface de la sphère

#### 6.3.6 PHASE 4 : Éclosion Finale (12-20s)

**Concept** : Explosion spectaculaire suivie de la formation d'un arc-en-ciel géant.

**Sous-phases** :

| Temps | Événement | Description |
|-------|-----------|-------------|
| 12.0-12.5s | EXPLOSION | Tous les drones projetés à 50 m/s, flash blanc |
| 12.5-14.0s | FORMATION | Arc-en-ciel se forme progressivement |
| 14.0-18.0s | STABLE | Arc-en-ciel visible avec légère ondulation |
| 18.0-20.0s | TRANSITION | Fondu vers les teintes du désert |

**Spécifications de l'arc-en-ciel** :
- Largeur : 150 mètres
- Hauteur : 60 mètres
- Rayon de courbure : 100 mètres
- Épaisseur des bandes : ~8 mètres

**Les 7 couleurs** :
| # | Couleur | RGB | Drones |
|---|---------|-----|--------|
| 1 | Violet | (0.58, 0, 0.83) | 143 |
| 2 | Indigo | (0.29, 0, 0.51) | 143 |
| 3 | Bleu | (0, 0, 1) | 143 |
| 4 | Vert | (0, 1, 0) | 143 |
| 5 | Jaune | (1, 1, 0) | 143 |
| 6 | Orange | (1, 0.65, 0) | 143 |
| 7 | Rouge | (1, 0, 0) | 142 |

**Transition vers Acte 1** :
- L'arc-en-ciel fond progressivement
- Les couleurs changent vers : Sable #F5A361, Ocre #DE8740, Terre cuite #D1691F
- Les drones s'aplatissent vers une formation de dunes

#### 6.3.7 Séquence Caméra Cinématique (20s)

```
Timeline caméra :
├── 0.0-3.0s  : Vue subjective sol → ciel (tilt up, 250→300m)
├── 3.0-8.0s  : Vue aérienne texte ANEM (180→300m, panoramique)
├── 8.0-12.0s : Orbite sphère dorée (120→80m, rotation 60°)
│   └── 11.0-12.0s : Accélération dramatique (lerp 1.2)
├── 12.0-12.5s: Recul explosion rapide (80→280m, lerp 2.5)
├── 12.5-14.0s: Stabilisation arc-en-ciel (280→350m)
├── 14.0-18.0s: Rotation admiration (350m, orbite lente 20°)
└── 18.0-20.0s: Descente vers désert (target_y 70→30m)
```

#### 6.3.8 Synchronisation Audio-Visuelle

| Temps | Visuel | Audio | Émotion |
|-------|--------|-------|---------|
| 0.0s | Ciel noir | Silence total | Attente |
| 0.5s | 1ère étoile | "Ping" cristallin | Émerveillement |
| 3.5s | A complet | Accord Do-Mi-Sol | Satisfaction |
| 4.5s | N complet | Note Mi | Continuité |
| 5.5s | E complet | Note Sol | Élévation |
| 6.5s | M complet | Accord complet | Accomplissement |
| 8.0s | Convergence | Montée tension | Suspense |
| 11.5s | Pulsation max | Silence... | Suspense extrême |
| **12.0s** | **EXPLOSION** | **BOUM + Cymbales** | **Libération** |
| 12.5s | Arc-en-ciel | Harpe glissando | Éblouissement |
| 18.0s | Transition | Fond désert | Calme |

#### 6.3.9 Symbolisme et Message

| Niveau | Interprétation |
|--------|----------------|
| **Littéral** | L'événement ANEM 2025 commence par une ouverture lumineuse |
| **Métaphorique** | De l'obscurité naît la lumière, du chaos naît l'ordre |
| **Culturel** | Comme les étoiles guidaient les nomades du Sahara, ANEM guide les étudiants |
| **Émotionnel** | Émerveillement → Reconnaissance → Anticipation → Exaltation → Sérénité |

#### 6.3.10 Fichier de Configuration

Voir : `config/act0_naissance_cosmique.yaml`

#### 6.3.11 Pourquoi Cette Ouverture Fonctionne

- ✅ **Commence SIMPLEMENT** (1 drone) → pas de bug possible
- ✅ **Montre la MÉTHODE** (points → formes) → éducatif
- ✅ **Utilise le TEXTE** (ANEM) → reconnaissance immédiate
- ✅ **A un CLIMAX** (explosion) → spectaculaire
- ✅ **Offre une TRANSITION** (arc-en-ciel → désert) → fluide
- ✅ **Contrôlable PHASE par PHASE** → débogage facile
- ✅ **Synchronisable avec AUDIO** → impact maximal
- ✅ **Adapté à 1000 DRONES** → chaque phase optimisée
- ✅ **RACONTE une HISTOIRE** → narrative cohérente
- ✅ **FIDÈLE à l'IDENTITÉ ANEM** → couleurs, symboles

---

#### 6.3.12 PHASES ORIGINALES (Textuelles)

| # | Phase | Code | Formation | Effet |
|---|-------|------|-----------|-------|
| 1 | Pluie | `phase1_pluie` | Cœur lumineux rouge | Pulsation |
| 2 | ANEM | `phase2_anem` | Texte "ANEM" | Rotation anneau |
| 3 | JCN | `phase3_jcn` | Texte "JCN2026" doré | Vague |
| 4 | FES | `phase4_fes` | Texte "FES-MEKNES" vert | Split & Move |
| 5 | Niger | `phase5_niger` | Texte "NIGER" orange | Heartbeat |
| 6 | Drapeau | `phase6_drapeau` | Drapeau 3 bandes | Ondulation |
| 7 | Carte | `phase7_carte` | Carte précise du Niger | Statique |
| 8 | Finale | `phase8_finale` | Anneau + Spirale | Rotation |

#### 6.2.3 PHASES SPÉCIALES (Heritage)

| # | Phase | Code | Description |
|---|-------|------|-------------|
| 9 | Grande Mosquée | `phase9_agadez` | Mosquée d'Agadez |
| 10 | Touareg | `phase10_touareg` | Motifs géométriques Touareg |
| 11 | Croix Agadez | `phase11_croix_agadez` | Croix traditionnelle |
| 12 | Chameau | `dubai_camel` | Chameau style Dubaï |
| 13 | Arbre de Vie | `act5_tree_of_life` | Baobab africain |
| 14 | Spirale | `phase_touareg_spiral` | Spirale méditative |
| 15 | 22ème Édition | `phase_22eme_edition` | Texte animé "22" |
| 16 | Miroir Céleste | `miroir_celeste` | Finale cosmique (45s) |

### 6.3 Détail des Formations Clés

#### 6.3.1 Formation Texte 3D

Algorithme de génération :
```
1. Police bitmap 5x7 pixels par caractère
2. Conversion caractère → matrice binaire
3. Remplissage uniforme (20x plus de points que drones)
4. Échantillonnage pour N drones
5. Ajout profondeur Z (10m) pour effet sculptural
6. Application effets dynamiques (rotation, wave, split)
```

Caractères supportés : A-Z, 0-9, "-"

#### 6.3.2 Formation Drapeau du Niger

```
Structure 3 bandes horizontales :
┌────────────────────────────────┐
│          ORANGE               │  33% hauteur
├────────────────────────────────┤
│    BLANC    ●    BLANC        │  33% + soleil centre
├────────────────────────────────┤
│           VERT                │  33% hauteur
└────────────────────────────────┘

Dimensions : 160m x 100m
Animation : Ondulation sinusoïdale sur Z
           wave = sin(x * 0.05 + t * 3.0) * amplitude
```

#### 6.3.3 Miroir Céleste (Finale Cosmique)

Séquence de 45 secondes :

| Temps | Phase | Description |
|-------|-------|-------------|
| 0-10s | Spirale Galaxie | Rotation Fibonacci |
| 10-14s | Implosion | Convergence vers singularité |
| 14-20s | Œil Cosmique | Sphère avec pupille/iris |
| 20s+ | Silence | Montée et fade out |

### 6.4 Effets Visuels sur Formations

| Effet | Description | Phases |
|-------|-------------|--------|
| **rotate_ring** | Rotation lente autour de Y | ANEM |
| **wave** | Vague sinusoïdale traversante | JCN2026 |
| **split_move** | Séparation et rapprochement | FES-MEKNES |
| **heartbeat** | Pulsation cardiaque explosive | NIGER |
| **sparkle** | Scintillement étoilé subtil | Toutes |
| **breathing** | Mouvement respiratoire | Désert |

---

## 7. INTERFACE UTILISATEUR

### 7.1 Fenêtre Principale

```
┌─────────────────────────────────────────────────────────────────┐
│  ANEM 2025 Drone Show Simulator                    [_][□][X]   │
├─────────────────────────────────────────────────────────────────┤
│                                                    │ Contrôles │
│                                                    │───────────│
│                                                    │ [Play]    │
│                                                    │ [Reset]   │
│                                                    │───────────│
│              ZONE DE RENDU 3D                      │ AUTO-SEQ  │
│                  (OpenGL)                          │───────────│
│                                                    │ [▶ Start] │
│            ████████████████████                    │ [⏸ Pause] │
│            █  1000 DRONES    █                     │ [◀][▶]    │
│            ████████████████████                    │───────────│
│                                                    │ AUDIO     │
│                                                    │───────────│
│                                                    │ [🎵 Load] │
│                                                    │ [▶][⏸][■]│
│                                                    │───────────│
│                                                    │ PHASES    │
│                                                    │───────────│
│                                                    │ [Acte 0]  │
│                                                    │ [Acte 1]  │
│                                                    │ [...]     │
│                                                    │ (scroll)  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Panneau de Contrôle

#### 7.2.1 Contrôles de Lecture
- **Play/Pause** : Démarrer/Arrêter la simulation
- **Reset** : Réinitialiser à l'état initial

#### 7.2.2 Auto-Séquençage
- **Start Sequence** : Lancer la séquence automatique
- **Pause/Resume** : Mettre en pause la séquence
- **◀ Prev / Next ▶** : Navigation manuelle
- **⏮ Rewind** : Retour au début

#### 7.2.3 Contrôles Audio
- **🎵 Load Audio** : Charger un fichier audio (MP3, WAV)
- **▶ Play** : Lire l'audio
- **⏸ Pause** : Mettre en pause
- **■ Stop** : Arrêter

#### 7.2.4 Effets Visuels
- **✨ Bloom/Glow** : Activer/désactiver l'effet de halo

#### 7.2.5 Sélecteur de Phases
Liste scrollable de 25+ formations organisées en catégories :
- Ouverture (Actes)
- Phases Originales
- Héritage & Spécial

### 7.3 Contrôles Souris

| Action | Effet |
|--------|-------|
| **Clic gauche + Drag** | Rotation orbitale de la caméra |
| *(Futur)* Molette | Zoom avant/arrière |
| *(Futur)* Clic droit | Pan de la caméra |

---

## 8. SYSTÈMES AUDIO ET VISUELS

### 8.1 Système Audio (AudioSystem)

#### 8.1.1 Capacités
- Chargement de fichiers audio (MP3, WAV, FLAC, OGG)
- Analyse FFT temps réel
- Détection de l'énergie par bande de fréquences
- Lecture synchronisée avec pygame

#### 8.1.2 Bandes de Fréquences

| Bande | Fréquences | Variable | Impact |
|-------|------------|----------|--------|
| **Bass** | 0-250 Hz | `bass_energy` | Amplitude des mouvements |
| **Mid** | 250-2000 Hz | `mid_energy` | Ondulations/vagues |
| **Treble** | 2000+ Hz | `treble_energy` | Scintillements |

#### 8.1.3 Métriques Globales
- `overall_energy` : Énergie totale normalisée [0, 1]
- `beat_strength` : Force du beat
- `kick_detected` : Détection des kicks (booléen)

### 8.2 Système d'Éclairage (LightingSystem)

Configuration OpenGL :
- **Lumière 0** : Directionnelle (position haut-droite)
- **Ambient** : 10% intensité (éclairage de base)
- **Diffuse** : 80% intensité (lumière principale)
- **Specular** : 50% intensité (reflets)
- **Material Tracking** : Couleur suit glColor

### 8.3 Post-Processing (ShaderSystem)

#### 8.3.1 Effet Bloom/Glow
Simulation de halo lumineux autour des drones brillants :

```
1. Rendu standard de la scène
2. Extraction pixels > seuil de luminosité
3. Flou gaussien multi-pass
4. Composition additive avec scène originale
```

Paramètres :
- `bloom_enabled` : true/false
- `bloom_threshold` : 0.7 (seuil de luminosité)
- `bloom_intensity` : 1.5 (force du halo)

---

## 9. PERFORMANCE ET OPTIMISATION

### 9.1 Techniques d'Optimisation Utilisées

| Technique | Description | Gain |
|-----------|-------------|------|
| **GL_POINTS** | Points au lieu de sphères | ~50x plus rapide |
| **SoA (Structure of Arrays)** | NumPy arrays contigus | Meilleur cache CPU |
| **Vectorisation NumPy** | Opérations SIMD | ~10x plus rapide |
| **Display Lists** | Géométrie précompilée | Moins d'appels GL |
| **Cache de formations** | Formations statiques en mémoire | Évite recalcul |
| **Double rendu points** | Halo (12px) + Core (4px) | Glow sans shader |

### 9.2 Métriques de Performance

| Métrique | Cible | Actuel |
|----------|-------|--------|
| FPS | 60 | 60 stable |
| Drones | 1000 | 1000 |
| Latence frame | < 16ms | ~10-12ms |
| RAM | < 500 Mo | ~300 Mo |
| GPU VRAM | < 512 Mo | ~200 Mo |

### 9.3 Optimisations Futures Possibles

1. **VBO (Vertex Buffer Objects)** : Transfert GPU des positions
2. **Instanced Rendering** : Un seul draw call pour tous les drones
3. **Compute Shaders** : Physique sur GPU
4. **LOD (Level of Detail)** : Simplification à distance

---

## 10. DÉPENDANCES ET INSTALLATION

### 10.1 Dépendances Python

```
PyQt6>=6.6.0           # Interface graphique
PyOpenGL>=3.1.7        # Rendu 3D OpenGL
PyOpenGL-accelerate>=3.1.7  # Accélération PyOpenGL
numpy>=1.26.0          # Calculs vectoriels
PyYAML>=6.0.1          # Configuration YAML
Pillow>=10.0.0         # Traitement images
librosa>=0.10.0        # Analyse audio FFT
soundfile>=0.12.0      # Lecture fichiers audio
pygame>=2.1.3          # Lecture audio temps réel
```

### 10.2 Installation

```bash
# 1. Cloner le projet
git clone <repository>
cd DRONES-3D-ANEM-2025

# 2. Créer environnement virtuel
python -m venv .venv

# 3. Activer l'environnement
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Installer dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python src/main.py
```

### 10.3 Résolution de Problèmes Courants

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: PyQt6` | `pip install PyQt6` |
| Écran noir au démarrage | Vérifier drivers GPU OpenGL 3.3+ |
| Audio ne joue pas | Installer pygame et vérifier codec |
| Performances faibles | Réduire `max_drones` dans config |
| librosa erreur | `pip install librosa soundfile` |

---

## 11. LIVRABLES

### 11.1 Livrables Actuels

| # | Livrable | Description | Statut |
|---|----------|-------------|--------|
| 1 | Code source complet | Dossier `src/` avec 12 modules | ✅ Complet |
| 2 | Configuration | 3 fichiers YAML | ✅ Complet |
| 3 | Documentation | README + Cahier des charges | ✅ Complet |
| 4 | 25+ formations | Bibliothèque de chorégraphies | ✅ Complet |
| 5 | Système audio | Analyse FFT + lecture | ✅ Complet |
| 6 | Interface utilisateur | Panneau de contrôle complet | ✅ Complet |

### 11.2 Livrables Attendus (Optionnels)

| # | Livrable | Description | Priorité |
|---|----------|-------------|----------|
| 1 | Export vidéo | Enregistrement MP4 des séquences | Haute |
| 2 | Timeline editor | Éditeur visuel de séquences | Moyenne |
| 3 | Import GeoJSON | Formes depuis fichiers GeoJSON | Moyenne |
| 4 | Multi-caméra | Plusieurs angles simultanés | Basse |
| 5 | VR Support | Visualisation casque VR | Basse |

---

## 12. ÉVOLUTIONS FUTURES

### 12.1 Améliorations Techniques

1. **Migration vers OpenGL moderne (3.3+ Core Profile)**
   - Shaders GLSL personnalisés
   - Instanced rendering pour 10000+ drones

2. **Export de données pour drones réels**
   - Format Skybrush/Drone Show Software
   - Timeline avec waypoints précis

3. **Éditeur de formations visuel**
   - Interface drag & drop
   - Preview temps réel

4. **Synchronisation réseau**
   - Contrôle multi-utilisateur
   - Streaming vers projecteur

### 12.2 Améliorations Artistiques

1. **Plus de formations**
   - Carte d'Afrique complète
   - Monuments nigériens
   - Portraits (figures historiques)

2. **Effets avancés**
   - Traînées lumineuses (trails)
   - Particules (pluie, sable, étoiles)
   - Fumée/Fog volumétrique

3. **Scènes interactives**
   - Réaction au public (via audio ambiant)
   - Mode "DJ" pour improvisation

---

## 📌 ANNEXES

### A. Coordonnées du Niger (GeoJSON simplifié)

Le fichier `formation_library.py` contient 500+ points de coordonnées précises des frontières du Niger pour la formation `phase7_carte`.

### B. Police Bitmap Intégrée

Caractères supportés avec matrice 5x7 :
```
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
0 1 2 3 4 5 6 7 8 9 -
```

### C. Glossaire

| Terme | Définition |
|-------|------------|
| **Bio-Swarm** | Algorithme de mouvement inspiré des essaims naturels |
| **Bloom** | Effet de halo lumineux autour des sources brillantes |
| **Morphing** | Transition fluide entre deux formations |
| **FFT** | Fast Fourier Transform - analyse fréquentielle |
| **SoA** | Structure of Arrays - organisation mémoire optimisée |
| **VBO** | Vertex Buffer Object - stockage GPU des vertices |

---

## 📝 HISTORIQUE DES VERSIONS

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | 29/01/2026 | Version initiale du cahier des charges |

---

**Document rédigé pour le projet DRONES-3D-ANEM-2025**  
*Simulation 3D de spectacle de drones pour la cérémonie ANEM 2025*

---
