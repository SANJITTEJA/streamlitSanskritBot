"""
Database verification script
Quick checks to ensure database is working correctly
"""
from database.db_manager import get_db_manager

def verify_database():
    """Run verification checks on the database"""
    print("=" * 60)
    print("Database Verification")
    print("=" * 60)
    
    db = get_db_manager()
    
    # 1. Check overall stats
    print("\n1. Overall Statistics:")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # 2. Check speakers
    print("\n2. Speaker Check:")
    speakers = db.get_speaker_list()
    print(f"   Found {len(speakers)} speakers")
    print(f"   First 5: {speakers[:5]}")
    print(f"   Last 5: {speakers[-5:]}")
    
    # 3. Check shlokas for first speaker
    print("\n3. Sample Shloka (sp001, #1):")
    shloka = db.get_shloka_by_number('sp001', 1)
    if shloka:
        print(f"   Devanagari: {shloka.devanagari_text[:80]}...")
        print(f"   SLP1: {shloka.slp1_text[:80]}...")
        print(f"   Audio: {shloka.audio_filename}")
        print(f"   Format: {shloka.audio_format}")
    
    # 4. Check shloka counts per speaker
    print("\n4. Shlokas per Speaker (first 5):")
    for speaker_id in speakers[:5]:
        count = db.get_shloka_count(speaker_id)
        print(f"   {speaker_id}: {count} shlokas")
    
    # 5. Test search functionality
    print("\n5. Search Test:")
    results = db.search_shlokas('पितरौ', limit=3)
    print(f"   Found {len(results)} shlokas containing 'पितरौ'")
    
    print("\n" + "=" * 60)
    print("✅ Database verification complete!")
    print("=" * 60)

if __name__ == '__main__':
    verify_database()
