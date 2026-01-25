"""
Create a smaller database for Streamlit Cloud deployment
Keeps only top 5 speakers to stay under 1GB limit
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import Speaker, Shloka, init_database, get_session

# Speakers to keep (based on previous migration stats):
# sp001: 11,625 shlokas (548MB) - KEEP
# sp003: 6,661 shlokas (263MB) - KEEP
# Total: ~18,286 shlokas (~811MB)

SPEAKERS_TO_KEEP = ['sp001', 'sp003']

def create_reduced_database():
    """Create smaller database with selected speakers"""
    print("Creating reduced database for Streamlit Cloud...")
    
    # Get source database
    source_session = get_session('database/sanskrit_voice_bot.db')
    
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
        
        # Copy shlokas
        shlokas = source_session.query(Shloka).filter_by(speaker_id=source_speaker.id).all()
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
