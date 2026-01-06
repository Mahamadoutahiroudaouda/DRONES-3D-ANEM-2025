import numpy as np
from physics_engine import PhysicsEngine

class DroneManager:
    def __init__(self, sim_config, vis_config):
        self.sim_config = sim_config
        self.vis_config = vis_config
        self.num_drones = sim_config['simulation']['max_drones']
        
        self.physics = PhysicsEngine(sim_config)
        
        # State arrays for efficiency (Structure of Arrays)
        # Using numpy for batch processing 1000 drones
        self.positions = np.zeros((self.num_drones, 3), dtype=np.float32)
        self.colors = np.ones((self.num_drones, 3), dtype=np.float32) # RGB
        self.targets = np.zeros((self.num_drones, 3), dtype=np.float32)
        
        # Initialize random positions on ground
        self.positions[:, 0] = np.random.uniform(-50, 50, self.num_drones)
        self.positions[:, 1] = 0 # Ground
        self.positions[:, 2] = np.random.uniform(-50, 50, self.num_drones)
        
        # Targets start at current positions (idle)
        self.targets[:] = self.positions[:]

    def update(self, dt, time_absolute=0.0):
        """
        Update all drone states for one frame.
        """
        self.positions = self.physics.update_drones(self.positions, self.targets, dt, time_absolute)

    def set_formation(self, target_coords, target_colors=None):
        """
        Update target positions from a formation pattern.
        """
        count = min(len(target_coords), self.num_drones)
        
        # Update targets for active drones
        self.targets[:count] = target_coords[:count]
        
        # Drones without a spot in formation could go to a holding area or ground
        # For now, let's keep them where they are or send to ground
        if count < self.num_drones:
            self.targets[count:, 1] = 0 # Land
            
        if target_colors is not None:
             self.colors[:count] = target_colors[:count]

    def get_render_data(self):
        """
        Returns data suitable for instanced rendering.
        """
        return self.positions, self.colors
