"""
Left Panel Component for Streamlit UI
Contains speaker and shloka selection
"""
import streamlit as st
from database.db_manager import get_db_manager


def load_shlokas_for_speaker(speaker_id):
    """Load available shlokas for the selected speaker from database"""
    db = get_db_manager()
    shlokas = db.get_shlokas_for_speaker(speaker_id)
    
    shlokas_list = []
    for shloka in shlokas:
        shlokas_list.append({
            'id': f"{speaker_id}_shloka{shloka.shloka_number}",
            'shloka_number': shloka.shloka_number,
            'devanagari': shloka.devanagari_text,
            'slp1': shloka.slp1_text,
            'audio_data': shloka.audio_data,  # Base64 encoded audio
            'audio_format': shloka.audio_format,  # mp3, wav, etc.
            'display': f"Shloka {shloka.shloka_number}: {shloka.devanagari_text[:50]}..."
        })
    
    return shlokas_list


def render_left_panel():
    """Render the left panel with speaker and shloka selection"""
    
    # Speaker Selection Section
    st.markdown("""
        <div class="panel-header">
            <span style="font-size: 1.3rem; margin-right: 8px;">👤</span>
            Select Speaker
        </div>
    """, unsafe_allow_html=True)
    
    # Get speaker list from database
    db = get_db_manager()
    speaker_list = db.get_speaker_list()
    
    if not speaker_list:
        st.error("No speakers found in database. Please run the data migration script.")
        return
    
    # Format speaker ID (sp001) to display name (Speaker 1)
    def format_speaker_name(idx):
        speaker_id = speaker_list[idx]
        # Extract number from sp001, sp002, etc.
        num = int(speaker_id.replace('sp', ''))
        return f"Speaker {num}"
    
    selected_speaker_index = st.selectbox(
        "Choose a speaker",
        options=range(len(speaker_list)),
        format_func=format_speaker_name,
        key='speaker_selectbox',
        label_visibility="collapsed"
    )
    
    # Update session state when speaker changes
    if selected_speaker_index is not None:
        speaker_id = speaker_list[selected_speaker_index]
        
        if st.session_state.selected_speaker != speaker_id:
            st.session_state.selected_speaker = speaker_id
            st.session_state.available_shlokas = load_shlokas_for_speaker(speaker_id)
            st.session_state.selected_shloka_index = None
            st.session_state.current_shloka = None
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Shloka Selection Section
    st.markdown("""
        <div class="panel-header">
            <span style="font-size: 1.3rem; margin-right: 8px;">📖</span>
            Select Shloka
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.available_shlokas:
        # Show only first 10 shlokas as compact dropdown
        shlokas_to_display = st.session_state.available_shlokas[:10]
        
        # Create compact display options
        shloka_options = [
            f"Shloka {s['shloka_number']}: {s['devanagari'][:40]}..." 
            if len(s['devanagari']) > 40 
            else f"Shloka {s['shloka_number']}: {s['devanagari']}"
            for s in shlokas_to_display
        ]
        
        # Add custom CSS for smaller font in selectbox
        st.markdown("""
            <style>
            .shloka-select label {
                font-size: 0.75rem !important;
            }
            .shloka-select [data-baseweb="select"] {
                font-size: 0.8rem !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        selected_shloka_idx = st.selectbox(
            "Choose a shloka to practice",
            options=range(len(shlokas_to_display)),
            format_func=lambda x: shloka_options[x],
            key='shloka_selectbox',
            label_visibility="collapsed"
        )
        
        # Update session state when shloka changes
        if selected_shloka_idx is not None:
            if st.session_state.selected_shloka_index != selected_shloka_idx:
                st.session_state.selected_shloka_index = selected_shloka_idx
                st.session_state.current_shloka = shlokas_to_display[selected_shloka_idx]
                st.rerun()
        
        # Show total count info
        total_shlokas = len(st.session_state.available_shlokas)
        if total_shlokas > 10:
            st.markdown(f"""
                <div style="font-size: 0.75rem; color: #64748b; text-align: center; margin-top: 8px;">
                    Showing 10 of {total_shlokas} shlokas
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #dbeafe 0%, #f8fafc 100%); 
                 padding: 20px; border-radius: 12px; text-align: center; 
                 border: 2px solid #3b82f6; margin: 16px 0;">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">📚</div>
                <p style="color: #1e293b; font-weight: 500; font-size: 0.9rem; margin: 0;">
                    Select a speaker to view available shlokas
                </p>
            </div>
        """, unsafe_allow_html=True)
