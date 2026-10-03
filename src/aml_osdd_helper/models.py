from pydantic import BaseModel, Field
from typing import Literal, Optional

class AnalyzeRequest(BaseModel):
    entity_name: str
    address: str = ""

class BatchSummary(BaseModel):
    summary: str
    key_facts: list[str] = Field(default_factory=list)


class EntitySearchResult(BaseModel):
    entity: str
    entity_type: Literal["Company", "Person", "Director", "UBO", "Organisation", "Group"]
    industry: Optional[str] = None
    jurisdiction: Optional[str] = None
    addresses: list[str] = Field(default_factory=list)
    description: str
    related_entities: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)

class AddressSearchResult(BaseModel):
    addresses: list[str] = Field(default_factory=list)
    associated_entities: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    sources: list[str] = Field(default_factory=list)

class RiskFactor(BaseModel):
    category: str
    description: str
    severity: Literal["Low", "Medium", "High", "Critical"]
    source_urls: list[str] = Field(default_factory=list)


class SanctionsResult(BaseModel):
    listed: bool = False
    details: Optional[str] = None
    sources: list[str] = Field(default_factory=list)

class NegativeNewsResult(BaseModel):
    negative_news: bool = False
    negative_news_summary: Optional[str] = None
    risk_factors: list[RiskFactor] = Field(default_factory=list)
    sanctions: SanctionsResult
    pep_association: bool = False
    related_entities: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)

class FinalAssessment(BaseModel):
    risk_score: int
    risk_level: Literal["Very Low", "Low", "Moderate", "High", "Critical"]
    confidence: float
    assessment_summary: str
    limitations: list[str] = Field(default_factory=list)

class FinalOSDDResult(BaseModel):
    entity: str
    entity_type: Literal["Company", "Person", "Director", "UBO", "Organisation", "Group"]
    industry: Optional[str] = None
    jurisdiction: Optional[str] = None
    addresses: list[str] = Field(default_factory=list)
    description: str
    sources: list[str] = Field(default_factory=list)
    negative_news: bool = False
    negative_news_summary: Optional[str] = None
    negative_news_sources: list[str] = Field(default_factory=list)
    risk_factors: list[RiskFactor] = Field(default_factory=list)
    sanctions: SanctionsResult
    pep_association: bool = False
    related_entities: list[str] = Field(default_factory=list)
    risk_score: int
    risk_level: Literal["Very Low", "Low", "Moderate", "High", "Critical"]
    confidence: float
    assessment_summary: str
    limitations: list[str] = Field(default_factory=list)


class BatchSummary(BaseModel):
    summary: str
    key_facts: list[str] = Field(default_factory=list)

class NegativeNewsBatchSummary(BaseModel):
    relevant: bool
    adverse_events: list[str] = Field(default_factory=list)
    risk_categories: list[str] = Field(default_factory=list)
    entities_mentioned: list[str] = Field(default_factory=list)
    evidence_quality: Literal["Low", "Medium", "High"]
    evidence_basis: str | None = None