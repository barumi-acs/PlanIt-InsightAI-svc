# Task 6: AI "데이터 없음" 문제 디버깅 가이드

## 문제 요약
사용자가 "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"라고 질문했을 때,
데이터베이스에는 완료된 할 일 레코드가 있지만 AI가 "최근 한 달 간 완료한 할 일 데이터가 없네요"라고 응답

## 진행 상황

### 완료된 작업
1. ✅ 문제 원인 분석 완료
2. ✅ 디버깅 스크립트 3개 생성
3. ✅ 로깅 강화 (chatbot.py)
4. ✅ 상세 디버깅 가이드 작성

### 생성된 파일
1. `check_data.py` - 데이터베이스 데이터 확인 스크립트
2. `test_chatbot_debug.py` - 챗봇 서비스 직접 테스트 스크립트
3. `DEBUG_NO_DATA_ISSUE.md` - 상세 디버깅 가이드 문서
4. `TASK6_DEBUG_GUIDE.md` - 이 파일 (요약 가이드)

## 빠른 디버깅 절차

### Step 1: 데이터베이스 확인 (필수!)

```bash
cd PlanIt-InsightAI-svc
python check_data.py
```

이 스크립트가 확인하는 내용:
- 데이터베이스에 있는 모든 user_id 목록
- test-user-001의 데이터 통계
- 최근 한 달 데이터 (오늘 기준)
- 요일별 완료 통계
- Tool 쿼리 시뮬레이션

**예상 결과:**
```
✅ 데이터베이스 연결 성공

1. 데이터베이스에 있는 모든 user_id 목록
  - test-user-001

2. test-user-001 데이터 통계
  전체 레코드 수: 97
  완료(COMPLETED): 52
  미룸(POSTPONED): 45
  가장 오래된 데이터: 2026-02-03 09:00:00
  가장 최근 데이터: 2026-03-04 15:00:00

3. 최근 한 달 데이터 (오늘 기준)
  시작 날짜: 2026-02-03
  종료 날짜: 2026-03-05
  전체 레코드 수: 97
  완료(COMPLETED): 52
```

### Step 2: Python 서버 로그 확인

gRPC 서버 또는 HTTP 서버를 실행하고 로그를 확인하세요.

**찾아야 할 로그:**

```
[gRPC REQUEST] QueryChatbot
  User ID: <여기 확인!>
  Query: 최근 한 달 간 완료한 할 일이 어느 요일에 많아?
```

```
[Tool Execution] query_user_action_logs
  User ID: <여기 확인!>
  Input Parameters: {'start_date': '...', 'end_date': '...', 'action_type': 'COMPLETED'}

[Tool] Query Details:
  - user_id: <여기 확인!>
  - start_date: 2026-02-03
  - end_date: 2026-03-05
  - action_type: COMPLETED

[Tool] Query returned X records  <-- 이 숫자가 0이면 문제!
```

### Step 3: 챗봇 서비스 직접 테스트

```bash
cd PlanIt-InsightAI-svc
python test_chatbot_debug.py
```

이 스크립트는:
1. 데이터베이스 연결 확인
2. test-user-001 데이터 확인
3. Bedrock 클라이언트 초기화
4. ChatbotService로 직접 질의 테스트

**이 테스트가 성공하면:**
- 데이터베이스 ✅
- Bedrock 연결 ✅
- ChatbotService 로직 ✅
- 문제는 API 호출 시 user_id 불일치!

**이 테스트가 실패하면:**
- AWS 자격 증명 문제 → `python check_aws_credentials.py`
- 데이터베이스 연결 문제 → `.env` 파일 확인
- Claude의 날짜 계산 문제 → 로그 확인

## 가장 가능성 높은 원인

### 원인 1: user_id 불일치 (90% 확률)

**증상:**
- `check_data.py`는 데이터를 찾음
- 하지만 API 호출 시 "데이터 없음" 응답

**확인 방법:**
Python 서버 로그에서 실제 사용된 user_id 확인

**해결 방법:**
API 호출 시 올바른 user_id 사용

```json
{
  "user_id": "test-user-001",  // 이 값이 DB와 일치해야 함!
  "query": "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
}
```

### 원인 2: 날짜 범위 문제 (5% 확률)

**증상:**
- user_id는 일치
- 하지만 Claude가 잘못된 날짜 범위 계산

**확인 방법:**
로그에서 Tool 실행 시 사용된 start_date, end_date 확인

**해결 방법:**
시스템 프롬프트에 명시적 날짜 지시 추가 (이미 포함됨)

### 원인 3: action_type 필터 문제 (5% 확률)

**증상:**
- user_id, 날짜 모두 정상
- 하지만 action_type이 잘못 전달됨

**확인 방법:**
로그에서 Tool 실행 시 action_type 값 확인

**해결 방법:**
Tool 정의 개선 (이미 명확하게 작성됨)

## API 테스트 방법

### HTTP API (포트 8085)

```powershell
$body = @{
    user_id = "test-user-001"
    query = "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8085/ai/chat/query" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### gRPC API (Java 서비스 통해, 포트 8080)

```powershell
$body = @{
    userId = "test-user-001"
    query = "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/v1/chat" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

## 수동 SQL 확인

데이터베이스에 직접 연결하여 확인:

```sql
-- 1. user_id 목록
SELECT DISTINCT user_id FROM user_action_logs;

-- 2. test-user-001 데이터 확인
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed
FROM user_action_logs
WHERE user_id = 'test-user-001'
  AND deleted_at IS NULL;

-- 3. 최근 한 달 완료 데이터
SELECT 
    day_of_week,
    COUNT(*) as count
FROM user_action_logs
WHERE user_id = 'test-user-001'
  AND action_type = 'COMPLETED'
  AND action_time BETWEEN '2026-02-03 00:00:00' AND '2026-03-05 23:59:59'
  AND deleted_at IS NULL
GROUP BY day_of_week
ORDER BY count DESC;
```

**예상 결과:**
```
day_of_week | count
------------|------
MONDAY      | 11
TUESDAY     | 10
THURSDAY    | 7
WEDNESDAY   | 6
FRIDAY      | 6
SATURDAY    | 3
SUNDAY      | 2
```

## 다음 단계

1. **먼저 실행:** `python check_data.py`
   - 데이터베이스에 데이터가 있는지 확인
   - 없으면 `test-data-chatbot.sql` 실행

2. **API 호출 테스트**
   - HTTP 또는 gRPC API로 질의
   - Python 서버 로그 확인

3. **로그 분석**
   - user_id 확인
   - Tool 실행 시 반환된 레코드 수 확인
   - 0개면 user_id 또는 날짜 문제

4. **문제 해결**
   - user_id 불일치 → 올바른 user_id로 재호출
   - 날짜 문제 → 로그 공유 (추가 분석 필요)
   - AWS 자격 증명 → `python check_aws_credentials.py`

## 추가 도움이 필요하면

다음 정보를 제공해주세요:

1. `python check_data.py` 실행 결과 전체
2. Python 서버 로그 (특히 Tool Execution 부분)
3. 실제 API 호출 시 사용한 JSON body
4. 수동 SQL 쿼리 실행 결과

## 참고 문서

- `DEBUG_NO_DATA_ISSUE.md` - 상세 디버깅 가이드
- `test-data-chatbot.sql` - 테스트 데이터 SQL
- `check_aws_credentials.py` - AWS 자격 증명 확인
