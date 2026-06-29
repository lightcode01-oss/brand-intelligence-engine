import pytest
from app.services.brand_engine.pipeline.stage_01_generate import Stage1Generate
from app.services.brand_engine.pipeline.stage_02_deduplicate import Stage2Deduplicate
from app.services.brand_engine.pipeline.stage_03_filter import Stage3Filter
from app.services.brand_engine.pipeline.stage_04_pronunciation import Stage4Pronunciation
from app.services.brand_engine.pipeline.stage_05_similarity import Stage5Similarity
from app.services.brand_engine.pipeline.stage_06_brand_score import Stage6BrandScore
from app.services.brand_engine.pipeline.stage_07_validation import Stage7Validation
from app.services.brand_engine.pipeline.stage_08_rank import Stage8Rank
from app.services.brand_engine.pipeline.orchestrator import BrandPipelineOrchestrator
from app.services.brand_engine.scoring import BrandScoreEngine, BrandScoreWeights
from app.services.brand_engine.similarity.jaro import jaro_winkler_similarity
from app.services.brand_engine.similarity.levenshtein import levenshtein_similarity
from app.services.brand_engine.similarity.metaphone import metaphone_key
from app.services.brand_engine.pronunciation.rule_engine import RulePronunciationEngine

@pytest.mark.asyncio
async def test_stage_01_generate() -> None:
    stage = Stage1Generate()
    names, meta = await stage.execute(industry="tech", context="AI software", target_count=5)
    assert len(names) > 0
    assert meta["provider"] in ["gemini", "openai", "claude", "ollama"]
    assert "prompt_version" in meta

def test_stage_02_deduplicate() -> None:
    stage = Stage2Deduplicate()
    raw = ["Alpha", "Beta", "alpha ", "Beta", "Gamma"]
    deduped = stage.execute(raw)
    assert len(deduped) == 3
    assert deduped == ["Alpha", "Beta", "Gamma"]

def test_stage_03_filter() -> None:
    stage = Stage3Filter(banned_words=["spam"])
    raw = ["GoodName", "spammy", "A", "VeryVeryLongCompanyNameThatIsInvalid"]
    filtered = stage.execute(raw)
    assert len(filtered) == 1
    assert filtered == ["GoodName"]

def test_stage_04_pronunciation() -> None:
    stage = Stage4Pronunciation()
    raw = ["Alpha", "Strsch"] # 'Strsch' is hard
    passed = stage.execute(raw)
    assert len(passed) == 1
    assert passed[0]["name"] == "Alpha"
    assert passed[0]["pronunciation"].syllable_count == 2

def test_stage_05_similarity() -> None:
    stage = Stage5Similarity()
    stage.reference_brands = ["apple"]
    # 'aple' is too similar to 'apple'
    candidates = [{"name": "Aple"}, {"name": "Zeta"}]
    passed = stage.execute(candidates, threshold=0.8)
    assert len(passed) == 1
    assert passed[0]["name"] == "Zeta"

def test_stage_06_brand_score() -> None:
    stage = Stage6BrandScore()
    # Mock passed metrics
    pe = RulePronunciationEngine()
    candidates = [{
        "name": "Nova",
        "pronunciation": pe.analyze("Nova"),
        "uniqueness_ratio": 0.9
    }]
    scored = stage.execute(candidates, style="Tech")
    assert len(scored) == 1
    assert "scorecard" in scored[0]
    assert scored[0]["scorecard"].bsi_overall > 50

def test_stage_07_validation() -> None:
    stage = Stage7Validation()
    pe = RulePronunciationEngine()
    engine = BrandScoreEngine()
    card = engine.calculate_scorecard("Nova", 90.0, 0.9, True, True, True)
    
    candidates = [{
        "name": "Nova",
        "scorecard": card
    }]
    validated = stage.execute(candidates)
    assert len(validated) == 1
    # Check domain validation updates overall index
    assert validated[0]["scorecard"].domain_score in [100.0, 20.0]

def test_stage_08_rank() -> None:
    stage = Stage8Rank()
    pe = RulePronunciationEngine()
    engine = BrandScoreEngine()
    
    card1 = engine.calculate_scorecard("LowBSI", 40.0, 0.2, False, False, False)
    card2 = engine.calculate_scorecard("HighBSI", 95.0, 0.95, True, True, True)
    
    candidates = [
        {"name": "Low", "scorecard": card1, "pronunciation": pe.analyze("Low")},
        {"name": "High", "scorecard": card2, "pronunciation": pe.analyze("High")}
    ]
    ranked = stage.execute(candidates)
    assert ranked[0]["name"] == "High"

@pytest.mark.asyncio
async def test_pipeline_orchestrator() -> None:
    orchestrator = BrandPipelineOrchestrator()
    results, meta = await orchestrator.run_pipeline(
        industry="tech",
        context="visual branding engine",
        target_count=3
    )
    assert len(results) <= 3
    assert "stages_latencies_ms" in meta
