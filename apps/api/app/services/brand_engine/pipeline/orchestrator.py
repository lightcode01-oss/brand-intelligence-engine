import time
from typing import Optional, Tuple
from app.services.brand_engine.pipeline.stage_01_generate import Stage1Generate
from app.services.brand_engine.pipeline.stage_02_deduplicate import Stage2Deduplicate
from app.services.brand_engine.pipeline.stage_03_filter import Stage3Filter
from app.services.brand_engine.pipeline.stage_04_pronunciation import Stage4Pronunciation
from app.services.brand_engine.pipeline.stage_05_similarity import Stage5Similarity
from app.services.brand_engine.pipeline.stage_06_brand_score import Stage6BrandScore
from app.services.brand_engine.pipeline.stage_07_validation import Stage7Validation
from app.services.brand_engine.pipeline.stage_08_rank import Stage8Rank
from app.core.logging import logger

class BrandPipelineOrchestrator:
    """Orchestrates candidate names generation, phonetic filtering, BSI scoring, and ranking stages."""
    
    def __init__(self):
        self.stage1 = Stage1Generate()
        self.stage2 = Stage2Deduplicate()
        self.stage3 = Stage3Filter()
        self.stage4 = Stage4Pronunciation()
        self.stage5 = Stage5Similarity()
        self.stage6 = Stage6BrandScore()
        self.stage7 = Stage7Validation()
        self.stage8 = Stage8Rank()
        
    async def run_pipeline(
        self, industry: str, context: str, target_count: int = 20, 
        temperature: float = 0.7, style: str = "Compound"
    ) -> Tuple[list[dict], dict]:
        """Runs the complete 8-stage pipeline, tracking latency for observability."""
        stages_metrics = {}
        
        # Stage 1: Generate Raw Candidates
        s1_start = time.perf_counter()
        # Query slightly higher count (e.g. 5x target) to account for filter dropouts
        raw_candidates, meta = await self.stage1.execute(
            industry=industry,
            context=context,
            target_count=target_count * 5,
            temperature=temperature
        )
        stages_metrics["stage_01_generate_ms"] = int((time.perf_counter() - s1_start) * 1000)
        
        # Stage 2: Deduplicate
        s2_start = time.perf_counter()
        deduped = self.stage2.execute(raw_candidates)
        stages_metrics["stage_02_dedup_ms"] = int((time.perf_counter() - s2_start) * 1000)
        
        # Stage 3: Filter Banned Terms
        s3_start = time.perf_counter()
        filtered = self.stage3.execute(deduped)
        stages_metrics["stage_03_filter_ms"] = int((time.perf_counter() - s3_start) * 1000)
        
        # Stage 4: Pronunciation Checks
        s4_start = time.perf_counter()
        pronounced = self.stage4.execute(filtered)
        stages_metrics["stage_04_pron_ms"] = int((time.perf_counter() - s4_start) * 1000)
        
        # Stage 5: Metaphone Similarity Screen
        s5_start = time.perf_counter()
        unique = self.stage5.execute(pronounced)
        stages_metrics["stage_05_similarity_ms"] = int((time.perf_counter() - s5_start) * 1000)
        
        # Stage 6: BSI Scorecard Suggestion
        s6_start = time.perf_counter()
        scored = self.stage6.execute(unique, style)
        stages_metrics["stage_06_brand_score_ms"] = int((time.perf_counter() - s6_start) * 1000)
        
        # Stage 7: Active Check Valids (Mock placeholders)
        s7_start = time.perf_counter()
        validated = self.stage7.execute(scored)
        stages_metrics["stage_07_validation_ms"] = int((time.perf_counter() - s7_start) * 1000)
        
        # Stage 8: Scorecard Sorting
        s8_start = time.perf_counter()
        ranked = self.stage8.execute(validated)
        stages_metrics["stage_08_rank_ms"] = int((time.perf_counter() - s8_start) * 1000)
        
        # Log complete metrics trace
        logger.info(
            f"Brand names generation pipeline resolved successfully for '{context}'. Candidates: {len(ranked)}",
            extra={"metrics": stages_metrics}
        )
        
        # Slice to requested target count
        final_candidates = ranked[:target_count]
        
        # Combine meta and stage latencies
        meta["stages_latencies_ms"] = stages_metrics
        return final_candidates, meta
