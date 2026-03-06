"""
Bedrock 연결 테스트 스크립트
AWS 자격 증명 및 Bedrock 모델 액세스 확인
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from app.clients.bedrock_client import BedrockClient
from app.core.config import get_settings


async def test_bedrock_connection():
    """Bedrock 연결 테스트"""
    print("=" * 60)
    print("AWS Bedrock 연결 테스트 시작")
    print("=" * 60)
    
    settings = get_settings()
    print(f"\n[설정 정보]")
    print(f"AWS Region: {settings.aws_region}")
    print(f"Model ID: {settings.bedrock_model_id}")
    print(f"Temperature: {settings.bedrock_temperature}")
    print(f"Max Tokens: {settings.bedrock_max_tokens}")
    
    try:
        # BedrockClient 초기화
        print("\n[1단계] BedrockClient 초기화 중...")
        client = BedrockClient()
        print("✅ BedrockClient 초기화 성공")
        
        # 간단한 테스트 메시지
        print("\n[2단계] Bedrock API 호출 중...")
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": "안녕하세요! 간단한 자기소개를 한 문장으로 해주세요."
                    }
                ]
            }
        ]
        
        response = await client.converse(
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        print("✅ Bedrock API 호출 성공")
        
        # 응답 파싱
        print("\n[3단계] 응답 파싱 중...")
        text = client.extract_text(response)
        
        print("\n" + "=" * 60)
        print("Claude 응답:")
        print("=" * 60)
        print(text)
        print("=" * 60)
        
        # 메타데이터 출력
        print("\n[응답 메타데이터]")
        print(f"Stop Reason: {response.get('stopReason')}")
        
        usage = response.get('usage', {})
        print(f"Input Tokens: {usage.get('inputTokens', 0)}")
        print(f"Output Tokens: {usage.get('outputTokens', 0)}")
        print(f"Total Tokens: {usage.get('totalTokens', 0)}")
        
        print("\n✅ 모든 테스트 통과!")
        print("Bedrock 연결이 정상적으로 작동합니다.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        print("\n[문제 해결 가이드]")
        print("1. AWS 자격 증명 확인:")
        print("   - .env 파일에 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY 설정")
        print("   - 또는 'aws configure' 명령어로 설정")
        print("\n2. Bedrock 모델 액세스 확인:")
        print("   - AWS Console → Bedrock → Model access")
        print("   - Claude 3.5 Sonnet v2 모델 활성화 필요")
        print("\n3. IAM 권한 확인:")
        print("   - bedrock:InvokeModel 권한 필요")
        print("\n4. 리전 확인:")
        print(f"   - 현재 리전: {settings.aws_region}")
        print("   - Claude 3.5 Sonnet v2는 us-east-1, us-west-2 등에서 사용 가능")
        
        return False


async def test_json_parsing():
    """JSON 응답 파싱 테스트"""
    print("\n" + "=" * 60)
    print("JSON 응답 파싱 테스트")
    print("=" * 60)
    
    try:
        client = BedrockClient()
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": """다음 형식의 JSON으로 응답해주세요:
{
  "name": "Claude",
  "version": "3.5",
  "message": "안녕하세요!"
}"""
                    }
                ]
            }
        ]
        
        response = await client.converse(messages=messages)
        text = client.extract_text(response)
        
        print("\n[원본 응답]")
        print(text)
        
        # JSON 파싱
        parsed = client.parse_json_response(text)
        
        print("\n[파싱된 JSON]")
        print(parsed)
        
        print("\n✅ JSON 파싱 테스트 통과!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ JSON 파싱 테스트 실패: {str(e)}")
        return False


async def main():
    """메인 테스트 실행"""
    print("\n🚀 PlanIt-InsightAI-svc Bedrock 테스트\n")
    
    # 기본 연결 테스트
    test1 = await test_bedrock_connection()
    
    if test1:
        # JSON 파싱 테스트
        test2 = await test_json_parsing()
        
        if test2:
            print("\n" + "=" * 60)
            print("🎉 모든 테스트 완료! Bedrock 준비 완료!")
            print("=" * 60)
    
    print("\n다음 단계: 리포트 생성 서비스 구현")


if __name__ == "__main__":
    asyncio.run(main())
