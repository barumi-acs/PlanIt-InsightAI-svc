"""
PlanIt 표준 JSON 로깅 설정
모든 로그를 JSON 형식으로 출력하여 CloudWatch/ELK 수집 용이
"""
import logging
import sys
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

# Trace ID를 저장할 context variable
trace_id_var: ContextVar[str] = ContextVar('trace_id', default='')


class PlanItJsonFormatter(jsonlogger.JsonFormatter):
    """
    PlanIt 표준 JSON 로그 포맷터 (평탄화 구조)
    
    출력 형식:
    {
        "timestamp": "2026-03-20T01:55:13.123Z",
        "level": "INFO",
        "service": "insightai-svc",
        "traceId": "69bca901634fcccf364e4f7bdb2931a9",
        "logger": "app.services.report_generator",
        "message": "리포트 생성 시작",
        "userId": "test123",
        "reportType": "GROWTH",
        "duration_ms": 1234
    }
    """
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # 필드명 매핑 (PlanIt 표준)
        from datetime import datetime, timezone
        # ISO8601 UTC 포맷 (밀리초 3자리)
        now = datetime.now(timezone.utc)
        log_record['timestamp'] = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        log_record['level'] = record.levelname
        log_record['service'] = 'insightai-svc'
        log_record['logger'] = record.name
        log_record['message'] = record.getMessage()
        
        # Trace ID 추가
        trace_id = trace_id_var.get()
        if trace_id:
            log_record['traceId'] = trace_id
        
        # 비즈니스 데이터를 루트 레벨에 평탄화 (Spring과 동일한 구조)
        if hasattr(record, 'data') and record.data:
            for key, value in record.data.items():
                log_record[key] = value
            # data 객체 자체는 제거 (중복 방지)
            log_record.pop('data', None)
        
        # 에러 발생 시 stack_trace 추가
        if record.exc_info:
            log_record['stack_trace'] = self.formatException(record.exc_info)
        
        # 불필요한 필드 제거
        for field in ['asctime', 'levelname', 'name', 'exc_info', 'exc_text', 'args', 'created', 
                      'filename', 'funcName', 'levelno', 'lineno', 'module', 'msecs', 'msg',
                      'pathname', 'process', 'processName', 'relativeCreated', 'thread', 'threadName']:
            log_record.pop(field, None)


def setup_logging(log_level: str = "INFO"):
    """
    PlanIt 표준 JSON 로깅 설정
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARN, ERROR)
    """
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # JSON 포맷 핸들러 추가 (ensure_ascii=False로 한글 깨짐 방지)
    json_handler = logging.StreamHandler(sys.stdout)
    formatter = PlanItJsonFormatter(
        '%(timestamp)s %(level)s %(service)s %(traceId)s %(logger)s %(message)s',
        json_ensure_ascii=False  # 한글 깨짐 방지
    )
    json_handler.setFormatter(formatter)
    root_logger.addHandler(json_handler)
    
    # uvicorn 로거도 JSON 포맷 적용
    for logger_name in ['uvicorn', 'uvicorn.access', 'uvicorn.error']:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(json_handler)
        logger.propagate = False


def log_with_data(logger: logging.Logger, level: str, message: str, **data):
    """
    구조화된 데이터와 함께 로그 출력 (평탄화 구조)
    
    Args:
        logger: 로거 인스턴스
        level: 로그 레벨 (info, warning, error, debug)
        message: 로그 메시지
        **data: 추가 비즈니스 데이터 (루트 레벨에 평탄화됨)
    
    Example:
        log_with_data(logger, 'info', '리포트 생성 완료', 
                      userId='test123', reportType='GROWTH', duration_ms=1234)
        
        출력:
        {
            "timestamp": "2026-03-20T01:55:13.123Z",
            "level": "INFO",
            "service": "insightai-svc",
            "traceId": "69bca901634fcccf364e4f7bdb2931a9",
            "logger": "app.services.report_generator",
            "message": "리포트 생성 완료",
            "userId": "test123",
            "reportType": "GROWTH",
            "duration_ms": 1234
        }
    """
    log_func = getattr(logger, level.lower())
    log_func(message, extra={'data': data})


def set_trace_id(trace_id: str):
    """
    현재 요청의 Trace ID 설정
    
    Args:
        trace_id: MSA 추적용 Trace ID
    """
    trace_id_var.set(trace_id)


def get_trace_id() -> str:
    """
    현재 요청의 Trace ID 조회
    
    Returns:
        Trace ID 문자열
    """
    return trace_id_var.get()
