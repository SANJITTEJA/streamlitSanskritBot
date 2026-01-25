"""
Audio Controls Component
Handles playing original audio
"""
import streamlit as st
import base64


def render_audio_controls():
    """Render audio control buttons"""
    
    if st.session_state.current_shloka:
        audio_data = st.session_state.current_shloka.get('audio_data')
        audio_format = st.session_state.current_shloka.get('audio_format', 'mp3')
        
        if audio_data:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown("**🔊 Play Original**")
            
            with col2:
                st.audio(audio_bytes, format=f'audio/{audio_format}')
        else:
            st.warning("Audio not available for this shloka")
    else:
        st.info("Select a shloka to play audio")
