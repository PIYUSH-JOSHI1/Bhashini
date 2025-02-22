import speech_recognition as sr
from google.cloud import speech_v1
from google.cloud import translate_v2
import pyaudio
import wave
import threading
import queue
import os
from datetime import datetime

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.speech_client = speech_v1.SpeechClient()
        self.translate_client = translate_v2.Client()
        self.audio_queue = queue.Queue()
        self.is_recording = False
        
        # Audio recording settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
    def start_recording(self):
        """Start recording audio"""
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join()
            
    def _record_audio(self):
        """Record audio in chunks and add to queue"""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)
        
        while self.is_recording:
            data = stream.read(self.CHUNK)
            self.audio_queue.put(data)
            
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    def process_audio(self, target_language='en'):
        """Process audio chunks and return transcription"""
        # Collect audio data from queue
        audio_data = b''
        while not self.audio_queue.empty():
            audio_data += self.audio_queue.get()
            
        if not audio_data:
            return None
            
        # Save temporary audio file
        temp_filename = f"temp_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(audio_data)
            
        # Perform speech recognition
        try:
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                
                # Translate if needed
                if target_language != 'en':
                    translation = self.translate_client.translate(
                        text,
                        target_language=target_language
                    )
                    text = translation['translatedText']
                    
                return text
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)