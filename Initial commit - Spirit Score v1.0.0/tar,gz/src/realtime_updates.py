"""
Real-time Spirit Score Updates
CTO Koda

Redis Pub/Sub을 사용한 실시간 점수 업데이트
"""

import redis
import json
from typing import Dict, Callable
import asyncio


class SpiritScoreRealtime:
    """
    실시간 Spirit Score 업데이트 시스템
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        """
        Args:
            redis_host: Redis 호스트
            redis_port: Redis 포트
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        
        # 채널 정의
        self.CHANNELS = {
            'score_update': 'spirit_score:updates',
            'activity': 'spirit_score:activities',
            'leaderboard': 'spirit_score:leaderboard',
            'notifications': 'spirit_score:notifications'
        }
    
    # ============================================
    # 점수 업데이트 발행
    # ============================================
    
    def publish_score_update(
        self, 
        user_id: str, 
        username: str,
        old_score: float, 
        new_score: float,
        activity_type: str
    ):
        """
        Spirit Score 업데이트 발행
        
        Args:
            user_id: 사용자 ID
            username: 사용자 이름
            old_score: 이전 점수
            new_score: 새 점수
            activity_type: 활동 유형
        """
        message = {
            'event': 'score_updated',
            'user_id': user_id,
            'username': username,
            'old_score': old_score,
            'new_score': new_score,
            'score_change': new_score - old_score,
            'activity_type': activity_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self.redis_client.publish(
            self.CHANNELS['score_update'],
            json.dumps(message)
        )
        
        # Redis에 최신 점수 캐싱
        self._cache_user_score(user_id, username, new_score)
    
    def publish_activity(
        self, 
        user_id: str,
        username: str,
        activity_type: str,
        activity_data: Dict
    ):
        """
        활동 발행
        
        Args:
            user_id: 사용자 ID
            username: 사용자 이름
            activity_type: 활동 유형
            activity_data: 활동 데이터
        """
        message = {
            'event': 'activity_recorded',
            'user_id': user_id,
            'username': username,
            'activity_type': activity_type,
            'activity_data': activity_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.redis_client.publish(
            self.CHANNELS['activity'],
            json.dumps(message)
        )
    
    def publish_leaderboard_update(self, leaderboard: list):
        """
        리더보드 업데이트 발행
        
        Args:
            leaderboard: 리더보드 데이터
        """
        message = {
            'event': 'leaderboard_updated',
            'leaderboard': leaderboard,
            'timestamp': datetime.now().isoformat()
        }
        
        self.redis_client.publish(
            self.CHANNELS['leaderboard'],
            json.dumps(message)
        )
        
        # Redis에 리더보드 캐싱
        self.redis_client.setex(
            'spirit_score:leaderboard:cache',
            3600,  # 1시간
            json.dumps(leaderboard)
        )
    
    def publish_notification(
        self, 
        user_id: str,
        notification_type: str,
        message: str,
        data: Dict = None
    ):
        """
        알림 발행
        
        Args:
            user_id: 사용자 ID
            notification_type: 알림 유형
            message: 알림 메시지
            data: 추가 데이터
        """
        notification = {
            'event': 'notification',
            'user_id': user_id,
            'type': notification_type,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.redis_client.publish(
            self.CHANNELS['notifications'],
            json.dumps(notification)
        )
    
    # ============================================
    # 캐싱
    # ============================================
    
    def _cache_user_score(self, user_id: str, username: str, score: float):
        """
        사용자 점수 캐싱
        """
        key = f'spirit_score:user:{user_id}'
        data = {
            'user_id': user_id,
            'username': username,
            'score': score,
            'cached_at': datetime.now().isoformat()
        }
        
        self.redis_client.setex(
            key,
            3600,  # 1시간
            json.dumps(data)
        )
    
    def get_cached_user_score(self, user_id: str) -> Dict:
        """
        캐시된 사용자 점수 조회
        
        Returns:
            사용자 점수 데이터 (캐시 없으면 None)
        """
        key = f'spirit_score:user:{user_id}'
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    def get_cached_leaderboard(self) -> list:
        """
        캐시된 리더보드 조회
        
        Returns:
            리더보드 데이터 (캐시 없으면 None)
        """
        data = self.redis_client.get('spirit_score:leaderboard:cache')
        
        if data:
            return json.loads(data)
        return None
    
    # ============================================
    # 구독 (Subscribe)
    # ============================================
    
    def subscribe_to_updates(self, callback: Callable):
        """
        점수 업데이트 구독
        
        Args:
            callback: 메시지 수신 시 호출할 함수
        """
        self.pubsub.subscribe(self.CHANNELS['score_update'])
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                callback(data)
    
    def subscribe_to_activities(self, callback: Callable):
        """
        활동 구독
        
        Args:
            callback: 메시지 수신 시 호출할 함수
        """
        self.pubsub.subscribe(self.CHANNELS['activity'])
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                callback(data)
    
    def subscribe_to_notifications(self, user_id: str, callback: Callable):
        """
        알림 구독
        
        Args:
            user_id: 사용자 ID
            callback: 메시지 수신 시 호출할 함수
        """
        self.pubsub.subscribe(self.CHANNELS['notifications'])
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                # 해당 사용자의 알림만 전달
                if data.get('user_id') == user_id:
                    callback(data)
    
    # ============================================
    # WebSocket 지원
    # ============================================
    
    async def websocket_handler(self, websocket):
        """
        WebSocket 연결 핸들러
        
        Args:
            websocket: WebSocket 연결 객체
        """
        # 클라이언트로부터 user_id 수신
        user_data = await websocket.receive_json()
        user_id = user_data.get('user_id')
        
        if not user_id:
            await websocket.close()
            return
        
        # Pub/Sub 구독
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(
            self.CHANNELS['score_update'],
            self.CHANNELS['activity'],
            self.CHANNELS['notifications']
        )
        
        try:
            # 메시지 리스닝 및 WebSocket으로 전송
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    
                    # 해당 사용자 관련 메시지만 전송
                    if data.get('user_id') == user_id or data.get('event') == 'leaderboard_updated':
                        await websocket.send_json(data)
        
        finally:
            pubsub.unsubscribe()
            await websocket.close()


# ============================================
# Spirit Score Engine과 통합
# ============================================

class SpiritScoreEngineWithRealtime:
    """
    실시간 업데이트가 통합된 Spirit Score Engine
    """
    
    def __init__(self, db_connection, redis_host="localhost"):
        from spirit_score_engine import SpiritScoreEngine
        
        self.engine = SpiritScoreEngine(db_connection)
        self.realtime = SpiritScoreRealtime(redis_host=redis_host)
    
    def record_activity(self, user_id: str, activity_type: str, **kwargs):
        """
        활동 기록 (실시간 업데이트 포함)
        """
        # 기존 로직 실행
        result = self.engine.record_activity(user_id, activity_type, **kwargs)
        
        # 실시간 업데이트 발행
        user_data = self.engine.get_user_score(user_id)
        
        self.realtime.publish_activity(
            user_id=user_id,
            username=user_data['username'],
            activity_type=activity_type,
            activity_data=result
        )
        
        # 점수 변경 발행
        if result.get('auto_approved'):
            self.realtime.publish_score_update(
                user_id=user_id,
                username=user_data['username'],
                old_score=user_data['spirit_score'] - result['score_change'],
                new_score=user_data['spirit_score'],
                activity_type=activity_type
            )
        
        # 리더보드 업데이트
        leaderboard = self.engine.get_leaderboard()
        self.realtime.publish_leaderboard_update(leaderboard)
        
        return result


# ============================================
# 사용 예시
# ============================================

from datetime import datetime

if __name__ == "__main__":
    print("Spirit Score Realtime 시스템 초기화 완료")
    print("Redis Pub/Sub 기반 실시간 업데이트")
    print()
    print("기능:")
    print("  - 점수 변경 실시간 알림")
    print("  - 활동 기록 브로드캐스트")
    print("  - 리더보드 실시간 업데이트")
    print("  - WebSocket 지원")
