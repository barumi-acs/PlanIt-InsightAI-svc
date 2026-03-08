# Tool Use 워크플로우 수정 완료

## 문제 상황

Bedrock Converse API의 Tool Use 기능 사용 시 다음 에러 발생:

```
ValidationException: Expected toolResult blocks at messages.2.content for the following Ids: tooluse_x0...
```

## 원인 분석

AI가 `toolUse`를 요청했을 때, 도구 실행 후 `toolResult` 블록을 Bedrock에 다시 전달하는 후속 처리가 정확하지 않았음:

1. **Assistant 메시지 추가 누락**: Tool Use를 포함한 assistant의 응답을 대화 컨텍스트에 먼저 추가해야 함
2. **toolResult 포맷 불일치**: toolUseId 매핑이 정확하지 않음
3. **stopReason 분기 처리 부족**: `tool_use`와 `end_turn`을 명확히 구분하지 않음

## 해결 방법

### 1. stopReason 기반 명확한 분기 처리

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

```python
# Assistant의 응답(toolUse 포함)을 대화 컨텍스트에 추가
assistant_message = response['output']['message']
messages.append({
    "role": "assistant",
    "content": assistant_message['content']
})
```

### 3. 모든 toolUse 블록 처리 및 정확한 toolResult 생성

```python
# 모든 toolUse 블록 처리
tool_results = []
for content_block in assistant_message['content']:
    if 'toolUse' in content_block:
        tool_use = content_block['toolUse']
        tool_use_id = tool_use['toolUseId']
        tool_name = tool_use['name']
        tool_input = tool_use.get('input', {})
        
        # Tool 실행
        tool_result = await self._execute_tool(
            tool_name=tool_name,
            tool_input=tool_input,
            user_id=user_id
        )
        
        # toolResult 블록 생성 (Bedrock API 명세에 맞춤)
        tool_results.append({
            "toolResult": {
                "toolUseId": tool_use_id,
                "content": [
                    {"json": tool_result}
                ]
            }
        })

# User 역할로 toolResult 전달
messages.append({
    "role": "user",
    "content": tool_results
})
```

## Bedrock Tool Use 워크플로우

### 정상적인 대화 흐름

```
1. User → Bedrock: 질문 전송
   messages = [{"role": "user", "content": [{"text": "질문"}]}]

2. Bedrock → Assistant: Tool Use 요청
   stopReason = "tool_use"
   content = [{"toolUse": {"toolUseId": "...", "name": "...", "input": {...}}}]

3. Assistant 메시지 추가
   messages.append({"role": "assistant", "content": [toolUse 블록]})

4. Tool 실행 및 결과 추가
   messages.append({"role": "user", "content": [{"toolResult": {...}}]})

5. User → Bedrock: toolResult 포함하여 재호출
   (3-4단계 반복 가능)

6. Bedrock → Assistant: 최종 답변
   stopReason = "end_turn"
   content = [{"text": "최종 답변"}]
```

## 수정된 파일

- `PlanIt-InsightAI-svc/app/services/chatbot.py`
  - `process_query` 메서드의 Tool Use 루프 로직 완전 재작성
  - stopReason 기반 명확한 분기 처리
  - Assistant 메시지 추가 → Tool 실행 → toolResult 추가 순서 보장
  - 다중 toolUse 블록 처리 지원

## 테스트 방법

### 1. 단위 테스트

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

브라우저에서 `http://localhost:8085/docs` 접속하여 `/ai/chat/query` 엔드포인트 테스트

## 예상 결과

### 성공 시 로그

```
[ChatbotService] Iteration 1/5
[ChatbotService] Stop reason: tool_use
[ChatbotService] Tool use detected, processing...
[ChatbotService] Executing tool: query_user_action_logs
  Tool Use ID: tooluse_abc123...
  Tool Input: {'start_date': '2026-03-01', 'end_date': '2026-03-07', 'action_type': 'POSTPONED'}
[Tool Execution] query_user_action_logs
[Tool] Query returned 15 records
[ChatbotService] Tool results added to context, continuing conversation...
[ChatbotService] Iteration 2/5
[ChatbotService] Stop reason: end_turn
[ChatbotService] Final answer generated
```

### 성공 응답 예시

```json
{
  "answer": "지난 주 데이터를 분석한 결과, 일요일에 할 일을 가장 많이 미루셨네요 (8건). 그 다음으로는 토요일(5건), 금요일(3건) 순입니다. 주말에 미루는 경향이 있으시네요. 주말에도 작은 목표를 설정해보시는 건 어떨까요? 😊",
  "sources": ["query_user_action_logs 실행"],
  "generated_at": "2026-03-08T10:30:00"
}
```

## 주의사항

1. **AWS 자격 증명**: Bedrock API 호출을 위해 유효한 AWS 자격 증명 필요
2. **데이터베이스 연결**: MariaDB 연결 정보가 `.env` 파일에 올바르게 설정되어야 함
3. **무한 루프 방지**: `max_iterations=5`로 제한되어 있음
4. **다중 Tool Use**: 한 번의 응답에 여러 toolUse가 있을 수 있으므로 모두 처리해야 함

## 참고 자료

- [AWS Bedrock Converse API 문서](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Boto3 Bedrock Runtime 문서](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
- [Claude Tool Use 가이드](https://docs.anthropic.com/claude/docs/tool-use)
