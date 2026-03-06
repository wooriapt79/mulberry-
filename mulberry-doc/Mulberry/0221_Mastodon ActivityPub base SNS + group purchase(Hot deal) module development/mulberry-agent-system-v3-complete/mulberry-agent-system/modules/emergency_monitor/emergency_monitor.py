"""
Mulberry Emergency Monitoring & Auto-Recovery System
CTO Koda

AI 기반 시스템 감지, 자동 진단, 자동 복구
라즈베리파이 단말기 헬스 체크 포함
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum
import json
import requests
import time


class ErrorSeverity(str, Enum):
    """에러 심각도"""
    INFO = "info"              # 정보성
    WARNING = "warning"        # 경고
    ERROR = "error"            # 에러
    CRITICAL = "critical"      # 심각


class SystemComponent(str, Enum):
    """시스템 컴포넌트"""
    RASPBERRY_PI = "raspberry_pi"           # 라즈베리파이 단말기
    DATABASE = "database"                   # 데이터베이스
    API_SERVER = "api_server"               # API 서버
    MASTODON = "mastodon"                   # Mastodon 서버
    PAYMENT_GATEWAY = "payment_gateway"     # 결제 게이트웨이
    NETWORK = "network"                     # 네트워크
    AGENT = "agent"                         # AI 에이전트


class RecoveryAction(str, Enum):
    """복구 액션"""
    RESTART = "restart"                    # 재시작
    RESET = "reset"                        # 리셋
    RECONNECT = "reconnect"                # 재연결
    CLEAR_CACHE = "clear_cache"            # 캐시 클리어
    SCALE_UP = "scale_up"                  # 스케일 업
    FAILOVER = "failover"                  # Failover
    NOTIFY_ADMIN = "notify_admin"          # 관리자 알림


class EmergencyEvent:
    """긴급 상황 이벤트"""
    
    def __init__(
        self,
        event_id: str,
        component: SystemComponent,
        severity: ErrorSeverity,
        error_type: str,
        error_message: str
    ):
        self.event_id = event_id
        self.component = component
        self.severity = severity
        self.error_type = error_type
        self.error_message = error_message
        
        self.detected_at = datetime.now()
        self.resolved_at: Optional[datetime] = None
        
        # 진단 결과
        self.diagnosis: Optional[str] = None
        
        # 복구 액션
        self.recovery_actions: List[RecoveryAction] = []
        self.recovery_log: List[str] = []
        
        # 상태
        self.is_resolved = False
        self.auto_resolved = False
        
        # 추가 데이터
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "component": self.component.value,
            "severity": self.severity.value,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "diagnosis": self.diagnosis,
            "recovery_actions": [a.value for a in self.recovery_actions],
            "recovery_log": self.recovery_log,
            "is_resolved": self.is_resolved,
            "auto_resolved": self.auto_resolved,
            "metadata": self.metadata
        }


class RaspberryPiHealthCheck:
    """
    라즈베리파이 단말기 헬스 체크
    
    각 단말기의 상태를 주기적으로 체크하고
    문제 발생 시 자동 복구 시도
    """
    
    def __init__(self, terminal_id: str, terminal_ip: str):
        self.terminal_id = terminal_id
        self.terminal_ip = terminal_ip
        
        # 헬스 체크 간격 (초)
        self.check_interval = 60
        
        # 마지막 응답 시간
        self.last_response_at: Optional[datetime] = None
        
        # 연속 실패 횟수
        self.consecutive_failures = 0
    
    def ping(self) -> bool:
        """
        단말기 Ping 체크
        
        Returns:
            응답 여부
        """
        try:
            # HTTP 헬스 체크 엔드포인트
            response = requests.get(
                f"http://{self.terminal_ip}:8000/health",
                timeout=5
            )
            
            if response.status_code == 200:
                self.last_response_at = datetime.now()
                self.consecutive_failures = 0
                return True
            else:
                self.consecutive_failures += 1
                return False
        
        except Exception as e:
            self.consecutive_failures += 1
            print(f"❌ 단말기 {self.terminal_id} 응답 없음: {e}")
            return False
    
    def get_status(self) -> Dict:
        """
        단말기 상태 조회
        
        Returns:
            상태 정보
        """
        try:
            response = requests.get(
                f"http://{self.terminal_ip}:8000/status",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Status check failed"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def is_healthy(self) -> bool:
        """헬스 체크 (3번 연속 실패 시 unhealthy)"""
        return self.consecutive_failures < 3
    
    def restart(self) -> bool:
        """
        단말기 재시작 시도
        
        Returns:
            성공 여부
        """
        try:
            response = requests.post(
                f"http://{self.terminal_ip}:8000/restart",
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 단말기 {self.terminal_id} 재시작 완료")
                return True
            else:
                print(f"❌ 단말기 {self.terminal_id} 재시작 실패")
                return False
        
        except Exception as e:
            print(f"❌ 재시작 요청 실패: {e}")
            return False


class AIEmergencyMonitor:
    """
    AI 기반 긴급 상황 모니터 & 자동 복구
    
    시스템의 모든 컴포넌트를 감시하고
    문제 발생 시 AI가 자동으로 진단하고 복구 시도
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection
        
        # 라즈베리파이 헬스 체크 목록
        self.pi_health_checks: Dict[str, RaspberryPiHealthCheck] = {}
        
        # 모니터링 활성화
        self.monitoring_enabled = True
    
    # ============================================
    # 1. 감지 (Detection)
    # ============================================
    
    def detect_raspberry_pi_failure(self, terminal_id: str) -> Optional[EmergencyEvent]:
        """
        라즈베리파이 단말기 장애 감지
        
        Args:
            terminal_id: 단말기 ID
        
        Returns:
            이벤트 (장애 발생 시)
        """
        if terminal_id not in self.pi_health_checks:
            return None
        
        health_check = self.pi_health_checks[terminal_id]
        
        # Ping 체크
        is_alive = health_check.ping()
        
        if not is_alive and not health_check.is_healthy():
            # 3번 연속 실패 → 장애!
            event_id = f"EMG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            event = EmergencyEvent(
                event_id=event_id,
                component=SystemComponent.RASPBERRY_PI,
                severity=ErrorSeverity.CRITICAL,
                error_type="connection_lost",
                error_message=f"단말기 {terminal_id} 응답 없음 (3회 연속)"
            )
            
            event.metadata = {
                "terminal_id": terminal_id,
                "terminal_ip": health_check.terminal_ip,
                "consecutive_failures": health_check.consecutive_failures,
                "last_response_at": health_check.last_response_at.isoformat() if health_check.last_response_at else None
            }
            
            print(f"🚨 긴급: 단말기 {terminal_id} 장애 감지!")
            
            return event
        
        return None
    
    def detect_database_issue(self) -> Optional[EmergencyEvent]:
        """데이터베이스 문제 감지"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT 1")
            return None
        except Exception as e:
            event_id = f"EMG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            event = EmergencyEvent(
                event_id=event_id,
                component=SystemComponent.DATABASE,
                severity=ErrorSeverity.CRITICAL,
                error_type="connection_failed",
                error_message=str(e)
            )
            
            print(f"🚨 긴급: 데이터베이스 연결 실패!")
            
            return event
    
    def detect_api_server_issue(self, api_url: str) -> Optional[EmergencyEvent]:
        """API 서버 문제 감지"""
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            
            if response.status_code != 200:
                event_id = f"EMG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                event = EmergencyEvent(
                    event_id=event_id,
                    component=SystemComponent.API_SERVER,
                    severity=ErrorSeverity.ERROR,
                    error_type="server_error",
                    error_message=f"API 서버 응답 코드: {response.status_code}"
                )
                
                return event
        
        except Exception as e:
            event_id = f"EMG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            event = EmergencyEvent(
                event_id=event_id,
                component=SystemComponent.API_SERVER,
                severity=ErrorSeverity.CRITICAL,
                error_type="connection_failed",
                error_message=str(e)
            )
            
            return event
        
        return None
    
    # ============================================
    # 2. 진단 (Diagnosis)
    # ============================================
    
    def diagnose(self, event: EmergencyEvent) -> str:
        """
        AI 기반 자동 진단
        
        Args:
            event: 긴급 상황 이벤트
        
        Returns:
            진단 결과
        """
        # 컴포넌트별 진단 로직
        if event.component == SystemComponent.RASPBERRY_PI:
            diagnosis = self._diagnose_raspberry_pi(event)
        
        elif event.component == SystemComponent.DATABASE:
            diagnosis = self._diagnose_database(event)
        
        elif event.component == SystemComponent.API_SERVER:
            diagnosis = self._diagnose_api_server(event)
        
        elif event.component == SystemComponent.NETWORK:
            diagnosis = self._diagnose_network(event)
        
        else:
            diagnosis = "일반적인 시스템 오류"
        
        event.diagnosis = diagnosis
        
        print(f"🔍 진단: {diagnosis}")
        
        return diagnosis
    
    def _diagnose_raspberry_pi(self, event: EmergencyEvent) -> str:
        """라즈베리파이 진단"""
        terminal_id = event.metadata.get('terminal_id')
        
        # 1. 네트워크 문제?
        # 2. 전원 문제?
        # 3. 소프트웨어 크래시?
        
        possible_causes = []
        
        if event.error_type == "connection_lost":
            possible_causes.append("네트워크 연결 끊김")
            possible_causes.append("단말기 전원 꺼짐")
            possible_causes.append("소프트웨어 크래시")
        
        return f"라즈베리파이 {terminal_id} 문제: " + ", ".join(possible_causes)
    
    def _diagnose_database(self, event: EmergencyEvent) -> str:
        """데이터베이스 진단"""
        if "connection" in event.error_message.lower():
            return "데이터베이스 연결 실패 (네트워크 또는 서버 다운)"
        elif "timeout" in event.error_message.lower():
            return "데이터베이스 응답 지연 (과부하 가능성)"
        else:
            return "데이터베이스 일반 오류"
    
    def _diagnose_api_server(self, event: EmergencyEvent) -> str:
        """API 서버 진단"""
        if event.error_type == "connection_failed":
            return "API 서버 다운 또는 네트워크 문제"
        elif "500" in event.error_message:
            return "API 서버 내부 오류"
        elif "503" in event.error_message:
            return "API 서버 과부하"
        else:
            return "API 서버 일반 오류"
    
    def _diagnose_network(self, event: EmergencyEvent) -> str:
        """네트워크 진단"""
        return "네트워크 연결 문제"
    
    # ============================================
    # 3. 복구 (Recovery)
    # ============================================
    
    def auto_recover(self, event: EmergencyEvent) -> bool:
        """
        자동 복구 시도
        
        Args:
            event: 긴급 상황 이벤트
        
        Returns:
            복구 성공 여부
        """
        print(f"🔧 자동 복구 시작: {event.event_id}")
        
        # 진단 먼저
        if not event.diagnosis:
            self.diagnose(event)
        
        # 컴포넌트별 복구 시도
        if event.component == SystemComponent.RASPBERRY_PI:
            success = self._recover_raspberry_pi(event)
        
        elif event.component == SystemComponent.DATABASE:
            success = self._recover_database(event)
        
        elif event.component == SystemComponent.API_SERVER:
            success = self._recover_api_server(event)
        
        else:
            success = False
        
        if success:
            event.is_resolved = True
            event.auto_resolved = True
            event.resolved_at = datetime.now()
            
            print(f"✅ 자동 복구 성공: {event.event_id}")
        else:
            print(f"❌ 자동 복구 실패: {event.event_id}")
            
            # 관리자 알림
            event.recovery_actions.append(RecoveryAction.NOTIFY_ADMIN)
            self._notify_admin(event)
        
        # 로그 저장
        self._save_event(event)
        
        return success
    
    def _recover_raspberry_pi(self, event: EmergencyEvent) -> bool:
        """라즈베리파이 복구"""
        terminal_id = event.metadata.get('terminal_id')
        
        if terminal_id not in self.pi_health_checks:
            return False
        
        health_check = self.pi_health_checks[terminal_id]
        
        # 1차 시도: 재시작
        event.recovery_actions.append(RecoveryAction.RESTART)
        event.recovery_log.append(f"{datetime.now()}: 단말기 재시작 시도")
        
        if health_check.restart():
            # 재시작 후 30초 대기
            time.sleep(30)
            
            # 다시 Ping 체크
            if health_check.ping():
                event.recovery_log.append(f"{datetime.now()}: 재시작 성공, 정상 작동 확인")
                return True
        
        # 2차 시도: 재연결
        event.recovery_actions.append(RecoveryAction.RECONNECT)
        event.recovery_log.append(f"{datetime.now()}: 재연결 시도")
        
        # TODO: 재연결 로직
        
        return False
    
    def _recover_database(self, event: EmergencyEvent) -> bool:
        """데이터베이스 복구"""
        # 1차 시도: 재연결
        event.recovery_actions.append(RecoveryAction.RECONNECT)
        event.recovery_log.append(f"{datetime.now()}: 데이터베이스 재연결 시도")
        
        try:
            # 재연결 시도
            self.db = sqlite3.connect('mulberry.db')
            self.db.row_factory = sqlite3.Row
            
            # 테스트 쿼리
            cursor = self.db.cursor()
            cursor.execute("SELECT 1")
            
            event.recovery_log.append(f"{datetime.now()}: 재연결 성공")
            return True
        
        except Exception as e:
            event.recovery_log.append(f"{datetime.now()}: 재연결 실패 - {e}")
            return False
    
    def _recover_api_server(self, event: EmergencyEvent) -> bool:
        """API 서버 복구"""
        # 1차 시도: 재시작
        event.recovery_actions.append(RecoveryAction.RESTART)
        event.recovery_log.append(f"{datetime.now()}: API 서버 재시작 시도")
        
        # TODO: API 서버 재시작 로직
        
        return False
    
    # ============================================
    # 4. 알림 (Notification)
    # ============================================
    
    def _notify_admin(self, event: EmergencyEvent):
        """관리자 알림"""
        print(f"📧 관리자 알림: {event.event_id}")
        print(f"   컴포넌트: {event.component.value}")
        print(f"   심각도: {event.severity.value}")
        print(f"   메시지: {event.error_message}")
        print(f"   진단: {event.diagnosis}")
        
        # TODO: 실제 알림 전송 (이메일, Slack, SMS 등)
    
    # ============================================
    # 5. 저장 & 조회
    # ============================================
    
    def _save_event(self, event: EmergencyEvent):
        """이벤트 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO emergency_events (
                event_id, component, severity, error_type, error_message,
                detected_at, resolved_at, diagnosis, recovery_actions,
                recovery_log, is_resolved, auto_resolved, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.component.value,
            event.severity.value,
            event.error_type,
            event.error_message,
            event.detected_at,
            event.resolved_at,
            event.diagnosis,
            json.dumps([a.value for a in event.recovery_actions]),
            json.dumps(event.recovery_log),
            event.is_resolved,
            event.auto_resolved,
            json.dumps(event.metadata)
        ))
        self.db.commit()
    
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """최근 이벤트 조회"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM emergency_events
            ORDER BY detected_at DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ============================================
    # 6. 모니터링 루프
    # ============================================
    
    def register_raspberry_pi(self, terminal_id: str, terminal_ip: str):
        """라즈베리파이 단말기 등록"""
        health_check = RaspberryPiHealthCheck(terminal_id, terminal_ip)
        self.pi_health_checks[terminal_id] = health_check
        
        print(f"✅ 단말기 등록: {terminal_id} ({terminal_ip})")
    
    def monitor_all_raspberry_pis(self):
        """모든 라즈베리파이 단말기 모니터링"""
        for terminal_id, health_check in self.pi_health_checks.items():
            event = self.detect_raspberry_pi_failure(terminal_id)
            
            if event:
                # 긴급 상황 발생!
                self.auto_recover(event)


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # monitor = AIEmergencyMonitor(db_connection)
    
    # 라즈베리파이 단말기 등록
    # monitor.register_raspberry_pi("RPI-001", "192.168.1.100")
    # monitor.register_raspberry_pi("RPI-002", "192.168.1.101")
    
    # 모니터링 루프 (백그라운드에서 실행)
    # while monitor.monitoring_enabled:
    #     monitor.monitor_all_raspberry_pis()
    #     time.sleep(60)  # 1분마다
    
    print("✅ Emergency Monitor 로드 완료")
