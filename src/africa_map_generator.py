"""
Africa Map Generator for Act 5: L'âme africaine
Generates drone coordinates to form map of Africa with Niger highlighted in red.
Uses improved contour detection and vectorized generation.
"""

import numpy as np
from PIL import Image, ImageDraw
import os
from scipy.ndimage import label, find_objects
from scipy import ndimage

class AfricaMapGenerator:
    """Generate Africa map with Niger highlighted for drone formations."""
    
    def __init__(self, width=800, height=600, scale=0.9):
        """
        Initialize Africa map generator.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            scale: Scale factor for map (0-1)
        """
        self.width = width
        self.height = height
        self.scale = scale
        self.image_path = None
        self.map_img = None
        self.niger_mask = None
        
    def create_detailed_africa_map(self):
        """Load the Africa map reference image instead of generating."""
        # Try to load reference image
        ref_path = r"e:\Hama\DRONES-3D-ANEM-2025\data\assets\africa_map_reference.png"
        
        if os.path.exists(ref_path):
            self.map_img = Image.open(ref_path)
            print(f"OK: Loaded Africa map reference: {self.map_img.size}")
        else:
            # Fallback: create simple procedural map
            print("WARNING: Reference image not found, creating procedural map")
            img = Image.new('RGB', (self.width, self.height), color=(220, 220, 220))
            draw = ImageDraw.Draw(img)
            
            africa_coastline = [
                (80, 100), (85, 150), (90, 200), (95, 250), (100, 300), (105, 350),
                (110, 400), (115, 450), (120, 480), (125, 520), (130, 540),
                (140, 560), (160, 570), (180, 575), (200, 570), (220, 560), (240, 550),
                (260, 545), (280, 540), (300, 540), (320, 545), (340, 555), (360, 570),
                (380, 580), (400, 575), (420, 560), (440, 540), (460, 520), (480, 500),
                (500, 480), (510, 450), (515, 420), (520, 380), (525, 340), (530, 300),
                (540, 260), (550, 220), (560, 180), (570, 140), (580, 100),
                (570, 80), (550, 75), (530, 72), (510, 70), (490, 68), (470, 67),
                (450, 68), (430, 72), (410, 78), (390, 85), (370, 90), (350, 92),
                (330, 90), (310, 85), (290, 82), (270, 80), (250, 82), (230, 85),
                (210, 90), (190, 92), (170, 90), (150, 85), (130, 80), (110, 78), (90, 82), (80, 90), (80, 100)
            ]
            
            draw.polygon(africa_coastline, outline=(200, 200, 200), fill=(245, 245, 245), width=2)
            
            niger_polygon = [
                (280, 200), (380, 210), (390, 270), (380, 280), (280, 275), (270, 220), (280, 200)
            ]
            draw.polygon(niger_polygon, outline=(200, 50, 50), fill=(220, 50, 50), width=3)
            
            self.map_img = img
        
        return self.map_img
    
    def save_map(self, filepath):
        """Save generated map image."""
        if self.map_img is None:
            self.create_detailed_africa_map()
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.map_img.save(filepath)
        self.image_path = filepath
        print(f"OK: Africa map saved: {filepath}")
        return filepath
    
    def extract_drone_coordinates(self, num_drones=1000, sampling_mode='contour'):
        """
        Extract drone coordinates from map using contour detection.
        
        Args:
            num_drones: Target number of drones
            sampling_mode: 'contour' for edge sampling, 'fill' for area filling
            
        Returns:
            positions: (N, 3) array of drone positions
            colors: (N, 3) array of RGB colors
        """
        if self.map_img is None:
            self.create_detailed_africa_map()
        
        # Convert to numpy array for processing
        img_array = np.array(self.map_img)
        
        # === DETECT REGIONS ===
        # Africa (light gray, ~245)
        africa_mask = (img_array[:, :, 0] > 240) & \
                     (img_array[:, :, 1] > 240) & \
                     (img_array[:, :, 2] > 240)
        
        # Niger (red/orange, R>200, G<100, B<100)
        niger_mask = (img_array[:, :, 0] > 200) & \
                    (img_array[:, :, 1] < 100) & \
                    (img_array[:, :, 2] < 100)
        
        # Get coordinates
        africa_coords = np.column_stack(np.where(africa_mask))
        niger_coords = np.column_stack(np.where(niger_mask))
        
        # Also get contours/edges
        africa_edges = self._get_contour_points(africa_mask)
        
        positions = []
        colors = []
        
        # === SAMPLE AFRICA OUTLINE (70% of drones) ===
        num_africa = int(num_drones * 0.7)
        
        if len(africa_edges) > 0:
            if len(africa_edges) > num_africa:
                indices = np.random.choice(len(africa_edges), num_africa, replace=False)
                africa_sample = africa_edges[indices]
            else:
                africa_sample = africa_edges
                # If not enough edges, add some interior points
                if len(africa_sample) < num_africa:
                    remaining = num_africa - len(africa_sample)
                    interior_indices = np.random.choice(len(africa_coords), remaining, replace=False)
                    interior_points = africa_coords[interior_indices]
                    africa_sample = np.vstack([africa_sample, interior_points])
            
            # Convert pixel coords to 3D world space
            africa_3d = self._pixel_to_3d(africa_sample)
            positions.append(africa_3d)
            colors.append(np.tile([0.95, 0.95, 1.0], (len(africa_sample), 1)))  # White/star color
        
        # === SAMPLE NIGER (30% of drones) ===
        num_niger = int(num_drones * 0.3)
        
        if len(niger_coords) > 0:
            if len(niger_coords) > num_niger:
                indices = np.random.choice(len(niger_coords), num_niger, replace=False)
                niger_sample = niger_coords[indices]
            else:
                niger_sample = niger_coords
            
            # Convert to 3D
            niger_3d = self._pixel_to_3d(niger_sample)
            positions.append(niger_3d)
            colors.append(np.tile([1.0, 0.2, 0.2], (len(niger_sample), 1)))  # Red
        
        # Combine and normalize
        if positions:
            all_positions = np.vstack(positions)
            all_colors = np.vstack(colors)
            
            # Pad or trim to exact num_drones
            current_num = len(all_positions)
            if current_num < num_drones:
                padding = num_drones - current_num
                all_positions = np.vstack([
                    all_positions,
                    np.zeros((padding, 3), dtype=np.float32)
                ])
                all_colors = np.vstack([
                    all_colors,
                    np.zeros((padding, 3), dtype=np.float32)
                ])
            elif current_num > num_drones:
                all_positions = all_positions[:num_drones]
                all_colors = all_colors[:num_drones]
            
            return all_positions.astype(np.float32), all_colors.astype(np.float32)
        
        return np.zeros((num_drones, 3), dtype=np.float32), np.zeros((num_drones, 3), dtype=np.float32)
    
    def _get_contour_points(self, mask):
        """Extract contour points from binary mask."""
        # Find edges using morphological operations
        from scipy.ndimage import binary_erosion
        
        eroded = binary_erosion(mask, iterations=1)
        edges = mask & ~eroded
        
        # Get coordinates of edge pixels
        edge_coords = np.column_stack(np.where(edges))
        
        if len(edge_coords) == 0:
            # If no edges, return some points from the mask
            edge_coords = np.column_stack(np.where(mask))
        
        return edge_coords
    
    def _pixel_to_3d(self, pixel_coords):
        """Convert pixel coordinates to 3D world coordinates."""
        # pixel_coords shape: (N, 2) with values [row, col]
        # Convert to [-100, 100] range
        
        y_pixel = pixel_coords[:, 0]  # row
        x_pixel = pixel_coords[:, 1]  # col
        
        # Normalize to [-100, 100]
        x_3d = (x_pixel / self.width - 0.5) * 200
        z_3d = (y_pixel / self.height - 0.5) * 200
        y_3d = np.full(len(pixel_coords), 50, dtype=np.float32)  # Height above ground
        
        return np.column_stack([x_3d, y_3d, z_3d]).astype(np.float32)
    
    def get_zoom_formation(self, positions, colors, zoom_center=None, zoom_factor=2.0):
        """
        Apply zoom transformation.
        
        Args:
            positions: Current drone positions
            colors: Drone colors
            zoom_center: Center point for zoom (default: origin)
            zoom_factor: Zoom multiplier
            
        Returns:
            zoomed_positions, colors
        """
        if zoom_center is None:
            zoom_center = np.array([0, 50, 0], dtype=np.float32)
        else:
            zoom_center = np.array(zoom_center, dtype=np.float32)
        
        # Vector from each drone to center
        vectors = zoom_center - positions
        
        # Zoom: move toward center
        zoomed = positions + vectors * (1 - 1/zoom_factor)
        
        return zoomed.astype(np.float32), colors


# Example usage
if __name__ == "__main__":
    generator = AfricaMapGenerator(width=800, height=600, scale=0.9)
    
    # Generate and save map
    generator.create_detailed_africa_map()
    map_path = r"e:\Hama\DRONES-3D-ANEM-2025\data\assets\africa_map.png"
    generator.save_map(map_path)
    
    # Extract drone coordinates
    positions, colors = generator.extract_drone_coordinates(num_drones=1000)
    print(f"OK: Extracted {len(positions)} drone positions")
    print(f"OK: Positions shape: {positions.shape}")
    print(f"OK: X range: [{positions[:, 0].min():.1f}, {positions[:, 0].max():.1f}]")
    print(f"OK: Z range: [{positions[:, 2].min():.1f}, {positions[:, 2].max():.1f}]")
    
    # Count white/red
    white = np.sum((colors[:, 0] > 0.8) & (colors[:, 1] > 0.8))
    red = np.sum((colors[:, 0] > 0.9) & (colors[:, 1] < 0.3))
    black = np.sum(np.all(colors < 0.1, axis=1))
    
    print(f"OK: White drones: {white}")
    print(f"OK: Red drones: {red}")
    print(f"OK: Black drones: {black}")

    """Generate Africa map with Niger highlighted for drone formations."""
    
    def __init__(self, width=400, height=400, scale=0.8):
        """
        Initialize Africa map generator.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            scale: Scale factor for map (0-1)
        """
        self.width = width
        self.height = height
        self.scale = scale
        self.image_path = None
        self.map_img = None
        self.niger_mask = None
        
    def generate_africa_map(self):
        """Generate Africa map image with Niger highlighted."""
        # Create image with black background
        img = Image.new('RGB', (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Simplified Africa outline (normalized coordinates, then scaled)
        # This is a highly simplified polygon - in production, use proper GeoJSON data
        africa_outline = [
            # North Coast
            (0.2, 0.15), (0.3, 0.1), (0.4, 0.08), (0.5, 0.1), (0.6, 0.12), (0.7, 0.15),
            # East Coast (Red Sea)
            (0.75, 0.2), (0.78, 0.3), (0.8, 0.4),
            # East Coast (Indian Ocean)
            (0.82, 0.5), (0.85, 0.6), (0.83, 0.7), (0.78, 0.8), (0.72, 0.85),
            # South Africa
            (0.6, 0.88), (0.5, 0.9), (0.4, 0.88), (0.35, 0.82),
            # Southwest
            (0.25, 0.8), (0.18, 0.75), (0.15, 0.6), (0.1, 0.5),
            # West Coast
            (0.08, 0.4), (0.05, 0.3), (0.08, 0.2), (0.15, 0.15), (0.2, 0.15)
        ]
        
        # Scale and center the outline
        center_x, center_y = self.width / 2, self.height / 2
        offset_x = center_x - (self.width * self.scale) / 2
        offset_y = center_y - (self.height * self.scale) / 2
        
        scaled_outline = [
            (offset_x + x * self.width * self.scale, offset_y + y * self.height * self.scale)
            for x, y in africa_outline
        ]
        
        # Draw Africa outline in white
        draw.polygon(scaled_outline, outline=(255, 255, 255), fill=None, width=3)
        
        # Draw Niger region (simplified, in red)
        # Niger is in West-Central Africa, approximately at (0.35, 0.35) normalized
        niger_bounds = self._get_niger_bounds()
        draw.rectangle(niger_bounds, outline=(255, 0, 0), fill=(255, 0, 0, 100), width=2)
        
        # Draw simplified country borders (thin white lines)
        self._draw_country_borders(draw, scaled_outline)
        
        self.map_img = img
        return img
    
    def _get_niger_bounds(self):
        """Get bounding box for Niger region (West-Central Africa)."""
        # Niger normalized bounds: roughly (0.3, 0.2) to (0.5, 0.4)
        center_x, center_y = self.width / 2, self.height / 2
        offset_x = center_x - (self.width * self.scale) / 2
        offset_y = center_y - (self.height * self.scale) / 2
        
        x_min = offset_x + 0.30 * self.width * self.scale
        x_max = offset_x + 0.50 * self.width * self.scale
        y_min = offset_y + 0.25 * self.height * self.scale
        y_max = offset_y + 0.45 * self.height * self.scale
        
        return [x_min, y_min, x_max, y_max]
    
    def _draw_country_borders(self, draw, africa_outline):
        """Draw simplified country borders within Africa."""
        # Simplified borders - in production, use proper GeoJSON
        border_lines = [
            # Sahel region borders
            [(0.25, 0.2), (0.75, 0.25)],  # North border
            # East-West divisions
            [(0.5, 0.2), (0.5, 0.8)],  # Central vertical
        ]
        
        center_x, center_y = self.width / 2, self.height / 2
        offset_x = center_x - (self.width * self.scale) / 2
        offset_y = center_y - (self.height * self.scale) / 2
        
        for line in border_lines:
            scaled_line = [
                (offset_x + x * self.width * self.scale, offset_y + y * self.height * self.scale)
                for x, y in line
            ]
            draw.line(scaled_line, fill=(200, 200, 200), width=1)
    
    def save_map(self, filepath):
        """Save generated map image."""
        if self.map_img is None:
            self.generate_africa_map()
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.map_img.save(filepath)
        self.image_path = filepath
        print(f"Africa map saved: {filepath}")
        return filepath
    
    def extract_drone_coordinates(self, num_drones=1000, sampling_mode='grid'):
        """
        Extract drone coordinates from map image.
        
        Args:
            num_drones: Target number of drones
            sampling_mode: 'grid' for regular grid, 'random' for random sampling
            
        Returns:
            positions: (N, 3) array of drone positions
            colors: (N, 3) array of RGB colors
        """
        if self.map_img is None:
            self.generate_africa_map()
        
        # Create a custom map with simple geometry for testing
        # This is a simpler approach that's guaranteed to work
        
        positions = []
        colors = []
        
        # === AFRICA OUTLINE (White drones) ===
        # Create a simplified Africa shape with polygonal sampling
        africa_points = self._generate_africa_outline_points(num_drones * 0.7)
        positions.append(africa_points)
        colors.append(np.tile([1, 1, 1], (len(africa_points), 1)))  # White
        
        # === NIGER REGION (Red drones) ===
        # Niger is in West-Central Africa, create a red rectangular region
        niger_points = self._generate_niger_points(num_drones * 0.3)
        positions.append(niger_points)
        colors.append(np.tile([1, 0, 0], (len(niger_points), 1)))  # Red
        
        # Concatenate all positions and colors
        if positions:
            all_positions = np.vstack(positions)
            all_colors = np.vstack(colors)
            
            # Pad or trim to exact num_drones
            current_num = len(all_positions)
            if current_num < num_drones:
                # Pad with black drones at origin
                padding = num_drones - current_num
                all_positions = np.vstack([
                    all_positions,
                    np.zeros((padding, 3))
                ])
                all_colors = np.vstack([
                    all_colors,
                    np.zeros((padding, 3))
                ])
            elif current_num > num_drones:
                # Trim
                all_positions = all_positions[:num_drones]
                all_colors = all_colors[:num_drones]
            
            return all_positions, all_colors
        else:
            # Return zeros if no pixels found
            return np.zeros((num_drones, 3)), np.zeros((num_drones, 3))
    
    def _generate_africa_outline_points(self, num_points):
        """Generate points forming simplified Africa outline."""
        num_points = int(num_points)
        
        # Simplified Africa boundary (normalized to -100/100 range for 3D)
        # These represent key points around Africa's coastline
        africa_outline_normalized = [
            # Northwest corner
            (-60, 60), (-50, 70), (-40, 80),
            # North coast
            (-20, 85), (0, 85), (20, 80), (40, 75),
            # Northeast (Red Sea)
            (50, 60), (60, 40),
            # East coast
            (70, 20), (75, 0), (70, -20), (60, -40),
            # Southeast
            (50, -60), (30, -70), (10, -75),
            # Southwest
            (-10, -70), (-30, -60), (-50, -50),
            # West coast
            (-70, -40), (-75, -20), (-70, 0), (-60, 20), (-60, 40)
        ]
        
        # Sample points along the outline
        from scipy.interpolate import interp1d
        
        # Convert to array
        outline = np.array(africa_outline_normalized)
        
        # Create parametric curve
        t_in = np.linspace(0, 1, len(outline))
        t_out = np.linspace(0, 1, num_points)
        
        # Interpolate X and Z coordinates
        x_interp = interp1d(t_in, outline[:, 0], kind='cubic', fill_value='extrapolate')
        z_interp = interp1d(t_in, outline[:, 1], kind='cubic', fill_value='extrapolate')
        
        x_points = x_interp(t_out)
        z_points = z_interp(t_out)
        y_points = np.full(num_points, 50)  # Height
        
        return np.column_stack([x_points, y_points, z_points]).astype(np.float32)
    
    def _generate_niger_points(self, num_points):
        """Generate points forming Niger region (red zone)."""
        num_points = int(num_points)
        
        # Niger is approximately in the center-west of Africa
        # Define a rectangular region
        niger_center_x = -10.0
        niger_center_z = 20.0
        niger_width = 30.0
        niger_height = 30.0
        
        # Generate random points within Niger bounds
        x_min = niger_center_x - niger_width / 2
        x_max = niger_center_x + niger_width / 2
        z_min = niger_center_z - niger_height / 2
        z_max = niger_center_z + niger_height / 2
        
        # Create a grid of points
        grid_side = int(np.sqrt(num_points))
        x_points = np.linspace(x_min, x_max, grid_side)
        z_points = np.linspace(z_min, z_max, grid_side)
        
        xx, zz = np.meshgrid(x_points, z_points)
        x_flat = xx.flatten()[:num_points]
        z_flat = zz.flatten()[:num_points]
        y_flat = np.full(len(x_flat), 50)
        
        # Add some random noise for organic look
        x_flat += np.random.uniform(-2, 2, len(x_flat))
        z_flat += np.random.uniform(-2, 2, len(z_flat))
        
        return np.column_stack([x_flat, y_flat, z_flat]).astype(np.float32)
    
    def get_niger_zoom_formation(self, positions, colors, zoom_factor=1.5):
        """
        Zoom transformation toward Niger center.
        
        Args:
            positions: Current drone positions
            colors: Current drone colors
            zoom_factor: How much to zoom (1.5 = 50% closer)
            
        Returns:
            zoomed_positions: Positions zoomed toward Niger
            colors: Same colors
        """
        # Niger center (approximate)
        niger_center = np.array([0, 50, 0])
        
        # Vector from each drone to Niger center
        vectors = niger_center - positions
        
        # Zoom: move drones closer to Niger center
        zoomed = positions + vectors * (1 - 1/zoom_factor)
        
        return zoomed, colors


# Example usage
if __name__ == "__main__":
    generator = AfricaMapGenerator(width=400, height=400, scale=0.8)
    
    # Generate and save map
    generator.generate_africa_map()
    map_path = r"e:\Hama\DRONES-3D-ANEM-2025\data\assets\africa_map.png"
    generator.save_map(map_path)
    
    # Extract drone coordinates
    positions, colors = generator.extract_drone_coordinates(num_drones=1000)
    print(f"Extracted {len(positions)} drone positions")
    print(f"Positions shape: {positions.shape}")
    print(f"Colors shape: {colors.shape}")
    print(f"Sample position: {positions[0]}")
    print(f"Sample color: {colors[0]}")
