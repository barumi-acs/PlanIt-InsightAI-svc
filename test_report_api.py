"""
리포트 생성 API 테스트 스크립트
"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.clients.bedrock_client import BedrockClient
from app.services.report_generator import ReportGeneratorService


# 테스트 데이터
TEST_STATS_DATA = {
    "growth": {
        "topic_name": "운동",
        "growth_rate": 24,
        "previous_completion_rate": 65,
        "current_completion_rate": 89
    },
    "timeline": {
        "chart_data": [
            {"month": "2025-11", "completion_rate": 45},
            {"month": "2025-12", "completion_rate": 60},
            {"month": "2026-01", "completion_rate": 72},
            {"month": "2026-02", "completion_rate": 89}
        ]
    },
    "pattern": {
        "daily_stats": [
            {"day": "MONDAY", "total": 10, "completed": 8, "postponed": 2},
            {"day": "TUESDAY", "total": 12, "completed": 10, "postponed": 2},
            {"day": "WEDNESDAY", "total": 11, "completed": 9, "postponed": 2},
            {"day": "THURSDAY", "total": 13, "completed": 11, "postponed": 2},
            {"day": "FRIDAY", "total": 14, "completed": 12, "postponed": 2},
            {"day": "SATURDAY", "total": 12, "completed": 7, "postponed": 5},
            {"day": "SUNDAY", "total": 15, "completed": 7, "postponed": 8}
        ]
    },
    "summary": {
        "total_tasks": 84,
        "completed_tasks": 67,
        "completion_rate": 79.8,
        "achievement_trend": "+12%"
    }
}


async def test_report_generation():
    """리포트 생성 테스트"""
    print("=" * 80)
    print("리포트 생성 API 테스트")
    print("=" * 80)
    
    try:
        # 클라이언트 및 서비스 초기화
        print("\n[1단계] BedrockClient 및 ReportGeneratorService 초기화...")
        bedrock_client = BedrockClient()
        report_service = ReportGeneratorService(bedrock_client)
        print("✅ 초기화 완료")
        
        # 리포트 생성
        print("\n[2단계] 리포트 생성 중...")
        print("  - Growth Feedback 생성 중...")
        print("  - Timeline Feedback 생성 중...")
        print("  - Pattern Feedback 생성 중...")
        print("  - Summary Feedback 생성 중...")
        
        response = await report_service.generate_report(TEST_STATS_DATA)
        
        print("✅ 리포트 생성 완료")
        
        # 결과 출력
        print("\n" + "=" * 80)
        print("생성된 리포트")
        print("=" * 80)
        
        # camelCase로 변환하여 출력
        report_dict = response.model_dump(by_alias=True)
        
        print("\n[Growth Feedback]")
        print(f"주제: {report_dict['reportData']['growth']['topicName']}")
        print(f"성장률: {report_dict['reportData']['growth']['growthRate']}%")
        print(f"메시지: {report_dict['reportData']['growth']['message']}")
        
        print("\n[Timeline Feedback]")
        print(f"메시지: {report_dict['reportData']['timeline']['message']}")
        
        print("\n[Pattern Feedback]")
        print(f"가장 미룬 요일: {report_dict['reportData']['pattern']['worstDay']}")
        print(f"평균 미룬 횟수: {report_dict['reportData']['pattern']['avgPostponeCount']}")
        print(f"메시지: {report_dict['reportData']['pattern']['message']}")
        
        print("\n[Summary Feedback]")
        print(f"메시지: {report_dict['reportData']['summary']['message']}")
        
        print("\n" + "=" * 80)
        print("JSON 응답 (camelCase)")
        print("=" * 80)
        print(json.dumps(report_dict, indent=2, ensure_ascii=False))
        
        print("\n✅ 모든 테스트 통과!")
        print("리포트 생성 API가 정상적으로 작동합니다.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """메인 테스트 실행"""
    print("\n🚀 PlanIt-InsightAI-svc 리포트 생성 테스트\n")
    
    success = await test_report_generation()
    
    if success:
        print("\n" + "=" * 80)
        print("🎉 Phase 2: Context Injection 구현 완료!")
        print("=" * 80)
        print("\n다음 단계:")
        print("1. FastAPI 서버 실행: uvicorn app.main:app --reload")
        print("2. API 문서 확인: http://localhost:8000/docs")
        print("3. POST /ai/reports/generate 엔드포인트 테스트")


if __name__ == "__main__":
    asyncio.run(main())
