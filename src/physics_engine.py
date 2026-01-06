import numpy as np

class PhysicsEngine:
    def __init__(self, config):
        self.config = config['simulation']['physics']
        self.max_speed = self.config['max_speed_m_s']
        self.acceleration = self.config['acceleration_m_s2']
        self.collision_radius = self.config['collision_radius_m']
        self.min_separation = self.config['min_separation_m']

    def update_drones(self, current_positions, target_positions, dt, time_absolute=0.0):
        """
        Updates drone positions based on targets and physics constraints.
        Includes "Bio-Swarm" vector fields and lightweight local avoidance.
        """
        # 1. Force towards Target (Elastic/Spring)
        to_target = target_positions - current_positions
        dist_target = np.linalg.norm(to_target, axis=1, keepdims=True)
        
        # Desired velocity is proportional to distance (P-Controller)
        # Clamped to max_speed
        desired_speed = np.clip(dist_target * 2.0, 0, self.max_speed)
        
        # Avoid division by zero
        safe_dist = np.where(dist_target < 1e-4, 1.0, dist_target)
        velocity_target = (to_target / safe_dist) * desired_speed
        
        # 2. Turbulence Organique (Curl Noise Simulation)
        # This adds the "living" feel without expensive fluid sims.
        freq = 0.05
        # Vectorized sin/cos noise field
        noise_x = np.sin(current_positions[:, 1] * freq) * np.cos(current_positions[:, 2] * freq)
        noise_y = np.sin(current_positions[:, 0] * freq) * np.cos(current_positions[:, 2] * freq)
        noise_z = np.cos(current_positions[:, 0] * freq) * np.sin(current_positions[:, 1] * freq)
        
        turbulence = np.column_stack((noise_x, noise_y, noise_z)) * 2.0 # Strength
        
        # 3. Micro-Avoidance / Grid Jitter
        # Prevents "Robot Line" artifacting by giving each drone a unique micro-personality
        # based on its index (modulo math cheaper than random usage per frame)
        indices = np.arange(len(current_positions))
        phase_jitter = indices * 0.1 + time_absolute
        jitter = np.column_stack((
            np.sin(phase_jitter), 
            np.cos(phase_jitter * 0.7), 
            np.sin(phase_jitter * 0.5)
        )) * 0.5

        # 4. Integrate
        # New Velocity = TargetSeeking + Turbulence + Jitter
        total_velocity = velocity_target + turbulence + jitter
        
        # Limit global acceleration to prevent snapping
        # (Simplified: Just clamp velocity magnitude to max_speed again just in case turbulence pushed it over)
        speed_sq = np.sum(total_velocity**2, axis=1, keepdims=True)
        over_speed_mask = (speed_sq > (self.max_speed**2)).flatten()
        
        if np.any(over_speed_mask):
            current_speeds = np.sqrt(speed_sq[over_speed_mask])
            scale = self.max_speed / current_speeds
            total_velocity[over_speed_mask] *= scale

        # Euler Integration
        new_positions = current_positions + total_velocity * dt
        
        return new_positions
