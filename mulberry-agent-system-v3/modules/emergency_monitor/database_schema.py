"""
Emergency Monitoring Database Schema
CTO Koda
"""

import sqlite3


def init_emergency_tables(db_connection):
    """
    긴급 상황 모니터링 테이블 초기화
    
    Args:
        db_connection: 데이터베이스 연결
    """
    cursor = db_connection.cursor()
    
    # ============================================
    # 1. 긴급 이벤트 테이블
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_events (
            event_id TEXT PRIMARY KEY,
            component TEXT NOT NULL,
            severity TEXT NOT NULL,
            error_type TEXT NOT NULL,
            error_message TEXT NOT NULL,
            
            detected_at TIMESTAMP NOT NULL,
            resolved_at TIMESTAMP,
            
            diagnosis TEXT,
            recovery_actions TEXT,  -- JSON array
            recovery_log TEXT,      -- JSON array
            
            is_resolved BOOLEAN DEFAULT 0,
            auto_resolved BOOLEAN DEFAULT 0,
            
            metadata TEXT,  -- JSON object
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ============================================
    # 2. 라즈베리파이 헬스 로그
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raspberry_pi_health_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            terminal_id TEXT NOT NULL,
            terminal_ip TEXT NOT NULL,
            
            is_alive BOOLEAN NOT NULL,
            response_time_ms INTEGER,
            
            status_data TEXT,  -- JSON from /status endpoint
            
            consecutive_failures INTEGER DEFAULT 0,
            
            checked_at TIMESTAMP NOT NULL,
            
            FOREIGN KEY (terminal_id) REFERENCES terminals(terminal_id)
        )
    """)
    
    # ============================================
    # 3. 시스템 메트릭 로그
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            component TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            unit TEXT,
            
            recorded_at TIMESTAMP NOT NULL
        )
    """)
    
    # ============================================
    # 인덱스 생성
    # ============================================
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_emergency_events_component 
        ON emergency_events(component, detected_at)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_emergency_events_severity 
        ON emergency_events(severity, is_resolved)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pi_health_terminal 
        ON raspberry_pi_health_logs(terminal_id, checked_at)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_system_metrics_component 
        ON system_metrics(component, metric_name, recorded_at)
    """)
    
    db_connection.commit()
    
    print("✅ Emergency 테이블 초기화 완료")


if __name__ == "__main__":
    # 테스트
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    init_emergency_tables(conn)
    
    # 테이블 목록 확인
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND (name LIKE 'emergency%' OR name LIKE '%health%' OR name LIKE 'system_metrics')
        ORDER BY name
    """)
    
    print("\n📊 생성된 테이블:")
    for row in cursor.fetchall():
        print(f"   - {row['name']}")
    
    conn.close()
