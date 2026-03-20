"""
Trace ID Middleware
MSA 환경에서 요청 추적을 위한 Trace ID 처리
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging_config import set_trace_id


class TraceIdMiddleware(BaseHTTPMiddleware):
    """
    Trace ID를 추출하거나 생성하여 context에 저장하는 미들웨어
    
    - X-Trace-Id 헤더가 있으면 사용
    - 없으면 새로 생성
    - 응답 헤더에도 Trace ID 포함
    """
    
    async def dispatch(self, request: Request, call_next):
        # Trace ID 추출 또는 생성
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        
        # Context에 Trace ID 저장 (로깅에서 사용)
        set_trace_id(trace_id)
        
        # 요청 처리
        response = await call_next(request)
        
        # 응답 헤더에 Trace ID 추가
        response.headers["X-Trace-Id"] = trace_id
        
        return response
