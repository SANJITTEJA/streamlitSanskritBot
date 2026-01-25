"""
Streamlit-specific configuration for Sanskrit Voice Bot
"""
from pathlib import Path

class StreamlitConfig:
    """Configuration settings for Streamlit interface"""
    
    # Color scheme - Dark modern messaging app inspired
    COLORS = {
        'primary': '#6366f1',        # Indigo
        'secondary': '#8b5cf6',      # Violet
        'success': '#10b981',        # Emerald green
        'error': '#ef4444',          # Red
        'warning': '#f59e0b',        # Amber
        'info': "#3b82f6",           # Blue
        'accent': '#a855f7',         # Purple
        'muted': '#9ca3af',          # Gray
        'background': "#1e293b",     # Dark slate
        'card_bg': '#2d3748',        # Dark card
        'card_border': '#374151',    # Dark border
        'hover': '#374151',          # Dark hover
        'border': '#4b5563',         # Gray border
        'text_primary': '#f1f5f9',   # Light text
        'text_secondary': '#94a3b8', # Muted text
        'gradient_start': '#6366f1',  # Indigo
        'gradient_end': '#8b5cf6',    # Violet
        'success_light': '#065f46',   # Dark success bg
        'error_light': '#7f1d1d',     # Dark error bg
        'warning_light': '#78350f',   # Dark warning bg
        'info_light': '#1e3a8a',      # Dark info bg
        'highlight': '#312e81',       # Dark highlight
        'shadow': 'rgba(0, 0, 0, 0.3)', # Dark shadow
    }
    
    # Layout settings
    PANEL_SPACING = 20
    COMPONENT_SPACING = 15
    
    # Audio settings
    AUDIO_SAMPLE_RATE = 44100
    MAX_RECORDING_DURATION = 30
