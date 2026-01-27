"""
Simplified Audio Manager for Sanskrit Voice Bot v2 (Web Deployment)
Handles audio transcription via Groq Whisper API
"""
import scipy.io.wavfile as wav
import numpy as np
import requests
import tempfile
from pathlib import Path
from typing import Dict, Any

from core.config import AudioConfig


class AudioManager:
    """Manages audio transcription for web deployment"""
    
    def __init__(self):
        """Initialize the AudioManager"""
        self._current_audio_data = None
        self._sample_rate = AudioConfig.SAMPLE_RATE
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize manager (no-op for web, but keeps interface compatible)"""
        self._initialized = True
        return True
    
    def transcribe_audio(self) -> Dict[str, Any]:
        """
        Transcribe the current audio using Groq Whisper API.
        
        Returns:
            Dict containing transcription result and status
        """
        if self._current_audio_data is None or len(self._current_audio_data) == 0:
            return {'success': False, 'error': 'No audio data available'}
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Normalize audio data
                audio_int16 = (self._current_audio_data * 32767).astype(np.int16)
                wav.write(temp_file.name, self._sample_rate, audio_int16)
                
                # Send to Groq API
                headers = {
                    'Authorization': f'Bearer {AudioConfig.GROQ_API_KEY}'
                }
                
                files = {
                    'file': (temp_file.name, open(temp_file.name, 'rb'), 'audio/wav'),
                    'model': (None, AudioConfig.WHISPER_MODEL),
                    'language': (None, 'hi'),  # Hindi for Devanagari support
                    'response_format': (None, 'json')
                }
                
                response = requests.post(AudioConfig.GROQ_API_URL, headers=headers, files=files)
                
                # Clean up temp file
                temp_file_path = Path(temp_file.name)
                if temp_file_path.exists():
                    temp_file_path.unlink()
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'transcription': result.get('text', '').strip()
                    }
                else:
                    return {
                        'success': False,
                        'error': f'API request failed: {response.status_code}'
                    }
        
        except Exception as e:
            return {'success': False, 'error': f'Transcription error: {str(e)}'}
