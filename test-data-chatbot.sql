-- 챗봇 테스트를 위한 풍부한 테스트 데이터
-- plainit_db.user_action_logs 테이블에 삽입

USE plainit_db;

-- 기존 테스트 데이터 삭제 (선택)
-- DELETE FROM user_action_logs WHERE user_id = 'test-user-001';

-- 테스트 사용자: test-user-001
-- 최근 4주 데이터 (2026-02-03 ~ 2026-03-04)

-- ========================================
-- 1주차: 2026-02-03 ~ 2026-02-09 (월~일)
-- 패턴: 주중 완료 많음, 주말 미룸 많음
-- ========================================

-- 월요일 (2026-02-03) - 완료 많음
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2001, 100, 'COMPLETED', '2026-02-03 09:00:00', '2026-02-03', NULL, 'MONDAY', 9, NOW()),
('test-user-001', 2002, 100, 'COMPLETED', '2026-02-03 14:30:00', '2026-02-03', NULL, 'MONDAY', 14, NOW()),
('test-user-001', 2003, 101, 'COMPLETED', '2026-02-03 18:00:00', '2026-02-03', NULL, 'MONDAY', 18, NOW());

-- 화요일 (2026-02-04) - 완료 많음
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2004, 100, 'COMPLETED', '2026-02-04 10:00:00', '2026-02-04', NULL, 'TUESDAY', 10, NOW()),
('test-user-001', 2005, 101, 'COMPLETED', '2026-02-04 15:00:00', '2026-02-04', NULL, 'TUESDAY', 15, NOW()),
('test-user-001', 2006, 100, 'COMPLETED', '2026-02-04 19:00:00', '2026-02-04', NULL, 'TUESDAY', 19, NOW()),
('test-user-001', 2007, 101, 'POSTPONED', '2026-02-04 20:00:00', '2026-02-04', '2026-02-05', 'TUESDAY', 20, NOW());

-- 수요일 (2026-02-05) - 완료 중간
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2008, 100, 'COMPLETED', '2026-02-05 09:30:00', '2026-02-05', NULL, 'WEDNESDAY', 9, NOW()),
('test-user-001', 2009, 101, 'COMPLETED', '2026-02-05 14:00:00', '2026-02-05', NULL, 'WEDNESDAY', 14, NOW()),
('test-user-001', 2010, 100, 'POSTPONED', '2026-02-05 18:30:00', '2026-02-05', '2026-02-06', 'WEDNESDAY', 18, NOW());

-- 목요일 (2026-02-06) - 완료 많음
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2011, 101, 'COMPLETED', '2026-02-06 10:00:00', '2026-02-06', NULL, 'THURSDAY', 10, NOW()),
('test-user-001', 2012, 100, 'COMPLETED', '2026-02-06 15:30:00', '2026-02-06', NULL, 'THURSDAY', 15, NOW()),
('test-user-001', 2013, 101, 'COMPLETED', '2026-02-06 19:00:00', '2026-02-06', NULL, 'THURSDAY', 19, NOW());

-- 금요일 (2026-02-07) - 완료 중간
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2014, 100, 'COMPLETED', '2026-02-07 09:00:00', '2026-02-07', NULL, 'FRIDAY', 9, NOW()),
('test-user-001', 2015, 101, 'COMPLETED', '2026-02-07 14:00:00', '2026-02-07', NULL, 'FRIDAY', 14, NOW()),
('test-user-001', 2016, 100, 'POSTPONED', '2026-02-07 18:00:00', '2026-02-07', '2026-02-10', 'FRIDAY', 18, NOW()),
('test-user-001', 2017, 101, 'POSTPONED', '2026-02-07 20:00:00', '2026-02-07', '2026-02-10', 'FRIDAY', 20, NOW());

-- 토요일 (2026-02-08) - 미룸 많음
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2018, 100, 'POSTPONED', '2026-02-08 10:00:00', '2026-02-08', '2026-02-10', 'SATURDAY', 10, NOW()),
('test-user-001', 2019, 101, 'POSTPONED', '2026-02-08 14:00:00', '2026-02-08', '2026-02-10', 'SATURDAY', 14, NOW()),
('test-user-001', 2020, 100, 'POSTPONED', '2026-02-08 18:00:00', '2026-02-08', '2026-02-10', 'SATURDAY', 18, NOW()),
('test-user-001', 2021, 101, 'COMPLETED', '2026-02-08 20:00:00', '2026-02-08', NULL, 'SATURDAY', 20, NOW());

-- 일요일 (2026-02-09) - 미룸 매우 많음 (최악의 요일)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2022, 100, 'POSTPONED', '2026-02-09 10:00:00', '2026-02-09', '2026-02-10', 'SUNDAY', 10, NOW()),
('test-user-001', 2023, 101, 'POSTPONED', '2026-02-09 12:00:00', '2026-02-09', '2026-02-10', 'SUNDAY', 12, NOW()),
('test-user-001', 2024, 100, 'POSTPONED', '2026-02-09 14:00:00', '2026-02-09', '2026-02-10', 'SUNDAY', 14, NOW()),
('test-user-001', 2025, 101, 'POSTPONED', '2026-02-09 16:00:00', '2026-02-09', '2026-02-10', 'SUNDAY', 16, NOW()),
('test-user-001', 2026, 100, 'POSTPONED', '2026-02-09 18:00:00', '2026-02-09', '2026-02-10', 'SUNDAY', 18, NOW()),
('test-user-001', 2027, 101, 'POSTPONED', '2026-02-09 20:00:00', '2026-02-09', '2026-02-10', 'SUNDAY', 20, NOW());

-- ========================================
-- 2주차: 2026-02-10 ~ 2026-02-16 (월~일)
-- 패턴: 전반적으로 완료율 향상
-- ========================================

-- 월요일 (2026-02-10)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2028, 100, 'COMPLETED', '2026-02-10 09:00:00', '2026-02-10', NULL, 'MONDAY', 9, NOW()),
('test-user-001', 2029, 101, 'COMPLETED', '2026-02-10 14:00:00', '2026-02-10', NULL, 'MONDAY', 14, NOW()),
('test-user-001', 2030, 100, 'COMPLETED', '2026-02-10 18:00:00', '2026-02-10', NULL, 'MONDAY', 18, NOW()),
('test-user-001', 2031, 101, 'COMPLETED', '2026-02-10 20:00:00', '2026-02-10', NULL, 'MONDAY', 20, NOW());

-- 화요일 (2026-02-11)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2032, 100, 'COMPLETED', '2026-02-11 10:00:00', '2026-02-11', NULL, 'TUESDAY', 10, NOW()),
('test-user-001', 2033, 101, 'COMPLETED', '2026-02-11 15:00:00', '2026-02-11', NULL, 'TUESDAY', 15, NOW()),
('test-user-001', 2034, 100, 'COMPLETED', '2026-02-11 19:00:00', '2026-02-11', NULL, 'TUESDAY', 19, NOW());

-- 수요일 (2026-02-12)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2035, 101, 'COMPLETED', '2026-02-12 09:30:00', '2026-02-12', NULL, 'WEDNESDAY', 9, NOW()),
('test-user-001', 2036, 100, 'COMPLETED', '2026-02-12 14:30:00', '2026-02-12', NULL, 'WEDNESDAY', 14, NOW()),
('test-user-001', 2037, 101, 'POSTPONED', '2026-02-12 18:30:00', '2026-02-12', '2026-02-13', 'WEDNESDAY', 18, NOW());

-- 목요일 (2026-02-13)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2038, 100, 'COMPLETED', '2026-02-13 10:00:00', '2026-02-13', NULL, 'THURSDAY', 10, NOW()),
('test-user-001', 2039, 101, 'COMPLETED', '2026-02-13 15:00:00', '2026-02-13', NULL, 'THURSDAY', 15, NOW());

-- 금요일 (2026-02-14)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2040, 100, 'COMPLETED', '2026-02-14 09:00:00', '2026-02-14', NULL, 'FRIDAY', 9, NOW()),
('test-user-001', 2041, 101, 'COMPLETED', '2026-02-14 14:00:00', '2026-02-14', NULL, 'FRIDAY', 14, NOW()),
('test-user-001', 2042, 100, 'POSTPONED', '2026-02-14 18:00:00', '2026-02-14', '2026-02-17', 'FRIDAY', 18, NOW());

-- 토요일 (2026-02-15)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2043, 101, 'COMPLETED', '2026-02-15 11:00:00', '2026-02-15', NULL, 'SATURDAY', 11, NOW()),
('test-user-001', 2044, 100, 'POSTPONED', '2026-02-15 15:00:00', '2026-02-15', '2026-02-17', 'SATURDAY', 15, NOW()),
('test-user-001', 2045, 101, 'POSTPONED', '2026-02-15 19:00:00', '2026-02-15', '2026-02-17', 'SATURDAY', 19, NOW());

-- 일요일 (2026-02-16)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2046, 100, 'POSTPONED', '2026-02-16 10:00:00', '2026-02-16', '2026-02-17', 'SUNDAY', 10, NOW()),
('test-user-001', 2047, 101, 'POSTPONED', '2026-02-16 14:00:00', '2026-02-16', '2026-02-17', 'SUNDAY', 14, NOW()),
('test-user-001', 2048, 100, 'POSTPONED', '2026-02-16 18:00:00', '2026-02-16', '2026-02-17', 'SUNDAY', 18, NOW()),
('test-user-001', 2049, 101, 'COMPLETED', '2026-02-16 20:00:00', '2026-02-16', NULL, 'SUNDAY', 20, NOW());

-- ========================================
-- 3주차: 2026-02-17 ~ 2026-02-23 (월~일)
-- 패턴: 지난 주 데이터 (챗봇 질의용)
-- ========================================

-- 월요일 (2026-02-17)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2050, 100, 'COMPLETED', '2026-02-17 09:00:00', '2026-02-17', NULL, 'MONDAY', 9, NOW()),
('test-user-001', 2051, 101, 'COMPLETED', '2026-02-17 14:00:00', '2026-02-17', NULL, 'MONDAY', 14, NOW()),
('test-user-001', 2052, 100, 'COMPLETED', '2026-02-17 18:00:00', '2026-02-17', NULL, 'MONDAY', 18, NOW());

-- 화요일 (2026-02-18)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2053, 100, 'COMPLETED', '2026-02-18 10:00:00', '2026-02-18', NULL, 'TUESDAY', 10, NOW()),
('test-user-001', 2054, 101, 'COMPLETED', '2026-02-18 15:00:00', '2026-02-18', NULL, 'TUESDAY', 15, NOW()),
('test-user-001', 2055, 100, 'POSTPONED', '2026-02-18 19:00:00', '2026-02-18', '2026-02-19', 'TUESDAY', 19, NOW());

-- 수요일 (2026-02-19)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2056, 101, 'COMPLETED', '2026-02-19 09:30:00', '2026-02-19', NULL, 'WEDNESDAY', 9, NOW()),
('test-user-001', 2057, 100, 'COMPLETED', '2026-02-19 14:30:00', '2026-02-19', NULL, 'WEDNESDAY', 14, NOW());

-- 목요일 (2026-02-20)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2058, 100, 'COMPLETED', '2026-02-20 10:00:00', '2026-02-20', NULL, 'THURSDAY', 10, NOW()),
('test-user-001', 2059, 101, 'COMPLETED', '2026-02-20 15:00:00', '2026-02-20', NULL, 'THURSDAY', 15, NOW()),
('test-user-001', 2060, 100, 'POSTPONED', '2026-02-20 19:00:00', '2026-02-20', '2026-02-21', 'THURSDAY', 19, NOW());

-- 금요일 (2026-02-21)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2061, 100, 'COMPLETED', '2026-02-21 09:00:00', '2026-02-21', NULL, 'FRIDAY', 9, NOW()),
('test-user-001', 2062, 101, 'COMPLETED', '2026-02-21 14:00:00', '2026-02-21', NULL, 'FRIDAY', 14, NOW()),
('test-user-001', 2063, 100, 'POSTPONED', '2026-02-21 18:00:00', '2026-02-21', '2026-02-24', 'FRIDAY', 18, NOW());

-- 토요일 (2026-02-22)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2064, 101, 'COMPLETED', '2026-02-22 11:00:00', '2026-02-22', NULL, 'SATURDAY', 11, NOW()),
('test-user-001', 2065, 100, 'POSTPONED', '2026-02-22 15:00:00', '2026-02-22', '2026-02-24', 'SATURDAY', 15, NOW()),
('test-user-001', 2066, 101, 'POSTPONED', '2026-02-22 19:00:00', '2026-02-22', '2026-02-24', 'SATURDAY', 19, NOW()),
('test-user-001', 2067, 100, 'POSTPONED', '2026-02-22 21:00:00', '2026-02-22', '2026-02-24', 'SATURDAY', 21, NOW());

-- 일요일 (2026-02-23) - 지난 주 최악의 요일
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2068, 100, 'POSTPONED', '2026-02-23 10:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 10, NOW()),
('test-user-001', 2069, 101, 'POSTPONED', '2026-02-23 12:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 12, NOW()),
('test-user-001', 2070, 100, 'POSTPONED', '2026-02-23 14:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 14, NOW()),
('test-user-001', 2071, 101, 'POSTPONED', '2026-02-23 16:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 16, NOW()),
('test-user-001', 2072, 100, 'POSTPONED', '2026-02-23 18:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 18, NOW()),
('test-user-001', 2073, 101, 'POSTPONED', '2026-02-23 20:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 20, NOW()),
('test-user-001', 2074, 100, 'POSTPONED', '2026-02-23 21:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 21, NOW()),
('test-user-001', 2075, 101, 'POSTPONED', '2026-02-23 22:00:00', '2026-02-23', '2026-02-24', 'SUNDAY', 22, NOW());

-- ========================================
-- 4주차: 2026-02-24 ~ 2026-03-04 (월~수, 현재까지)
-- 패턴: 이번 주 데이터
-- ========================================

-- 월요일 (2026-02-24)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2076, 100, 'COMPLETED', '2026-02-24 09:00:00', '2026-02-24', NULL, 'MONDAY', 9, NOW()),
('test-user-001', 2077, 101, 'COMPLETED', '2026-02-24 14:00:00', '2026-02-24', NULL, 'MONDAY', 14, NOW()),
('test-user-001', 2078, 100, 'COMPLETED', '2026-02-24 18:00:00', '2026-02-24', NULL, 'MONDAY', 18, NOW()),
('test-user-001', 2079, 101, 'COMPLETED', '2026-02-24 20:00:00', '2026-02-24', NULL, 'MONDAY', 20, NOW());

-- 화요일 (2026-02-25)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2080, 100, 'COMPLETED', '2026-02-25 10:00:00', '2026-02-25', NULL, 'TUESDAY', 10, NOW()),
('test-user-001', 2081, 101, 'COMPLETED', '2026-02-25 15:00:00', '2026-02-25', NULL, 'TUESDAY', 15, NOW()),
('test-user-001', 2082, 100, 'COMPLETED', '2026-02-25 19:00:00', '2026-02-25', NULL, 'TUESDAY', 19, NOW());

-- 수요일 (2026-02-26)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2083, 101, 'COMPLETED', '2026-02-26 09:30:00', '2026-02-26', NULL, 'WEDNESDAY', 9, NOW()),
('test-user-001', 2084, 100, 'COMPLETED', '2026-02-26 14:30:00', '2026-02-26', NULL, 'WEDNESDAY', 14, NOW());

-- 목요일 (2026-02-27)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2085, 100, 'COMPLETED', '2026-02-27 10:00:00', '2026-02-27', NULL, 'THURSDAY', 10, NOW()),
('test-user-001', 2086, 101, 'COMPLETED', '2026-02-27 15:00:00', '2026-02-27', NULL, 'THURSDAY', 15, NOW());

-- 금요일 (2026-02-28)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2087, 100, 'COMPLETED', '2026-02-28 09:00:00', '2026-02-28', NULL, 'FRIDAY', 9, NOW()),
('test-user-001', 2088, 101, 'COMPLETED', '2026-02-28 14:00:00', '2026-02-28', NULL, 'FRIDAY', 14, NOW());

-- 토요일 (2026-03-01)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2089, 101, 'COMPLETED', '2026-03-01 11:00:00', '2026-03-01', NULL, 'SATURDAY', 11, NOW()),
('test-user-001', 2090, 100, 'POSTPONED', '2026-03-01 15:00:00', '2026-03-01', '2026-03-03', 'SATURDAY', 15, NOW());

-- 일요일 (2026-03-02)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2091, 100, 'COMPLETED', '2026-03-02 10:00:00', '2026-03-02', NULL, 'SUNDAY', 10, NOW()),
('test-user-001', 2092, 101, 'POSTPONED', '2026-03-02 14:00:00', '2026-03-02', '2026-03-03', 'SUNDAY', 14, NOW()),
('test-user-001', 2093, 100, 'POSTPONED', '2026-03-02 18:00:00', '2026-03-02', '2026-03-03', 'SUNDAY', 18, NOW());

-- 월요일 (2026-03-03)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2094, 100, 'COMPLETED', '2026-03-03 09:00:00', '2026-03-03', NULL, 'MONDAY', 9, NOW()),
('test-user-001', 2095, 101, 'COMPLETED', '2026-03-03 14:00:00', '2026-03-03', NULL, 'MONDAY', 14, NOW());

-- 화요일 (2026-03-04, 오늘)
INSERT INTO user_action_logs (user_id, task_id, goals_id, action_type, action_time, due_date, postponed_to_date, day_of_week, hour_of_day, created_at)
VALUES 
('test-user-001', 2096, 100, 'COMPLETED', '2026-03-04 10:00:00', '2026-03-04', NULL, 'TUESDAY', 10, NOW()),
('test-user-001', 2097, 101, 'COMPLETED', '2026-03-04 15:00:00', '2026-03-04', NULL, 'TUESDAY', 15, NOW());

-- ========================================
-- 데이터 검증 쿼리
-- ========================================

-- 1. 전체 통계
SELECT 
    '전체 통계' as category,
    COUNT(*) as total_count,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN action_type = 'POSTPONED' THEN 1 ELSE 0 END) as postponed,
    ROUND(SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_rate
FROM user_action_logs 
WHERE user_id = 'test-user-001';

-- 2. 요일별 통계
SELECT 
    day_of_week,
    COUNT(*) as total,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN action_type = 'POSTPONED' THEN 1 ELSE 0 END) as postponed,
    ROUND(SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_rate
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

-- 3. 지난 주 (2026-02-17 ~ 2026-02-23) 통계
SELECT 
    '지난 주' as period,
    COUNT(*) as total,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN action_type = 'POSTPONED' THEN 1 ELSE 0 END) as postponed,
    ROUND(SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_rate
FROM user_action_logs 
WHERE user_id = 'test-user-001'
  AND action_time BETWEEN '2026-02-17 00:00:00' AND '2026-02-23 23:59:59';

-- 4. 지난 주 요일별 미룸 횟수 (챗봇 질의 테스트용)
SELECT 
    day_of_week,
    COUNT(*) as postponed_count
FROM user_action_logs 
WHERE user_id = 'test-user-001'
  AND action_type = 'POSTPONED'
  AND action_time BETWEEN '2026-02-17 00:00:00' AND '2026-02-23 23:59:59'
GROUP BY day_of_week
ORDER BY postponed_count DESC;

-- 5. 이번 달 (2026-02) 통계
SELECT 
    '이번 달' as period,
    COUNT(*) as total,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN action_type = 'POSTPONED' THEN 1 ELSE 0 END) as postponed,
    ROUND(SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_rate
FROM user_action_logs 
WHERE user_id = 'test-user-001'
  AND action_time BETWEEN '2026-02-01 00:00:00' AND '2026-02-28 23:59:59';

-- 6. 최근 할 일 목록 (상위 10개)
SELECT 
    task_id,
    goals_id,
    action_type,
    action_time,
    day_of_week
FROM user_action_logs 
WHERE user_id = 'test-user-001'
ORDER BY action_time DESC
LIMIT 10;

-- ========================================
-- 챗봇 테스트 질의 예시
-- ========================================

/*
테스트할 수 있는 질문들:

1. "지난 주에 내가 가장 많이 미룬 요일은 언제야?"
   → 예상 답변: 일요일 (8개)

2. "이번 달 완료율은 얼마야?"
   → 예상 답변: 약 60-70%

3. "지난 주 완료율은 얼마야?"
   → 예상 답변: 약 50-60%

4. "최근에 완료한 할 일 보여줘"
   → 예상 답변: 최근 완료한 task_id 목록

5. "요일별로 완료율이 어떻게 돼?"
   → 예상 답변: 월~금 높음, 토~일 낮음
*/
