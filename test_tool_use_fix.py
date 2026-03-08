"""
Tool Use 수정 검증 스크립트
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.clients.bedrock_client import BedrockClient
from app.clients.database_client import get_database_client
from app.services.chatbot import ChatbotService


async def test_tool_use():
    """Tool Use 워크플로우 테스트"""
    print("=" * 80)
    print("Tool Use 수정 검증 테스트")
    print("=" * 80)
    
    try:
        # 클라이언트 초기화
        print("\n[1단계] 서비스 초기화 중...")
        bedrock_client = BedrockClient()
        db_client = await get_database_client()
        chatbot_service = ChatbotService(bedrock_client, db_client)
        print("✓ 서비스 초기화 완료")
        
        # 테스트 질의
        test_query = "지난 주에 어느 요일에 할 일을 가장 많이 미뤘나요?"
        user_id = "test-user-001"
        
        print(f"\n[2단계] 챗봇 질의 테스트")
        print(f"  User ID: {user_id}")
        print(f"  Query: {test_query}")
        print("\n처리 중...")
        
        # 질의 처리
        result = await chatbot_service.process_query(
            user_id=user_id,
            query=test_query
        )
        
        print("\n" + "=" * 80)
        print("✓ 테스트 성공!")
        print("=" * 80)
        print(f"\n답변:\n{result['answer']}")
        print(f"\n출처: {', '.join(result['sources'])}")
        print(f"\n생성 시각: {result['generated_at']}")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("✗ 테스트 실패")
        print("=" * 80)
        print(f"\n에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """메인 실행"""
    print("\n🔧 PlanIt-InsightAI-svc Tool Use 수정 검증\n")
    
    success = await test_tool_use()
    
    if success:
        print("\n" + "=" * 80)
        print("✓ Tool Use 워크플로우가 정상적으로 작동합니다!")
        print("=" * 80)
        print("\n다음 단계:")
        print("1. FastAPI 서버 실행: python -m uvicorn app.main:app --host 0.0.0.0 --port 8085 --reload")
        print("2. POST /ai/chat/query 엔드포인트 테스트")
        print("3. Swagger UI에서 API 문서 확인: http://localhost:8085/docs")
    else:
        print("\n" + "=" * 80)
        print("✗ Tool Use 워크플로우에 문제가 있습니다.")
        print("=" * 80)
        print("\n문제 해결:")
        print("1. AWS 자격 증명 확인: python check_aws_credentials.py")
        print("2. 데이터베이스 연결 확인: python check_data.py")
        print("3. 로그 확인하여 상세 에러 분석")


if __name__ == "__main__":
    asyncio.run(main())
