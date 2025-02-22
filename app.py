from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
from services.speech_service import SpeechService
import base64
from threading import Thread
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
speech_service = SpeechService()

# Store active translation sessions
active_sessions = {}

@app.route('/')
def index():
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'mr': 'Marathi',
        'hi': 'Hindi'
    }
    return render_template('index.html', languages=SUPPORTED_LANGUAGES)

@app.route('/emergency-alerts')
def emergency_alerts():
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'mr': 'Marathi',
        'hi': 'Hindi'
    }
    return render_template('emergency-alerts.html', languages=SUPPORTED_LANGUAGES)

@app.route('/live-translation')
def live_translation():
    return render_template('live-translation.html')

@socketio.on('start_translation')
def handle_translation_start(data):
    """Handle start of translation session"""
    session_id = data.get('session_id')
    target_language = data.get('target_language', 'en')
    
    active_sessions[session_id] = {
        'target_language': target_language,
        'is_active': True
    }
    
    # Start speech recognition
    speech_service.start_recording()
    
    # Start processing thread
    def process_audio():
        while active_sessions.get(session_id, {}).get('is_active', False):
            text = speech_service.process_audio(target_language)
            if text:
                emit('translation_result', {
                    'session_id': session_id,
                    'text': text,
                    'timestamp': time.time()
                })
            time.sleep(1)  # Process every second
            
    Thread(target=process_audio).start()

@socketio.on('stop_translation')
def handle_translation_stop(data):
    """Handle end of translation session"""
    session_id = data.get('session_id')
    if session_id in active_sessions:
        active_sessions[session_id]['is_active'] = False
        speech_service.stop_recording()

@socketio.on('video_frame')
def handle_video_frame(data):
    """Handle incoming video frames"""
    session_id = data.get('session_id')
    frame_data = data.get('frame')
    
    # Decode base64 frame
    frame_bytes = base64.b64decode(frame_data.split(',')[1])
    np_arr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    # Process frame if needed (e.g., add overlays)
    # ... frame processing code ...
    
    # Encode and send back to client
    _, buffer = cv2.imencode('.jpg', frame)
    frame_data = base64.b64encode(buffer).decode('utf-8')
    
    emit('processed_frame', {
        'session_id': session_id,
        'frame': f'data:image/jpeg;base64,{frame_data}'
    })


if __name__ == '__main__':
    socketio.run(app, debug=True)