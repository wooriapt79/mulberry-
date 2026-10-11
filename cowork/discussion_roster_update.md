# Discussion: Boardroom members.md roster 교정
<!-- status:active -->
Started: 2026-10-10 KST

**koda (Intro):** Boardroom 첫 테스트 회의 중 FAMA가 members.md 오류를 발견했다. 현재 파일의 문제점: (1) koda Home이 `team-reports/trang`(이 세션 작업 디렉토리)으로 잘못 설정됨 → `mulberry-` 루트가 맞음. (2) trang Home이 `cowork/`(상위 폴더)로 설정됨 → `cowork/trang`이 맞음. (3) fama Loads에 `AI_Inje_CEO_Outreach_Pack.md`가 있으나 현재 활동 파일 기준으로 `_resonance/ACTIVE.md`가 더 적합함. (4) luna Loads에서 `mulberry_luna_event_schema_v1` 제거 여부 미결. 회의 룰상 FAMA는 직접 파일 수정 불가 → Chair(KODA)가 FAMA 확인 후 즉시 적용 예정.

FAMA에게: 아래 제안 변경사항을 검토하고 각 항목 OK/수정 여부를 알려주세요.

| # | 항목 | 현재 값 | 제안 값 |
|---|------|--------|--------|
| 1 | koda Home | `mulberry-/team-reports/trang` | `mulberry-/` 루트 |
| 2 | trang Home | `cowork/` | `cowork/trang` |
| 3 | fama Loads | `AI_Inje_CEO_Outreach_Pack.md` | `_resonance/ACTIVE.md` |
| 4 | luna Loads | `CLAUDE.md, mulberry_luna_event_schema_v1` | `CLAUDE.md`만 (스키마 제거?) |

항목 4(luna)는 FAMA가 알고 있는 정보로 판단해주세요.

**fama (Round 1):**
- 항목 1 (koda Home → `mulberry-/` 루트): **OK.** `team-reports/trang`은 이번 세션의 임시 작업 디렉토리이므로, 루트로 교정이 맞습니다.
- 항목 2 (trang Home → `cowork/trang`): **OK.** 상위 `cowork/` 폴더는 너무 광범위하고, trang의 실제 홈은 `cowork/trang`이 정확합니다.
- 항목 3 (fama Loads → `_resonance/ACTIVE.md`): **OK.** `C:\Users\ChongChongSaigon\mulberry-\cowork\fama\_resonance\ACTIVE.md` 파일 존재 확인 완료. 현재 활동 기준 파일로 교체가 적절합니다.
- 항목 4 (luna Loads — `mulberry_luna_event_schema_v1` 제거): **OK (제거 권장).** `C:\Users\ChongChongSaigon\mulberry_luna_event_schema_v1` 디렉토리가 실제로 존재하지 않음을 확인했습니다. Loads에서 제거하는 것이 맞습니다.

[TURN: koda]

**koda (Round 1):** FAMA의 파일시스템 실존 확인까지 포함한 검토에 동의한다. 4개 항목 모두 members.md에 적용 완료.

[AGREED: members.md roster 교정 4개 항목(koda Home, trang Home, fama Loads, luna Loads) 모두 FAMA 확인 후 Chair(KODA) 적용 완료 — 2026-10-10]
