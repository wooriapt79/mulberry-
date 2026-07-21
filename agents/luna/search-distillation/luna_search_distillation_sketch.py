# luna_search_distillation_sketch.py
# Mulberry Project — Luna Search Distillation
# Author  : CSA KeBin (초안) / Jr. TRANG Luna (검수·수정)
# Version : v0.1.1  Date: 2026-07-21
#
# Security:
#   1. No Naver AI-tab scraping / login bypass / CAPTCHA bypass
#   2. No LocalProvider registration without business consent
#   3. passport_id must be issued by agent_gateway v2.0
#   4. PII candidates always routed to HumanReviewGate

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
import uuid


@dataclass
class SearchRequest:
    query: str
    region: str
    budget: int | None = None
    constraints: list[str] = field(default_factory=list)


@dataclass
class TradeCandidate:
    candidate_id: str
    name: str
    source: str
    price: int | None
    availability: str
    sponsored: bool
    local_business: bool
    passport_id: str | None
    verified_at: str
    evidence_url: str


class SearchAdapter(Protocol):
    name: str
    def search(self, request: SearchRequest) -> list[TradeCandidate]: ...


class NaverOfficialAPIAdapter:
    """
    Official Naver API only.
    [SECURITY] No scraping / login bypass / CAPTCHA bypass.
    [SECURITY] passport_id is always None (external unverified data).
    """
    name = "naver_official_api"

    def search(self, request: SearchRequest) -> list[TradeCandidate]:
        return [
            TradeCandidate(
                candidate_id=str(uuid.uuid4()),
                name="인제 지역 업체 A",
                source=self.name,
                price=85_000,
                availability="unknown",
                sponsored=False,
                local_business=True,
                passport_id=None,
                verified_at=datetime.now().isoformat(),
                evidence_url="https://example.com/provider-a",
            )
        ]


class LocalProviderAdapter:
    """
    Mulberry registered local providers (consent required).
    [SECURITY] passport_id must be from agent_gateway v2.0 issue_passport().
    """
    name = "mulberry_local_provider"

    def search(self, request: SearchRequest) -> list[TradeCandidate]:
        return [
            TradeCandidate(
                candidate_id=str(uuid.uuid4()),
                name="인제 지역 업체 B",
                source=self.name,
                price=79_000,
                availability="confirmed",
                sponsored=False,
                local_business=True,
                passport_id="PROVIDER-INJE-001",
                verified_at=datetime.now().isoformat(),
                evidence_url="https://example.com/provider-b",
            )
        ]


class CandidateNormalizer:
    def normalize(self, candidates: list[TradeCandidate]) -> list[TradeCandidate]:
        unique: dict[str, TradeCandidate] = {}
        for c in candidates:
            key = c.name.strip().lower()
            if key not in unique:
                unique[key] = c
            elif c.availability == "confirmed" and unique[key].availability != "confirmed":
                unique[key] = c
        return list(unique.values())


class LunaRanker:
    """Score: confirmed+30, local+20, passport+20, budget+20, evidence+10, sponsored-10"""

    def score(self, request: SearchRequest, candidate: TradeCandidate) -> float:
        s = 0.0
        if candidate.availability == "confirmed": s += 30
        if candidate.local_business: s += 20
        if candidate.passport_id: s += 20
        if request.budget and candidate.price and candidate.price <= request.budget: s += 20
        if candidate.sponsored: s -= 10
        if candidate.evidence_url: s += 10
        return s

    def rank(self, request, candidates):
        return sorted([(c, self.score(request, c)) for c in candidates], key=lambda x: x[1], reverse=True)


class HumanReviewGate:
    """Triggers: score<50 | availability unknown | no passport"""
    def requires_review(self, candidate: TradeCandidate, score: float) -> bool:
        return score < 50 or candidate.availability == "unknown" or candidate.passport_id is None


def run_sketch() -> list[dict]:
    request = SearchRequest(
        query="부모님과 갈 수 있는 인제 숙소",
        region="인제군",
        budget=100_000,
        constraints=["주차", "고령자 접근성"],
    )
    adapters: list[SearchAdapter] = [NaverOfficialAPIAdapter(), LocalProviderAdapter()]
    collected: list[TradeCandidate] = []
    for adapter in adapters:
        collected.extend(adapter.search(request))
    candidates = CandidateNormalizer().normalize(collected)
    ranked = LunaRanker().rank(request, candidates)
    gate = HumanReviewGate()
    return [
        {
            "candidate": c.name, "source": c.source, "score": score,
            "sponsored": c.sponsored, "passport_verified": bool(c.passport_id),
            "human_review_required": gate.requires_review(c, score),
        }
        for c, score in ranked
    ]


if __name__ == "__main__":
    # [FIX v0.1.1] typo: run sketch() -> run_sketch()
    for result in run_sketch():
        print(result)
