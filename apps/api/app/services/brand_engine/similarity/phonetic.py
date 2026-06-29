from app.services.brand_engine.similarity.metaphone import metaphone_key
from app.services.brand_engine.similarity.jaro import jaro_winkler_similarity

def phonetic_similarity(s1: str, s2: str) -> float:
    """Calculates similarity based on the phonetic metaphone hashes of the two words."""
    key1 = metaphone_key(s1)
    key2 = metaphone_key(s2)
    
    if not key1 and not key2:
        return 1.0
    if not key1 or not key2:
        return 0.0
        
    # Run Jaro-Winkler on phonetic keys
    return jaro_winkler_similarity(key1, key2)
