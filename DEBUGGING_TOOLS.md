# 디버깅 도구 모음

PlanIt-InsightAI-svc의 문제 해결을 위한 디버깅 도구 및 가이드

## 📋 목차

1. [AWS 자격 증명 문제](#aws-자격-증명-문제)
2. [데이터베이스 데이터 확인](#데이터베이스-데이터-확인)
3. [챗봇 서비스 테스트](#챗봇-서비스-테스트)
4. [AI "데이터 없음" 문제](#ai-데이터-없음-문제)

---

## AWS 자격 증명 문제

### 증상
```
ExpiredTokenException: The security token included in the request is expired
```

### 해결 도구
```bash
python check_aws_credentials.py
```

### 상세 가이드
- AWS 자격 증명 상태 확인
- 임시 자격 증명 vs 장기 자격 증명 구분
- 프로필 설정 확인

### 관련 파일
- `check_aws_credentials.py`
- `.env.example`

---

## 데이터베이스 데이터 확인

### 증상
- AI가 "데이터가 없다"고 응답
- 쿼리 결과가 비어있음
- user_id 불일치 의심

### 해결 도구
```bash
python check_data.py
```

### 확인 내용
1. 데이터베이스 연결 상태
2. 모든 user_id 목록
3. test-user-001 데이터 통계
4. 최근 한 달 데이터 (오늘 기준)
5. 요일별 완료 통계
6. Tool 쿼리 시뮬레이션

### 예상 출력
```
✅ 데이터베이스 연결 성공

1. 데이터베이스에 있는 모든 user_id 목록
  - test-user-001

2. test-user-001 데이터 통계
  전체 레코드 수: 97
  완료(COMPLETED): 52
  미룸(POSTPONED): 45
```

### 관련 파일
- `check_data.py`
- `test-data-chatbot.sql` (테스트 데이터)

---

## 챗봇 서비스 테스트

### 증상
- 챗봇 API가 제대로 동작하는지 확인 필요
- Bedrock 연결 테스트 필요
- 전체 플로우 검증 필요

### 해결 도구
```bash
python test_chatbot_debug.py
```

### 테스트 내용
1. 데이터베이스 연결 확인
2. test-user-001 데이터 확인
3. Bedrock 클라이언트 초기화
4. ChatbotService 생성
5. 3가지 질의 테스트:
   - "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
   - "지난 주에 가장 많이 미룬 요일은?"
   - "이번 달 완료율은 얼마야?"

### 성공 시 출력
```
✅ 답변 생성 성공
답변: 최근 한 달 동안 완료한 할 일을 요일별로 분석해봤어요! 📊...
출처: query_user_action_logs 실행
```

### 관련 파일
- `test_chatbot_debug.py`
- `app/services/chatbot.py`
- `app/clients/bedrock_client.py`
- `app/clients/database_client.py`

---

## AI "데이터 없음" 문제

### 증상
데이터베이스에는 데이터가 있지만 AI가 "데이터가 없다"고 응답

### 빠른 진단
```bash
# 1단계: 데이터 확인
python check_data.py

# 2단계: 챗봇 직접 테스트
python test_chatbot_debug.py

# 3단계: 로그 확인
# Python 서버 로그에서 다음을 찾으세요:
# [Tool Execution] query_user_action_logs
#   User ID: <확인!>
#   Input Parameters: {...}
# [Tool] Query returned X records  <-- 0이면 문제!
```

### 가능한 원인 (우선순위)

1. **user_id 불일치 (90%)**
   - API 호출 시 사용한 user_id ≠ DB의 user_id
   - 해결: 올바른 user_id로 재호출

2. **날짜 범위 문제 (5%)**
   - Claude가 잘못된 날짜 계산
   - 해결: 로그에서 날짜 확인

3. **action_type 필터 문제 (5%)**
   - 잘못된 action_type 전달
   - 해결: 로그에서 action_type 확인

### 상세 가이드
- `TASK6_DEBUG_GUIDE.md` - 빠른 디버깅 가이드
- `DEBUG_NO_DATA_ISSUE.md` - 상세 디버깅 가이드

### 개선 사항
- ✅ 로깅 강화 (chatbot.py)
- ✅ Tool 실행 시 상세 파라미터 로깅
- ✅ 0개 레코드 반환 시 경고 메시지
- ✅ 디버깅 스크립트 3개 생성

---

## 🚀 빠른 시작

### 문제가 발생했을 때

1. **먼저 실행:**
   ```bash
   python check_data.py
   ```
   데이터베이스에 데이터가 있는지 확인

2. **그 다음:**
   ```bash
   python test_chatbot_debug.py
   ```
   챗봇 서비스가 정상 동작하는지 확인

3. **로그 확인:**
   Python 서버 로그에서 Tool Execution 부분 확인

4. **문제 해결:**
   - user_id 불일치 → 올바른 user_id로 재호출
   - AWS 자격 증명 → `python check_aws_credentials.py`
   - 데이터 없음 → `test-data-chatbot.sql` 실행

---

## 📚 전체 문서 목록

### 디버깅 도구
- `check_aws_credentials.py` - AWS 자격 증명 확인
- `check_data.py` - 데이터베이스 데이터 확인
- `test_chatbot_debug.py` - 챗봇 서비스 직접 테스트

### 가이드 문서
- `DEBUGGING_TOOLS.md` - 이 파일 (도구 모음)
- `TASK6_DEBUG_GUIDE.md` - AI "데이터 없음" 빠른 가이드
- `DEBUG_NO_DATA_ISSUE.md` - AI "데이터 없음" 상세 가이드

### 테스트 데이터
- `test-data-chatbot.sql` - 챗봇 테스트용 데이터 (4주치)

### 기타 문서
- `GRPC_SETUP_SUMMARY.md` - gRPC 설정 요약
- `GRPC_IMPLEMENTATION_GUIDE.md` - gRPC 구현 가이드
- `TESTING_GUIDE.md` - 전체 테스트 가이드
- `PHASE4_COMPLETION.md` - Phase 4 완료 보고서

---

## 💡 팁

### 로그 레벨 조정
`.env` 파일에서 로그 레벨 설정:
```
LOG_LEVEL=DEBUG  # 더 자세한 로그
LOG_LEVEL=INFO   # 기본 로그
```

### 데이터베이스 직접 확인
```sql
-- user_id 목록
SELECT DISTINCT user_id FROM user_action_logs;

-- 데이터 통계
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed
FROM user_action_logs
WHERE user_id = 'test-user-001';
```

### API 테스트
```powershell
# HTTP API (포트 8085)
$body = @{
    user_id = "test-user-001"
    query = "최근 한 달 간 완료한 할 일이 어느 요일에 많아?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8085/ai/chat/query" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## 🆘 추가 도움

문제가 계속되면 다음 정보를 제공해주세요:

1. `python check_data.py` 실행 결과 전체
2. Python 서버 로그 (Tool Execution 부분)
3. 실제 API 호출 시 사용한 JSON body
4. 수동 SQL 쿼리 실행 결과
