# TASK 8: Chatbot Tool Use 처리 로직 수정 완료

## 작업 개요

Bedrock Converse API의 Tool Use 워크플로우에서 `toolResult` 블록 누락 문제를 해결했습니다.

## 문제 상황

```
ValidationException: Expected toolResult blocks at messages.2.content for the following Ids: tooluse_x0...
```

AI가 `toolUse`를 요청했는데, 도구 실행 후 `toolResult` 블록을 Bedrock에 다시 전달하는 후속 처리가 정확하지 않아 발생한 에러입니다.

## 핵심 수정 사항

### 1. stopReason 기반 명확한 분기 처리

기존 코드는 `has_tool_use()` 메서드만으로 판단했으나, Bedrock API의 `stopReason`을 명시적으로 확인하도록 수정:

```python
stop_reason = response.get('stopReason')

if stop_reason == 'tool_use' or self.bedrock.has_tool_use(response):
    # Tool Use 처리
elif stop_reason == 'end_turn':
    # 최종 답변 반환
else:
    # 예상치 못한 상황 처리
```

### 2. Assistant 메시지 먼저 추가

Tool Use를 포함한 assistant의 응답을 대화 컨텍스트에 먼저 추가:

```python
# Assistant의 응답(toolUse 포함)을 대화 컨텍스트에 추가
assistant_message = response['output']['message']
messages.append({
    "role": "assistant",
    "content": assistant_message['content']
})
```

### 3. 정확한 toolResult 포맷 생성

각 `toolUse` 블록에 대해 정확히 매칭되는 `toolUseId`를 가진 `toolResult` 블록 생성:

```python
# 모든 toolUse 블록 처리
tool_results = []
for content_block in assistant_message['content']:
    if 'toolUse' in content_block:
        tool_use = content_block['toolUse']
        tool_use_id = tool_use['toolUseId']
        
        # Tool 실행
        tool_result = await self._execute_tool(...)
        
        # toolResult 블록 생성 (Bedrock API 명세에 맞춤)
        tool_results.append({
            "toolResult": {
                "toolUseId": tool_use_id,
                "content": [{"json": tool_result}]
            }
        })

# User 역할로 toolResult 전달
messages.append({
    "role": "user",
    "content": tool_results
})
```

## Bedrock Tool Use 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User → Bedrock: 질문 전송                                │
│    messages = [{"role": "user", "content": [{"text": ...}]}]│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Bedrock → Assistant: Tool Use 요청                       │
│    stopReason = "tool_use"                                  │
│    content = [{"toolUse": {...}}]                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Assistant 메시지 추가 (중요!)                            │
│    messages.append({"role": "assistant", "content": [...]}) │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Tool 실행 및 결과 추가                                   │
│    messages.append({"role": "user", "content": [toolResult]})│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. User → Bedrock: toolResult 포함하여 재호출               │
│    (3-4단계 반복 가능)                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Bedrock → Assistant: 최종 답변                           │
│    stopReason = "end_turn"                                  │
│    content = [{"text": "최종 답변"}]                        │
└─────────────────────────────────────────────────────────────┘
```

## 수정된 파일

- `PlanIt-InsightAI-svc/app/services/chatbot.py`
  - `process_query()` 메서드의 Tool Use 루프 로직 완전 재작성
  - stopReason 기반 명확한 분기 처리 추가
  - Assistant 메시지 → Tool 실행 → toolResult 추가 순서 보장
  - 다중 toolUse 블록 처리 지원
  - 상세한 로깅 추가

## 테스트 방법

### 1. 단위 테스트 스크립트 실행

```bash
cd PlanIt-InsightAI-svc
python test_tool_use_fix.py
```

### 2. FastAPI 서버 실행

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8085 --reload
```

### 3. API 호출 테스트

```bash
curl -X POST "http://localhost:8085/ai/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-001",
    "query": "지난 주에 어느 요일에 할 일을 가장 많이 미뤘나요?"
  }'
```

### 4. Swagger UI 테스트

브라우저에서 `http://localhost:8085/docs` 접속

## 예상 결과

### 성공 시 로그

```
[ChatbotService] Iteration 1/5
[Bedrock] Calling Converse API
  Model: global.anthropic.claude-sonnet-4-5-20250929-v1:0
  Messages: 1
  Tools: 4
[Bedrock] Response received
  Stop Reason: tool_use
[ChatbotService] Stop reason: tool_use
[ChatbotService] Tool use detected, processing...
[ChatbotService] Executing tool: query_user_action_logs
  Tool Use ID: tooluse_abc123...
  Tool Input: {'start_date': '2026-03-01', 'end_date': '2026-03-07', 'action_type': 'POSTPONED'}
[Tool Execution] query_user_action_logs
[Tool] Query returned 15 records
[ChatbotService] Tool results added to context, continuing conversation...
[ChatbotService] Iteration 2/5
[Bedrock] Calling Converse API
  Messages: 3
[Bedrock] Response received
  Stop Reason: end_turn
[ChatbotService] Stop reason: end_turn
[ChatbotService] Final answer generated
  Answer length: 156 chars
  Sources used: query_user_action_logs 실행
```

### 성공 응답 예시

```json
{
  "answer": "지난 주 데이터를 분석한 결과, 일요일에 할 일을 가장 많이 미루셨네요 (8건). 그 다음으로는 토요일(5건), 금요일(3건) 순입니다. 주말에 미루는 경향이 있으시네요. 주말에도 작은 목표를 설정해보시는 건 어떨까요? 😊",
  "sources": ["query_user_action_logs 실행"],
  "generated_at": "2026-03-08T10:30:00.123456"
}
```

## 주요 개선 사항

1. **정확한 API 명세 준수**: Bedrock Converse API의 Tool Use 워크플로우를 정확히 구현
2. **다중 Tool Use 지원**: 한 번의 응답에 여러 toolUse가 있어도 모두 처리
3. **명확한 로깅**: 각 단계마다 상세한 로그 출력으로 디버깅 용이
4. **예외 상황 처리**: 예상치 못한 stopReason에 대한 fallback 처리
5. **무한 루프 방지**: max_iterations=5로 제한

## 참고 문서

- `TOOL_USE_FIX.md`: 상세한 기술 문서
- `test_tool_use_fix.py`: 검증 스크립트
- [AWS Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)

## 다음 단계

1. FastAPI 서버 실행하여 실제 테스트
2. 다양한 질의 패턴으로 Tool Use 동작 검증
3. 프론트엔드와 통합 테스트
4. 프로덕션 배포

---

**작업 완료 일시**: 2026-03-08  
**상태**: ✅ 완료  
**테스트**: 코드 검증 완료, 실제 API 테스트 필요
