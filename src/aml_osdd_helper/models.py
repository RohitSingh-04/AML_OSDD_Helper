from typing import Literal, Optional

from pydantic import BaseModel, Field


from typing import Any, Dict, List, Literal, Optional


class RiskFactor(BaseModel):
    category: str = Field(description="Category of the risk factor (e.g., Financial, Regulatory, PEP, Reputational)")
    description: str = Field(description="Factual description of the identified risk")
    severity: Literal["Low", "Medium", "High", "Critical"] = Field(description="Risk severity level")


class SanctionsResult(BaseModel):
    is_sanctioned: bool = Field(default=False, description="Whether the entity or associated parties are under sanctions")
    details: Optional[str] = Field(default=None, description="Specific sanctions programs, lists, or regulatory bodies")
    sources: List[str] = Field(default_factory=list, description="URLs or reference points confirming sanctions checks")


class FinalOSDDResult(BaseModel):
    entity: str
    entity_type: Literal["Company", "Person", "Director", "UBO", "Organisation", "Group"]
    industry: Optional[str] = None
    jurisdiction: Optional[str] = None
    addresses: List[str] = Field(default_factory=list)
    description: str
    sources: List[str] = Field(default_factory=list)
    negative_news: bool = False
    negative_news_summary: Optional[str] = None
    negative_news_sources: List[str] = Field(default_factory=list)
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    sanctions: SanctionsResult
    pep_association: bool = False
    related_entities: List[str] = Field(default_factory=list)
    risk_score: int = Field(ge=0, le=100, description="Risk score from 0 (lowest) to 100 (highest)")
    risk_level: Literal["Very Low", "Low", "Moderate", "High", "Critical"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    assessment_summary: str
    limitations: List[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    entity_name: str
    address: str = ""


# Intermediate extraction model for chunked URL distillation
class SectionDistillation(BaseModel):
    findings: str = Field(description="Factual findings from this source relative to AML/KYC background")
    identified_addresses: List[str] = Field(default_factory=list)
    identified_related_entities: List[str] = Field(default_factory=list)
    negative_news_identified: bool = Field(default=False)
    negative_news_details: Optional[str] = Field(default=None)
    sanction_or_pep_flags: Optional[str] = Field(default=None)