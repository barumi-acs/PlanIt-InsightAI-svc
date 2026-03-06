"""
환경 변수 설정 관리
Pydantic Settings를 활용하여 타입 안정성과 검증 제공
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 서버 설정
    port: int = 8085
    grpc_port: int = 50051  # gRPC 서버 포트
    log_level: str = "INFO"
    environment: str = "development"
    
    # AWS Bedrock 설정
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_max_tokens: int = 2000
    bedrock_temperature: float = 0.7
    bedrock_timeout: int = 30
    
    # MariaDB 설정 (MCP Tool Use용)
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "plainit_db"
    db_user: str = "root"
    db_password: str = "root"
    db_pool_size: int = 5
    db_query_timeout: int = 10
    
    # Service A 연동 (향후 확장용)
    service_a_base_url: str = "http://localhost:8080"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    싱글톤 패턴으로 설정 객체 반환
    애플리케이션 전체에서 동일한 설정 인스턴스 사용
    """
    return Settings()
