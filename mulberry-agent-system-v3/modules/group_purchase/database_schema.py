"""
Mulberry Group Purchase - Database Schema
CTO Koda

공동구매 모듈 데이터베이스 스키마
"""

import sqlite3


def init_group_purchase_tables(db_connection):
    """
    공동구매 테이블 초기화
    
    Args:
        db_connection: 데이터베이스 연결
    """
    cursor = db_connection.cursor()
    
    # ============================================
    # 1. 공동구매 상품 테이블
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_purchase_products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            
            -- 생산자 정보
            producer_agent_id TEXT NOT NULL,
            producer_location TEXT NOT NULL,
            producer_story TEXT,
            
            -- 가격 정보
            original_price REAL NOT NULL,
            group_price REAL NOT NULL,
            discount_rate REAL NOT NULL,
            
            -- 수량
            min_quantity INTEGER NOT NULL,
            max_quantity INTEGER NOT NULL,
            
            -- 기간
            start_at TIMESTAMP NOT NULL,
            end_at TIMESTAMP NOT NULL,
            
            -- 이미지
            image_urls TEXT,  -- JSON array
            
            -- 배송
            delivery_type TEXT NOT NULL,
            delivery_fee REAL DEFAULT 0,
            
            -- ActivityPub
            activitypub_uri TEXT,
            
            -- 메타
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            
            FOREIGN KEY (producer_agent_id) REFERENCES agents(agent_id)
        )
    """)
    
    # ============================================
    # 2. 공동구매 캠페인 테이블
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_purchase_campaigns (
            campaign_id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            
            -- 목표
            min_participants INTEGER NOT NULL,
            target_quantity INTEGER NOT NULL,
            
            -- 현재 상태
            current_participants INTEGER DEFAULT 0,
            current_quantity INTEGER DEFAULT 0,
            
            -- 상태
            status TEXT NOT NULL,
            
            -- 기간
            start_at TIMESTAMP NOT NULL,
            end_at TIMESTAMP NOT NULL,
            
            -- 참여자
            participants TEXT,  -- JSON array of user_ids
            
            -- ActivityPub
            activity_uri TEXT,
            
            -- 메타
            created_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP,
            
            FOREIGN KEY (product_id) REFERENCES group_purchase_products(product_id)
        )
    """)
    
    # ============================================
    # 3. 공동구매 주문 테이블
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_purchase_orders (
            order_id TEXT PRIMARY KEY,
            campaign_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            
            -- 수량 및 가격
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            
            -- 결제
            payment_status TEXT DEFAULT 'pending',
            payment_method TEXT,
            payment_at TIMESTAMP,
            
            -- 배송
            delivery_status TEXT DEFAULT 'pending',
            delivery_address TEXT,
            delivery_phone TEXT,
            delivery_at TIMESTAMP,
            tracking_number TEXT,
            
            -- 메타
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            
            FOREIGN KEY (campaign_id) REFERENCES group_purchase_campaigns(campaign_id),
            FOREIGN KEY (product_id) REFERENCES group_purchase_products(product_id)
        )
    """)
    
    # ============================================
    # 4. Mastodon 사용자 연동 테이블
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mastodon_users (
            mastodon_user_id TEXT PRIMARY KEY,
            instance_url TEXT NOT NULL,
            username TEXT NOT NULL,
            display_name TEXT,
            
            -- OAuth
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            token_expires_at TIMESTAMP,
            
            -- Mulberry 연결
            mulberry_user_id TEXT,
            
            -- 메타
            created_at TIMESTAMP NOT NULL,
            last_login_at TIMESTAMP,
            
            UNIQUE(instance_url, username)
        )
    """)
    
    # ============================================
    # 5. ActivityPub 활동 로그
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activitypub_activities (
            activity_id TEXT PRIMARY KEY,
            activity_type TEXT NOT NULL,  -- Create, Update, Announce
            
            -- 주체
            actor_uri TEXT NOT NULL,
            
            -- 객체
            object_type TEXT NOT NULL,  -- Article, Note, Offer
            object_id TEXT NOT NULL,
            
            -- 내용
            content TEXT,
            
            -- 대상
            to_uris TEXT,  -- JSON array
            cc_uris TEXT,  -- JSON array
            
            -- 상태
            published BOOLEAN DEFAULT 0,
            published_at TIMESTAMP,
            
            -- 메타
            created_at TIMESTAMP NOT NULL
        )
    """)
    
    # ============================================
    # 6. 공동구매 리뷰 테이블
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_purchase_reviews (
            review_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            campaign_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            
            -- 평가
            rating INTEGER NOT NULL,  -- 1-5
            title TEXT,
            content TEXT NOT NULL,
            
            -- 이미지
            image_urls TEXT,  -- JSON array
            
            -- ActivityPub (타임라인 공유)
            activity_uri TEXT,
            
            -- 메타
            created_at TIMESTAMP NOT NULL,
            
            FOREIGN KEY (order_id) REFERENCES group_purchase_orders(order_id),
            FOREIGN KEY (campaign_id) REFERENCES group_purchase_campaigns(campaign_id),
            FOREIGN KEY (product_id) REFERENCES group_purchase_products(product_id)
        )
    """)
    
    # ============================================
    # 7. 공동구매 알림 테이블
    # ============================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_purchase_notifications (
            notification_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            
            -- 종류
            notification_type TEXT NOT NULL,  -- campaign_start, goal_reached, deadline_soon, shipped
            
            -- 관련 객체
            campaign_id TEXT,
            product_id TEXT,
            order_id TEXT,
            
            -- 내용
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            
            -- 상태
            is_read BOOLEAN DEFAULT 0,
            read_at TIMESTAMP,
            
            -- Mastodon 알림 전송
            sent_to_mastodon BOOLEAN DEFAULT 0,
            
            -- 메타
            created_at TIMESTAMP NOT NULL
        )
    """)
    
    # ============================================
    # 인덱스 생성
    # ============================================
    
    # 상품 조회 최적화
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_category 
        ON group_purchase_products(category, end_at)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_location 
        ON group_purchase_products(producer_location)
    """)
    
    # 캠페인 조회 최적화
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_campaigns_status 
        ON group_purchase_campaigns(status, end_at)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_campaigns_product 
        ON group_purchase_campaigns(product_id)
    """)
    
    # 주문 조회 최적화
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_user 
        ON group_purchase_orders(user_id, created_at)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_campaign 
        ON group_purchase_orders(campaign_id)
    """)
    
    db_connection.commit()
    
    print("✅ 공동구매 데이터베이스 테이블 초기화 완료")


if __name__ == "__main__":
    # 테스트
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    init_group_purchase_tables(conn)
    
    # 테이블 목록 확인
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name LIKE 'group_purchase%' OR name = 'mastodon_users' OR name = 'activitypub_activities'
        ORDER BY name
    """)
    
    print("\n📊 생성된 테이블:")
    for row in cursor.fetchall():
        print(f"   - {row['name']}")
    
    conn.close()
