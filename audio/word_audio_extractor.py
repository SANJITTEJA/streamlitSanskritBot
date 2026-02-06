"""
Word Audio Extraction for Sanskrit Voice Bot v2
Extracts individual word audio segments from shloka recordings
Uses REAL word timestamps from Whisper API
"""
import numpy as np
import scipy.io.wavfile as wav
import tempfile
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import base64
import io

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

# Import timestamp extraction
from audio.word_timestamp_extractor import (
    get_word_timestamps_from_audio,
    find_word_in_timestamps
)


def calculate_word_character_duration(word: str) -> float:
    """
    Calculate duration weight for a word based on character count.
    Uses simple character-length proportional distribution.
    """
    if not word:
        return 0
    # Simple character count - works reliably for all scripts
    return len(word)


def create_word_timestamp_map(shloka_text: str, total_audio_duration: float) -> Dict:
    """
    Create a mapping of words to their estimated start/end times.
    Uses character-length proportional distribution.
    
    Args:
        shloka_text: Full text of the verse/shloka
        total_audio_duration: Total duration of the audio in seconds
        
    Returns:
        dict with word as key, timing info as value
    """
    if not shloka_text or total_audio_duration <= 0:
        return {}
    
    words = shloka_text.strip().split()
    if not words:
        return {}
    
    # Calculate total character count for proportional timing
    total_chars = sum(len(word) for word in words)
    if total_chars == 0:
        return {}
    
    # Create timestamp mapping
    timestamp_map = {}
    current_time = 0.0
    
    for word in words:
        # Duration proportional to character length
        word_duration = (len(word) / total_chars) * total_audio_duration
        
        timestamp_map[word] = {
            'start_time': current_time,
            'end_time': current_time + word_duration,
            'duration': word_duration
        }
        
        current_time += word_duration
    
    return timestamp_map


def get_audio_duration(audio_bytes: bytes, audio_format: str = 'mp3') -> float:
    """Get the duration of audio from bytes"""
    try:
        if HAS_PYDUB:
            audio_io = io.BytesIO(audio_bytes)
            audio = AudioSegment.from_file(audio_io, format=audio_format)
            duration = len(audio) / 1000.0
            return duration
        
        if HAS_LIBROSA and audio_format == 'wav':
            audio_io = io.BytesIO(audio_bytes)
            sample_rate, audio_data = wav.read(audio_io)
            duration = len(audio_data) / sample_rate
            return duration
        
        # Fallback estimate
        return 10.0
        
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 10.0


def load_audio_data(audio_bytes: bytes, audio_format: str = 'mp3') -> Tuple[int, np.ndarray]:
    """Load audio data from bytes"""
    
    # Try scipy first for WAV (most reliable, no external dependencies)
    if audio_format.lower() == 'wav':
        try:
            audio_io = io.BytesIO(audio_bytes)
            sample_rate, audio_data = wav.read(audio_io)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Convert to float32 and normalize
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32767.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483647.0
            else:
                audio_data = audio_data.astype(np.float32)
            
            return sample_rate, audio_data
        except Exception as e:
            print(f"Scipy WAV loading failed: {e}")
    
    # Try librosa (works for many formats)
    if HAS_LIBROSA:
        try:
            audio_io = io.BytesIO(audio_bytes)
            audio_data, sample_rate = librosa.load(audio_io, sr=None, mono=True)
            return sample_rate, audio_data
        except Exception as e:
            print(f"Librosa loading failed: {e}")
    
    # Try pydub (requires ffmpeg but supports many formats)
    if HAS_PYDUB:
        try:
            audio_io = io.BytesIO(audio_bytes)
            audio = AudioSegment.from_file(audio_io, format=audio_format)
            
            # Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            sample_rate = audio.frame_rate
            audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
            
            # Normalize based on sample width
            if audio.sample_width == 2:  # 16-bit
                audio_data = audio_data / 32767.0
            elif audio.sample_width == 4:  # 32-bit
                audio_data = audio_data / 2147483647.0
            else:
                audio_data = audio_data / (2 ** (8 * audio.sample_width - 1))
            
            return sample_rate, audio_data
        except Exception as e:
            print(f"Pydub loading failed: {e}")
    
    raise Exception(f"Could not load {audio_format} audio - no suitable library available or working")


def calculate_word_similarity(word1: str, word2: str) -> float:
    """Calculate similarity between two words using character-level matching"""
    from difflib import SequenceMatcher
    
    # Remove common punctuation
    import re
    word1_clean = re.sub(r'[।॥\s]+', '', word1.strip())
    word2_clean = re.sub(r'[।॥\s]+', '', word2.strip())
    
    # Calculate similarity ratio
    similarity = SequenceMatcher(None, word1_clean, word2_clean).ratio()
    return similarity


def extract_word_audio(
    shloka_audio_base64: str,
    shloka_audio_format: str,
    word_text: str,
    shloka_text: str,
    word_timestamps: List[Dict] = None
) -> Optional[bytes]:
    """
    Extract audio segment for a specific word from the shloka audio.
    Uses REAL word timestamps from Whisper API if provided.
    
    Args:
        shloka_audio_base64: Base64 encoded audio data
        shloka_audio_format: Audio format (mp3, wav, etc)
        word_text: The word to extract
        shloka_text: Full shloka text
        word_timestamps: Optional pre-computed word timestamps from Whisper API
        
    Returns:
        WAV audio bytes for the word, or None if extraction fails
    """
    print(f"\n=== Word Audio Extraction ===")
    print(f"Target word: {word_text}")
    print(f"Format: {shloka_audio_format}")
    
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(shloka_audio_base64)
        print(f"Audio size: {len(audio_bytes)} bytes")
        
        word_timing = None
        
        # Method 1: Use pre-computed timestamps if available
        if word_timestamps:
            print(f"Using pre-computed timestamps ({len(word_timestamps)} words)")
            word_timing = find_word_in_timestamps(word_text, word_timestamps)
        
        # Method 2: Get timestamps from Whisper API (more accurate)
        if not word_timing:
            print("Getting word timestamps from Whisper API...")
            timestamp_result = get_word_timestamps_from_audio(audio_bytes, shloka_audio_format)
            
            if timestamp_result.get('success') and timestamp_result.get('words'):
                words_data = timestamp_result['words']
                print(f"Got {len(words_data)} words from API")
                word_timing = find_word_in_timestamps(word_text, words_data)
        
        if not word_timing:
            print(f"✗ Could not find timestamps for '{word_text}'")
            return None
        
        print(f"✓ Word timing: {word_timing['start_time']:.2f}s - {word_timing['end_time']:.2f}s")
        
        # Load audio data
        sample_rate, audio_data = load_audio_data(audio_bytes, shloka_audio_format)
        print(f"Loaded audio: {sample_rate}Hz, {len(audio_data)} samples")
        
        # Convert timing to sample indices
        start_sample = int(word_timing['start_time'] * sample_rate)
        end_sample = int(word_timing['end_time'] * sample_rate)
        
        # Add 0.3 second padding before and after for natural sound
        padding_samples = int(0.3 * sample_rate)
        start_padded = max(0, start_sample - padding_samples)
        end_padded = min(len(audio_data), end_sample + padding_samples)
        
        print(f"Extracting samples {start_padded} to {end_padded}")
        
        # Extract word segment
        word_audio_segment = audio_data[start_padded:end_padded]
        
        # Ensure we have data
        if len(word_audio_segment) == 0:
            print("ERROR: Extracted segment is empty")
            return None
        
        print(f"Extracted {len(word_audio_segment)} samples")
        
        # Convert to 16-bit integer with proper clipping
        word_audio_int16 = np.clip(word_audio_segment * 32767, -32768, 32767).astype(np.int16)
        
        # Ensure contiguous array for WAV writing
        word_audio_int16 = np.ascontiguousarray(word_audio_int16)
        
        # Write to bytes buffer
        audio_buffer = io.BytesIO()
        try:
            wav.write(audio_buffer, sample_rate, word_audio_int16)
            audio_buffer.seek(0)
            
            result = audio_buffer.read()
            print(f"Generated word audio: {len(result)} bytes")
            print("=== Extraction Successful ===\n")
            
            return result
        except Exception as write_error:
            print(f"ERROR writing WAV: {write_error}")
            return None
        
    except Exception as e:
        print(f"ERROR in extract_word_audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
