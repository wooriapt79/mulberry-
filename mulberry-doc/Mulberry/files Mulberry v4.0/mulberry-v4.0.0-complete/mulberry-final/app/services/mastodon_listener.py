"""
Mulberry Phase 1 - Mastodon Listener Service
마스토돈 API를 통한 실시간 #Mulberry_재고 태그 리스닝
"""

import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime
from mastodon import Mastodon, StreamListener, MastodonError
from loguru import logger

from app.config import settings
from app.services.qwen_service import QwenService


class MulberryStreamListener(StreamListener):
    """
    Mastodon 스트림 리스너
    해시태그가 포함된 게시물을 실시간으로 캐치
    """
    
    def __init__(
        self,
        on_inventory_post: Optional[Callable] = None,
        qwen_service: Optional[QwenService] = None
    ):
        """
        Args:
            on_inventory_post: 재고 게시물 발견 시 호출할 콜백 함수
            qwen_service: Qwen 서비스 인스턴스 (텍스트 정규화용)
        """
        self.on_inventory_post = on_inventory_post
        self.qwen_service = qwen_service or QwenService()
        self.processed_posts = set()  # 중복 처리 방지
    
    def on_update(self, status):
        """
        새로운 게시물이 수신되었을 때 호출
        
        Args:
            status: Mastodon 게시물 객체
        """
        try:
            post_id = str(status['id'])
            
            # 중복 처리 방지
            if post_id in self.processed_posts:
                return
            
            self.processed_posts.add(post_id)
            
            # 게시물 정보 추출
            content = status.get('content', '')
            account = status.get('account', {})
            created_at = status.get('created_at')
            tags = [tag.get('name', '') for tag in status.get('tags', [])]
            
            logger.info(f"📨 New post detected: {post_id} from @{account.get('acct')}")
            
            # 관심 해시태그 확인
            target_hashtags = [tag.replace('#', '') for tag in settings.mastodon_hashtags_list]
            
            if any(tag in target_hashtags for tag in tags):
                logger.info(f"✅ Inventory post found: {tags}")
                
                # 게시물 데이터 구조화
                post_data = {
                    'post_id': post_id,
                    'mastodon_handle': f"@{account.get('acct')}",
                    'account_id': account.get('id'),
                    'display_name': account.get('display_name'),
                    'content': content,
                    'raw_text': self._extract_text(content),
                    'tags': tags,
                    'created_at': created_at,
                    'url': status.get('url'),
                    'visibility': status.get('visibility'),
                    'language': status.get('language'),
                }
                
                # 콜백 함수 호출 (비동기 처리)
                if self.on_inventory_post:
                    asyncio.create_task(self.on_inventory_post(post_data))
                
        except Exception as e:
            logger.error(f"❌ Error processing post: {str(e)}")
    
    def on_notification(self, notification):
        """알림 수신 시 호출"""
        logger.debug(f"Notification received: {notification.get('type')}")
    
    def on_delete(self, status_id):
        """게시물 삭제 시 호출"""
        logger.info(f"Post deleted: {status_id}")
        self.processed_posts.discard(str(status_id))
    
    def on_abort(self, err):
        """스트림 중단 시 호출"""
        logger.warning(f"⚠️ Stream aborted: {err}")
    
    @staticmethod
    def _extract_text(html_content: str) -> str:
        """
        HTML 태그 제거하여 순수 텍스트 추출
        
        Args:
            html_content: HTML 형식의 게시물 내용
            
        Returns:
            str: 순수 텍스트
        """
        import re
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', html_content)
        # HTML 엔티티 변환
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return text.strip()


class MastodonListenerService:
    """
    Mastodon 리스너 서비스 (메인 관리 클래스)
    """
    
    def __init__(self):
        """Mastodon 클라이언트 초기화"""
        self.client: Optional[Mastodon] = None
        self.listener: Optional[MulberryStreamListener] = None
        self._setup_client()
    
    def _setup_client(self):
        """Mastodon 클라이언트 설정"""
        try:
            self.client = Mastodon(
                client_id=settings.mastodon_client_id,
                client_secret=settings.mastodon_client_secret,
                access_token=settings.mastodon_access_token,
                api_base_url=settings.mastodon_instance_url,
                request_timeout=30
            )
            logger.info(f"✅ Mastodon client initialized: {settings.mastodon_instance_url}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Mastodon client: {str(e)}")
            raise
    
    def verify_credentials(self) -> Dict[str, Any]:
        """
        인증 정보 확인
        
        Returns:
            dict: 계정 정보
        """
        try:
            account = self.client.account_verify_credentials()
            logger.info(f"✅ Authenticated as @{account['acct']}")
            return {
                'id': account['id'],
                'username': account['username'],
                'acct': account['acct'],
                'display_name': account['display_name'],
                'followers_count': account['followers_count'],
                'following_count': account['following_count'],
            }
        except MastodonError as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            raise
    
    async def start_listening(
        self,
        on_inventory_post: Callable,
        qwen_service: Optional[QwenService] = None
    ):
        """
        해시태그 스트림 리스닝 시작
        
        Args:
            on_inventory_post: 재고 게시물 발견 시 호출할 콜백
            qwen_service: Qwen 서비스 인스턴스
        """
        self.listener = MulberryStreamListener(
            on_inventory_post=on_inventory_post,
            qwen_service=qwen_service
        )
        
        # 해시태그 목록 (첫 번째 태그로 스트림 시작)
        primary_tag = settings.mastodon_hashtags_list[0].replace('#', '')
        
        logger.info(f"🎧 Starting hashtag stream: #{primary_tag}")
        
        try:
            # 해시태그 타임라인 스트리밍
            self.client.stream_hashtag(
                tag=primary_tag,
                listener=self.listener,
                reconnect_async=True,
                reconnect_async_wait_sec=settings.mastodon_stream_reconnect_wait_sec
            )
        except KeyboardInterrupt:
            logger.info("⏹️ Stream stopped by user")
        except Exception as e:
            logger.error(f"❌ Stream error: {str(e)}")
            raise
    
    def stop_listening(self):
        """스트림 리스닝 중단"""
        if self.listener:
            logger.info("⏹️ Stopping Mastodon stream...")
            # Mastodon.py의 스트림은 별도 중단 메서드가 없으므로
            # 프로세스 종료로 처리
    
    def fetch_recent_posts(
        self,
        hashtag: Optional[str] = None,
        limit: int = 20
    ) -> list:
        """
        최근 해시태그 게시물 수동 조회 (초기 데이터 수집용)
        
        Args:
            hashtag: 조회할 해시태그 (기본값: 설정의 첫 번째 태그)
            limit: 조회할 게시물 수
            
        Returns:
            list: 게시물 목록
        """
        if not hashtag:
            hashtag = settings.mastodon_hashtags_list[0].replace('#', '')
        
        try:
            timeline = self.client.timeline_hashtag(
                hashtag=hashtag,
                limit=limit
            )
            
            logger.info(f"📥 Fetched {len(timeline)} posts with #{hashtag}")
            
            # 데이터 정규화
            posts = []
            for status in timeline:
                account = status.get('account', {})
                posts.append({
                    'post_id': str(status['id']),
                    'mastodon_handle': f"@{account.get('acct')}",
                    'content': status.get('content', ''),
                    'raw_text': MulberryStreamListener._extract_text(status.get('content', '')),
                    'tags': [tag.get('name', '') for tag in status.get('tags', [])],
                    'created_at': status.get('created_at'),
                    'url': status.get('url'),
                })
            
            return posts
            
        except MastodonError as e:
            logger.error(f"❌ Failed to fetch posts: {str(e)}")
            return []
    
    def post_status(
        self,
        content: str,
        visibility: str = "public"
    ) -> Optional[Dict]:
        """
        게시물 작성 (AI 에이전트가 사용)
        
        Args:
            content: 게시물 내용
            visibility: 공개 범위 (public, unlisted, private, direct)
            
        Returns:
            dict: 작성된 게시물 정보
        """
        try:
            status = self.client.status_post(
                status=content,
                visibility=visibility
            )
            
            logger.info(f"📤 Posted status: {status['id']}")
            return {
                'post_id': str(status['id']),
                'url': status['url'],
                'created_at': status['created_at'],
            }
            
        except MastodonError as e:
            logger.error(f"❌ Failed to post status: {str(e)}")
            return None


# ============================================
# Singleton Instance
# ============================================

_mastodon_service_instance: Optional[MastodonListenerService] = None


def get_mastodon_service() -> MastodonListenerService:
    """
    싱글톤 Mastodon 서비스 인스턴스 반환
    
    Returns:
        MastodonListenerService: 서비스 인스턴스
    """
    global _mastodon_service_instance
    
    if _mastodon_service_instance is None:
        _mastodon_service_instance = MastodonListenerService()
    
    return _mastodon_service_instance


# ============================================
# 테스트용 메인 함수
# ============================================

async def test_listener():
    """테스트용 리스너"""
    
    async def on_post_received(post_data):
        logger.info(f"🎯 Inventory post received: {post_data['mastodon_handle']}")
        logger.info(f"Content: {post_data['raw_text'][:100]}...")
    
    service = get_mastodon_service()
    
    # 인증 확인
    account = service.verify_credentials()
    logger.info(f"Logged in as: {account['display_name']} (@{account['acct']})")
    
    # 최근 게시물 조회
    recent = service.fetch_recent_posts(limit=5)
    logger.info(f"Recent posts: {len(recent)}")
    
    # 스트림 리스닝 시작
    await service.start_listening(on_inventory_post=on_post_received)


if __name__ == "__main__":
    # 테스트 실행
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    try:
        asyncio.run(test_listener())
    except KeyboardInterrupt:
        logger.info("
Test stopped by user")
        sys.exit(0)
