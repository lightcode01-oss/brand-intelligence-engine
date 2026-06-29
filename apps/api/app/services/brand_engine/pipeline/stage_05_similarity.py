from app.services.brand_engine.similarity.engine import SimilarityEngine

class Stage5Similarity:
    """Stage 5: Performs metaphone similarity checks against a dictionary of top trademark brands."""
    
    def __init__(self):
        self.engine = SimilarityEngine()
        self.reference_brands = ["apple", "google", "amazon", "microsoft", "meta", "netflix"]
        
    def execute(self, candidates: list[dict], threshold: float = 0.8) -> list[dict]:
        passed = []
        for item in candidates:
            name = item["name"]
            
            # Check collisions with top reference brands
            clash = self.engine.is_too_similar(name, self.reference_brands, threshold)
            if clash:
                continue
                
            # Compute uniqueness score (1.0 minus highest reference similarity)
            max_sim = 0.0
            for ref in self.reference_brands:
                sim = self.engine.compute_similarity(name, ref)["phonetic"]
                if sim > max_sim:
                    max_sim = sim
            item["uniqueness_ratio"] = 1.0 - max_sim
            passed.append(item)
            
        return passed
