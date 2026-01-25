"""
Database models for Sanskrit Voice Bot
Using SQLAlchemy ORM for database operations
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from pathlib import Path

Base = declarative_base()


class Speaker(Base):
    """Model for speakers in the dataset"""
    __tablename__ = 'speakers'
    
    id = Column(Integer, primary_key=True)
    speaker_id = Column(String(10), unique=True, nullable=False)  # e.g., 'sp001'
    name = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shlokas = relationship('Shloka', back_populates='speaker', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Speaker(speaker_id='{self.speaker_id}', name='{self.name}')>"


class Shloka(Base):
    """Model for shlokas with audio and transcripts"""
    __tablename__ = 'shlokas'
    
    id = Column(Integer, primary_key=True)
    speaker_id = Column(Integer, ForeignKey('speakers.id'), nullable=False)
    shloka_number = Column(Integer, nullable=False)  # Sequential number for this speaker
    audio_filename = Column(String(255))  # Original filename
    audio_data = Column(Text)  # Base64 encoded audio or file path
    audio_format = Column(String(10))  # mp3, wav, etc.
    duration = Column(Float)  # Duration in seconds
    
    # Transcripts
    devanagari_text = Column(Text, nullable=False)
    slp1_text = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    speaker = relationship('Speaker', back_populates='shlokas')
    practice_sessions = relationship('PracticeSession', back_populates='shloka', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Shloka(speaker='{self.speaker.speaker_id}', number={self.shloka_number})>"


class PracticeSession(Base):
    """Model for user practice sessions"""
    __tablename__ = 'practice_sessions'
    
    id = Column(Integer, primary_key=True)
    shloka_id = Column(Integer, ForeignKey('shlokas.id'), nullable=False)
    
    # User audio
    user_audio_data = Column(Text)  # Base64 encoded or file path
    user_audio_format = Column(String(10))
    
    # Analysis results
    transcribed_text = Column(Text)
    accuracy_score = Column(Float)
    pronunciation_score = Column(Float)
    
    # Detailed feedback
    llm_feedback = Column(Text)
    word_comparison = Column(Text)  # JSON string with word-by-word comparison
    
    # Metadata
    practice_mode = Column(String(20))  # 'full' or 'word'
    session_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shloka = relationship('Shloka', back_populates='practice_sessions')
    
    def __repr__(self):
        return f"<PracticeSession(id={self.id}, shloka_id={self.shloka_id}, date='{self.session_date}')>"


class WordPractice(Base):
    """Model for individual word practice tracking"""
    __tablename__ = 'word_practice'
    
    id = Column(Integer, primary_key=True)
    shloka_id = Column(Integer, ForeignKey('shlokas.id'), nullable=False)
    word_index = Column(Integer, nullable=False)  # Position in the shloka
    word_text = Column(String(100), nullable=False)
    
    # Practice statistics
    attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_practiced = Column(DateTime)
    mastered = Column(Boolean, default=False)
    
    # Latest scores
    latest_accuracy = Column(Float)
    latest_pronunciation_score = Column(Float)
    
    # Relationships
    shloka = relationship('Shloka')
    
    def __repr__(self):
        return f"<WordPractice(word='{self.word_text}', attempts={self.attempts}, mastered={self.mastered})>"


# Database initialization
def get_database_path():
    """Get the path to the SQLite database file - prioritize cloud database"""
    db_dir = Path(__file__).parent
    # Use cloud database for Streamlit Cloud deployment
    cloud_db = db_dir / 'sanskrit_voice_bot_cloud.db'
    if cloud_db.exists():
        return str(cloud_db)
    # Fallback to full database for local development
    full_db = db_dir / 'sanskrit_voice_bot_full.db'
    if full_db.exists():
        return str(full_db)
    # Default name if neither exists
    return str(db_dir / 'sanskrit_voice_bot.db')


def init_database(db_path=None):
    """Initialize the database and create all tables"""
    if db_path is None:
        db_path = get_database_path()
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(db_path=None):
    """Get a database session"""
    if db_path is None:
        db_path = get_database_path()
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    # Create database and tables
    print("Initializing database...")
    engine = init_database()
    print(f"Database created at: {get_database_path()}")
    print("Tables created successfully!")
