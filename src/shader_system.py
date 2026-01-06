"""
GLSL Shader system for advanced post-processing effects.
Implements bloom/glow and HDR cinematic effects.
"""

import OpenGL.GL as gl
import numpy as np

# Check if shader functions are available
def check_shader_support():
    """Safely check if shader functions are available."""
    try:
        # Try to check if OpenGL 2.0+ is available
        version = gl.glGetString(gl.GL_VERSION)
        if version:
            return True
    except:
        pass
    return False

HAS_SHADER_SUPPORT = check_shader_support()

# === VERTEX SHADER (Simple Passthrough) ===
VERTEX_SHADER = """
#version 120

void main(void)
{
    gl_Position = gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
"""

# === FRAGMENT SHADER (Bloom Glow Effect) ===
FRAGMENT_SHADER_BLOOM = """
#version 120

uniform sampler2D texture0;
uniform float bloom_threshold;
uniform float bloom_intensity;

void main(void)
{
    vec4 color = texture2D(texture0, gl_TexCoord[0].st);
    
    // Extract bright areas (pixels brighter than threshold)
    float brightness = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    
    if (brightness > bloom_threshold) {
        // Apply glow to bright pixels
        gl_FragColor = color * bloom_intensity;
    } else {
        gl_FragColor = color * 0.3;  // Darken non-bright areas
    }
}
"""

# === FRAGMENT SHADER (Gaussian Blur for Bloom) ===
FRAGMENT_SHADER_BLUR = """
#version 120

uniform sampler2D texture0;
uniform vec2 texture_offset[9];
uniform float kernel[9];

void main(void)
{
    vec4 color = vec4(0.0);
    
    for (int i = 0; i < 9; i++) {
        color += texture2D(texture0, gl_TexCoord[0].st + texture_offset[i]) * kernel[i];
    }
    
    gl_FragColor = color;
}
"""

# === FRAGMENT SHADER (Tone Mapping HDR) ===
FRAGMENT_SHADER_TONEMAP = """
#version 120

uniform sampler2D texture0;
uniform sampler2D bloom_texture;
uniform float exposure;
uniform float gamma;

vec3 Reinhard_Tonemap(vec3 color)
{
    return color / (color + vec3(1.0));
}

void main(void)
{
    vec3 hdr_color = texture2D(texture0, gl_TexCoord[0].st).rgb;
    vec3 bloom = texture2D(bloom_texture, gl_TexCoord[0].st).rgb;
    
    // Combine HDR with bloom
    vec3 final = hdr_color + bloom * 0.5;
    
    // Tone mapping
    final = final * exposure;
    final = Reinhard_Tonemap(final);
    
    // Gamma correction
    final = pow(final, vec3(1.0 / gamma));
    
    gl_FragColor = vec4(final, 1.0);
}
"""


class ShaderProgram:
    """Manages a GLSL shader program."""
    
    def __init__(self, vertex_src, fragment_src, name="ShaderProgram"):
        self.name = name
        self.program = None
        self.uniforms = {}
        
        try:
            self.compile_shaders(vertex_src, fragment_src)
        except Exception as e:
            print(f"ERROR compiling shader {name}: {e}")
    
    def compile_shaders(self, vertex_src, fragment_src):
        """Compile vertex and fragment shaders."""
        if not HAS_SHADER_SUPPORT:
            print(f"WARNING: Shader support not available on this GPU. Skipping {self.name}.")
            self.program = None
            return
        
        try:
            # Check if shader functions actually exist
            if not hasattr(gl, 'glCreateShader'):
                print(f"WARNING: glCreateShader not found. Shader {self.name} disabled.")
                self.program = None
                return
            
            # Compile vertex shader
            vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
            gl.glShaderSource(vertex, vertex_src)
            gl.glCompileShader(vertex)
            
            if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
                log = gl.glGetShaderInfoLog(vertex).decode()
                raise Exception(f"Vertex shader compilation failed:\n{log}")
            
            # Compile fragment shader
            fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
            gl.glShaderSource(fragment, fragment_src)
            gl.glCompileShader(fragment)
            
            if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
                log = gl.glGetShaderInfoLog(fragment).decode()
                raise Exception(f"Fragment shader compilation failed:\n{log}")
            
            # Link program
            self.program = gl.glCreateProgram()
            gl.glAttachShader(self.program, vertex)
            gl.glAttachShader(self.program, fragment)
            gl.glLinkProgram(self.program)
            
            if not gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS):
                log = gl.glGetProgramInfoLog(self.program).decode()
                raise Exception(f"Program linking failed:\n{log}")
            
            gl.glDeleteShader(vertex)
            gl.glDeleteShader(fragment)
            
            print(f"OK: Shader compiled: {self.name}")
        except Exception as e:
            print(f"WARNING: Shader {self.name} disabled: {e}")
            self.program = None
    
    def use(self):
        """Use this shader program."""
        if self.program is not None:
            gl.glUseProgram(self.program)
    
    def stop(self):
        """Stop using any shader program."""
        gl.glUseProgram(0)
    
    def set_uniform_1f(self, name, value):
        """Set a float uniform."""
        if self.program is None:
            return
        loc = gl.glGetUniformLocation(self.program, name)
        if loc != -1:
            gl.glUniform1f(loc, value)
    
    def set_uniform_2f(self, name, x, y):
        """Set a 2D float uniform."""
        loc = gl.glGetUniformLocation(self.program, name)
        if loc != -1:
            gl.glUniform2f(loc, x, y)
    
    def set_uniform_3f(self, name, x, y, z):
        """Set a 3D float uniform."""
        loc = gl.glGetUniformLocation(self.program, name)
        if loc != -1:
            gl.glUniform3f(loc, x, y, z)
    
    def set_uniform_1i(self, name, value):
        """Set an integer uniform."""
        loc = gl.glGetUniformLocation(self.program, name)
        if loc != -1:
            gl.glUniform1i(loc, value)
    
    def set_uniform_matrix4(self, name, matrix):
        """Set a 4x4 matrix uniform."""
        loc = gl.glGetUniformLocation(self.program, name)
        if loc != -1:
            gl.glUniformMatrix4fv(loc, 1, gl.GL_TRUE, matrix)


class PostProcessingPipeline:
    """Manages post-processing effects (bloom, tone mapping, etc)."""
    
    def __init__(self):
        self.bloom_shader = None
        self.blur_shader = None
        self.tonemap_shader = None
        
        self.fbo_bloom = None
        self.fbo_blur = None
        self.texture_bloom = None
        self.texture_blur = None
        
        self.width = 1280
        self.height = 720
        
        try:
            self.init_shaders()
            self.init_framebuffers()
        except Exception as e:
            print(f"ERROR initializing post-processing: {e}")
    
    def init_shaders(self):
        """Initialize shader programs."""
        try:
            self.bloom_shader = ShaderProgram(VERTEX_SHADER, FRAGMENT_SHADER_BLOOM, "Bloom")
            self.blur_shader = ShaderProgram(VERTEX_SHADER, FRAGMENT_SHADER_BLUR, "Blur")
            self.tonemap_shader = ShaderProgram(VERTEX_SHADER, FRAGMENT_SHADER_TONEMAP, "Tonemap")
            print("OK: All shaders initialized")
        except Exception as e:
            print(f"WARNING: Shader compilation failed. Bloom effects disabled: {e}")
    
    def init_framebuffers(self):
        """Initialize FBO textures for bloom pipeline."""
        if not HAS_SHADER_SUPPORT:
            print("WARNING: Skipping framebuffer setup (shader support unavailable)")
            return
        
        try:
            # Check if framebuffer functions exist
            if not hasattr(gl, 'glGenFramebuffers'):
                print("WARNING: glGenFramebuffers not available. FBO disabled.")
                return
            
            # Create bloom FBO and texture
            self.fbo_bloom = gl.glGenFramebuffers(1)
            self.texture_bloom = gl.glGenTextures(1)
            
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_bloom)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.width, self.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo_bloom)
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.texture_bloom, 0)
            
            if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
                raise Exception("Bloom FBO incomplete")
            
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            print("✓ Framebuffers initialized")
        except Exception as e:
            print(f"WARNING: Framebuffer setup failed: {e}")
    
    def apply_bloom(self, exposure=1.0, gamma=2.2, bloom_threshold=0.8, bloom_intensity=1.5):
        """Apply bloom post-processing effect."""
        if not self.bloom_shader or not self.fbo_bloom:
            return
        
        try:
            # Extract bright areas with bloom shader
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo_bloom)
            self.bloom_shader.use()
            self.bloom_shader.set_uniform_1f("bloom_threshold", bloom_threshold)
            self.bloom_shader.set_uniform_1f("bloom_intensity", bloom_intensity)
            
            # Render full-screen quad with bloom
            self.render_fullscreen_quad()
            
            # Apply tone mapping
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            self.tonemap_shader.use()
            self.tonemap_shader.set_uniform_1f("exposure", exposure)
            self.tonemap_shader.set_uniform_1f("gamma", gamma)
            self.tonemap_shader.set_uniform_1i("bloom_texture", 1)
            
            gl.glActiveTexture(gl.GL_TEXTURE1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_bloom)
            
            self.render_fullscreen_quad()
            self.tonemap_shader.stop()
            
        except Exception as e:
            print(f"ERROR applying bloom: {e}")
    
    def render_fullscreen_quad(self):
        """Render a full-screen quad for post-processing."""
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(-1, 1, -1, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0, 0); gl.glVertex2f(-1, -1)
        gl.glTexCoord2f(1, 0); gl.glVertex2f(1, -1)
        gl.glTexCoord2f(1, 1); gl.glVertex2f(1, 1)
        gl.glTexCoord2f(0, 1); gl.glVertex2f(-1, 1)
        gl.glEnd()
        
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
    
    def resize(self, width, height):
        """Resize post-processing buffers."""
        self.width = width
        self.height = height
        # Would need to recreate textures here
