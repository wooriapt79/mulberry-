"""
Mulberry Phase 1 - Qwen 2.5 Service
비정형 텍스트를 정규화된 JSON으로 변환하는 AI 서비스
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from app.config import settings


class QwenService:
    """
    Qwen 2.5 API 연동 서비스
    재고 게시물의 비정형 텍스트를 구조화된 데이터로 변환
    """
    
    def __init__(self):
        """Qwen API 클라이언트 초기화"""
        self.api_key = settings.qwen_api_key
        self.api_base_url = settings.qwen_api_base_url
        self.model = settings.qwen_model
        self.timeout = settings.qwen_timeout_seconds
        
        # HTTP 클라이언트 (비동기)
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        logger.info(f"✅ Qwen service initialized: {self.model}")
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def extract_inventory_data(
        self,
        raw_text: str,
        mastodon_handle: str,
        post_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        재고 게시물 텍스트에서 구조화된 데이터 추출
        
        Args:
            raw_text: 마스토돈 게시물 원본 텍스트
            mastodon_handle: 작성자 마스토돈 핸들
            post_metadata: 게시물 메타데이터 (날짜, URL 등)
            
        Returns:
            dict: 정규화된 재고 데이터 (JSON)
        """
        try:
            # 프롬프트 생성
            prompt = self._build_extraction_prompt(
                raw_text=raw_text,
                mastodon_handle=mastodon_handle,
                post_metadata=post_metadata
            )
            
            # Qwen API 호출
            response = await self._call_qwen_api(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction specialist for agricultural inventory management. Extract structured data from Korean text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # 낮은 온도로 일관성 있는 출력
                response_format={"type": "json_object"}  # JSON 모드
            )
            
            # 응답 파싱
            extracted_data = self._parse_qwen_response(response)
            
            logger.info(f"✅ Data extracted: {extracted_data.get('product_name', 'N/A')}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Qwen extraction failed: {str(e)}")
            # 실패 시 기본 구조 반환
            return self._create_fallback_data(raw_text, mastodon_handle)
    
    def _build_extraction_prompt(
        self,
        raw_text: str,
        mastodon_handle: str,
        post_metadata: Optional[Dict] = None
    ) -> str:
        """
        Qwen용 프롬프트 생성
        
        Returns:
            str: 완성된 프롬프트
        """
        prompt = f"""
다음은 농산물 재고를 알리는 마스토돈 게시물입니다. 
이 텍스트에서 재고 정보를 추출하여 JSON 형식으로 반환하세요.

【게시물 정보】
- 작성자: {mastodon_handle}
- 내용: {raw_text}
{f"- 작성 시간: {post_metadata.get('created_at')}" if post_metadata else ""}

【추출 규칙】
1. product_name: 상품명 (예: 사과, 배추, 감자)
2. category: 카테고리 (과일, 채소, 육류, 유제품, 곡물, 기타 중 하나)
3. quantity: 수량 (숫자만, 예: 100)
4. unit: 단위 (kg, 개, 박스, 포기 등)
5. price_per_unit: 단가 (원 단위, 숫자만)
6. total_price: 총액 (원 단위, 숫자만)
7. harvest_date: 수확일 (YYYY-MM-DD 형식, 없으면 null)
8. expiry_date: 유통기한 (YYYY-MM-DD 형식, 없으면 null)
9. quality_grade: 품질 등급 (A, B, C, 특, 상, 중, 하 등, 없으면 null)
10. description: 상품 설명 (간단히 요약)
11. region: 생산 지역 (시/군/구 단위, 없으면 null)

【출력 형식】
반드시 다음과 같은 JSON 형식으로 반환하세요:
{{
    "product_name": "상품명",
    "category": "카테고리",
    "quantity": 100,
    "unit": "단위",
    "price_per_unit": 5000,
    "total_price": 500000,
    "harvest_date": "2024-02-10",
    "expiry_date": null,
    "quality_grade": "A",
    "description": "설명",
    "region": "지역"
}}

【주의사항】
- 숫자는 반드시 숫자 타입으로 (따옴표 없이)
- 정보가 없는 필드는 null
- 날짜는 YYYY-MM-DD 형식
- 가격에서 "원", "만원" 등의 단위 제거
- 수량과 단가를 구분하여 추출

JSON만 반환하고 다른 설명은 추가하지 마세요.
"""
        return prompt.strip()
    
    async def _call_qwen_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Qwen API 호출 (OpenAI 호환 포맷)
        
        Args:
            messages: 대화 메시지 목록
            temperature: 샘플링 온도
            max_tokens: 최대 토큰 수
            response_format: 응답 형식 (JSON 모드 등)
            
        Returns:
            dict: API 응답
        """
        endpoint = f"{self.api_base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # JSON 모드 활성화 (지원하는 경우)
        if response_format:
            payload["response_format"] = response_format
        
        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Qwen API response: {data}")
            
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Qwen API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"❌ Qwen API request error: {str(e)}")
            raise
    
    def _parse_qwen_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qwen API 응답에서 JSON 데이터 추출
        
        Args:
            response: Qwen API 응답
            
        Returns:
            dict: 추출된 재고 데이터
        """
        try:
            # OpenAI 호환 응답 구조
            content = response["choices"][0]["message"]["content"]
            
            # JSON 파싱
            data = json.loads(content)
            
            # 데이터 검증 및 타입 변환
            normalized_data = {
                "product_name": data.get("product_name", "알 수 없음"),
                "category": data.get("category"),
                "quantity": self._to_float(data.get("quantity")),
                "unit": data.get("unit"),
                "price_per_unit": self._to_float(data.get("price_per_unit")),
                "total_price": self._to_float(data.get("total_price")),
                "harvest_date": self._to_date(data.get("harvest_date")),
                "expiry_date": self._to_date(data.get("expiry_date")),
                "quality_grade": data.get("quality_grade"),
                "description": data.get("description"),
                "region": data.get("region"),
                "extracted_at": datetime.now().isoformat(),
                "extraction_confidence": "high"  # 향후 신뢰도 점수 추가 가능
            }
            
            # total_price가 없으면 계산
            if not normalized_data["total_price"] and normalized_data["quantity"] and normalized_data["price_per_unit"]:
                normalized_data["total_price"] = normalized_data["quantity"] * normalized_data["price_per_unit"]
            
            return normalized_data
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"❌ Failed to parse Qwen response: {str(e)}")
            raise
    
    def _create_fallback_data(
        self,
        raw_text: str,
        mastodon_handle: str
    ) -> Dict[str, Any]:
        """
        API 실패 시 기본 데이터 생성
        
        Args:
            raw_text: 원본 텍스트
            mastodon_handle: 작성자 핸들
            
        Returns:
            dict: 기본 구조 데이터
        """
        return {
            "product_name": "수동 확인 필요",
            "category": None,
            "quantity": None,
            "unit": None,
            "price_per_unit": None,
            "total_price": None,
            "harvest_date": None,
            "expiry_date": None,
            "quality_grade": None,
            "description": raw_text[:200],  # 처음 200자만
            "region": None,
            "extracted_at": datetime.now().isoformat(),
            "extraction_confidence": "failed",
            "error": "Qwen API 호출 실패 또는 파싱 오류"
        }
    
    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        """값을 float으로 안전하게 변환"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _to_date(value: Any) -> Optional[str]:
        """날짜 문자열 검증 (YYYY-MM-DD 형식)"""
        if not value:
            return None
        
        # 간단한 날짜 형식 검증
        try:
            datetime.strptime(str(value), "%Y-%m-%d")
            return str(value)
        except ValueError:
            return None
    
    async def generate_hot_deal_proposal(
        self,
        inventory_items: List[Dict[str, Any]],
        target_category: str
    ) -> Dict[str, Any]:
        """
        재고 데이터를 기반으로 공동구매 제안 생성 (Market Orchestrator용)
        
        Args:
            inventory_items: 재고 아이템 목록
            target_category: 대상 카테고리
            
        Returns:
            dict: 핫딜 제안 정보
        """
        try:
            # 프롬프트 생성
            items_summary = "\n".join([
                f"- {item['product_name']} ({item['quantity']}{item['unit']}) @ {item['price_per_unit']}원/{item['unit']}"
                for item in inventory_items[:10]  # 최대 10개
            ])
            
            prompt = f"""
다음은 {target_category} 카테고리의 재고 데이터입니다.
이를 바탕으로 효과적인 공동구매(핫딜) 제안을 생성하세요.

【재고 현황】
{items_summary}

【핫딜 제안 요구사항】
1. deal_name: 매력적인 핫딜 이름
2. description: 핫딜 설명 (2-3문장)
3. target_quantity: 목표 수량 (단위 포함)
4. min_quantity: 최소 수량
5. discount_rate: 권장 할인율 (%)
6. duration_days: 모집 기간 (일)

JSON 형식으로 반환하세요:
{{
    "deal_name": "핫딜 이름",
    "description": "설명",
    "target_quantity": 1000,
    "min_quantity": 500,
    "discount_rate": 15,
    "duration_days": 7
}}
"""
            
            response = await self._call_qwen_api(
                messages=[
                    {"role": "system", "content": "You are a marketing specialist for agricultural group purchases."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response["choices"][0]["message"]["content"]
            proposal = json.loads(content)
            
            logger.info(f"✅ Hot deal proposal generated: {proposal.get('deal_name')}")
            return proposal
            
        except Exception as e:
            logger.error(f"❌ Failed to generate hot deal proposal: {str(e)}")
            return {
                "deal_name": f"{target_category} 공동구매",
                "description": "재고 정리를 위한 특별 할인",
                "target_quantity": 1000,
                "min_quantity": 500,
                "discount_rate": 10,
                "duration_days": 7
            }


# ============================================
# 싱글톤 인스턴스
# ============================================

_qwen_service_instance: Optional[QwenService] = None


def get_qwen_service() -> QwenService:
    """
    싱글톤 Qwen 서비스 인스턴스 반환
    
    Returns:
        QwenService: 서비스 인스턴스
    """
    global _qwen_service_instance
    
    if _qwen_service_instance is None:
        _qwen_service_instance = QwenService()
    
    return _qwen_service_instance


# ============================================
# 테스트용 메인 함수
# ============================================

async def test_qwen():
    """Qwen 서비스 테스트"""
    service = get_qwen_service()
    
    # 테스트 데이터
    test_text = """
    🍎 신선한 사과 판매합니다! 🍎
    
    품목: 홍로 사과
    수량: 500kg (20kg 박스 25개)
    가격: 박스당 35,000원
    등급: 특품
    수확일: 2024년 2월 5일
    
    강원도 인제군에서 직접 재배한 사과입니다.
    #Mulberry_재고 #사과 #강원도
    """
    
    result = await service.extract_inventory_data(
        raw_text=test_text,
        mastodon_handle="@test_farm@mastodon.social",
        post_metadata={"created_at": "2024-02-10T10:00:00Z"}
    )
    
    logger.info(f"Extraction result:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
    
    await service.close()


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    asyncio.run(test_qwen())
