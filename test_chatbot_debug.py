"""
챗봇 "데이터 없음" 문제 디버깅 테스트 스크립트
"""
import asyncio
import sys
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, '.')

from app.clients.bedrock_client import BedrockClient
from app.clients.database_client import get_database_client
from app.services.chatbot import ChatbotService


async def test_chatbot_with_debug():
    """챗봇 서비스 테스트 (디버깅 정보 포함)"""
    
    print("=" * 80)
    print("챗봇 디버깅 테스트 시작")
    print("=" * 80)
    print()
    
    # 1. 데이터베이스 연결 확인
    print("1. 데이터베이스 연결 중...")
    try:
        db_client = await get_database_client()
        print("   ✅ 데이터베이스 연결 성공")
    except Exception as e:
        print(f"   ❌ 데이터베이스 연결 실패: {e}")
        return
    print()
    
    # 2. 테스트 데이터 확인
    print("2. 테스트 데이터 확인 중...")
    test_user_id = 'test-user-001'
    
    try:
        # 최근 한 달 날짜 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"   User ID: {test_user_id}")
        print(f"   Date Range: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        print()
        
        # 전체 데이터 조회
        all_results = await db_client.query_action_logs(
            user_id=test_user_id,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        print(f"   전체 레코드: {len(all_results)}개")
        
        # 완료 데이터만 조회
        completed_results = await db_client.query_action_logs(
            user_id=test_user_id,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            action_type='COMPLETED'
        )
        print(f"   완료(COMPLETED) 레코드: {len(completed_results)}개")
        
        # 미룸 데이터만 조회
        postponed_results = await db_client.query_action_logs(
            user_id=test_user_id,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            action_type='POSTPONED'
        )
        print(f"   미룸(POSTPONED) 레코드: {len(postponed_results)}개")
        print()
        
        if len(completed_results) == 0:
            print("   ⚠️ 경고: 완료 데이터가 없습니다!")
            print("   테스트 데이터를 먼저 삽입하세요: test-data-chatbot.sql")
            return
        
        # 요일별 집계
        day_counts = {}
        for row in completed_results:
            day = row['day_of_week']
            day_counts[day] = day_counts.get(day, 0) + 1
        
        print("   요일별 완료 통계:")
        for day, count in sorted(day_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"     {day}: {count}개")
        print()
        
    except Exception as e:
        print(f"   ❌ 데이터 조회 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Bedrock 클라이언트 초기화
    print("3. Bedrock 클라이언트 초기화 중...")
    try:
        bedrock_client = BedrockClient()
        print("   ✅ Bedrock 클라이언트 초기화 성공")
    except Exception as e:
        print(f"   ❌ Bedrock 클라이언트 초기화 실패: {e}")
        print("   AWS 자격 증명을 확인하세요: python check_aws_credentials.py")
        return
    print()
    
    # 4. ChatbotService 생성
    print("4. ChatbotService 생성 중...")
    try:
        chatbot_service = ChatbotService(bedrock_client, db_client)
        print("   ✅ ChatbotService 생성 성공")
    except Exception as e:
        print(f"   ❌ ChatbotService 생성 실패: {e}")
        return
    print()
    
    # 5. 챗봇 질의 테스트
    print("5. 챗봇 질의 테스트 중...")
    print("=" * 80)
    
    test_queries = [
        "최근 한 달 간 완료한 할 일이 어느 요일에 많아?",
        "지난 주에 가장 많이 미룬 요일은?",
        "이번 달 완료율은 얼마야?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print()
        print(f"테스트 {i}: {query}")
        print("-" * 80)
        
        try:
            result = await chatbot_service.process_query(
                user_id=test_user_id,
                query=query
            )
            
            print(f"✅ 답변 생성 성공")
            print(f"답변: {result['answer'][:200]}...")
            print(f"출처: {', '.join(result['sources'])}")
            
        except Exception as e:
            print(f"❌ 질의 실패: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 80)
    
    print()
    print("=" * 80)
    print("테스트 완료")
    print("=" * 80)
    
    # 데이터베이스 연결 종료
    await db_client.close()


if __name__ == "__main__":
    asyncio.run(test_chatbot_with_debug())
