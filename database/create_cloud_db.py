"""
Create a smaller database for Streamlit Cloud deployment
Keeps only first 100 shlokas from each speaker for fast deployment
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import Speaker, Shloka, init_database, get_session

# All 27 speakers, but only 100 shlokas each
SPEAKERS_TO_KEEP = [f'sp{i:03d}' for i in range(1, 28)]  # sp001 to sp027
MAX_SHLOKAS_PER_SPEAKER = 100  # Only first 100 shlokas per speaker (~120MB total)

def create_reduced_database():
    """Create smaller database with selected speakers"""
    print("Creating reduced database for Streamlit Cloud...")
    
    # Get source database (full version)
    source_db = 'database/sanskrit_voice_bot_full.db'
    if not Path(source_db).exists():
        print(f"Error: Source database not found at {source_db}")
        return
    
    source_session = get_session(source_db)
    
    # Create new database
    target_db = 'database/sanskrit_voice_bot_cloud.db'
    Path(target_db).unlink(missing_ok=True)
    init_database(target_db)
    target_session = get_session(target_db)
    
    total_shlokas = 0
    
    for speaker_id in SPEAKERS_TO_KEEP:
        print(f"\nCopying {speaker_id}...")
        
        # Get speaker from source
        source_speaker = source_session.query(Speaker).filter_by(speaker_id=speaker_id).first()
        if not source_speaker:
            print(f"  Speaker {speaker_id} not found!")
            continue
        
        # Create in target
        target_speaker = Speaker(
            speaker_id=source_speaker.speaker_id,
            name=source_speaker.name,
            description=source_speaker.description
        )
        target_session.add(target_speaker)
        target_session.flush()
        
        # Copy shlokas (limited to first MAX_SHLOKAS_PER_SPEAKER)
        shlokas = source_session.query(Shloka).filter_by(speaker_id=source_speaker.id).limit(MAX_SHLOKAS_PER_SPEAKER).all()
        for shloka in shlokas:
            new_shloka = Shloka(
                speaker_id=target_speaker.id,
                shloka_number=shloka.shloka_number,
                audio_filename=shloka.audio_filename,
                audio_data=shloka.audio_data,
                audio_format=shloka.audio_format,
                duration=shloka.duration,
                devanagari_text=shloka.devanagari_text,
                slp1_text=shloka.slp1_text
            )
            target_session.add(new_shloka)
        
        target_session.commit()
        print(f"  Copied {len(shlokas)} shlokas")
        total_shlokas += len(shlokas)
    
    source_session.close()
    target_session.close()
    
    print(f"\n✅ Created cloud database!")
    print(f"   Speakers: {len(SPEAKERS_TO_KEEP)}")
    print(f"   Shlokas: {total_shlokas}")
    print(f"   File: {target_db}")

if __name__ == '__main__':
    create_reduced_database()
