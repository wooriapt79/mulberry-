# Mulberry Email Agent

**해외 커뮤니티 활동 및 파트너십을 위한 이메일 에이전트**

---

## 📋 개요

Mulberry Email Agent는 CEO re.eul님의 Gmail 계정을 통해 개인화된 파트너십 제안 이메일을 작성하고 임시저장함에 저장하는 도구입니다.

### 3대 원칙

1. **Ultra-Personalization (철저한 개인화)**
   - 수신자 직함, 최근 성과 언급
   - "오직 당신을 위한 전략 제안"

2. **Data-Driven Logic (데이터 기반 객관성)**
   - Koda의 실시간 데이터
   - PM의 금융 로직
   - 숫자로 설득

3. **Smart Frequency Control (적절한 빈도 제어)**
   - 반응 속도에 맞춘 타이밍
   - 전략적 팔로업

---

## 🚀 설치 방법

### 방법 1: .exe 파일 사용 (추천)

1. `mulberry_email_agent.exe` 실행
2. Gmail 인증 버튼 클릭
3. 즉시 사용 가능!

### 방법 2: Python 소스 실행

```bash
# 1. 필요한 패키지 설치
pip install -r requirements.txt

# 2. 애플리케이션 실행
python mulberry_email_agent.py
```

---

## 🔧 사용 방법

### Step 1: Gmail 인증

1. "Gmail 계정 인증" 버튼 클릭
2. 브라우저에서 Google 로그인
3. Mulberry Email Agent에 권한 부여
4. 인증 완료!

**주의:** 최초 1회만 인증하면 됩니다. 이후에는 자동으로 로그인됩니다.

### Step 2: 수신자 정보 입력

필수 항목:
- **이메일**: 수신자 이메일 주소
- **이름**: 수신자 이름
- **직함**: 수신자 직함 (선택)

예시:
```
이메일: partnerships@google.com
이름: Sarah Johnson
직함: Partnership Manager
```

### Step 3: 템플릿 선택

4가지 템플릿 제공:

1. **google_partnership**: Google 파트너십 팀용
2. **inje_government**: 인제군청 전략사업과용
3. **media**: IT 미디어 기자단용
4. **overseas_partner**: 해외 파트너용

### Step 4: 데이터 포인트 입력 (선택)

Mulberry 프로젝트의 실제 데이터 입력:
- ROI: 1,966% (기본값)
- Seniors: 10 (기본값)

### Step 5: 커스텀 내용 추가 (선택)

특별히 강조하고 싶은 내용이 있다면 여기에 입력하세요.

예시:
```
Our recent AP2 community engagement (Issue #172) has received 
positive feedback from industry leaders.
```

### Step 6: 이메일 생성

두 가지 옵션:

1. **미리보기**: 이메일 내용을 먼저 확인
2. **임시저장함에 저장**: Gmail 임시저장함에 바로 저장

**중요:** 이메일은 자동 발송되지 않습니다!  
임시저장함에 저장되므로, 대표님께서 검토 후 발송하실 수 있습니다.

---

## 📧 템플릿 상세 설명

### 1. Google Partnership Template

**대상:** Google 파트너십 팀, AP2 커뮤니티 리더

**주요 포인트:**
- AP2 프로토콜 실제 구현 사례
- Social Welfare Mandates 세계 최초
- Spirit Score 혁신
- 협업 제안 (문서화, 표준화, 케이스 스터디)

**언어:** 영어

**예상 효과:**
- Google Cloud 케이스 스터디 참여
- AP2 레퍼런스 구현 인정
- 기술 커뮤니티 가시성 확보

---

### 2. Inje Government Template

**대상:** 인제군청 전략사업과, 사회복지과

**주요 포인트:**
- 식품사막 문제 해결
- 파일럿 예산 및 규모 (5백만원, 10명)
- 지역 경제 활성화
- 정부 예산 부담 최소화

**언어:** 한국어

**예상 효과:**
- 인제군 MOU 체결
- Q2 2026 파일럿 승인
- 정부 지원 확보

---

### 3. Media Template

**대상:** IT 미디어 기자, 테크 블로거

**주요 포인트:**
- 스토리 앵글 제시
- 뉴스 가치 강조 (기술, 임팩트, 타이밍, 혁신)
- 독점 인터뷰 제안
- 파일럿 결과 조기 접근

**언어:** 영어

**예상 효과:**
- TechCrunch, The Verge 등 주요 매체 보도
- 글로벌 가시성 확보
- 투자자 관심 유도

---

### 4. Overseas Partner Template

**대상:** 해외 기업, 투자자, 기술 파트너

**주요 포인트:**
- Mulberry 플랫폼 소개
- 파트너십 기회 제시
- 4가지 협업 영역 (기술, 지역 확장, R&D, 투자)
- 글로벌 확장 가능성

**언어:** 영어

**예상 효과:**
- 해외 투자 유치
- 기술 파트너십 체결
- 글로벌 확장 기반 마련

---

## 🎯 고급 사용법

### Batch Processing (여러 이메일 한번에)

향후 업데이트 예정:
- CSV 파일로 수신자 목록 업로드
- 한번에 여러 이메일 생성
- 자동 개인화

### 추적 기능

현재 버전: 기본 Gmail 추적 (열람 확인 요청)

향후 업데이트 예정:
- 링크 클릭 추적
- 관심도 순위 보고
- 자동 팔로업 제안

### A/B Testing

향후 업데이트 예정:
- 제목 라인 테스트
- 내용 변형 테스트
- 최적 발송 시간 분석

---

## 🔒 보안 및 프라이버시

### OAuth 2.0 인증

- Google의 공식 OAuth 2.0 사용
- 비밀번호 저장 안함
- 언제든 권한 취소 가능

### 권한 범위

Mulberry Email Agent가 요청하는 권한:
- `gmail.compose`: 이메일 작성
- `gmail.modify`: 임시저장함 접근

**요청하지 않는 권한:**
- 이메일 읽기
- 이메일 삭제
- 연락처 접근

### 데이터 저장

로컬에만 저장:
- `token.pickle`: OAuth 토큰 (로컬)
- `client_secret.json`: OAuth 클라이언트 정보 (로컬)

**서버 전송 없음**: 모든 작업이 로컬에서 처리됩니다.

---

## 🛠️ 문제 해결

### 인증 실패

**증상:** "인증 실패" 오류

**해결:**
1. `token.pickle` 파일 삭제
2. 애플리케이션 재시작
3. 다시 인증

### client_secret.json 오류

**증상:** "client_secret.json not found"

**해결:**
1. `client_secret.json` 파일이 같은 폴더에 있는지 확인
2. 파일명이 정확한지 확인

### 임시저장함에 없음

**증상:** 이메일이 임시저장함에 보이지 않음

**해결:**
1. Gmail 새로고침 (F5)
2. 임시저장함 직접 확인
3. 스팸함 확인

---

## 📊 사용 통계 (Malu 실장님용)

### 주요 메트릭

추적 가능 항목:
- 임시저장함 생성 수
- 템플릿별 사용 빈도
- 평균 커스텀 내용 길이

### 성과 측정

Gmail에서 확인:
- 열람률 (Gmail 열람 확인 기능)
- 회신률
- 미팅 전환율

---

## 🚀 로드맵

### v1.0 (현재)
- ✅ 4가지 템플릿
- ✅ Gmail 임시저장함 저장
- ✅ 데이터 포인트 삽입
- ✅ 커스텀 내용 추가

### v1.1 (예정)
- ⏳ CSV 배치 처리
- ⏳ 링크 클릭 추적
- ⏳ 자동 팔로업

### v2.0 (예정)
- ⏳ AI 기반 개인화 강화
- ⏳ 다국어 지원 (중국어, 일본어)
- ⏳ 관심도 대시보드

---

## 💡 베스트 프랙티스

### 1. 개인화는 필수

**나쁜 예:**
```
Dear Sir/Madam,
```

**좋은 예:**
```
Dear Partnership Manager Sarah Johnson,

I noticed your recent work on Google Cloud AI initiatives...
```

### 2. 데이터로 말하라

**나쁜 예:**
```
Our platform works well.
```

**좋은 예:**
```
Our pilot achieved 1,966% ROI and supported 10 seniors 
with zero government subsidies.
```

### 3. 명확한 CTA (Call-to-Action)

**나쁜 예:**
```
Let me know if you're interested.
```

**좋은 예:**
```
Would you be available for a 15-minute call next Tuesday 
at 2pm PST to explore this further?
```

### 4. 적절한 빈도

**권장:**
- 첫 이메일 후 3일 대기
- 회신 없으면 부드러운 팔로업
- 2회 팔로업 후 중단

**비권장:**
- 매일 이메일
- 동일 내용 반복
- 공격적인 톤

---

## 🤝 지원

### 문의

**기술 문의:**
- CTO Koda
- GitHub Issues

**사용 문의:**
- Malu 실장님

### 피드백

사용 중 개선 아이디어가 있으시면 언제든 공유해주세요!

---

## 📝 라이선스

**Mulberry Project Internal Use Only**

본 소프트웨어는 Mulberry 프로젝트 팀 내부용입니다.

---

## 🙏 크레딧

**개발:** CTO Koda  
**기획:** CEO re.eul, Malu 실장  
**협력:** CSA Kbin, PM

**One Team!** 💙

---

**Mulberry Email Agent v1.0**  
**2026년 2월 26일**
