import numpy as np

class FormationLibrary:
    def __init__(self):
        # Palette Officielle
        self.colors = {
            "orange_niger": [1.0, 1.0, 1.0], # OVERRIDE TO WHITE
            "blanc_pure": [1.0, 1.0, 1.0],      
            "vert_niger": [1.0, 1.0, 1.0],  # OVERRIDE TO WHITE
            "soleil_or": [1.0, 1.0, 1.0],       # OVERRIDE TO WHITE
            "bleu_nuit": [0.0, 0.122, 0.247],   
            "turquoise": [0.224, 0.8, 0.8],      
        }

    def get_phase(self, phase_name, num_drones):
        """
        Returns (positions, colors) for a given phase.
        """
        if phase_name == "phase1_pluie":
            return self._phase_1_pluie(num_drones)
        elif phase_name == "phase2_anem":
            return self._text_formation("ANEM", num_drones, self.colors["orange_niger"])
        elif phase_name == "phase3_jcn":
            return self._phase_3_jcn(num_drones)
        elif phase_name == "phase4_fes":
            return self._phase_4_fes(num_drones)
        elif phase_name == "phase5_niger":
            return self._phase_5_niger(num_drones)
        elif phase_name == "phase6_drapeau":
            return self._phase_6_drapeau(num_drones)
        elif phase_name == "phase7_carte":
            return self._phase_7_carte(num_drones)
        elif phase_name == "phase8_finale":
            return self._phase_8_finale(num_drones)
        elif phase_name == "phase9_agadez":
            return self._phase_9_agadez(num_drones)
        elif phase_name == "phase10_touareg":
            return self._phase_10_touareg(num_drones)
        else:
            # Default fallback: Sphere
            return self._shape_sphere(num_drones, 50.0, self.colors["turquoise"])

    def _text_formation(self, text, num_drones, color, scale_override=None):
        # Improved Text Generation: Dot Matrix / structured Grid style
        # "TECNO" reference style: Clean, bold, readable dots.
        
        # Font definition (5x7)
        font = {
            'A': [[0,1,1,1,0],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1]],
            'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1]],
            'E': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,1,1,1,1]],
            'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'J': [[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'C': [[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[0,1,1,1,1]],
            '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,1,1,0],[0,1,0,0,0],[1,1,1,1,1]],
            '0': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '6': [[0,1,1,1,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[0,1,1,1,0]],
            'F': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,0,0],[1,0,0,0,0],[1,0,0,0,0]],
            'S': [[0,1,1,1,1],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[1,1,1,1,0]],
            '-': [[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[0,0,0,0,0],[0,0,0,0,0]],
            'K': [[1,0,0,1,0],[1,0,1,0,0],[1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0]],
            'I': [[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            'G': [[0,1,1,1,0],[1,0,0,0,0],[1,0,1,1,1],[1,0,0,0,1],[0,1,1,1,0]],
            'R': [[1,1,1,1,0],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1]],
        }
        
        points = []
        offset_x = 0
        spacing = 6
        
        if scale_override:
            scale = scale_override
        else:
            scale = 8.0 # Default
        
        # To make it "Bold" like the image, we can:
        # 1. Use multiple layers in Z (Depth)
        # 2. Add sub-pixels (e.g. 2x2 grid per font pixel) 
        #    But 5x7 is already tight.
        # Let's align drones in strict Z-layers to emulate "bars" of light.
        
        depth_layers = 5 # 5 layers of depth to use many drones
        depth_spacing = 2.0
        
        total_width_grid = len(text) * 5 + (len(text)-1) * 1
        total_width_world = total_width_grid * scale
        start_x = -total_width_world / 2
        
        # Center Y logic:
        # We want the text block centered at Y=70
        # Font height is 7 units
        height_world = 7 * scale
        top_y = 70 + height_world / 2
        
        for char in text:
            if char in font:
                grid = font[char]
                h = len(grid)
                w = len(grid[0])
                
                for r in range(h):
                    for c in range(w):
                        if grid[r][c]:
                            # Base pixel position
                            x = start_x + (offset_x + c) * scale
                            y = top_y - r * scale 
                            
                            # Create a "Column" or "Bar" in Z
                            for d in range(depth_layers):
                                z = (d - (depth_layers-1)/2) * depth_spacing
                                points.append([x, y, z])
            
            offset_x += spacing
            
        if not points:
             return self._shape_sphere(num_drones, 20, color)
        
        points = np.array(points)
        num_points = len(points)
        
        final_pos = np.zeros((num_drones, 3))
        final_cols = np.tile(color, (num_drones, 1))
        
        # Distribute drones to points.
        # If drones > points, reuse points (super density)
        # If drones < points, we have a problem (gaps), but 1000 is a lot.
        
        for i in range(num_drones):
            target_idx = i % num_points
            pos = points[target_idx]
            final_pos[i] = pos
            
            # Color Logic: Flag Gradient
            # ... (Sim core overrides this generally to white, but we keep structure)
            y = pos[1]
            # ... strict white override below
            final_cols[i] = self.colors["blanc_pure"]
            
        return final_pos, final_cols


    def _shape_cube(self, num, size, color):
        # Simple random cube for testing
        pos = np.random.uniform(-size/2, size/2, (num, 3))
        pos[:, 1] += 50 # Lift up
        cols = np.tile(color, (num, 1))
        return pos, cols

    def _shape_sphere(self, num, radius, color):
        # Fibonacci sphere
        indices = np.arange(0, num, dtype=float) + 0.5
        phi = np.arccos(1 - 2*indices/num)
        theta = np.pi * (1 + 5**0.5) * indices
        
        x = radius * np.cos(theta) * np.sin(phi)
        y = radius * np.sin(theta) * np.sin(phi) + 75 # Center altitude
        z = radius * np.cos(phi)
        
        pos = np.column_stack((x, y, z))
        cols = np.tile(color, (num, 1))
        return pos, cols

    def _phase_1_pluie(self, num):
        # "Une pluie verticale parfaitement organisée"
        # "Points alignés en lignes droites"
        # "Rideau de lumière"
        
        # We create a grid of vertical lines.
        # X-Z plane grid. Y is filled.
        
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        # Grid dimensions
        rows_x = 25
        rows_z = 4  # Minimal depth for curtain
        
        drones_per_line = num // (rows_x * rows_z)
        if drones_per_line < 1: drones_per_line = 1
        
        # Spacing
        spacing_x = 6.0
        spacing_z = 3.0
        spacing_y = 2.5 # Vertical density
        
        start_x = -((rows_x - 1) * spacing_x) / 2
        start_y = 120 # Start high, they will "fall" or just sit there?
        # User said "Descend lentement".
        # But formation usually returns a target state.
        # Let's create the "Finish" state as the full curtain.
        
        idx = 0
        for x_i in range(rows_x):
            for z_i in range(rows_z):
                # For each vertical line
                line_x = start_x + x_i * spacing_x
                line_z = (z_i - (rows_z-1)/2) * spacing_z
                
                for y_i in range(drones_per_line):
                    if idx >= num: break
                    
                    # Top to bottom filling? or Bottom up?
                    # "Rideau qui tombe" -> usually implies filling from top or sliding down.
                    # Let's position them in the final "Curtain" state.
                    # Y range: Center around 70m (perfect for screen)
                    # Height 30m?
                    
                    line_y = 85 - y_i * spacing_y # 85 down to ~60
                    
                    pos[idx] = [line_x, line_y, line_z]
                    
                    # Color Logic: Flag Bands (Used for geometry, but Simulation currently overrides to White)
                    # Still good to keep geometry logic correct just in case
                    if line_y > 77:
                         cols[idx] = self.colors["orange_niger"]
                    elif line_y > 70:
                         cols[idx] = self.colors["blanc_pure"]
                    else:
                         cols[idx] = self.colors["vert_niger"]
                    
                    idx += 1
                    
        return pos, cols

    def _phase_3_jcn(self, num):
        # "JCN2026" - Matrix Style, Unified White
        return self._text_formation("JCN2026", num, self.colors["blanc_pure"], scale_override=4.0)

    def _phase_4_fes(self, num):
        # "FES-MEKNES" - Matrix Style, Unified White
        # Longer string -> Reduce scale further
        return self._text_formation("FES-MEKNES", num, self.colors["blanc_pure"], scale_override=3.5)

    def _phase_5_niger(self, num):
        # "NIGER" - Matrix Style, Unified White
        return self._text_formation("NIGER", num, self.colors["blanc_pure"], scale_override=5.5)

    def _phase_6_drapeau(self, num):
        # "Drapeau Flottant / Surface Vivante"
        cols_grid = 40
        rows_grid = num // cols_grid
        
        pos = np.zeros((num, 3))
        cols = np.zeros((num, 3))
        
        width = 160.0
        height = 90.0
        start_y = 30.0 # Centered lower for flag
        
        dx = width / (cols_grid - 1)
        dy = height / (rows_grid - 1)
        
        idx = 0
        for r in range(rows_grid):
            for c in range(cols_grid):
                if idx >= num: break
                x = c * dx - width/2
                y = (rows_grid - 1 - r) * dy + start_y
                pos[idx] = [x, y, 0]
                cols[idx] = self.colors["blanc_pure"]
                idx += 1
        return pos, cols

    def _phase_7_carte(self, num):
        # Precise Niger Map logic
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["blanc_pure"], (num, 1))
        
        min_x, max_x = -70, 70
        min_y, max_y = -30, 40
        
        count = 0
        trials = 0
        while count < num and trials < num * 20:
            rx = np.random.uniform(min_x, max_x)
            ry = np.random.uniform(min_y, max_y)
            
            # Simplified Niger Shape (Heuristic)
            in_niger = False
            # Western "Handle"
            if rx > -65 and rx < -30 and ry > 0 and ry < 30: in_niger = True
            # Main Body
            if rx >= -30 and rx < 50 and ry > -25 and ry < 35: in_niger = True
            # Eastern Part
            if rx >= 50 and rx < 90 and ry > -10 and ry < 25: in_niger = True
            
            if in_niger:
                pos[count] = [rx, ry + 60, 0]
                count += 1
            trials += 1
            
        return pos, cols

    def _phase_8_finale(self, num):
        # Spectacular Finale: 8-branch star 3D
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["blanc_pure"], (num, 1))
        
        # Fibonacci sphere for the core
        core_num = num // 2
        indices = np.arange(0, core_num, dtype=float) + 0.5
        phi = np.arccos(1 - 2*indices/core_num)
        theta = np.pi * (1 + 5**0.5) * indices
        radius = 25.0
        pos[:core_num, 0] = radius * np.cos(theta) * np.sin(phi)
        pos[:core_num, 1] = radius * np.sin(theta) * np.sin(phi) + 70
        pos[:core_num, 2] = radius * np.cos(phi)
        
        # Rays
        rays_num = num - core_num
        rays = 8
        drones_per_ray = rays_num // rays
        for r in range(rays):
            angle = (2 * np.pi / rays) * r
            for d in range(drones_per_ray):
                idx = core_num + r * drones_per_ray + d
                dist = radius + d * 2.5
                pos[idx] = [
                    dist * np.cos(angle),
                    dist * np.sin(angle) + 70,
                    np.random.uniform(-3, 3)
                ]
        return pos, cols

    def _phase_9_agadez(self, num):
        # "La Grande Mosquée d'Agadez"
        # Monumental, Pure White, Solid structure
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["blanc_pure"], (num, 1))
        
        # 1. Main body (Tapering Pyramid) - ~600 drones
        body_num = 600
        height = 90.0
        base_w = 34.0
        top_w = 8.0
        center_y = 20.0 # Starting altitude
        
        # We fill the faces of the pyramid
        idx = 0
        face_drones = body_num // 4
        
        for f in range(4):
            for i in range(face_drones):
                h_rel = np.random.uniform(0, 1) # vertical rel position
                w_curr = base_w * (1.0 - h_rel) + top_w * h_rel
                side_rel = np.random.uniform(-0.5, 0.5)
                
                y = center_y + h_rel * height
                local_x = side_rel * w_curr
                
                if f == 0: # Front
                    px, py, pz = local_x, y, w_curr/2
                elif f == 1: # Back
                    px, py, pz = local_x, y, -w_curr/2
                elif f == 2: # Left
                    px, py, pz = -w_curr/2, y, local_x
                else: # Right
                    px, py, pz = w_curr/2, y, local_x
                
                pos[idx] = [px, py, pz]
                idx += 1
                
        # 2. Torons (Protruding beams) - ~300 drones
        toron_num = 300
        rows = 12
        per_row = toron_num // rows
        
        for r in range(rows):
            h_rel = (r + 1) / (rows + 1)
            w_curr = base_w * (1.0 - h_rel) + top_w * h_rel
            y = center_y + h_rel * height
            
            for p in range(per_row):
                corner = p % 4
                beam_len = np.random.uniform(2.0, 6.0)
                
                if corner == 0: # TL
                    pos[idx] = [-w_curr/2 - beam_len, y, w_curr/2 + beam_len]
                elif corner == 1: # TR
                    pos[idx] = [w_curr/2 + beam_len, y, w_curr/2 + beam_len]
                elif corner == 2: # BL
                    pos[idx] = [-w_curr/2 - beam_len, y, -w_curr/2 - beam_len]
                else: # BR
                    pos[idx] = [w_curr/2 + beam_len, y, -w_curr/2 - beam_len]
                
                idx += 1
                
        # 3. Base (Rectangular buildings) - Remaining drones
        base_num = num - idx
        for i in range(max(0, base_num)):
            bx = np.random.uniform(-60, 60)
            bz = np.random.uniform(-40, 40)
            by = np.random.uniform(0, 20)
            
            if abs(bx) < base_w/2 + 2 and abs(bz) < base_w/2 + 2:
                bx += 40 if bx > 0 else -40
            
            pos[idx] = [bx, by, bz]
            idx += 1
            
        return pos, cols

    def _phase_10_touareg(self, num):
        # "Touareg avec son chameau"
        # 3D sculptural scene
        pos = np.zeros((num, 3))
        cols = np.tile(self.colors["blanc_pure"], (num, 1))
        
        idx = 0
        
        # --- CAMEL (approx 600 drones) ---
        camel_num = 600
        # Body (Ellipse-like)
        body_n = 250
        body_center = [15, 30, 0]
        for i in range(body_n):
             rx = np.random.uniform(-15, 15)
             ry = np.random.uniform(-10, 10)
             rz = np.random.uniform(-8, 8)
             # Spheroid filter
             if (rx/15)**2 + (ry/10)**2 + (rz/8)**2 < 1.0:
                 pos[idx] = [body_center[0] + rx, body_center[1] + ry, body_center[2] + rz]
                 idx += 1
        
        # Hump
        hump_n = 80
        for i in range(hump_n):
             rx = np.random.uniform(-7, 7)
             ry = np.random.uniform(0, 10)
             rz = np.random.uniform(-6, 6)
             if (rx/7)**2 + (ry/10)**2 + (rz/6)**2 < 1.0:
                 pos[idx] = [body_center[0] + rx, body_center[1] + 10 + ry, body_center[2] + rz]
                 idx += 1
                 
        # Neck & Head
        neck_n = 100
        neck_base = [body_center[0] - 15, body_center[1] + 5, 0]
        for i in range(neck_n):
             t = i / neck_n
             nx = neck_base[0] - 10 * t
             ny = neck_base[1] + 25 * t
             nz = np.random.uniform(-2, 2)
             pos[idx] = [nx, ny, nz]
             idx += 1
             
        # Head
        head_n = 50
        head_pos = [neck_base[0] - 12, neck_base[1] + 28, 0]
        for i in range(head_n):
             rx, ry, rz = np.random.uniform(-5, 5, 3)
             if rx*rx + ry*ry + rz*rz < 25:
                 pos[idx] = [head_pos[0] + rx, head_pos[1] + ry, head_pos[2] + rz]
                 idx += 1
                 
        # Legs (4 legs)
        leg_n = 120
        leg_pos = [[10, 20, 5], [10, 20, -5], [-10, 20, 5], [-10, 20, -5]]
        for l in range(4):
            lp = leg_pos[l]
            for i in range(leg_n // 4):
                 t = i / (leg_n // 4)
                 lx = body_center[0] + lp[0]
                 ly = (body_center[1] - 5) * (1-t) # To ground
                 lz = lp[2]
                 pos[idx] = [lx, ly, lz]
                 idx += 1
                 
        # --- TOUAREG (approx 400 drones) ---
        touareg_num = num - idx
        t_center = [-25, 20, 5] # Standing next to camel head
        # Robe / Body (Cylinder)
        for i in range(int(touareg_num * 0.8)):
             h = np.random.uniform(0, 40)
             r = 6 * (1.0 - h/80) # Slightly tapering
             angle = np.random.uniform(0, 2*np.pi)
             tx = t_center[0] + r * np.cos(angle)
             ty = h
             tz = t_center[2] + r * np.sin(angle)
             pos[idx] = [tx, ty, tz]
             idx += 1
             
        # Head / Turban
        for i in range(num - idx):
             rx, ry, rz = np.random.uniform(-5, 5, 3)
             if rx*rx + ry*ry + rz*rz < 25:
                 pos[idx] = [t_center[0] + rx, 45 + ry, t_center[2] + rz]
                 idx += 1
                 
        return pos, cols
