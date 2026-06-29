from app.services.brand_engine.scoring import Scorecard

class CandidateRanker:
    """Sorts generated names based on their calculated scorecard weights."""
    
    def rank_candidates(self, candidates_list: list[dict]) -> list[dict]:
        """Sorts candidates list descending by bsi_overall and then by pronounceability."""
        def sorting_key(item: dict) -> tuple[float, float]:
            scorecard: Scorecard = item.get("scorecard")
            if scorecard:
                return (scorecard.bsi_overall, scorecard.pronunciation_score)
            return (0.0, 0.0)
            
        return sorted(candidates_list, key=sorting_key, reverse=True)
