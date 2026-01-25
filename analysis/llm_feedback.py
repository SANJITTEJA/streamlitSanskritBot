"""
LLM Feedback Module for Sanskrit Voice Bot v2
Uses Google's Gemini API and Llama to generate personalized, empathetic feedback
for Sanskrit pronunciation practice.
"""

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

import requests
import json
from typing import Dict, List, Any, Optional

from core.config import AnalysisConfig


def init_gemini_api():
    """Initialize the Gemini API with the API key"""
    try:
        if hasattr(AnalysisConfig, 'GEMINI_API_KEY') and AnalysisConfig.GEMINI_API_KEY:
            genai.configure(api_key=AnalysisConfig.GEMINI_API_KEY)
            return True
        else:
            print("Gemini API key not configured")
            return False
    except Exception as e:
        print(f"Error initializing Gemini API: {e}")
        return False


class LLMFeedbackGenerator:
    """Class for generating personalized feedback using Gemini LLM"""
    
    def __init__(self):
        """Initialize the LLM feedback generator"""
        self.model = None
        self.initialized = False
        self.try_initialize()
    
    def try_initialize(self):
        """Attempt to initialize the Gemini model"""
        try:
            if init_gemini_api():
                # Use the configured Gemini model
                model_name = getattr(AnalysisConfig, 'GEMINI_MODEL', 'gemini-2.5-flash')
                self.model = genai.GenerativeModel(model_name)
                self.initialized = True
                return True
            return False
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            return False
    
    def generate_feedback(self, analysis_result: Dict[str, Any], 
                        user_level: str = "beginner") -> Optional[Dict[str, str]]:
        """
        Generate empathetic feedback based on pronunciation analysis
        
        Args:
            analysis_result: Dictionary containing analysis data
            user_level: Proficiency level of the user (beginner/intermediate/advanced)
            
        Returns:
            Dictionary containing feedback text and motivational message
        """
        if not self.initialized:
            if not self.try_initialize():
                return None  # Don't display feedback if LLM is unavailable
        
        try:
            # Extract relevant information from analysis result
            accuracy = analysis_result.get('accuracy', 0)
            analysis_type = analysis_result.get('analysis_type', 'full_shloka')
            incorrect_words = analysis_result.get('incorrect_words', [])
            incorrect_count = len(incorrect_words)
            
            # Create context for the LLM
            context = self._create_feedback_context(
                analysis_result, user_level, accuracy, analysis_type, incorrect_count
            )
            
            # Generate personalized feedback
            response = self.model.generate_content(context)
            
            if not response or not hasattr(response, 'text'):
                return None  # Don't display feedback if LLM response is invalid
            
            # Parse the LLM response
            feedback_text = response.text
            
            # Format the feedback based on analysis type and accuracy
            return self._format_feedback(feedback_text, analysis_type, accuracy)
            
        except Exception as e:
            print(f"Error generating LLM feedback: {e}")
            return None  # Don't display feedback if there's an error
    
    def _create_feedback_context(self, analysis_result: Dict[str, Any], 
                               user_level: str, accuracy: float, 
                               analysis_type: str, incorrect_count: int) -> str:
        """Create the context prompt for the LLM with Chain of Thought reasoning"""
        
        # Basic context based on analysis type
        if analysis_type == 'single_word':
            word_data = analysis_result['word_results'][0] if analysis_result['word_results'] else {}
            original_word = word_data.get('original', '')
            user_word = word_data.get('user', '')
            
            # Extract detailed phonetic differences
            phonetic_details = self._analyze_phonetic_differences(original_word, user_word)
            
            context = f"""
            You are an expert Sanskrit pronunciation coach with deep knowledge of phonetics and oral positioning.
            
            CONTEXT:
            - Target word: "{original_word}"
            - User's pronunciation (transcribed): "{user_word}"
            - Accuracy: {accuracy}%
            - Student level: {user_level}
            - Phonetic analysis: {phonetic_details}
            
            TASK: Use Chain of Thought reasoning to provide comprehensive feedback.
            
            Think through this step-by-step:
            1. First, identify the specific phonetic errors (which sounds were mispronounced)
            2. Then, explain WHY these errors occurred (common causes: tongue position, aspiration, vowel length, etc.)
            3. Next, describe the CORRECT oral/articulatory positions needed
            4. Finally, provide encouragement and a clear practice strategy
            
            Format your response EXACTLY as follows:
            
            ANALYSIS:
            **** [Step 1-2: Identify the specific phonetic errors and explain why they occurred. Be technical but clear.]
            
            ORAL_POSITION:
            **** [Step 3: Detailed instructions on tongue placement, lip shape, airflow, and other articulatory features needed for correct pronunciation.]
            
            MOTIVATION:
            **** [Step 4: Encouraging message with specific practice recommendations to improve.]
            
            Keep each section focused and under 50 words. Use Sanskrit phonetic terminology where appropriate.
            """
        else:
            # Full shloka context
            total_words = analysis_result.get('total_count', 0)
            correct_words = analysis_result.get('correct_count', 0)
            incorrect_words = analysis_result.get('incorrect_words', [])
            
            # Build detailed error pattern analysis
            error_patterns = self._identify_error_patterns(incorrect_words)
            
            context = f"""
            You are an expert Sanskrit pronunciation coach with deep knowledge of phonetics and oral positioning.
            
            CONTEXT:
            - Practice type: Full verse (shloka)
            - Overall accuracy: {accuracy}%
            - Words correct: {correct_words}/{total_words}
            - Words with errors: {incorrect_count}
            - Student level: {user_level}
            - Error patterns observed: {error_patterns}
            
            TASK: Use Chain of Thought reasoning to provide comprehensive feedback.
            
            Think through this step-by-step:
            1. First, identify the PATTERNS in pronunciation errors (which types of sounds are problematic)
            2. Then, explain the likely CAUSES (tongue positioning, aspiration control, vowel length, etc.)
            3. Next, describe specific TECHNIQUES and oral positions to fix these patterns
            4. Finally, provide strategic motivation for continued practice
            
            Format your response EXACTLY as follows:
            
            ANALYSIS:
            **** [Step 1-2: Identify error patterns and explain their root causes. Be specific about phonetic categories.]
            
            TECHNIQUE:
            **** [Step 3: Specific techniques and oral positioning guidance to address the identified patterns.]
            
            MOTIVATION:
            **** [Step 4: Strategic encouragement with a clear improvement plan based on their current performance.]
            
            Keep each section focused and under 50 words. Be encouraging yet technical.
            """
        
        return context
    
    def _format_feedback(self, feedback_text: str, analysis_type: str, accuracy: float) -> Dict[str, str]:
        """Format the LLM response into structured feedback"""
        # Split feedback into sections
        sections = feedback_text.split("\n\n")
        feedback_parts = {}
        
        # Define section mappings based on analysis type
        if analysis_type == 'single_word':
            section_keys = ['ANALYSIS:', 'ORAL_POSITION:', 'MOTIVATION:']
            output_keys = ['feedback', 'suggestion', 'motivation']
        else:
            section_keys = ['ANALYSIS:', 'TECHNIQUE:', 'MOTIVATION:']
            output_keys = ['feedback', 'suggestion', 'motivation']
        
        # Process each section
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            lines = section.split("\n")
            
            # Check which section this is
            for i, section_key in enumerate(section_keys):
                if any(line.startswith(section_key) for line in lines):
                    # Extract content, handling asterisk formatting
                    content = []
                    for line in lines:
                        if line.startswith(section_key):
                            continue
                        if line.startswith("****"):
                            content.append(line.replace("****", "").strip())
                        else:
                            content.append(line.strip())
                    
                    if content:
                        feedback_parts[output_keys[i]] = " ".join(content).strip()
                    break
        
        # If parsing failed, try direct section extraction
        if "feedback" not in feedback_parts:
            for i, section_key in enumerate(section_keys):
                section_match = self._extract_section(feedback_text, section_key)
                if section_match:
                    feedback_parts[output_keys[i]] = section_match
                
        # Last resort: use the whole text as feedback
        if not feedback_parts:
            feedback_parts["feedback"] = feedback_text.strip()
        
        # Clean up any asterisks that might remain
        for key in feedback_parts:
            feedback_parts[key] = feedback_parts[key].replace("****", "").strip()
        
        return feedback_parts
        
    def _extract_section(self, text: str, section_marker: str) -> Optional[str]:
        """Extract a section from the text based on the marker"""
        if section_marker not in text:
            return None
            
        start_idx = text.find(section_marker) + len(section_marker)
        
        # Find the next section marker or end of text
        next_markers = ["FEEDBACK:", "SUGGESTION:", "MOTIVATION:", "ANALYSIS:", "ORAL_POSITION:", "TECHNIQUE:"]
        end_indices = []
        
        for marker in next_markers:
            if marker == section_marker:
                continue
                
            idx = text.find(marker, start_idx)
            if idx != -1:
                end_indices.append(idx)
        
        if end_indices:
            end_idx = min(end_indices)
            section_text = text[start_idx:end_idx]
        else:
            section_text = text[start_idx:]
            
        # Clean up the section text
        lines = section_text.strip().split("\n")
        content = []
        for line in lines:
            line = line.strip()
            if line.startswith("****"):
                content.append(line.replace("****", "").strip())
            elif line:
                content.append(line)
                
        return " ".join(content).strip()
    
    def _analyze_phonetic_differences(self, original: str, user: str) -> str:
        """Analyze phonetic differences between original and user pronunciation"""
        if not original or not user:
            return "No phonetic data available"
        
        differences = []
        
        # Check for length differences
        if len(original) != len(user):
            differences.append(f"Length mismatch: expected {len(original)} chars, got {len(user)}")
        
        # Character-level comparison
        mismatches = []
        for i, (o_char, u_char) in enumerate(zip(original, user)):
            if o_char != u_char:
                mismatches.append(f"Position {i+1}: '{o_char}' → '{u_char}'")
        
        if mismatches:
            differences.extend(mismatches[:3])  # Limit to first 3 for brevity
        
        return "; ".join(differences) if differences else "Minor variations detected"
    
    def _identify_error_patterns(self, incorrect_words: List[Dict[str, Any]]) -> str:
        """Identify common patterns in pronunciation errors"""
        if not incorrect_words:
            return "No errors detected"
        
        patterns = []
        
        # Count types of errors
        aspirated_errors = 0
        vowel_errors = 0
        consonant_errors = 0
        
        for word in incorrect_words[:5]:  # Analyze first 5 words
            original = word.get('slp1', '').lower()
            user = word.get('user', '').lower()
            
            # Check for aspirated consonant issues (kh, gh, ch, jh, th, dh, ph, bh)
            if any(asp in original for asp in ['kh', 'gh', 'ch', 'jh', 'th', 'dh', 'ph', 'bh']):
                if original != user:
                    aspirated_errors += 1
            
            # Check for vowel issues (a, i, u, e, o, long vowels)
            if any(v in original for v in ['A', 'I', 'U', 'E', 'O']):
                if original != user:
                    vowel_errors += 1
            
            # General consonant issues
            if original != user:
                consonant_errors += 1
        
        if aspirated_errors > 0:
            patterns.append(f"{aspirated_errors} aspirated consonant errors")
        if vowel_errors > 0:
            patterns.append(f"{vowel_errors} vowel length/quality errors")
        if consonant_errors > 0:
            patterns.append(f"{consonant_errors} general articulation errors")
        
        return "; ".join(patterns) if patterns else "Mixed pronunciation issues"


class LlamaFeedbackGenerator:
    """Class for generating personalized feedback using Llama LLM via Ollama"""
    
    def __init__(self, model_name: str = "llama3.2"):
        """Initialize the Llama feedback generator
        
        Args:
            model_name: The Llama model to use (default: llama3.2)
        """
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api/generate"
        self.initialized = False
        self.try_initialize()
    
    def try_initialize(self) -> bool:
        """Attempt to check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                # Check if our model is available
                model_available = any(self.model_name in model.get('name', '') for model in models)
                if model_available:
                    self.initialized = True
                    print(f"Llama model '{self.model_name}' is available")
                    return True
                else:
                    print(f"Llama model '{self.model_name}' not found. Available models: {[m.get('name') for m in models]}")
                    return False
            return False
        except Exception as e:
            print(f"Error initializing Llama model (Ollama may not be running): {e}")
            return False
    
    def generate_feedback(self, analysis_result: Dict[str, Any], 
                        user_level: str = "beginner") -> Optional[Dict[str, str]]:
        """
        Generate empathetic feedback based on pronunciation analysis
        
        Args:
            analysis_result: Dictionary containing analysis data
            user_level: Proficiency level of the user (beginner/intermediate/advanced)
            
        Returns:
            Dictionary containing feedback text and motivational message
        """
        if not self.initialized:
            if not self.try_initialize():
                return None  # Don't display feedback if LLM is unavailable
        
        try:
            # Extract relevant information from analysis result
            accuracy = analysis_result.get('accuracy', 0)
            analysis_type = analysis_result.get('analysis_type', 'full_shloka')
            incorrect_words = analysis_result.get('incorrect_words', [])
            incorrect_count = len(incorrect_words)
            
            # Create a simpler, more focused prompt for Llama
            context = self._create_llama_prompt(
                analysis_result, user_level, accuracy, analysis_type, incorrect_count
            )
            
            # Call Ollama API with adjusted settings
            payload = {
                "model": self.model_name,
                "prompt": context,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 500,  # Limit response length
                    "stop": ["---", "###"]  # Stop sequences
                }
            }
            
            print(f"📡 Sending request to Llama ({self.model_name})...")
            response = requests.post(self.base_url, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"Llama API error: {response.status_code}")
                if response.text:
                    print(f"Error details: {response.text[:200]}")
                return None
            
            response_data = response.json()
            feedback_text = response_data.get('response', '')
            
            if not feedback_text:
                print("Empty response from Llama")
                return None
            
            print(f"✅ Received Llama response ({len(feedback_text)} chars)")
            
            # Format the feedback based on analysis type and accuracy
            gemini_gen = LLMFeedbackGenerator()
            return gemini_gen._format_feedback(feedback_text, analysis_type, accuracy)
            
        except requests.exceptions.Timeout:
            print(f"Llama request timed out after 60s")
            return None
        except Exception as e:
            print(f"Error generating Llama feedback: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_llama_prompt(self, analysis_result: Dict[str, Any], 
                            user_level: str, accuracy: float, 
                            analysis_type: str, incorrect_count: int) -> str:
        """Create a simpler prompt optimized for Llama"""
        
        if analysis_type == 'single_word':
            word_data = analysis_result['word_results'][0] if analysis_result['word_results'] else {}
            original_word = word_data.get('original', '')
            user_word = word_data.get('user', '')
            
            prompt = f"""You are a Sanskrit pronunciation coach. A {user_level} student practiced pronouncing "{original_word}" but said "{user_word}" (accuracy: {accuracy}%).

Provide feedback in exactly 3 sections:

ANALYSIS:
Identify the specific pronunciation errors and explain why they occurred (aspiration, tongue position, vowel length, etc.). Be concise (max 40 words).

ORAL_POSITION:
Describe the correct tongue placement, lip shape, and airflow needed for proper pronunciation. Be specific (max 40 words).

MOTIVATION:
Give encouraging feedback with clear next steps for practice (max 30 words).

Begin your response now:"""
        else:
            # Full shloka
            total_words = analysis_result.get('total_count', 0)
            correct_words = analysis_result.get('correct_count', 0)
            
            prompt = f"""You are a Sanskrit pronunciation coach. A {user_level} student practiced a verse with {accuracy}% accuracy ({correct_words}/{total_words} words correct, {incorrect_count} words need work).

Provide feedback in exactly 3 sections:

ANALYSIS:
Identify the main pronunciation patterns that need improvement (aspirated consonants, vowels, etc.). Be concise (max 40 words).

TECHNIQUE:
Provide specific techniques and oral positioning to fix these patterns (max 40 words).

MOTIVATION:
Give strategic encouragement with a practice plan (max 30 words).

Begin your response now:"""
        
        return prompt