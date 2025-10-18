import threading
import time
import numpy as np
from scipy.ndimage import gaussian_filter

class PPPAnimator:
    """Pixel-Perfect-Performance Animator for LED effects"""
    
    def __init__(self, graphics_engine):
        self.graphics = graphics_engine
        self.running = False
        self.current_effect = None
        self.thread = None
        self.fps = 30
        self.frame_time = 1.0 / self.fps
        self.effect_speed = 1.0
        self.frame_count = 0
        
        # Effect state
        self.effect_state = {}
    
    def start_effect(self, effect_name, speed=1.0):
        """Start an animation effect"""
        self.stop_effect()
        self.current_effect = effect_name
        self.effect_speed = speed
        self.frame_count = 0
        self.effect_state = {}
        self.running = True
        
        # Initialize effect-specific state
        self._init_effect_state(effect_name)
        
        self.thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.thread.start()
    
    def stop_effect(self):
        """Stop the current animation"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.current_effect = None
    
    def _animation_loop(self):
        """Main animation loop"""
        while self.running:
            start_time = time.time()
            
            # Render the current effect
            if self.current_effect:
                self._render_effect(self.current_effect)
            
            # Update display (subclass should override)
            self._update_display()
            
            self.frame_count += 1
            
            # Frame rate limiting
            elapsed = time.time() - start_time
            sleep_time = self.frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _update_display(self):
        """Override this in subclass to update hardware display"""
        pass
    
    def _init_effect_state(self, effect_name):
        """Initialize state for specific effects"""
        if effect_name == 'fire':
            self.effect_state['heat'] = np.zeros(self.graphics.width, dtype=float)
        elif effect_name == 'stars':
            num_stars = 50
            self.effect_state['stars'] = {
                'x': np.random.rand(num_stars) * self.graphics.width,
                'y': np.random.rand(num_stars) * self.graphics.height,
                'speed': np.random.rand(num_stars) * 2 + 0.5,
                'brightness': np.random.rand(num_stars)
            }
        elif effect_name == 'matrix':
            self.effect_state['drops'] = []
            for _ in range(20):
                self.effect_state['drops'].append({
                    'x': np.random.randint(0, self.graphics.width),
                    'y': np.random.randint(-20, 0),
                    'speed': np.random.randint(1, 4),
                    'length': np.random.randint(5, 15)
                })
    
    def _render_effect(self, effect_name):
        """Render the specified effect"""
        effect_map = {
            'rainbow': self._effect_rainbow,
            'fire': self._effect_fire,
            'matrix': self._effect_matrix,
            'stars': self._effect_stars,
            'pulse': self._effect_pulse,
            'scanner': self._effect_scanner
        }
        
        if effect_name in effect_map:
            effect_map[effect_name]()
    
    def _effect_rainbow(self):
        """Rainbow wave effect"""
        for x in range(self.graphics.width):
            for y in range(self.graphics.height):
                hue = (x + self.frame_count * self.effect_speed) % self.graphics.width
                hue = hue / self.graphics.width * 360
                rgb = self._hsv_to_rgb(hue, 1.0, 1.0)
                self.graphics.set_pixel(x, y, rgb)
    
    def _effect_fire(self):
        """Realistic fire effect"""
        width = self.graphics.width
        height = self.graphics.height
        heat = self.effect_state['heat']
        
        # Cool down
        heat *= 0.85
        
        # Add random heat at bottom
        for x in range(width):
            if np.random.rand() < 0.3:
                heat[x] = min(255, heat[x] + np.random.randint(100, 200))
        
        # Create fire buffer
        fire_buffer = np.zeros((height, width, 3), dtype=np.uint8)
        
        for x in range(width):
            for y in range(height):
                # Height affects intensity
                intensity = heat[x] * (1.0 - y / height)
                intensity = int(np.clip(intensity, 0, 255))
                
                # Fire colors: red -> yellow -> white
                if intensity < 85:
                    r = intensity * 3
                    g = 0
                    b = 0
                elif intensity < 170:
                    r = 255
                    g = (intensity - 85) * 3
                    b = 0
                else:
                    r = 255
                    g = 255
                    b = (intensity - 170) * 3
                
                fire_buffer[y, x] = (r, g, b)
        
        # Blur for smooth effect
        for c in range(3):
            fire_buffer[:, :, c] = gaussian_filter(fire_buffer[:, :, c], sigma=0.8)
        
        self.graphics.buffer[:] = fire_buffer
    
    def _effect_matrix(self):
        """Matrix digital rain effect"""
        self.graphics.dim(0.85)
        
        for drop in self.effect_state['drops']:
            # Draw the drop
            for i in range(drop['length']):
                y = int(drop['y'] - i)
                if 0 <= y < self.graphics.height:
                    brightness = int(255 * (1 - i / drop['length']))
                    self.graphics.set_pixel(drop['x'], y, (0, brightness, 0))
            
            # Update position
            drop['y'] += drop['speed'] * self.effect_speed
            
            # Reset if off screen
            if drop['y'] > self.graphics.height + drop['length']:
                drop['x'] = np.random.randint(0, self.graphics.width)
                drop['y'] = -drop['length']
    
    def _effect_stars(self):
        """Parallax starfield effect"""
        self.graphics.clear()
        stars = self.effect_state['stars']
        
        for i in range(len(stars['x'])):
            # Update position
            stars['y'][i] += stars['speed'][i] * self.effect_speed
            
            # Wrap around
            if stars['y'][i] > self.graphics.height:
                stars['y'][i] = 0
                stars['x'][i] = np.random.rand() * self.graphics.width
            
            # Draw star
            x = int(stars['x'][i])
            y = int(stars['y'][i])
            brightness = int(stars['brightness'][i] * 255)
            
            # Twinkle effect
            stars['brightness'][i] = 0.5 + 0.5 * np.sin(self.frame_count * 0.1 + i)
            
            self.graphics.set_pixel(x, y, (brightness, brightness, brightness))
    
    def _effect_pulse(self):
        """Breathing pulse effect"""
        # Sine wave breathing
        intensity = (np.sin(self.frame_count * 0.1 * self.effect_speed) + 1) / 2
        intensity = int(intensity * 255)
        
        # Cyan pulse
        color = (0, intensity, intensity)
        self.graphics.fill(color)
    
    def _effect_scanner(self):
        """Radar scanner effect"""
        self.graphics.dim(0.9)
        
        angle = (self.frame_count * 3 * self.effect_speed) % 360
        angle_rad = np.radians(angle)
        
        center_x = self.graphics.width // 2
        center_y = self.graphics.height // 2
        
        # Draw scanner line
        length = max(self.graphics.width, self.graphics.height)
        end_x = int(center_x + length * np.cos(angle_rad))
        end_y = int(center_y + length * np.sin(angle_rad))
        
        self.graphics.draw_line(center_x, center_y, end_x, end_y, (0, 255, 0))
        
        # Draw center dot
        self.graphics.set_pixel(center_x, center_y, (255, 255, 255))
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB"""
        h = h / 60.0
        i = int(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        
        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def get_available_effects(self):
        """Return list of available effects"""
        return [
            {'name': 'rainbow', 'description': 'Smooth rainbow waves', 'icon': '🌈'},
            {'name': 'fire', 'description': 'Realistic fire simulation', 'icon': '🔥'},
            {'name': 'stars', 'description': 'Parallax starfield', 'icon': '⭐'},
            {'name': 'matrix', 'description': 'Digital rain', 'icon': '💚'},
            {'name': 'pulse', 'description': 'Breathing glow', 'icon': '💙'},
            {'name': 'scanner', 'description': 'Radar sweep', 'icon': '📡'}
        ]
