"""
Database Manager - High-level API for database operations
Provides clean interface for application to interact with database
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from database.models import Speaker, Shloka, PracticeSession, WordPractice, get_session


class DatabaseManager:
    """Manager class for database operations"""
    
    def __init__(self, db_path=None):
        """Initialize database manager"""
        self.db_path = db_path
        self.session = get_session(db_path)
    
    def __del__(self):
        """Close session on cleanup"""
        if hasattr(self, 'session') and self.session:
            self.session.close()
    
    # ==================== SPEAKER OPERATIONS ====================
    
    def get_all_speakers(self) -> List[Speaker]:
        """Get all speakers sorted by speaker_id"""
        return self.session.query(Speaker).order_by(Speaker.speaker_id).all()
    
    def get_speaker_by_id(self, speaker_id: str) -> Optional[Speaker]:
        """Get speaker by speaker_id (e.g., 'sp001')"""
        return self.session.query(Speaker).filter_by(speaker_id=speaker_id).first()
    
    def get_speaker_list(self) -> List[str]:
        """Get list of speaker IDs for dropdown"""
        speakers = self.session.query(Speaker.speaker_id).order_by(Speaker.speaker_id).all()
        return [s.speaker_id for s in speakers]
    
    # ==================== SHLOKA OPERATIONS ====================
    
    def get_shlokas_for_speaker(self, speaker_id: str) -> List[Shloka]:
        """Get all shlokas for a specific speaker"""
        speaker = self.get_speaker_by_id(speaker_id)
        if not speaker:
            return []
        
        return self.session.query(Shloka)\
            .filter_by(speaker_id=speaker.id)\
            .order_by(Shloka.shloka_number)\
            .all()
    
    def get_shloka_by_number(self, speaker_id: str, shloka_number: int) -> Optional[Shloka]:
        """Get specific shloka by speaker and number"""
        speaker = self.get_speaker_by_id(speaker_id)
        if not speaker:
            return None
        
        return self.session.query(Shloka)\
            .filter_by(speaker_id=speaker.id, shloka_number=shloka_number)\
            .first()
    
    def get_shloka_count(self, speaker_id: str) -> int:
        """Get count of shlokas for a speaker"""
        speaker = self.get_speaker_by_id(speaker_id)
        if not speaker:
            return 0
        
        return self.session.query(Shloka).filter_by(speaker_id=speaker.id).count()
    
    def get_shloka_text(self, speaker_id: str, shloka_number: int) -> Tuple[str, str]:
        """
        Get shloka text in both formats
        
        Returns:
            Tuple of (devanagari_text, slp1_text)
        """
        shloka = self.get_shloka_by_number(speaker_id, shloka_number)
        if not shloka:
            return ("", "")
        
        return (shloka.devanagari_text, shloka.slp1_text)
    
    def get_shloka_audio_path(self, speaker_id: str, shloka_number: int) -> Optional[str]:
        """Get audio file path for a shloka"""
        shloka = self.get_shloka_by_number(speaker_id, shloka_number)
        if not shloka or not shloka.audio_data:
            return None
        
        return shloka.audio_data
    
    # ==================== PRACTICE SESSION OPERATIONS ====================
    
    def create_practice_session(
        self,
        speaker_id: str,
        shloka_number: int,
        user_audio_data: str,
        user_audio_format: str,
        transcribed_text: str = None,
        accuracy_score: float = None,
        pronunciation_score: float = None,
        llm_feedback: str = None,
        word_comparison: Dict = None,
        practice_mode: str = 'full'
    ) -> PracticeSession:
        """Create a new practice session record"""
        shloka = self.get_shloka_by_number(speaker_id, shloka_number)
        if not shloka:
            raise ValueError(f"Shloka not found: {speaker_id} #{shloka_number}")
        
        session = PracticeSession(
            shloka_id=shloka.id,
            user_audio_data=user_audio_data,
            user_audio_format=user_audio_format,
            transcribed_text=transcribed_text,
            accuracy_score=accuracy_score,
            pronunciation_score=pronunciation_score,
            llm_feedback=llm_feedback,
            word_comparison=json.dumps(word_comparison) if word_comparison else None,
            practice_mode=practice_mode
        )
        
        self.session.add(session)
        self.session.commit()
        
        return session
    
    def get_practice_history(self, speaker_id: str, shloka_number: int, limit: int = 10) -> List[PracticeSession]:
        """Get practice history for a specific shloka"""
        shloka = self.get_shloka_by_number(speaker_id, shloka_number)
        if not shloka:
            return []
        
        return self.session.query(PracticeSession)\
            .filter_by(shloka_id=shloka.id)\
            .order_by(PracticeSession.session_date.desc())\
            .limit(limit)\
            .all()
    
    def get_all_practice_sessions(self, speaker_id: str = None, limit: int = 50) -> List[PracticeSession]:
        """Get all practice sessions, optionally filtered by speaker"""
        query = self.session.query(PracticeSession)\
            .join(Shloka)\
            .join(Speaker)
        
        if speaker_id:
            query = query.filter(Speaker.speaker_id == speaker_id)
        
        return query.order_by(PracticeSession.session_date.desc()).limit(limit).all()
    
    def get_practice_stats(self, speaker_id: str = None) -> Dict:
        """Get practice statistics"""
        query = self.session.query(PracticeSession).join(Shloka).join(Speaker)
        
        if speaker_id:
            query = query.filter(Speaker.speaker_id == speaker_id)
        
        total_sessions = query.count()
        
        if total_sessions == 0:
            return {
                'total_sessions': 0,
                'average_accuracy': 0,
                'average_pronunciation': 0,
                'best_accuracy': 0,
                'best_pronunciation': 0
            }
        
        sessions = query.all()
        
        accuracies = [s.accuracy_score for s in sessions if s.accuracy_score is not None]
        pronunciations = [s.pronunciation_score for s in sessions if s.pronunciation_score is not None]
        
        return {
            'total_sessions': total_sessions,
            'average_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0,
            'average_pronunciation': sum(pronunciations) / len(pronunciations) if pronunciations else 0,
            'best_accuracy': max(accuracies) if accuracies else 0,
            'best_pronunciation': max(pronunciations) if pronunciations else 0
        }
    
    # ==================== WORD PRACTICE OPERATIONS ====================
    
    def update_word_practice(
        self,
        speaker_id: str,
        shloka_number: int,
        word_index: int,
        word_text: str,
        accuracy: float,
        pronunciation_score: float,
        is_correct: bool
    ) -> WordPractice:
        """Update or create word practice record"""
        shloka = self.get_shloka_by_number(speaker_id, shloka_number)
        if not shloka:
            raise ValueError(f"Shloka not found: {speaker_id} #{shloka_number}")
        
        # Find existing record or create new
        word_practice = self.session.query(WordPractice)\
            .filter_by(shloka_id=shloka.id, word_index=word_index)\
            .first()
        
        if not word_practice:
            word_practice = WordPractice(
                shloka_id=shloka.id,
                word_index=word_index,
                word_text=word_text,
                attempts=0,
                correct_attempts=0
            )
            self.session.add(word_practice)
        
        # Update statistics
        word_practice.attempts += 1
        if is_correct:
            word_practice.correct_attempts += 1
        
        word_practice.latest_accuracy = accuracy
        word_practice.latest_pronunciation_score = pronunciation_score
        word_practice.last_practiced = datetime.utcnow()
        
        # Mark as mastered if 3+ correct attempts with high accuracy
        if word_practice.correct_attempts >= 3 and accuracy >= 90:
            word_practice.mastered = True
        
        self.session.commit()
        
        return word_practice
    
    def get_word_practice_stats(self, speaker_id: str, shloka_number: int) -> List[WordPractice]:
        """Get word practice statistics for a shloka"""
        shloka = self.get_shloka_by_number(speaker_id, shloka_number)
        if not shloka:
            return []
        
        return self.session.query(WordPractice)\
            .filter_by(shloka_id=shloka.id)\
            .order_by(WordPractice.word_index)\
            .all()
    
    def get_difficult_words(self, speaker_id: str = None, limit: int = 10) -> List[WordPractice]:
        """Get words that need more practice (low accuracy, not mastered)"""
        query = self.session.query(WordPractice)\
            .filter(WordPractice.mastered == False)\
            .filter(WordPractice.attempts >= 2)
        
        if speaker_id:
            query = query.join(Shloka).join(Speaker)\
                .filter(Speaker.speaker_id == speaker_id)
        
        return query.order_by(WordPractice.latest_accuracy)\
            .limit(limit)\
            .all()
    
    # ==================== UTILITY OPERATIONS ====================
    
    def search_shlokas(self, search_text: str, limit: int = 20) -> List[Shloka]:
        """Search shlokas by text content"""
        return self.session.query(Shloka)\
            .filter(
                (Shloka.devanagari_text.contains(search_text)) |
                (Shloka.slp1_text.contains(search_text))
            )\
            .limit(limit)\
            .all()
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        return {
            'total_speakers': self.session.query(Speaker).count(),
            'total_shlokas': self.session.query(Shloka).count(),
            'total_practice_sessions': self.session.query(PracticeSession).count(),
            'total_word_practices': self.session.query(WordPractice).count(),
            'mastered_words': self.session.query(WordPractice).filter_by(mastered=True).count()
        }


# Singleton instance for easy access
_db_manager = None

def get_db_manager(db_path=None) -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager
