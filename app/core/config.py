from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8085
    grpc_port: int = 50051
    log_level: str = "INFO"
    environment: str = "development"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    bedrock_max_tokens: int = 2000
    bedrock_temperature: float = 0.7
    bedrock_timeout: int = 30
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "plainit_db"
    db_user: str = "root"
    db_password: str = "root"
    db_pool_size: int = 5
    db_query_timeout: int = 10
    service_a_base_url: str = "http://localhost:8084"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
