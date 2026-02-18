"""
Word Practice Tracker for Sanskrit Voice Bot v2
Tracks user performance on word practice and provides intelligent suggestions.
"""
import time
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import PracticeConfig


class WordPracticeTracker:
    """
    Tracks word practice attempts and provides intelligent practice suggestions.
    
    This class provides:
    - Recording word practice attempts
    - Tracking accuracy trends
    - Suggesting alphabet practice when needed
    - Providing practice statistics
    """
    
    def __init__(self):
        """Initialize the WordPracticeTracker"""
        self.word_attempts = {}  # Track attempts per word
        self.session_start_time = time.time()
        self.max_attempts_before_suggestion = PracticeConfig.MAX_ATTEMPTS_BEFORE_SUGGESTION
        self.decreasing_accuracy_threshold = PracticeConfig.DECREASING_ACCURACY_THRESHOLD
    
    def reset_tracker(self):
        """Reset the tracker for a new practice session"""
        self.word_attempts = {}
        self.session_start_time = time.time()
    
    def record_word_attempt(self, word_key: str, accuracy: float, user_transcription: str = ""):
        """
        Record an attempt for a specific word.
        
        Args:
            word_key: Unique identifier for the word
            accuracy: Accuracy score for this attempt
            user_transcription: What the user said
        """
        if word_key not in self.word_attempts:
            self.word_attempts[word_key] = {
                'attempts': [],
                'accuracies': [],
                'last_accuracy': 0,
                'decreasing_streak': 0,
                'best_accuracy': 0,
                'transcriptions': []
            }
        
        word_data = self.word_attempts[word_key]
        word_data['attempts'].append(time.time())
        word_data['accuracies'].append(accuracy)
        word_data['transcriptions'].append(user_transcription)
        
        # Check for decreasing accuracy trend
        if accuracy < word_data['last_accuracy']:
            word_data['decreasing_streak'] += 1
        else:
            word_data['decreasing_streak'] = 0
        
        word_data['last_accuracy'] = accuracy
        word_data['best_accuracy'] = max(word_data['best_accuracy'], accuracy)
    
    def should_suggest_alphabet_practice(self, word_key: str) -> bool:
        """
        Determine if alphabet practice should be suggested for a word.
        
        Args:
            word_key: Unique identifier for the word
            
        Returns:
            bool: True if alphabet practice should be suggested
        """
        if word_key not in self.word_attempts:
            return False
        
        word_data = self.word_attempts[word_key]
        attempt_count = len(word_data['attempts'])
        
        # Suggest if user has made many attempts without improvement
        if attempt_count >= self.max_attempts_before_suggestion:
            return True
        
        # Suggest if accuracy is consistently decreasing for 5 consecutive attempts
        if word_data['decreasing_streak'] >= self.decreasing_accuracy_threshold:
            return True
        
        # Suggest if best accuracy is still very low after several attempts
        if (attempt_count >= PracticeConfig.MINIMUM_ATTEMPTS_FOR_SUGGESTION and 
            word_data['best_accuracy'] < 40):
            return True
        
        return False
    
    def get_suggestion_message(self, word_key: str, word_text: str) -> str:
        """
        Get a personalized suggestion message for a word.
        
        Args:
            word_key: Unique identifier for the word
            word_text: The actual word text
            
        Returns:
            Personalized suggestion message
        """
        if word_key not in self.word_attempts:
            return f"Let's practice the word '{word_text}' step by step."
        
        word_data = self.word_attempts[word_key]
        attempt_count = len(word_data['attempts'])
        best_accuracy = word_data['best_accuracy']
        last_accuracy = word_data['last_accuracy']
        
        message = f"You've been working hard on the word '{word_text}'.\n\n"
        
        if attempt_count >= self.max_attempts_before_suggestion:
            message += f"After {attempt_count} attempts (best: {best_accuracy:.1f}%), it might help to practice the individual sounds first.\n\n"
        elif word_data['decreasing_streak'] >= self.decreasing_accuracy_threshold:
            message += f"Your accuracy has been decreasing over the last {word_data['decreasing_streak']} attempts. Let's go back to basics.\n\n"
        elif best_accuracy < 40:
            message += f"This word seems challenging for you. Let's build up your foundation with alphabet practice.\n\n"
        
        message += "🎯 Options:\n"
        message += "1️⃣ Move to Next Shloka - Try different content\n"
        message += "2️⃣ Alphabet Practice - Build fundamental skills\n"
        message += "🔄 Keep Trying - Continue with this word"
        
        return message
    
    def get_word_statistics(self, word_key: str) -> Dict[str, Any]:
        """
        Get statistics for a specific word.
        
        Args:
            word_key: Unique identifier for the word
            
        Returns:
            Dictionary containing word practice statistics
        """
        if word_key not in self.word_attempts:
            return {
                'total_attempts': 0,
                'best_accuracy': 0,
                'last_accuracy': 0,
                'average_accuracy': 0,
                'improvement_trend': 'none'
            }
        
        word_data = self.word_attempts[word_key]
        accuracies = word_data['accuracies']
        
        # Calculate statistics
        total_attempts = len(accuracies)
        best_accuracy = word_data['best_accuracy']
        last_accuracy = word_data['last_accuracy']
        average_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        
        # Determine improvement trend
        if total_attempts < 2:
            improvement_trend = 'insufficient_data'
        elif len(accuracies) >= 3:
            recent_avg = sum(accuracies[-3:]) / 3
            earlier_avg = sum(accuracies[:-3]) / len(accuracies[:-3]) if len(accuracies) > 3 else accuracies[0]
            
            if recent_avg > earlier_avg + 5:
                improvement_trend = 'improving'
            elif recent_avg < earlier_avg - 5:
                improvement_trend = 'declining'
            else:
                improvement_trend = 'stable'
        else:
            improvement_trend = 'stable'
        
        return {
            'total_attempts': total_attempts,
            'best_accuracy': best_accuracy,
            'last_accuracy': last_accuracy,
            'average_accuracy': round(average_accuracy, 1),
            'improvement_trend': improvement_trend,
            'decreasing_streak': word_data['decreasing_streak']
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current practice session.
        
        Returns:
            Dictionary containing session statistics
        """
        total_words_practiced = len(self.word_attempts)
        total_attempts = sum(len(data['attempts']) for data in self.word_attempts.values())
        session_duration = time.time() - self.session_start_time
        
        if total_words_practiced > 0:
            words_with_improvement = 0
            words_needing_help = 0
            
            for word_data in self.word_attempts.values():
                if len(word_data['accuracies']) >= 2:
                    if word_data['accuracies'][-1] > word_data['accuracies'][0]:
                        words_with_improvement += 1
                
                if word_data['best_accuracy'] < 50:
                    words_needing_help += 1
        else:
            words_with_improvement = 0
            words_needing_help = 0
        
        return {
            'total_words_practiced': total_words_practiced,
            'total_attempts': total_attempts,
            'session_duration_minutes': round(session_duration / 60, 1),
            'words_with_improvement': words_with_improvement,
            'words_needing_help': words_needing_help
        }
