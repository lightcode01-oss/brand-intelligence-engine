import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# 1. Overview Schema
class OverviewMetricPoint(BaseModel):
    total_generations: int
    credits_consumed: float
    success_rate: float
    export_count: int
    active_projects: int
    total_members: int

class OverviewResponse(BaseModel):
    workspace_id: uuid.UUID
    metrics: OverviewMetricPoint
    daily_generations: List[Dict[str, Any]] # e.g. [{"date": "2026-06-29", "count": 120}]
    credit_usage: List[Dict[str, Any]] # e.g. [{"date": "2026-06-29", "amount": 25.0}]

# 2. Credits Schema
class CreditTransactionPoint(BaseModel):
    id: uuid.UUID
    amount: float
    type: str
    created_at: datetime
    expires_at: Optional[datetime] = None

class CreditsAnalyticsResponse(BaseModel):
    current_balance: float
    total_credited: float
    total_debited: float
    transactions: List[CreditTransactionPoint]

# 3. Usage Schema
class UsageAnalyticsResponse(BaseModel):
    total_requests: int
    provider_breakdown: Dict[str, int] # {"gemini": 150, "gpt-4o": 50, "claude": 20}
    daily_usage: List[Dict[str, Any]]

# 4. Team Activity Schema
class UserMetricPoint(BaseModel):
    user_id: uuid.UUID
    email: str
    credits_consumed: float
    generations_count: int
    exports_count: int
    comments_count: int
    favorites_count: int
    collections_count: int

class TeamActivityResponse(BaseModel):
    members: List[UserMetricPoint]
    leaderboard: List[Dict[str, Any]]

# 5. Workspace Analytics Schema
class WorkspaceAnalyticsResponse(BaseModel):
    workspace_id: uuid.UUID
    projects_count: int
    members_count: int
    collections_count: int
    favorites_count: int
    growth_timeline: List[Dict[str, Any]] # [{"date": "2026-06-29", "projects": 5, "members": 2}]

# 6. AI Performance Schema
class AIProviderMetric(BaseModel):
    provider: str
    latency_avg_ms: float
    success_rate: float
    failure_rate: float
    requests_total: int
    cost_total: float
    tokens_avg: float
    requests_per_minute: float

class AIPerformanceResponse(BaseModel):
    providers: List[AIProviderMetric]

# 7. Brand Score Trends Schema
class BrandScoreTrendsResponse(BaseModel):
    average_overall_bsi: float
    avg_length: float
    avg_pronounceability: float
    avg_domain_score: float
    avg_trademark_score: float
    avg_semantic_score: float
    trademark_risk_distribution: Dict[str, int] # {"CLEAR": 80, "WARNING": 15, "CONFLICT": 5}
    length_distribution: Dict[int, int] # {5: 12, 6: 25, 7: 18}

# 8. Saved Reports Schema
class SavedReportCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    report_type: str = Field(..., description="Type of report generated ('analytics', 'insights', 'team', 'audit').")
    format: str = Field(..., description="File format ('pdf', 'markdown', 'json', 'csv').")
    data_json: Optional[Dict[str, Any]] = None

class SavedReportResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    report_type: str
    format: str
    data_json: Dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 9. Recommendation Schema
class RecommendationResponse(BaseModel):
    stronger_prompts: List[str]
    better_industries: List[str]
    logo_colors: List[str]
    typography: List[str]
    slogan_suggestions: List[str]
    domain_alternatives: List[str]
    similar_successful_brands: List[str]
