"""
Pronunciation Analysis Module for Sanskrit Voice Bot v2
Handles pronunciation comparison and analysis logic with integrated LLM feedback.
"""
from typing import Dict, List, Any, Optional

from core.config import AnalysisConfig
from utils.text_processor import TextProcessor
from analysis.feedback_generator import FeedbackGenerator


class PronunciationAnalyzer:
    """
    Analyzes user pronunciation against original Sanskrit text.
    
    This class provides:
    - Full shloka pronunciation analysis
    - Single word pronunciation analysis
    - Accuracy calculations
    - Detailed word-by-word comparisons
    - Integrated LLM feedback generation
    """
    
    def __init__(self):
        """Initialize the PronunciationAnalyzer"""
        self.text_processor = TextProcessor()
        self.feedback_generator = FeedbackGenerator()
    
    def analyze_pronunciation(self, user_transcription: str, original_shloka: Dict[str, Any], 
                            practice_mode: str = 'full', practice_words: Optional[List[Dict[str, Any]]] = None, 
                            current_word_index: int = 0) -> Dict[str, Any]:
        """
        Analyze user pronunciation based on practice mode.
        
        Args:
            user_transcription: User's spoken text (transcribed)
            original_shloka: Original shloka data
            practice_mode: 'full' for complete shloka, 'words' for individual words
            practice_words: List of words being practiced (for word mode)
            current_word_index: Current word index (for word mode)
            
        Returns:
            Dictionary containing analysis results
        """
        if practice_mode == 'words' and practice_words:
            return self._analyze_single_word(user_transcription, practice_words, current_word_index)
        else:
            return self._analyze_full_shloka(user_transcription, original_shloka)
    
    def _analyze_full_shloka(self, user_transcription: str, original_shloka: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze pronunciation of complete shloka.
        
        Args:
            user_transcription: User's spoken text
            original_shloka: Original shloka data
            
        Returns:
            Complete analysis results
        """
        original_text = original_shloka['devanagari']
        original_words = self.text_processor.smart_word_split(original_text)
        user_words = self.text_processor.smart_word_split(user_transcription)
        
        # Align words for comparison
        word_results = self.text_processor.align_words(
            original_words, 
            user_words, 
            original_shloka.get('words', [])
        )
        
        # Calculate metrics
        accuracy = self.text_processor.calculate_accuracy(word_results)
        correct_count = sum(1 for r in word_results if r['correct'] and r['original'])
        total_count = len([r for r in word_results if r['original']])
        incorrect_words = self.text_processor.extract_incorrect_words(word_results)
        
        return {
            'accuracy': accuracy,
            'correct_count': correct_count,
            'total_count': total_count,
            'word_results': word_results,
            'incorrect_words': incorrect_words,
            'passed': accuracy >= AnalysisConfig.PASSING_ACCURACY,
            'user_transcription': user_transcription,
            'original_words': original_words,
            'user_words': user_words,
            'analysis_type': 'full_shloka'
        }
    
    def _analyze_single_word(self, user_transcription: str, practice_words: List[Dict[str, Any]], 
                           current_word_index: int) -> Optional[Dict[str, Any]]:
        """
        Analyze pronunciation of a single practice word.
        
        Args:
            user_transcription: User's spoken text
            practice_words: List of words being practiced
            current_word_index: Index of current word
            
        Returns:
            Single word analysis results, or None if invalid
        """
        if not practice_words or current_word_index >= len(practice_words):
            return None
        
        current_word = practice_words[current_word_index]
        original_word = current_word['devanagari']
        
        # For single word analysis, use the full transcription as the user word
        user_word = user_transcription.strip()
        
        # Calculate similarity
        similarity = self.text_processor.calculate_similarity(original_word, user_word)
        is_correct = similarity > AnalysisConfig.WORD_SIMILARITY_THRESHOLD
        
        # Create result similar to full analysis
        word_result = {
            'index': 0,
            'original': original_word,
            'user': user_word,
            'correct': is_correct,
            'similarity': similarity,
            'devanagari': current_word['devanagari'],
            'slp1': current_word['slp1']
        }
        
        accuracy = similarity * 100
        
        return {
            'accuracy': round(accuracy, 1),
            'correct_count': 1 if is_correct else 0,
            'total_count': 1,
            'word_results': [word_result],
            'incorrect_words': [] if is_correct else [word_result],
            'passed': is_correct,
            'user_transcription': user_transcription,
            'original_words': [original_word],
            'user_words': [user_word],
            'analysis_type': 'single_word',
            'word_index': current_word_index,
            'total_practice_words': len(practice_words)
        }
    
    def split_into_words(self, devanagari_text: str, slp1_text: str) -> List[Dict[str, Any]]:
        """
        Split text into words with metadata - wrapper for TextProcessor method.
        
        Args:
            devanagari_text: Text in Devanagari script
            slp1_text: Text in SLP1 transliteration
            
        Returns:
            List of word dictionaries
        """
        return self.text_processor.split_into_words(devanagari_text, slp1_text)
    
    def compare_with_threshold(self, similarity: float, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Compare similarity against threshold.
        
        Args:
            similarity: Calculated similarity score
            threshold: Optional threshold (uses default if None)
            
        Returns:
            Comparison result dictionary
        """
        if threshold is None:
            threshold = AnalysisConfig.WORD_SIMILARITY_THRESHOLD
        
        return {
            'passed': similarity >= threshold,
            'similarity': similarity,
            'threshold': threshold,
            'difference': similarity - threshold
        }
    
    def get_detailed_word_analysis(self, word_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed analysis for a specific word.
        
        Args:
            word_result: Word result dictionary from analysis
            
        Returns:
            Detailed word analysis
        """
        analysis = {
            'word': word_result['devanagari'],
            'user_attempt': word_result['user'],
            'similarity': word_result['similarity'],
            'similarity_percentage': round(word_result['similarity'] * 100, 1),
            'passed': word_result['correct'],
            'pronunciation_guide': self.text_processor.generate_pronunciation_guide(word_result)
        }
        
        # Add difficulty assessment
        if word_result['similarity'] < 0.3:
            analysis['difficulty'] = 'Very difficult - needs significant practice'
        elif word_result['similarity'] < 0.6:
            analysis['difficulty'] = 'Challenging - focus on pronunciation guide'
        elif word_result['similarity'] < 0.8:
            analysis['difficulty'] = 'Almost correct - minor adjustments needed'
        else:
            analysis['difficulty'] = 'Well pronounced'
        
        return analysis
    
    def generate_feedback(self, analysis_result: Dict[str, Any], user_level: str = "beginner") -> Optional[Dict[str, str]]:
        """
        Generate personalized feedback based on analysis results
        
        Args:
            analysis_result: Dictionary containing analysis data
            user_level: Proficiency level of the user (beginner/intermediate/advanced)
            
        Returns:
            Dictionary containing feedback text or None if generation fails
        """
        return self.feedback_generator.generate_feedback(analysis_result, user_level)
    
    def get_practice_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """
        Get specific practice suggestions based on analysis
        
        Args:
            analysis_result: Analysis results dictionary
            
        Returns:
            List of practice suggestions
        """
        return self.feedback_generator.get_practice_suggestions(analysis_result)
    
    def set_llm_mode(self, mode: str):
        """
        Set the LLM mode for feedback generation
        
        Args:
            mode: LLM mode ('gemini', 'llama', or 'compare')
        """
        self.feedback_generator.set_llm_mode(mode)
    
    def get_llm_mode(self) -> str:
        """
        Get the current LLM mode
        
        Returns:
            Current LLM mode
        """
        return self.feedback_generator.get_llm_mode()
    
    def generate_word_feedback(self, accuracy: float) -> str:
        """Generate feedback for single word practice"""
        if accuracy >= 90:
            return "🌟 Excellent! This word is much better now. Try the next word or return to full practice."
        elif accuracy >= 70:
            return "👍 Good improvement! Practice a few more times to perfect this word."
        elif accuracy >= 50:
            return "📚 Getting better! Focus on the pronunciation guide and try again."
        else:
            return "💪 Keep practicing! Break the word into smaller parts and pronounce slowly."
    
    def generate_shloka_feedback(self, accuracy: float, incorrect_word_count: int) -> str:
        """Generate feedback for full shloka practice"""
        if accuracy >= 90:
            return "🌟 Excellent pronunciation! You've mastered this shloka."
        elif accuracy >= 70:
            return f"👍 Good job! Practice the {incorrect_word_count} highlighted words to perfect your pronunciation."
        elif accuracy >= 50:
            return f"📚 Keep practicing! Focus on the {incorrect_word_count} specific words that need work."
        else:
            return "💪 Don't worry, Sanskrit pronunciation takes time. Let's practice the words step by step."
