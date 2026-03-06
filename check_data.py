"""
데이터베이스 데이터 확인 스크립트
AI가 "데이터가 없다"고 응답하는 문제 디버깅용
"""
import asyncio
import aiomysql
from datetime import datetime, timedelta
from app.core.config import get_settings

settings = get_settings()


async def check_database():
    """데이터베이스 연결 및 데이터 확인"""
    
    print("=" * 80)
    print("데이터베이스 연결 정보")
    print("=" * 80)
    print(f"Host: {settings.db_host}")
    print(f"Port: {settings.db_port}")
    print(f"Database: {settings.db_name}")
    print(f"User: {settings.db_user}")
    print()
    
    try:
        # 데이터베이스 연결
        conn = await aiomysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            charset='utf8mb4'
        )
        
        print("✅ 데이터베이스 연결 성공")
        print()
        
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 1. 전체 user_id 목록
            print("=" * 80)
            print("1. 데이터베이스에 있는 모든 user_id 목록")
            print("=" * 80)
            await cursor.execute("SELECT DISTINCT user_id FROM user_action_logs")
            user_ids = await cursor.fetchall()
            for row in user_ids:
                print(f"  - {row['user_id']}")
            print()
            
            # 2. test-user-001 데이터 확인
            test_user_id = 'test-user-001'
            print("=" * 80)
            print(f"2. {test_user_id} 데이터 통계")
            print("=" * 80)
            
            await cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed_count,
                    SUM(CASE WHEN action_type = 'POSTPONED' THEN 1 ELSE 0 END) as postponed_count,
                    MIN(action_time) as earliest_date,
                    MAX(action_time) as latest_date
                FROM user_action_logs
                WHERE user_id = %s
                  AND deleted_at IS NULL
            """, [test_user_id])
            
            stats = await cursor.fetchone()
            print(f"  전체 레코드 수: {stats['total_count']}")
            print(f"  완료(COMPLETED): {stats['completed_count']}")
            print(f"  미룸(POSTPONED): {stats['postponed_count']}")
            print(f"  가장 오래된 데이터: {stats['earliest_date']}")
            print(f"  가장 최근 데이터: {stats['latest_date']}")
            print()
            
            # 3. 최근 한 달 데이터 확인 (Claude가 계산하는 방식)
            print("=" * 80)
            print("3. 최근 한 달 데이터 (오늘 기준)")
            print("=" * 80)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            print(f"  시작 날짜: {start_date.strftime('%Y-%m-%d')}")
            print(f"  종료 날짜: {end_date.strftime('%Y-%m-%d')}")
            print()
            
            await cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    SUM(CASE WHEN action_type = 'COMPLETED' THEN 1 ELSE 0 END) as completed_count
                FROM user_action_logs
                WHERE user_id = %s
                  AND action_time BETWEEN %s AND %s
                  AND deleted_at IS NULL
            """, [test_user_id, start_date, end_date])
            
            recent_stats = await cursor.fetchone()
            print(f"  전체 레코드 수: {recent_stats['total_count']}")
            print(f"  완료(COMPLETED): {recent_stats['completed_count']}")
            print()
            
            # 4. 요일별 완료 통계 (최근 한 달)
            print("=" * 80)
            print("4. 요일별 완료 통계 (최근 한 달)")
            print("=" * 80)
            
            await cursor.execute("""
                SELECT 
                    day_of_week,
                    COUNT(*) as count
                FROM user_action_logs
                WHERE user_id = %s
                  AND action_type = 'COMPLETED'
                  AND action_time BETWEEN %s AND %s
                  AND deleted_at IS NULL
                GROUP BY day_of_week
                ORDER BY count DESC
            """, [test_user_id, start_date, end_date])
            
            day_stats = await cursor.fetchall()
            for row in day_stats:
                print(f"  {row['day_of_week']}: {row['count']}개")
            print()
            
            # 5. 실제 Tool이 실행할 쿼리 테스트
            print("=" * 80)
            print("5. Tool 쿼리 시뮬레이션 (action_type='COMPLETED')")
            print("=" * 80)
            
            query = """
                SELECT 
                    task_id,
                    user_id,
                    goals_id,
                    action_type,
                    action_time,
                    day_of_week,
                    hour_of_day,
                    due_date,
                    postponed_to_date
                FROM user_action_logs
                WHERE user_id = %s
                    AND action_time BETWEEN %s AND %s
                    AND deleted_at IS NULL
                    AND action_type = %s
                ORDER BY action_time DESC
            """
            
            params = [
                test_user_id,
                f"{start_date.strftime('%Y-%m-%d')} 00:00:00",
                f"{end_date.strftime('%Y-%m-%d')} 23:59:59",
                'COMPLETED'
            ]
            
            print(f"  Query Parameters:")
            print(f"    user_id: {params[0]}")
            print(f"    start_date: {params[1]}")
            print(f"    end_date: {params[2]}")
            print(f"    action_type: {params[3]}")
            print()
            
            await cursor.execute(query, params)
            results = await cursor.fetchall()
            
            print(f"  결과: {len(results)}개 레코드")
            print()
            
            if results:
                print("  최근 5개 레코드:")
                for i, row in enumerate(results[:5], 1):
                    print(f"    {i}. task_id={row['task_id']}, "
                          f"action_type={row['action_type']}, "
                          f"day_of_week={row['day_of_week']}, "
                          f"action_time={row['action_time']}")
            else:
                print("  ⚠️ 레코드가 없습니다!")
            print()
            
            # 6. 다른 user_id로 테스트 (실제 사용자 ID 확인)
            print("=" * 80)
            print("6. 실제 API 호출 시 사용한 user_id 확인 필요")
            print("=" * 80)
            print("  Python 서버 로그에서 다음을 확인하세요:")
            print("  [Tool Execution] query_user_action_logs")
            print("    Input: {'start_date': '...', 'end_date': '...', 'action_type': '...', 'user_id': '...'}")
            print()
            print("  만약 user_id가 'test-user-001'이 아니라면,")
            print("  해당 user_id로 데이터를 다시 확인해야 합니다.")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_database())
