import numpy as np
from PIL import Image, ImageDraw, ImageFont

class PPPGraphics:
    """Pixel-Perfect-Performance Graphics Engine for LED matrices"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # RGB buffer: shape (height, width, 3)
        self.buffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.image = Image.new('RGB', (width, height), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
    
    def clear(self, color=(0, 0, 0)):
        """Clear the buffer to a specific color"""
        self.buffer[:] = color
        self.image = Image.new('RGB', (self.width, self.height), color)
        self.draw = ImageDraw.Draw(self.image)
    
    def set_pixel(self, x, y, color):
        """Set a single pixel color (x, y, RGB tuple)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y, x] = color
    
    def get_pixel(self, x, y):
        """Get a single pixel color"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.buffer[y, x])
        return (0, 0, 0)
    
    def draw_line(self, x0, y0, x1, y1, color):
        """Draw a line using Bresenham's algorithm"""
        self.draw.line([(x0, y0), (x1, y1)], fill=color, width=1)
        self._sync_from_image()
    
    def draw_rect(self, x, y, w, h, color, fill=False):
        """Draw a rectangle"""
        if fill:
            self.draw.rectangle([x, y, x+w-1, y+h-1], fill=color)
        else:
            self.draw.rectangle([x, y, x+w-1, y+h-1], outline=color)
        self._sync_from_image()
    
    def draw_circle(self, x, y, radius, color, fill=False):
        """Draw a circle"""
        bbox = [x-radius, y-radius, x+radius, y+radius]
        if fill:
            self.draw.ellipse(bbox, fill=color)
        else:
            self.draw.ellipse(bbox, outline=color)
        self._sync_from_image()
    
    def draw_text(self, text, x, y, color, font_size=8):
        """Draw text on the display"""
        try:
            # Try to use a proper font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        self.draw.text((x, y), text, fill=color, font=font)
        self._sync_from_image()
    
    def fill(self, color):
        """Fill entire display with color"""
        self.clear(color)
    
    def blend(self, other_buffer, alpha=0.5):
        """Alpha blend another buffer onto this one"""
        self.buffer = (self.buffer * (1 - alpha) + other_buffer * alpha).astype(np.uint8)
    
    def dim(self, factor=0.9):
        """Dim the entire buffer by a factor (0.0 to 1.0)"""
        self.buffer = (self.buffer * factor).astype(np.uint8)
    
    def _sync_from_image(self):
        """Sync the numpy buffer from the PIL image"""
        self.buffer = np.array(self.image)
    
    def _sync_to_image(self):
        """Sync the PIL image from the numpy buffer"""
        self.image = Image.fromarray(self.buffer)
        self.draw = ImageDraw.Draw(self.image)
    
    def get_buffer_copy(self):
        """Return a copy of the current buffer"""
        return self.buffer.copy()
    
    def set_buffer(self, buffer):
        """Set the buffer from an external numpy array"""
        if buffer.shape == self.buffer.shape:
            self.buffer = buffer.copy()
            self._sync_to_image()
