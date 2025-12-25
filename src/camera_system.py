import numpy as np
from OpenGL.GLU import gluLookAt

class CameraSystem:
    def __init__(self):
        self.position = np.array([0.0, 50.0, 150.0]) # Default position
        self.target = np.array([0.0, 50.0, 0.0]) # Look at center
        self.up = np.array([0.0, 1.0, 0.0])
        self.fov = 45.0
        self.aspect_ratio = 1.6
        
    def apply_view(self):
        """
        Apply the camera view transformation.
        Assumes MatrixMode is MODELVIEW.
        """
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            self.target[0], self.target[1], self.target[2],
            self.up[0], self.up[1], self.up[2]
        )
        
    def set_position(self, x, y, z):
        self.position = np.array([x, y, z])

    def rotate_orbit(self, angle_y):
        """
        Simple orbit around 0,0,0
        """
        radius = np.linalg.norm(self.position)
        # Simplified math for quick orbit
        # In a real app we'd use proper quaternions or matrices
        import math
        theta = math.radians(angle_y)
        self.position[0] = radius * math.sin(theta)
        self.position[2] = radius * math.cos(theta)
