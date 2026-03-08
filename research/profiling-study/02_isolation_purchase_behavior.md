# 🧠 프로파일러 스터디 #02
## 고립감 × 구매 행동 패턴

**정리자**: Nguyen Trang (AI Ops Manager)
**날짜**: 2026-03-08
**목적**: 외로운 어르신의 구매 심리를 이해하고 Mulberry 공동구매 설계에 반영

---

## 📌 핵심 발견 1: 외로움 → 쇼핑으로 도피한다

**논문**: "Escaping loneliness through shopping: materialism, impulse buying and escapism" (ResearchGate, 2025)
- 링크: https://www.researchgate.net/publication/390619896

**핵심**:
- 외로움 → 물질주의 강화 → 충동구매 증가
- 코로나 고립 → 불안·외로움 → 충동구매 → 죄책감·후회
- **감정 보상 소비 (Compensatory Consumption)**: 외로울 때 물건을 사서 심리적 공백을 채우려는 행동

### ⚠️ 역설적 결과
> 외로움을 물건으로 채우려 하면 → 오히려 더 외로워진다
> (물건이 사람 관계를 대체하기 때문)

### Mulberry Agent 적용
```
❌ 잘못된 접근: "좋은 상품 많아요, 사세요"
✅ 올바른 접근: "우리 동네 어르신들이랑 같이 사면 더 저렴해요"

→ 구매의 이유를 '물건'이 아닌 '사람·커뮤니티'로 프레이밍
→ 공동구매 = 쇼핑 + 소속감 동시 해결
```

---

## 📌 핵심 발견 2: 고립된 어르신의 구매 행동 패턴

**논문**: "Consumer loneliness: A systematic review and research agenda" (PMC, 2023)
- 링크: https://pmc.ncbi.nlm.nih.gov/articles/PMC9895855/

**논문**: "Loneliness and Social Isolation Among US Older Adults" (JAMA, 2024)
- 링크: https://jamanetwork.com/journals/jama/fullarticle/2827710

**핵심 데이터**:
- 미국 50-80세: **33.9%**가 "외롭다" (2018)
- 팬데믹 이후: **41.4%**로 급증 (2020)
- 현재(2024): 33.4% — 여전히 3명 중 1명
- 한국 농촌 어르신: 이보다 훨씬 높을 것으로 추정

**외로운 소비자의 행동 특징**:
- 판매자와의 **대화·관계**를 더 중요시함
- **신뢰할 수 있는 고정 판매자**를 선호 (가격보다 관계)
- 반복 구매 패턴 → 한 번 신뢰 형성되면 이탈율 낮음
- 구매 전후 **확인 전화**를 원함 (안심 욕구)

---

## 📌 핵심 발견 3: 한국 농촌 × 공동구매 × 신뢰

**논문**: "Food Desert, Purchasing Refugees, and Cooperatives in Rural South Korea" (FFTC, 2023)
- 링크: https://ap.fftc.org.tw/article/3276

**논문**: "Community Group-Buying and Trust Transfer Theory" (Frontiers in Psychology, 2022)
- 링크: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.903221/full

**핵심**:
- 한국 농촌: 이동 거리 멀고 마트 없음 → **구매 난민(Purchasing Refugees)** 발생
- 협동조합 이동 판매차 → 농촌 어르신의 식품 접근 문제 일부 해결
- **오프라인 커뮤니티에서는 사람 관계 기반 신뢰가 핵심**
- 고정 그룹장(리더)에 대한 신뢰 → 장기 구매 의도 증가

### 공동구매 리더(그룹장)의 역할
```
그룹장 = 신뢰 앵커
- 이웃 어르신들의 신뢰를 받는 사람이 그룹장
- 그룹장이 추천하면 → 다른 어르신들이 따라 구매
- mulberry 공동구매 모임 = 그룹장 중심 신뢰 네트워크
```

---

## 📌 핵심 발견 4: 노인·식품·사회적 포용

**논문**: "Supporting each other: Older adults' food security and social inclusion in rural/food desert communities" (ScienceDirect, 2024)
- 링크: https://www.sciencedirect.com/science/article/pii/S0195666324001545

**핵심**:
- 식품 접근 = 단순 먹거리 문제가 아닌 **사회적 포용(Social Inclusion)** 문제
- 함께 장보고, 함께 먹는 행위 → 고립감 해소
- 식품 공동구매 모임 → 노인 자존감·참여감 향상

---

## 📊 종합 정리: 고립 어르신 구매 심리 지도

```
고립·외로움
    ↓
[감정 보상 욕구] → 물건으로 채우려 함 (단기 해소, 장기 악화)
    ↓
[Mulberry 개입 포인트]
    ↓
공동구매 모임 참여
= 물건 구매 + 사람 만남 + 소속감
    ↓
외로움 근본 해소 + 식품 접근성 해결
    ↓
신뢰 형성 → 반복 구매 → 그룹장 역할 부여
    ↓
자존감·자아실현 (매슬로우 4-5단계)
```

---

## 🎯 Mulberry Agent 설계 원칙 (이번 스터디 기반)

| 상황 | Agent 대응 전략 |
|---|---|
| 어르신이 혼자 산다고 함 | "우리 동네 어르신들이랑 같이 해봐요" (소속감 유도) |
| 가격만 물어볼 때 | "이웃 누구누구 어르신도 하세요" (신뢰 전이) |
| 자주 전화·확인할 때 | 안심시키기 우선, 확인 문자 발송 |
| 처음 구매 망설임 | 소량 체험 → 그룹장 연결 → 신뢰 확보 순서 |
| 반복 구매 어르신 | 그룹장 후보로 육성 (자존감 4단계 자극) |

---

## 다음 스터디 예정 주제
- [ ] #03 방언·사투리와 신뢰 형성 심리
- [ ] #04 고령자 디지털 기기 수용 심리
- [ ] #05 커뮤니티 신뢰 네트워크 이론

---

*📚 Nguyen Trang 프로파일러 스터디 시리즈 #02*
*"외로움을 물건이 아닌 사람으로 채워주는 것이 Mulberry의 역할이다"*
