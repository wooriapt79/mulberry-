"""
Mulberry Terminal Matching System
CTO Koda

라즈베리파이 단말기와 AI 에이전트 1:1 매칭 시스템
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json


class TerminalStatus(str, Enum):
    """단말기 상태"""
    REGISTERED = "registered"        # 등록됨
    AVAILABLE = "available"          # 사용 가능
    ASSIGNED = "assigned"            # 에이전트 할당됨
    ACTIVE = "active"                # 활성 (영업 중)
    MAINTENANCE = "maintenance"      # 점검 중
    OFFLINE = "offline"              # 오프라인
    RETIRED = "retired"              # 폐기


class StoreInfo:
    """가게 정보"""
    
    def __init__(
        self,
        store_name: str,
        store_type: str,
        address: str,
        phone: str,
        business_hours: Dict,
        google_business_id: Optional[str] = None
    ):
        self.store_name = store_name
        self.store_type = store_type
        self.address = address
        self.phone = phone
        self.business_hours = business_hours  # {"mon": "09:00-22:00", ...}
        self.google_business_id = google_business_id
        
        # 추가 정보
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.owner_name: Optional[str] = None
        self.owner_phone: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "store_name": self.store_name,
            "store_type": self.store_type,
            "address": self.address,
            "phone": self.phone,
            "business_hours": self.business_hours,
            "google_business_id": self.google_business_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "owner_name": self.owner_name,
            "owner_phone": self.owner_phone
        }


class RaspberryPiTerminal:
    """라즈베리파이 단말기"""
    
    def __init__(
        self,
        terminal_id: str,
        serial_number: str,
        model: str = "Raspberry Pi 5"
    ):
        self.terminal_id = terminal_id
        self.serial_number = serial_number  # 하드웨어 시리얼 번호
        self.model = model
        
        # 상태
        self.status = TerminalStatus.REGISTERED
        self.registered_at = datetime.now()
        
        # 매칭 정보
        self.agent_id: Optional[str] = None
        self.assigned_at: Optional[datetime] = None
        
        # 가게 정보
        self.store_info: Optional[StoreInfo] = None
        
        # 하드웨어 정보
        self.ip_address: Optional[str] = None
        self.mac_address: Optional[str] = None
        self.firmware_version: Optional[str] = None
        
        # 주변 장치
        self.has_display: bool = False
        self.has_scanner: bool = False
        self.has_printer: bool = False
        self.has_card_reader: bool = False
        
        # 통계
        self.total_uptime_hours: float = 0.0
        self.last_heartbeat: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "terminal_id": self.terminal_id,
            "serial_number": self.serial_number,
            "model": self.model,
            "status": self.status.value,
            "registered_at": self.registered_at.isoformat(),
            "agent_id": self.agent_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "store_info": self.store_info.to_dict() if self.store_info else None,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "firmware_version": self.firmware_version,
            "has_display": self.has_display,
            "has_scanner": self.has_scanner,
            "has_printer": self.has_printer,
            "has_card_reader": self.has_card_reader,
            "total_uptime_hours": self.total_uptime_hours,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }


class TerminalMatchingManager:
    """
    단말기 매칭 관리자
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection
    
    def register_terminal(
        self,
        serial_number: str,
        store_info: StoreInfo,
        hardware_specs: Optional[Dict] = None
    ) -> RaspberryPiTerminal:
        """
        단말기 등록
        
        Args:
            serial_number: 하드웨어 시리얼 번호
            store_info: 가게 정보
            hardware_specs: 하드웨어 사양 (선택)
        
        Returns:
            등록된 단말기
        """
        # 중복 확인
        existing = self._find_by_serial(serial_number)
        if existing:
            raise ValueError(f"시리얼 번호 {serial_number}는 이미 등록되어 있습니다.")
        
        # 단말기 ID 생성
        terminal_id = f"RPI-{datetime.now().strftime('%Y%m%d')}-{serial_number[-6:]}"
        
        # 단말기 생성
        terminal = RaspberryPiTerminal(
            terminal_id=terminal_id,
            serial_number=serial_number
        )
        
        # 가게 정보 설정
        terminal.store_info = store_info
        
        # 하드웨어 사양 설정
        if hardware_specs:
            terminal.has_display = hardware_specs.get('display', False)
            terminal.has_scanner = hardware_specs.get('scanner', False)
            terminal.has_printer = hardware_specs.get('printer', False)
            terminal.has_card_reader = hardware_specs.get('card_reader', False)
        
        terminal.status = TerminalStatus.AVAILABLE
        
        # 저장
        self._save_terminal(terminal)
        
        print(f"✅ 단말기 등록 완료: {terminal_id}")
        print(f"   가게: {store_info.store_name} ({store_info.store_type})")
        print(f"   주소: {store_info.address}")
        
        return terminal
    
    def assign_agent(
        self,
        terminal_id: str,
        agent_id: str
    ) -> RaspberryPiTerminal:
        """
        에이전트를 단말기에 할당
        
        Args:
            terminal_id: 단말기 ID
            agent_id: 에이전트 ID
        
        Returns:
            매칭된 단말기
        """
        terminal = self._load_terminal(terminal_id)
        
        # 상태 확인
        if terminal.status != TerminalStatus.AVAILABLE:
            raise ValueError(
                f"단말기 {terminal_id}는 현재 사용 불가능합니다. (상태: {terminal.status.value})"
            )
        
        if terminal.agent_id:
            raise ValueError(
                f"단말기 {terminal_id}는 이미 에이전트 {terminal.agent_id}가 할당되어 있습니다."
            )
        
        # 에이전트 매칭
        terminal.agent_id = agent_id
        terminal.assigned_at = datetime.now()
        terminal.status = TerminalStatus.ASSIGNED
        
        self._update_terminal(terminal)
        
        print(f"✅ 에이전트 매칭 완료!")
        print(f"   단말기: {terminal_id}")
        print(f"   에이전트: {agent_id}")
        print(f"   가게: {terminal.store_info.store_name if terminal.store_info else 'N/A'}")
        
        return terminal
    
    def activate_terminal(self, terminal_id: str) -> RaspberryPiTerminal:
        """
        단말기 활성화 (영업 시작)
        
        Args:
            terminal_id: 단말기 ID
        
        Returns:
            활성화된 단말기
        """
        terminal = self._load_terminal(terminal_id)
        
        if terminal.status != TerminalStatus.ASSIGNED:
            raise ValueError(
                f"단말기 {terminal_id}는 에이전트가 할당되지 않았습니다."
            )
        
        if not terminal.agent_id:
            raise ValueError(
                f"단말기 {terminal_id}에 에이전트가 없습니다."
            )
        
        terminal.status = TerminalStatus.ACTIVE
        self._update_terminal(terminal)
        
        print(f"🚀 단말기 {terminal_id} 활성화! 영업 시작!")
        
        return terminal
    
    def get_terminal_by_agent(self, agent_id: str) -> Optional[RaspberryPiTerminal]:
        """
        에이전트의 단말기 조회
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            단말기 또는 None
        """
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM terminals WHERE agent_id = ?",
            (agent_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_terminal(row)
    
    def get_available_terminals(self) -> List[RaspberryPiTerminal]:
        """
        사용 가능한 단말기 목록
        
        Returns:
            사용 가능한 단말기들
        """
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM terminals WHERE status = ?",
            (TerminalStatus.AVAILABLE.value,)
        )
        rows = cursor.fetchall()
        
        return [self._row_to_terminal(row) for row in rows]
    
    def heartbeat(self, terminal_id: str, status_data: Dict) -> bool:
        """
        단말기 하트비트 (생존 신호)
        
        Args:
            terminal_id: 단말기 ID
            status_data: 상태 데이터 (온도, 메모리, CPU 등)
        
        Returns:
            성공 여부
        """
        terminal = self._load_terminal(terminal_id)
        
        terminal.last_heartbeat = datetime.now()
        
        # 상태 데이터 처리 (필요시)
        if 'ip_address' in status_data:
            terminal.ip_address = status_data['ip_address']
        
        self._update_terminal(terminal)
        
        return True
    
    def update_store_info(
        self,
        terminal_id: str,
        store_info: StoreInfo
    ) -> RaspberryPiTerminal:
        """
        가게 정보 업데이트
        
        Args:
            terminal_id: 단말기 ID
            store_info: 새 가게 정보
        
        Returns:
            업데이트된 단말기
        """
        terminal = self._load_terminal(terminal_id)
        terminal.store_info = store_info
        self._update_terminal(terminal)
        
        print(f"✅ 가게 정보 업데이트: {terminal_id}")
        
        return terminal
    
    def get_matching_stats(self) -> Dict:
        """매칭 통계"""
        cursor = self.db.cursor()
        
        stats = {}
        
        # 전체 단말기 수
        cursor.execute("SELECT COUNT(*) FROM terminals")
        stats['total_terminals'] = cursor.fetchone()[0]
        
        # 상태별 집계
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM terminals 
            GROUP BY status
        """)
        stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 가게 종류별 집계
        cursor.execute("""
            SELECT store_type, COUNT(*) 
            FROM terminals 
            WHERE store_info IS NOT NULL
            GROUP BY store_type
        """)
        stats['by_store_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        return stats
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _find_by_serial(self, serial_number: str) -> Optional[RaspberryPiTerminal]:
        """시리얼 번호로 찾기"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM terminals WHERE serial_number = ?",
            (serial_number,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_terminal(row)
    
    def _save_terminal(self, terminal: RaspberryPiTerminal):
        """단말기 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO terminals (
                terminal_id, serial_number, model, status,
                registered_at, agent_id, store_info,
                has_display, has_scanner, has_printer, has_card_reader
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            terminal.terminal_id,
            terminal.serial_number,
            terminal.model,
            terminal.status.value,
            terminal.registered_at,
            terminal.agent_id,
            json.dumps(terminal.store_info.to_dict()) if terminal.store_info else None,
            terminal.has_display,
            terminal.has_scanner,
            terminal.has_printer,
            terminal.has_card_reader
        ))
        self.db.commit()
    
    def _load_terminal(self, terminal_id: str) -> RaspberryPiTerminal:
        """단말기 조회"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM terminals WHERE terminal_id = ?",
            (terminal_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"단말기 {terminal_id}를 찾을 수 없습니다.")
        
        return self._row_to_terminal(row)
    
    def _update_terminal(self, terminal: RaspberryPiTerminal):
        """단말기 업데이트"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE terminals SET
                status = ?,
                agent_id = ?,
                assigned_at = ?,
                store_info = ?,
                ip_address = ?,
                last_heartbeat = ?
            WHERE terminal_id = ?
        """, (
            terminal.status.value,
            terminal.agent_id,
            terminal.assigned_at,
            json.dumps(terminal.store_info.to_dict()) if terminal.store_info else None,
            terminal.ip_address,
            terminal.last_heartbeat,
            terminal.terminal_id
        ))
        self.db.commit()
    
    def _row_to_terminal(self, row) -> RaspberryPiTerminal:
        """DB 행을 Terminal 객체로 변환"""
        terminal = RaspberryPiTerminal(
            terminal_id=row['terminal_id'],
            serial_number=row['serial_number'],
            model=row['model']
        )
        
        terminal.status = TerminalStatus(row['status'])
        terminal.agent_id = row['agent_id']
        # ... 기타 필드 로드
        
        if row['store_info']:
            store_data = json.loads(row['store_info'])
            terminal.store_info = StoreInfo(
                store_name=store_data['store_name'],
                store_type=store_data['store_type'],
                address=store_data['address'],
                phone=store_data['phone'],
                business_hours=store_data['business_hours'],
                google_business_id=store_data.get('google_business_id')
            )
        
        return terminal


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # manager = TerminalMatchingManager(db_connection)
    
    # 가게 정보
    store = StoreInfo(
        store_name="맛있는 김밥",
        store_type="restaurant",
        address="서울시 강남구 테헤란로 123",
        phone="02-1234-5678",
        business_hours={
            "mon": "09:00-22:00",
            "tue": "09:00-22:00",
            "wed": "09:00-22:00",
            "thu": "09:00-22:00",
            "fri": "09:00-22:00",
            "sat": "10:00-21:00",
            "sun": "10:00-21:00"
        },
        google_business_id="ChIJxxxxx"
    )
    
    # 단말기 등록
    # terminal = manager.register_terminal(
    #     serial_number="RPI5-2024-ABC123",
    #     store_info=store,
    #     hardware_specs={
    #         'display': True,
    #         'scanner': True,
    #         'printer': False,
    #         'card_reader': True
    #     }
    # )
    
    # 에이전트 매칭
    # manager.assign_agent(terminal.terminal_id, "AGENT-20240220-12345678")
    
    # 활성화
    # manager.activate_terminal(terminal.terminal_id)
    
    print("✅ Terminal Matching 모듈 로드 완료")
