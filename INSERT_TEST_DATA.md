# 테스트 데이터 삽입 가이드

## 📊 테스트 데이터 개요

챗봇 API를 테스트하기 위한 풍부한 사용자 행동 데이터입니다.

### 데이터 특징
- **사용자**: test-user-001
- **기간**: 2026-02-03 ~ 2026-03-04 (약 4주)
- **총 레코드**: 97개
- **패턴**: 
  - 주중(월~금): 완료율 높음
  - 주말(토~일): 미룸 많음, 특히 일요일이 최악
  - 지난 주 일요일: 8개 미룸 (테스트 질의용)

## 🚀 데이터 삽입 방법

### 방법 1: MySQL 클라이언트 사용

```bash
# MariaDB 접속
mysql -u root -p

# 데이터베이스 선택
USE plainit_db;

# SQL 파일 실행
source C:/workspace/PlanIt/PlanIt-InsightAI-svc/test-data-chatbot.sql
```

### 방법 2: PowerShell에서 직접 실행

```powershell
# SQL 파일 경로
$sqlFile = "C:\workspace\PlanIt\PlanIt-InsightAI-svc\test-data-chatbot.sql"

# MySQL 실행
mysql -u root -p plainit_db < $sqlFile
```

### 방법 3: MySQL Workbench 사용

1. MySQL Workbench 열기
2. 연결 선택
3. File → Open SQL Script
4. `test-data-chatbot.sql` 선택
5. Execute (번개 아이콘 클릭)

## ✅ 데이터 확인

삽입 후 다음 쿼리로 데이터를 확인하세요:

```sql
-- 전체 레코드 수 확인
SELECT COUNT(*) as total_records
FROM user_action_logs 
WHERE user_id = 'test-user-001';

-- 요일별 통계 확인
SELECT 
    day_of_week,
    COUNT(*) as total,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN action_type = 'POSTPONED' THEN 1 ELSE 0 END) as postponed
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
```

**예상 결과:**
```
+-------------+-------+-----------+-----------+
| day_of_week | total | completed | postponed |
+-------------+-------+-----------+-----------+
| MONDAY      |    16 |        16 |         0 |
| TUESDAY     |    15 |        13 |         2 |
| WEDNESDAY   |    10 |         8 |         2 |
| THURSDAY    |    10 |         8 |         2 |
| FRIDAY      |    11 |         8 |         3 |
| SATURDAY    |    11 |         4 |         7 |
| SUNDAY      |    14 |         3 |        11 |
+-------------+-------+-----------+-----------+
```

## 🧪 챗봇 테스트 질의

데이터 삽입 후 다음 질문들로 챗봇을 테스트할 수 있습니다:

### 1. 지난 주 미룸 패턴 분석
```json
{
  "user_id": "test-user-001",
  "query": "지난 주에 내가 가장 많이 미룬 요일은 언제야?"
}
```
**예상 답변**: "지난 주에 가장 많이 미룬 요일은 일요일이에요. 총 8개의 할 일을 미루셨네요."

### 2. 이번 달 완료율
```json
{
  "user_id": "test-user-001",
  "query": "이번 달 완료율은 얼마야?"
}
```
**예상 답변**: "이번 달 완료율은 약 65%예요."

### 3. 지난 주 완료율
```json
{
  "user_id": "test-user-001",
  "query": "지난 주 완료율은 얼마야?"
}
```
**예상 답변**: "지난 주 완료율은 약 55%예요."

### 4. 최근 완료한 할 일
```json
{
  "user_id": "test-user-001",
  "query": "최근에 완료한 할 일 보여줘"
}
```

### 5. 요일별 완료율
```json
{
  "user_id": "test-user-001",
  "query": "요일별로 완료율이 어떻게 돼?"
}
```
**예상 답변**: "월요일이 가장 높고(100%), 일요일이 가장 낮아요(21%)."

## 🔄 데이터 초기화

테스트 데이터를 삭제하고 다시 시작하려면:

```sql
-- 테스트 사용자 데이터만 삭제
DELETE FROM user_action_logs WHERE user_id = 'test-user-001';

-- 다시 삽입
source C:/workspace/PlanIt/PlanIt-InsightAI-svc/test-data-chatbot.sql
```

## 📝 테스트 시나리오

### 시나리오 1: 기본 챗봇 테스트
1. 서버 시작: `uvicorn app.main:app --reload --port 8085`
2. Swagger UI 열기: http://localhost:8085/docs
3. `/ai/chat/query` 엔드포인트 선택
4. "Try it out" 클릭
5. 위의 질의 중 하나 입력
6. "Execute" 클릭
7. 응답 확인

### 시나리오 2: 리포트 생성 테스트
1. Java Service A에서 통계 데이터 조회
2. `/ai/reports/generate` 엔드포인트 호출
3. AI 피드백 생성 확인

### 시나리오 3: 통합 테스트
1. 챗봇으로 데이터 조회
2. 리포트 생성
3. 두 결과 비교

## 💡 팁

- 데이터가 많을수록 챗봇 답변이 더 정확해집니다
- 다양한 패턴의 데이터를 추가하면 더 흥미로운 인사이트를 얻을 수 있습니다
- `goals_id`를 다르게 설정하면 주제별 분석도 가능합니다

## 🐛 문제 해결

### 데이터가 삽입되지 않는 경우
1. 테이블이 존재하는지 확인:
   ```sql
   SHOW TABLES LIKE 'user_action_logs';
   ```

2. 테이블 구조 확인:
   ```sql
   DESCRIBE user_action_logs;
   ```

3. 권한 확인:
   ```sql
   SHOW GRANTS FOR CURRENT_USER;
   ```

### 챗봇이 데이터를 찾지 못하는 경우
1. user_id가 정확한지 확인
2. 날짜 범위가 올바른지 확인
3. DB 연결 설정 확인 (.env 파일)
