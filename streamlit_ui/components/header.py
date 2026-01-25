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
            <span class="header-emoji">🕉️</span><span class="header-text">Sanskrit Voice Bot</span>
        </div>
        <div class="sub-header">
            An AI Tutor That Listens, Learns, and Corrects Sanskrit Speech- Version {AppConfig.VERSION}
        </div>
    """, unsafe_allow_html=True)
