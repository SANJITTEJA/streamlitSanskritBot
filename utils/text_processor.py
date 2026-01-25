"""
Text Processing Utilities for Sanskrit Voice Bot v2
Handles text normalization, word splitting, similarity calculations, and alignment.
"""
import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional


class TextProcessor:
    """
    Handles all text processing operations for Sanskrit text analysis.
    
    This class provides:
    - Smart word splitting for Sanskrit text
    - Text similarity calculations
    - Word alignment algorithms
    - Text normalization utilities
    """
    
    @staticmethod
    def smart_word_split(text: str) -> List[str]:
        """
        Improved word splitting for Sanskrit text.
        
        Args:
            text: Input Sanskrit text
            
        Returns:
            List of individual words
        """
        if not text:
            return []
        
        # Remove punctuation and normalize spaces
        # Keep Sanskrit characters, spaces, and basic punctuation
        text = re.sub(r'[^\u0900-\u097F\s।॥]', ' ', text)
        
        # Split by spaces and filter empty strings
        words = [word.strip() for word in text.split() if word.strip()]
        
        return words
    
    @staticmethod
    def split_into_words(devanagari_text: str, slp1_text: str) -> List[Dict[str, Any]]:
        """
        Split text into words with metadata for comparison.
        
        Args:
            devanagari_text: Text in Devanagari script
            slp1_text: Text in SLP1 transliteration
            
        Returns:
            List of word dictionaries with index, devanagari, and slp1 data
        """
        devanagari_words = TextProcessor.smart_word_split(devanagari_text)
        slp1_words = TextProcessor.smart_word_split(slp1_text)
        
        words = []
        max_length = max(len(devanagari_words), len(slp1_words))
        
        for i in range(max_length):
            devanagari_word = devanagari_words[i] if i < len(devanagari_words) else ''
            slp1_word = slp1_words[i] if i < len(slp1_words) else ''
            
            words.append({
                'index': i,
                'devanagari': devanagari_word,
                'slp1': slp1_word
            })
        
        return words
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings using sequence matching.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ''
        
        # Convert to lowercase and strip whitespace
        text = text.lower().strip()
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def align_words(original_words: List[str], user_words: List[str], 
                   shloka_words_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Align words for better comparison using dynamic programming approach.
        
        Args:
            original_words: List of original words
            user_words: List of user-spoken words
            shloka_words_data: Optional word metadata
            
        Returns:
            List of word alignment results
        """
        from core.config import AnalysisConfig
        
        results = []
        max_length = max(len(original_words), len(user_words))
        
        for i in range(max_length):
            original_word = original_words[i] if i < len(original_words) else ''
            user_word = user_words[i] if i < len(user_words) else ''
            
            # Calculate similarity if both words exist
            if original_word and user_word:
                similarity = TextProcessor.calculate_similarity(original_word, user_word)
                is_correct = similarity > AnalysisConfig.WORD_SIMILARITY_THRESHOLD
            else:
                similarity = 0.0
                is_correct = False
            
            # Get corresponding word data if available
            word_data = None
            if shloka_words_data and i < len(shloka_words_data):
                word_data = shloka_words_data[i]
            
            results.append({
                'index': i,
                'original': original_word,
                'user': user_word,
                'correct': is_correct,
                'similarity': similarity,
                'devanagari': word_data['devanagari'] if word_data else original_word,
                'slp1': word_data['slp1'] if word_data else ''
            })
        
        return results
    
    @staticmethod
    def extract_incorrect_words(word_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract words that need practice from alignment results.
        
        Args:
            word_results: List of word alignment results
            
        Returns:
            List of incorrect word results
        """
        return [result for result in word_results if not result['correct'] and result['original']]
    
    @staticmethod
    def calculate_accuracy(word_results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall accuracy from word results.
        
        Args:
            word_results: List of word alignment results
            
        Returns:
            Accuracy percentage (0.0 to 100.0)
        """
        if not word_results:
            return 0.0
        
        # Count words that exist in original (ignore empty placeholders)
        original_words = [r for r in word_results if r['original']]
        if not original_words:
            return 0.0
        
        correct_count = sum(1 for r in original_words if r['correct'])
        accuracy = (correct_count / len(original_words)) * 100
        
        return round(accuracy, 1)
    
    @staticmethod
    def generate_pronunciation_guide(word_data: Dict[str, Any]) -> str:
        """
        Generate a pronunciation guide for a word.
        
        Args:
            word_data: Dictionary containing word information
            
        Returns:
            Pronunciation guide string
        """
        if not word_data:
            return ""
        
        guide_parts = []
        
        if word_data.get('slp1'):
            guide_parts.append(f"SLP1: {word_data['slp1']}")
        
        return " | ".join(guide_parts)
    
    @staticmethod
    def split_into_syllables(text: str) -> List[str]:
        """
        Basic syllable splitting for pronunciation practice.
        
        Args:
            text: Text to split into syllables
            
        Returns:
            List of syllables
        """
        if not text:
            return []
        
        # Simple implementation - could be improved with proper Sanskrit syllable rules
        syllables = []
        current_syllable = ""
        
        vowels = set('aeiouAEIOUāīūṛṝḷḹēōṁḥ')
        
        for char in text:
            current_syllable += char
            if char in vowels:
                syllables.append(current_syllable)
                current_syllable = ""
        
        if current_syllable:
            syllables.append(current_syllable)
        
        return [s for s in syllables if s.strip()]
