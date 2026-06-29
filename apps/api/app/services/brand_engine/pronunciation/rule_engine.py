import re
from app.services.brand_engine.pronunciation.base import AbstractPronunciationEngine, PronunciationMetrics

class RulePronunciationEngine(AbstractPronunciationEngine):
    """Pure-Python rules-based phonetic engine measuring syllable count and pronunciation complexity."""
    
    def count_syllables(self, word: str) -> int:
        """Counts syllable groupings using a standard English vowel ruleset."""
        w = word.strip().lower()
        if not w:
            return 0
            
        # Remove silent trailing 'e'
        if w.endswith("e"):
            # Keep if ending in 'le' (e.g. 'candle')
            if not w.endswith("le"):
                w = w[:-1]
                
        # Count vowel groupings
        vowels = "aeiouy"
        count = 0
        in_vowel_group = False
        
        for char in w:
            if char in vowels:
                if not in_vowel_group:
                    count += 1
                    in_vowel_group = True
            else:
                in_vowel_group = False
                
        return max(1, count)

    def generate_ipa(self, word: str) -> str:
        """Generates standard IPA phoneme transcription from grapheme characters using rule matches."""
        w = word.strip().lower()
        
        # Dictionary mappings for common sounds
        replacements = [
            ("ch", "tʃ"), ("sh", "ʃ"), ("th", "θ"), ("ph", "f"),
            ("ea", "i:"), ("ee", "i:"), ("oo", "u:"), ("ai", "eɪ"),
            ("c", "k"), ("ck", "k"), ("x", "ks"), ("q", "kw")
        ]
        
        for grapheme, phoneme in replacements:
            w = w.replace(grapheme, phoneme)
            
        # Basic vowels cleanup
        vowels_map = {"a": "æ", "e": "e", "i": "aɪ", "o": "ɒ", "u": "ʌ", "y": "aɪ"}
        for k, v in vowels_map.items():
            w = w.replace(k, v)
            
        return f"/{w}/"

    def analyze(self, word: str) -> PronunciationMetrics:
        w = word.strip().lower()
        syllables = self.count_syllables(w)
        ipa = self.generate_ipa(w)
        
        # 1. Calculate pronounceability score (0.0 to 100.0)
        # Penalize excessive length and dense consonant clusters
        len_penalty = max(0, (len(w) - 6) * 5)
        
        # Regex matching 3 or more consecutive consonants (e.g., 'str', 'sch')
        clusters = len(re.findall(r"[bcdfghjklmnpqrstvwxz]{3,}", w))
        cluster_penalty = clusters * 20
        
        score = max(10.0, 100.0 - len_penalty - cluster_penalty)
        
        # 2. Determine reading difficulty
        has_vowels = any(c in "aeiouy" for c in w)
        consonant_clusters = re.findall(r"[bcdfghjklmnpqrstvwxz]+", w)
        max_cluster_len = max([len(c) for c in consonant_clusters]) if consonant_clusters else 0

        if not has_vowels or max_cluster_len >= 4:
            difficulty = "HARD"
            score = min(score, 30.0)
        elif score > 80.0:
            difficulty = "EASY"
        elif score > 50.0:
            difficulty = "MEDIUM"
        else:
            difficulty = "HARD"
            
        # 3. Detect tongue twisters (high count of repeating consonant sounds)
        consonants = re.findall(r"[bcdfghjklmnpqrstvwxz]", w)
        is_twister = False
        if len(consonants) >= 4:
            # Check if alternating or repeating
            unique_ratio = len(set(consonants)) / len(consonants)
            if unique_ratio < 0.4:
                is_twister = True
                
        return PronunciationMetrics(
            ipa_transcription=ipa,
            syllable_count=syllables,
            pronounceability_score=score,
            reading_difficulty=difficulty,
            is_tongue_twister=is_twister,
            international_notes="IPA transcription generated using local ruleset."
        )
