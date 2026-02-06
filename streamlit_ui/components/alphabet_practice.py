"""
Alphabet Practice Component for Streamlit
Provides structured alphabet practice for building fundamental pronunciation skills.
"""
import streamlit as st
import sys
from pathlib import Path

# Add v2 to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import SanskritConstants, PracticeConfig
from streamlit_ui.backend_integration import get_backend


def initialize_alphabet_practice():
    """Initialize alphabet practice session state"""
    if 'alphabet_category' not in st.session_state:
        st.session_state.alphabet_category = 'vowels'
    
    if 'alphabet_index' not in st.session_state:
        st.session_state.alphabet_index = 0
    
    if 'alphabet_scores' not in st.session_state:
        st.session_state.alphabet_scores = {}
        
        # Initialize scores for all alphabets
        for devanagari, slp1 in SanskritConstants.VOWELS:
            st.session_state.alphabet_scores[devanagari] = {
                'attempts': 0,
                'best_score': 0,
                'category': 'vowels',
                'slp1': slp1
            }
        
        for devanagari, slp1 in SanskritConstants.CONSONANTS:
            st.session_state.alphabet_scores[devanagari] = {
                'attempts': 0,
                'best_score': 0,
                'category': 'consonants',
                'slp1': slp1
            }
    
    if 'alphabet_result' not in st.session_state:
        st.session_state.alphabet_result = None


def get_current_alphabets():
    """Get current alphabet list based on category"""
    if st.session_state.alphabet_category == 'vowels':
        return SanskritConstants.VOWELS
    else:
        return SanskritConstants.CONSONANTS


def count_completed_alphabets():
    """Count completed alphabets in current category"""
    alphabets = get_current_alphabets()
    completed = 0
    
    for devanagari, _ in alphabets:
        if (devanagari in st.session_state.alphabet_scores and 
            st.session_state.alphabet_scores[devanagari]['best_score'] >= PracticeConfig.ALPHABET_COMPLETION_THRESHOLD):
            completed += 1
    
    return completed


def render_alphabet_practice():
    """Render alphabet practice interface"""
    initialize_alphabet_practice()
    
    # Header
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #a78bfa; margin-bottom: 5px;">🔤 Sanskrit Alphabet Practice</h2>
            <p style="color: #94a3b8; font-size: 0.95rem;">
                Build your foundation by practicing individual sounds
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Category selection
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Vowels (स्वर)", 
                    use_container_width=True, 
                    type="primary" if st.session_state.alphabet_category == 'vowels' else "secondary"):
            st.session_state.alphabet_category = 'vowels'
            st.session_state.alphabet_index = 0
            st.session_state.alphabet_result = None
            st.rerun()
    
    with col2:
        if st.button("📝 Consonants (व्यञ्जन)", 
                    use_container_width=True,
                    type="primary" if st.session_state.alphabet_category == 'consonants' else "secondary"):
            st.session_state.alphabet_category = 'consonants'
            st.session_state.alphabet_index = 0
            st.session_state.alphabet_result = None
            st.rerun()
    
    # Get current alphabets
    alphabets = get_current_alphabets()
    current_idx = st.session_state.alphabet_index
    
    if current_idx >= len(alphabets):
        current_idx = 0
        st.session_state.alphabet_index = 0
    
    devanagari, slp1 = alphabets[current_idx]
    
    # Progress section
    completed = count_completed_alphabets()
    total = len(alphabets)
    category_name = "Vowels" if st.session_state.alphabet_category == 'vowels' else "Consonants"
    
    st.markdown("---")
    st.markdown(f"**Progress:** {completed}/{total} {category_name} completed")
    st.progress(completed / total)
    
    # Current alphabet display
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
            <div style="background: rgba(124, 58, 237, 0.1); border: 3px solid #7c3aed; 
                 border-radius: 16px; padding: 40px; text-align: center; margin: 20px 0;">
                <div style="font-size: 5rem; color: #f1f5f9; margin-bottom: 15px; font-weight: bold;">
                    {devanagari}
                </div>
                <div style="font-size: 1.5rem; color: #a78bfa; font-style: italic;">
                    SLP1: {slp1}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Show statistics if attempts exist
    if devanagari in st.session_state.alphabet_scores:
        score_data = st.session_state.alphabet_scores[devanagari]
        if score_data['attempts'] > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Attempts", score_data['attempts'])
            with col2:
                st.metric("Best Score", f"{score_data['best_score']:.1f}%")
            with col3:
                status = "✅ Completed" if score_data['best_score'] >= PracticeConfig.ALPHABET_COMPLETION_THRESHOLD else "🔄 Practice"
                st.metric("Status", status)
    
    # Audio recording section
    st.markdown("---")
    st.markdown("### 🎤 Record Your Pronunciation")
    
    audio_value = st.audio_input(f"Pronounce '{devanagari}'", key=f"alphabet_audio_{current_idx}_{devanagari}")
    
    if audio_value:
        audio_bytes = audio_value.read()
        
        # Analyze button
        if st.button("🔍 Check Pronunciation", type="primary", use_container_width=True):
            with st.spinner("Analyzing your pronunciation..."):
                backend = get_backend()
                
                # Transcribe user's audio
                transcription_result = backend.transcribe_audio(audio_bytes)
                
                if transcription_result.get('success'):
                    user_said = transcription_result.get('transcription', '').strip()
                    
                    # Compare with expected alphabet
                    from utils.text_processor import TextProcessor
                    text_processor = TextProcessor()
                    similarity = text_processor.calculate_similarity(devanagari, user_said)
                    accuracy = similarity * 100
                    
                    # Record the attempt
                    st.session_state.alphabet_scores[devanagari]['attempts'] += 1
                    st.session_state.alphabet_scores[devanagari]['best_score'] = max(
                        st.session_state.alphabet_scores[devanagari]['best_score'],
                        accuracy
                    )
                    
                    # Store result
                    st.session_state.alphabet_result = {
                        'alphabet': devanagari,
                        'slp1': slp1,
                        'user_said': user_said,
                        'accuracy': accuracy,
                        'passed': accuracy >= PracticeConfig.ALPHABET_COMPLETION_THRESHOLD
                    }
                    
                    st.rerun()
                else:
                    st.error(f"Failed to analyze: {transcription_result.get('error', 'Unknown error')}")
    
    # Display result if exists
    if st.session_state.alphabet_result:
        result = st.session_state.alphabet_result
        
        if result['alphabet'] == devanagari:  # Make sure result matches current alphabet
            st.markdown("---")
            st.markdown("### 📊 Your Result")
            
            # Result card
            if result['passed']:
                bg_color = "rgba(16, 185, 129, 0.1)"
                border_color = "#10b981"
                icon = "✅"
                message = f"Excellent! '{devanagari}' pronounced correctly"
            elif result['accuracy'] >= 60:
                bg_color = "rgba(251, 191, 36, 0.1)"
                border_color = "#fbbf24"
                icon = "⚠️"
                message = f"Good try! '{devanagari}' needs a bit more practice"
            else:
                bg_color = "rgba(239, 68, 68, 0.1)"
                border_color = "#ef4444"
                icon = "❌"
                message = f"Keep practicing '{devanagari}'"
            
            st.markdown(f"""
                <div style="background: {bg_color}; border: 2px solid {border_color}; 
                     border-radius: 12px; padding: 20px; margin: 15px 0;">
                    <div style="font-size: 1.3rem; text-align: center; margin-bottom: 10px;">
                        {icon} {message}
                    </div>
                    <div style="font-size: 1.1rem; text-align: center; color: #f1f5f9; margin-bottom: 5px;">
                        {result['accuracy']:.1f}% Accuracy
                    </div>
                    <div style="text-align: center; color: #94a3b8; font-size: 0.9rem;">
                        You said: <strong style="color: #f1f5f9;">{result['user_said']}</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Auto-advance message if passed
            if result['passed']:
                st.success("🎉 Great job! Moving to next alphabet...")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⬅️ Previous", disabled=(current_idx == 0), use_container_width=True):
            st.session_state.alphabet_index = max(0, current_idx - 1)
            st.session_state.alphabet_result = None
            st.rerun()
    
    with col2:
        if st.button("➡️ Next", disabled=(current_idx >= len(alphabets) - 1), use_container_width=True):
            st.session_state.alphabet_index = min(len(alphabets) - 1, current_idx + 1)
            st.session_state.alphabet_result = None
            st.rerun()
    
    with col3:
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.alphabet_result = None
            st.rerun()
    
    with col4:
        if st.button("✅ Back to Practice", type="primary", use_container_width=True):
            st.session_state.practice_mode = 'full'
            st.rerun()
    
    # Check for category completion
    if st.session_state.alphabet_result and st.session_state.alphabet_result['passed']:
        if count_completed_alphabets() == len(alphabets):
            st.balloons()
            st.success(f"🌟 Congratulations! You've completed all {category_name}!")
            
            if st.session_state.alphabet_category == 'vowels':
                st.info("Now let's practice the consonants!")
                if st.button("Start Consonants Practice", type="primary"):
                    st.session_state.alphabet_category = 'consonants'
                    st.session_state.alphabet_index = 0
                    st.session_state.alphabet_result = None
                    st.rerun()
            else:
                st.info("You've mastered the basics! Ready to return to word and shloka practice.")


def get_alphabet_statistics():
    """Get statistics about alphabet practice progress"""
    vowel_completed = 0
    consonant_completed = 0
    total_attempts = 0
    
    for devanagari, score_data in st.session_state.get('alphabet_scores', {}).items():
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
        'total_attempts': total_attempts
    }
