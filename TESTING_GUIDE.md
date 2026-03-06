# 실제 서비스 테스트 가이드

## 🚀 방법 1: 로컬 FastAPI 서버 실행 (추천)

### 1단계: 서버 시작

```bash
cd PlanIt-InsightAI-svc
uvicorn app.main:app --reload --port 8085
```

서버가 시작되면 다음과 같은 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://127.0.0.1:8085 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2단계: API 문서 확인

브라우저에서 다음 URL을 열어보세요:
- **Swagger UI**: http://localhost:8085/docs
- **ReDoc**: http://localhost:8085/redoc
- **Health Check**: http://localhost:8085/health

### 3단계: API 테스트

#### 3-1. Health Check 테스트

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8085/health" -Method Get | ConvertTo-Json
```

**예상 응답:**
```json
{
  "status": "healthy",
  "service": "PlanIt-InsightAI-svc",
  "version": "1.0.0",
  "timestamp": "2026-03-04T...",
  "environment": "development"
}
```

#### 3-2. 리포트 생성 API 테스트

**PowerShell:**
```powershell
$body = @{
    user_id = "USER123"
    year_month = "2026-02"
    week = 9
    stats_data = @{
        growth = @{
            topic_name = "운동"
            growth_rate = 24
            previous_completion_rate = 65
            current_completion_rate = 89
        }
        timeline = @{
            chart_data = @(
                @{ month = "2025-11"; completion_rate = 45 },
                @{ month = "2025-12"; completion_rate = 60 },
                @{ month = "2026-01"; completion_rate = 72 },
                @{ month = "2026-02"; completion_rate = 89 }
            )
        }
        pattern = @{
            daily_stats = @(
                @{ day = "MONDAY"; total = 10; completed = 8; postponed = 2 },
                @{ day = "TUESDAY"; total = 12; completed = 10; postponed = 2 },
                @{ day = "SUNDAY"; total = 15; completed = 7; postponed = 8 }
            )
        }
        summary = @{
            total_tasks = 84
            completed_tasks = 67
            completion_rate = 79.8
            achievement_trend = "+12%"
        }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8085/ai/reports/generate" -Method Post -Body $body -ContentType "application/json" | ConvertTo-Json -Depth 10
```

#### 3-3. 챗봇 API 테스트

**PowerShell:**
```powershell
$body = @{
    user_id = "USER123"
    query = "지난 주에 내가 가장 많이 미룬 요일은 언제야?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8085/ai/chat/query" -Method Post -Body $body -ContentType "application/json" | ConvertTo-Json
```

### 4단계: Swagger UI에서 직접 테스트 (가장 쉬움!)

1. http://localhost:8085/docs 열기
2. 원하는 API 엔드포인트 클릭
3. "Try it out" 버튼 클릭
4. 요청 데이터 입력
5. "Execute" 버튼 클릭
6. 응답 확인

---

## 🐳 방법 2: Docker 컨테이너로 실행

### 1단계: Docker 이미지 빌드

```bash
cd PlanIt-InsightAI-svc
docker build -t planit-insightai-svc:latest .
```

### 2단계: 컨테이너 실행

```bash
docker run -d `
  --name planit-insightai-svc `
  -p 8085:8085 `
  -e AWS_REGION=us-east-1 `
  -e AWS_ACCESS_KEY_ID=$env:AWS_ACCESS_KEY_ID `
  -e AWS_SECRET_ACCESS_KEY=$env:AWS_SECRET_ACCESS_KEY `
  -e DB_HOST=host.docker.internal `
  -e DB_PORT=3306 `
  -e DB_NAME=plainit_db `
  -e DB_USER=root `
  -e DB_PASSWORD=root `
  planit-insightai-svc:latest
```

### 3단계: 로그 확인

```bash
docker logs -f planit-insightai-svc
```

### 4단계: 테스트

위의 "방법 1"과 동일하게 API 테스트 진행

### 5단계: 컨테이너 중지 및 삭제

```bash
docker stop planit-insightai-svc
docker rm planit-insightai-svc
```

---

## 📝 간단한 테스트 스크립트

### test_report_api.py 사용

이미 만들어둔 테스트 스크립트를 사용할 수 있습니다:

```bash
# 서버가 실행 중인 상태에서
python test_report_api.py
```

### test_chatbot_api.py 사용

```bash
# 서버가 실행 중인 상태에서
python test_chatbot_api.py
```

---

## 🔍 문제 해결

### 1. 포트 충돌 (8085 포트가 이미 사용 중)

다른 포트로 실행:
```bash
uvicorn app.main:app --reload --port 8086
```

### 2. AWS 자격 증명 오류

.env 파일 확인:
```bash
cat .env
```

또는 환경 변수 직접 설정:
```bash
$env:AWS_ACCESS_KEY_ID="AKIA..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_REGION="us-east-1"
```

### 3. MariaDB 연결 오류

DB 설정 확인 (.env 파일):
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=plainit_db
DB_USER=root
DB_PASSWORD=root
```

DB가 실행 중인지 확인:
```bash
# MariaDB 상태 확인
mysql -u root -p -e "SELECT 1"
```

### 4. Bedrock 모델 접근 오류

AWS Console에서 Bedrock Model Access 확인:
1. AWS Console → Bedrock → Model access
2. Claude Sonnet 4.5 모델 활성화 확인

---

## 💡 팁

### 1. 실시간 로그 확인

서버 실행 시 로그가 실시간으로 표시됩니다:
```
INFO:     127.0.0.1:xxxxx - "POST /ai/reports/generate HTTP/1.1" 200 OK
```

### 2. 디버그 모드

더 자세한 로그를 보려면 .env 파일에서:
```env
LOG_LEVEL=DEBUG
```

### 3. 빠른 재시작

`--reload` 옵션을 사용하면 코드 변경 시 자동으로 재시작됩니다.

### 4. Postman 사용

Postman을 사용하는 경우:
1. http://localhost:8085/openapi.json 다운로드
2. Postman에서 Import → OpenAPI 선택
3. 자동으로 모든 API 엔드포인트 생성됨

---

## 🎯 추천 테스트 순서

1. ✅ Health Check 테스트 (서버 정상 동작 확인)
2. ✅ Swagger UI 열기 (http://localhost:8085/docs)
3. ✅ 리포트 생성 API 테스트 (Swagger UI에서)
4. ✅ 챗봇 API 테스트 (Swagger UI에서)
5. ✅ 실제 Bedrock 호출 확인 (로그 확인)

가장 쉬운 방법은 **Swagger UI**를 사용하는 것입니다!
