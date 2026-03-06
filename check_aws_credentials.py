"""
AWS 자격증명 확인 스크립트
현재 사용 중인 AWS 자격증명을 확인합니다.
"""
import boto3
import os
from datetime import datetime

print("=" * 80)
print("AWS 자격증명 확인")
print("=" * 80)

# 환경 변수 확인
print("\n[환경 변수]")
print(f"AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'NOT SET')[:20]}...")
print(f"AWS_SECRET_ACCESS_KEY: {os.environ.get('AWS_SECRET_ACCESS_KEY', 'NOT SET')[:20]}...")
print(f"AWS_SESSION_TOKEN: {os.environ.get('AWS_SESSION_TOKEN', 'NOT SET')[:20]}...")
print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'NOT SET')}")

# .env 파일 확인
print("\n[.env 파일]")
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('AWS_'):
                key = line.split('=')[0]
                value = line.split('=')[1].strip()[:20] if '=' in line else ''
                print(f"{key}: {value}...")
except FileNotFoundError:
    print(".env 파일이 없습니다!")

# boto3 세션 확인
print("\n[boto3 세션]")
try:
    session = boto3.Session()
    credentials = session.get_credentials()
    
    if credentials:
        print(f"Access Key: {credentials.access_key[:20]}...")
        print(f"Secret Key: {credentials.secret_key[:20]}...")
        if credentials.token:
            print(f"Session Token: {credentials.token[:20]}...")
            print("⚠️  임시 자격증명(Session Token) 사용 중 - 만료 가능성 있음")
        else:
            print("✅ 장기 자격증명 사용 중")
    else:
        print("❌ 자격증명을 찾을 수 없습니다!")
        
except Exception as e:
    print(f"❌ 에러: {e}")

# STS로 자격증명 유효성 확인
print("\n[자격증명 유효성 테스트]")
try:
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print(f"✅ 자격증명 유효함")
    print(f"Account: {identity['Account']}")
    print(f"UserId: {identity['UserId']}")
    print(f"Arn: {identity['Arn']}")
except Exception as e:
    print(f"❌ 자격증명 무효: {e}")

# Bedrock 접근 테스트
print("\n[Bedrock 접근 테스트]")
try:
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    # 간단한 API 호출로 테스트
    print("✅ Bedrock 클라이언트 생성 성공")
except Exception as e:
    print(f"❌ Bedrock 접근 실패: {e}")

print("\n" + "=" * 80)
print("확인 완료")
print("=" * 80)
