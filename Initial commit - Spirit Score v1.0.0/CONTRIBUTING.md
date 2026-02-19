# Contributing to Spirit Score System

감사합니다! Mulberry Spirit Score 시스템에 기여해주셔서 감사합니다.

## 개발 환경 설정

### 1. 저장소 클론
```bash
git clone https://github.com/mulberry-project/spirit-score.git
cd spirit-score
```

### 2. 가상 환경 생성
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구
```

### 4. 데이터베이스 설정
```bash
./scripts/setup_db.sh
```

## 코딩 규칙

### Python 스타일
- **PEP 8** 준수
- **Black** 포매터 사용
- **isort** import 정렬
- 최대 줄 길이: 100자

### 코드 포맷팅
```bash
# 포맷팅
black src/ tests/
isort src/ tests/

# 검사
flake8 src/ tests/
```

### 타입 힌트
```python
from typing import Dict, List, Optional

def calculate_score(user_id: str, activity_type: str) -> float:
    ...
```

## Git Workflow

### 브랜치 전략
```
main        # 프로덕션
  └─ develop    # 개발
       ├─ feature/new-feature
       ├─ fix/bug-fix
       └─ refactor/improvement
```

### 커밋 메시지
```
feat: Add GitHub webhook integration
fix: Correct Spirit Score calculation
docs: Update API documentation
test: Add activity tracker tests
refactor: Improve database queries
```

### Pull Request
1. `develop` 브랜치에서 새 브랜치 생성
2. 작업 완료 후 `develop`로 PR
3. 코드 리뷰 완료 후 머지
4. CI/CD 통과 필수

## 테스트

### 테스트 실행
```bash
# 전체 테스트
pytest tests/

# 특정 테스트
pytest tests/test_spirit_score.py

# 커버리지
pytest --cov=src --cov-report=html
```

### 테스트 작성
```python
def test_activity_recording():
    """Test that activities are recorded correctly"""
    # Arrange
    user_id = "test-user"
    activity_type = "daily_login"
    
    # Act
    result = engine.record_activity(user_id, activity_type)
    
    # Assert
    assert result['score_change'] == 0.01
```

## 문서화

### Docstring
```python
def record_activity(user_id: str, activity_type: str) -> Dict:
    """
    활동 기록 및 점수 업데이트
    
    Args:
        user_id: 사용자 ID
        activity_type: 활동 유형
    
    Returns:
        활동 기록 결과
    
    Raises:
        ValueError: 잘못된 activity_type
    """
    ...
```

### README 업데이트
새로운 기능 추가 시 README.md 업데이트 필수

## 코드 리뷰

### 리뷰어 체크리스트
- [ ] 코드가 의도한 대로 작동하는가?
- [ ] 테스트가 충분한가?
- [ ] 문서화가 되어 있는가?
- [ ] 보안 이슈는 없는가?
- [ ] 성능에 영향은 없는가?

### 작성자 체크리스트
- [ ] 테스트 작성 완료
- [ ] 문서화 완료
- [ ] CI/CD 통과
- [ ] 코드 포맷팅 완료
- [ ] 변경 사항 README 반영

## Spirit Score 철학

우리의 코드는 우리의 철학을 반영합니다:

### 투명성
- 모든 점수 변화는 기록됩니다
- 명확한 이유가 있어야 합니다

### 상부상조
- 코드 리뷰로 서로 돕습니다
- 문서화로 지식을 공유합니다

### 책임감
- 테스트로 품질을 보장합니다
- 리뷰 코멘트에 성실히 응답합니다

## 질문이 있으신가요?

- **이슈**: GitHub Issues에 등록
- **토론**: GitHub Discussions
- **긴급**: Slack #dev-spirit-score

## 감사합니다!

모든 기여에 감사드립니다. 함께 더 나은 시스템을 만들어갑시다! 🌾
