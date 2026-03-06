# 🚀 Mulberry Email Agent - 빠른 시작 가이드

**해외 커뮤니티 활동 및 파트너십을 위한 이메일 에이전트**

---

## ⚡ 5분 안에 시작하기

### 1️⃣ 파일 준비 (이미 완료!)

다음 파일들이 있는지 확인:
- ✅ `mulberry_email_agent.py` (메인 프로그램)
- ✅ `client_secret.json` (Google OAuth 인증 정보)
- ✅ `requirements.txt` (필요한 패키지)
- ✅ `README.md` (상세 가이드)

### 2️⃣ 실행 방법 선택

#### 방법 A: Python 직접 실행 (권장)

```bash
# 1. 패키지 설치 (최초 1회만)
pip install -r requirements.txt

# 2. 실행
python mulberry_email_agent.py
```

#### 방법 B: .exe 파일 생성 (Windows용)

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. .exe 빌드
python build_exe.py

# 3. 생성된 파일 실행
# → dist/mulberry_email_agent.exe
```

### 3️⃣ Gmail 인증

1. **"Gmail 계정 인증"** 버튼 클릭
2. 브라우저가 열리면 Google 로그인
3. "Mulberry Email Agent" 권한 허용
4. 완료! (다음부터는 자동 로그인)

### 4️⃣ 첫 이메일 작성

**수신자 정보:**
```
이메일: partnerships@google.com
이름: Sarah Johnson
직함: Partnership Manager
```

**템플릿:** `google_partnership`

**데이터:** 
- ROI: 1,966%
- Seniors: 10

**버튼 클릭:** "임시저장함에 저장"

### 5️⃣ Gmail에서 확인

1. Gmail 임시저장함 열기
2. 방금 만든 이메일 확인
3. 필요시 수정
4. 발송!

---

## 📧 4가지 템플릿

### 1. Google Partnership
- **대상:** Google 파트너십 팀
- **언어:** English
- **내용:** AP2 implementation, Social Welfare Mandates

### 2. Inje Government
- **대상:** 인제군청 전략사업과
- **언어:** 한국어
- **내용:** 파일럿 제안, 예산 계획

### 3. Media
- **대상:** IT 미디어, 기자
- **언어:** English
- **내용:** 스토리 앵글, 독점 인터뷰

### 4. Overseas Partner
- **대상:** 해외 파트너, 투자자
- **언어:** English
- **내용:** 협업 제안, 4가지 영역

---

## 🎯 3대 원칙

### 1. Ultra-Personalization
✅ 수신자 이름, 직함 필수 입력  
✅ 최근 성과 언급  
✅ "오직 당신을 위한 제안"

### 2. Data-Driven Logic
✅ ROI 1,966% (실제 데이터)  
✅ Seniors 10명 지원  
✅ 구체적 숫자로 설득

### 3. Smart Frequency Control
✅ 첫 이메일 후 3일 대기  
✅ 부드러운 팔로업  
✅ 최대 2회 팔로업

---

## 🔒 보안

### ✅ 안전합니다
- Google 공식 OAuth 2.0 사용
- 비밀번호 저장 안함
- 로컬에서만 작동
- 서버 전송 없음

### 📋 권한
**요청하는 권한:**
- gmail.compose (이메일 작성)
- gmail.modify (임시저장함 접근)

**요청하지 않는 권한:**
- 이메일 읽기 ❌
- 이메일 삭제 ❌
- 연락처 접근 ❌

---

## 🆘 문제 해결

### 인증 오류?
```bash
# 1. token.pickle 삭제
rm token.pickle

# 2. 다시 시작
python mulberry_email_agent.py
```

### 패키지 오류?
```bash
# 재설치
pip install -r requirements.txt --force-reinstall
```

### 임시저장함에 없음?
1. Gmail 새로고침 (F5)
2. 스팸함 확인
3. 다시 저장 시도

---

## 📞 지원

**기술 문의:** CTO Koda  
**사용 문의:** Malu 실장님

---

## 💡 팁

### 효과적인 이메일
1. **제목:** 간결하고 구체적으로
2. **본문:** 데이터 중심, 3문단 이내
3. **CTA:** 명확한 다음 단계 제시

### 최적 발송 시간
- **해외:** 현지 시간 화요일-목요일 오전
- **국내:** 화요일-목요일 오전 10-11시

### 팔로업 타이밍
- **1차:** 3일 후
- **2차:** 1주일 후
- **중단:** 2회 이후 회신 없으면

---

## 🎉 이제 시작하세요!

```bash
python mulberry_email_agent.py
```

**One Team!** 💙

---

**Mulberry Email Agent v1.0**  
**2026년 2월 26일**  
**CTO Koda**
