"""
Chatbot gRPC Servicer
기존 ChatbotService 로직을 gRPC Servicer에 연결
"""
import logging
from datetime import datetime
import time

import grpc

# gRPC generated code import (proto 컴파일 후 생성됨)
from app.grpc_generated import chat_service_pb2
from app.grpc_generated import chat_service_pb2_grpc

# 기존 서비스 import
from app.services.chatbot import ChatbotService
from app.clients.bedrock_client import BedrockClient
from app.clients.database_client import DatabaseClient
from app.core.config import get_settings
from app.core.logging_config import log_with_data

settings = get_settings()

logger = logging.getLogger(__name__)


class ChatbotServicer(chat_service_pb2_grpc.ChatbotServiceServicer):
    """
    ChatbotService gRPC Servicer
    
    기존 ChatbotService의 query_chatbot() 로직을
    gRPC QueryChatbot() RPC 메서드에 연결
    """
    
    def __init__(self):
        """
        Servicer 초기화
        BedrockClient와 DatabaseClient를 주입하여 ChatbotService 생성
        """
        self.bedrock_client = BedrockClient()
        # DatabaseClient는 싱글톤으로 관리되므로 여기서는 None으로 초기화
        self.database_client = None
        logger.info("ChatbotServicer initialized")
    
    async def _get_database_client(self):
        """DatabaseClient 싱글톤 가져오기"""
        if self.database_client is None:
            from app.clients.database_client import get_database_client
            self.database_client = await get_database_client()
        return self.database_client
    
    async def QueryChatbot(
        self,
        request: chat_service_pb2.ChatRequest,
        context: grpc.aio.ServicerContext
    ) -> chat_service_pb2.ChatResponse:
        """
        챗봇 질의 처리 (Unary RPC)
        
        Args:
            request: ChatRequest (user_id, query)
            context: gRPC context
            
        Returns:
            ChatResponse (answer, sources, generated_at)
        """
        start_time = time.time()
        
        user_id = request.user_id
        query = request.query
        
        # 요청 로그 (구조화)
        log_with_data(logger, 'info', 'gRPC 요청 수신',
                      method='QueryChatbot',
                      userId=user_id,
                      query=query,
                      peer=context.peer())
        
        try:
            # 유효성 검증
            if not user_id or not query:
                log_with_data(logger, 'warning', 'gRPC 유효성 검증 실패',
                              userId=user_id,
                              has_query=bool(query))
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("user_id and query are required")
                return chat_service_pb2.ChatResponse()
            
            # DatabaseClient 가져오기
            database_client = await self._get_database_client()
            
            # ChatbotService 생성 및 호출
            chatbot_service = ChatbotService(
                bedrock_client=self.bedrock_client,
                db_client=database_client
            )
            
            result = await chatbot_service.process_query(
                user_id=user_id,
                query=query
            )
            
            # gRPC Response 생성
            response = chat_service_pb2.ChatResponse(
                answer=result["answer"],
                sources=result["sources"],
                generated_at=result["generated_at"]
            )
            
            # 성공 로그
            elapsed_time = time.time() - start_time
            log_with_data(logger, 'info', 'gRPC 응답 성공',
                          method='QueryChatbot',
                          userId=user_id,
                          answer_len=len(result['answer']),
                          sources=result['sources'],
                          duration_ms=int(elapsed_time * 1000))
            
            return response
            
        except ValueError as e:
            # 유효성 검증 에러
            elapsed_time = time.time() - start_time
            log_with_data(logger, 'error', 'gRPC 유효성 검증 에러',
                          method='QueryChatbot',
                          userId=user_id,
                          error=str(e),
                          duration_ms=int(elapsed_time * 1000))
            
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return chat_service_pb2.ChatResponse()
            
        except Exception as e:
            # 서버 에러
            elapsed_time = time.time() - start_time
            log_with_data(logger, 'error', 'gRPC 내부 서버 에러',
                          method='QueryChatbot',
                          userId=user_id,
                          error_type=type(e).__name__,
                          error=str(e),
                          duration_ms=int(elapsed_time * 1000))
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return chat_service_pb2.ChatResponse()
