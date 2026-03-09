# AI "데이터 없음" 문제 디버깅 가이드

## 문제 상황
사용자가 "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"라고 질문했을 때,
데이터베이스에는 완료된 할 일 레코드가 있지만 AI가 "최근 한 달 간 완료한 할 일 데이터가 없네요"라고 응답하는 문제

## 가능한 원인

### 1. user_id 불일치 (가장 가능성 높음)
- API 호출 시 사용한 `user_id`와 DB에 저장된 `user_id`가 다를 수 있음
- 테스트 데이터는 `test-user-001`로 저장되어 있음
- 실제 API 호출 시 다른 user_id를 사용했을 가능성

### 2. 날짜 범위 계산 오류
- Claude가 "최근 한 달"을 계산할 때 잘못된 날짜 범위를 사용
- 현재 날짜: 2026-03-05 (목요일)
- 예상 범위: 2026-02-03 ~ 2026-03-05
- 실제 데이터 범위: 2026-02-03 ~ 2026-03-04

### 3. action_type 필터 문제
- Tool 정의에서 action_type='COMPLETED' 필터가 제대로 전달되지 않음
- Claude가 잘못된 action_type을 사용

### 4. 쿼리 실행 오류
- SQL 쿼리 자체는 정상이지만 파라미터 바인딩 문제
- deleted_at IS NULL 조건으로 인한 필터링

## 디버깅 단계

### Step 1: 데이터베이스 데이터 확인

```bash
# Python 가상환경 활성화 후
python check_data.py
```

이 스크립트는 다음을 확인합니다:
1. 데이터베이스에 있는 모든 user_id 목록
2. test-user-001의 전체 통계
3. 최근 한 달 데이터 (오늘 기준)
4. 요일별 완료 통계
5. Tool이 실행할 쿼리 시뮬레이션

### Step 2: Python 서버 로그 확인

gRPC 서버 또는 HTTP 서버 로그에서 다음을 찾으세요:

```
[gRPC REQUEST] QueryChatbot
  User ID: <실제 사용된 user_id>
  Query: <사용자 질문>
```

```
[Tool Execution] query_user_action_logs
  Input: {'start_date': '...', 'end_date': '...', 'action_type': '...'}
```

```
[Tool] Query returned X records
```

**중요**: Tool 실행 로그에서 반환된 레코드 수를 확인하세요!
- 0개 반환 → user_id 또는 날짜 범위 문제
- N개 반환 → Claude의 해석 문제

### Step 3: 실제 API 호출 재현

#### HTTP API 테스트 (포트 8085)

```bash
# PowerShell
$body = @{
    user_id = "test-user-001"
    query = "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8085/ai/chat/query" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

#### gRPC API 테스트 (포트 9095)

Java 서비스를 통해 테스트:

```bash
# PowerShell
$body = @{
    userId = "test-user-001"
    query = "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8084/api/v1/chat" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Step 4: 수동 SQL 쿼리 실행

데이터베이스에 직접 연결하여 확인:

```sql
-- 1. user_id 목록 확인
SELECT DISTINCT user_id FROM user_action_logs;

-- 2. test-user-001 데이터 확인
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
    MIN(action_time) as earliest,
    MAX(action_time) as latest
FROM user_action_logs
WHERE user_id = 'test-user-001'
  AND deleted_at IS NULL;

-- 3. 최근 한 달 완료 데이터 (2026-02-03 ~ 2026-03-05)
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

-- 4. 실제 사용자 ID로 테스트 (로그에서 확인한 user_id 사용)
SELECT 
    day_of_week,
    COUNT(*) as count
FROM user_action_logs
WHERE user_id = '<실제_user_id>'  -- 로그에서 확인한 값
  AND action_type = 'COMPLETED'
  AND action_time BETWEEN '2026-02-03 00:00:00' AND '2026-03-05 23:59:59'
  AND deleted_at IS NULL
GROUP BY day_of_week
ORDER BY count DESC;
```

## 해결 방법

### 해결책 1: user_id 확인 및 수정

만약 API 호출 시 다른 user_id를 사용했다면:

**옵션 A**: 올바른 user_id로 API 재호출
```json
{
  "user_id": "test-user-001",
  "query": "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
}
```

**옵션 B**: 실제 사용한 user_id로 테스트 데이터 추가
```sql
-- 실제 user_id로 데이터 복사
INSERT INTO user_action_logs 
  (user_id, task_id, goals_id, action_type, action_time, due_date, 
   postponed_to_date, day_of_week, hour_of_day, created_at)
SELECT 
  '<실제_user_id>',  -- 여기에 실제 user_id 입력
  task_id + 10000,   -- task_id 중복 방지
  goals_id,
  action_type,
  action_time,
  due_date,
  postponed_to_date,
  day_of_week,
  hour_of_day,
  NOW()
FROM user_action_logs
WHERE user_id = 'test-user-001';
```

### 해결책 2: 날짜 범위 문제

만약 Claude가 잘못된 날짜를 계산했다면, 시스템 프롬프트에 명시적 지시 추가:

```python
# chatbot.py의 system_prompt에 추가
오늘 날짜: {datetime.now().strftime('%Y-%m-%d')}

날짜 계산 규칙:
- "최근 한 달": 오늘부터 30일 전까지
- "지난 주": 지난 월요일부터 일요일까지
- "이번 주": 이번 월요일부터 오늘까지
```

### 해결책 3: Tool 정의 개선

Tool 설명을 더 명확하게 수정:

```python
{
    "toolSpec": {
        "name": "query_user_action_logs",
        "description": """사용자의 할 일 처리 로그를 조회합니다.

중요: 사용자가 "완료한 할 일", "잘한 요일", "생산적인 요일"을 물으면
반드시 action_type='COMPLETED'를 사용하세요!

예시:
- "완료를 많이 한 요일" → action_type='COMPLETED'
- "미룬 요일" → action_type='POSTPONED'
- "완료율 계산" → action_type 생략 (전체 조회)
""",
        # ... 나머지 동일
    }
}
```

### 해결책 4: 로깅 강화

더 자세한 로그를 위해 `_execute_tool` 메서드 수정:

```python
async def _execute_tool(self, tool_name: str, tool_input: Dict, user_id: str) -> Dict:
    logger.info(f"[Tool Execution] {tool_name}")
    logger.info(f"  User ID: {user_id}")  # 추가
    logger.info(f"  Input: {tool_input}")
    
    if tool_name == "query_user_action_logs":
        logger.info(f"[Tool] Querying action logs from database...")
        logger.info(f"  Parameters: user_id={user_id}, start={tool_input['start_date']}, "
                   f"end={tool_input['end_date']}, action_type={tool_input.get('action_type', 'ALL')}")
        
        results = await self.db.query_action_logs(...)
        
        logger.info(f"[Tool] Query returned {len(results)} records")
        
        # 결과 샘플 로깅 추가
        if len(results) > 0:
            logger.info(f"[Tool] Sample record: {results[0]}")
        else:
            logger.warning(f"[Tool] ⚠️ No records found! Check user_id and date range.")
        
        # ... 나머지 동일
```

## 체크리스트

디버깅 시 다음을 순서대로 확인하세요:

- [ ] `python check_data.py` 실행하여 DB 데이터 확인
- [ ] Python 서버 로그에서 실제 사용된 user_id 확인
- [ ] Tool 실행 로그에서 반환된 레코드 수 확인
- [ ] user_id가 'test-user-001'인지 확인
- [ ] 날짜 범위가 올바른지 확인 (2026-02-03 ~ 2026-03-05)
- [ ] action_type='COMPLETED'가 제대로 전달되었는지 확인
- [ ] 수동 SQL 쿼리로 데이터 존재 여부 재확인

## 예상 결과

정상 동작 시 로그:

```
[Tool Execution] query_user_action_logs
  User ID: test-user-001
  Input: {'start_date': '2026-02-03', 'end_date': '2026-03-05', 'action_type': 'COMPLETED'}

[Tool] Querying action logs from database...
[Tool] Query returned 52 records

[ChatbotService] Final answer generated
  Answer preview: 최근 한 달 동안 완료한 할 일을 요일별로 분석해봤어요! 📊

월요일에 가장 많이 완료하셨네요...
```

## 추가 도움

문제가 계속되면 다음 정보를 제공해주세요:

1. `python check_data.py` 실행 결과 전체
2. Python 서버 로그 (Tool Execution 부분)
3. 실제 API 호출 시 사용한 JSON body
4. 수동 SQL 쿼리 실행 결과
