# 1. THESE TWO LINES MUST BE AT THE VERY TOP (Before any other imports)
from app import create_app, socketio
import os
import sys

# 1. Detect if we are running on a Server (Linux) or Local (Windows)
IS_WINDOWS = sys.platform.startswith('win')

# 2. Only use Eventlet if we are NOT on Windows
if not IS_WINDOWS:
    import eventlet
    eventlet.monkey_patch()


app = create_app()

if __name__ == '__main__':
    if IS_WINDOWS:
        # --- WINDOWS MODE (Safe for your Laptop) ---
        print("----------------------------------------------------------------")
        print("💻 LOCAL WINDOWS DETECTED: Using Standard Threading")
        print("👉 Open: http://127.0.0.1:5000")
        print("----------------------------------------------------------------")
        socketio.run(app, host='0.0.0.0', port=5000,
                     debug=True, allow_unsafe_werkzeug=True)
    else:
        # --- SERVER MODE (Fast for Deployment) ---
        print("🚀 LINUX SERVER DETECTED: Using Eventlet")
        socketio.run(app, host='0.0.0.0', port=5000)
