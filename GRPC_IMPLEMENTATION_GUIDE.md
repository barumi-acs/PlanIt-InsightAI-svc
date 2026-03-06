# gRPC Implementation Guide (Python Service)

## 완료된 작업

### 1. ✅ requirements.txt 업데이트
gRPC 라이브러리 추가:
```txt
grpcio==1.62.0
grpcio-tools==1.62.0
grpcio-reflection==1.62.0
```

### 2. ✅ Proto 파일 복사
```
PlanIt-InsightAI-svc/
└── proto/
    └── chat_service.proto  (Java에서 복사)
```

### 3. ✅ 디렉토리 구조 생성
```
PlanIt-InsightAI-svc/
├── proto/
│   └── chat_service.proto
├── app/
│   ├── grpc_generated/  (proto 컴파일 결과)
│   │   └── __init__.py
│   ├── grpc_server/  (Servicer 구현)
│   │   ├── __init__.py
│   │   └── chatbot_servicer.py
│   └── main_grpc.py  (gRPC 서버 실행)
```

### 4. ✅ gRPC Servicer 구현
**파일**: `app/grpc_server/chatbot_servicer.py`
- `ChatbotServicer` 클래스 구현
- 기존 `ChatbotService.query_chatbot()` 로직 연결
- gRPC 에러 핸들링 (INVALID_ARGUMENT, INTERNAL)

### 5. ✅ gRPC 서버 구현
**파일**: `app/main_grpc.py`
- Port 50051에서 gRPC 서버 실행
- Reflection 활성화 (grpcurl 테스트용)
- Database 연결 풀 관리
- 비동기 서버 (grpc.aio)

### 6. ✅ Config 업데이트
**파일**: `app/core/config.py`
- `grpc_port: int = 50051` 추가

---

## 실행 방법

### Step 1: gRPC 라이브러리 설치
```bash
cd PlanIt-InsightAI-svc

# 가상환경 활성화 (선택)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt
```

### Step 2: Proto 컴파일 (Python Stub 생성)
```bash
# Windows (PowerShell)
python -m grpc_tools.protoc `
  -I.\proto `
  --python_out=.\app\grpc_generated `
  --grpc_python_out=.\app\grpc_generated `
  .\proto\chat_service.proto

# Linux/Mac
python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./app/grpc_generated \
  --grpc_python_out=./app/grpc_generated \
  ./proto/chat_service.proto
```

**생성되는 파일**:
```
app/grpc_generated/
├── __init__.py  (이미 생성됨)
├── chat_service_pb2.py  (메시지 클래스)
└── chat_service_pb2_grpc.py  (서비스 스텁)
```

### Step 3: 환경 변수 설정
`.env` 파일 생성:
```env
# AWS Bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=plainit_db
DB_USER=root
DB_PASSWORD=root

# Server
PORT=8085
GRPC_PORT=50051
```

### Step 4: gRPC 서버 실행
```bash
# gRPC 서버 실행 (Port 50051)
python -m app.main_grpc
```

**예상 로그**:
```
2026-03-05 20:57:00,000 - __main__ - INFO - Starting gRPC server on [::]:50051
2026-03-05 20:57:00,001 - __main__ - INFO - AWS Region: us-east-1
2026-03-05 20:57:00,002 - __main__ - INFO - Bedrock Model: anthropic.claude-3-sonnet-20240229-v1:0
2026-03-05 20:57:00,003 - __main__ - INFO - Database: localhost:3306/plainit_db
2026-03-05 20:57:00,100 - __main__ - INFO - Database connection pool initialized
2026-03-05 20:57:00,101 - __main__ - INFO - gRPC server started successfully
```

### Step 5: FastAPI 서버도 함께 실행 (선택)
다른 터미널에서:
```bash
# FastAPI 서버 실행 (Port 8085)
uvicorn app.main:app --host 0.0.0.0 --port 8085 --reload
```

---

## 테스트 방법

### 1. grpcurl로 테스트 (Reflection 사용)

#### 서비스 목록 조회
```bash
grpcurl -plaintext localhost:50051 list
```

**예상 출력**:
```
com.planit.analytics.grpc.ChatbotService
grpc.reflection.v1alpha.ServerReflection
```

#### 메서드 상세 조회
```bash
grpcurl -plaintext localhost:50051 describe com.planit.analytics.grpc.ChatbotService
```

#### QueryChatbot 호출
```bash
grpcurl -plaintext -d '{
  "user_id": "test-user-001",
  "query": "지난주에 할 일을 가장 많이 완료한 요일은?"
}' localhost:50051 com.planit.analytics.grpc.ChatbotService/QueryChatbot
```

**예상 응답**:
```json
{
  "answer": "분석 결과에 따르면, 지난주에 가장 많이 완료한 요일은 월요일입니다...",
  "sources": [
    "query_user_action_logs",
    "calculate_completion_rate"
  ],
  "generatedAt": "2026-03-05T20:57:30.123Z"
}
```

### 2. Python 클라이언트로 테스트

**테스트 스크립트**: `test_grpc_client.py`
```python
import asyncio
import grpc
from app.grpc_generated import chat_service_pb2
from app.grpc_generated import chat_service_pb2_grpc


async def test_query_chatbot():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = chat_service_pb2_grpc.ChatbotServiceStub(channel)
        
        request = chat_service_pb2.ChatRequest(
            user_id="test-user-001",
            query="지난주에 할 일을 가장 많이 완료한 요일은?"
        )
        
        response = await stub.QueryChatbot(request)
        
        print(f"Answer: {response.answer}")
        print(f"Sources: {response.sources}")
        print(f"Generated At: {response.generated_at}")


if __name__ == '__main__':
    asyncio.run(test_query_chatbot())
```

실행:
```bash
python test_grpc_client.py
```

---

## 아키텍처

### gRPC 통신 흐름
```
┌─────────────────────────────────────┐
│  Java Service (Client)              │
│  Port: 8080                         │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ ChatbotServiceGrpc.Stub      │  │
│  │ (Generated from proto)       │  │
│  └──────────────┬───────────────┘  │
└─────────────────┼───────────────────┘
                  │ gRPC (HTTP/2)
                  │ Port: 50051
                  ↓
┌─────────────────────────────────────┐
│  Python Service (Server)            │
│  Port: 50051 (gRPC)                 │
│  Port: 8085 (FastAPI)               │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ ChatbotServicer              │  │
│  │ (Implements gRPC Service)    │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│                 ↓                   │
│  ┌──────────────────────────────┐  │
│  │ ChatbotService               │  │
│  │ (Business Logic)             │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│                 ↓                   │
│  ┌──────────────────────────────┐  │
│  │ BedrockClient                │  │
│  │ (AWS Bedrock API)            │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### 코드 구조
```
ChatbotServicer (gRPC Layer)
    ↓
ChatbotService (Business Logic)
    ↓
BedrockClient + DatabaseClient (Infrastructure)
```

---

## 에러 핸들링

### gRPC Status Codes
```python
# 유효성 검증 실패
context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
context.set_details("user_id and query are required")

# 서버 내부 에러
context.set_code(grpc.StatusCode.INTERNAL)
context.set_details(f"Internal server error: {str(e)}")
```

### Java 클라이언트에서 처리
```java
try {
    ChatResponse response = stub.queryChatbot(request);
} catch (StatusRuntimeException e) {
    if (e.getStatus().getCode() == Status.Code.INVALID_ARGUMENT) {
        // 유효성 검증 에러
    } else if (e.getStatus().getCode() == Status.Code.INTERNAL) {
        // 서버 에러
    }
}
```

---

## 성능 비교

### HTTP/REST vs gRPC
| 항목 | HTTP/REST (JSON) | gRPC (Protobuf) |
|------|------------------|-----------------|
| 프로토콜 | HTTP/1.1 | HTTP/2 |
| 직렬화 | JSON (텍스트) | Protobuf (바이너리) |
| 속도 | 기준 | 3-10배 빠름 |
| 크기 | 기준 | 30-50% 작음 |
| 타입 안정성 | 낮음 | 높음 (스키마 기반) |
| 스트리밍 | 제한적 | 완벽 지원 |

### 예상 성능 향상
- 응답 시간: 100ms → 30-50ms
- 네트워크 대역폭: 50% 절감
- CPU 사용량: 20-30% 절감

---

## 트러블슈팅

### 문제 1: Proto 컴파일 실패
```bash
# grpcio-tools 재설치
pip uninstall grpcio-tools
pip install grpcio-tools==1.62.0

# 다시 컴파일
python -m grpc_tools.protoc ...
```

### 문제 2: Import 에러
```python
# 절대 경로 import 사용
from app.grpc_generated import chat_service_pb2
from app.grpc_generated import chat_service_pb2_grpc
```

### 문제 3: 포트 충돌
```bash
# Windows
netstat -ano | findstr :50051

# Linux/Mac
lsof -i :50051

# 프로세스 종료 후 재시작
```

### 문제 4: Database 연결 실패
```bash
# MariaDB 실행 확인
mysql -u root -p

# 테스트 데이터 확인
USE plainit_db;
SELECT COUNT(*) FROM action_logs WHERE user_id = 'test-user-001';
```

---

## 다음 단계

### Java gRPC 클라이언트 구현
1. Proto 컴파일 (Java)
2. gRPC Client 구현
3. ChatController에서 gRPC 호출
4. 통합 테스트

### 성능 최적화
1. Connection Pool 튜닝
2. Keep-Alive 설정
3. 압축 활성화
4. 메트릭 수집

---

## 체크리스트

- [x] requirements.txt 업데이트
- [x] Proto 파일 복사
- [x] 디렉토리 구조 생성
- [x] ChatbotServicer 구현
- [x] gRPC 서버 구현
- [x] Config 업데이트
- [ ] Proto 컴파일 실행
- [ ] gRPC 서버 실행
- [ ] grpcurl 테스트
- [ ] Java 클라이언트 구현
- [ ] 통합 테스트

---

## 참고 자료

- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Guide](https://protobuf.dev/programming-guides/proto3/)
- [grpcurl GitHub](https://github.com/fullstorydev/grpcurl)
