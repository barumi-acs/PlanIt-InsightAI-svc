"""
AI 리포트 생성 gRPC Servicer
Insight-svc(Java)로부터 리포트 생성 요청을 받아 처리
"""
import json
import logging
from datetime import datetime

import grpc
from proto import report_service_pb2, report_service_pb2_grpc

from app.clients.bedrock_client import BedrockClient
from app.services.report_generator import ReportGeneratorService
from app.core.logging_config import log_with_data

logger = logging.getLogger(__name__)


class ReportServiceServicer(report_service_pb2_grpc.ReportServiceServicer):
    """AI 리포트 생성 gRPC Servicer"""
    
    def __init__(self):
        """초기화"""
        self.bedrock_client = BedrockClient()
        self.report_service = ReportGeneratorService(self.bedrock_client)
        logger.info("ReportServiceServicer initialized")
    
    async def GenerateReport(
        self, 
        request: report_service_pb2.GenerateReportRequest, 
        context: grpc.aio.ServicerContext
    ) -> report_service_pb2.GenerateReportResponse:
        """
        AI 리포트 생성
        
        Args:
            request: 리포트 생성 요청
            context: gRPC 컨텍스트
        
        Returns:
            리포트 생성 응답
        """
        try:
            log_with_data(logger, 'info', 'gRPC 리포트 생성 요청 수신',
                          userId=request.user_id,
                          reportType=request.report_type,
                          targetPeriod=request.target_period)
            
            # JSON 문자열을 딕셔너리로 파싱
            try:
                statistics_data = json.loads(request.statistics_data)
            except json.JSONDecodeError as e:
                log_with_data(logger, 'error', 'statistics_data JSON 파싱 실패',
                              error=str(e))
                return report_service_pb2.GenerateReportResponse(
                    success=False,
                    report_data="{}",
                    error_message=f"Invalid JSON in statistics_data: {str(e)}",
                    generated_at=datetime.now().isoformat()
                )
            
            logger.info(f"Parsed statistics_data: {statistics_data}")
            
            # 리포트 타입별 처리
            report_type = request.report_type.upper()
            
            if report_type == "GROWTH":
                # Growth 리포트 생성
                growth_data = {
                    'topic_name': statistics_data.get('topicName', '전체'),
                    'growth_rate': statistics_data.get('growthRate', 0),
                    'previous_rate': statistics_data.get('previousRate', 0),
                    'current_rate': statistics_data.get('currentRate', 0)
                }
                feedback = await self.report_service._generate_growth_feedback(growth_data)
                report_data = feedback.model_dump(by_alias=True)
                
            elif report_type == "TIMELINE":
                # Timeline 리포트 생성
                chart_data_raw = statistics_data.get('chartData', [])
                timeline_data = {
                    'chart_data': [
                        {'month': item.get('month', ''), 'completion_rate': item.get('rate', 0)}
                        for item in chart_data_raw
                    ]
                }
                feedback = await self.report_service._generate_timeline_feedback(timeline_data)
                report_data = feedback.model_dump(by_alias=True)
                
            elif report_type == "PATTERN":
                # Pattern 리포트 생성
                chart_raw = statistics_data.get('chart', [])
                pattern_data = {
                    'daily_stats': [
                        {
                            'day': item.get('day', 'MONDAY'),
                            'total': item.get('count', 0) + 10,
                            'completed': 10,
                            'postponed': item.get('count', 0)
                        }
                        for item in chart_raw
                    ]
                }
                feedback = await self.report_service._generate_pattern_feedback(pattern_data)
                report_data = feedback.model_dump(by_alias=True)
                
            elif report_type == "SUMMARY":
                # Summary 리포트 생성
                summary_data = {
                    'total_tasks': statistics_data.get('totalTasks', 0),
                    'completed_tasks': statistics_data.get('completedTasks', 0),
                    'completion_rate': statistics_data.get('completionRate', 0),
                    'currentRate': statistics_data.get('currentRate', statistics_data.get('completionRate', 0)),
                    'achievement_trend': statistics_data.get('achievementTrend', '0%'),
                    'achievementTrend': statistics_data.get('achievementTrend', '0%'),
                    'bestFocusTime': statistics_data.get('bestFocusTime', '08:00-10:00'),
                    'best_focus_time': statistics_data.get('bestFocusTime', '08:00-10:00')
                }
                feedback = await self.report_service._generate_summary_feedback(
                    None, None, None, summary_data
                )
                report_data = feedback.model_dump(by_alias=True)
                
            else:
                log_with_data(logger, 'error', '지원하지 않는 리포트 타입',
                              reportType=report_type)
                return report_service_pb2.GenerateReportResponse(
                    success=False,
                    report_data="{}",
                    error_message=f"Unsupported report type: {report_type}",
                    generated_at=datetime.now().isoformat()
                )
            
            # JSON 문자열로 변환
            report_data_json = json.dumps(report_data, ensure_ascii=False)
            
            log_with_data(logger, 'info', 'gRPC 리포트 생성 성공',
                          userId=request.user_id,
                          reportType=report_type)
            
            return report_service_pb2.GenerateReportResponse(
                success=True,
                report_data=report_data_json,
                error_message="",
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            log_with_data(logger, 'error', 'gRPC 리포트 생성 실패',
                          error=str(e))
            return report_service_pb2.GenerateReportResponse(
                success=False,
                report_data="{}",
                error_message=f"Report generation failed: {str(e)}",
                generated_at=datetime.now().isoformat()
            )
