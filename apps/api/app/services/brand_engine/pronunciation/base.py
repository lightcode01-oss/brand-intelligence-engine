from abc import ABC, abstractmethod
from pydantic import BaseModel

class PronunciationMetrics(BaseModel):
    ipa_transcription: str
    syllable_count: int
    pronounceability_score: float # 0.0 to 100.0
    reading_difficulty: str      # 'EASY', 'MEDIUM', 'HARD'
    is_tongue_twister: bool
    international_notes: str

class AbstractPronunciationEngine(ABC):
    """Abstract interface defining name phonetics clearance metrics calculations."""
    
    @abstractmethod
    def analyze(self, word: str) -> PronunciationMetrics:
        """Computes IPA transcription, syllable counts, and difficulty rating."""
        pass
