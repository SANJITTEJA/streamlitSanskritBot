"""
Feedback Generation Module for Sanskrit Voice Bot v2
Generates intelligent feedback using LLM and traditional methods with improved architecture.
"""
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from enum import Enum

from core.config import AnalysisConfig
from analysis.llm_feedback import LLMFeedbackGenerator, LlamaFeedbackGenerator
from .llm_comparison import LLMComparison


class FeedbackType(Enum):
    """Enumeration of feedback types"""
    SINGLE_WORD = "single_word"
    FULL_SHLOKA = "full_shloka"
    ALPHABET = "alphabet"


class UserLevel(Enum):
    """Enumeration of user skill levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class FeedbackRequest:
    """Data class for feedback request parameters"""
    analysis_result: Dict[str, Any]
    user_level: UserLevel = UserLevel.BEGINNER
    feedback_type: FeedbackType = FeedbackType.FULL_SHLOKA
    context: Optional[Dict[str, Any]] = None


@dataclass
class FeedbackResponse:
    """Data class for structured feedback response"""
    feedback: str
    suggestion: Optional[str] = None
    motivation: Optional[str] = None
    practice_tips: Optional[List[str]] = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.practice_tips is None:
            self.practice_tips = []


class CircuitBreaker:
    """Circuit breaker pattern for API resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        return False
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class FeedbackStrategy(ABC):
    """Abstract base class for feedback strategies"""
    
    @abstractmethod
    def generate_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        """Generate feedback for the given request"""
        pass
    
    @abstractmethod
    def get_practice_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Get practice suggestions based on analysis"""
        pass


class SingleWordFeedbackStrategy(FeedbackStrategy):
    """Feedback strategy for single word practice"""
    
    def generate_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        """Generate feedback for single word practice"""
        analysis = request.analysis_result
        accuracy = analysis.get('accuracy', 0)
        word_results = analysis.get('word_results', [])
        
        if not word_results:
            return FeedbackResponse(
                feedback="Unable to analyze the pronunciation. Please try again.",
                confidence_score=0.0
            )
        
        word_result = word_results[0]
        original_word = word_result.get('devanagari', '')
        user_word = word_result.get('user', '')
        
        # Generate targeted feedback for single word
        if accuracy >= 80:
            feedback = f"Excellent pronunciation of '{original_word}'! Your articulation is clear and accurate."
            suggestion = "Continue practicing with similar consonant clusters to maintain this level."
        elif accuracy >= 60:
            feedback = f"Good attempt at '{original_word}'. Some sounds need refinement for clarity."
            suggestion = "Focus on the middle consonants. Practice slowly, emphasizing each sound distinctly."
        else:
            feedback = f"The pronunciation of '{original_word}' needs improvement. Focus on individual sounds."
            suggestion = "Break the word into syllables. Practice each part separately before combining."
        
        return FeedbackResponse(
            feedback=feedback,
            suggestion=suggestion,
            practice_tips=self.get_practice_suggestions(analysis),
            confidence_score=min(accuracy / 100.0, 1.0)
        )
    
    def get_practice_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Get practice suggestions for single word"""
        accuracy = analysis_result.get('accuracy', 0)
        suggestions = []
        
        if accuracy < 70:
            suggestions.extend([
                "🔤 Break the word into syllables and practice each part slowly",
                "🎯 Focus on clear pronunciation of each consonant cluster",
                "⏰ Take your time - accuracy is more important than speed"
            ])
        
        suggestions.extend([
            "🔊 Listen to the original audio multiple times",
            "🗣️ Record yourself several times and compare",
            "📖 Study the SLP1 transliteration for phonetic guidance"
        ])
        
        return suggestions


class FullShlokaFeedbackStrategy(FeedbackStrategy):
    """Feedback strategy for full shloka practice"""
    
    def generate_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        """Generate feedback for full shloka practice"""
        analysis = request.analysis_result
        accuracy = analysis.get('accuracy', 0)
        incorrect_words = analysis.get('incorrect_words', [])
        total_words = analysis.get('total_count', 0)
        correct_words = analysis.get('correct_count', 0)
        
        # Generate comprehensive feedback
        if accuracy >= 80:
            feedback = f"Excellent pronunciation! You achieved {accuracy}% accuracy with {correct_words}/{total_words} words correct."
            motivation = "Your Sanskrit pronunciation skills are developing beautifully. Continue with regular practice."
        elif accuracy >= 60:
            feedback = f"Good progress with {accuracy}% accuracy. {len(incorrect_words)} words need attention."
            motivation = "You're on the right track. Focus on the highlighted words for improvement."
        else:
            feedback = f"Keep practicing! {accuracy}% accuracy shows effort. Work on {len(incorrect_words)} specific words."
            motivation = "Every expert was once a beginner. Consistent practice will bring significant improvement."
        
        return FeedbackResponse(
            feedback=feedback,
            motivation=motivation,
            practice_tips=self.get_practice_suggestions(analysis),
            confidence_score=min(accuracy / 100.0, 1.0)
        )
    
    def get_practice_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Get practice suggestions for full shloka"""
        accuracy = analysis_result.get('accuracy', 0)
        incorrect_words = analysis_result.get('incorrect_words', [])
        suggestions = []
        
        if len(incorrect_words) > 0:
            suggestions.extend([
                f"🎯 Focus on the {len(incorrect_words)} highlighted words",
                "📝 Use the 'Practice Incorrect Words' feature",
                "🔄 Practice word by word before attempting the full shloka"
            ])
        
        if accuracy < 50:
            suggestions.extend([
                "⏰ Slow down your pronunciation significantly",
                "🎧 Listen to the original audio more carefully",
                "📚 Start with shorter practice sessions"
            ])
        elif accuracy < 70:
            suggestions.extend([
                "🔍 Pay attention to subtle differences in sounds",
                "📖 Study the SLP1 transliteration for guidance",
                "🎵 Focus on the rhythm and flow of the verse"
            ])
        
        suggestions.append("💡 Regular daily practice will improve your Sanskrit pronunciation")
        return suggestions


class LLMIntegratedFeedbackStrategy(FeedbackStrategy):
    """Enhanced LLM feedback strategy with comparison mode support"""
    
    def __init__(self):
        self.llm_feedback_generator = LLMFeedbackGenerator()
        self.llama_feedback_generator = LlamaFeedbackGenerator()
        self.llm_comparison = LLMComparison()
        
        # Track which LLM to use ('gemini', 'llama', or 'compare')
        self.selected_llm_mode = 'compare'  # Default to comparison mode
        self.circuit_breaker = CircuitBreaker()
        self.cache = {}
    
    def set_llm_mode(self, mode: str):
        """Set the LLM mode ('gemini', 'llama', or 'compare')"""
        if mode in ['gemini', 'llama', 'compare']:
            self.selected_llm_mode = mode
        else:
            raise ValueError(f"Invalid LLM mode: {mode}. Must be 'gemini', 'llama', or 'compare'")
    
    def generate_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        """Generate LLM feedback with comparison support"""
        if not self.circuit_breaker.can_execute():
            return self._fallback_feedback(request)
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            feedback_dict = None
            
            if self.selected_llm_mode == 'compare' and AnalysisConfig.USE_LLM_FEEDBACK:
                # Run comparison mode
                comparison_results = self.llm_comparison.compare_models(request.analysis_result)
                
                # Return the winner's feedback with comparison data attached
                winner = comparison_results.get('winner', 'None')
                
                if winner != 'None':
                    if 'Gemini' in winner:
                        feedback_dict = comparison_results['gemini']['feedback']
                    elif 'Llama' in winner:
                        feedback_dict = comparison_results['llama']['feedback']
                    else:
                        # Fallback to Gemini if winner is unclear
                        feedback_dict = comparison_results['gemini']['feedback'] if comparison_results['gemini']['success'] else None
                    
                    # Attach comparison data for UI display
                    if feedback_dict:
                        feedback_dict['_comparison_data'] = comparison_results
                        feedback_dict['_comparison_mode'] = True
            
            elif self.selected_llm_mode == 'gemini' and AnalysisConfig.USE_LLM_FEEDBACK:
                # Use only Gemini
                if self.llm_feedback_generator.initialized:
                    feedback_dict = self.llm_feedback_generator.generate_feedback(request.analysis_result)
            
            elif self.selected_llm_mode == 'llama' and AnalysisConfig.USE_LLM_FEEDBACK:
                # Use only Llama
                if self.llama_feedback_generator.initialized:
                    feedback_dict = self.llama_feedback_generator.generate_feedback(request.analysis_result)
            
            # Convert dictionary feedback to FeedbackResponse
            if feedback_dict:
                response = self._convert_dict_to_response(feedback_dict, request)
                self.cache[cache_key] = response
                self.circuit_breaker.record_success()
                return response
            else:
                self.circuit_breaker.record_failure()
                return self._fallback_feedback(request)
                
        except Exception as e:
            print(f"Error generating LLM feedback: {e}")
            self.circuit_breaker.record_failure()
            return self._fallback_feedback(request)
    
    def _convert_dict_to_response(self, feedback_dict: Dict[str, Any], request: FeedbackRequest) -> FeedbackResponse:
        """Convert dictionary feedback to FeedbackResponse object"""
        return FeedbackResponse(
            feedback=feedback_dict.get('feedback', 'Feedback not available'),
            suggestion=feedback_dict.get('suggestion'),
            motivation=feedback_dict.get('motivation'),
            practice_tips=self.get_practice_suggestions(request.analysis_result),
            confidence_score=0.85  # High confidence for LLM responses
        )
    
    def _generate_cache_key(self, request: FeedbackRequest) -> str:
        """Generate cache key for request"""
        analysis = request.analysis_result
        accuracy = analysis.get('accuracy', 0)
        feedback_type = request.feedback_type.value
        return f"{self.selected_llm_mode}_{feedback_type}_{accuracy}_{request.user_level.value}"
    
    def _fallback_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        """Provide fallback feedback when LLM is unavailable"""
        if request.feedback_type == FeedbackType.SINGLE_WORD:
            strategy = SingleWordFeedbackStrategy()
        else:
            strategy = FullShlokaFeedbackStrategy()
        
        return strategy.generate_feedback(request)
    
    def get_practice_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Get practice suggestions based on analysis"""
        accuracy = analysis_result.get('accuracy', 0)
        analysis_type = analysis_result.get('analysis_type', 'full_shloka')
        incorrect_words = analysis_result.get('incorrect_words', [])
        
        suggestions = []
        
        if analysis_type == 'single_word':
            if accuracy < 70:
                suggestions.extend([
                    "🔤 Break this word into syllables and practice each part slowly",
                    "🎯 Focus on clear pronunciation of each sound",
                    "⏰ Take your time - accuracy is more important than speed"
                ])
            
            suggestions.extend([
                "🔊 Listen to the original audio multiple times",
                "🗣️ Record yourself several times and compare",
                "📖 Study the SLP1 transliteration for phonetic guidance"
            ])
        else:
            if len(incorrect_words) > 0:
                suggestions.extend([
                    f"🎯 Focus on the {len(incorrect_words)} highlighted words",
                    "📝 Use the 'Practice Incorrect Words' feature",
                    "🔄 Practice word by word before attempting the full shloka"
                ])
            
            if accuracy < 50:
                suggestions.extend([
                    "⏰ Slow down your pronunciation significantly",
                    "🎧 Listen to the original audio more carefully",
                    "📚 Start with shorter practice sessions"
                ])
            elif accuracy < 70:
                suggestions.extend([
                    "🔍 Pay attention to subtle differences in sounds",
                    "📖 Study the SLP1 transliteration for guidance",
                    "🎵 Focus on the rhythm and flow of the verse"
                ])
            
            suggestions.append("💡 Regular daily practice will improve your Sanskrit pronunciation")
        
        return suggestions


class FeedbackFactory:
    """Factory for creating appropriate feedback strategies"""
    
    @staticmethod
    def create_strategy(use_llm: bool = True, feedback_type: FeedbackType = FeedbackType.FULL_SHLOKA) -> FeedbackStrategy:
        """Create appropriate feedback strategy"""
        if use_llm and AnalysisConfig.USE_LLM_FEEDBACK:
            return LLMIntegratedFeedbackStrategy()
        elif feedback_type == FeedbackType.SINGLE_WORD:
            return SingleWordFeedbackStrategy()
        else:
            return FullShlokaFeedbackStrategy()


class FeedbackGenerator:
    """
    Enhanced feedback generator with improved architecture and error handling.
    
    This class provides:
    - Strategy pattern for different feedback types
    - Circuit breaker for API resilience
    - Caching for performance
    - Comprehensive error handling
    """
    
    def __init__(self):
        """Initialize the FeedbackGenerator with strategy pattern"""
        self.strategies = {}
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize different feedback strategies"""
        self.strategies = {
            'llm': FeedbackFactory.create_strategy(use_llm=True),
            'single_word': FeedbackFactory.create_strategy(use_llm=False, feedback_type=FeedbackType.SINGLE_WORD),
            'full_shloka': FeedbackFactory.create_strategy(use_llm=False, feedback_type=FeedbackType.FULL_SHLOKA)
        }
    
    def generate_feedback(self, analysis_result: Dict[str, Any], 
                        user_level: str = "beginner") -> Optional[Dict[str, str]]:
        """
        Generate personalized feedback based on pronunciation analysis.
        
        Args:
            analysis_result: Dictionary containing analysis data
            user_level: User's skill level (beginner, intermediate, advanced)
            
        Returns:
            Dictionary containing structured feedback or None if generation fails
        """
        try:
            # Create feedback request
            request = self._create_feedback_request(analysis_result, user_level)
            
            # Determine strategy
            strategy_key = self._select_strategy(request)
            strategy = self.strategies.get(strategy_key)
            
            if not strategy:
                return self._generate_fallback_feedback(analysis_result)
            
            # Generate feedback
            response = strategy.generate_feedback(request)
            
            # Convert to legacy format for compatibility
            return self._convert_to_legacy_format(response)
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return self._generate_fallback_feedback(analysis_result)
    
    def _create_feedback_request(self, analysis_result: Dict[str, Any], user_level: str) -> FeedbackRequest:
        """Create a structured feedback request"""
        # Convert string level to enum
        try:
            level_enum = UserLevel(user_level.lower())
        except ValueError:
            level_enum = UserLevel.BEGINNER
        
        # Determine feedback type
        analysis_type = analysis_result.get('analysis_type', 'full_shloka')
        if analysis_type == 'single_word':
            feedback_type = FeedbackType.SINGLE_WORD
        else:
            feedback_type = FeedbackType.FULL_SHLOKA
        
        return FeedbackRequest(
            analysis_result=analysis_result,
            user_level=level_enum,
            feedback_type=feedback_type
        )
    
    def _select_strategy(self, request: FeedbackRequest) -> str:
        """Select appropriate strategy based on request"""
        # Use LLM if available and enabled
        if AnalysisConfig.USE_LLM_FEEDBACK:
            llm_strategy = self.strategies.get('llm')
            if isinstance(llm_strategy, LLMIntegratedFeedbackStrategy):
                return 'llm'
        
        # Fall back to appropriate rule-based strategy
        if request.feedback_type == FeedbackType.SINGLE_WORD:
            return 'single_word'
        else:
            return 'full_shloka'
    
    def _convert_to_legacy_format(self, response: FeedbackResponse) -> Dict[str, str]:
        """Convert new response format to legacy format for compatibility"""
        result = {"feedback": response.feedback}
        
        if response.suggestion:
            result["suggestion"] = response.suggestion
        
        if response.motivation:
            result["motivation"] = response.motivation
        
        return result
    
    def _generate_fallback_feedback(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Generate simple fallback feedback when all strategies fail"""
        accuracy = analysis_result.get('accuracy', 0)
        
        if accuracy >= 80:
            message = "Excellent pronunciation! Keep up the great work with your Sanskrit practice."
        elif accuracy >= 60:
            message = "Good progress in your pronunciation. Continue practicing for further improvement."
        else:
            message = "Keep practicing! Regular practice will significantly improve your Sanskrit pronunciation."
        
        return {"feedback": message}
    
    def get_practice_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """
        Get practice suggestions using the appropriate strategy.
        
        Args:
            analysis_result: Analysis results dictionary
            
        Returns:
            List of practice suggestions
        """
        try:
            # Create request to determine appropriate strategy
            request = self._create_feedback_request(analysis_result, "beginner")
            strategy_key = self._select_strategy(request)
            strategy = self.strategies.get(strategy_key)
            
            if strategy:
                return strategy.get_practice_suggestions(analysis_result)
            else:
                return self._get_default_suggestions(analysis_result)
                
        except Exception as e:
            print(f"Error getting practice suggestions: {e}")
            return self._get_default_suggestions(analysis_result)
    
    def _get_default_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Get default practice suggestions as fallback"""
        accuracy = analysis_result.get('accuracy', 0)
        suggestions = [
            "🎯 Practice regularly for consistent improvement",
            "🔊 Listen carefully to the reference pronunciation",
            "📖 Study the Sanskrit text and transliteration"
        ]
        
        if accuracy < 70:
            suggestions.append("⏰ Focus on accuracy over speed")
        
        return suggestions
    
    # Legacy methods for backward compatibility
    def _try_initialize_llm(self) -> bool:
        """Legacy method - functionality moved to LLMIntegratedFeedbackStrategy"""
        llm_strategy = self.strategies.get('llm')
        if isinstance(llm_strategy, LLMIntegratedFeedbackStrategy):
            return (llm_strategy.llm_feedback_generator.initialized or 
                   llm_strategy.llama_feedback_generator.initialized)
        return False
    
    def generate_traditional_feedback(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Legacy method for backward compatibility"""
        request = self._create_feedback_request(analysis_result, "beginner")
        
        if request.feedback_type == FeedbackType.SINGLE_WORD:
            strategy = self.strategies.get('single_word')
        else:
            strategy = self.strategies.get('full_shloka')
        
        if strategy:
            response = strategy.generate_feedback(request)
            return self._convert_to_legacy_format(response)
        else:
            return self._generate_fallback_feedback(analysis_result)
    
    @property
    def initialized(self) -> bool:
        """Check if any feedback strategy is available"""
        return len(self.strategies) > 0
    
    def set_llm_mode(self, mode: str):
        """Set the LLM mode for comparison ('gemini', 'llama', or 'compare')"""
        llm_strategy = self.strategies.get('llm')
        if isinstance(llm_strategy, LLMIntegratedFeedbackStrategy):
            llm_strategy.set_llm_mode(mode)
        else:
            print(f"Cannot set LLM mode: LLM strategy not available")
    
    def get_llm_mode(self) -> str:
        """Get the current LLM mode"""
        llm_strategy = self.strategies.get('llm')
        if isinstance(llm_strategy, LLMIntegratedFeedbackStrategy):
            return llm_strategy.selected_llm_mode
        return 'none'
