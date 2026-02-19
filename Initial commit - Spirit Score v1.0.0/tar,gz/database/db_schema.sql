-- ============================================
-- Spirit Score 자동화 시스템 - Database Schema
-- CTO Koda
-- ============================================

-- 1. Users 테이블 (팀원 정보)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'CEO', 'PM', 'CTO', 'Lead_Dev'
    spirit_score DECIMAL(10, 4) DEFAULT 0.70, -- 초기값 0.70
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Activities 테이블 (활동 기록)
CREATE TABLE activities (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    activity_type VARCHAR(50) NOT NULL, -- 'login', 'mention_response', 'commit', 'pr_review', etc.
    activity_data JSONB, -- 활동 상세 정보
    score_change DECIMAL(10, 4) NOT NULL, -- 점수 변화량 (+0.01, -0.02 등)
    auto_approved BOOLEAN DEFAULT true, -- 자동 승인 여부
    approved_by UUID REFERENCES users(user_id), -- 수동 승인자
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Spirit Score History 테이블 (점수 변경 이력)
CREATE TABLE spirit_score_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    activity_id UUID REFERENCES activities(activity_id),
    previous_score DECIMAL(10, 4) NOT NULL,
    new_score DECIMAL(10, 4) NOT NULL,
    score_change DECIMAL(10, 4) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Mutual Aid Fund 테이블 (상부상조 기금)
CREATE TABLE mutual_aid_fund (
    fund_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    contribution_amount DECIMAL(15, 2) NOT NULL, -- 기여 금액
    contribution_type VARCHAR(50) NOT NULL, -- '10_percent_auto', 'manual', 'bonus'
    spirit_score_bonus DECIMAL(10, 4) DEFAULT 0, -- 기여로 얻은 점수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Activity Rules 테이블 (활동별 점수 규칙)
CREATE TABLE activity_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_type VARCHAR(50) UNIQUE NOT NULL,
    score_change DECIMAL(10, 4) NOT NULL,
    auto_approve BOOLEAN DEFAULT true,
    description TEXT,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Meeting Attendance 테이블 (회의 참석 기록)
CREATE TABLE meeting_attendance (
    attendance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id VARCHAR(100) NOT NULL,
    meeting_name VARCHAR(200) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(user_id),
    attended BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 인덱스 생성 (성능 최적화)
-- ============================================

CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_created_at ON activities(created_at);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_spirit_score_history_user_id ON spirit_score_history(user_id);
CREATE INDEX idx_mutual_aid_user_id ON mutual_aid_fund(user_id);
CREATE INDEX idx_meeting_attendance_user_id ON meeting_attendance(user_id);

-- ============================================
-- 기본 Activity Rules 삽입
-- ============================================

INSERT INTO activity_rules (activity_type, score_change, auto_approve, description) VALUES
    ('daily_login', 0.01, true, '일일 로그인'),
    ('mention_response', 0.02, true, '@호출 응답'),
    ('code_commit', 0.03, true, '코드 커밋 (승인된 것)'),
    ('pr_review', 0.02, true, 'PR 리뷰'),
    ('bug_report', 0.03, false, '버그 리포트 (수동 승인)'),
    ('important_decision', 0.05, false, '중요 결정 제안 (수동 승인)'),
    ('meeting_absence', -0.01, true, '회의 불참'),
    ('mention_no_response_3x', -0.02, true, '호출 무응답 3회'),
    ('documentation', 0.03, false, '문서화 (수동 승인)'),
    ('mutual_aid_contribution', 0.001, true, '상부상조 기여 (₩1000당 +0.001)');

-- ============================================
-- Trigger: Users 테이블 updated_at 자동 업데이트
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Trigger: Spirit Score 변경 시 자동 히스토리 기록
-- ============================================

CREATE OR REPLACE FUNCTION record_spirit_score_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.spirit_score <> NEW.spirit_score THEN
        INSERT INTO spirit_score_history (
            user_id,
            previous_score,
            new_score,
            score_change,
            reason
        ) VALUES (
            NEW.user_id,
            OLD.spirit_score,
            NEW.spirit_score,
            NEW.spirit_score - OLD.spirit_score,
            'Automatic score update'
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER track_spirit_score_changes AFTER UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION record_spirit_score_change();

-- ============================================
-- 초기 팀원 데이터 삽입 (예시)
-- ============================================

INSERT INTO users (username, display_name, email, role, spirit_score) VALUES
    ('re.eul', '대표님', 'ceo@mulberry.team', 'CEO', 0.80),
    ('pm', 'PM', 'pm@mulberry.team', 'PM', 0.75),
    ('koda', 'CTO Koda', 'koda@mulberry.team', 'CTO', 0.75),
    ('malu', 'Malu 수석', 'malu@mulberry.team', 'Lead_Dev', 0.75);

-- ============================================
-- 유용한 View 생성
-- ============================================

-- 팀원별 최근 활동 요약
CREATE VIEW user_activity_summary AS
SELECT 
    u.user_id,
    u.username,
    u.display_name,
    u.spirit_score,
    COUNT(a.activity_id) as total_activities,
    SUM(CASE WHEN a.score_change > 0 THEN 1 ELSE 0 END) as positive_activities,
    SUM(CASE WHEN a.score_change < 0 THEN 1 ELSE 0 END) as negative_activities,
    MAX(a.created_at) as last_activity_at
FROM users u
LEFT JOIN activities a ON u.user_id = a.user_id
GROUP BY u.user_id, u.username, u.display_name, u.spirit_score;

-- Spirit Score 리더보드
CREATE VIEW spirit_score_leaderboard AS
SELECT 
    u.username,
    u.display_name,
    u.role,
    u.spirit_score,
    RANK() OVER (ORDER BY u.spirit_score DESC) as rank
FROM users u
ORDER BY u.spirit_score DESC;

-- ============================================
-- 완료!
-- ============================================
