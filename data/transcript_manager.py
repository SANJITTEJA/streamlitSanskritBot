"""
Transcript Manager Module for Sanskrit Voice Bot v2
Handles loading, parsing, and accessing transcript data for Sanskrit texts.
"""
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.config import AppConfig


class TranscriptManager:
    """
    Manages transcript data for Sanskrit texts in both Devanagari and SLP1 formats.
    
    This class provides:
    - Loading transcript files for all speakers
    - Accessing shloka data by speaker and audio ID
    - Previewing shloka content
    - Managing transcript statistics
    """
    
    def __init__(self):
        """Initialize the TranscriptManager"""
        self._transcripts = {}
    
    def load_all_transcripts(self):
        """Load all transcript files for all available speakers"""
        if not AppConfig.TRANSCRIPT_PATH.exists():
            print("Error: Transcript directory not found!")
            return
        
        print("Loading transcripts...")
        
        # Load transcripts for all speakers
        for i in range(AppConfig.MIN_SPEAKER, AppConfig.MAX_SPEAKER + 1):
            speaker_id = AppConfig.get_speaker_id(i)
            
            devanagari_file = AppConfig.DEVANAGARI_PATH / f"{speaker_id}.txt"
            slp1_file = AppConfig.SLP1_PATH / f"{speaker_id}.txt"
            
            if devanagari_file.exists() and slp1_file.exists():
                devanagari_content = self._read_file(devanagari_file)
                slp1_content = self._read_file(slp1_file)
                
                self._transcripts[speaker_id] = {
                    'devanagari': self._parse_transcript_content(devanagari_content),
                    'slp1': self._parse_transcript_content(slp1_content)
                }
                
                print(f"Loaded transcripts for {speaker_id}: {len(self._transcripts[speaker_id]['devanagari'])} entries")
            else:
                print(f"Missing transcript files for {speaker_id}")
        
        print(f"Successfully loaded transcripts for {len(self._transcripts)} speakers")
    
    def _read_file(self, file_path: Path) -> str:
        """Read file content with proper encoding"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_transcript_content(self, content: str) -> Dict[str, str]:
        """Parse transcript file content into dictionary"""
        result = {}
        lines = content.strip().split('\n')
        
        for line in lines:
            if '\t' in line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    audio_id, text = parts
                    result[audio_id.strip()] = text.strip()
        
        return result
    
    def has_data(self) -> bool:
        """Check if transcript data is loaded"""
        return len(self._transcripts) > 0
    
    def get_available_speakers(self) -> List[str]:
        """Get list of available speaker IDs"""
        return list(self._transcripts.keys())
    
    def get_speaker_transcripts(self, speaker_id: str) -> Dict[str, Dict[str, str]]:
        """Get all transcripts for a specific speaker"""
        return self._transcripts.get(speaker_id, {'devanagari': {}, 'slp1': {}})
    
    def get_audio_ids(self, speaker_id: str, limit: Optional[int] = None) -> List[str]:
        """
        Get list of available audio IDs for a speaker.
        
        Args:
            speaker_id: The speaker identifier
            limit: Optional limit on number of results
            
        Returns:
            List of audio IDs
        """
        speaker_transcripts = self.get_speaker_transcripts(speaker_id)
        audio_ids = list(speaker_transcripts['devanagari'].keys())
        
        if limit:
            audio_ids = audio_ids[:limit]
        
        return audio_ids
    
    def get_shloka_text(self, speaker_id: str, audio_id: str, format_type: str = 'devanagari') -> str:
        """
        Get shloka text in specified format.
        
        Args:
            speaker_id: The speaker identifier
            audio_id: The audio file identifier
            format_type: 'devanagari' or 'slp1'
            
        Returns:
            The shloka text in requested format
        """
        speaker_transcripts = self.get_speaker_transcripts(speaker_id)
        return speaker_transcripts.get(format_type, {}).get(audio_id, '')
    
    def get_shloka_data(self, speaker_id: str, audio_id: str) -> Optional[Dict[str, str]]:
        """
        Get complete shloka data including both formats.
        
        Args:
            speaker_id: The speaker identifier
            audio_id: The audio file identifier
            
        Returns:
            Dictionary containing shloka data in both formats, or None if not found
        """
        devanagari_text = self.get_shloka_text(speaker_id, audio_id, 'devanagari')
        slp1_text = self.get_shloka_text(speaker_id, audio_id, 'slp1')
        
        if not devanagari_text or not slp1_text:
            return None
        
        return {
            'audio_id': audio_id,
            'speaker_id': speaker_id,
            'devanagari': devanagari_text,
            'slp1': slp1_text
        }
    
    def get_shloka_preview(self, speaker_id: str, audio_id: str, max_length: int = 50) -> str:
        """
        Get a preview of the shloka text for display purposes.
        
        Args:
            speaker_id: The speaker identifier
            audio_id: The audio file identifier
            max_length: Maximum length of preview text
            
        Returns:
            Preview text (truncated if necessary)
        """
        devanagari_text = self.get_shloka_text(speaker_id, audio_id, 'devanagari')
        if not devanagari_text:
            return ""
        
        if len(devanagari_text) > max_length:
            return devanagari_text[:max_length] + "..."
        
        return devanagari_text
    
    def is_valid_selection(self, speaker_id: str, audio_id: str) -> bool:
        """
        Check if speaker and audio ID combination is valid.
        
        Args:
            speaker_id: The speaker identifier
            audio_id: The audio file identifier
            
        Returns:
            bool: True if combination is valid, False otherwise
        """
        return (speaker_id in self._transcripts and 
                audio_id in self._transcripts[speaker_id]['devanagari'] and
                audio_id in self._transcripts[speaker_id]['slp1'])
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about loaded transcripts.
        
        Returns:
            Dictionary containing transcript statistics
        """
        stats = {
            'total_speakers': len(self._transcripts),
            'total_audio_files': 0,
            'speakers_with_data': []
        }
        
        for speaker_id, data in self._transcripts.items():
            audio_count = len(data['devanagari'])
            stats['total_audio_files'] += audio_count
            stats['speakers_with_data'].append({
                'speaker_id': speaker_id,
                'audio_count': audio_count
            })
        
        return stats