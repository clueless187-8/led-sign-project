from flask import Flask, request, jsonify
from flask_cors import CORS
from graphics.ppp_engine import PPPGraphics
from graphics.ppp_animator import PPPAnimator
from led_driver import create_led_driver

app = Flask(__name__)
CORS(app)

print("Initializing LED Sign System...")
graphics = PPPGraphics(96, 16)
USE_MOCK = True  # Set False for real hardware
led_driver = create_led_driver(mock=USE_MOCK)

class LEDAnimator(PPPAnimator):
    def __init__(self, graphics_engine, led_driver):
        super().__init__(graphics_engine)
        self.led_driver = led_driver
    
    def _update_display(self):
        self.led_driver.send_frame(self.graphics.buffer)

animator = LEDAnimator(graphics, led_driver)

@app.route('/api/ppp/effect', methods=['POST'])
def start_effect():
    try:
        data = request.json
        effect_name = data.get('effect', 'rainbow')
        speed = data.get('speed', 1.0)
        animator.start_effect(effect_name, speed=speed)
        return jsonify({'status': 'success', 'effect': effect_name, 'speed': speed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ppp/stop', methods=['POST'])
def stop_effect():
    try:
        animator.stop_effect()
        graphics.clear()
        return jsonify({'status': 'stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ppp/effects', methods=['GET'])
def get_effects():
    return jsonify(animator.get_available_effects())

@app.route('/api/ppp/status', methods=['GET'])
def get_status():
    return jsonify({
        'running': animator.running,
        'current_effect': animator.current_effect,
        'fps': 30,
        'driver_connected': led_driver.serial.is_open if hasattr(led_driver, 'serial') else True,
        'mock_mode': USE_MOCK
    })

@app.route('/api/text', methods=['POST'])
def send_text():
    try:
        data = request.json
        text = data.get('text', 'Hello')
        led_driver.send_text(text)
        return jsonify({'status': 'success', 'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/brightness', methods=['POST'])
def set_brightness():
    try:
        level = request.json.get('level', 7)
        led_driver.set_brightness(level)
        return jsonify({'status': 'success', 'brightness': level})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_display():
    try:
        animator.stop_effect()
        graphics.clear()
        led_driver.clear()
        return jsonify({'status': 'cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'led_sign'})

if __name__ == '__main__':
    print("=" * 50)
    print("LED Sign Server")
    print(f"Mock Mode: {USE_MOCK}")
    print(f"Effects: {len(animator.get_available_effects())}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
