import uuid
from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Project
from app.models.brand import GeneratedName

class RecommendationEngine:
    """Enterprise AI Naming Recommendation Engine offering typography, colors, slogan alternatives, and prompt suggestions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_recommendations(self, project_id: uuid.UUID) -> Dict[str, Any]:
        """Provides AI-driven naming prompt optimizations, brand colors, slogans, and typography choices."""
        # 1. Fetch project prompt
        stmt = select(Project).where(Project.id == project_id)
        project = (await self.db.execute(stmt)).scalar()
        if not project:
            return {
                "stronger_prompts": ["Generate high-performance secure ledger concepts"],
                "better_industries": ["Technology", "Fintech"],
                "logo_colors": ["indigo", "emerald"],
                "typography": ["Inter", "Outfit"],
                "slogan_suggestions": ["Nomen: Infinite Naming Speed"],
                "domain_alternatives": ["getnomen.io", "nomenhq.com"],
                "similar_successful_brands": ["Stripe", "Figma"]
            }

        prompt = project.prompt.lower()
        
        # 2. Dynamic recommendations logic
        better_prompts = [
            f"optimised alternative: {project.prompt} - short 5-7 letter abstract name variations",
            f"premium suffix mapping: {project.prompt} with clean .io or .com suffix formats",
            f"metaphorical naming styles: {project.prompt} based on mythology or natural forces"
        ]

        colors = ["#4F46E5 (Indigo)", "#10B981 (Emerald)"]
        fonts = ["Outfit", "Inter"]
        slogans = [
            f"Nomen: Empowering {project.prompt} discoveries",
            f"The ultimate naming workspace for {project.prompt}"
        ]
        
        # Standard alternatives list
        domains = ["getbrand.io", "brandhq.com", "trybrand.ai"]
        successful_brands = ["Vercel", "Linear", "Retool"]
        industries = ["SaaS", "Fintech", "Developer Tools"]

        # Customize recommendations based on keywords
        if "crypto" in prompt or "web3" in prompt or "ledger" in prompt:
            colors = ["#F59E0B (Amber Gold)", "#6366F1 (Indigo)"]
            fonts = ["JetBrains Mono", "Space Grotesk"]
            domains = ["cryptobrand.io", "ledgerhq.xyz", "web3concept.co"]
            successful_brands = ["Ethereum", "Solana", "Coinbase"]
            industries = ["Blockchain", "Web3", "Finance"]
        elif "health" in prompt or "bio" in prompt or "clinic" in prompt:
            colors = ["#06B6D4 (Cyan)", "#10B981 (Emerald)"]
            fonts = ["Plus Jakarta Sans", "Roboto"]
            domains = ["healthcarebrand.org", "biobrand.io", "healhq.com"]
            successful_brands = ["Moderna", "Oscar Health", "CVS"]
            industries = ["Biotech", "Healthcare", "Wellness"]

        return {
            "stronger_prompts": better_prompts,
            "better_industries": industries,
            "logo_colors": colors,
            "typography": fonts,
            "slogan_suggestions": slogans,
            "domain_alternatives": domains,
            "similar_successful_brands": successful_brands
        }
