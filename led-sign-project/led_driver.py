import serial
import serial.tools.list_ports
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_led_panel():
    """Auto-detect LED panel USB port"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'USB' in port.description or 'Serial' in port.description:
            logger.info(f"Found potential LED panel at {port.device}")
            return port.device
    return None

class LEDDriver:
    """Real hardware LED driver"""
    def __init__(self, port=None, baudrate=115200):
        if port is None:
            port = find_led_panel()
        
        if port is None:
            raise RuntimeError("No LED panel found. Check USB connection.")
        
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for device to initialize
        logger.info(f"Connected to LED panel on {port}")
    
    def send_frame(self, buffer):
        """Send RGB buffer to LED panel"""
        try:
            # Flatten the buffer and send as bytes
            data = buffer.tobytes()
            self.serial.write(b'FRAME')
            self.serial.write(len(data).to_bytes(4, 'big'))
            self.serial.write(data)
        except Exception as e:
            logger.error(f"Error sending frame: {e}")
    
    def send_text(self, text):
        """Send text command to LED panel"""
        try:
            cmd = f"TEXT:{text}\n".encode('utf-8')
            self.serial.write(cmd)
        except Exception as e:
            logger.error(f"Error sending text: {e}")
    
    def set_brightness(self, level):
        """Set brightness (0-15)"""
        try:
            level = max(0, min(15, level))
            cmd = f"BRIGHT:{level}\n".encode('utf-8')
            self.serial.write(cmd)
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
    
    def clear(self):
        """Clear display"""
        try:
            self.serial.write(b'CLEAR\n')
        except Exception as e:
            logger.error(f"Error clearing display: {e}")
    
    def close(self):
        """Close serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Serial connection closed")

class MockLEDDriver:
    """Mock driver for testing without hardware"""
    def __init__(self):
        logger.info("Using MOCK LED driver (no hardware)")
        self.brightness = 7
        self.last_text = ""
    
    def send_frame(self, buffer):
        """Mock frame send"""
        pass  # Just accept the buffer silently
    
    def send_text(self, text):
        """Mock text send"""
        self.last_text = text
        logger.info(f"Mock: Would display text: {text}")
    
    def set_brightness(self, level):
        """Mock brightness set"""
        self.brightness = level
        logger.info(f"Mock: Brightness set to {level}")
    
    def clear(self):
        """Mock clear"""
        logger.info("Mock: Display cleared")
    
    def close(self):
        """Mock close"""
        pass

def create_led_driver(mock=False, port=None, baudrate=115200):
    """Factory function to create appropriate driver"""
    if mock:
        return MockLEDDriver()
    else:
        return LEDDriver(port=port, baudrate=baudrate)
