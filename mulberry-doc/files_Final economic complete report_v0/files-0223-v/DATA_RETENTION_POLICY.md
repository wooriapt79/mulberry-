# 📦 데이터 보존 정책 (Data Retention Policy)

**프로젝트:** Mulberry AI Agent Investment Platform  
**작성:** CTO Koda  
**일자:** 2026년 2월 23일  
**PM 제안 반영**

---

## 🎯 정책 개요

시간이 지남에 따라 중요도가 낮아지는 데이터를 효율적으로 관리하기 위한 보존 및 아카이빙 전략입니다.

---

## 📊 테이블별 보존 정책

### Tier 1: 영구 보존 (Permanent)

**대상 테이블:**
- `Investor` (투자자 마스터)
- `Agent` (Agent 마스터)
- `Investment` (투자 계약)
- `Badge` (배지 정의)
- `AP2Mandate` (법적 계약)

**정책:**
```
보존 기간: 영구
백업: 일일 전체 백업
아카이빙: 없음
이유: 법적/재무 기록
```

---

### Tier 2: 장기 보존 (Long-term, 5년)

**대상 테이블:**
- `Return` (수익 배분)
- `SkillNFT` (NFT 거래)
- `NFTTransaction` (거래 내역)
- `AuditLog` (감사 로그)

**정책:**
```
핫 스토리지: 최근 1년
웜 스토리지: 1~3년
콜드 스토리지: 3~5년
삭제: 5년 후 (법적 요구 충족 후)
```

**구현:**
```sql
-- PostgreSQL 파티셔닝 (연도별)
CREATE TABLE returns_2026 PARTITION OF returns
  FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- 콜드 스토리지로 이동 (3년 후)
CREATE TABLE returns_cold_2026 AS
  SELECT * FROM returns_2026
  WHERE distributed_at < NOW() - INTERVAL '3 years';

-- 원본 삭제 (5년 후)
DELETE FROM returns_2026
  WHERE distributed_at < NOW() - INTERVAL '5 years';
```

---

### Tier 3: 중기 보존 (Medium-term, 1년)

**대상 테이블:**
- `InvestorActivity` (투자자 활동)
- `AgentActivity` (Agent 활동)
- `Notification` (알림)

**정책:**
```
핫 스토리지: 최근 3개월
웜 스토리지: 3~12개월
삭제: 1년 후
```

**구현:**
```sql
-- 월별 파티셔닝
CREATE TABLE investor_activity_2026_01 PARTITION OF investor_activity
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- 자동 삭제 (1년 후)
CREATE EXTENSION pg_cron;

SELECT cron.schedule(
  'delete-old-activities',
  '0 2 * * 0',  -- 매주 일요일 02:00
  $$
  DELETE FROM investor_activity
  WHERE created_at < NOW() - INTERVAL '1 year'
  $$
);
```

---

### Tier 4: 단기 보존 (Short-term, 90일)

**대상 테이블:**
- `Leaderboard` (리더보드 - 주간/월간)

**정책:**
```
핫 스토리지: 전체 기간 (90일)
삭제: 90일 후
예외: all_time 타입은 영구 보존
```

**구현:**
```sql
-- 조건부 삭제
DELETE FROM leaderboard
WHERE period IN ('daily', 'weekly', 'monthly')
  AND period_end < NOW() - INTERVAL '90 days';
```

---

## 🗄️ 아카이빙 전략

### 1. 핫 스토리지 (Hot Storage)

**특징:**
- 빠른 SSD
- 자주 조회되는 최신 데이터
- 응답 시간 < 100ms

**대상:**
- 최근 3개월 활동
- 진행 중인 투자
- 활성 NFT 거래

---

### 2. 웜 스토리지 (Warm Storage)

**특징:**
- HDD 또는 저속 SSD
- 가끔 조회되는 데이터
- 응답 시간 < 1초

**대상:**
- 3개월 ~ 1년 활동
- 완료된 투자 (최근 1년)
- 오래된 감사 로그

**구현:**
```sql
-- Tablespace 분리
CREATE TABLESPACE warm_storage
  LOCATION '/data/warm';

ALTER TABLE investor_activity_2025_10
  SET TABLESPACE warm_storage;
```

---

### 3. 콜드 스토리지 (Cold Storage)

**특징:**
- S3, Glacier, Tape
- 거의 조회 안 됨
- 복원 시간 수 시간 가능

**대상:**
- 1년 이상 된 데이터
- 법적 요구로만 보존

**구현:**
```bash
# PostgreSQL → S3 백업
pg_dump -t returns_2023 | \
  gzip | \
  aws s3 cp - s3://mulberry-archive/returns_2023.sql.gz \
    --storage-class GLACIER
```

---

## 📅 자동화 스케줄

### 일일 작업 (Daily)

```bash
# 02:00 - 증분 백업
0 2 * * * /scripts/backup_incremental.sh

# 03:00 - 핫 스토리지 정리
0 3 * * * /scripts/cleanup_hot.sh
```

### 주간 작업 (Weekly)

```bash
# 일요일 04:00 - 웜 스토리지로 이동
0 4 * * 0 /scripts/move_to_warm.sh

# 일요일 05:00 - 오래된 알림 삭제
0 5 * * 0 /scripts/delete_old_notifications.sh
```

### 월간 작업 (Monthly)

```bash
# 매월 1일 06:00 - 콜드 스토리지로 이동
0 6 1 * * /scripts/move_to_cold.sh

# 매월 1일 07:00 - 전체 백업
0 7 1 * * /scripts/backup_full.sh
```

### 연간 작업 (Yearly)

```bash
# 매년 1월 1일 - 5년 이상 데이터 삭제
0 8 1 1 * /scripts/delete_old_data.sh
```

---

## 📊 스토리지 용량 계획

### 현재 (파일럿 - 10 Agents, 10 Investors)

| 저장소 | 용량 | 백업 |
|--------|------|------|
| 핫 | 100MB | 일일 |
| 웜 | 0MB | - |
| 콜드 | 0MB | - |
| **총계** | **100MB** | - |

---

### 1년 후 (1,000 Agents, 10,000 Investors)

| 저장소 | 용량 | 비율 |
|--------|------|------|
| 핫 (3개월) | 100MB | 26% |
| 웜 (9개월) | 200MB | 51% |
| 콜드 | 90MB | 23% |
| **총계** | **390MB** | 100% |

---

### 5년 후 (10,000 Agents, 100,000 Investors)

| 저장소 | 용량 | 비율 |
|--------|------|------|
| 핫 (3개월) | 1GB | 5% |
| 웜 (9개월) | 3GB | 16% |
| 콜드 (4년) | 15GB | 79% |
| **총계** | **19GB** | 100% |

---

## 🔐 보안 및 규정 준수

### 개인정보보호법 준수

```
✅ 3년 보존 (금융 거래)
✅ 5년 보존 (계약 관계)
✅ 7년 보존 (세무 기록)
✅ 익명화 처리 (마케팅 데이터)
✅ 삭제 요청 대응 (GDPR)
```

### 암호화

```
핫 스토리지: AES-256 (at-rest)
웜 스토리지: AES-256 (at-rest)
콜드 스토리지: AES-256 + Glacier Vault Lock
```

### 삭제 정책

```python
# 완전 삭제 (GDPR 준수)
def delete_user_data(user_id: str):
    """
    사용자 데이터 완전 삭제
    - 개인식별정보 즉시 삭제
    - 거래 기록은 익명화 후 보존
    - 감사 로그에 삭제 기록
    """
    
    # 1. 개인정보 삭제
    db.execute("""
        UPDATE investors
        SET name = 'DELETED',
            email = NULL,
            passport_id = NULL
        WHERE id = %s
    """, [user_id])
    
    # 2. 거래 기록 익명화
    db.execute("""
        UPDATE investments
        SET investor_id = 'ANONYMOUS'
        WHERE investor_id = %s
    """, [user_id])
    
    # 3. 감사 로그 기록
    audit_log.create({
        'action': 'USER_DATA_DELETED',
        'entity_id': user_id,
        'reason': 'GDPR_REQUEST'
    })
```

---

## 📈 모니터링

### 용량 알림

```python
# 일일 체크
if hot_storage_usage > 80%:
    alert("핫 스토리지 80% 초과 - 웜으로 이동 필요")

if total_storage > budget * 0.9:
    alert("총 스토리지 예산 90% 초과")
```

### 성능 모니터링

```sql
-- 느린 쿼리 감지
SELECT query, mean_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 1초 이상
ORDER BY mean_exec_time DESC;
```

---

## 🔄 복원 절차

### 핫/웜 스토리지 복원 (즉시)

```sql
-- 단순 조회
SELECT * FROM returns_2025_06
WHERE investment_id = 'inv_123';
```

### 콜드 스토리지 복원 (수 시간)

```bash
# 1. S3에서 다운로드
aws s3 cp s3://mulberry-archive/returns_2023.sql.gz . \
  --restore-request Days=7

# 2. 압축 해제
gunzip returns_2023.sql.gz

# 3. 복원
psql -d mulberry -f returns_2023.sql
```

---

## ✅ 체크리스트

### 월간 점검

```
☐ 핫 스토리지 용량 확인
☐ 웜 스토리지로 이동 완료 확인
☐ 백업 무결성 검증
☐ 삭제 스케줄 실행 확인
```

### 분기 점검

```
☐ 콜드 스토리지 용량 확인
☐ 스토리지 비용 검토
☐ 보존 정책 준수 확인
☐ 복원 테스트 수행
```

### 연간 점검

```
☐ 전체 데이터 아카이브
☐ 5년 이상 데이터 삭제
☐ 보존 정책 갱신
☐ 규정 준수 감사
```

---

<div align="center">

## 📦 데이터 보존 정책

**효율적 스토리지 관리**

**법적 요구사항 준수**

**비용 최적화**

---

**Made with 💙 by CTO Koda**

**2026년 2월 23일**

</div>
