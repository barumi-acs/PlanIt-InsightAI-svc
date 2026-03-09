# gRPC 통합 아키텍처 가이드

## 개요
InsightAI-svc는 단일 포트(50051)에서 gRPC Multiplexing을 활용하여 여러 서비스를 제공합니다.

## 아키텍처 원칙

### ✅ 채택: 단일 포트 통합 (gRPC Multiplexing)
```
InsightAI-svc (Python)
Port: 50051 (단일 포트)
┌─────────────────────────────────┐
│   gRPC Server (Multiplexing)    │
│                                  │
│  ┌────────────────────────────┐ │
│  │  ChatbotService            │ │
│  │  (chat.ChatbotService)     │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │  ReportService             │ │
│  │  (report.ReportService)    │ │
│  └────────────────────────────┘ │
│                                  │
└─────────────────────────────────┘
```

### ❌ 기각: 포트 분리 (안티 패턴)
```
❌ ChatbotService  → Port 50051
❌ ReportService   → Port 50052
```

**기각 이유**:
- 단일 마이크로서비스에서 포트 분리는 배포 복잡도 증가
- gRPC는 기본적으로 HTTP/2 Multiplexing 지원
- 서비스별 독립 배포가 필요하면 마이크로서비스 자체를 분리해야 함

## 통합 서버 구현

### Python: app/main_grpc.py

```python
"""
통합 gRPC 서버 (Chatbot + Report)
Port: 50051 (단일 포트)
"""

import grpc
from grpc_reflection.v1alpha import reflection

# Chatbot gRPC
from app.grpc_generated import chat_service_pb2_grpc
from app.grpc_server.chatbot_servicer import ChatbotServicer

# Report gRPC
from proto import report_service_pb2_grpc
from app.grpc_server.report_servicer import ReportServiceServicer

async def serve():
    server = grpc.aio.server(...)
    
    # Chatbot Servicer 등록
    chat_service_pb2_grpc.add_ChatbotServiceServicer_to_server(
        ChatbotServicer(), server
    )
    
    # Report Servicer 등록
    report_service_pb2_grpc.add_ReportServiceServicer_to_server(
        ReportServiceServicer(), server
    )
    
    # 단일 포트 50051
    server.add_insecure_port('[::]50051')
    await server.start()
```

### 실행 방법

```powershell
# 단일 명령으로 모든 서비스 실행
cd PlanIt-InsightAI-svc
python -m app.main_grpc
```

**로그 출력**:
```
============================================================
Starting unified gRPC server on [::]:50051
Services available:
  1. ChatbotService (chat.ChatbotService)
  2. ReportService (report.ReportService)
AWS Region: us-east-1
Bedrock Model: global.anthropic.claude-sonnet-4-5-20250929-v1:0
Database: localhost:3306/planit_insight_db
============================================================
✓ Unified gRPC server started successfully
✓ Listening on port 50051
```

## Java 클라이언트 설정

### application.yml

```yaml
grpc:
  client:
    # Chatbot 서비스
    chat-service:
      address: 'static://localhost:50051'
      negotiationType: plaintext
      enableKeepAlive: true
      keepAliveTime: 30s
      keepAliveTimeout: 10s
    
    # Report 서비스 (동일 포트)
    report-service:
      address: 'static://localhost:50051'
      negotiationType: plaintext
      enableKeepAlive: true
      keepAliveTime: 30s
      keepAliveTimeout: 10s
```

### Java 클라이언트 코드

```java
// Chatbot 클라이언트
@GrpcClient("chat-service")
private ChatbotServiceGrpc.ChatbotServiceBlockingStub chatbotStub;

// Report 클라이언트 (동일 포트, 다른 서비스)
@GrpcClient("report-service")
private ReportServiceGrpc.ReportServiceBlockingStub reportStub;
```

## gRPC Multiplexing 동작 원리

### HTTP/2 기반 멀티플렉싱

```
Client (Java)                    Server (Python)
                                 Port: 50051
┌──────────────┐                ┌──────────────┐
│ ChatClient   │───Stream 1────>│ ChatServicer │
└──────────────┘                └──────────────┘
                                        
┌──────────────┐                ┌──────────────┐
│ ReportClient │───Stream 2────>│ReportServicer│
└──────────────┘                └──────────────┘

        동일 TCP 연결 (Port 50051)
```

### 서비스 구분 방법

gRPC는 **서비스 이름(Full Method Name)**으로 라우팅:
- `chat.ChatbotService/SendMessage` → ChatbotServicer
- `report.ReportService/GenerateReport` → ReportServiceServicer

## 테스트 방법

### 1. Python 서버 시작

```powershell
cd PlanIt-InsightAI-svc
python -m app.main_grpc
```

### 2. 서비스 목록 확인 (grpcurl)

```powershell
grpcurl -plaintext localhost:50051 list
```

**출력**:
```
chat.ChatbotService
grpc.reflection.v1alpha.ServerReflection
report.ReportService
```

### 3. Chatbot 서비스 테스트

```powershell
grpcurl -plaintext -d '{
  "user_id": "test-user",
  "message": "안녕하세요"
}' localhost:50051 chat.ChatbotService/SendMessage
```

### 4. Report 서비스 테스트

```powershell
grpcurl -plaintext -d '{
  "user_id": "test-user-001",
  "report_type": "GROWTH",
  "target_period": "2026-02",
  "statistics_data": "{\"topicName\":\"운동\",\"growthRate\":25}"
}' localhost:50051 report.ReportService/GenerateReport
```

### 5. Java 통합 테스트

```powershell
# Insight-svc 실행
cd PlanIt-Insight-svc
./gradlew bootRun

# 배치 API 호출
Invoke-WebRequest -Uri "http://localhost:8084/api/v1/batch/generate-report?userId=test-user-001&yearMonth=2026-02" -Method POST
```

## 포트 정리

| 서비스 | 프로토콜 | 포트 | 용도 |
|--------|---------|------|------|
| Schedule-svc | HTTP | 8083 | REST API |
| Insight-svc | HTTP | 8084 | REST API |
| Insight-svc | gRPC | 9090 | ActionLog 서버 |
| InsightAI-svc | gRPC | 50051 | Chatbot + Report (통합) |
| InsightAI-svc | HTTP | 8085 | FastAPI (Deprecated) |

## 마이그레이션 체크리스트

- [x] main_grpc.py에 Report 서비스 통합
- [x] main_grpc_report.py 삭제
- [x] main_grpc_all.py 삭제
- [x] application.yml 통합 설정
- [ ] Proto 컴파일 (Python)
- [ ] Proto 컴파일 (Java)
- [ ] 통합 서버 실행 테스트
- [ ] Java 클라이언트 연동 테스트
- [ ] REST API 제거 (선택사항)

## 장점

1. **단순성**: 하나의 프로세스, 하나의 포트
2. **효율성**: TCP 연결 재사용, HTTP/2 Multiplexing
3. **배포 용이성**: 단일 컨테이너, 단일 서비스
4. **관리 편의성**: 로그 통합, 모니터링 단순화
5. **gRPC 표준**: gRPC의 설계 의도에 부합

## 참고 자료

- [gRPC Multiplexing](https://grpc.io/docs/what-is-grpc/core-concepts/#rpc-life-cycle)
- [HTTP/2 Multiplexing](https://developers.google.com/web/fundamentals/performance/http2)
- [Microservices Best Practices](https://microservices.io/patterns/microservices.html)
