"""
Right Panel Component for Streamlit UI
Minimalist single-tile design
"""
import streamlit as st
from streamlit_ui.components.shloka_display import render_shloka_display
from streamlit_ui.components.audio_controls import render_audio_controls
from streamlit_ui.components.practice_section import render_practice_section
from streamlit_ui.components.results_display import render_results_display


def render_right_panel():
    """Render the right panel as a single compact tile"""
    
    if not st.session_state.current_shloka:
        st.markdown("""
            <div style="text-align: center; padding: 60px 20px; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 16px;">📖</div>
                <h3 style="color: #94a3b8; font-weight: 500;">Select a shloka to begin</h3>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Compact shloka display
    st.markdown(f"""
        <div style="text-align: center; padding: 16px 12px; background: rgba(99, 102, 241, 0.05); 
             border-radius: 8px; margin-bottom: 12px; border-left: 3px solid #6366f1;">
            <div style="font-size: 1.4rem; font-weight: 600; color: #f1f5f9; margin-bottom: 6px; line-height: 1.5;">
                {st.session_state.current_shloka['devanagari']}
            </div>
            <div style="font-size: 0.95rem; font-style: italic; color: #94a3b8;">
                {st.session_state.current_shloka['slp1']}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Audio player inline
    if st.session_state.current_shloka.get('audio_data'):
        import base64
        audio_data = st.session_state.current_shloka.get('audio_data')
        audio_format = st.session_state.current_shloka.get('audio_format', 'mp3')
        
        # Map formats for browser compatibility
        format_map = {
            'm4a': 'audio/mp4',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg'
        }
        
        mime_type = format_map.get(audio_format, f'audio/{audio_format}')
        
        try:
            audio_bytes = base64.b64decode(audio_data)
            st.audio(audio_bytes, format=mime_type)
        except Exception as e:
            st.error(f"Could not load audio: {str(e)}")
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    # Compact practice section
    render_practice_section()
    
    # Compact results (if any)
    if st.session_state.analysis_results:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        render_results_display()
