# live_translation_system.py

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import cv2
import numpy as np
from transformers import MBartForConditionalGeneration, MBartTokenizer
import torch
import mediapipe as mp
from threading import Lock

@dataclass
class TranslationSession:
    session_id: str
    source_lang: str
    target_lang: str
    start_time: datetime
    is_active: bool = True
    translation_history: List[Dict] = None

    def __post_init__(self):
        self.translation_history = []

class LiveTranslationSystem:
    def __init__(self):
        self.sessions: Dict[str, TranslationSession] = {}
        self.session_lock = Lock()
        
        # Initialize translation model
        self.model_name = "facebook/mbart-large-50-many-to-many-mmt"
        self.tokenizer = MBartTokenizer.from_pretrained(self.model_name)
        self.model = MBartForConditionalGeneration.from_pretrained(self.model_name)
        
        # Use GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Initialize MediaPipe for face detection and speech recognition
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        
        # Initialize OpenCV video capture
        self.video_capture = None
        
        # Language codes mapping
        self.language_codes = {
            'en': 'en_XX',
            'hi': 'hi_IN',
            'mr': 'mr_IN',
            'ur': 'ur_PK'
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_session(self, session_id: str, source_lang: str, target_lang: str) -> bool:
        """Start a new translation session"""
        with self.session_lock:
            if session_id in self.sessions:
                self.logger.warning(f"Session {session_id} already exists")
                return False
            
            try:
                session = TranslationSession(
                    session_id=session_id,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    start_time=datetime.now()
                )
                self.sessions[session_id] = session
                self.logger.info(f"Started new session: {session_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error starting session: {str(e)}")
                return False

    def end_session(self, session_id: str) -> bool:
        """End an existing translation session"""
        with self.session_lock:
            if session_id not in self.sessions:
                return False
            
            try:
                self.sessions[session_id].is_active = False
                self.logger.info(f"Ended session: {session_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error ending session: {str(e)}")
                return False

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using the mBART model"""
        try:
            # Get the correct language codes
            src_code = self.language_codes.get(source_lang, 'en_XX')
            tgt_code = self.language_codes.get(target_lang, 'en_XX')
            
            # Set the source language
            self.tokenizer.src_lang = src_code
            
            # Tokenize the input text
            encoded = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generate translation
            generated_tokens = self.model.generate(
                **encoded,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_code],
                max_length=128,
                num_beams=4,
                length_penalty=0.6
            )
            
            # Decode the generated tokens
            translation = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
            return translation
        except Exception as e:
            self.logger.error(f"Translation error: {str(e)}")
            return text

    def process_video_frame(self, session_id: str, frame_data: np.ndarray) -> Optional[Dict]:
        """Process video frame and return translation results"""
        if session_id not in self.sessions or not self.sessions[session_id].is_active:
            return None
            
        try:
            session = self.sessions[session_id]
            
            # Convert frame data to RGB
            frame_rgb = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
            
            # Detect faces in the frame
            face_results = self.face_detection.process(frame_rgb)
            
            # If faces detected, process for lip movement
            if face_results.detections:
                # Here you would typically implement lip movement detection
                # For this example, we'll simulate with sample text
                detected_text = self._simulate_speech_to_text()
                
                if detected_text:
                    # Translate the detected text
                    translation = self.translate_text(
                        detected_text,
                        session.source_lang,
                        session.target_lang
                    )
                    
                    # Create translation record
                    translation_record = {
                        'timestamp': datetime.now().isoformat(),
                        'original': detected_text,
                        'translation': translation
                    }
                    
                    # Add to session history
                    session.translation_history.append(translation_record)
                    
                    return translation_record
                    
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return None

    def get_session_history(self, session_id: str) -> List[Dict]:
        """Retrieve translation history for a session"""
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id].translation_history

    def _simulate_speech_to_text(self) -> Optional[str]:
        """Simulate speech-to-text conversion for testing"""
        sample_texts = [
            "आज की बैठक में आपका स्वागत है",
            "कृपया अपने सवाल चैट बॉक्स में टाइप करें",
            "धन्यवाद आपके समय के लिए"
        ]
        return np.random.choice(sample_texts) if np.random.random() < 0.3 else None

    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.video_capture:
                self.video_capture.release()
            
            # End all active sessions
            with self.session_lock:
                for session in self.sessions.values():
                    session.is_active = False
            
            # Clear face detection
            self.face_detection.close()
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")