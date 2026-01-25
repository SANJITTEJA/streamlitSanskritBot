"""
LLM Metrics Evaluation Module for Sanskrit Voice Bot v2
Calculates detailed metrics to compare LLM feedback quality including:
- Sentiment polarity
- Coherence and readability
- Helpfulness and actionability
- Technical accuracy
- Response length and completeness
"""

import re
from typing import Dict, List, Any, Optional
import time

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TextBlob = None
    TEXTBLOB_AVAILABLE = False


class LLMMetricsEvaluator:
    """Evaluate and compare feedback from different LLMs"""
    
    def __init__(self):
        """Initialize the metrics evaluator"""
        # Sanskrit-specific technical terms for accuracy checking
        self.sanskrit_phonetic_terms = [
            'tongue', 'palatal', 'dental', 'retroflex', 'aspirated', 'aspiration',
            'vowel', 'consonant', 'guttural', 'labial', 'cerebral', 'nasal',
            'sibilant', 'visarga', 'anusvara', 'chandrabindu', 'voiced', 'unvoiced',
            'short vowel', 'long vowel', 'diphthong', 'semivowel', 'fricative',
            'plosive', 'velar', 'glottal', 'alveolar', 'soft palate', 'hard palate',
            'tip of tongue', 'root of tongue', 'lips', 'teeth', 'airflow', 'breath'
        ]
        
        # Motivational keywords
        self.motivational_words = [
            'practice', 'improve', 'progress', 'keep', 'continue', 'great', 'good',
            'excellent', 'well done', 'better', 'try', 'focus', 'work', 'master',
            'succeed', 'achieve', 'build', 'develop', 'strengthen', 'enhance'
        ]
        
    def evaluate_feedback(self, feedback: Dict[str, str], 
                         analysis_result: Dict[str, Any],
                         model_name: str,
                         generation_time: float = 0) -> Dict[str, Any]:
        """
        Evaluate a single feedback response with comprehensive metrics
        
        Args:
            feedback: Dictionary containing feedback sections
            analysis_result: Original analysis result for context
            model_name: Name of the LLM model
            generation_time: Time taken to generate feedback (seconds)
            
        Returns:
            Dictionary containing all calculated metrics
        """
        if not feedback:
            return self._empty_metrics(model_name)
        
        # Combine all feedback text for overall analysis
        full_text = " ".join([
            feedback.get('feedback', ''),
            feedback.get('suggestion', ''),
            feedback.get('motivation', '')
        ])
        
        metrics = {
            'model_name': model_name,
            'generation_time': generation_time,
            'timestamp': time.time()
        }
        
        # Calculate individual metrics
        metrics.update(self._calculate_sentiment_metrics(full_text, feedback))
        metrics.update(self._calculate_coherence_metrics(full_text, feedback))
        metrics.update(self._calculate_helpfulness_metrics(full_text, feedback))
        metrics.update(self._calculate_technical_accuracy(full_text, feedback))
        metrics.update(self._calculate_completeness_metrics(feedback))
        metrics.update(self._calculate_structure_metrics(feedback))
        
        # Calculate overall quality score (weighted average)
        metrics['overall_quality_score'] = self._calculate_overall_score(metrics)
        
        return metrics
    
    def _calculate_sentiment_metrics(self, full_text: str, feedback: Dict[str, str]) -> Dict[str, float]:
        """Calculate sentiment polarity and subjectivity"""
        try:
            if TEXTBLOB_AVAILABLE and TextBlob:
                blob = TextBlob(full_text)
                
                # Overall sentiment
                polarity = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
                
                # Section-specific sentiment
                feedback_polarity = TextBlob(feedback.get('feedback', '')).sentiment.polarity
                suggestion_polarity = TextBlob(feedback.get('suggestion', '')).sentiment.polarity
                motivation_polarity = TextBlob(feedback.get('motivation', '')).sentiment.polarity
                
                # Normalized polarity (0-100 scale, where 50 is neutral)
                normalized_polarity = (polarity + 1) * 50
                
                # Positivity score (ideal is slightly positive for motivation)
                positivity_score = min(100, max(0, (polarity + 0.5) * 66.67))
                
                return {
                    'sentiment_polarity': polarity,
                    'sentiment_subjectivity': subjectivity,
                    'normalized_polarity': normalized_polarity,
                    'positivity_score': positivity_score,
                    'feedback_section_polarity': feedback_polarity,
                    'suggestion_section_polarity': suggestion_polarity,
                    'motivation_section_polarity': motivation_polarity
                }
            else:
                # Fallback when TextBlob is not available
                return self._simple_sentiment_analysis(full_text, feedback)
        except Exception as e:
            print(f"Error calculating sentiment: {e}")
            return {
                'sentiment_polarity': 0,
                'sentiment_subjectivity': 0.5,
                'normalized_polarity': 50,
                'positivity_score': 50,
                'feedback_section_polarity': 0,
                'suggestion_section_polarity': 0,
                'motivation_section_polarity': 0
            }
    
    def _simple_sentiment_analysis(self, full_text: str, feedback: Dict[str, str]) -> Dict[str, float]:
        """Simple sentiment analysis fallback when TextBlob is unavailable"""
        positive_words = ['good', 'great', 'excellent', 'better', 'improve', 'progress', 'success']
        negative_words = ['error', 'wrong', 'incorrect', 'bad', 'poor', 'difficult', 'problem']
        
        words = full_text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Simple polarity calculation
        if len(words) > 0:
            polarity = (positive_count - negative_count) / len(words) * 10  # Scale to roughly -1 to 1
            polarity = max(-1, min(1, polarity))
        else:
            polarity = 0
        
        normalized_polarity = (polarity + 1) * 50
        positivity_score = min(100, max(0, (polarity + 0.5) * 66.67))
        
        return {
            'sentiment_polarity': polarity,
            'sentiment_subjectivity': 0.5,  # Default neutral
            'normalized_polarity': normalized_polarity,
            'positivity_score': positivity_score,
            'feedback_section_polarity': polarity,
            'suggestion_section_polarity': polarity,
            'motivation_section_polarity': polarity
        }
    
    def _calculate_coherence_metrics(self, full_text: str, feedback: Dict[str, str]) -> Dict[str, float]:
        """Calculate coherence, readability, and clarity metrics"""
        if not full_text:
            return {
                'word_count': 0,
                'sentence_count': 0,
                'avg_sentence_length': 0,
                'readability_score': 0,
                'clarity_score': 0
            }
        
        # Basic text statistics
        words = full_text.split()
        word_count = len(words)
        
        # Count sentences (split by . ! ?)
        sentences = re.split(r'[.!?]+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability score (simpler = better, based on avg sentence length)
        # Ideal: 10-20 words per sentence
        if 10 <= avg_sentence_length <= 20:
            readability_score = 100
        elif avg_sentence_length < 10:
            readability_score = 60 + (avg_sentence_length * 4)
        else:
            readability_score = max(0, 100 - ((avg_sentence_length - 20) * 3))
        
        # Clarity score: based on use of transition words and coherence markers
        transition_words = ['first', 'then', 'next', 'finally', 'however', 'therefore', 
                          'because', 'thus', 'additionally', 'moreover', 'furthermore']
        transition_count = sum(1 for word in words if word.lower() in transition_words)
        clarity_score = min(100, (transition_count / max(1, sentence_count)) * 200)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'readability_score': round(readability_score, 2),
            'clarity_score': round(clarity_score, 2)
        }
    
    def _calculate_helpfulness_metrics(self, full_text: str, feedback: Dict[str, str]) -> Dict[str, float]:
        """Calculate actionability and helpfulness metrics"""
        if not full_text:
            return {
                'actionability_score': 0,
                'specificity_score': 0,
                'motivational_score': 0
            }
        
        words = full_text.lower().split()
        
        # Actionability: presence of action verbs and imperative instructions
        action_verbs = ['place', 'position', 'move', 'touch', 'press', 'release', 
                       'hold', 'make', 'produce', 'practice', 'focus', 'try', 
                       'ensure', 'keep', 'maintain', 'adjust', 'control']
        action_count = sum(1 for word in words if word in action_verbs)
        actionability_score = min(100, (action_count / max(1, len(words))) * 500)
        
        # Specificity: mentions of specific body parts and technical terms
        specific_terms = ['tongue', 'lips', 'teeth', 'palate', 'throat', 'mouth',
                         'position', 'placement', 'sound', 'breath', 'air']
        specificity_count = sum(1 for word in words if word in specific_terms)
        specificity_score = min(100, (specificity_count / max(1, len(words))) * 400)
        
        # Motivational content
        motivation_count = sum(1 for word in words if word in self.motivational_words)
        motivational_score = min(100, (motivation_count / max(1, len(words))) * 300)
        
        return {
            'actionability_score': round(actionability_score, 2),
            'specificity_score': round(specificity_score, 2),
            'motivational_score': round(motivational_score, 2)
        }
    
    def _calculate_technical_accuracy(self, full_text: str, feedback: Dict[str, str]) -> Dict[str, float]:
        """Calculate technical accuracy and terminology usage"""
        if not full_text:
            return {
                'technical_term_count': 0,
                'technical_density': 0,
                'phonetic_accuracy_score': 0
            }
        
        words = full_text.lower().split()
        
        # Count Sanskrit phonetic terminology
        technical_count = 0
        for term in self.sanskrit_phonetic_terms:
            technical_count += full_text.lower().count(term.lower())
        
        # Technical density (terms per 100 words)
        technical_density = (technical_count / max(1, len(words))) * 100
        
        # Phonetic accuracy score: appropriate use of terminology
        # Ideal: 2-5 technical terms per 100 words
        if 2 <= technical_density <= 5:
            phonetic_accuracy_score = 100
        elif technical_density < 2:
            phonetic_accuracy_score = technical_density * 50
        else:
            phonetic_accuracy_score = max(0, 100 - ((technical_density - 5) * 10))
        
        return {
            'technical_term_count': technical_count,
            'technical_density': round(technical_density, 2),
            'phonetic_accuracy_score': round(phonetic_accuracy_score, 2)
        }
    
    def _calculate_completeness_metrics(self, feedback: Dict[str, str]) -> Dict[str, Any]:
        """Calculate completeness of feedback sections"""
        sections_present = []
        section_lengths = {}
        
        for key in ['feedback', 'suggestion', 'motivation']:
            text = feedback.get(key, '').strip()
            if text:
                sections_present.append(key)
                section_lengths[f'{key}_length'] = len(text.split())
            else:
                section_lengths[f'{key}_length'] = 0
        
        completeness_score = (len(sections_present) / 3) * 100
        
        # Check if sections are balanced (ideally 30-60 words each)
        balance_scores = []
        for key in ['feedback', 'suggestion', 'motivation']:
            length = section_lengths[f'{key}_length']
            if 30 <= length <= 60:
                balance_scores.append(100)
            elif length < 30:
                balance_scores.append((length / 30) * 100)
            else:
                balance_scores.append(max(0, 100 - ((length - 60) * 2)))
        
        balance_score = sum(balance_scores) / 3 if balance_scores else 0
        
        return {
            'completeness_score': round(completeness_score, 2),
            'sections_present': sections_present,
            'section_balance_score': round(balance_score, 2),
            **section_lengths
        }
    
    def _calculate_structure_metrics(self, feedback: Dict[str, str]) -> Dict[str, float]:
        """Calculate structural quality metrics"""
        structure_score = 0
        
        # Check if feedback follows expected structure
        has_problem_identification = len(feedback.get('feedback', '')) > 20
        has_solution = len(feedback.get('suggestion', '')) > 20
        has_motivation = len(feedback.get('motivation', '')) > 15
        
        structure_score += 33.33 if has_problem_identification else 0
        structure_score += 33.33 if has_solution else 0
        structure_score += 33.34 if has_motivation else 0
        
        # Check logical flow (problem -> solution -> motivation)
        flow_score = 0
        if has_problem_identification and has_solution:
            flow_score += 50
        if has_solution and has_motivation:
            flow_score += 50
        
        return {
            'structure_score': round(structure_score, 2),
            'logical_flow_score': round(flow_score, 2)
        }
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate weighted overall quality score"""
        weights = {
            'positivity_score': 0.10,
            'readability_score': 0.15,
            'clarity_score': 0.10,
            'actionability_score': 0.20,
            'specificity_score': 0.15,
            'phonetic_accuracy_score': 0.15,
            'completeness_score': 0.10,
            'structure_score': 0.05
        }
        
        score = 0
        for key, weight in weights.items():
            score += metrics.get(key, 0) * weight
        
        return round(score, 2)
    
    def _empty_metrics(self, model_name: str) -> Dict[str, Any]:
        """Return empty metrics when feedback is not available"""
        return {
            'model_name': model_name,
            'error': 'No feedback generated',
            'overall_quality_score': 0
        }
    
    def compare_models(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple model metrics and determine the best one
        
        Args:
            metrics_list: List of metrics dictionaries from different models
            
        Returns:
            Comparison summary with winner and detailed breakdown
        """
        if not metrics_list:
            return {'error': 'No metrics to compare'}
        
        # Filter out failed generations
        valid_metrics = [m for m in metrics_list if 'error' not in m]
        
        if not valid_metrics:
            return {'error': 'All models failed to generate feedback'}
        
        # Find best model by overall score
        best_model = max(valid_metrics, key=lambda x: x.get('overall_quality_score', 0))
        
        # Create comparison breakdown
        comparison = {
            'winner': best_model['model_name'],
            'winner_score': best_model['overall_quality_score'],
            'models_compared': len(valid_metrics),
            'metric_breakdown': {}
        }
        
        # Compare key metrics
        key_metrics = [
            'overall_quality_score', 'positivity_score', 'actionability_score',
            'specificity_score', 'phonetic_accuracy_score', 'readability_score',
            'generation_time'
        ]
        
        for metric in key_metrics:
            comparison['metric_breakdown'][metric] = {
                model['model_name']: model.get(metric, 0)
                for model in valid_metrics
            }
        
        # Determine strengths
        comparison['strengths'] = {}
        for model in valid_metrics:
            strengths = []
            model_name = model['model_name']
            
            # Check which metrics this model excels at
            for metric in key_metrics[1:]:  # Skip overall score
                if metric == 'generation_time':
                    # Lower is better for generation time
                    if model.get(metric, float('inf')) == min(m.get(metric, float('inf')) for m in valid_metrics):
                        strengths.append(f"Fastest ({model.get(metric, 0):.2f}s)")
                else:
                    if model.get(metric, 0) == max(m.get(metric, 0) for m in valid_metrics):
                        strengths.append(metric.replace('_', ' ').title())
            
            comparison['strengths'][model_name] = strengths
        
        return comparison
    
    def generate_report(self, metrics: Dict[str, Any]) -> str:
        """Generate a human-readable report from metrics"""
        if 'error' in metrics:
            return f"❌ {metrics['error']}"
        
        report = []
        report.append(f"\n{'='*60}")
        report.append(f"LLM FEEDBACK QUALITY REPORT: {metrics['model_name']}")
        report.append(f"{'='*60}\n")
        
        report.append(f"⚡ Generation Time: {metrics.get('generation_time', 0):.2f}s")
        report.append(f"🎯 Overall Quality Score: {metrics.get('overall_quality_score', 0):.1f}/100\n")
        
        report.append("📊 DETAILED METRICS:")
        report.append(f"  • Positivity: {metrics.get('positivity_score', 0):.1f}/100")
        report.append(f"  • Sentiment Polarity: {metrics.get('sentiment_polarity', 0):.2f} (-1 to +1)")
        report.append(f"  • Readability: {metrics.get('readability_score', 0):.1f}/100")
        report.append(f"  • Clarity: {metrics.get('clarity_score', 0):.1f}/100")
        report.append(f"  • Actionability: {metrics.get('actionability_score', 0):.1f}/100")
        report.append(f"  • Specificity: {metrics.get('specificity_score', 0):.1f}/100")
        report.append(f"  • Motivational Content: {metrics.get('motivational_score', 0):.1f}/100")
        report.append(f"  • Technical Accuracy: {metrics.get('phonetic_accuracy_score', 0):.1f}/100")
        report.append(f"  • Completeness: {metrics.get('completeness_score', 0):.1f}/100")
        report.append(f"  • Structure Quality: {metrics.get('structure_score', 0):.1f}/100\n")
        
        report.append("📝 TEXT STATISTICS:")
        report.append(f"  • Total Words: {metrics.get('word_count', 0)}")
        report.append(f"  • Sentences: {metrics.get('sentence_count', 0)}")
        report.append(f"  • Avg Sentence Length: {metrics.get('avg_sentence_length', 0):.1f} words")
        report.append(f"  • Technical Terms: {metrics.get('technical_term_count', 0)}")
        report.append(f"  • Technical Density: {metrics.get('technical_density', 0):.1f} terms/100 words\n")
        
        report.append("📋 SECTION ANALYSIS:")
        report.append(f"  • Feedback Section: {metrics.get('feedback_length', 0)} words")
        report.append(f"  • Suggestion Section: {metrics.get('suggestion_length', 0)} words")
        report.append(f"  • Motivation Section: {metrics.get('motivation_length', 0)} words")
        report.append(f"  • Sections Present: {', '.join(metrics.get('sections_present', []))}\n")
        
        report.append(f"{'='*60}\n")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    evaluator = LLMMetricsEvaluator()
    
    # Example feedback
    sample_feedback = {
        'feedback': 'Your pronunciation of the aspirated consonant "kha" was incorrect. The aspiration was too weak.',
        'suggestion': 'Place your tongue at the soft palate and release a strong burst of air after the "k" sound.',
        'motivation': 'Keep practicing! Focus on the breath control and you will improve quickly.'
    }
    
    sample_analysis = {'accuracy': 75}
    
    metrics = evaluator.evaluate_feedback(sample_feedback, sample_analysis, 'gemini-1.5', 1.2)
    print(evaluator.generate_report(metrics))