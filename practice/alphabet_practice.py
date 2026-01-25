"""
Alphabet Practice Module for Sanskrit Voice Bot v2
Provides structured alphabet practice for building fundamental pronunciation skills.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Callable

from core.config import UIConfig, SanskritConstants, PracticeConfig


class AlphabetPractice:
    """
    Manages alphabet practice functionality for Sanskrit pronunciation.
    
    This class provides:
    - Structured vowel and consonant practice
    - Progress tracking for each alphabet
    - Interactive practice interface
    - Performance assessment
    """
    
    def __init__(self, main_app):
        """
        Initialize the AlphabetPractice module.
        
        Args:
            main_app: Reference to the main application controller
        """
        self.main_app = main_app
        self.root = main_app.root
        
        # Practice state
        self.current_category = 'vowels'  # 'vowels' or 'consonants'
        self.current_index = 0
        self.alphabet_scores = {}
        self.practice_complete = False
        
        # UI components
        self.alphabet_window = None
        self.widgets = {}
        
        # Initialize alphabet scores
        self.reset_practice_state()
    
    def reset_practice_state(self):
        """Reset practice state for new session"""
        self.alphabet_scores = {}
        
        # Initialize scores for all alphabets
        for devanagari, slp1 in SanskritConstants.VOWELS:
            self.alphabet_scores[devanagari] = {
                'attempts': 0,
                'best_score': 0,
                'category': 'vowels',
                'slp1': slp1
            }
        
        for devanagari, slp1 in SanskritConstants.CONSONANTS:
            self.alphabet_scores[devanagari] = {
                'attempts': 0,
                'best_score': 0,
                'category': 'consonants',
                'slp1': slp1
            }
        
        self.current_category = 'vowels'
        self.current_index = 0
        self.practice_complete = False
    
    def show_alphabet_practice(self):
        """Show the alphabet practice window"""
        if self.alphabet_window and self.alphabet_window.winfo_exists():
            self.alphabet_window.lift()
            return
        
        self._create_alphabet_window()
        self._update_current_alphabet_display()
    
    def _create_alphabet_window(self):
        """Create the alphabet practice window"""
        self.alphabet_window = tk.Toplevel(self.root)
        self.alphabet_window.title("Sanskrit Alphabet Practice")
        self.alphabet_window.geometry("800x600")
        self.alphabet_window.configure(bg=UIConfig.COLORS['background'])
        self.alphabet_window.transient(self.root)
        
        # Center the window
        self.alphabet_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        self._create_alphabet_ui()
    
    def _create_alphabet_ui(self):
        """Create the alphabet practice user interface"""
        # Header
        header_frame = tk.Frame(self.alphabet_window, bg=UIConfig.COLORS['background'])
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🔤 Sanskrit Alphabet Practice",
            font=UIConfig.FONTS['title'],
            bg=UIConfig.COLORS['background'],
            fg=UIConfig.COLORS['primary']
        ).pack()
        
        tk.Label(
            header_frame,
            text="Build your foundation by practicing individual sounds",
            font=UIConfig.FONTS['subtitle'],
            bg=UIConfig.COLORS['background'],
            fg=UIConfig.COLORS['text_secondary']
        ).pack(pady=(5, 0))
        
        # Category selection
        self._create_category_selection(header_frame)
        
        # Current alphabet display
        self._create_alphabet_display()
        
        # Practice controls
        self._create_practice_controls()
        
        # Progress display
        self._create_progress_display()
        
        # Navigation controls
        self._create_navigation_controls()
    
    def _create_category_selection(self, parent):
        """Create category selection buttons"""
        category_frame = tk.Frame(parent, bg=UIConfig.COLORS['background'])
        category_frame.pack(pady=20)
        
        self.widgets['vowels_button'] = tk.Button(
            category_frame,
            text="Vowels (स्वर)",
            font=UIConfig.FONTS['normal'],
            bg=UIConfig.COLORS['primary'],
            fg=UIConfig.COLORS['white'],
            command=lambda: self._switch_category('vowels'),
            padx=20, pady=10
        )
        self.widgets['vowels_button'].pack(side=tk.LEFT, padx=(0, 10))
        
        self.widgets['consonants_button'] = tk.Button(
            category_frame,
            text="Consonants (व्यञ्जन)",
            font=UIConfig.FONTS['normal'],
            bg=UIConfig.COLORS['secondary'],
            fg=UIConfig.COLORS['white'],
            command=lambda: self._switch_category('consonants'),
            padx=20, pady=10
        )
        self.widgets['consonants_button'].pack(side=tk.LEFT)
    
    def _create_alphabet_display(self):
        """Create the current alphabet display section"""
        display_frame = tk.Frame(self.alphabet_window, bg=UIConfig.COLORS['card_bg'], relief=tk.RAISED, bd=2)
        display_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.widgets['current_alphabet_label'] = tk.Label(
            display_frame,
            text="अ",
            font=("Arial Unicode MS", 72, "bold"),
            bg=UIConfig.COLORS['card_bg'],
            fg=UIConfig.COLORS['primary']
        )
        self.widgets['current_alphabet_label'].pack(pady=30)
        
        self.widgets['alphabet_info_label'] = tk.Label(
            display_frame,
            text="SLP1: a",
            font=UIConfig.FONTS['header'],
            bg=UIConfig.COLORS['card_bg'],
            fg=UIConfig.COLORS['text_secondary']
        )
        self.widgets['alphabet_info_label'].pack(pady=(0, 20))
    
    def _create_practice_controls(self):
        """Create practice control buttons"""
        controls_frame = tk.Frame(self.alphabet_window, bg=UIConfig.COLORS['background'])
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.widgets['practice_record_button'] = tk.Button(
            controls_frame,
            text="🎤 Record Pronunciation",
            font=UIConfig.FONTS['header'],
            bg=UIConfig.COLORS['success'],
            fg=UIConfig.COLORS['white'],
            command=self._toggle_alphabet_recording,
            padx=20, pady=10
        )
        self.widgets['practice_record_button'].pack(side=tk.LEFT, padx=(0, 10))
        
        self.widgets['analyze_alphabet_button'] = tk.Button(
            controls_frame,
            text="🔍 Check Pronunciation",
            font=UIConfig.FONTS['header'],
            bg=UIConfig.COLORS['info'],
            fg=UIConfig.COLORS['white'],
            command=self._analyze_alphabet_pronunciation,
            padx=20, pady=10,
            state=tk.DISABLED
        )
        self.widgets['analyze_alphabet_button'].pack(side=tk.LEFT)
    
    def _create_progress_display(self):
        """Create progress display section"""
        progress_frame = tk.Frame(self.alphabet_window, bg=UIConfig.COLORS['background'])
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.widgets['progress_label'] = tk.Label(
            progress_frame,
            text="Progress: 0/16 Vowels completed",
            font=UIConfig.FONTS['normal'],
            bg=UIConfig.COLORS['background'],
            fg=UIConfig.COLORS['text_secondary']
        )
        self.widgets['progress_label'].pack()
        
        # Progress bar
        self.widgets['progress_bar'] = ttk.Progressbar(
            progress_frame,
            length=400,
            mode='determinate'
        )
        self.widgets['progress_bar'].pack(pady=10)
    
    def _create_navigation_controls(self):
        """Create navigation control buttons"""
        nav_frame = tk.Frame(self.alphabet_window, bg=UIConfig.COLORS['background'])
        nav_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.widgets['prev_alphabet_button'] = tk.Button(
            nav_frame,
            text="⬅ Previous",
            font=UIConfig.FONTS['normal'],
            bg=UIConfig.COLORS['muted'],
            fg=UIConfig.COLORS['white'],
            command=self._prev_alphabet,
            padx=15, pady=8
        )
        self.widgets['prev_alphabet_button'].pack(side=tk.LEFT)
        
        self.widgets['next_alphabet_button'] = tk.Button(
            nav_frame,
            text="Next ➡",
            font=UIConfig.FONTS['normal'],
            bg=UIConfig.COLORS['muted'],
            fg=UIConfig.COLORS['white'],
            command=self._next_alphabet,
            padx=15, pady=8
        )
        self.widgets['next_alphabet_button'].pack(side=tk.LEFT, padx=(10, 0))
        
        self.widgets['close_alphabet_button'] = tk.Button(
            nav_frame,
            text="✖ Close Practice",
            font=UIConfig.FONTS['normal'],
            bg=UIConfig.COLORS['error'],
            fg=UIConfig.COLORS['white'],
            command=self._close_alphabet_practice,
            padx=15, pady=8
        )
        self.widgets['close_alphabet_button'].pack(side=tk.RIGHT)
    
    def _switch_category(self, category: str):
        """Switch between vowels and consonants"""
        self.current_category = category
        self.current_index = 0
        self._update_current_alphabet_display()
        self._update_category_buttons()
    
    def _update_category_buttons(self):
        """Update category button appearance"""
        if self.current_category == 'vowels':
            self.widgets['vowels_button'].config(bg=UIConfig.COLORS['primary'])
            self.widgets['consonants_button'].config(bg=UIConfig.COLORS['secondary'])
        else:
            self.widgets['vowels_button'].config(bg=UIConfig.COLORS['secondary'])
            self.widgets['consonants_button'].config(bg=UIConfig.COLORS['primary'])
    
    def _get_current_alphabets(self) -> List[tuple]:
        """Get current alphabet list based on category"""
        if self.current_category == 'vowels':
            return SanskritConstants.VOWELS
        else:
            return SanskritConstants.CONSONANTS
    
    def _update_current_alphabet_display(self):
        """Update the display for current alphabet"""
        alphabets = self._get_current_alphabets()
        
        if self.current_index < len(alphabets):
            devanagari, slp1 = alphabets[self.current_index]
            
            self.widgets['current_alphabet_label'].config(text=devanagari)
            self.widgets['alphabet_info_label'].config(text=f"SLP1: {slp1}")
            
            # Update progress
            completed = self._count_completed_alphabets()
            total = len(alphabets)
            category_name = "Vowels" if self.current_category == 'vowels' else "Consonants"
            
            self.widgets['progress_label'].config(
                text=f"Progress: {completed}/{total} {category_name} completed"
            )
            
            progress_percentage = (completed / total) * 100
            self.widgets['progress_bar']['value'] = progress_percentage
            
            # Update navigation buttons
            self.widgets['prev_alphabet_button'].config(
                state=tk.NORMAL if self.current_index > 0 else tk.DISABLED
            )
            self.widgets['next_alphabet_button'].config(
                state=tk.NORMAL if self.current_index < len(alphabets) - 1 else tk.DISABLED
            )
    
    def _count_completed_alphabets(self) -> int:
        """Count completed alphabets in current category"""
        alphabets = self._get_current_alphabets()
        completed = 0
        
        for devanagari, _ in alphabets:
            if (devanagari in self.alphabet_scores and 
                self.alphabet_scores[devanagari]['best_score'] >= PracticeConfig.ALPHABET_COMPLETION_THRESHOLD):
                completed += 1
        
        return completed
    
    def _prev_alphabet(self):
        """Navigate to previous alphabet"""
        if self.current_index > 0:
            self.current_index -= 1
            self._update_current_alphabet_display()
    
    def _next_alphabet(self):
        """Navigate to next alphabet"""
        alphabets = self._get_current_alphabets()
        if self.current_index < len(alphabets) - 1:
            self.current_index += 1
            self._update_current_alphabet_display()
    
    def _toggle_alphabet_recording(self):
        """Toggle recording for alphabet practice"""
        # Use the main app's audio manager
        if not self.main_app.audio_manager.is_recording():
            self._start_alphabet_recording()
        else:
            self._stop_alphabet_recording()
    
    def _start_alphabet_recording(self):
        """Start recording for alphabet practice"""
        if self.main_app.audio_manager.start_recording():
            self.widgets['practice_record_button'].config(
                text="🛑 Stop Recording",
                bg=UIConfig.COLORS['warning']
            )
        else:
            self._show_alphabet_error("Could not start recording")
    
    def _stop_alphabet_recording(self):
        """Stop recording for alphabet practice"""
        result = self.main_app.audio_manager.stop_recording()
        self.widgets['practice_record_button'].config(
            text="🎤 Record Pronunciation",
            bg=UIConfig.COLORS['success']
        )
        
        if result['success']:
            self.widgets['analyze_alphabet_button'].config(state=tk.NORMAL)
        else:
            self._show_alphabet_error(f"Recording failed: {result.get('error', 'Unknown error')}")
    
    def _analyze_alphabet_pronunciation(self):
        """Analyze pronunciation of current alphabet"""
        alphabets = self._get_current_alphabets()
        if self.current_index >= len(alphabets):
            return
        
        devanagari, slp1 = alphabets[self.current_index]
        
        # Get transcription from main audio manager
        transcription_result = self.main_app.audio_manager.transcribe_audio()
        
        if transcription_result['success']:
            user_text = transcription_result['transcription'].strip()
            
            # Calculate similarity
            from utils.text_processor import TextProcessor
            similarity = TextProcessor.calculate_similarity(devanagari, user_text)
            accuracy = similarity * 100
            
            # Record the attempt
            self.alphabet_scores[devanagari]['attempts'] += 1
            self.alphabet_scores[devanagari]['best_score'] = max(
                self.alphabet_scores[devanagari]['best_score'], 
                accuracy
            )
            
            # Show result
            self._show_alphabet_result(devanagari, slp1, user_text, accuracy)
            
            # Update progress display
            self._update_current_alphabet_display()
            
            # Auto-advance if accuracy is good
            if accuracy >= PracticeConfig.ALPHABET_COMPLETION_THRESHOLD:
                self.root.after(2000, self._auto_advance)
        else:
            self._show_alphabet_error(f"Transcription failed: {transcription_result.get('error', 'Unknown error')}")
        
        # Reset analyze button
        self.widgets['analyze_alphabet_button'].config(state=tk.DISABLED)
    
    def _show_alphabet_result(self, devanagari: str, slp1: str, user_text: str, accuracy: float):
        """Show result of alphabet pronunciation attempt"""
        if accuracy >= PracticeConfig.ALPHABET_COMPLETION_THRESHOLD:
            result_text = f"✅ Excellent! '{devanagari}' pronounced correctly ({accuracy:.1f}%)"
            result_color = UIConfig.COLORS['success']
        elif accuracy >= 60:
            result_text = f"⚠️ Good try! '{devanagari}' needs a bit more practice ({accuracy:.1f}%)"
            result_color = UIConfig.COLORS['warning']
        else:
            result_text = f"❌ Keep practicing '{devanagari}' - you said '{user_text}' ({accuracy:.1f}%)"
            result_color = UIConfig.COLORS['error']
        
        # Create or update result label
        if 'result_label' not in self.widgets:
            self.widgets['result_label'] = tk.Label(
                self.alphabet_window,
                text=result_text,
                font=UIConfig.FONTS['normal'],
                bg=UIConfig.COLORS['background'],
                fg=result_color,
                wraplength=600
            )
            self.widgets['result_label'].pack(pady=10)
        else:
            self.widgets['result_label'].config(text=result_text, fg=result_color)
    
    def _auto_advance(self):
        """Automatically advance to next alphabet after successful attempt"""
        alphabets = self._get_current_alphabets()
        if self.current_index < len(alphabets) - 1:
            self._next_alphabet()
        else:
            # Check if all alphabets in category are complete
            if self._is_category_complete():
                if self.current_category == 'vowels':
                    self._show_category_completion_message('vowels')
                    self._switch_category('consonants')
                else:
                    self._show_practice_completion()
    
    def _is_category_complete(self) -> bool:
        """Check if current category is complete"""
        alphabets = self._get_current_alphabets()
        
        for devanagari, _ in alphabets:
            if (devanagari not in self.alphabet_scores or 
                self.alphabet_scores[devanagari]['best_score'] < PracticeConfig.ALPHABET_COMPLETION_THRESHOLD):
                return False
        
        return True
    
    def _show_category_completion_message(self, category: str):
        """Show message when a category is completed"""
        category_name = "Vowels" if category == 'vowels' else "Consonants"
        messagebox.showinfo(
            "Category Complete!",
            f"🎉 Congratulations! You've completed all {category_name}!\n\n"
            f"Now let's practice the consonants."
        )
    
    def _show_practice_completion(self):
        """Show message when all alphabet practice is complete"""
        messagebox.showinfo(
            "Practice Complete!",
            "🌟 Excellent work! You've completed the alphabet practice.\n\n"
            "You're now ready to return to word and shloka practice with a stronger foundation!"
        )
        self.practice_complete = True
        self._close_alphabet_practice()
    
    def _show_alphabet_error(self, message: str):
        """Show error message in alphabet practice"""
        messagebox.showerror("Alphabet Practice Error", message)
    
    def _close_alphabet_practice(self):
        """Close alphabet practice window"""
        if self.alphabet_window and self.alphabet_window.winfo_exists():
            self.alphabet_window.destroy()
    
    def get_practice_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about alphabet practice progress.
        
        Returns:
            Dictionary containing practice statistics
        """
        vowel_completed = 0
        consonant_completed = 0
        total_attempts = 0
        
        for devanagari, score_data in self.alphabet_scores.items():
            total_attempts += score_data['attempts']
            
            if score_data['best_score'] >= PracticeConfig.ALPHABET_COMPLETION_THRESHOLD:
                if score_data['category'] == 'vowels':
                    vowel_completed += 1
                else:
                    consonant_completed += 1
        
        return {
            'vowels_completed': vowel_completed,
            'vowels_total': len(SanskritConstants.VOWELS),
            'consonants_completed': consonant_completed,
            'consonants_total': len(SanskritConstants.CONSONANTS),
            'total_attempts': total_attempts,
            'practice_complete': self.practice_complete
        }
