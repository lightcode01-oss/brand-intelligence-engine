from app.services.brand_engine.similarity.levenshtein import levenshtein_similarity
from app.services.brand_engine.similarity.jaro import jaro_winkler_similarity
from app.services.brand_engine.similarity.phonetic import phonetic_similarity
from app.services.brand_engine.similarity.semantic_placeholder import semantic_similarity

class SimilarityEngine:
    """Consolidates text, phonetic, and semantic string comparison algorithms."""
    
    def compute_similarity(self, s1: str, s2: str) -> dict[str, float]:
        """Runs edit distance, Jaro-Winkler, metaphone, and semantic matches."""
        return {
            "levenshtein": levenshtein_similarity(s1, s2),
            "jaro_winkler": jaro_winkler_similarity(s1, s2),
            "phonetic": phonetic_similarity(s1, s2),
            "semantic": semantic_similarity(s1, s2)
        }
        
    def is_too_similar(self, candidate: str, reference_list: list[str], threshold: float = 0.8) -> bool:
        """Verifies if a candidate name clashes phonetically or textually with existing entries."""
        for ref in reference_list:
            scores = self.compute_similarity(candidate, ref)
            # Flag if phonetic or jaro-winkler exceeds threshold
            if scores["phonetic"] >= threshold or scores["jaro_winkler"] >= threshold:
                return True
        return False
