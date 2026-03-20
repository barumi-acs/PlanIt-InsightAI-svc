"""
PlanIt-InsightAI-svc FastAPI 애플리케이션 진입점
AWS Bedrock Claude Sonnet 4.5를 활용한 AI 리포트 생성 및 챗봇 서비스
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.api import reports, chatbot
from app.clients.database_client import get_database_client
from app.middleware.trace import TraceIdMiddleware

# 설정 로드
settings = get_settings()

# PlanIt 표준 JSON 로깅 설정
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    logger.info("서비스 시작", extra={'data': {
        'port': settings.port,
        'env': settings.environment,
        'region': settings.aws_region,
        'model': settings.bedrock_model_id
    }})
    
    # 데이터베이스 연결 풀 초기화
    try:
        await get_database_client()
        logger.info("DB 연결 풀 초기화 완료")
    except Exception as e:
        logger.warning("DB 초기화 실패 (첫 요청 시 재시도)", extra={'data': {'error': str(e)}})
    
    yield
    
    # Shutdown
    logger.info("[insightAI] 서비스 종료 시작")
    
    # 데이터베이스 연결 풀 종료
    try:
        db_client = await get_database_client()
        await db_client.close()
        logger.info("[insightAI] DB 연결 풀 종료 완료")
    except Exception as e:
        logger.error("[insightAI] DB 연결 풀 종료 실패 | error=%s", str(e), exc_info=True)


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="PlanIt InsightAI Service",
    description="AI-powered report generation and chatbot service using AWS Bedrock Claude Sonnet 4.5",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Trace ID 미들웨어 등록 (로그에 traceId 자동 주입)
app.add_middleware(TraceIdMiddleware)

# 라우터 등록
app.include_router(reports.router)
app.include_router(chatbot.router)


@app.get("/health")
async def health_check():
    """
    헬스체크 엔드포인트
    컨테이너 오케스트레이션 및 로드밸런서에서 사용
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "PlanIt-InsightAI-svc",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.environment
        }
    )


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Welcome to PlanIt InsightAI Service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # uvicorn 로깅 설정 비활성화 (PlanIt 표준 로깅 사용)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True if settings.environment == "dev" else False,
        log_config=None  # uvicorn 기본 로깅 비활성화
    )
