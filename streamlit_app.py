"""
Streamlit Web Interface for Sanskrit Voice Bot v2
Main entry point for the web application
"""
import streamlit as st
from pathlib import Path
import sys

# Add the project root to the Python path for proper imports
PROJECT_ROOT = Path(__file__).parent.parent
V2_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(V2_DIR))

from streamlit_ui.config import StreamlitConfig
from streamlit_ui.components.header import render_header
from streamlit_ui.components.left_panel import render_left_panel
from streamlit_ui.components.right_panel import render_right_panel
from core.config import AppConfig


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'selected_speaker' not in st.session_state:
        st.session_state.selected_speaker = None
    
    if 'selected_shloka_index' not in st.session_state:
        st.session_state.selected_shloka_index = None
    
    if 'current_shloka' not in st.session_state:
        st.session_state.current_shloka = None
    
    if 'available_shlokas' not in st.session_state:
        st.session_state.available_shlokas = []
    
    if 'recording_state' not in st.session_state:
        st.session_state.recording_state = 'idle'
    
    if 'uploaded_audio' not in st.session_state:
        st.session_state.uploaded_audio = None
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'practice_mode' not in st.session_state:
        st.session_state.practice_mode = 'full'
    
    if 'current_word_index' not in st.session_state:
        st.session_state.current_word_index = 0


def apply_custom_css():
    """Apply custom CSS styling with dark modern messaging app design"""
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800;900&family=Cinzel:wght@400;500;600;700;800;900&display=swap');
        
        /* Main container styling */
        .main {{
            background: {StreamlitConfig.COLORS['background']};
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            color: {StreamlitConfig.COLORS['text_primary']};
        }}
        
        /* Hide Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        header {{visibility: hidden;}}
        
        /* Header styling */
        .main-header {{
            text-align: center;
            font-size: 3rem;
            font-weight: 800;
            margin-top: -1rem;
            margin-bottom: 0.3rem;
            letter-spacing: -1.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}
        
        .header-emoji {{
            font-size: 3rem;
            filter: drop-shadow(0 0 10px rgba(124, 58, 237, 0.5));
        }}
        
        .header-text {{
            background: linear-gradient(135deg, {StreamlitConfig.COLORS['gradient_start']} 0%, {StreamlitConfig.COLORS['gradient_end']} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-family: 'Cinzel', serif;
        }}
        
        .sub-header {{
            text-align: center;
            color: {StreamlitConfig.COLORS['text_secondary']};
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
            font-weight: 400;
            letter-spacing: 0.5px;
        }}
        
        /* Card styling */
        div[data-testid="stVerticalBlock"] > div[data-testid="column"] > div {{
            background-color: {StreamlitConfig.COLORS['card_bg']};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 25px {StreamlitConfig.COLORS['shadow']};
            border: 1px solid {StreamlitConfig.COLORS['card_border']};
        }}
        
        /* Panel headers */
        .panel-header {{
            color: {StreamlitConfig.COLORS['text_primary']};
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding: 0 0 0.5rem 0;
            background: transparent;
            border-bottom: 1px solid {StreamlitConfig.COLORS['border']};
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Devanagari text */
        .devanagari-text {{
            font-size: 2rem;
            font-weight: 600;
            text-align: center;
            color: {StreamlitConfig.COLORS['text_primary']};
            padding: 32px 24px;
            background: {StreamlitConfig.COLORS['background']};
            border-radius: 12px;
            margin: 16px 0;
            box-shadow: 0 4px 12px {StreamlitConfig.COLORS['shadow']};
            border: 1px solid {StreamlitConfig.COLORS['card_border']};
            line-height: 1.6;
        }}
        
        /* SLP1 text */
        .slp1-text {{
            font-size: 1.3rem;
            font-style: italic;
            text-align: center;
            color: {StreamlitConfig.COLORS['text_secondary']};
            padding: 20px 24px;
            background: {StreamlitConfig.COLORS['background']};
            border-radius: 12px;
            margin: 16px 0;
            box-shadow: 0 2px 8px {StreamlitConfig.COLORS['shadow']};
            border: 1px solid {StreamlitConfig.COLORS['card_border']};
        }}
        
        /* Button styling */
        .stButton>button {{
            background: linear-gradient(135deg, {StreamlitConfig.COLORS['primary']} 0%, {StreamlitConfig.COLORS['secondary']} 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
        }}
        
        .stButton>button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(99, 102, 241, 0.5);
        }}
        
        .stButton>button[kind="secondary"] {{
            background: {StreamlitConfig.COLORS['card_bg']};
            color: {StreamlitConfig.COLORS['text_primary']};
            border: 1px solid {StreamlitConfig.COLORS['border']};
            box-shadow: 0 2px 6px {StreamlitConfig.COLORS['shadow']};
        }}
        
        .stButton>button[kind="secondary"]:hover {{
            background: {StreamlitConfig.COLORS['hover']};
            border-color: {StreamlitConfig.COLORS['primary']};
        }}
        
        .stButton>button[kind="primary"] {{
            background: linear-gradient(135deg, {StreamlitConfig.COLORS['primary']} 0%, {StreamlitConfig.COLORS['secondary']} 100%);
            border: none;
        }}
        
        /* Selectbox styling */
        .stSelectbox label {{
            color: {StreamlitConfig.COLORS['text_secondary']};
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stSelectbox > div > div {{
            background: {StreamlitConfig.COLORS['background']};
            border-radius: 8px;
            border: 1px solid {StreamlitConfig.COLORS['border']};
            transition: all 0.2s;
            color: {StreamlitConfig.COLORS['text_primary']};
        }}
        
        .stSelectbox > div > div:focus-within {{
            border-color: {StreamlitConfig.COLORS['primary']};
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }}
        
        /* File uploader styling */
        .stFileUploader > div {{
            border-radius: 12px;
            border: 2px dashed {StreamlitConfig.COLORS['border']};
            padding: 20px;
            background: {StreamlitConfig.COLORS['background']};
            transition: all 0.3s ease;
        }}
        
        .stFileUploader > div:hover {{
            border-color: {StreamlitConfig.COLORS['primary']};
            background: {StreamlitConfig.COLORS['card_bg']};
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: {StreamlitConfig.COLORS['background']};
            border-radius: 8px;
            padding: 4px;
            border-bottom: 1px solid {StreamlitConfig.COLORS['border']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            color: {StreamlitConfig.COLORS['text_secondary']};
            font-size: 0.9rem;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {StreamlitConfig.COLORS['primary']} 0%, {StreamlitConfig.COLORS['secondary']} 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background: {StreamlitConfig.COLORS['card_bg']};
            border-radius: 8px;
            font-weight: 500;
            color: {StreamlitConfig.COLORS['text_primary']};
            border: 1px solid {StreamlitConfig.COLORS['border']};
        }}
        
        /* Success/Error/Warning boxes */
        .stSuccess {{
            background-color: {StreamlitConfig.COLORS['success_light']};
            border-left: 4px solid {StreamlitConfig.COLORS['success']};
            border-radius: 8px;
            padding: 16px;
            color: {StreamlitConfig.COLORS['text_primary']};
        }}
        
        .stError {{
            background-color: {StreamlitConfig.COLORS['error_light']};
            border-left: 4px solid {StreamlitConfig.COLORS['error']};
            border-radius: 8px;
            padding: 16px;
            color: {StreamlitConfig.COLORS['text_primary']};
        }}
        
        .stWarning {{
            background-color: {StreamlitConfig.COLORS['warning_light']};
            border-left: 4px solid {StreamlitConfig.COLORS['warning']};
            border-radius: 8px;
            padding: 16px;
            color: {StreamlitConfig.COLORS['text_primary']};
        }}
        
        .stInfo {{
            background-color: {StreamlitConfig.COLORS['info_light']};
            border-left: 4px solid {StreamlitConfig.COLORS['info']};
            border-radius: 8px;
            padding: 16px;
            color: {StreamlitConfig.COLORS['text_primary']};
        }}
        
        /* Progress bar */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {StreamlitConfig.COLORS['primary']} 0%, {StreamlitConfig.COLORS['secondary']} 100%);
            border-radius: 10px;
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {StreamlitConfig.COLORS['background']};
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {StreamlitConfig.COLORS['border']};
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {StreamlitConfig.COLORS['primary']};
        }}
        
        /* Success/Error text */
        .success-text {{
            color: {StreamlitConfig.COLORS['success']};
            font-weight: 600;
        }}
        
        .error-text {{
            color: {StreamlitConfig.COLORS['error']};
            font-weight: 600;
        }}
        
        .warning-text {{
            color: {StreamlitConfig.COLORS['warning']};
            font-weight: 600;
        }}
        
        /* Results card */
        .results-card {{
            background: {StreamlitConfig.COLORS['card_bg']};
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 20px {StreamlitConfig.COLORS['shadow']};
            border: 1px solid {StreamlitConfig.COLORS['card_border']};
            margin: 20px 0;
        }}
        
        /* Gradient boxes */
        .gradient-box {{
            background: {StreamlitConfig.COLORS['success_light']};
            border-radius: 12px;
            padding: 24px;
            border: 2px solid {StreamlitConfig.COLORS['success']};
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }}
        
        .gradient-box-error {{
            background: {StreamlitConfig.COLORS['error_light']};
            border-radius: 12px;
            padding: 24px;
            border: 2px solid {StreamlitConfig.COLORS['error']};
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }}
        
        /* Input fields */
        input, textarea {{
            background: {StreamlitConfig.COLORS['background']} !important;
            color: {StreamlitConfig.COLORS['text_primary']} !important;
            border: 1px solid {StreamlitConfig.COLORS['border']} !important;
        }}
        
        /* Audio player */
        audio {{
            filter: invert(1) hue-rotate(180deg);
        }}
        </style>
    """, unsafe_allow_html=True)


def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Sanskrit Voice Bot",
        page_icon="🕉",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Render header
    render_header()
    
    # Create two-column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_left_panel()
    
    with col2:
        render_right_panel()


if __name__ == "__main__":
    main()
