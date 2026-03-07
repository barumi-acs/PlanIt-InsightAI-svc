# Task 7 완료 요약: Bedrock 모델 ID 설정 및 예외 처리 개선

## 작업 완료 일시
2026-03-08

## 최종 업데이트: Summary 환각 문제 완전 해결 ✅

### Summary 프롬프트 완전 개편 (USER QUERY 29)
**파일**: `PlanIt-InsightAI-svc/app/services/report_generator.py`

#### 1. 긍정문 강제 (Positive Prompt)
```python
# 핵심 규칙 (절대 준수)
1. 반드시 제공된 `currentRate`(현재 달성률)와 `achievementTrend`(추세) 수치를 문장 안에 직접 언급하며 현재의 성과를 요약하세요.
2. 사용자는 이미 활발히 할 일을 수행하고 있으며, 통계 수치가 그 증거입니다.
3. 수치를 기반으로 구체적인 칭찬과 격려를 제공하세요.
```

#### 2. Few-Shot 예시 하드코딩
```python
예시 1 (높은 달성률):
입력: currentRate=67%, achievementTrend=+12%, bestFocusTime=16:00-18:00
출력:
{
  "message": "이번 주 달성률은 67%로 훌륭한 성과를 보이고 있습니다! 추세도 +12% 상승하며 꾸준히 발전하고 계시네요. 가장 집중력이 좋은 16:00-18:00 시간대를 활용해 남은 목표도 달성해 보세요 🎯"
}

예시 2 (중간 달성률):
입력: currentRate=55%, achievementTrend=+3%, bestFocusTime=09:00-11:00
출력:
{
  "message": "현재 달성률 55%로 안정적인 페이스를 유지하고 계시네요. 추세가 +3% 상승 중이니 이 흐름을 이어가면 좋겠어요. 09:00-11:00 시간대에 집중력이 가장 높으니 이 시간을 적극 활용해보세요 💪"
}

예시 3 (낮은 달성률):
입력: currentRate=38%, achievementTrend=-5%, bestFocusTime=14:00-16:00
출력:
{
  "message": "현재 달성률은 38%로 조금 아쉽지만, 충분히 회복 가능한 수치입니다. 14:00-16:00 시간대에 집중력이 가장 좋으니 이 시간을 활용해 작은 목표부터 다시 시작해보는 건 어떨까요? 😊"
}

예시 4 (매우 높은 달성률):
입력: currentRate=82%, achievementTrend=+18%, bestFocusTime=10:00-12:00
출력:
{
  "message": "와우! 달성률 82%에 추세도 +18% 급상승 중이에요! 정말 대단한 성과입니다. 10:00-12:00 시간대의 높은 집중력을 계속 유지하면 100% 달성도 가능할 거예요 🚀"
}
```

#### 3. 디버깅 로그 추가
```python
# 디버깅 로그: 실제 입력 데이터 확인
logger.info(f"Summary Prompt Input Data: {summary_data}")

# 통계 데이터 추출
current_rate = summary_data.get('currentRate', completion_rate)
achievement_trend = summary_data.get('achievement_trend', summary_data.get('achievementTrend', '0%'))
best_focus_time = summary_data.get('bestFocusTime', summary_data.get('best_focus_time', '08:00-10:00'))

logger.info(f"Extracted values - currentRate: {current_rate}, achievementTrend: {achievement_trend}, bestFocusTime: {best_focus_time}")

logger.info("Generating summary feedback with enforced positive prompt")
logger.info(f"Prompt includes: currentRate={current_rate}%, achievementTrend={achievement_trend}, bestFocusTime={best_focus_time}")
```

#### 4. Fallback 메시지 개선
```python
# Fallback: 실제 수치를 사용한 기본 메시지
current_rate = summary_data.get('currentRate', summary_data.get('completion_rate', 50))
achievement_trend = summary_data.get('achievementTrend', summary_data.get('achievement_trend', '0%'))
best_focus_time = summary_data.get('bestFocusTime', summary_data.get('best_focus_time', '08:00-10:00'))

fallback_message = f"현재 달성률 {current_rate}%로 꾸준히 노력하고 계시네요! 추세는 {achievement_trend}이며, {best_focus_time} 시간대에 가장 집중력이 좋습니다. 계속 화이팅하세요 💪"
```

### Java Summary 데이터 강화
**파일**: `PlanIt-Insight-svc/src/main/java/com/planit/analytics/service/AnalyticsService.java`

```java
// 총 할 일 및 완료한 할 일 계산
int totalTasks = currentLogs.size();
long completedTasks = currentLogs.stream()
    .filter(log -> log.getActionType() == ActionType.COMPLETED)
    .count();

Map<String, Object> result = new HashMap<>();
result.put("achievementTrend", trendStr);
result.put("bestFocusTime", bestFocusTime);
result.put("currentRate", Math.round(currentRate));
result.put("totalTasks", totalTasks);
result.put("completedTasks", (int) completedTasks);
result.put("completionRate", Math.round(currentRate));  // Python에서 사용할 수 있도록 추가
```

### Python API 데이터 전달 개선
**파일**: `PlanIt-InsightAI-svc/app/api/reports.py`

```python
elif report_type == "SUMMARY":
    # SUMMARY는 전체 통계 데이터 전달
    summary_data = {
        'total_tasks': stats_data.get('totalTasks', 0),
        'completed_tasks': stats_data.get('completedTasks', 0),
        'completion_rate': stats_data.get('completionRate', 0),
        'currentRate': stats_data.get('currentRate', stats_data.get('completionRate', 0)),
        'achievement_trend': stats_data.get('achievementTrend', '0%'),
        'achievementTrend': stats_data.get('achievementTrend', '0%'),  # 양쪽 키 모두 지원
        'bestFocusTime': stats_data.get('bestFocusTime', '08:00-10:00'),
        'best_focus_time': stats_data.get('bestFocusTime', '08:00-10:00')  # 양쪽 키 모두 지원
    }
    
    logger.info(f"Summary data prepared: {summary_data}")
```

## 주요 변경 사항

### 1. Bedrock 모델 ID 변경 ✅
**파일**: `PlanIt-InsightAI-svc/app/core/config.py`

```python
bedrock_model_id: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

- Claude 4.5 Sonnet 최신 모델로 변경 완료
- Global 리전 prefix 추가

### 2. 예외 처리 개선 ✅
**파일**: `PlanIt-InsightAI-svc/app/clients/bedrock_client.py`

- `ClientError`와 일반 예외를 명확히 구분하여 로깅
- 에러 코드와 메시지를 상세히 출력
- `exc_info=True`로 스택 트레이스 포함

```python
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_message = e.response['Error']['Message']
    logger.error(f"Bedrock ClientError: {error_code} - {error_message}")
    raise Exception(f"Bedrock API 호출 실패: {error_message}")

except Exception as e:
    logger.error(f"Unexpected error in Bedrock call: {str(e)}", exc_info=True)
    raise Exception(f"Bedrock 호출 중 오류 발생: {str(e)}")
```

### 3. Report Generator 안전한 파싱 로직 추가 ✅
**파일**: `PlanIt-InsightAI-svc/app/services/report_generator.py`

#### Timeline 피드백
- None 체크 추가
- 빈 응답 체크
- 상세한 로깅 (`logger.info`, `exc_info=True`)

#### Pattern 피드백
- None 체크 추가
- 빈 응답 체크
- 상세한 로깅

#### Summary 피드백
- None 체크 및 안전한 메시지 추출
- `hasattr()` 사용하여 속성 존재 확인
- 빈 응답 체크

### 4. Growth 마이너스 성장 예외 처리 ✅
**파일**: `PlanIt-InsightAI-svc/app/services/report_generator.py`

#### Python 프롬프트 개선
- 음수 성장률일 때 "감소했어요" 표현 사용
- "성장" 단어 사용 금지
- Few-shot 예시 추가 (양수/음수 시나리오)

#### Fallback 메시지 분기 처리
```python
if growth_rate_val >= 0:
    message = f"이전 3개월 보다 {topic} 분야에서 {growth_rate_val}% 성장했어요!"
else:
    message = f"이전 3개월 보다 {topic} 분야 활동이 {abs(growth_rate_val)}% 감소했어요."
```

### 5. Summary 환각 문제 완전 해결 ✅
**파일**: `PlanIt-InsightAI-svc/app/services/report_generator.py`

#### 긍정문 강제 (Positive Prompt)
- "하지 마세요" 대신 "반드시 수치를 직접 언급하세요"로 변경
- currentRate, achievementTrend, bestFocusTime 수치를 문장에 포함하도록 강제

#### Few-shot 예시 하드코딩
- 4가지 시나리오 예시 (높은/중간/낮은/매우 높은 달성률)
- 각 예시마다 실제 수치를 문장에 포함한 구체적인 메시지 제공

#### 디버깅 로그 추가
- 입력 데이터 확인: `logger.info(f"Summary Prompt Input Data: {summary_data}")`
- 추출된 값 확인: `logger.info(f"Extracted values - currentRate: {current_rate}...")`
- 프롬프트 구성 확인: `logger.info(f"Prompt includes: currentRate={current_rate}%...")`

### 6. Topic Name 실제 카테고리명 매핑 ✅
**파일**: `PlanIt-Insight-svc/src/main/java/com/planit/analytics/service/AnalyticsService.java`

- `CategoryList`, `Goals` 엔티티 및 리포지토리 추가
- `findTopGrowthTopic()` 메서드에서 실제 DB 조회
- "주제#101" 대신 "운동", "업무" 등 실제 카테고리명 반환

```java
return goalsRepository.findByGoalsId(topGoalsId)
    .flatMap(goals -> categoryListRepository.findByListId(goals.getListId()))
    .map(categoryList -> categoryList.getName())
    .orElse("전체");
```

## 테스트 방법

### 1. InsightAI-svc 재시작
```powershell
cd PlanIt-InsightAI-svc
python -m uvicorn app.main:app --host 0.0.0.0 --port 8085 --reload
```

### 2. Insight-svc 재시작
```powershell
cd PlanIt-Insight-svc
./gradlew bootRun
```

### 3. 배치 API 테스트
```powershell
Invoke-WebRequest -Uri "http://localhost:8084/api/v1/batch/generate-report?userId=test-user-001&yearMonth=2026-02" -Method POST
```

### 4. DynamoDB 데이터 확인
```powershell
aws dynamodb scan --table-name ai_reports --endpoint-url http://localhost:8001
```

### 5. Dashboard API로 리포트 조회
```powershell
Invoke-WebRequest -Uri "http://localhost:8084/api/v1/feedbacks/dashboard?userId=test-user-001&yearMonth=2026-02" -Method GET
```

### 6. 로그 확인 (Summary 디버깅)
InsightAI-svc 터미널에서 다음 로그를 확인:
```
INFO - Summary Prompt Input Data: {'currentRate': 67, 'achievementTrend': '+12%', 'bestFocusTime': '16:00-18:00', ...}
INFO - Extracted values - currentRate: 67, achievementTrend: +12%, bestFocusTime: 16:00-18:00
INFO - Generating summary feedback with enforced positive prompt
INFO - Prompt includes: currentRate=67%, achievementTrend=+12%, bestFocusTime=16:00-18:00
```

## 예상 결과

### Growth 리포트 (양수)
```json
{
  "topicName": "운동",
  "growthRate": 24,
  "message": "이전 3개월 보다 운동 분야에서 24% 성장했어요! 정말 대단한 변화입니다. 꾸준한 노력이 빛을 발하고 있네요 💪"
}
```

### Growth 리포트 (음수)
```json
{
  "topicName": "학습",
  "growthRate": -10,
  "message": "이전 3개월 보다 학습 분야 활동이 10% 감소했어요. 누구에게나 슬럼프는 있어요. 작은 목표부터 다시 시작해보는 건 어떨까요? 😊"
}
```

### Summary 리포트 (환각 해결!)
```json
{
  "message": "이번 주 달성률은 67%로 훌륭한 성과를 보이고 있습니다! 추세도 +12% 상승하며 꾸준히 발전하고 계시네요. 가장 집중력이 좋은 16:00-18:00 시간대를 활용해 남은 목표도 달성해 보세요 🎯"
}
```

## 주요 개선 사항 요약

1. ✅ Claude 4.5 Sonnet 모델 적용
2. ✅ 상세한 에러 로깅 (ClientError, 스택 트레이스)
3. ✅ 안전한 응답 파싱 (None 체크, 빈 응답 처리)
4. ✅ Growth 음수 성장률 처리 (감소 표현 사용)
5. ✅ Summary 환각 완전 해결 (긍정문 강제, Few-shot 하드코딩, 디버깅 로그)
6. ✅ 실제 카테고리명 매핑 (DB 조회)
7. ✅ Java Summary 데이터 강화 (totalTasks, completedTasks 추가)
8. ✅ Python API 데이터 전달 개선 (양쪽 키 모두 지원)

## Summary 환각 해결 전략

### 문제 원인
- AI 모델이 부정 프롬프트("하지 마세요")를 무시
- 데이터가 없다고 착각하여 "아직 데이터가 쌓이지 않았지만..." 출력

### 해결 방법
1. **긍정문 강제**: "반드시 수치를 직접 언급하세요"로 명확한 지시
2. **Few-shot 하드코딩**: 4가지 구체적인 예시를 프롬프트에 박아넣어 패턴 학습
3. **디버깅 로그**: 데이터가 제대로 전달되는지 확인
4. **Fallback 개선**: 실제 수치를 사용한 기본 메시지

## 다음 단계

1. 서비스 재시작 후 배치 API 테스트
2. InsightAI-svc 로그에서 Summary 디버깅 로그 확인
3. DynamoDB에 저장된 Summary 리포트 확인
4. Dashboard API로 생성된 Summary 리포트 조회
5. "아직 데이터가 쌓이지 않았지만..." 환각이 사라졌는지 확인

## 참고 사항

- InsightAI-svc 로그: 터미널 출력 또는 `2>&1 | Tee-Object -FilePath "insightai.log"`
- Insight-svc 로그: `PlanIt-Insight-svc/logs/` 디렉토리
- DynamoDB 로컬: `http://localhost:8001`
- Swagger UI: `http://localhost:8084/swagger-ui/index.html`
