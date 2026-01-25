"""
Data migration script to load existing files into database
Migrates speakers, shlokas, transcripts, and audio files
"""
import sys
from pathlib import Path
import base64
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import Speaker, Shloka, init_database, get_session


class DataMigrator:
    """Handles migration of file-based data to database"""
    
    def __init__(self, data_dir, db_path=None):
        """
        Initialize the migrator
        
        Args:
            data_dir: Path to the data directory containing speaker folders
            db_path: Optional path to database file
        """
        self.data_dir = Path(data_dir)
        self.transcript_dir = self.data_dir / 'Transcript'
        self.db_path = db_path
        self.session = None
        
    def initialize_database(self):
        """Initialize database and create session"""
        print("Initializing database...")
        init_database(self.db_path)
        self.session = get_session(self.db_path)
        print("Database initialized successfully!")
        
    def get_speaker_folders(self):
        """Get list of speaker folders (sp001, sp002, etc.)"""
        speaker_folders = []
        for folder in self.data_dir.iterdir():
            if folder.is_dir() and folder.name.startswith('sp') and folder.name[2:].isdigit():
                speaker_folders.append(folder)
        return sorted(speaker_folders)
    
    def read_transcript(self, speaker_id, format_type='Devanagari'):
        """
        Read transcript file for a speaker
        
        Args:
            speaker_id: Speaker ID (e.g., 'sp001')
            format_type: 'Devanagari' or 'SLP1'
        
        Returns:
            List of lines from the transcript
        """
        transcript_file = self.transcript_dir / format_type / f'{speaker_id}.txt'
        if transcript_file.exists():
            with open(transcript_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                return lines
        return []
    
    def get_audio_files(self, speaker_folder):
        """Get all audio files for a speaker"""
        audio_extensions = ['.wav', '.mp3', '.m4a', '.ogg']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(speaker_folder.glob(f'*{ext}'))
        
        return sorted(audio_files)
    
    def encode_audio_file(self, audio_path):
        """
        Encode audio file as base64 string for database storage
        This ensures deployment works without file system dependencies
        """
        try:
            with open(audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                return audio_base64
        except Exception as e:
            print(f"  Warning: Failed to encode {audio_path.name}: {e}")
            return None
    
    def get_audio_duration(self, audio_path):
        """Get duration of audio file (placeholder - requires librosa or pydub)"""
        # TODO: Implement with librosa or pydub
        # For now, return None
        return None
    
    def migrate_speaker(self, speaker_folder):
        """Migrate a single speaker with all their shlokas"""
        speaker_id = speaker_folder.name
        print(f"\nMigrating speaker: {speaker_id}")
        
        # Create speaker entry
        speaker = Speaker(
            speaker_id=speaker_id,
            name=f"Speaker {speaker_id[2:]}",
            description=f"Sanskrit speaker {speaker_id}"
        )
        self.session.add(speaker)
        self.session.flush()  # Get the speaker.id
        
        # Read transcripts
        devanagari_lines = self.read_transcript(speaker_id, 'Devanagari')
        slp1_lines = self.read_transcript(speaker_id, 'SLP1')
        
        # Get audio files
        audio_files = self.get_audio_files(speaker_folder)
        
        # Create shloka entries
        num_shlokas = max(len(devanagari_lines), len(slp1_lines), len(audio_files))
        
        for i in range(num_shlokas):
            devanagari_text = devanagari_lines[i] if i < len(devanagari_lines) else ""
            slp1_text = slp1_lines[i] if i < len(slp1_lines) else ""
            
            # Find corresponding audio file
            audio_data = None
            audio_format = None
            audio_filename = None
            duration = None
            
            if i < len(audio_files):
                audio_path = audio_files[i]
                audio_data = self.encode_audio_file(audio_path)
                audio_format = audio_path.suffix[1:]  # Remove the dot
                audio_filename = audio_path.name
                duration = self.get_audio_duration(audio_path)
            
            shloka = Shloka(
                speaker_id=speaker.id,
                shloka_number=i + 1,
                audio_filename=audio_filename,
                audio_data=audio_data,
                audio_format=audio_format,
                duration=duration,
                devanagari_text=devanagari_text,
                slp1_text=slp1_text
            )
            self.session.add(shloka)
            
        print(f"  Created {num_shlokas} shlokas for {speaker_id}")
        
    def migrate_all(self):
        """Migrate all speakers and their data"""
        try:
            self.initialize_database()
            
            speaker_folders = self.get_speaker_folders()
            print(f"\nFound {len(speaker_folders)} speakers to migrate")
            
            for speaker_folder in speaker_folders:
                self.migrate_speaker(speaker_folder)
            
            # Commit all changes
            self.session.commit()
            print("\n✅ Migration completed successfully!")
            
            # Print summary
            total_speakers = self.session.query(Speaker).count()
            total_shlokas = self.session.query(Shloka).count()
            print(f"\nSummary:")
            print(f"  Speakers: {total_speakers}")
            print(f"  Shlokas: {total_shlokas}")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            if self.session:
                self.session.rollback()
            raise
        finally:
            if self.session:
                self.session.close()


def main():
    """Main migration function"""
    # Get data directory - fix path resolution
    data_dir = Path(__file__).parent.parent / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        return
    
    print("=" * 60)
    print("Sanskrit Voice Bot - Data Migration")
    print("=" * 60)
    print(f"Data directory: {data_dir}")
    
    # Create migrator and run migration
    migrator = DataMigrator(data_dir)
    migrator.migrate_all()
    
    print("\n" + "=" * 60)
    print("Migration complete! Database is ready to use.")
    print("=" * 60)


if __name__ == '__main__':
    main()
