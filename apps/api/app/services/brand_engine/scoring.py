import os
from pydantic import BaseModel, Field
from typing import Optional

class BrandScoreWeights(BaseModel):
    memorability: float = 0.15
    pronunciation: float = 0.15
    length: float = 0.10
    visual_balance: float = 0.05
    uniqueness: float = 0.10
    international_safety: float = 0.05
    domain: float = 0.15
    trademark: float = 0.15
    social: float = 0.05
    typing_ease: float = 0.02
    voice_assistant: float = 0.03

class Scorecard(BaseModel):
    bsi_overall: int
    memorability_score: float
    pronunciation_score: float
    length_score: float
    visual_balance_score: float
    uniqueness_score: float
    international_safety_score: float
    domain_score: float
    trademark_score: float
    social_score: float
    typing_ease_score: float
    voice_assistant_score: float

class BrandScoreEngine:
    """Computes the overall Brand Score Index (BSI) using customizable parameter weights."""
    
    def __init__(self, weights: Optional[BrandScoreWeights] = None):
        self.weights = weights or self._load_default_weights()
        
    def _load_default_weights(self) -> BrandScoreWeights:
        """Loads weights dynamically from environment properties, preventing hardcoding."""
        return BrandScoreWeights(
            memorability=float(os.getenv("BSI_WEIGHT_MEMORABILITY", "0.15")),
            pronunciation=float(os.getenv("BSI_WEIGHT_PRONUNCIATION", "0.15")),
            length=float(os.getenv("BSI_WEIGHT_LENGTH", "0.10")),
            visual_balance=float(os.getenv("BSI_WEIGHT_VISUAL", "0.05")),
            uniqueness=float(os.getenv("BSI_WEIGHT_UNIQUENESS", "0.10")),
            international_safety=float(os.getenv("BSI_WEIGHT_INT_SAFETY", "0.05")),
            domain=float(os.getenv("BSI_WEIGHT_DOMAIN", "0.15")),
            trademark=float(os.getenv("BSI_WEIGHT_TRADEMARK", "0.15")),
            social=float(os.getenv("BSI_WEIGHT_SOCIAL", "0.05")),
            typing_ease=float(os.getenv("BSI_WEIGHT_TYPING", "0.02")),
            voice_assistant=float(os.getenv("BSI_WEIGHT_VOICE", "0.03"))
        )

    def calculate_scorecard(
        self, name: str, pronunciation_ease: float, uniqueness_ratio: float, 
        domain_ok: bool, trademark_ok: bool, social_ok: bool
    ) -> Scorecard:
        """Runs weighted attribute algorithms to compile a complete score card."""
        # 1. Base attribute calculations
        length_score = max(10.0, 100.0 - (len(name) - 5) * 8)
        pron_score = pronunciation_ease
        uniq_score = uniqueness_ratio * 100.0
        
        # Binary status conversions
        dom_score = 100.0 if domain_ok else 20.0
        tm_score = 100.0 if trademark_ok else 10.0
        soc_score = 100.0 if social_ok else 30.0
        
        # Simplistic rules checks for additional attributes
        mem_score = max(20.0, (length_score + pron_score) / 2)
        visual_score = 100.0 - (len(name) % 3) * 10
        int_safety = 100.0 if not any(c in "xyzj" for c in name.lower()) else 70.0
        typing_ease = 100.0 - (len(name) * 4)
        voice_score = pron_score
        
        # 2. Compute overall weighted index sum
        w = self.weights
        total_weight = (
            w.memorability + w.pronunciation + w.length + w.visual_balance + 
            w.uniqueness + w.international_safety + w.domain + w.trademark + 
            w.social + w.typing_ease + w.voice_assistant
        )
        
        weighted_sum = (
            (mem_score * w.memorability) + (pron_score * w.pronunciation) +
            (length_score * w.length) + (visual_score * w.visual_balance) +
            (uniq_score * w.uniqueness) + (int_safety * w.international_safety) +
            (dom_score * w.domain) + (tm_score * w.trademark) +
            (soc_score * w.social) + (typing_ease * w.typing_ease) +
            (voice_score * w.voice_assistant)
        )
        
        bsi_overall = int(round(weighted_sum / total_weight))
        
        return Scorecard(
            bsi_overall=min(100, max(10, bsi_overall)),
            memorability_score=mem_score,
            pronunciation_score=pron_score,
            length_score=length_score,
            visual_balance_score=visual_score,
            uniqueness_score=uniq_score,
            international_safety_score=int_safety,
            domain_score=dom_score,
            trademark_score=tm_score,
            social_score=soc_score,
            typing_ease_score=typing_ease,
            voice_assistant_score=voice_score
        )
