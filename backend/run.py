# 1. THESE TWO LINES MUST BE AT THE VERY TOP (Before any other imports)
import eventlet
eventlet.monkey_patch()

# 2. Now import the rest
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Use socketio.run instead of app.run
    socketio.run(app, host='0.0.0.0', port=5000)

