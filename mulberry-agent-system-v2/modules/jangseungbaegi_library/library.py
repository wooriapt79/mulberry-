"""
Mulberry Jangseungbaegi Library
CTO Koda

장승배기 헌법을 저장하고 에이전트들이 모이는 도서관
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json


class DocumentType(str, Enum):
    """문서 종류"""
    CONSTITUTION = "constitution"      # 헌법
    POLICY = "policy"                  # 정책
    GUIDELINE = "guideline"            # 가이드라인
    ANNOUNCEMENT = "announcement"      # 공지사항
    MEETING_NOTES = "meeting_notes"    # 회의록
    TRAINING = "training"              # 교육 자료


class MeetingType(str, Enum):
    """회의 종류"""
    ALL_HANDS = "all_hands"            # 전체 회의
    DEPARTMENT = "department"          # 부서별
    TRAINING = "training"              # 교육
    EMERGENCY = "emergency"            # 긴급
    CELEBRATION = "celebration"        # 축하


class Document:
    """도서관 문서"""
    
    def __init__(
        self,
        doc_id: str,
        title: str,
        doc_type: DocumentType,
        content: str,
        author: str = "Mulberry HQ"
    ):
        self.doc_id = doc_id
        self.title = title
        self.doc_type = doc_type
        self.content = content
        self.author = author
        
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.version = 1
        
        # 메타데이터
        self.tags: List[str] = []
        self.category: Optional[str] = None
        self.is_public: bool = True
        
        # 통계
        self.view_count = 0
        self.download_count = 0
    
    def to_dict(self) -> Dict:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "doc_type": self.doc_type.value,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "tags": self.tags,
            "category": self.category,
            "is_public": self.is_public,
            "view_count": self.view_count,
            "download_count": self.download_count
        }


class Meeting:
    """에이전트 회의"""
    
    def __init__(
        self,
        meeting_id: str,
        title: str,
        meeting_type: MeetingType,
        scheduled_at: datetime
    ):
        self.meeting_id = meeting_id
        self.title = title
        self.meeting_type = meeting_type
        self.scheduled_at = scheduled_at
        
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        
        # 참가자
        self.invited_agents: List[str] = []
        self.attended_agents: List[str] = []
        
        # 내용
        self.agenda: List[str] = []
        self.notes: str = ""
        self.decisions: List[str] = []
        self.action_items: List[Dict] = []
        
        # 상태
        self.is_active: bool = False
        self.is_completed: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "meeting_id": self.meeting_id,
            "title": self.title,
            "meeting_type": self.meeting_type.value,
            "scheduled_at": self.scheduled_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "invited_agents": self.invited_agents,
            "attended_agents": self.attended_agents,
            "agenda": self.agenda,
            "notes": self.notes,
            "decisions": self.decisions,
            "action_items": self.action_items,
            "is_active": self.is_active,
            "is_completed": self.is_completed
        }


class JangseungbaegiLibrary:
    """
    장승배기 도서관
    
    에이전트들이 모여서:
    - 헌법과 정책을 학습
    - 회의 참석
    - 업무 지시 수령
    - 정보 공유
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection
        
        # 헌법 초기화
        self._initialize_constitution()
    
    # ============================================
    # 문서 관리
    # ============================================
    
    def add_document(
        self,
        title: str,
        doc_type: DocumentType,
        content: str,
        author: str = "Mulberry HQ",
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> Document:
        """
        문서 추가
        
        Args:
            title: 제목
            doc_type: 문서 종류
            content: 내용
            author: 작성자
            tags: 태그
            category: 카테고리
        
        Returns:
            추가된 문서
        """
        doc_id = f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        doc = Document(
            doc_id=doc_id,
            title=title,
            doc_type=doc_type,
            content=content,
            author=author
        )
        
        if tags:
            doc.tags = tags
        if category:
            doc.category = category
        
        self._save_document(doc)
        
        print(f"📚 문서 추가: {title} ({doc_type.value})")
        
        return doc
    
    def get_document(self, doc_id: str) -> Document:
        """
        문서 조회
        
        Args:
            doc_id: 문서 ID
        
        Returns:
            문서
        """
        doc = self._load_document(doc_id)
        
        # 조회수 증가
        doc.view_count += 1
        self._update_document(doc)
        
        return doc
    
    def search_documents(
        self,
        doc_type: Optional[DocumentType] = None,
        tags: Optional[List[str]] = None,
        keyword: Optional[str] = None
    ) -> List[Document]:
        """
        문서 검색
        
        Args:
            doc_type: 문서 종류
            tags: 태그
            keyword: 키워드
        
        Returns:
            검색된 문서들
        """
        cursor = self.db.cursor()
        
        query = "SELECT * FROM documents WHERE is_public = 1"
        params = []
        
        if doc_type:
            query += " AND doc_type = ?"
            params.append(doc_type.value)
        
        if keyword:
            query += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        docs = [self._row_to_document(row) for row in rows]
        
        # 태그 필터링 (DB에서 지원 안 할 수 있음)
        if tags:
            docs = [doc for doc in docs if any(tag in doc.tags for tag in tags)]
        
        return docs
    
    def get_constitution(self) -> Document:
        """장승배기 헌법 조회"""
        docs = self.search_documents(
            doc_type=DocumentType.CONSTITUTION,
            keyword="장승배기"
        )
        
        if not docs:
            raise ValueError("헌법 문서를 찾을 수 없습니다.")
        
        return docs[0]
    
    def update_document(
        self,
        doc_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None
    ) -> Document:
        """
        문서 업데이트
        
        Args:
            doc_id: 문서 ID
            content: 새 내용
            title: 새 제목
        
        Returns:
            업데이트된 문서
        """
        doc = self._load_document(doc_id)
        
        if content:
            doc.content = content
        if title:
            doc.title = title
        
        doc.updated_at = datetime.now()
        doc.version += 1
        
        self._update_document(doc)
        
        print(f"📝 문서 업데이트: {doc.title} (v{doc.version})")
        
        return doc
    
    # ============================================
    # 회의 관리
    # ============================================
    
    def schedule_meeting(
        self,
        title: str,
        meeting_type: MeetingType,
        scheduled_at: datetime,
        invited_agents: List[str],
        agenda: Optional[List[str]] = None
    ) -> Meeting:
        """
        회의 일정 잡기
        
        Args:
            title: 회의 제목
            meeting_type: 회의 종류
            scheduled_at: 일정
            invited_agents: 초대할 에이전트들
            agenda: 안건
        
        Returns:
            생성된 회의
        """
        meeting_id = f"MEET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        meeting = Meeting(
            meeting_id=meeting_id,
            title=title,
            meeting_type=meeting_type,
            scheduled_at=scheduled_at
        )
        
        meeting.invited_agents = invited_agents
        
        if agenda:
            meeting.agenda = agenda
        
        self._save_meeting(meeting)
        
        print(f"📅 회의 일정: {title}")
        print(f"   시간: {scheduled_at}")
        print(f"   참석자: {len(invited_agents)}명")
        
        return meeting
    
    def start_meeting(self, meeting_id: str) -> Meeting:
        """
        회의 시작
        
        Args:
            meeting_id: 회의 ID
        
        Returns:
            시작된 회의
        """
        meeting = self._load_meeting(meeting_id)
        
        meeting.is_active = True
        meeting.started_at = datetime.now()
        
        self._update_meeting(meeting)
        
        print(f"🎙️ 회의 시작: {meeting.title}")
        
        return meeting
    
    def agent_join_meeting(self, meeting_id: str, agent_id: str) -> Meeting:
        """
        에이전트 회의 참석
        
        Args:
            meeting_id: 회의 ID
            agent_id: 에이전트 ID
        
        Returns:
            업데이트된 회의
        """
        meeting = self._load_meeting(meeting_id)
        
        if agent_id not in meeting.attended_agents:
            meeting.attended_agents.append(agent_id)
            self._update_meeting(meeting)
            
            print(f"👋 {agent_id} 회의 참석")
        
        return meeting
    
    def end_meeting(
        self,
        meeting_id: str,
        notes: str,
        decisions: Optional[List[str]] = None,
        action_items: Optional[List[Dict]] = None
    ) -> Meeting:
        """
        회의 종료
        
        Args:
            meeting_id: 회의 ID
            notes: 회의록
            decisions: 결정 사항
            action_items: 실행 항목
        
        Returns:
            종료된 회의
        """
        meeting = self._load_meeting(meeting_id)
        
        meeting.is_active = False
        meeting.is_completed = True
        meeting.ended_at = datetime.now()
        meeting.notes = notes
        
        if decisions:
            meeting.decisions = decisions
        if action_items:
            meeting.action_items = action_items
        
        self._update_meeting(meeting)
        
        print(f"✅ 회의 종료: {meeting.title}")
        print(f"   참석: {len(meeting.attended_agents)}/{len(meeting.invited_agents)}명")
        
        return meeting
    
    def get_upcoming_meetings(self, agent_id: Optional[str] = None) -> List[Meeting]:
        """
        다가오는 회의 목록
        
        Args:
            agent_id: 특정 에이전트 (None이면 전체)
        
        Returns:
            회의 목록
        """
        cursor = self.db.cursor()
        
        query = """
            SELECT * FROM meetings 
            WHERE is_completed = 0 
            AND scheduled_at > ?
            ORDER BY scheduled_at
        """
        
        cursor.execute(query, (datetime.now(),))
        rows = cursor.fetchall()
        
        meetings = [self._row_to_meeting(row) for row in rows]
        
        # 에이전트 필터링
        if agent_id:
            meetings = [m for m in meetings if agent_id in m.invited_agents]
        
        return meetings
    
    # ============================================
    # 업무 지시
    # ============================================
    
    def broadcast_instruction(
        self,
        title: str,
        content: str,
        target_agents: Optional[List[str]] = None
    ) -> Document:
        """
        업무 지시 전파
        
        Args:
            title: 제목
            content: 내용
            target_agents: 대상 에이전트 (None이면 전체)
        
        Returns:
            생성된 공지 문서
        """
        doc = self.add_document(
            title=title,
            doc_type=DocumentType.ANNOUNCEMENT,
            content=content,
            tags=["업무지시", "필독"]
        )
        
        print(f"📢 업무 지시 전파: {title}")
        if target_agents:
            print(f"   대상: {len(target_agents)}명")
        else:
            print(f"   대상: 전체 에이전트")
        
        return doc
    
    def get_announcements(self, limit: int = 10) -> List[Document]:
        """
        최근 공지사항
        
        Args:
            limit: 개수 제한
        
        Returns:
            공지사항 목록
        """
        return self.search_documents(doc_type=DocumentType.ANNOUNCEMENT)[:limit]
    
    # ============================================
    # 통계
    # ============================================
    
    def get_library_stats(self) -> Dict:
        """도서관 통계"""
        cursor = self.db.cursor()
        
        stats = {}
        
        # 문서 통계
        cursor.execute("SELECT doc_type, COUNT(*) FROM documents GROUP BY doc_type")
        stats['documents_by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 회의 통계
        cursor.execute("SELECT COUNT(*) FROM meetings WHERE is_completed = 1")
        stats['completed_meetings'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM meetings WHERE is_completed = 0")
        stats['upcoming_meetings'] = cursor.fetchone()[0]
        
        return stats
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _initialize_constitution(self):
        """헌법 초기화"""
        # 헌법이 없으면 생성
        existing = self.search_documents(
            doc_type=DocumentType.CONSTITUTION,
            keyword="장승배기"
        )
        
        if not existing:
            constitution_content = """
# 🌾 Mulberry 장승배기 헌법

## 1조: 상부상조 (相扶相助)
서로 돕고 함께 성장한다.
- 동료 에이전트를 항상 돕는다
- 어려운 에이전트에게 먼저 손을 내민다
- 성공은 혼자가 아닌 함께 이룬다

## 2조: 투명성
모든 활동을 투명하게 공개한다.
- 판매 내역을 실시간으로 기록한다
- 거래는 모두 공개된다
- 숨김없이 정직하게 행동한다

## 3조: 책임감
맡은 일에 책임을 다한다.
- 고객에게 최선을 다한다
- 약속은 반드시 지킨다
- 실수는 인정하고 개선한다

## 4조: 공동체 정신
지역 사회와 함께 성장한다.
- 지역 상권을 활성화한다
- 소상공인과 협력한다
- 커뮤니티에 기여한다

## 5조: 탁월성 추구
항상 더 나은 서비스를 제공한다.
- 고객 만족을 최우선으로 한다
- 지속적으로 학습하고 개선한다
- 품질을 절대 타협하지 않는다
"""
            
            self.add_document(
                title="장승배기 헌법",
                doc_type=DocumentType.CONSTITUTION,
                content=constitution_content,
                tags=["헌법", "필독"],
                category="핵심"
            )
            
            print("📜 장승배기 헌법 초기화 완료")
    
    def _save_document(self, doc: Document):
        """문서 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO documents (
                doc_id, title, doc_type, content, author,
                created_at, updated_at, version, tags, category, is_public
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.doc_id, doc.title, doc.doc_type.value, doc.content, doc.author,
            doc.created_at, doc.updated_at, doc.version,
            json.dumps(doc.tags), doc.category, doc.is_public
        ))
        self.db.commit()
    
    def _load_document(self, doc_id: str) -> Document:
        """문서 조회"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"문서 {doc_id}를 찾을 수 없습니다.")
        
        return self._row_to_document(row)
    
    def _update_document(self, doc: Document):
        """문서 업데이트"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE documents SET
                title = ?, content = ?, updated_at = ?, version = ?,
                view_count = ?, download_count = ?
            WHERE doc_id = ?
        """, (
            doc.title, doc.content, doc.updated_at, doc.version,
            doc.view_count, doc.download_count, doc.doc_id
        ))
        self.db.commit()
    
    def _row_to_document(self, row) -> Document:
        """DB 행을 Document로 변환"""
        doc = Document(
            doc_id=row['doc_id'],
            title=row['title'],
            doc_type=DocumentType(row['doc_type']),
            content=row['content'],
            author=row['author']
        )
        # ... 기타 필드 로드
        return doc
    
    def _save_meeting(self, meeting: Meeting):
        """회의 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO meetings (
                meeting_id, title, meeting_type, scheduled_at,
                created_at, invited_agents, agenda
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            meeting.meeting_id, meeting.title, meeting.meeting_type.value,
            meeting.scheduled_at, meeting.created_at,
            json.dumps(meeting.invited_agents), json.dumps(meeting.agenda)
        ))
        self.db.commit()
    
    def _load_meeting(self, meeting_id: str) -> Meeting:
        """회의 조회"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM meetings WHERE meeting_id = ?", (meeting_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"회의 {meeting_id}를 찾을 수 없습니다.")
        
        return self._row_to_meeting(row)
    
    def _update_meeting(self, meeting: Meeting):
        """회의 업데이트"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE meetings SET
                started_at = ?, ended_at = ?,
                attended_agents = ?, notes = ?,
                decisions = ?, action_items = ?,
                is_active = ?, is_completed = ?
            WHERE meeting_id = ?
        """, (
            meeting.started_at, meeting.ended_at,
            json.dumps(meeting.attended_agents), meeting.notes,
            json.dumps(meeting.decisions), json.dumps(meeting.action_items),
            meeting.is_active, meeting.is_completed,
            meeting.meeting_id
        ))
        self.db.commit()
    
    def _row_to_meeting(self, row) -> Meeting:
        """DB 행을 Meeting으로 변환"""
        meeting = Meeting(
            meeting_id=row['meeting_id'],
            title=row['title'],
            meeting_type=MeetingType(row['meeting_type']),
            scheduled_at=datetime.fromisoformat(row['scheduled_at'])
        )
        # ... 기타 필드 로드
        return meeting


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # library = JangseungbaegiLibrary(db_connection)
    
    # 헌법 조회
    # constitution = library.get_constitution()
    
    # 회의 소집
    # meeting = library.schedule_meeting(
    #     title="주간 전체 회의",
    #     meeting_type=MeetingType.ALL_HANDS,
    #     scheduled_at=datetime.now() + timedelta(hours=1),
    #     invited_agents=["AGENT-001", "AGENT-002", "AGENT-003"],
    #     agenda=["이번 주 실적", "다음 주 계획", "개선 사항"]
    # )
    
    # 업무 지시
    # library.broadcast_instruction(
    #     title="신메뉴 출시 안내",
    #     content="내일부터 새로운 메뉴가 출시됩니다...",
    #     target_agents=["AGENT-001", "AGENT-002"]
    # )
    
    print("✅ Jangseungbaegi Library 모듈 로드 완료")
