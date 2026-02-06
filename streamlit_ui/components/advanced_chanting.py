"""
Advanced Chanting Analysis Component
Meter (Laghu-Guru) and Pitch Analysis for Sanskrit Shlokas
Ported from chanting_app.py (Gradio) to Streamlit
"""
import streamlit as st
import numpy as np
import os
import tempfile
import requests
from typing import Tuple, List, Dict, Optional
import io

# Import audio libraries
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from core.config import AudioConfig

# Sanskrit character mappings
DEVANAGARI_TO_IAST = {
    'अ': 'a', 'आ': 'A', 'इ': 'i', 'ई': 'I', 'उ': 'u', 'ऊ': 'U',
    'ऋ': '_r', 'ॠ': '_R', 'ऌ': '_l', 'ॡ': '_L',
    'ए': 'e', 'ऐ': 'E', 'ओ': 'o', 'औ': 'O',
    'ा': 'A', 'ि': 'i', 'ी': 'I', 'ु': 'u', 'ू': 'U',
    'ृ': '_r', 'ॄ': '_R', 'ॢ': '_l', 'ॣ': '_L',
    'े': 'e', 'ै': 'E', 'ो': 'o', 'ौ': 'O',
    'ं': 'M', 'ः': 'H', '्': '', 'ँ': 'M',
    'क': 'ka', 'ख': 'Ka', 'ग': 'ga', 'घ': 'Ga', 'ङ': '_na',
    'च': 'ca', 'छ': 'Ca', 'ज': 'ja', 'झ': 'Ja', 'ञ': '_Na',
    'ट': 'Ta', 'ठ': '_Ta', 'ड': 'Da', 'ढ': '_Da', 'ण': 'Na',
    'त': 'ta', 'थ': '_ta', 'द': 'da', 'ध': '_da', 'न': 'na',
    'प': 'pa', 'फ': 'Pa', 'ब': 'ba', 'भ': 'Ba', 'म': 'ma',
    'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
    'श': 'za', 'ष': 'Sa', 'स': 'sa', 'ह': 'ha',
    'ळ': 'La', '।': '|', '॥': '||', ' ': ' ',
}


def devanagari_to_transliteration(text: str) -> str:
    """Convert Devanagari to transliteration"""
    result = []
    i = 0
    text = text.strip()
    
    while i < len(text):
        char = text[i]
        if char in DEVANAGARI_TO_IAST:
            trans = DEVANAGARI_TO_IAST[char]
            if trans and trans.endswith('a') and len(trans) >= 2:
                if i + 1 < len(text):
                    next_char = text[i + 1]
                    if next_char == '्':
                        result.append(trans[:-1])
                        i += 2
                        continue
                    elif next_char in DEVANAGARI_TO_IAST and DEVANAGARI_TO_IAST[next_char] in ['A', 'i', 'I', 'u', 'U', '_r', '_R', '_l', '_L', 'e', 'E', 'o', 'O']:
                        result.append(trans[:-1] + DEVANAGARI_TO_IAST[next_char])
                        i += 2
                        continue
            result.append(trans)
        else:
            result.append(char)
        i += 1
    return ''.join(result)


def preprocessing(text: str) -> str:
    """Preprocess text for meter analysis"""
    prep_string = ""
    i = 0
    while i < len(text):
        if text[i] in ['M', 'H']:
            if i >= 2 and text[i-2] == '_':
                prep_string = prep_string[:-2] + text[i]
            elif i >= 1:
                prep_string = prep_string[:-1] + text[i]
            else:
                prep_string += text[i]
        else:
            prep_string += text[i]
        i += 1
    return prep_string


def laghu_guru(str_ver: str) -> str:
    """Convert verse to Laghu (L) and Guru (G) pattern"""
    vyanjana = ["k", "K", "g", "G", "_n", "c", "C", "j", "J", "_N", 
                "T", "_T", "D", "_D", "N", "t", "_t", "d", "_d", "n", 
                "p", "P", "b", "B", "m", "y", "r", "l", "v", "z", 
                "S", "s", "h", "L", "R", "_L"]
    hrasva_svara = ["a", "i", "u", "_r", "_l", "e", "o"]
    dirgha_svara = ["A", "I", "U", "_R", "E", "_I", "O", "_O", "M", "H"]
    
    la_gr = ""
    i = 0
    ver_len = len(str_ver)
    
    while i < ver_len:
        if i < ver_len and str_ver[i] == '_':
            str_dummy = str_ver[i:i+2]
            i += 2
        else:
            str_dummy = str_ver[i]
            i += 1
        
        if str_dummy in hrasva_svara:
            la_gr += "L"
        elif str_dummy in dirgha_svara:
            la_gr += "G"
        elif str_dummy in vyanjana:
            la_gr += "V"
    return la_gr


def remove_vyanjana(lg_string: str) -> str:
    """Remove consonants and adjust for clusters"""
    lg = ""
    v_count = 0
    pos = 0
    
    for char in lg_string:
        if char == 'V':
            v_count += 1
        else:
            if v_count >= 2 and pos >= 1:
                lg = lg[:-1] + 'G'
            v_count = 0
            lg += char
            pos += 1
    return lg


def transcribe_audio_for_chanting(audio_bytes: bytes, language: str = 'sa') -> Tuple[str, bool]:
    """Transcribe audio using Groq Whisper API"""
    try:
        headers = {"Authorization": f"Bearer {AudioConfig.GROQ_API_KEY}"}
        files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
        data = {
            'model': AudioConfig.WHISPER_MODEL, 
            'language': language, 
            'response_format': 'json'
        }
        
        response = requests.post(AudioConfig.GROQ_API_URL, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            return response.json().get('text', ''), True
        else:
            return f"API Error: {response.status_code}", False
    except Exception as e:
        return f"Error: {str(e)}", False


def extract_pitch(audio_bytes: bytes) -> Tuple[np.ndarray, np.ndarray, int]:
    """Extract pitch (F0) from audio using librosa's pyin algorithm"""
    if not HAS_LIBROSA:
        return np.array([]), np.array([]), 22050
    
    try:
        # Load audio from bytes
        audio_io = io.BytesIO(audio_bytes)
        y, sr = librosa.load(audio_io, sr=None)
        
        # Extract pitch using pyin
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, 
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C6'),
            sr=sr
        )
        
        times = librosa.times_like(f0, sr=sr)
        return times, f0, sr
    except Exception as e:
        print(f"Pitch extraction error: {e}")
        return np.array([]), np.array([]), 22050


def get_pitch_per_syllable(audio_bytes: bytes, num_syllables: int) -> List[Dict]:
    """Extract average pitch for each syllable segment"""
    times, pitches, sr = extract_pitch(audio_bytes)
    
    if len(pitches) == 0 or num_syllables == 0:
        return []
    
    segment_size = len(pitches) // num_syllables
    syllable_pitches = []
    
    for i in range(num_syllables):
        start_idx = i * segment_size
        end_idx = (i + 1) * segment_size if i < num_syllables - 1 else len(pitches)
        
        segment = pitches[start_idx:end_idx]
        valid_pitches = segment[~np.isnan(segment)]
        
        if len(valid_pitches) > 0:
            avg_pitch = np.mean(valid_pitches)
            min_pitch = np.min(valid_pitches)
            max_pitch = np.max(valid_pitches)
        else:
            avg_pitch = 0
            min_pitch = 0
            max_pitch = 0
        
        syllable_pitches.append({
            'avg': avg_pitch,
            'min': min_pitch,
            'max': max_pitch,
            'start_time': times[start_idx] if start_idx < len(times) else 0,
            'end_time': times[end_idx - 1] if end_idx - 1 < len(times) else 0
        })
    
    return syllable_pitches


def get_pitch_direction(current_pitch: float, next_pitch: float) -> str:
    """Determine pitch direction between syllables"""
    if next_pitch == 0 or current_pitch == 0:
        return "→"
    
    diff = next_pitch - current_pitch
    threshold = 20
    
    if diff > threshold:
        return "↗"
    elif diff < -threshold:
        return "↘"
    else:
        return "→"


def normalize_pitch(pitches: List[float]) -> List[float]:
    """Normalize pitch values to 0-100 scale"""
    valid = [p for p in pitches if p > 0]
    if not valid:
        return [50] * len(pitches)
    
    min_p = min(valid)
    max_p = max(valid)
    range_p = max_p - min_p if max_p > min_p else 1
    
    normalized = []
    for p in pitches:
        if p > 0:
            normalized.append((p - min_p) / range_p * 100)
        else:
            normalized.append(50)
    
    return normalized


def compare_pitch_contours(ref_pitches: List[Dict], user_pitches: List[Dict]) -> Dict:
    """Compare pitch contours between reference and user"""
    if not ref_pitches or not user_pitches:
        return {'score': 0, 'details': [], 'feedback': 'No pitch data available'}
    
    ref_avg = [p['avg'] for p in ref_pitches]
    user_avg = [p['avg'] for p in user_pitches]
    
    ref_norm = normalize_pitch(ref_avg)
    user_norm = normalize_pitch(user_avg)
    
    details = []
    total_diff = 0
    valid_comparisons = 0
    
    min_len = min(len(ref_norm), len(user_norm))
    
    for i in range(min_len):
        ref_val = ref_norm[i]
        user_val = user_norm[i]
        
        diff = abs(ref_val - user_val)
        total_diff += diff
        valid_comparisons += 1
        
        if diff < 10:
            match = "correct"
            instruction = "✓"
        elif user_val < ref_val:
            match = "low"
            instruction = "↑"
        else:
            match = "high"
            instruction = "↓"
        
        ref_direction = "→"
        if i < min_len - 1:
            ref_direction = get_pitch_direction(ref_avg[i], ref_avg[i + 1])
        
        details.append({
            'syllable': i + 1,
            'ref_pitch': ref_avg[i],
            'user_pitch': user_avg[i],
            'diff': diff,
            'match': match,
            'instruction': instruction,
            'direction': ref_direction
        })
    
    avg_diff = total_diff / valid_comparisons if valid_comparisons > 0 else 100
    score = max(0, 100 - avg_diff)
    
    if score >= 85:
        feedback = "🎵 Excellent pitch matching! Your intonation closely follows the reference."
    elif score >= 70:
        feedback = "🎵 Good pitch control! Minor adjustments needed in some syllables."
    elif score >= 50:
        feedback = "🎵 Moderate match. Focus on the pitch arrows and try to follow the contour."
    else:
        feedback = "🎵 Keep practicing! Listen carefully to the reference pitch pattern."
    
    return {'score': score, 'details': details, 'feedback': feedback}


def get_syllable_character_mapping(original_text: str, lg_pattern: str, is_devanagari: bool) -> List[Dict]:
    """Map each syllable to its Devanagari character(s) and meter"""
    syllables = []
    
    if not is_devanagari:
        for i, lg in enumerate(lg_pattern):
            syllables.append({
                'char': '?',
                'lg': lg,
                'meter': '◡' if lg == 'L' else '–'
            })
        return syllables
    
    text = original_text.replace(' ', '')
    matras = set('ािीुूृॄेैोौंःँ॒॑')
    virama = '्'
    vowels = set('अआइईउऊऋॠऌॡएऐओऔ')
    
    i = 0
    syllable_idx = 0
    current_syllable = ""
    
    while i < len(text) and syllable_idx < len(lg_pattern):
        char = text[i]
        current_syllable += char
        
        is_vowel = char in vowels
        is_matra = char in matras
        is_consonant = '\u0915' <= char <= '\u0939' or char in 'ळक्षज्ञ'
        
        next_char = text[i + 1] if i + 1 < len(text) else None
        next_is_matra = next_char in matras if next_char else False
        next_is_virama = next_char == virama if next_char else False
        
        syllable_complete = False
        
        if is_vowel:
            syllable_complete = True
        elif is_matra:
            syllable_complete = True
        elif is_consonant and not next_is_matra and not next_is_virama:
            syllable_complete = True
        
        if syllable_complete and syllable_idx < len(lg_pattern):
            lg = lg_pattern[syllable_idx]
            syllables.append({
                'char': current_syllable,
                'lg': lg,
                'meter': '◡' if lg == 'L' else '–'
            })
            current_syllable = ""
            syllable_idx += 1
        
        i += 1
    
    while syllable_idx < len(lg_pattern):
        lg = lg_pattern[syllable_idx]
        syllables.append({
            'char': '?',
            'lg': lg,
            'meter': '◡' if lg == 'L' else '–'
        })
        syllable_idx += 1
    
    return syllables


def analyze_text(text: str) -> Dict:
    """Analyze Sanskrit text for meter"""
    if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text):
        transliterated = devanagari_to_transliteration(text)
        is_devanagari = True
        original_text = text
    else:
        transliterated = text
        is_devanagari = False
        original_text = text
    
    clean_trans = transliterated.replace('|', '').replace('।', '').replace('॥', '').replace('\n', ' ')
    clean_orig = original_text.replace('|', '').replace('।', '').replace('॥', '').replace('\n', ' ')
    
    prep = preprocessing(clean_trans)
    str_verse = prep.replace(' ', '')
    lg = laghu_guru(str_verse)
    lg_full = remove_vyanjana(lg)
    
    syllable_chars = get_syllable_character_mapping(clean_orig, lg_full, is_devanagari)
    
    padas = []
    syllables_per_pada = 8
    
    total_syllables = len(lg_full)
    num_padas = (total_syllables + syllables_per_pada - 1) // syllables_per_pada
    
    for i in range(num_padas):
        start_idx = i * syllables_per_pada
        end_idx = min((i + 1) * syllables_per_pada, total_syllables)
        
        pada_lg = lg_full[start_idx:end_idx]
        pada_chars = syllable_chars[start_idx:end_idx] if start_idx < len(syllable_chars) else []
        
        padas.append({
            'number': i + 1,
            'laghu_guru': pada_lg,
            'syllable_chars': pada_chars,
            'syllables': len(pada_lg)
        })
    
    return {'text': text, 'padas': padas, 'total_syllables': total_syllables}


def create_pitch_contour_chart(ref_pitches: List[Dict], user_pitches: List[Dict] = None):
    """Create pitch contour visualization using matplotlib"""
    if not HAS_MATPLOTLIB:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    ref_avg = [p['avg'] for p in ref_pitches if p['avg'] > 0]
    ref_x = range(1, len(ref_avg) + 1)
    
    if ref_avg:
        ax.plot(ref_x, ref_avg, 'o-', linewidth=2.5, markersize=8, label='Reference', color='#667eea')
        ax.fill_between(ref_x, ref_avg, alpha=0.2, color='#667eea')
    
    if user_pitches:
        user_avg = [p['avg'] for p in user_pitches if p['avg'] > 0]
        user_x = range(1, len(user_avg) + 1)
        if user_avg:
            ax.plot(user_x, user_avg, 's--', linewidth=2.5, markersize=8, label='Your Chant', color='#f5576c')
            ax.fill_between(user_x, user_avg, alpha=0.15, color='#f5576c')
    
    ax.set_xlabel('Syllable Number', fontsize=11, color='white')
    ax.set_ylabel('Pitch (Hz)', fontsize=11, color='white')
    ax.set_title('Pitch Contour Comparison', fontsize=13, fontweight='bold', color='white')
    ax.legend(facecolor='#1e1e2e', edgecolor='#444', labelcolor='white')
    ax.grid(True, alpha=0.3, color='#444')
    ax.set_facecolor('#1e1e2e')
    fig.patch.set_facecolor('#1e1e2e')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#444')
    
    return fig


def render_meter_visualization(analysis: Dict, pitch_data: List[Dict] = None):
    """Render meter and pitch visualization in Streamlit"""
    padas = analysis['padas']
    
    if not padas:
        st.warning("No text to analyze")
        return
    
    # Flatten syllables for pitch mapping
    all_syllables = []
    for pada in padas:
        all_syllables.extend(pada.get('syllable_chars', []))
    
    global_syl_idx = 0
    
    for pada in padas:
        pada_num = pada['number']
        syllable_chars = pada.get('syllable_chars', [])
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
             border-radius: 12px; padding: 20px; margin: 10px 0; border: 1px solid #333;">
            <div style="color: #ffd700; font-weight: bold; margin-bottom: 15px;">
                पाद {pada_num} — {pada['syllables']} syllables
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(syllable_chars), 8))
        
        for idx, syl in enumerate(syllable_chars):
            col_idx = idx % len(cols)
            
            pitch_arrow = ""
            if pitch_data and global_syl_idx < len(pitch_data):
                if global_syl_idx < len(pitch_data) - 1:
                    pitch_arrow = get_pitch_direction(
                        pitch_data[global_syl_idx]['avg'],
                        pitch_data[global_syl_idx + 1]['avg']
                    )
                else:
                    pitch_arrow = "●"
            
            meter_color = "#ff6b6b" if syl['lg'] == 'G' else "#00ff88"
            
            with cols[col_idx]:
                st.markdown(f"""
                <div style="text-align: center; background: rgba(255,255,255,0.05); 
                     border-radius: 8px; padding: 10px; margin: 3px 0;">
                    <div style="color: #00d4ff; font-size: 18px;">{pitch_arrow}</div>
                    <div style="color: {meter_color}; font-size: 20px; font-weight: bold;">{syl['meter']}</div>
                    <div style="color: white; font-size: 22px;">{syl['char']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            global_syl_idx += 1
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_comparison_scores(meter_score: float, pitch_score: float, combined_score: float):
    """Render score cards"""
    col1, col2, col3 = st.columns(3)
    
    def get_color(score):
        if score >= 85:
            return "#10b981"
        elif score >= 70:
            return "#667eea"
        elif score >= 50:
            return "#f59e0b"
        else:
            return "#ef4444"
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {get_color(meter_score)}, {get_color(meter_score)}88);
             border-radius: 12px; padding: 25px; text-align: center;">
            <div style="color: rgba(255,255,255,0.8); font-size: 12px;">METER</div>
            <div style="color: white; font-size: 36px; font-weight: bold;">{meter_score:.0f}%</div>
            <div style="color: rgba(255,255,255,0.9); font-size: 13px;">Laghu-Guru Pattern</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {get_color(pitch_score)}, {get_color(pitch_score)}88);
             border-radius: 12px; padding: 25px; text-align: center;">
            <div style="color: rgba(255,255,255,0.8); font-size: 12px;">PITCH</div>
            <div style="color: white; font-size: 36px; font-weight: bold;">{pitch_score:.0f}%</div>
            <div style="color: rgba(255,255,255,0.9); font-size: 13px;">Intonation Match</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {get_color(combined_score)}, {get_color(combined_score)}88);
             border-radius: 12px; padding: 25px; text-align: center;">
            <div style="color: rgba(255,255,255,0.8); font-size: 12px;">OVERALL</div>
            <div style="color: white; font-size: 36px; font-weight: bold;">{combined_score:.0f}%</div>
            <div style="color: rgba(255,255,255,0.9); font-size: 13px;">Combined Score</div>
        </div>
        """, unsafe_allow_html=True)


def compare_meters(ref_analysis: Dict, user_analysis: Dict) -> float:
    """Compare meter patterns and return score"""
    ref_padas = ref_analysis['padas']
    user_padas = user_analysis['padas']
    
    total_syllables = 0
    matching_syllables = 0
    
    max_padas = max(len(ref_padas), len(user_padas))
    
    for i in range(max_padas):
        ref = ref_padas[i] if i < len(ref_padas) else None
        user = user_padas[i] if i < len(user_padas) else None
        
        if ref and user:
            ref_lg = ref['laghu_guru']
            user_lg = user['laghu_guru']
            
            min_len = min(len(ref_lg), len(user_lg))
            max_len = max(len(ref_lg), len(user_lg))
            
            matches = sum(1 for j in range(min_len) if ref_lg[j] == user_lg[j])
            
            total_syllables += max_len
            matching_syllables += matches
    
    return (matching_syllables / total_syllables * 100) if total_syllables > 0 else 0


def render_advanced_chanting():
    """Main render function for advanced chanting analysis"""
    
    # Initialize session state
    if 'adv_reference_audio' not in st.session_state:
        st.session_state.adv_reference_audio = None
    if 'adv_reference_analysis' not in st.session_state:
        st.session_state.adv_reference_analysis = None
    if 'adv_reference_pitch' not in st.session_state:
        st.session_state.adv_reference_pitch = None
    if 'adv_user_analysis' not in st.session_state:
        st.session_state.adv_user_analysis = None
    if 'adv_user_pitch' not in st.session_state:
        st.session_state.adv_user_pitch = None
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent;
             font-size: 2.5rem; margin-bottom: 10px;">
            🎵 Advanced Chanting Analysis
        </h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Meter (Laghu-Guru) & Pitch Analysis for Sanskrit Shlokas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Main App", type="secondary"):
        st.session_state.app_mode = 'main'
        st.rerun()
    
    st.markdown("---")
    
    # Legend
    with st.expander("📚 Guide - Meter & Pitch Symbols", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Meter Symbols:**
            - ◡ (Laghu) = Short syllable
            - – (Guru) = Long syllable
            """)
        with col2:
            st.markdown("""
            **Pitch Arrows:**
            - ↗ = Pitch rising
            - ↘ = Pitch falling
            - → = Pitch steady
            """)
    
    # Two columns for Reference and User
    col_ref, col_user = st.columns(2)
    
    with col_ref:
        st.markdown("### 📖 Reference Audio")
        st.markdown("*Upload reference audio or use current shloka*")
        
        ref_source = st.radio(
            "Reference source:",
            ["Upload audio file", "Use current shloka"],
            key="ref_source",
            horizontal=True
        )
        
        ref_audio_bytes = None
        
        if ref_source == "Upload audio file":
            ref_file = st.file_uploader(
                "Upload reference audio",
                type=['wav', 'mp3', 'm4a', 'ogg'],
                key="ref_uploader"
            )
            if ref_file:
                ref_audio_bytes = ref_file.read()
                st.audio(ref_audio_bytes, format=f'audio/{ref_file.name.split(".")[-1]}')
        else:
            # Use current shloka from main app
            if st.session_state.get('current_shloka') and st.session_state.current_shloka.get('audio_data'):
                import base64
                ref_audio_bytes = base64.b64decode(st.session_state.current_shloka['audio_data'])
                audio_format = st.session_state.current_shloka.get('audio_format', 'mp3')
                st.audio(ref_audio_bytes, format=f'audio/{audio_format}')
                st.success("Using current shloka audio")
            else:
                st.warning("No shloka selected. Please select a shloka in the main app first.")
        
        if ref_audio_bytes and st.button("🔍 Analyze Reference", type="primary", key="analyze_ref"):
            with st.spinner("Transcribing and analyzing..."):
                # Transcribe
                transcript, success = transcribe_audio_for_chanting(ref_audio_bytes, 'sa')
                
                if success:
                    st.session_state.adv_reference_audio = ref_audio_bytes
                    st.session_state.adv_reference_analysis = analyze_text(transcript)
                    
                    # Extract pitch
                    total_syl = st.session_state.adv_reference_analysis.get('total_syllables', 0)
                    if total_syl > 0 and HAS_LIBROSA:
                        st.session_state.adv_reference_pitch = get_pitch_per_syllable(ref_audio_bytes, total_syl)
                    
                    st.success(f"✓ Transcribed: {transcript[:100]}...")
                else:
                    st.error(f"Transcription failed: {transcript}")
        
        # Show reference analysis
        if st.session_state.adv_reference_analysis:
            st.markdown("#### Reference Meter Pattern")
            render_meter_visualization(
                st.session_state.adv_reference_analysis,
                st.session_state.adv_reference_pitch
            )
    
    with col_user:
        st.markdown("### 🎤 Your Chanting")
        st.markdown("*Upload your recording or record live*")
        
        user_source = st.radio(
            "Your audio source:",
            ["Upload audio file", "Record live"],
            key="user_source",
            horizontal=True
        )
        
        user_audio_bytes = None
        
        if user_source == "Upload audio file":
            user_file = st.file_uploader(
                "Upload your chanting",
                type=['wav', 'mp3', 'm4a', 'ogg'],
                key="user_uploader"
            )
            if user_file:
                user_audio_bytes = user_file.read()
                st.audio(user_audio_bytes, format=f'audio/{user_file.name.split(".")[-1]}')
        else:
            user_recording = st.audio_input("Record your chanting", key="user_recorder")
            if user_recording:
                user_audio_bytes = user_recording.read()
                st.audio(user_audio_bytes, format='audio/wav')
        
        if user_audio_bytes and st.button("🔍 Analyze My Chanting", type="primary", key="analyze_user"):
            with st.spinner("Transcribing and analyzing..."):
                transcript, success = transcribe_audio_for_chanting(user_audio_bytes, 'sa')
                
                if success:
                    st.session_state.adv_user_analysis = analyze_text(transcript)
                    
                    total_syl = st.session_state.adv_user_analysis.get('total_syllables', 0)
                    if total_syl > 0 and HAS_LIBROSA:
                        st.session_state.adv_user_pitch = get_pitch_per_syllable(user_audio_bytes, total_syl)
                    
                    st.success(f"✓ Transcribed: {transcript[:100]}...")
                else:
                    st.error(f"Transcription failed: {transcript}")
        
        # Show user analysis
        if st.session_state.adv_user_analysis:
            st.markdown("#### Your Meter Pattern")
            render_meter_visualization(
                st.session_state.adv_user_analysis,
                st.session_state.adv_user_pitch
            )
    
    # Comparison section
    st.markdown("---")
    
    if st.session_state.adv_reference_analysis and st.session_state.adv_user_analysis:
        st.markdown("### ⚖️ Comparison Results")
        
        # Calculate scores
        meter_score = compare_meters(
            st.session_state.adv_reference_analysis,
            st.session_state.adv_user_analysis
        )
        
        pitch_score = 0
        pitch_comparison = None
        if st.session_state.adv_reference_pitch and st.session_state.adv_user_pitch:
            pitch_comparison = compare_pitch_contours(
                st.session_state.adv_reference_pitch,
                st.session_state.adv_user_pitch
            )
            pitch_score = pitch_comparison['score']
        
        combined_score = (meter_score * 0.6 + pitch_score * 0.4) if pitch_comparison else meter_score
        
        # Render scores
        render_comparison_scores(meter_score, pitch_score, combined_score)
        
        # Pitch contour chart
        if st.session_state.adv_reference_pitch and st.session_state.adv_user_pitch and HAS_MATPLOTLIB:
            st.markdown("#### 📊 Pitch Contour Comparison")
            fig = create_pitch_contour_chart(
                st.session_state.adv_reference_pitch,
                st.session_state.adv_user_pitch
            )
            if fig:
                st.pyplot(fig)
                plt.close(fig)
        
        # Pitch feedback
        if pitch_comparison:
            st.markdown(f"""
            <div style="background: rgba(102, 126, 234, 0.1); border-radius: 10px; 
                 padding: 15px; margin-top: 15px; border-left: 4px solid #667eea;">
                <p style="color: #e2e8f0; margin: 0;">{pitch_comparison['feedback']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Overall feedback
        if combined_score >= 85:
            feedback = "🏆 Outstanding! Your chanting demonstrates excellent control of both meter and pitch."
        elif combined_score >= 70:
            feedback = "⭐ Good progress! Focus on the highlighted areas to improve further."
        elif combined_score >= 50:
            feedback = "💪 Keep practicing! Pay attention to both the length (laghu/guru) and pitch patterns."
        else:
            feedback = "🎯 Listen to the reference again carefully, noting both rhythm and melody."
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%);
             border-radius: 12px; padding: 20px; margin-top: 20px; text-align: center;">
            <h4 style="color: #ffd700; margin-bottom: 10px;">💡 Overall Feedback</h4>
            <p style="color: #e2e8f0; font-size: 16px;">{feedback}</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif not st.session_state.adv_reference_analysis:
        st.info("👆 Please analyze a reference audio first")
    elif not st.session_state.adv_user_analysis:
        st.info("👆 Please analyze your chanting to see comparison")
