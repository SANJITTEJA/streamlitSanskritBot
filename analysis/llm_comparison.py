"""
LLM Comparison Module for Sanskrit Voice Bot v2
Runs A/B testing between Gemini and Llama models for feedback generation
and provides detailed comparative analysis.
"""

import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from .llm_feedback import LLMFeedbackGenerator, LlamaFeedbackGenerator
from .llm_metrics import LLMMetricsEvaluator


class LLMComparison:
    """Class for comparing multiple LLM models for feedback generation"""
    
    def __init__(self):
        """Initialize the comparison framework"""
        self.gemini_generator = LLMFeedbackGenerator()
        self.llama_generator = LlamaFeedbackGenerator()
        self.metrics_evaluator = LLMMetricsEvaluator()
        
        # Track comparison history
        self.comparison_history = []
        self.history_file = Path("llm_comparison_history.json")
        
        # Load previous comparisons if available
        self._load_history()
    
    def compare_models(self, analysis_result: Dict[str, Any], 
                      user_level: str = "beginner") -> Dict[str, Any]:
        """
        Run both LLM models and compare their outputs
        
        Args:
            analysis_result: Dictionary containing pronunciation analysis data
            user_level: Proficiency level of the user
            
        Returns:
            Dictionary containing both feedbacks and comparative metrics
        """
        results = {
            'gemini': {},
            'llama': {},
            'comparison': {},
            'winner': None
        }
        
        # Generate feedback from Gemini
        print("\n🤖 Generating Gemini feedback...")
        gemini_start = time.time()
        gemini_feedback = self.gemini_generator.generate_feedback(analysis_result, user_level)
        gemini_time = time.time() - gemini_start
        
        if gemini_feedback:
            gemini_metrics = self.metrics_evaluator.evaluate_feedback(
                gemini_feedback, 
                analysis_result, 
                'Gemini-2.0-Flash',
                gemini_time
            )
            results['gemini'] = {
                'feedback': gemini_feedback,
                'metrics': gemini_metrics,
                'success': True
            }
            print(f"✅ Gemini completed in {gemini_time:.2f}s")
        else:
            results['gemini'] = {
                'feedback': None,
                'metrics': self.metrics_evaluator._empty_metrics('Gemini-2.0-Flash'),
                'success': False
            }
            print("❌ Gemini failed to generate feedback")
        
        # Generate feedback from Llama
        print("\n🦙 Generating Llama feedback...")
        llama_start = time.time()
        llama_feedback = self.llama_generator.generate_feedback(analysis_result, user_level)
        llama_time = time.time() - llama_start
        
        if llama_feedback:
            llama_metrics = self.metrics_evaluator.evaluate_feedback(
                llama_feedback,
                analysis_result,
                'Llama-3.2',
                llama_time
            )
            results['llama'] = {
                'feedback': llama_feedback,
                'metrics': llama_metrics,
                'success': True
            }
            print(f"✅ Llama completed in {llama_time:.2f}s")
        else:
            results['llama'] = {
                'feedback': None,
                'metrics': self.metrics_evaluator._empty_metrics('Llama-3.2'),
                'success': False
            }
            print("❌ Llama failed to generate feedback")
        
        # Compare the results
        if results['gemini']['success'] or results['llama']['success']:
            metrics_list = []
            if results['gemini']['success']:
                metrics_list.append(results['gemini']['metrics'])
            if results['llama']['success']:
                metrics_list.append(results['llama']['metrics'])
            
            comparison = self.metrics_evaluator.compare_models(metrics_list)
            results['comparison'] = comparison
            results['winner'] = comparison.get('winner', 'None')
            
            # Save to history
            self._add_to_history(results, analysis_result)
            
            print(f"\n🏆 Winner: {results['winner']}")
        else:
            results['comparison'] = {'error': 'Both models failed'}
            results['winner'] = 'None'
        
        return results
    
    def generate_detailed_report(self, comparison_results: Dict[str, Any]) -> str:
        """
        Generate a detailed comparison report
        
        Args:
            comparison_results: Results from compare_models()
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "="*80)
        report.append("LLM FEEDBACK COMPARISON REPORT")
        report.append("="*80 + "\n")
        
        # Winner announcement
        winner = comparison_results.get('winner', 'None')
        if winner != 'None':
            report.append(f"🏆 WINNER: {winner}")
            report.append("")
        
        # Gemini results
        if comparison_results['gemini']['success']:
            report.append("=" * 80)
            report.append("GEMINI-2.0-FLASH FEEDBACK")
            report.append("=" * 80)
            gemini_feedback = comparison_results['gemini']['feedback']
            report.append(f"\n📊 ANALYSIS:")
            report.append(f"{gemini_feedback.get('feedback', 'N/A')}\n")
            report.append(f"💡 SUGGESTION/TECHNIQUE:")
            report.append(f"{gemini_feedback.get('suggestion', 'N/A')}\n")
            report.append(f"✨ MOTIVATION:")
            report.append(f"{gemini_feedback.get('motivation', 'N/A')}\n")
            
            # Metrics
            report.append(self.metrics_evaluator.generate_report(comparison_results['gemini']['metrics']))
        else:
            report.append("\n❌ Gemini feedback generation failed\n")
        
        # Llama results
        if comparison_results['llama']['success']:
            report.append("\n" + "=" * 80)
            report.append("LLAMA-3.2 FEEDBACK")
            report.append("=" * 80)
            llama_feedback = comparison_results['llama']['feedback']
            report.append(f"\n📊 ANALYSIS:")
            report.append(f"{llama_feedback.get('feedback', 'N/A')}\n")
            report.append(f"💡 SUGGESTION/TECHNIQUE:")
            report.append(f"{llama_feedback.get('suggestion', 'N/A')}\n")
            report.append(f"✨ MOTIVATION:")
            report.append(f"{llama_feedback.get('motivation', 'N/A')}\n")
            
            # Metrics
            report.append(self.metrics_evaluator.generate_report(comparison_results['llama']['metrics']))
        else:
            report.append("\n❌ Llama feedback generation failed\n")
        
        # Comparative analysis
        if 'error' not in comparison_results['comparison']:
            report.append("\n" + "=" * 80)
            report.append("COMPARATIVE ANALYSIS")
            report.append("=" * 80 + "\n")
            
            comparison = comparison_results['comparison']
            
            # Metric breakdown
            report.append("📊 METRIC-BY-METRIC COMPARISON:\n")
            metric_breakdown = comparison.get('metric_breakdown', {})
            
            for metric, values in metric_breakdown.items():
                report.append(f"  {metric.replace('_', ' ').title()}:")
                for model, score in values.items():
                    if metric == 'generation_time':
                        report.append(f"    • {model}: {score:.2f}s")
                    else:
                        report.append(f"    • {model}: {score:.2f}")
                report.append("")
            
            # Strengths
            report.append("💪 MODEL STRENGTHS:\n")
            strengths = comparison.get('strengths', {})
            for model, strength_list in strengths.items():
                if strength_list:
                    report.append(f"  {model}:")
                    for strength in strength_list:
                        report.append(f"    ✓ {strength}")
                else:
                    report.append(f"  {model}: No standout strengths")
                report.append("")
        
        report.append("=" * 80 + "\n")
        
        return "\n".join(report)
    
    def get_preferred_model(self, min_samples: int = 5) -> Optional[str]:
        """
        Determine the preferred model based on historical performance
        
        Args:
            min_samples: Minimum number of comparisons needed for recommendation
            
        Returns:
            Preferred model name or None if insufficient data
        """
        if len(self.comparison_history) < min_samples:
            return None
        
        # Count wins
        wins = {}
        total_scores = {}
        
        for entry in self.comparison_history:
            winner = entry.get('winner', 'None')
            if winner != 'None':
                wins[winner] = wins.get(winner, 0) + 1
            
            # Aggregate scores
            for model in ['gemini', 'llama']:
                if entry[model]['success']:
                    model_name = entry[model]['metrics']['model_name']
                    score = entry[model]['metrics'].get('overall_quality_score', 0)
                    if model_name not in total_scores:
                        total_scores[model_name] = []
                    total_scores[model_name].append(score)
        
        # Calculate average scores
        avg_scores = {}
        for model, scores in total_scores.items():
            if scores:
                avg_scores[model] = sum(scores) / len(scores)
        
        # Determine preferred model
        if avg_scores:
            preferred = max(avg_scores.items(), key=lambda x: x[1])
            return preferred[0]
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of all comparisons"""
        if not self.comparison_history:
            return {'error': 'No comparison history available'}
        
        stats = {
            'total_comparisons': len(self.comparison_history),
            'gemini': {
                'successes': 0,
                'failures': 0,
                'avg_score': 0,
                'avg_time': 0,
                'wins': 0
            },
            'llama': {
                'successes': 0,
                'failures': 0,
                'avg_score': 0,
                'avg_time': 0,
                'wins': 0
            }
        }
        
        gemini_scores = []
        gemini_times = []
        llama_scores = []
        llama_times = []
        
        for entry in self.comparison_history:
            # Gemini stats
            if entry['gemini']['success']:
                stats['gemini']['successes'] += 1
                score = entry['gemini']['metrics'].get('overall_quality_score', 0)
                time_taken = entry['gemini']['metrics'].get('generation_time', 0)
                gemini_scores.append(score)
                gemini_times.append(time_taken)
            else:
                stats['gemini']['failures'] += 1
            
            # Llama stats
            if entry['llama']['success']:
                stats['llama']['successes'] += 1
                score = entry['llama']['metrics'].get('overall_quality_score', 0)
                time_taken = entry['llama']['metrics'].get('generation_time', 0)
                llama_scores.append(score)
                llama_times.append(time_taken)
            else:
                stats['llama']['failures'] += 1
            
            # Count wins
            winner = entry.get('winner', 'None')
            if 'Gemini' in winner:
                stats['gemini']['wins'] += 1
            elif 'Llama' in winner:
                stats['llama']['wins'] += 1
        
        # Calculate averages
        if gemini_scores:
            stats['gemini']['avg_score'] = sum(gemini_scores) / len(gemini_scores)
            stats['gemini']['avg_time'] = sum(gemini_times) / len(gemini_times)
        
        if llama_scores:
            stats['llama']['avg_score'] = sum(llama_scores) / len(llama_scores)
            stats['llama']['avg_time'] = sum(llama_times) / len(llama_times)
        
        return stats
    
    def print_statistics(self):
        """Print a formatted statistics report"""
        stats = self.get_statistics()
        
        if 'error' in stats:
            print(stats['error'])
            return
        
        print("\n" + "="*60)
        print("LLM COMPARISON STATISTICS")
        print("="*60)
        print(f"\nTotal Comparisons: {stats['total_comparisons']}")
        
        print("\n📊 GEMINI-2.0-FLASH:")
        print(f"  • Successes: {stats['gemini']['successes']}")
        print(f"  • Failures: {stats['gemini']['failures']}")
        print(f"  • Wins: {stats['gemini']['wins']}")
        print(f"  • Avg Quality Score: {stats['gemini']['avg_score']:.2f}/100")
        print(f"  • Avg Generation Time: {stats['gemini']['avg_time']:.2f}s")
        
        print("\n🦙 LLAMA-3.2:")
        print(f"  • Successes: {stats['llama']['successes']}")
        print(f"  • Failures: {stats['llama']['failures']}")
        print(f"  • Wins: {stats['llama']['wins']}")
        print(f"  • Avg Quality Score: {stats['llama']['avg_score']:.2f}/100")
        print(f"  • Avg Generation Time: {stats['llama']['avg_time']:.2f}s")
        
        # Recommendation
        preferred = self.get_preferred_model()
        if preferred:
            print(f"\n🏆 RECOMMENDED MODEL: {preferred}")
        else:
            print(f"\n⚠️  Insufficient data for recommendation (need at least 5 comparisons)")
        
        print("="*60 + "\n")
    
    def _add_to_history(self, results: Dict[str, Any], analysis_result: Dict[str, Any]):
        """Add comparison results to history"""
        entry = {
            'timestamp': time.time(),
            'accuracy': analysis_result.get('accuracy', 0),
            'analysis_type': analysis_result.get('analysis_type', 'unknown'),
            'winner': results.get('winner', 'None'),
            'gemini': {
                'success': results['gemini']['success'],
                'metrics': results['gemini']['metrics'] if results['gemini']['success'] else None
            },
            'llama': {
                'success': results['llama']['success'],
                'metrics': results['llama']['metrics'] if results['llama']['success'] else None
            }
        }
        
        self.comparison_history.append(entry)
        self._save_history()
    
    def _load_history(self):
        """Load comparison history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.comparison_history = json.load(f)
                print(f"Loaded {len(self.comparison_history)} previous comparisons")
            except Exception as e:
                print(f"Error loading comparison history: {e}")
                self.comparison_history = []
        else:
            self.comparison_history = []
    
    def _save_history(self):
        """Save comparison history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.comparison_history, f, indent=2)
        except Exception as e:
            print(f"Error saving comparison history: {e}")


# Example usage
if __name__ == "__main__":
    comparison = LLMComparison()
    
    # Example analysis result
    sample_analysis = {
        'accuracy': 75,
        'analysis_type': 'single_word',
        'word_results': [{
            'original': 'namaste',
            'user': 'namasthe',
            'correct': False
        }],
        'incorrect_words': [{
            'devanagari': 'नमस्ते',
            'slp1': 'namaste',
            'user': 'namasthe'
        }]
    }
    
    # Run comparison
    results = comparison.compare_models(sample_analysis, user_level='beginner')
    
    # Print detailed report
    print(comparison.generate_detailed_report(results))
    
    # Print statistics
    comparison.print_statistics()