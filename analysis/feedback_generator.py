"""
Simplified Feedback Generator for Sanskrit Voice Bot v2
Uses Gemini directly for AI-powered feedback
"""
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

from typing import Dict, Any, Optional, List
from core.config import AnalysisConfig


class FeedbackGenerator:
    """Simple feedback generator using Gemini LLM"""
    
    def __init__(self):
        self.model = None
        self.initialized = False
        self._try_initialize()
    
    def _try_initialize(self) -> bool:
        """Initialize Gemini API"""
        if not GENAI_AVAILABLE:
            return False
        try:
            if AnalysisConfig.GEMINI_API_KEY:
                genai.configure(api_key=AnalysisConfig.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(AnalysisConfig.GEMINI_MODEL)
                self.initialized = True
                return True
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
        return False
    
    def generate_feedback(self, analysis_result: Dict[str, Any], user_level: str = "beginner") -> Optional[Dict[str, str]]:
        """Generate feedback based on pronunciation analysis"""
        
        if not self.initialized and not self._try_initialize():
            return self._simple_feedback(analysis_result)
        
        try:
            accuracy = analysis_result.get('accuracy', 0)
            incorrect_words = analysis_result.get('incorrect_words', [])
            total_words = analysis_result.get('total_count', 0)
            correct_words = analysis_result.get('correct_count', 0)
            
            prompt = f"""You are a supportive Sanskrit pronunciation coach.

STUDENT RESULTS:
- Accuracy: {accuracy:.1f}%
- Words correct: {correct_words}/{total_words}
- Mispronounced words: {', '.join([w.get('original', '') for w in incorrect_words[:5]]) or 'None'}
- Level: {user_level}

Provide brief, encouraging feedback in this exact format:

FEEDBACK: [2-3 sentences about their performance and specific areas to improve]

MOTIVATION: [2 encouraging sentence to keep them practicing]

TIPS: [2-3 lines about their oral positioning and breathing techniques]

Keep it concise and supportive."""

            response = self.model.generate_content(prompt)
            
            if response and hasattr(response, 'text'):
                return self._parse_response(response.text, accuracy)
            
        except Exception as e:
            print(f"Gemini error: {e}")
        
        return self._simple_feedback(analysis_result)
    
    def _parse_response(self, text: str, accuracy: float) -> Dict[str, str]:
        """Parse Gemini response into structured feedback"""
        feedback = "Great effort!"
        motivation = "Keep practicing!"
        tips = []
        
        lines = text.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('FEEDBACK:'):
                current_section = 'feedback'
                feedback = line.replace('FEEDBACK:', '').strip()
            elif line.startswith('MOTIVATION:'):
                current_section = 'motivation'
                motivation = line.replace('MOTIVATION:', '').strip()
            elif line.startswith('TIPS:'):
                current_section = 'tips'
                # Check if tips are on the same line as TIPS:
                tip_content = line.replace('TIPS:', '').strip()
                if tip_content:
                    tips.append(tip_content)
            elif current_section == 'feedback' and line:
                feedback += ' ' + line
            elif current_section == 'motivation' and line:
                motivation += ' ' + line
            elif current_section == 'tips' and line:
                # Accept any line format: bullets, numbers, or plain text
                cleaned = line.lstrip('-•*0123456789.) ')
                if cleaned:
                    tips.append(cleaned)
        
        return {
            'feedback': feedback,
            'motivation': motivation,
            'practice_tips': tips if tips else self._default_tips(accuracy)
        }
    
    def _simple_feedback(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Fallback feedback when Gemini unavailable"""
        accuracy = analysis_result.get('accuracy', 0)
        
        if accuracy >= 90:
            feedback = "Excellent pronunciation! Your chanting is very accurate."
            motivation = "Outstanding work! You're mastering Sanskrit pronunciation."
        elif accuracy >= 70:
            feedback = f"Good job! You achieved {accuracy:.1f}% accuracy. Keep refining your pronunciation."
            motivation = "You're making great progress!"
        else:
            feedback = f"Keep practicing! You achieved {accuracy:.1f}% accuracy. Focus on the highlighted words."
            motivation = "Every practice session brings improvement!"
        
        return {
            'feedback': feedback,
            'motivation': motivation,
            'practice_tips': self._default_tips(accuracy)
        }
    
    def _default_tips(self, accuracy: float) -> List[str]:
        """Default practice tips based on accuracy"""
        if accuracy >= 90:
            return ["Try practicing at a faster pace", "Move on to more challenging shlokas"]
        elif accuracy >= 70:
            return ["Listen to the original audio again", "Focus on words you missed"]
        else:
            return ["Break the shloka into smaller parts", "Practice each word slowly", "Repeat multiple times"]
