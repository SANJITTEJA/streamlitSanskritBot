"""
Word Practice Component
Handles practice of individual mispronounced words with tracking and analysis
"""
import streamlit as st
import sys
from pathlib import Path

# Add v2 to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_ui.backend_integration import get_backend
from tracking.word_practice_tracker import WordPracticeTracker


def render_word_practice():
    """Render individual word practice interface"""
    
    # Initialize word tracker if not exists
    if 'word_tracker' not in st.session_state:
        st.session_state.word_tracker = WordPracticeTracker()
    
    # Check if we have words to practice
    if not st.session_state.get('words_to_practice'):
        st.info("📝 No words selected for practice. Complete a full shloka practice first to identify areas for improvement.")
        return
    
    # Get current word index
    if 'current_word_practice_index' not in st.session_state:
        st.session_state.current_word_practice_index = 0
    
    words_list = st.session_state.words_to_practice
    current_idx = st.session_state.current_word_practice_index
    
    if current_idx >= len(words_list):
        st.success("🎉 You've practiced all selected words!")
        if st.button("Start New Practice Session", type="primary"):
            st.session_state.current_word_practice_index = 0
            st.session_state.words_to_practice = []
            st.session_state.practice_mode = 'full'
            st.rerun()
        return
    
    current_word = words_list[current_idx]
    
    # Get the correct original word from shloka (not what user said)
    # The 'devanagari' field contains the actual shloka word
    # The 'original' field contains what the user said
    word_key = current_word.get('devanagari', current_word.get('original', ''))
    
    # For display and audio extraction, prioritize devanagari
    original_shloka_word = current_word.get('devanagari', word_key)
    
    # Clean up the SLP1 text - remove any HTML tags and get clean text
    slp1_text = current_word.get('slp1', '')
    if not slp1_text or '<' in slp1_text:
        # Fallback to original or word_key if slp1 contains HTML or is empty
        slp1_text = current_word.get('original', word_key)
    
    # Header
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #a78bfa; margin-bottom: 5px;">Word Practice</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">Word {current_idx + 1} of {len(words_list)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress = (current_idx + 1) / len(words_list)
    st.progress(progress)
    
    # Display current word with audio playback
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%); 
             border: 3px solid #7c3aed; border-radius: 16px; padding: 50px 40px; 
             text-align: center; margin: 30px 0; box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);">
            <div style="font-size: 4.5rem; font-weight: 700; color: #ffffff; 
                 margin-bottom: 20px; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3); 
                 letter-spacing: 2px;">
                {word_key}
            </div>
            <div style="font-size: 1.5rem; color: #c4b5fd; font-style: italic; 
                 font-weight: 500; letter-spacing: 1px;">
                {slp1_text}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate and play audio for the word using audio extraction
    st.markdown("### 🔊 Listen to Correct Pronunciation")
    
    # Debug info
    has_shloka = st.session_state.current_shloka is not None
    has_audio = has_shloka and st.session_state.current_shloka.get('audio_data') is not None
    
    if not has_shloka:
        st.warning("⚠️ No shloka selected. Please select a shloka first.")
    elif not has_audio:
        st.warning("⚠️ Original shloka audio not available.")
    else:
        try:
            from audio.word_audio_extractor import extract_word_audio
            import base64
            
            shloka_audio_base64 = st.session_state.current_shloka.get('audio_data')
            shloka_audio_format = st.session_state.current_shloka.get('audio_format', 'mp3')
            shloka_text = st.session_state.current_shloka.get('devanagari', '')
            # Get pre-computed word timestamps if available
            word_timestamps = st.session_state.current_shloka.get('word_timestamps', None)
            
            with st.spinner("Extracting word audio (using Whisper timestamps)..."):
                # Extract word audio using REAL timestamps from Whisper API
                word_audio_bytes = extract_word_audio(
                    shloka_audio_base64=shloka_audio_base64,
                    shloka_audio_format=shloka_audio_format,
                    word_text=original_shloka_word,  # Use the actual shloka word
                    shloka_text=shloka_text,
                    word_timestamps=word_timestamps  # Pass pre-computed timestamps
                )
            
            if word_audio_bytes:
                # Validate the audio bytes
                if len(word_audio_bytes) < 100:
                    st.warning("⚠️ Audio file too small, using full shloka")
                    audio_bytes = base64.b64decode(shloka_audio_base64)
                    format_map = {
                        'm4a': 'audio/mp4',
                        'mp3': 'audio/mpeg',
                        'wav': 'audio/wav',
                        'ogg': 'audio/ogg'
                    }
                    mime_type = format_map.get(shloka_audio_format, f'audio/{shloka_audio_format}')
                    st.audio(audio_bytes, format=mime_type)
                else:
                    # Display audio player for the extracted word
                    st.success(f"✅ Playing pronunciation of '{word_key}'")
                    # Use explicit MIME type for WAV
                    st.audio(word_audio_bytes, format='audio/wav', start_time=0)
            else:
                # Fallback: show full shloka audio
                st.info("💡 Playing full shloka audio (word extraction unavailable)")
                audio_bytes = base64.b64decode(shloka_audio_base64)
                
                # Map format for browser compatibility
                format_map = {
                    'm4a': 'audio/mp4',
                    'mp3': 'audio/mpeg',
                    'wav': 'audio/wav',
                    'ogg': 'audio/ogg'
                }
                mime_type = format_map.get(shloka_audio_format, f'audio/{shloka_audio_format}')
                
                st.audio(audio_bytes, format=mime_type)
                
        except Exception as e:
            st.error(f"❌ Error with audio: {str(e)}")
            
            # Show full audio as fallback
            try:
                import base64
                shloka_audio_base64 = st.session_state.current_shloka.get('audio_data')
                shloka_audio_format = st.session_state.current_shloka.get('audio_format', 'mp3')
                audio_bytes = base64.b64decode(shloka_audio_base64)
                
                format_map = {
                    'm4a': 'audio/mp4',
                    'mp3': 'audio/mpeg',
                    'wav': 'audio/wav',
                    'ogg': 'audio/ogg'
                }
                mime_type = format_map.get(shloka_audio_format, f'audio/{shloka_audio_format}')
                
                st.info("📻 Playing full shloka audio as fallback")
                st.audio(audio_bytes, format=mime_type)
            except Exception as fallback_error:
                st.error(f"Could not play audio: {str(fallback_error)}")
    
    # Get word statistics
    word_stats = st.session_state.word_tracker.get_word_statistics(word_key)
    
    # Show statistics if attempts exist with improved design
    if word_stats['total_attempts'] > 0:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(99, 102, 241, 0.3);">
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 5px;">ATTEMPTS</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #f1f5f9;">{word_stats['total_attempts']}</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(16, 185, 129, 0.3);">
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 5px;">BEST SCORE</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #10b981;">{word_stats['best_accuracy']:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div style="background: rgba(168, 85, 247, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(168, 85, 247, 0.3);">
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 5px;">LAST SCORE</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #a855f7;">{word_stats['last_accuracy']:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Audio recording section
    st.markdown("---")
    st.markdown("### 🎤 Record Your Pronunciation")
    
    audio_value = st.audio_input(f"Record pronunciation of '{word_key}'", key=f"word_audio_{current_idx}")
    
    if audio_value:
        audio_bytes = audio_value.read()
        
        # Analyze button
        if st.button("🔍 Analyze My Pronunciation", type="primary", use_container_width=True):
            with st.spinner("Analyzing your pronunciation..."):
                # Analyze single word using the SAME logic as full shloka
                backend = get_backend()
                
                # Transcribe user's audio
                transcription_result = backend.transcribe_audio(audio_bytes)
                
                if transcription_result.get('success'):
                    user_said = transcription_result.get('transcription', '').strip()
                    
                    # Use the SAME text processor and alignment logic as full shloka
                    from utils.text_processor import TextProcessor
                    text_processor = TextProcessor()
                    
                    # Split both into words
                    original_words = text_processor.smart_word_split(original_shloka_word)
                    user_words = text_processor.smart_word_split(user_said)
                    
                    # Align words (same as full shloka analysis)
                    word_results = text_processor.align_words(original_words, user_words, [])
                    
                    # Calculate accuracy based on alignment
                    if word_results and len(word_results) > 0:
                        # Get the first word result (since we're practicing one word)
                        first_result = word_results[0]
                        accuracy = first_result['similarity'] * 100
                        is_correct = first_result['correct']
                    else:
                        # Fallback to simple similarity
                        similarity = text_processor.calculate_similarity(original_shloka_word, user_said)
                        accuracy = similarity * 100
                        is_correct = accuracy >= 70
                    
                    # Record the attempt
                    st.session_state.word_tracker.record_word_attempt(word_key, accuracy, user_said)
                    
                    # Store result
                    st.session_state.word_practice_result = {
                        'word': word_key,
                        'expected': original_shloka_word,
                        'user_said': user_said,
                        'accuracy': accuracy,
                        'passed': is_correct
                    }
                        # 'passed': accuracy >= 70
                    
                    
                    # Check if suggestion is needed
                    should_suggest = st.session_state.word_tracker.should_suggest_alphabet_practice(word_key)
                    st.session_state.show_suggestion = should_suggest
                    
                    st.rerun()
                else:
                    st.error(f"Failed to analyze: {transcription_result.get('error', 'Unknown error')}")
    
    # Display result if exists
    if st.session_state.get('word_practice_result'):
        result = st.session_state.word_practice_result
        
        if result['word'] == word_key:  # Make sure result matches current word
            st.markdown("---")
            st.markdown("### 📊 Your Result")
            
            # Result card
            bg_color = "rgba(16, 185, 129, 0.1)" if result['passed'] else "rgba(239, 68, 68, 0.1)"
            border_color = "#10b981" if result['passed'] else "#ef4444"
            icon = "✅" if result['passed'] else "❌"
            
            st.markdown(f"""
                <div style="background: {bg_color}; border: 2px solid {border_color}; 
                     border-radius: 12px; padding: 20px; margin: 15px 0;">
                    <div style="font-size: 1.5rem; text-align: center; margin-bottom: 10px;">
                        {icon} {result['accuracy']:.1f}% Accuracy
                    </div>
                    <div style="text-align: center; color: #94a3b8; font-size: 0.9rem;">
                        You said: <strong style="color: #f1f5f9;">{result['user_said']}</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", use_container_width=True):
                    # Clear result to try again
                    st.session_state.word_practice_result = None
                    st.rerun()
            
            with col2:
                if current_idx < len(words_list) - 1:
                    if st.button("➡️ Next Word", type="primary", use_container_width=True):
                        st.session_state.current_word_practice_index += 1
                        st.session_state.word_practice_result = None
                        st.session_state.show_suggestion = False
                        st.rerun()
                else:
                    if st.button("✅ Complete Practice", type="primary", use_container_width=True):
                        st.session_state.current_word_practice_index = 0
                        st.session_state.words_to_practice = []
                        st.session_state.word_practice_result = None
                        st.session_state.practice_mode = 'full'
                        st.success("Great job completing the practice session!")
                        st.rerun()
    
    # Show suggestion dialog if needed
    if st.session_state.get('show_suggestion'):
        st.markdown("---")
        suggestion_msg = st.session_state.word_tracker.get_suggestion_message(word_key, word_key)
        
        st.warning("⚠️ Suggestion")
        st.markdown(suggestion_msg)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📚 Next Shloka", use_container_width=True):
                # Move to next shloka
                if st.session_state.selected_shloka_index is not None:
                    st.session_state.selected_shloka_index += 1
                st.session_state.practice_mode = 'full'
                st.session_state.words_to_practice = []
                st.session_state.show_suggestion = False
                st.rerun()
        
        with col2:
            if st.button("🔤 Alphabet Practice", type="primary", use_container_width=True):
                st.session_state.practice_mode = 'alphabet'
                st.session_state.show_suggestion = False
                st.rerun()
        
        with col3:
            if st.button("🔄 Keep Trying", use_container_width=True):
                st.session_state.show_suggestion = False
                st.session_state.word_practice_result = None
                st.rerun()


def select_words_for_practice():
    """Allow user to select which mispronounced words to practice"""
    if not st.session_state.get('analysis_results'):
        return
    
    results = st.session_state.analysis_results
    incorrect_words = results.get('incorrect_words', [])
    
    if not incorrect_words:
        st.info("🎉 No mispronounced words! Great job!")
        return
    
    st.markdown("### 🎯 Select Words to Practice")
    st.markdown("Choose which words you'd like to focus on:")
    
    selected_words = []
    
    for i, word in enumerate(incorrect_words):
        word_key = word.get('devanagari', word.get('original', ''))
        slp1 = word.get('slp1', word.get('original', ''))
        user_said = word.get('user', '')
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <strong style="font-size: 1.1rem; color: #f1f5f9;">{word_key}</strong><br/>
                    <span style="color: #94a3b8; font-size: 0.85rem;">
                        Expected: {slp1} | You said: {user_said}
                    </span>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.checkbox("Select", key=f"select_word_{i}", value=True):
                selected_words.append(word)
    
    if selected_words:
        if st.button("✅ Start Practicing Selected Words", type="primary", use_container_width=True):
            st.session_state.words_to_practice = selected_words
            st.session_state.current_word_practice_index = 0
            st.session_state.practice_mode = 'word'
            st.session_state.word_practice_result = None
            st.rerun()
