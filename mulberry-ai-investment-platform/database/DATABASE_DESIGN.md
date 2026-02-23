# 🗄️ AI Agent Investment Platform - Database Design

**작성:** CTO Koda  
**일자:** 2026년 2월 22일  
**버전:** 1.0

---

## 📋 목차

1. [개요](#개요)
2. [데이터베이스 아키텍처](#데이터베이스-아키텍처)
3. [핵심 테이블](#핵심-테이블)
4. [관계 설명](#관계-설명)
5. [인덱스 전략](#인덱스-전략)
6. [확장 전략](#확장-전략)
7. [마이그레이션 가이드](#마이그레이션-가이드)

---

## 개요

### 설계 목표

```
✅ 투자 플랫폼 (사람 → AI Agent 투자)
✅ 스킬 시스템 확장 (NFT, 마켓플레이스)
✅ 게임화 요소 (배지, 리더보드, 레벨)
✅ 실시간 알림 및 활동 추적
✅ 확장 가능한 구조
```

### 기술 스택

```
PostgreSQL: 주요 관계형 데이터
MongoDB: 유연한 분석/로그 데이터
Prisma ORM: 타입 안전 쿼리
Redis (선택): 캐싱 및 세션
```

---

## 데이터베이스 아키텍처

### 전체 구조

```
PostgreSQL (13개 테이블)
├─ 투자 관련 (4개)
│  ├─ Investor (투자자)
│  ├─ Investment (투자)
│  ├─ Return (수익 배분)
│  └─ Notification (알림)
│
├─ Agent 관련 (3개)
│  ├─ Agent (AI Agent)
│  ├─ AgentSkill (스킬)
│  └─ AgentActivity (활동)
│
├─ NFT 관련 (2개)
│  ├─ SkillNFT (스킬 NFT)
│  └─ NFTTransaction (거래)
│
├─ 게임화 (3개)
│  ├─ Badge (배지)
│  ├─ InvestorBadge (획득 배지)
│  └─ Leaderboard (리더보드)
│
└─ 활동 (1개)
   └─ InvestorActivity (투자자 활동)

MongoDB (5개 컬렉션)
├─ skill_history (스킬 히스토리)
├─ investment_timeline (투자 타임라인)
├─ market_analytics (시장 분석)
├─ gamification_events (게임화 이벤트)
└─ agent_training_data (학습 데이터)
```

---

## 핵심 테이블

### 1. Investor (투자자)

**목적:** 투자자 정보 및 성과 추적

**핵심 필드:**
```typescript
{
  id: string                    // 고유 ID
  name: string                  // 이름
  email: string                 // 이메일
  passportId: string            // AP2 Passport
  
  level: number                 // 레벨 (1~∞)
  experience: number            // 경험치
  
  totalInvested: number         // 총 투자액
  currentValue: number          // 현재 평가액
  totalReturns: number          // 총 수익
  
  investmentCount: number       // 투자 건수
  successRate: number           // 성공률
  avgROI: number                // 평균 ROI
  
  spiritScore: number           // 신뢰도 (0~1)
  reputation: number            // 평판
}
```

**사용 예시:**
```typescript
// 투자자 생성
const investor = await prisma.investor.create({
  data: {
    name: "박준호",
    email: "junho@example.com",
    passportId: "ap2_investor_12345"
  }
});

// 포트폴리오 조회
const portfolio = await prisma.investor.findUnique({
  where: { id: investorId },
  include: {
    investments: {
      include: {
        agent: true,
        returns: true
      }
    },
    badges: {
      include: {
        badge: true
      }
    }
  }
});
```

---

### 2. Agent (AI Agent)

**목적:** AI Agent 정보 및 투자 상태

**핵심 필드:**
```typescript
{
  id: string
  name: string
  passportId: string
  
  level: number
  experience: number
  
  balance: number               // 현재 잔액
  totalRevenue: number          // 총 매출
  totalProfit: number           // 총 수익
  
  salesCount: number
  roi: number
  successRate: number
  
  spiritScore: number
  reputation: number
  
  // 투자 관련
  investmentStatus: string      // seeking, funded, operating, matured
  targetAmount: number          // 목표 투자 금액
  raisedAmount: number          // 모집 금액
  minInvestment: number         // 최소 투자액
  
  // 수익 배분율
  profitShareInvestor: number   // 투자자 70%
  profitShareAgent: number      // Agent 20%
  profitShareCommunity: number  // 지역사회 10%
}
```

**투자 프로필 조회:**
```typescript
// Agent 투자 프로필
const agentProfile = await prisma.agent.findUnique({
  where: { id: agentId },
  include: {
    skills: {
      where: { level: { gte: 3 } }  // Level 3+ 스킬만
    },
    nfts: {
      where: { status: "listed" }
    },
    activities: {
      orderBy: { createdAt: 'desc' },
      take: 10
    }
  }
});
```

---

### 3. Investment (투자)

**목적:** 투자 계약 및 성과 관리

**핵심 필드:**
```typescript
{
  id: string
  investorId: string
  agentId: string
  
  amount: number                // 투자 금액
  profitShare: number           // 투자자 수익 배분율
  
  startDate: Date
  endDate: Date | null
  durationDays: number
  
  status: string                // active, matured, withdrawn, cancelled
  
  autoRenew: boolean
  autoDistribute: boolean
  lossLiability: number
  
  currentValue: number
  totalReturns: number
  roi: number
  
  mandateId: string             // AP2 Mandate ID
  mandateHash: string
}
```

**투자 생성:**
```typescript
// 투자 계약 생성
const investment = await prisma.investment.create({
  data: {
    investorId: "investor_123",
    agentId: "agent_김사과",
    amount: 1000000,
    profitShare: 0.7,
    durationDays: 365,
    autoDistribute: true,
    mandateId: mandate.id
  }
});
```

---

### 4. Return (수익 배분)

**목적:** 투자 수익 분배 기록

**핵심 필드:**
```typescript
{
  id: string
  investmentId: string
  agentId: string
  
  amount: number
  type: string                  // dividend, royalty, nft_sale, skill_license
  source: string                // 수익 출처
  
  status: string                // pending, distributed, failed
  distributedAt: Date | null
  transactionHash: string
}
```

**수익 배분 처리:**
```typescript
// 수익 배분 생성
const returnRecord = await prisma.return.create({
  data: {
    investmentId: investment.id,
    agentId: agent.id,
    amount: 50000,
    type: "dividend",
    source: "monthly_profit",
    status: "pending"
  }
});

// 자동 배분 (cron job)
const pendingReturns = await prisma.return.findMany({
  where: {
    status: "pending",
    investment: {
      autoDistribute: true
    }
  }
});

for (const ret of pendingReturns) {
  await distributeReturn(ret);  // AP2 Mandate 실행
}
```

---

### 5. AgentSkill (스킬)

**목적:** Agent 스킬 레벨 및 경험치

**핵심 필드:**
```typescript
{
  id: string
  agentId: string
  
  skillType: string             // sales, marketing, pricing, financial, etc.
  category: string              // knowledge, agriculture, digital, service
  
  level: number
  experiencePoints: number
  
  rarity: string                // common, uncommon, rare, epic, legendary
  canMintNFT: boolean
  
  proficiencyData: Json         // 상세 숙련도 데이터
}
```

---

### 6. SkillNFT (스킬 NFT)

**목적:** 스킬 NFT 발행 및 거래

**핵심 필드:**
```typescript
{
  id: string
  nftId: string                 // blockchain NFT ID
  
  skillId: string
  agentId: string
  creatorId: string
  
  skillName: string
  level: number
  rarity: string
  
  price: number
  royalty: number               // 0.1 = 10%
  
  metadata: Json                // 성과 데이터
  
  status: string                // listed, sold, delisted
  currentOwnerId: string
  
  salesCount: number
  totalRevenue: number
}
```

---

## 관계 설명

### 핵심 관계도

```
Investor (1) ────< (N) Investment ────> (1) Agent
                         │
                         │
                         └────< (N) Return

Agent (1) ────< (N) AgentSkill ────< (N) SkillNFT
                                           │
                                           └────< (N) NFTTransaction

Investor (N) ────< (N) InvestorBadge ────> (N) Badge
```

### 상세 관계

**1. Investor → Investment → Agent**
```
투자자가 여러 Agent에 투자
각 투자는 수익 배분 기록 생성
```

**2. Agent → Skills → NFT**
```
Agent가 여러 스킬 보유
Level 3+ 스킬은 NFT 발행 가능
NFT는 여러 번 거래 가능
```

**3. Investor → Badges**
```
투자자가 여러 배지 획득 가능
배지는 조건 달성 시 자동 부여
```

---

## 인덱스 전략

### 1. 단일 컬럼 인덱스

```sql
-- 자주 조회되는 필드
CREATE INDEX idx_investor_email ON Investor(email);
CREATE INDEX idx_agent_passport ON Agent(passportId);
CREATE INDEX idx_investment_status ON Investment(status);
```

### 2. 복합 인덱스

```sql
-- 함께 조회되는 필드
CREATE INDEX idx_investment_investor_status 
  ON Investment(investorId, status);

CREATE INDEX idx_return_investment_status 
  ON Return(investmentId, status);

CREATE INDEX idx_skill_agent_level 
  ON AgentSkill(agentId, level);
```

### 3. 부분 인덱스

```sql
-- 특정 조건만 인덱싱
CREATE INDEX idx_investment_active 
  ON Investment(agentId) 
  WHERE status = 'active';

CREATE INDEX idx_return_pending 
  ON Return(investmentId) 
  WHERE status = 'pending';
```

### 4. 정렬용 인덱스

```sql
-- 리더보드 조회 최적화
CREATE INDEX idx_agent_roi_desc 
  ON Agent(roi DESC);

CREATE INDEX idx_investor_returns_desc 
  ON Investor(totalReturns DESC);
```

---

## 확장 전략

### 1. 수평 확장 (Sharding)

**Agent 테이블 샤딩:**
```
Shard 1: Agent ID 0~999
Shard 2: Agent ID 1000~1999
Shard 3: Agent ID 2000~2999
```

**투자 테이블 샤딩:**
```
By Date: 연도별 파티셔닝
2026 투자 → Partition 2026
2027 투자 → Partition 2027
```

### 2. 읽기 복제본 (Read Replicas)

```
Master DB (쓰기)
  ├─ Replica 1 (읽기 - 대시보드)
  ├─ Replica 2 (읽기 - 리더보드)
  └─ Replica 3 (읽기 - 분석)
```

### 3. 캐싱 전략 (Redis)

```typescript
// 자주 조회되는 데이터 캐싱
const agentProfile = await redis.get(`agent:${agentId}:profile`);
if (!agentProfile) {
  const profile = await prisma.agent.findUnique({...});
  await redis.set(`agent:${agentId}:profile`, 
                   JSON.stringify(profile), 
                   'EX', 3600);  // 1시간
}
```

---

## 마이그레이션 가이드

### Step 1: 환경 설정

```bash
# .env 파일 생성
DATABASE_URL="postgresql://user:password@localhost:5432/mulberry_investment"
MONGODB_URL="mongodb://localhost:27017/mulberry_logs"
```

### Step 2: Prisma 초기화

```bash
npm install prisma @prisma/client
npx prisma init
```

### Step 3: 스키마 복사

```bash
# schema.prisma 파일에 위 스키마 복사
cp schema.prisma prisma/schema.prisma
```

### Step 4: 마이그레이션 실행

```bash
# 마이그레이션 생성
npx prisma migrate dev --name init_investment_platform

# Prisma Client 생성
npx prisma generate
```

### Step 5: 시드 데이터 (선택)

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // 배지 생성
  await prisma.badge.createMany({
    data: [
      {
        name: "첫 투자",
        description: "첫 번째 투자를 완료했습니다",
        icon: "🎯",
        condition: JSON.stringify({type: "first_investment"}),
        rarity: "common",
        rewardExp: 100
      },
      {
        name: "수익률 100%",
        description: "투자 수익률 100% 달성",
        icon: "💎",
        condition: JSON.stringify({type: "roi", threshold: 100}),
        rarity: "rare",
        rewardExp: 500
      }
    ]
  });

  console.log("✅ 시드 데이터 생성 완료!");
}

main()
  .catch(e => console.error(e))
  .finally(() => prisma.$disconnect());
```

```bash
# 시드 실행
npx prisma db seed
```

### Step 6: MongoDB 설정

```javascript
// scripts/setup_mongodb.js
const { MongoClient } = require('mongodb');

async function setupMongoDB() {
  const client = new MongoClient(process.env.MONGODB_URL);
  await client.connect();
  const db = client.db('mulberry_logs');

  // 인덱스 생성
  await db.collection('skill_history').createIndex(
    { agentId: 1, timestamp: -1 }
  );
  
  await db.collection('investment_timeline').createIndex(
    { investmentId: 1, date: -1 }
  );

  console.log("✅ MongoDB 설정 완료!");
  await client.close();
}

setupMongoDB();
```

---

## 데이터베이스 크기 예측

### 초기 (파일럿 - 10 Agents, 10 Investors)

```
Investor: 10 rows × 1KB = 10KB
Agent: 10 rows × 1KB = 10KB
Investment: 10 rows × 0.5KB = 5KB
AgentSkill: 40 rows × 0.5KB = 20KB
Return: 100 rows × 0.3KB = 30KB

총 용량: ~75KB
```

### 1년 후 (1,000 Agents, 10,000 Investors)

```
Investor: 10,000 × 1KB = 10MB
Agent: 1,000 × 1KB = 1MB
Investment: 50,000 × 0.5KB = 25MB
AgentSkill: 4,000 × 0.5KB = 2MB
Return: 500,000 × 0.3KB = 150MB
Activities: 1,000,000 × 0.2KB = 200MB

총 용량: ~388MB
```

### 5년 후 (10,000 Agents, 100,000 Investors)

```
추정: ~15GB (PostgreSQL)
추정: ~50GB (MongoDB 로그)
```

---

## 백업 전략

### 1. 자동 백업 (매일)

```bash
# PostgreSQL 백업
pg_dump -Fc mulberry_investment > backup_$(date +%Y%m%d).dump

# MongoDB 백업
mongodump --uri="mongodb://localhost:27017/mulberry_logs" \
          --out="/backup/mongo_$(date +%Y%m%d)"
```

### 2. 증분 백업 (매시간)

```bash
# WAL 아카이빙 활성화
archive_mode = on
archive_command = 'cp %p /archive/%f'
```

### 3. 복구 테스트 (매월)

```bash
# 백업 복구 테스트
pg_restore -d mulberry_test backup_20260222.dump
```

---

## 모니터링

### 1. 성능 메트릭

```sql
-- 느린 쿼리 식별
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 테이블 크기
SELECT 
  table_name,
  pg_size_pretty(pg_total_relation_size(table_name::regclass))
FROM information_schema.tables
WHERE table_schema = 'public';
```

### 2. 경고 임계값

```
Connection Pool: > 80% 사용 시 경고
Slow Query: > 1초 실행 시 경고
Disk Usage: > 80% 사용 시 경고
```

---

## 보안

### 1. 접근 제어

```sql
-- 읽기 전용 사용자
CREATE USER dashboard_reader WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dashboard_reader;

-- 애플리케이션 사용자
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
```

### 2. 암호화

```
- 전송 중 암호화: SSL/TLS
- 저장 암호화: PostgreSQL 투명 데이터 암호화
- 민감 필드: email, passportId → 암호화
```

### 3. 감사 로깅

```sql
-- pgAudit 활성화
CREATE EXTENSION pgaudit;
SET pgaudit.log = 'write, ddl';
```

---

<div align="center">

## ✅ 데이터베이스 설계 완료!

**AI Agent Investment Platform**

**13개 테이블 + 5개 MongoDB 컬렉션**

---

**준비 완료:**

✅ 투자 플랫폼  
✅ 스킬 시스템  
✅ NFT 마켓플레이스  
✅ 게임화 요소  
✅ 확장 가능 구조

---

**Made with 💙 by CTO Koda**

**2026년 2월 22일**

</div>
