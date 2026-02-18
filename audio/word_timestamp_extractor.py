"""
Word Timestamp Extraction using Whisper API
Gets actual word-level timestamps from audio using verbose_json response
"""
import requests
from typing import Dict, List, Optional, Any
from core.config import AudioConfig


def get_word_timestamps_from_audio(
    audio_bytes: bytes,
    audio_format: str = 'mp3'
) -> Dict[str, Any]:
    """
    Get word-level timestamps from audio using Groq Whisper API.
    
    Args:
        audio_bytes: Raw audio bytes
        audio_format: Audio format (mp3, wav, etc.)
        
    Returns:
        Dict with:
        - success: bool
        - text: Full transcription text
        - words: List of {word, start, end} dicts
        - segments: List of segment dicts
        - error: Error message if failed
    """
    try:
        headers = {
            'Authorization': f'Bearer {AudioConfig.GROQ_API_KEY}'
        }
        
        # Request verbose_json with word-level timestamps
        files = {
            'file': (f'audio.{audio_format}', audio_bytes, f'audio/{audio_format}'),
            'model': (None, AudioConfig.WHISPER_MODEL),
            'language': (None, 'hi'),  # Hindi for Devanagari
            'response_format': (None, 'verbose_json'),
            'timestamp_granularities[]': (None, 'word'),
        }
        
        print(f"Requesting word timestamps from Groq API...")
        
        response = requests.post(
            AudioConfig.GROQ_API_URL,
            headers=headers,
            files=files,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract word timestamps
            words = result.get('words', [])
            segments = result.get('segments', [])
            text = result.get('text', '').strip()
            
            print(f"✓ Got {len(words)} words with timestamps")
            print(f"✓ Text: {text[:100]}...")
            
            # Debug: Print first few word timestamps
            for i, word in enumerate(words[:5]):
                print(f"  Word {i+1}: '{word.get('word', '')}' ({word.get('start', 0):.2f}s - {word.get('end', 0):.2f}s)")
            
            return {
                'success': True,
                'text': text,
                'words': words,
                'segments': segments,
                'duration': result.get('duration', 0)
            }
        else:
            error_msg = f"API request failed: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                pass
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
            
    except Exception as e:
        print(f"✗ Error getting word timestamps: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def create_word_timestamp_map_from_api(words_data: List[Dict]) -> Dict[str, Dict]:
    """
    Create a word->timing map from Whisper API word data.
    
    Args:
        words_data: List of word dicts from Whisper API
                   [{'word': 'माता', 'start': 0.5, 'end': 1.2}, ...]
                   
    Returns:
        Dict mapping words to their timing info
    """
    timestamp_map = {}
    
    for word_info in words_data:
        word = word_info.get('word', '').strip()
        if not word:
            continue
            
        # Store timing - if word appears multiple times, keep first occurrence
        if word not in timestamp_map:
            timestamp_map[word] = {
                'start_time': word_info.get('start', 0),
                'end_time': word_info.get('end', 0),
                'duration': word_info.get('end', 0) - word_info.get('start', 0)
            }
    
    return timestamp_map


def find_word_in_timestamps(
    target_word: str,
    words_data: List[Dict]
) -> Optional[Dict]:
    """
    Find timing for a specific word in the API response.
    Uses exact match first, then fuzzy matching.
    
    Args:
        target_word: The word to find
        words_data: List of word dicts from Whisper API
        
    Returns:
        Timing dict or None
    """
    import re
    from difflib import SequenceMatcher
    
    target_clean = target_word.strip()
    target_no_punct = re.sub(r'[।॥\s]+', '', target_clean)
    
    # First pass: exact match
    for word_info in words_data:
        word = word_info.get('word', '').strip()
        if word == target_clean:
            print(f"✓ Exact match: '{word}'")
            return {
                'start_time': word_info.get('start', 0),
                'end_time': word_info.get('end', 0)
            }
    
    # Second pass: match without punctuation
    for word_info in words_data:
        word = word_info.get('word', '').strip()
        word_no_punct = re.sub(r'[।॥\s]+', '', word)
        if word_no_punct == target_no_punct:
            print(f"✓ Match (no punct): '{word}'")
            return {
                'start_time': word_info.get('start', 0),
                'end_time': word_info.get('end', 0)
            }
    
    # Third pass: substring match
    for word_info in words_data:
        word = word_info.get('word', '').strip()
        word_no_punct = re.sub(r'[।॥\s]+', '', word)
        if target_no_punct in word_no_punct or word_no_punct in target_no_punct:
            print(f"✓ Substring match: '{word}'")
            return {
                'start_time': word_info.get('start', 0),
                'end_time': word_info.get('end', 0)
            }
    
    # Fourth pass: fuzzy match (>50% similarity)
    best_match = None
    best_similarity = 0.0
    
    for word_info in words_data:
        word = word_info.get('word', '').strip()
        word_no_punct = re.sub(r'[।॥\s]+', '', word)
        
        similarity = SequenceMatcher(None, target_no_punct, word_no_punct).ratio()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = word_info
    
    if best_match and best_similarity >= 0.5:
        print(f"✓ Fuzzy match: '{best_match.get('word', '')}' ({best_similarity:.1%})")
        return {
            'start_time': best_match.get('start', 0),
            'end_time': best_match.get('end', 0)
        }
    
    print(f"✗ No match found for '{target_word}'")
    return None
