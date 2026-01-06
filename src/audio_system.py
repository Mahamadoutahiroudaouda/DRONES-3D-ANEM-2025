import numpy as np
import threading
import os
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("WARNING: librosa not installed. Audio reactivity disabled.")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("WARNING: pygame not installed. Audio playback disabled.")

class AudioSystem:
    """
    Real-time audio analysis system for drone shows.
    Provides FFT-based energy extraction for bass, mid, treble frequencies.
    """
    
    def __init__(self):
        self.audio_loaded = False
        self.audio_path = None
        self.y = None  # Audio time series
        self.sr = None  # Sample rate
        self.current_sample = 0
        
        # Audio playback state
        self.is_playing = False
        self.playback_position = 0  # in samples
        self.playback_start_time = 0
        
        # FFT analysis parameters
        self.n_fft = 2048
        self.hop_length = 512
        self.frame_index = 0
        
        # Frequency bands (normalized [0,1])
        self.bass_energy = 0.0      # 0-250 Hz
        self.mid_energy = 0.0       # 250-2000 Hz
        self.treble_energy = 0.0    # 2000+ Hz
        
        # General metrics
        self.overall_energy = 0.0
        self.beat_strength = 0.0
        self.kick_detected = False
        
        # Smoothing for stability
        self.smoothing_alpha = 0.3
        self.bass_smooth = 0.0
        self.mid_smooth = 0.0
        self.treble_smooth = 0.0
        
        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("Pygame mixer initialized successfully")
                self.pygame_sound = None
            except Exception as e:
                print(f"WARNING: Could not initialize pygame mixer: {e}")
                self.pygame_available_local = False
                return
    
    def load_audio(self, filepath):
        """Load audio file using librosa."""
        if not LIBROSA_AVAILABLE:
            print("ERROR: librosa not available. Cannot load audio.")
            return False
        
        # Validate file exists
        if not os.path.exists(filepath):
            print(f"ERROR: File not found: {filepath}")
            return False
        
        try:
            # Load with librosa for analysis
            self.y, self.sr = librosa.load(filepath, sr=None)
            self.audio_loaded = True
            self.audio_path = filepath
            self.current_sample = 0
            self.frame_index = 0
            self.playback_position = 0
            print(f"Audio loaded: {filepath}")
            print(f"Sample rate: {self.sr}, Duration: {len(self.y)/self.sr:.2f}s")
            
            # Load with pygame mixer for playback
            if PYGAME_AVAILABLE:
                try:
                    # Close any existing sound first
                    if self.pygame_sound:
                        self.pygame_sound.stop()
                    
                    self.pygame_sound = pygame.mixer.Sound(filepath)
                    print(f"Audio ready for playback: {os.path.basename(filepath)}")
                    return True
                except Exception as e:
                    print(f"WARNING: Could not load audio with pygame: {e}")
                    print(f"File type might not be supported. Supported: WAV, OGG, MP3 (with SDL_mixer)")
                    return False
            else:
                print("WARNING: Pygame not available for playback")
                return False
                
        except Exception as e:
            print(f"ERROR loading audio: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update(self, dt):
        """Update audio analysis based on elapsed time."""
        if not self.audio_loaded:
            return
        
        # Calculate current sample position
        self.current_sample = int(self.frame_index * self.hop_length)
        
        # Check if we've reached the end
        if self.current_sample >= len(self.y):
            self.current_sample = 0
            self.frame_index = 0
        
        # Extract current frame
        frame_end = min(self.current_sample + self.n_fft, len(self.y))
        frame = self.y[self.current_sample:frame_end]
        
        if len(frame) < self.n_fft:
            # Pad if necessary
            frame = np.pad(frame, (0, self.n_fft - len(frame)))
        
        # Compute FFT
        S = np.abs(librosa.stft(frame, n_fft=self.n_fft))
        S_db = librosa.power_to_db(S ** 2, ref=np.max)
        
        # Compute frequencies
        freqs = librosa.fft_frequencies(sr=self.sr, n_fft=self.n_fft)
        
        # Extract energy by frequency band
        bass_idx = (freqs < 250)
        mid_idx = (freqs >= 250) & (freqs < 2000)
        treble_idx = (freqs >= 2000)
        
        bass_raw = np.mean(S_db[bass_idx]) if np.any(bass_idx) else 0.0
        mid_raw = np.mean(S_db[mid_idx]) if np.any(mid_idx) else 0.0
        treble_raw = np.mean(S_db[treble_idx]) if np.any(treble_idx) else 0.0
        
        # Normalize to [0, 1]
        bass_norm = np.clip((bass_raw + 80) / 80, 0, 1)
        mid_norm = np.clip((mid_raw + 80) / 80, 0, 1)
        treble_norm = np.clip((treble_raw + 80) / 80, 0, 1)
        
        # Exponential smoothing for stability
        self.bass_smooth = self.smoothing_alpha * bass_norm + (1 - self.smoothing_alpha) * self.bass_smooth
        self.mid_smooth = self.smoothing_alpha * mid_norm + (1 - self.smoothing_alpha) * self.mid_smooth
        self.treble_smooth = self.smoothing_alpha * treble_norm + (1 - self.smoothing_alpha) * self.treble_smooth
        
        self.bass_energy = self.bass_smooth
        self.mid_energy = self.mid_smooth
        self.treble_energy = self.treble_smooth
        
        # Overall energy metric
        self.overall_energy = (self.bass_energy * 0.4 + self.mid_energy * 0.3 + self.treble_energy * 0.3)
        
        # Simple kick detection: large jump in bass
        bass_delta = self.bass_energy - self.bass_smooth
        self.kick_detected = bass_delta > 0.3
        
        # Advance frame
        self.frame_index += 1
    
    def get_audio_energy(self):
        """Return overall audio energy [0, 1]."""
        return self.overall_energy
    
    def get_bass_energy(self):
        """Return bass frequency energy [0, 1]."""
        return self.bass_energy
    
    def get_mid_energy(self):
        """Return mid frequency energy [0, 1]."""
        return self.mid_energy
    
    def get_treble_energy(self):
        """Return treble frequency energy [0, 1]."""
        return self.treble_energy
    
    def is_kick_detected(self):
        """Return whether a kick was detected this frame."""
        return self.kick_detected
    
    def play(self):
        """Start audio playback."""
        if not self.audio_loaded:
            print("ERROR: No audio loaded. Cannot play.")
            return False
        
        if not self.pygame_sound:
            print("ERROR: pygame_sound object not initialized")
            return False
        
        if PYGAME_AVAILABLE:
            try:
                # Stop any existing playback first
                pygame.mixer.stop()
                # Play the sound
                self.pygame_sound.play()
                self.is_playing = True
                self.playback_position = 0
                print("OK: Audio playback started")
                return True
            except Exception as e:
                print(f"ERROR: Could not play audio: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("ERROR: Pygame mixer not available for playback")
            return False
    
    def stop(self):
        """Stop audio playback."""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.stop()
                self.is_playing = False
                print("OK: Audio playback stopped")
                return True
            except Exception as e:
                print(f"ERROR: Could not stop audio: {e}")
                return False
        return False
    
    def pause(self):
        """Pause audio playback."""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.pause()
                self.is_playing = False
                print("OK: Audio playback paused")
                return True
            except Exception as e:
                print(f"ERROR: Could not pause audio: {e}")
                return False
        return False
    
    def unpause(self):
        """Resume audio playback from pause."""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.unpause()
                self.is_playing = True
                print("OK: Audio playback resumed")
                return True
            except Exception as e:
                print(f"ERROR: Could not resume audio: {e}")
                return False
        return False
