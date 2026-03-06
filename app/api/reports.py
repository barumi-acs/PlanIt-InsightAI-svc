"""
리포트 생성 API 라우터
"""
import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models.request import ReportGenerationRequest
from app.models.response import ReportGenerationResponse
from app.clients.bedrock_client import BedrockClient
from app.services.report_generator import ReportGeneratorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/reports", tags=["Reports"])

# 싱글톤 인스턴스
bedrock_client = BedrockClient()
report_service = ReportGeneratorService(bedrock_client)


@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(request: ReportGenerationRequest):
    """
    리포트 생성 API (Context Injection 방식)
    
    Service A가 조회한 통계 데이터를 받아 AI 피드백 생성
    """
    try:
        logger.info(f"Report generation requested for user: {request.user_id}, period: {request.year_month}-W{request.week}")
        
        # 통계 데이터를 딕셔너리로 변환
        stats_data = {
            'growth': request.stats_data.growth.model_dump(),
            'timeline': {
                'chart_data': [item.model_dump() for item in request.stats_data.timeline.chart_data]
            },
            'pattern': {
                'daily_stats': [item.model_dump() for item in request.stats_data.pattern.daily_stats]
            },
            'summary': request.stats_data.summary.model_dump()
        }
        
        # 리포트 생성
        response = await report_service.generate_report(stats_data)
        
        logger.info(f"Report generated successfully for user: {request.user_id}")
        
        return response
    
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"리포트 생성 중 오류가 발생했습니다: {str(e)}"
        )
