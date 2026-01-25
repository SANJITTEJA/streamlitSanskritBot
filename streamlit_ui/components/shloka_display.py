"""
Shloka Display Component
Shows the current shloka in Devanagari and SLP1 format
"""
import streamlit as st


def render_shloka_display():
    """Render the current shloka display"""
    st.markdown('<div class="panel-header">Current Shloka</div>', unsafe_allow_html=True)
    
    if st.session_state.current_shloka:
        shloka = st.session_state.current_shloka
        
        # Display Devanagari text
        st.markdown(f"""
            <div class="devanagari-text">
                {shloka['devanagari']}
            </div>
        """, unsafe_allow_html=True)
        
        # Display SLP1 transliteration
        st.markdown(f"""
            <div class="slp1-text">
                {shloka['slp1']}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="devanagari-text">
                Select a shloka to practice
            </div>
        """, unsafe_allow_html=True)
