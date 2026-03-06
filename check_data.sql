-- 데이터 확인 쿼리

USE plainit_db;

-- 1. 테이블 존재 확인
SHOW TABLES LIKE 'user_action_logs';

-- 2. 테이블 구조 확인
DESCRIBE user_action_logs;

-- 3. test-user-001 데이터 개수 확인
SELECT COUNT(*) as total_count
FROM user_action_logs 
WHERE user_id = 'test-user-001';

-- 4. 최근 10개 데이터 확인
SELECT 
    user_id,
    task_id,
    action_type,
    action_time,
    day_of_week
FROM user_action_logs 
WHERE user_id = 'test-user-001'
ORDER BY action_time DESC
LIMIT 10;

-- 5. 액션 타입별 개수
SELECT 
    action_type,
    COUNT(*) as count
FROM user_action_logs 
WHERE user_id = 'test-user-001'
GROUP BY action_type;

-- 6. 요일별 개수
SELECT 
    day_of_week,
    COUNT(*) as count
FROM user_action_logs 
WHERE user_id = 'test-user-001'
GROUP BY day_of_week
ORDER BY 
    CASE day_of_week
        WHEN 'MONDAY' THEN 1
        WHEN 'TUESDAY' THEN 2
        WHEN 'WEDNESDAY' THEN 3
        WHEN 'THURSDAY' THEN 4
        WHEN 'FRIDAY' THEN 5
        WHEN 'SATURDAY' THEN 6
        WHEN 'SUNDAY' THEN 7
    END;
