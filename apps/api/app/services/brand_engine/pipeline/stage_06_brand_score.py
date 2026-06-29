from app.services.brand_engine.scoring import BrandScoreEngine
from app.services.brand_engine.logo_rec import LogoRecommendationEngine

class Stage6BrandScore:
    """Stage 6: Generates logo recommendations and calculates the overall Brand Score Index (BSI)."""
    
    def __init__(self):
        self.score_engine = BrandScoreEngine()
        self.logo_engine = LogoRecommendationEngine()
        
    def execute(self, candidates: list[dict], style: str) -> list[dict]:
        scored = []
        for item in candidates:
            name = item["name"]
            
            # Default mock domain/trademark checks on this stage (updated later on validation)
            domain_ok = True
            trademark_ok = True
            social_ok = True
            
            # 1. Calculate Scorecard
            card = self.score_engine.calculate_scorecard(
                name=name,
                pronunciation_ease=item["pronunciation"].pronounceability_score,
                uniqueness_ratio=item.get("uniqueness_ratio", 0.7),
                domain_ok=domain_ok,
                trademark_ok=trademark_ok,
                social_ok=social_ok
            )
            
            # 2. Logo suggestions
            logo = self.logo_engine.generate_recommendation(name, style)
            
            item["scorecard"] = card
            item["logo_recommendation"] = logo
            scored.append(item)
            
        return scored
