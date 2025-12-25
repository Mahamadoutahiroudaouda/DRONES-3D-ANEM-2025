import OpenGL.GL as gl

class LightingSystem:
    def __init__(self, vis_config):
        self.config = vis_config['visuals']['lighting']
        
    def setup(self):
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        
        # Light colors
        ambient = [self.config['ambient_intensity']] * 3 + [1.0]
        diffuse = [self.config['diffuse_intensity']] * 3 + [1.0]
        specular = [self.config['specular_intensity']] * 3 + [1.0]
        
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, ambient)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, diffuse)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, specular)
        
        # Light position (Directional light from "moon" or stadium lights)
        pos = [50.0, 100.0, 50.0, 0.0] # w=0 means directional
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, pos)
        
        # Material tracking
        gl.glColorMaterial(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE)
