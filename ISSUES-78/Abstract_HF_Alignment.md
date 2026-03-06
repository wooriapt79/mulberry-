# Abstract x HuggingFace Demo 정합성 가이드
# 2026-03-04

## 수치 통일 기준표

| 항목 | 현재 표기 | 확정 표기 |
|------|---------|---------|
| 트랜잭션 수 | 3,000+ | 1,500+ field + simulation-extended |
| DTMF 성공률 | 97% | ~97% (simulation-projected) |
| 취소 시간 | 13초/3분 혼재 | 15s agent-side / 3min end-to-end |
| arXiv | under submission | in preparation (Q2 2026) |

## HF Demo Space 2 수정 문구

Voice Protocol Simulator 결과창:
- Agent-side processing: ~15 seconds
- Full propagation: < 3 minutes  
- Simulation-projected reliability: ~97%
- Field baseline: 1,500+ transactions in Inje-gun
- Data-only comparison: 30+ minutes (60% success)
- Note: Simulation values validated against field deployment

## Abstract 핵심 문장 수정

기존: "3,000+ completed transactions ... 99.9% success rate"
수정: "1,500+ field transactions (simulation-extended) ... 99.9% simulated success rate (field validation ongoing)"

기존: "under submission to arXiv"
수정: "in preparation (target: arXiv Q2 2026)"
