"""
Header Component for Streamlit UI
Displays the application title and subtitle
"""
import streamlit as st
from core.config import AppConfig


def render_header():
    """Render the main header section"""
    st.markdown(f"""
        <div class="main-header">
            🕉 Sanskrit Voice Bot
        </div>
        <div class="sub-header">
            Learn Sanskrit Pronunciation - Version {AppConfig.VERSION}
        </div>
    """, unsafe_allow_html=True)
