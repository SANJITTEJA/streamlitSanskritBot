"""
Practice Section Component
Handles recording, file upload, and analysis controls
"""
import streamlit as st
import base64
from database.db_manager import get_db_manager
from streamlit_ui.backend_integration import get_backend


def render_practice_section():
    """Render compact practice section"""
    
    # Compact tabs for recording/upload
    tab1, tab2 = st.tabs(["🎤 Record", "📁 Upload"])
    
    with tab1:
        st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 8px;">
                    Click the microphone button below to record your chanting
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Native Streamlit audio input
        audio_value = st.audio_input("Record your chanting")
        
        if audio_value:
            # Read the audio bytes
            audio_bytes = audio_value.read()
            st.session_state.uploaded_audio = audio_bytes
            st.session_state.recording_state = 'recorded'
            
            st.markdown("""
                <div style="text-align: center; margin-top: 12px; padding: 10px; 
                     background: rgba(16, 185, 129, 0.1); border-radius: 8px; 
                     border: 1px solid #10b981;">
                    <span style="color: #10b981; font-weight: 600;">✓ Recording Complete</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Audio playback
            st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #64748b; margin-top: 8px;'>Listen to your recording:</p>", unsafe_allow_html=True)
            st.audio(audio_bytes, format='audio/wav')
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Audio file",
            type=['wav', 'mp3', 'm4a', 'ogg'],
            key='audio_uploader',
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_audio = uploaded_file.read()
            st.session_state.recording_state = 'uploaded'
            st.success("✓ File ready", icon="✅")
    
    # Compact analysis button
    if st.session_state.uploaded_audio or st.session_state.recording_state == 'recorded':
        if st.button("🔍Analyze", use_container_width=True, type="primary"):
            analyze_pronunciation()


def analyze_pronunciation():
    """Handle pronunciation analysis and save to database"""
    
    # Get backend instance
    backend = get_backend()
    
    # Get current shloka info
    current_shloka = st.session_state.current_shloka
    
    # Analyze pronunciation - backend will transcribe both audio files and compare
    with st.spinner('🎙️ Transcribing and analyzing your pronunciation...'):
        analysis_results = backend.analyze_pronunciation(
            user_audio_bytes=st.session_state.uploaded_audio,
            original_shloka=current_shloka,
            practice_mode=st.session_state.practice_mode
        )
        
        if not analysis_results.get('success', True):
            st.error(f"❌ Analysis failed: {analysis_results.get('error', 'Unknown error')}")
            return
    
    # Step 3: Save practice session to database
    try:
        db = get_db_manager()
        
        # Encode audio data to base64 for storage
        audio_data = st.session_state.uploaded_audio
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Get current info
        speaker_id = st.session_state.selected_speaker
        shloka_number = current_shloka['shloka_number']
        
        # Create practice session
        session = db.create_practice_session(
            speaker_id=speaker_id,
            shloka_number=shloka_number,
            user_audio_data=audio_base64,
            user_audio_format='wav',  # or detect from uploaded file
            transcribed_text=analysis_results['user_transcription'],
            accuracy_score=analysis_results['accuracy'],
            pronunciation_score=analysis_results['accuracy'],
            llm_feedback=str(analysis_results.get('llm_feedback', {})),
            word_comparison=analysis_results.get('incorrect_words', []),
            practice_mode=st.session_state.practice_mode,
            passed=analysis_results.get('passed', False)
        )
        
        st.session_state.analysis_results = analysis_results
        
    except Exception as e:
        st.error(f"Error saving practice session: {str(e)}")
        # Still show results even if save fails
        st.session_state.analysis_results = analysis_results
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #ffffff 100%); 
             padding: 16px; border-radius: 12px; margin: 16px 0; 
             border: 2px solid #3b82f6; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);">
            <p style="color: #1e40af; font-weight: 600; margin: 0;">
                ✓ Analysis complete! See detailed results below.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.rerun()
