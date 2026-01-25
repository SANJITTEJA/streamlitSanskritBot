"""
Audio Manager Module for Sanskrit Voice Bot v2
Handles audio recording, playback, transcription, and word-level audio processing.
"""
# Optional imports for desktop features (not needed for Streamlit)
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

import scipy.io.wavfile as wav
import numpy as np
import requests
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from core.config import AudioConfig, SanskritConstants

# Try to import additional audio libraries for MP3 support
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False


class AudioManager:
    """
    Manages all audio-related operations including recording, playback, and transcription.
    
    This class provides:
    - Audio recording functionality
    - Audio file playback
    - Speech-to-text transcription via Groq API
    - Word-level audio extraction and playback
    - Audio setup testing
    """
    
    def __init__(self):
        """Initialize the AudioManager"""
        self._is_recording = False
        self._current_audio_data = None
        self._sample_rate = AudioConfig.SAMPLE_RATE
        self._recording = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize pygame mixer for audio playback.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not HAS_PYGAME:
            # Not available in web deployment, that's OK
            self._initialized = False
            return False
        
        try:
            pygame.mixer.init()
            self._initialized = True
            return True
        except Exception as e:
            print(f"Error initializing audio: {e}")
            return False
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._is_recording
    
    def start_recording(self) -> bool:
        """
        Start aHAS_SOUNDDEVICE:
            return False
            
        if not udio recording.
        
        Returns:
            bool: True if recording started successfully, False otherwise
        """
        if not self._is_recording:
            try:
                self._is_recording = True
                duration = 10  # Maximum recording duration
                self._recording = sd.rec(
                    int(duration * self._sample_rate), 
                    samplerate=self._sample_rate, 
                    channels=1, 
                    dtype=np.float32
                )
                return True
            except Exception as e:
                print(f"Error starting recording: {e}")
                self._is_recording = False
                return False
        return False
    
    def stop_recording(self) -> Dict[str, Any]:
        """
        Stop audio recording and prepare for analysis.
        
        Retnot HAS_SOUNDDEVICE:
            return {'success': False, 'error': 'Recording not available in web mode'}
            
        if urns:
            Dict containing success status and audio information
        """
        if self._is_recording:
            try:
                sd.stop()
                self._is_recording = False
                self._current_audio_data = self._recording.copy()
                
                # Check if audio is too quiet
                max_amplitude = np.max(np.abs(self._current_audio_data))
                is_quiet = max_amplitude < AudioConfig.QUIET_AUDIO_THRESHOLD
                
                return {
                    'success': True, 
                    'has_audio': len(self._current_audio_data) > 0,
                    'is_quiet': is_quiet,
                    'max_amplitude': float(max_amplitude)
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'No recording in progress'}
    
    def transcribe_audio(self) -> Dict[str, Any]:
        """
        Transcribe the current audio using Groq API.
        
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
                    'language': (None, 'hi'),  # Use Hindi for better Devanagari support
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
    
    def load_audio_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load audio from an external file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing success status and message
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {'success': False, 'error': 'File not found'}
        
        try:
            sample_rate_file, audio_data = wav.read(str(file_path))
            
            # Convert to float32 and mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            self._current_audio_data = audio_data.astype(np.float32) / 32767.0
            
            return {'success': True, 'message': 'Audio file loaded successfully'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to load audio file: {str(e)}'}
    
    def play_audio_file(self, file_path: Path) -> bool:
        """
        Play an audio file using pygame.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            bool: True if playback started successfully, False otherwise
        """
        if not self._initialized:
            return False
            
        file_path = Path(file_path)
        if not file_path.exists():
            return False
        
        try:
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.play()
            return True
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
    
    def test_audio_setup(self) -> Dict[str, Any]:
        """
        Test audio recording setup.
        
        Returns:
            Dict containing test results and audio metrics
        """
        try:
            # Simple test recording
            test_duration = 2
            test_recording = sd.rec(
                int(test_duration * self._sample_rate), 
                samplerate=self._sample_rate, 
                channels=1, 
                dtype=np.float32
            )
            sd.wait()
            
            max_amplitude = np.max(np.abs(test_recording))
            
            return {
                'success': True,
                'max_amplitude': float(max_amplitude),
                'file_size': len(test_recording) * 4,  # float32 = 4 bytes per sample
                'duration': test_duration,
                'sample_rate': self._sample_rate
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Audio test failed: {str(e)}'
            }
    
    def play_word_audio(self, audio_file_path: Path, word_text: str, shloka_text: str) -> Dict[str, Any]:
        """
        Play audio for a specific word using calculated timestamps.
        
        Args:
            audio_file_path: Path to the source audio file
            word_text: The specific word to play
            shloka_text: The complete shloka text for timing calculations
            
        Returns:
            Dict containing playback result and timing information
        """
        try:
            # Validate inputs
            if not audio_file_path or not word_text or not shloka_text:
                return {'success': False, 'error': 'Missing required parameters'}
            
            audio_file_path = Path(audio_file_path)
            if not audio_file_path.exists():
                return {'success': False, 'error': f'Audio file not found: {audio_file_path}'}
            
            # Get audio duration and create timestamp mapping
            total_duration = self._get_audio_duration(audio_file_path)
            timestamp_map = self._create_word_timestamp_map(shloka_text, total_duration)
            
            # Find timing for target word
            word_timing = self._find_word_timing(word_text, timestamp_map)
            
            if not word_timing:
                # Fallback: play entire audio
                return self._play_fallback_audio(audio_file_path, word_text)
            
            # Extract and play word segment
            return self._play_word_segment(audio_file_path, word_timing, word_text)
            
        except Exception as e:
            return {'success': False, 'error': f'Error playing word audio: {str(e)}'}
    
    def _get_audio_duration(self, audio_file_path: Path) -> float:
        """Get the duration of an audio file in seconds"""
        try:
            # Try with pydub first (best MP3 support)
            if HAS_PYDUB:
                try:
                    audio = AudioSegment.from_file(str(audio_file_path))
                    return len(audio) / 1000.0  # Convert milliseconds to seconds
                except Exception:
                    pass
            
            # Try with librosa
            if HAS_LIBROSA:
                try:
                    return librosa.get_duration(filename=str(audio_file_path))
                except Exception:
                    pass
            
            # Fallback: estimate based on file size for MP3
            file_size = audio_file_path.stat().st_size
            # Rough estimate: 128 kbps MP3 ≈ 16KB per second
            estimated_duration = file_size / 16000.0
            return max(estimated_duration, 5.0)  # Minimum 5 seconds
            
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 10.0  # Default duration
    
    def _create_word_timestamp_map(self, shloka_text: str, total_duration: float) -> Dict[str, Dict[str, float]]:
        """Create a timestamp mapping for each word in the shloka"""
        if not shloka_text or total_duration <= 0:
            return {}
        
        # Split into words
        words = shloka_text.split()
        if not words:
            return {}
        
        # Calculate phonetic duration for each word
        word_durations = []
        total_phonetic_duration = 0
        
        for word in words:
            duration = self._calculate_word_phoneme_duration(word)
            word_durations.append(duration)
            total_phonetic_duration += duration
        
        # Create timestamp mapping
        timestamp_map = {}
        current_time = 0
        
        for i, word in enumerate(words):
            word_phonetic_duration = word_durations[i]
            word_audio_duration = (word_phonetic_duration / total_phonetic_duration) * total_duration
            
            timestamp_map[word] = {
                'start_time': current_time,
                'end_time': current_time + word_audio_duration,
                'duration': word_audio_duration,
                'phonetic_duration': word_phonetic_duration
            }
            
            current_time += word_audio_duration
        
        return timestamp_map
    
    def _calculate_word_phoneme_duration(self, word: str) -> float:
        """Calculate the phonetic duration of a Sanskrit word"""
        if not word:
            return 0
        
        weights = SanskritConstants.get_phoneme_duration_weights()
        total_duration = 0
        
        # Process character by character with context awareness
        i = 0
        while i < len(word):
            char = word[i]
            
            if char in weights:
                duration = weights[char]
                
                # Special handling for consonants followed by virama
                if (char in 'कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह' and 
                    i + 1 < len(word) and word[i + 1] == '्'):
                    # Consonant + virama: no inherent vowel sound
                    duration = 0.5  # Just the consonant sound
                
                total_duration += duration
            else:
                # Unknown character, assume minimal duration
                total_duration += 0.5
            
            i += 1
        
        # Ensure minimum duration
        return max(total_duration, 0.5)
    
    def _find_word_timing(self, word_text: str, timestamp_map: Dict[str, Dict[str, float]]) -> Optional[Dict[str, float]]:
        """Find timing information for a specific word"""
        target_word_clean = word_text.strip()
        
        # Try exact match first
        if target_word_clean in timestamp_map:
            return timestamp_map[target_word_clean]
        
        # Try partial matching
        for word, timing in timestamp_map.items():
            if target_word_clean in word or word in target_word_clean:
                return timing
        
        return None
    
    def _play_fallback_audio(self, audio_file_path: Path, word_text: str) -> Dict[str, Any]:
        """Play entire audio as fallback when word timing not found"""
        if self.play_audio_file(audio_file_path):
            return {
                'success': True,
                'message': f'Word "{word_text}" not found in timing map, playing full audio',
                'fallback': True
            }
        else:
            return {
                'success': False,
                'error': 'Failed to play audio file'
            }
    
    def _play_word_segment(self, audio_file_path: Path, word_timing: Dict[str, float], word_text: str) -> Dict[str, Any]:
        """Extract and play a specific word segment from audio"""
        try:
            # Load the audio file
            sample_rate, audio_data = self._load_audio_data(audio_file_path)
            
            # Convert timing to sample indices
            start_sample = int(word_timing['start_time'] * sample_rate)
            end_sample = int(word_timing['end_time'] * sample_rate)
            
            # Add padding (0.3 seconds before and after)
            padding_samples = int(0.3 * sample_rate)
            start_padded = max(0, start_sample - padding_samples)
            end_padded = min(len(audio_data), end_sample + padding_samples)
            
            # Extract the word segment
            word_audio_segment = audio_data[start_padded:end_padded]
            
            # Convert back to 16-bit integer for saving
            word_audio_int16 = (word_audio_segment * 32767).astype(np.int16)
            
            # Save to temporary file and play
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wav.write(temp_file.name, sample_rate, word_audio_int16)
                
                # Play the word audio
                pygame.mixer.music.load(temp_file.name)
                pygame.mixer.music.play()
                
                return {
                    'success': True,
                    'message': f'Playing word "{word_text}" from {word_timing["start_time"]:.2f}s to {word_timing["end_time"]:.2f}s',
                    'timing': word_timing
                }
                
        except Exception as e:
            # Fallback to full audio on error
            return self._play_fallback_audio(audio_file_path, word_text)
    
    def _load_audio_data(self, audio_file_path: Path) -> Tuple[int, np.ndarray]:
        """
        Load audio data from file, supporting both WAV and MP3.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Tuple of (sample_rate, audio_data_mono)
        """
        audio_file_path = Path(audio_file_path)
        
        # Try with pydub first (best MP3 support)
        if HAS_PYDUB:
            try:
                audio = AudioSegment.from_file(str(audio_file_path))
                # Convert to mono
                if audio.channels > 1:
                    audio = audio.set_channels(1)
                # Get sample rate and audio data
                sample_rate = audio.frame_rate
                audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
                # Normalize to [-1, 1] range
                audio_data = audio_data / (2**15)  # 16-bit audio
                return sample_rate, audio_data
            except Exception as e:
                print(f"Pydub loading failed: {e}")
        
        # Try with librosa
        if HAS_LIBROSA:
            try:
                audio_data, sample_rate = librosa.load(str(audio_file_path), sr=None, mono=True)
                return sample_rate, audio_data
            except Exception as e:
                print(f"Librosa loading failed: {e}")
        
        # Try with scipy (WAV only)
        try:
            sample_rate, audio_data = wav.read(str(audio_file_path))
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            # Convert to float32 and normalize
            audio_data = audio_data.astype(np.float32) / (2**15)
            return sample_rate, audio_data
        except Exception as e:
            print(f"Scipy loading failed: {e}")
        
        raise Exception("Could not load audio file - no suitable library available")
    
    def cleanup(self):
        """Clean up audio resources"""
        if self._initialized:
            pygame.mixer.quit()
            self._initialized = False
