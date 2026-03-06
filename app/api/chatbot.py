"""
챗봇 API 라우터
"""
import logging
from fastapi import APIRouter, HTTPException

from app.models.request import ChatQueryRequest
from app.models.response import ChatQueryResponse
from app.clients.bedrock_client import BedrockClient
from app.clients.database_client import get_database_client
from app.services.chatbot import ChatbotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/chat", tags=["Chatbot"])

# 싱글톤 인스턴스
bedrock_client = BedrockClient()
chatbot_service = None


async def get_chatbot_service():
    """ChatbotService 싱글톤 반환"""
    global chatbot_service
    if chatbot_service is None:
        db_client = await get_database_client()
        chatbot_service = ChatbotService(bedrock_client, db_client)
    return chatbot_service


@router.post("/query", response_model=ChatQueryResponse)
async def query_chatbot(request: ChatQueryRequest):
    """
    챗봇 질의 API (Bedrock Tool Use 방식)
    
    Claude가 자율적으로 데이터베이스를 조회하여 답변 생성
    """
    try:
        logger.info(f"Chatbot query requested: user={request.user_id}, query={request.query}")
        
        # ChatbotService 가져오기
        service = await get_chatbot_service()
        
        # 질의 처리
        result = await service.process_query(
            user_id=request.user_id,
            query=request.query
        )
        
        logger.info(f"Chatbot query completed: user={request.user_id}")
        
        return ChatQueryResponse(**result)
    
    except Exception as e:
        logger.error(f"Chatbot query failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 질의 처리 중 오류가 발생했습니다: {str(e)}"
        )
