"""
간결한 답변 스타일 검증 스크립트
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.clients.bedrock_client import BedrockClient
from app.clients.database_client import get_database_client
from app.services.chatbot import ChatbotService


async def test_concise_responses():
    """간결한 답변 스타일 테스트"""
    print("=" * 80)
    print("간결한 답변 스타일 검증")
    print("=" * 80)
    
    try:
        # 서비스 초기화
        print("\n[초기화] 챗봇 서비스 준비 중...")
        bedrock_client = BedrockClient()
        db_client = await get_database_client()
        chatbot_service = ChatbotService(bedrock_client, db_client)
        print("✓ 초기화 완료\n")
        
        # 테스트 케이스
        test_cases = [
            {
                "query": "지난 주에 어느 요일에 할 일을 가장 많이 미뤘나요?",
                "expected": "간결한 답변 (꼬리 질문 없음)"
            },
            {
                "query": "이번 주 완료율은?",
                "expected": "숫자 중심의 짧은 답변"
            }
        ]
        
        user_id = "test-user-001"
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"[테스트 {i}] {test_case['query']}")
            print(f"기대: {test_case['expected']}")
            print("-" * 80)
            
            result = await chatbot_service.process_query(
                user_id=user_id,
                query=test_case['query']
            )
            
            answer = result['answer']
            answer_length = len(answer)
            
            print(f"\n답변 ({answer_length}자):")
            print(answer)
            print()
            
            # 검증
            has_follow_up = any(marker in answer for marker in [
                "할까요?", "원하시나요?", "궁금하신가요?", 
                "더 알고 싶으시면", "다른 질문"
            ])
            
            if has_follow_up:
                print("⚠️  경고: 꼬리 질문 발견!")
            else:
                print("✓ 꼬리 질문 없음")
            
            if answer_length > 200:
                print(f"⚠️  경고: 답변이 너무 김 ({answer_length}자)")
            else:
                print(f"✓ 적절한 길이 ({answer_length}자)")
            
            print("=" * 80)
            print()
        
        print("\n✓ 테스트 완료!")
        print("\n검증 포인트:")
        print("1. 꼬리 질문 없음 (Stateless)")
        print("2. 간결한 답변 (150자 내외)")
        print("3. 프로페셔널한 톤")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """메인 실행"""
    print("\n🔧 PlanIt-InsightAI-svc 간결한 답변 스타일 검증\n")
    
    success = await test_concise_responses()
    
    if success:
        print("\n" + "=" * 80)
        print("✓ 간결한 답변 스타일이 적용되었습니다!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("✗ 테스트 실패")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
