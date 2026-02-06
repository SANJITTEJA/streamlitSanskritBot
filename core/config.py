"""
Configuration module for Sanskrit Voice Bot v2
Contains all application settings, constants, and configuration values.
"""
from pathlib import Path
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Try to import streamlit for secrets (deployment)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

class AppConfig:
    """Application-wide configuration settings"""
    
    # Application metadata
    TITLE = "Sanskrit Voice Bot - Learn Sanskrit Pronunciation"
    VERSION = "2.0.0"
    GEOMETRY = "1200x800"
    BACKGROUND_COLOR = "#f9f3f4"
    
    # Data paths configuration - relative to v2 directory
    V2_ROOT = Path(__file__).parent.parent  # Go up from v2/core/ to v2/
    DATA_PATH = V2_ROOT / "data"
    TRANSCRIPT_PATH = DATA_PATH / "Transcript"
    DEVANAGARI_PATH = TRANSCRIPT_PATH / "Devanagari"
    SLP1_PATH = TRANSCRIPT_PATH / "SLP1"
    
    # Speaker configuration
    MIN_SPEAKER = 1
    MAX_SPEAKER = 27
    MAX_SHLOKAS_DISPLAY = 20  # Limit for demo purposes
    
    @staticmethod
    def get_speaker_id(speaker_num):
        """Generate speaker ID from number"""
        return f"sp{speaker_num:03d}"
    
    @staticmethod
    def get_speaker_options():
        """Get list of speaker options for UI"""
        return [f"Speaker {i:02d} (sp{i:03d})" for i in range(AppConfig.MIN_SPEAKER, AppConfig.MAX_SPEAKER + 1)]


class AudioConfig:
    """Audio processing configuration"""
    
    SAMPLE_RATE = 44100
    RECORDING_DURATION = 30  
    AUDIO_CHANNELS = 1
    
    # Audio analysis thresholds
    QUIET_AUDIO_THRESHOLD = 0.001
    LOUD_AUDIO_THRESHOLD = 0.01
    
    # Groq API configuration - Read from .env, Streamlit secrets, or environment variable
    if HAS_STREAMLIT:
        try:
            GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
        except:
            GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    else:
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    
    GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    WHISPER_MODEL = "whisper-large-v3-turbo"


class AnalysisConfig:
    """Analysis and comparison configuration"""
    
    # Analysis thresholds
    WORD_SIMILARITY_THRESHOLD = 0.7
    PASSING_ACCURACY = 70.0
    
    # LLM Feedback settings - Read from Streamlit secrets if available
    if HAS_STREAMLIT:
        try:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        except:
            GEMINI_API_KEY = "AIzaSyCmbwI9zbFy9b4iiUNVjQzEkmyL9drOoBA"
    else:
        GEMINI_API_KEY = "AIzaSyCmbwI9zbFy9b4iiUNVjQzEkmyL9drOoBA"
    # GEMINI_API_KEY = "AIzaSyCmbwI9zbFy9b4iiUNVjQzEkmyL9drOoBA"
    GEMINI_MODEL = "gemini-2.5-flash"  # Use the newer model with better quotas
    USE_LLM_FEEDBACK = True
    LLM_FEEDBACK_RETRY_LIMIT = 2
    
    # Ollama settings for local LLM
    OLLAMA_BASE_URL = "http://localhost:11434"
    LLAMA_MODEL = "llama3.2"
    
    # LLM timeouts and circuit breaker
    LLM_TIMEOUT = 30
    MAX_RETRIES = 3


class PracticeConfig:
    """Practice session configuration"""
    
    # Word practice settings
    MAX_ATTEMPTS_BEFORE_SUGGESTION = 5
    DECREASING_ACCURACY_THRESHOLD = 5  # Number of consecutive decreasing scores before suggesting alternatives
    
    # Alphabet practice settings
    ALPHABET_COMPLETION_THRESHOLD = 80.0  # Minimum accuracy to complete alphabet practice
    
    # Word-level practice thresholds
    WORD_ACCURACY_THRESHOLD = 60.0  # Minimum accuracy for individual word to be considered "correct"
    MINIMUM_ATTEMPTS_FOR_SUGGESTION = 3  # Minimum attempts before suggesting alphabet practice


# Sanskrit language constants
class SanskritConstants:
    """Sanskrit language-specific constants and data"""
    
    # Sanskrit Devanagari vowels and consonants with SLP1 mapping
    VOWELS = [
        ('अ', 'a'), ('आ', 'A'), ('इ', 'i'), ('ई', 'I'), ('उ', 'u'), ('ऊ', 'U'),
        ('ऋ', 'f'), ('ॠ', 'F'), ('ऌ', 'x'), ('ॡ', 'X'), ('ए', 'e'), ('ऐ', 'E'),
        ('ओ', 'o'), ('औ', 'O'), ('अं', 'M'), ('अः', 'H')
    ]
    
    CONSONANTS = [
        ('क', 'ka'), ('ख', 'Ka'), ('ग', 'ga'), ('घ', 'Ga'), ('ङ', 'Na'),
        ('च', 'ca'), ('छ', 'Ca'), ('ज', 'ja'), ('झ', 'Ja'), ('ञ', 'Ya'),
        ('ट', 'wa'), ('ठ', 'Wa'), ('ड', 'qa'), ('ढ', 'Qa'), ('ण', 'Ra'),
        ('त', 'ta'), ('थ', 'Ta'), ('द', 'da'), ('ध', 'Da'), ('न', 'na'),
        ('प', 'pa'), ('फ', 'Pa'), ('ब', 'ba'), ('भ', 'Ba'), ('म', 'ma'),
        ('य', 'ya'), ('र', 'ra'), ('ल', 'la'), ('व', 'va'),
        ('श', 'Sa'), ('ष', 'za'), ('स', 'sa'), ('ह', 'ha')
    ]
    
    # Phoneme duration weights for timing calculations
    @staticmethod
    def get_phoneme_duration_weights():
        """Get duration weights for different Sanskrit phonemes"""
        return {
            # Short vowels (1 unit)
            'अ': 1, 'इ': 1, 'उ': 1, 'ऋ': 1, 'ऌ': 1,
            
            # Long vowels (2 units)
            'आ': 2, 'ई': 2, 'ऊ': 2, 'ए': 2, 'ओ': 2, 'ऐ': 2, 'औ': 2, 'ॠ': 2, 'ॡ': 2,
            
            # Consonants with inherent 'a' (1 unit)
            'क': 1, 'ख': 1, 'ग': 1, 'घ': 1, 'ङ': 1,
            'च': 1, 'छ': 1, 'ज': 1, 'झ': 1, 'ञ': 1,
            'ट': 1, 'ठ': 1, 'ड': 1, 'ढ': 1, 'ण': 1,
            'त': 1, 'थ': 1, 'द': 1, 'ध': 1, 'न': 1,
            'प': 1, 'फ': 1, 'ब': 1, 'भ': 1, 'म': 1,
            'य': 1, 'र': 1, 'ल': 1, 'व': 1,
            'श': 1, 'ष': 1, 'स': 1, 'ह': 1,
            
            # Vowel matras (modifiers)
            'ा': 1,  # आ matra (adds 1 unit to make total 2)
            'ि': 0,  # इ matra (replaces inherent अ, so net 0)
            'ी': 1,  # ई matra (adds 1 unit to make total 2)
            'ु': 0,  # उ matra (replaces inherent अ, so net 0)
            'ू': 1,  # ऊ matra (adds 1 unit to make total 2)
            'ृ': 0,  # ऋ matra (replaces inherent अ, so net 0)
            'े': 1,  # ए matra (adds 1 unit to make total 2)
            'ो': 1,  # ओ matra (adds 1 unit to make total 2)
            'ै': 1,  # ऐ matra (adds 1 unit to make total 2)
            'ौ': 1,  # औ matra (adds 1 unit to make total 2)
            
            # Halanta (virama) - removes inherent vowel
            '्': -1,
            
            # Anusvara and Visarga
            'ं': 0.5,  # Half unit
            'ः': 0.5,  # Half unit
            'ँ': 0.5,  # Chandrabindu
            
            # Punctuation (no duration)
            '।': 0,
            '॥': 0,
            ' ': 0,  # Space
        }
