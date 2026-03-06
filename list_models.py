"""
AWS Bedrock에서 사용 가능한 모델 목록 조회
"""
import boto3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings

settings = get_settings()

print("=" * 80)
print("AWS Bedrock 사용 가능한 모델 목록 조회")
print("=" * 80)
print(f"\nAWS Region: {settings.aws_region}\n")

try:
    # Bedrock 클라이언트 생성
    client = boto3.client('bedrock', region_name=settings.aws_region)
    
    # 모델 목록 조회
    response = client.list_foundation_models()
    
    # Claude 모델만 필터링
    claude_models = [
        model for model in response.get('modelSummaries', [])
        if 'claude' in model.get('modelId', '').lower()
    ]
    
    print(f"총 {len(claude_models)}개의 Claude 모델 발견:\n")
    
    for model in claude_models:
        model_id = model.get('modelId')
        model_name = model.get('modelName')
        provider = model.get('providerName')
        
        print(f"Model ID: {model_id}")
        print(f"  Name: {model_name}")
        print(f"  Provider: {provider}")
        print()
    
    print("=" * 80)
    print("\n위 모델 ID 중 하나를 .env 파일의 BEDROCK_MODEL_ID에 설정하세요.")
    print("예: BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    print("\n가능한 원인:")
    print("1. AWS 자격 증명이 올바르지 않음")
    print("2. IAM 권한 부족 (bedrock:ListFoundationModels 필요)")
    print("3. 리전이 올바르지 않음")
