from app.services.brand_engine.pronunciation.rule_engine import RulePronunciationEngine

class Stage4Pronunciation:
    """Stage 4: Calculates IPA transcriptions and removes candidates tagged with high pronunciation difficulty."""
    
    def __init__(self):
        self.engine = RulePronunciationEngine()
        
    def execute(self, candidates: list[str], max_syllables: int = 4) -> list[dict]:
        passed = []
        for name in candidates:
            metrics = self.engine.analyze(name)
            
            # Filter out hard names
            if metrics.reading_difficulty == "HARD" or metrics.syllable_count > max_syllables:
                continue
                
            passed.append({
                "name": name,
                "pronunciation": metrics
            })
        return passed
