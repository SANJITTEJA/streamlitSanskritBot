"""
Backend Integration for Streamlit App
Uses the SAME analysis logic as the tkinter application
"""
import tempfile
import requests
from pathlib import Path
from typing import Dict, Any
import sys
import numpy as np

# Add v2 to path for imports
v2_path = Path(__file__).parent.parent
sys.path.insert(0, str(v2_path))

from core.config import AudioConfig, AnalysisConfig
from audio.audio_manager import AudioManager
from analysis.feedback_generator import FeedbackGenerator


class StreamlitBackend:
    """Backend integration for Streamlit app"""
    
    def __init__(self):
        """Initialize backend components"""
        self.audio_manager = AudioManager()
        self.feedback_generator = FeedbackGenerator()
        self.audio_manager.initialize()
    
    def _generate_simple_feedback(self, accuracy: float) -> str:
        """Generate simple feedback based on accuracy"""
        if accuracy >= 90:
            return "Excellent pronunciation! Your chanting is very accurate."
        elif accuracy >= 70:
            return f"Good job! You achieved {accuracy:.1f}% accuracy."
        else:
            return f"Keep practicing! You achieved {accuracy:.1f}% accuracy."
    
    def transcribe_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Transcribe audio using the SAME method as tkinter app
        Uses AudioManager.transcribe_audio() logic
        """
        try:
            # Convert audio bytes to numpy array and load into AudioManager
            # This mimics what happens after recording in tkinter app
            import scipy.io.wavfile as wav
            from io import BytesIO
            
            # Read audio from bytes
            audio_io = BytesIO(audio_bytes)
            sample_rate, audio_data = wav.read(audio_io)
            
            # Convert to float32 format like AudioManager expects
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32767.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483647.0
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Set the audio data in AudioManager - SAME as tkinter app does after recording
            self.audio_manager._current_audio_data = audio_data
            self.audio_manager._sample_rate = sample_rate
            
            # Now call the SAME transcribe_audio method used in tkinter app
            transcription_result = self.audio_manager.transcribe_audio()
            
            return transcription_result
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Transcription error: {str(e)}'
            }
    
    def analyze_pronunciation(
        self, 
        user_audio_bytes: bytes,
        original_shloka: Dict[str, Any],
        practice_mode: str = 'full'
    ) -> Dict[str, Any]:
        """
        Analyze pronunciation by transcribing BOTH original and user audio
        Then comparing the two transcriptions - this ensures proper word splitting
        """
        try:
            # Step 1: Transcribe user's audio
            user_transcription_result = self.transcribe_audio(user_audio_bytes)
            if not user_transcription_result.get('success'):
                return {
                    'success': False,
                    'error': f"Failed to transcribe user audio: {user_transcription_result.get('error')}"
                }
            user_transcription = user_transcription_result.get('transcription', '').strip()
            
            # Step 2: Transcribe original audio from database (base64 encoded)
            original_audio_data = original_shloka.get('audio_data')
            original_audio_format = original_shloka.get('audio_format', 'mp3')
            
            if not original_audio_data:
                return {
                    'success': False,
                    'error': 'Original audio data not found in database'
                }
            
            # Decode base64 audio data
            import base64
            try:
                audio_bytes = base64.b64decode(original_audio_data)
            except Exception as decode_error:
                return {
                    'success': False,
                    'error': f"Failed to decode audio data: {str(decode_error)}"
                }
            
            # Transcribe original audio directly using Groq API
            try:
                headers = {
                    'Authorization': f'Bearer {AudioConfig.GROQ_API_KEY}'
                }
                
                files = {
                    'file': (f'original.{original_audio_format}', audio_bytes, f'audio/{original_audio_format}'),
                    'model': (None, AudioConfig.WHISPER_MODEL),
                    'language': (None, 'hi'),
                    'response_format': (None, 'json')
                }
                
                response = requests.post(
                    AudioConfig.GROQ_API_URL,
                    headers=headers,
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    original_transcription = result.get('text', '').strip()
                else:
                    return {
                        'success': False,
                        'error': f"Failed to transcribe original audio: HTTP {response.status_code}"
                    }
            except Exception as transcribe_error:
                return {
                    'success': False,
                    'error': f"Error transcribing original audio: {str(transcribe_error)}"
                }
            
            # Step 3: Now compare the two transcriptions
            # Split both transcriptions into words
            from utils.text_processor import TextProcessor
            text_processor = TextProcessor()
            
            original_words = text_processor.smart_word_split(original_transcription)
            user_words = text_processor.smart_word_split(user_transcription)
            
            # Align words for comparison
            word_results = text_processor.align_words(original_words, user_words, [])
            
            # Calculate metrics
            accuracy = text_processor.calculate_accuracy(word_results)
            correct_count = sum(1 for r in word_results if r['correct'] and r['original'])
            total_count = len([r for r in word_results if r['original']])
            incorrect_words = text_processor.extract_incorrect_words(word_results)
            
            # Create analysis result
            analysis_result = {
                'accuracy': accuracy,
                'correct_count': correct_count,
                'total_count': total_count,
                'word_results': word_results,
                'incorrect_words': incorrect_words,
                'passed': accuracy >= AnalysisConfig.PASSING_ACCURACY,
                'user_transcription': user_transcription,
                'original_transcription': original_transcription,
                'original_words': original_words,
                'user_words': user_words,
                'analysis_type': 'full_shloka'
            }
            
            # Generate feedback using the SAME method as tkinter app
            if analysis_result and analysis_result.get('accuracy') is not None:
                try:
                    # Call generate_feedback with analysis_result dict - SAME as tkinter (app.py line 351)
                    feedback = self.feedback_generator.generate_feedback(
                        analysis_result=analysis_result,
                        user_level='beginner'
                    )
                    
                    # Add feedback to analysis result
                    if feedback:
                        analysis_result['llm_feedback'] = {
                            'analysis': feedback.get('feedback', 'Good effort!'),
                            'motivation': feedback.get('motivation', 'Keep practicing!'),
                            'practice_tips': feedback.get('practice_tips', [])
                        }
                    else:
                        # Fallback if feedback is None
                        analysis_result['llm_feedback'] = {
                            'analysis': self._generate_simple_feedback(analysis_result.get('accuracy', 0)),
                            'motivation': 'Keep practicing!',
                            'practice_tips': []
                        }
                except Exception as feedback_error:
                    # If feedback generation fails, provide basic feedback
                    analysis_result['llm_feedback'] = {
                        'analysis': self._generate_simple_feedback(analysis_result.get('accuracy', 0)),
                        'motivation': 'Keep practicing!',
                        'practice_tips': []
                    }
                
                # Ensure success flag
                analysis_result['success'] = True
            
            return analysis_result
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }


# Singleton instance
_backend = None

def get_backend() -> StreamlitBackend:
    """Get or create backend singleton"""
    global _backend
    if _backend is None:
        _backend = StreamlitBackend()
    return _backend
