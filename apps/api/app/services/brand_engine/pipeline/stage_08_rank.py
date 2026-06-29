from app.services.brand_engine.ranking import CandidateRanker

class Stage8Rank:
    """Stage 8: Sorts and ranks final candidate names according to overall BSI scorecards."""
    
    def __init__(self):
        self.ranker = CandidateRanker()
        
    def execute(self, candidates: list[dict]) -> list[dict]:
        return self.ranker.rank_candidates(candidates)
