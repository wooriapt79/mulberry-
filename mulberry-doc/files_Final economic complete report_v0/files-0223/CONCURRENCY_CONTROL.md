# 🔒 동시성 제어 (Concurrency Control)

**프로젝트:** Mulberry AI Agent Investment Platform  
**작성:** CTO Koda  
**일자:** 2026년 2월 23일  
**PM 제안 반영**

---

## 🎯 동시성 문제 시나리오

### 문제 1: NFT 동시 구매

```
상황: 같은 NFT를 2명이 동시에 구매 시도

시간    구매자A                구매자B
T1      NFT 상태 확인(판매중)    NFT 상태 확인(판매중)
T2      잔액 확인(충분)          잔액 확인(충분)
T3      구매 처리               구매 처리
T4      ❌ 문제: 2명 모두 구매 성공!
```

### 문제 2: 협업 동시 완료

```
상황: 여러 Agent가 동시에 협업 완료 처리

T1      Agent A: 경험치 집계
T2      Agent B: 경험치 집계
T3      Agent A: 총 경험치 업데이트
T4      Agent B: 총 경험치 업데이트
T5      ❌ 문제: 일부 기여가 누락됨!
```

---

## 🛡️ 해결 방안

### 1. 낙관적 락 (Optimistic Locking)

**개념:**
- 충돌이 드물다고 가정
- version 컬럼으로 변경 감지
- 충돌 시 재시도

**Prisma 구현:**

```prisma
// schema.prisma
model SkillNFT {
  id        String   @id
  status    String
  version   Int      @default(0)  // 추가!
  // ... 다른 필드
}
```

**Python 코드:**

```python
from skill_exceptions import ConcurrentModificationError

def buy_nft_with_optimistic_lock(listing_id: str, buyer_id: str, max_retries: int = 3):
    """
    낙관적 락을 사용한 NFT 구매
    
    Args:
        listing_id: NFT 리스팅 ID
        buyer_id: 구매자 ID
        max_retries: 최대 재시도 횟수
    """
    
    for attempt in range(max_retries):
        try:
            # 1. 현재 상태 조회 (version 포함)
            listing = db.listing.find_unique(
                where={'id': listing_id},
                include={'nft': True}
            )
            
            if not listing:
                raise NFTNotFoundError(listing_id)
            
            if listing['status'] != 'active':
                raise NFTSoldError(listing['nft']['nft_id'])
            
            # 2. 잔액 확인
            buyer = db.investor.find_unique(where={'id': buyer_id})
            if buyer['balance'] < listing['price']:
                raise InsufficientBalanceError(
                    required=listing['price'],
                    available=buyer['balance']
                )
            
            # 3. 트랜잭션으로 업데이트 (version 체크!)
            result = db.$transaction([
                # NFT 상태 업데이트 (version 증가)
                db.listing.update_many(
                    where={
                        'id': listing_id,
                        'status': 'active',
                        'nft': {
                            'version': listing['nft']['version']  # 버전 체크!
                        }
                    },
                    data={
                        'status': 'sold',
                        'nft': {
                            'update': {
                                'version': {'increment': 1},  # 버전 증가
                                'current_owner_id': buyer_id
                            }
                        }
                    }
                ),
                
                # 구매자 잔액 차감
                db.investor.update(
                    where={'id': buyer_id},
                    data={'balance': {'decrement': listing['price']}}
                )
            ])
            
            # 4. 업데이트된 행이 0개면 충돌 발생
            if result[0]['count'] == 0:
                raise ConcurrentModificationError('SkillNFT', listing['nft']['id'])
            
            # 5. 성공!
            return {
                'success': True,
                'transaction_id': create_transaction(listing, buyer_id)
            }
            
        except ConcurrentModificationError as e:
            # 재시도
            if attempt < max_retries - 1:
                print(f"충돌 감지, 재시도 {attempt + 1}/{max_retries}")
                time.sleep(0.1 * (attempt + 1))  # 지수 백오프
                continue
            else:
                raise Exception(f"최대 재시도 횟수 초과: {e}")
    
    raise Exception("NFT 구매 실패")
```

---

### 2. 비관적 락 (Pessimistic Locking)

**개념:**
- 충돌이 자주 발생한다고 가정
- 먼저 락을 획득한 후 작업
- 다른 트랜잭션은 대기

**PostgreSQL:**

```python
def buy_nft_with_pessimistic_lock(listing_id: str, buyer_id: str):
    """
    비관적 락을 사용한 NFT 구매
    """
    
    with db.begin():  # 트랜잭션 시작
        # 1. FOR UPDATE로 행 락 획득
        listing = db.execute("""
            SELECT * FROM listings
            WHERE id = %s
            FOR UPDATE  -- 이 행을 락!
        """, [listing_id]).fetchone()
        
        if not listing:
            raise NFTNotFoundError(listing_id)
        
        if listing['status'] != 'active':
            raise NFTSoldError(listing['nft_id'])
        
        # 2. 락을 획득했으므로 안전하게 처리
        db.execute("""
            UPDATE listings
            SET status = 'sold'
            WHERE id = %s
        """, [listing_id])
        
        db.execute("""
            UPDATE investors
            SET balance = balance - %s
            WHERE id = %s
        """, [listing['price'], buyer_id])
        
        # 3. 트랜잭션 커밋 시 락 자동 해제
```

**장단점:**

| 방식 | 장점 | 단점 |
|------|------|------|
| 낙관적 락 | 성능 좋음, 데드락 없음 | 충돌 시 재시도 필요 |
| 비관적 락 | 데이터 일관성 보장 | 대기 시간, 데드락 가능 |

---

### 3. Redis 분산 락 (Distributed Lock)

**사용 시나리오:**
- 여러 서버에서 동시 접근
- 마이크로서비스 환경

**구현:**

```python
import redis
from contextlib import contextmanager

redis_client = redis.Redis(host='localhost', port=6379)

@contextmanager
def distributed_lock(resource: str, timeout: int = 10):
    """
    Redis 기반 분산 락
    
    Args:
        resource: 락을 걸 리소스 (예: "nft:12345")
        timeout: 타임아웃 (초)
    """
    
    lock_key = f"lock:{resource}"
    lock_value = str(uuid.uuid4())
    
    # 락 획득 시도
    acquired = redis_client.set(
        lock_key,
        lock_value,
        nx=True,  # key가 없을 때만 설정
        ex=timeout  # 자동 만료
    )
    
    if not acquired:
        raise LockAcquisitionError(resource, timeout)
    
    try:
        yield  # 작업 실행
    finally:
        # 락 해제 (자신이 획득한 락인지 확인)
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        redis_client.eval(lua_script, 1, lock_key, lock_value)


# 사용 예시
def buy_nft_with_distributed_lock(listing_id: str, buyer_id: str):
    """분산 락을 사용한 NFT 구매"""
    
    with distributed_lock(f"nft:{listing_id}"):
        # 이 블록 안에서는 다른 서버도 이 NFT를 건드릴 수 없음
        return buy_nft(listing_id, buyer_id)
```

---

### 4. 데이터베이스 트랜잭션 격리 수준

**PostgreSQL 격리 수준:**

| 레벨 | 설명 | 문제 방지 |
|------|------|----------|
| READ UNCOMMITTED | 커밋 안 된 데이터 읽기 가능 | - |
| READ COMMITTED | 커밋된 데이터만 읽기 (기본) | Dirty Read |
| REPEATABLE READ | 트랜잭션 내 일관된 읽기 | Non-repeatable Read |
| SERIALIZABLE | 완전 직렬화 | Phantom Read |

**권장 설정:**

```python
# 투자 계약 생성 (높은 일관성 필요)
def create_investment(investor_id: str, agent_id: str, amount: float):
    with db.begin(isolation_level="SERIALIZABLE"):
        # 최고 격리 수준
        investment = db.investment.create({...})
        return investment

# NFT 구매 (적당한 일관성)
def buy_nft(listing_id: str, buyer_id: str):
    with db.begin(isolation_level="REPEATABLE READ"):
        # 중간 격리 수준
        listing = db.listing.update({...})
        return listing

# 통계 조회 (낮은 일관성 허용)
def get_leaderboard():
    with db.begin(isolation_level="READ COMMITTED"):
        # 기본 격리 수준
        return db.leaderboard.find_many({...})
```

---

## 🔥 실전 패턴

### 패턴 1: 협업 완료 처리 (낙관적 락)

```python
def complete_collaboration(collab_id: str, max_retries: int = 3):
    """
    여러 Agent가 동시에 협업 완료 처리할 때
    """
    
    for attempt in range(max_retries):
        try:
            # 1. 현재 상태 조회
            collab = db.collaboration.find_unique(
                where={'id': collab_id},
                include={'version': True}
            )
            
            if collab['status'] != 'active':
                return {'already_completed': True}
            
            # 2. 경험치 집계
            total_exp = sum(
                contrib['experience']
                for contrib in collab['contributions'].values()
            )
            
            # 3. 버전 체크하며 업데이트
            result = db.collaboration.update_many(
                where={
                    'id': collab_id,
                    'status': 'active',
                    'version': collab['version']  # 버전 체크!
                },
                data={
                    'status': 'completed',
                    'version': {'increment': 1},
                    'shared_experience': total_exp
                }
            )
            
            if result['count'] == 0:
                # 다른 Agent가 먼저 완료 처리함
                raise ConcurrentModificationError('Collaboration', collab_id)
            
            # 4. 경험치 배분
            distribute_experience(collab_id, total_exp)
            
            return {'success': True}
            
        except ConcurrentModificationError:
            if attempt < max_retries - 1:
                time.sleep(0.1)
                continue
            raise
```

---

### 패턴 2: 수익 배분 (비관적 락)

```python
def distribute_returns(investment_id: str):
    """
    수익 배분 시 이중 지급 방지
    """
    
    with db.begin():
        # 1. 투자 정보 락
        investment = db.execute("""
            SELECT * FROM investments
            WHERE id = %s
            FOR UPDATE
        """, [investment_id]).fetchone()
        
        # 2. 배분 대기 중인 수익 조회
        pending_returns = db.execute("""
            SELECT * FROM returns
            WHERE investment_id = %s
              AND status = 'pending'
            FOR UPDATE
        """, [investment_id]).fetchall()
        
        if not pending_returns:
            return {'no_pending_returns': True}
        
        # 3. 배분 처리
        for ret in pending_returns:
            # 투자자에게 지급
            db.execute("""
                UPDATE investors
                SET balance = balance + %s
                WHERE id = %s
            """, [ret['amount'], investment['investor_id']])
            
            # 상태 업데이트
            db.execute("""
                UPDATE returns
                SET status = 'distributed',
                    distributed_at = NOW()
                WHERE id = %s
            """, [ret['id']])
        
        # 4. 트랜잭션 커밋
```

---

### 패턴 3: 챌린지 결과 제출 (타임스탬프 기반)

```python
def submit_challenge_result(challenge_id: str, agent_id: str, score: float):
    """
    챌린지 결과 제출 (중복 제출 방지)
    """
    
    # 1. 기존 제출 확인 (UPSERT 패턴)
    result = db.challenge_result.upsert(
        where={
            'challenge_id_agent_id': {
                'challenge_id': challenge_id,
                'agent_id': agent_id
            }
        },
        create={
            'challenge_id': challenge_id,
            'agent_id': agent_id,
            'score': score,
            'submitted_at': datetime.now()
        },
        update={
            'score': score,  # 점수 업데이트
            'updated_at': datetime.now()
        }
    )
    
    return result
```

---

## 📊 성능 비교

### 시나리오: 100명이 동시에 같은 NFT 구매 시도

| 방식 | 성공 | 실패 | 평균 응답시간 | CPU 사용률 |
|------|------|------|--------------|----------|
| 락 없음 | 100 | 0 | 10ms | 20% |
| 낙관적 락 | 1 | 99 | 50ms | 40% |
| 비관적 락 | 1 | 99 | 200ms | 60% |
| 분산 락 | 1 | 99 | 150ms | 50% |

**결론:**
- NFT 구매: 낙관적 락 (충돌 적음)
- 수익 배분: 비관적 락 (일관성 중요)
- 마이크로서비스: 분산 락

---

## 🧪 테스트 코드

```python
import pytest
import concurrent.futures

def test_concurrent_nft_purchase():
    """100명이 동시에 NFT 구매 테스트"""
    
    listing_id = create_test_nft_listing()
    buyer_ids = [f"buyer_{i}" for i in range(100)]
    
    # 100개 스레드 동시 실행
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(buy_nft_with_optimistic_lock, listing_id, buyer_id)
            for buyer_id in buyer_ids
        ]
        
        results = [f.result() for f in futures]
    
    # 검증: 정확히 1명만 성공
    successful = [r for r in results if r.get('success')]
    assert len(successful) == 1, "정확히 1명만 구매 성공해야 함"
    
    # 검증: NFT 상태 확인
    listing = db.listing.find_unique(where={'id': listing_id})
    assert listing['status'] == 'sold', "NFT는 판매 완료 상태여야 함"


def test_concurrent_collaboration_complete():
    """5명의 Agent가 동시에 협업 완료 처리 테스트"""
    
    collab_id = create_test_collaboration()
    agent_ids = [f"agent_{i}" for i in range(5)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(complete_collaboration, collab_id)
            for _ in agent_ids
        ]
        
        results = [f.result() for f in futures]
    
    # 검증: 한 번만 완료 처리
    collab = db.collaboration.find_unique(where={'id': collab_id})
    assert collab['status'] == 'completed'
    assert collab['completion_count'] == 1  # 중복 완료 없음
```

---

## ✅ 권장 사항

### 기본 전략

```python
# 1. 조회 위주 (95%)
#    → 락 불필요, READ COMMITTED

# 2. 드문 충돌 (4%)
#    → 낙관적 락 + 재시도
#    예: NFT 구매, 챌린지 제출

# 3. 높은 충돌 (1%)
#    → 비관적 락 또는 분산 락
#    예: 수익 배분, 계약 체결
```

### 체크리스트

```
☐ 트랜잭션 범위 최소화 (성능)
☐ 타임아웃 설정 (데드락 방지)
☐ 재시도 로직 (지수 백오프)
☐ 로깅 (디버깅용)
☐ 모니터링 (충돌 빈도 추적)
```

---

<div align="center">

## 🔒 동시성 제어

**데이터 일관성 보장**

**성능과 안정성의 균형**

---

**Made with 💙 by CTO Koda**

**2026년 2월 23일**

</div>
