"""
챗봇 서비스 (Bedrock Tool Use 방식)
Claude가 자율적으로 데이터베이스 조회 및 분석
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.clients.bedrock_client import BedrockClient
from app.clients.database_client import DatabaseClient

logger = logging.getLogger(__name__)


class ChatbotService:
    """Bedrock Tool Use 기반 챗봇 서비스"""
    
    def __init__(
        self,
        bedrock_client: BedrockClient,
        db_client: DatabaseClient
    ):
        self.bedrock = bedrock_client
        self.db = db_client
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict]:
        """
        Bedrock Tool Spec 정의
        Claude가 사용할 수 있는 도구들을 정의
        """
        return [
            {
                "toolSpec": {
                    "name": "query_user_action_logs",
                    "description": """사용자의 할 일 처리 로그를 조회합니다. 
                    
action_type 파라미터 사용법:
- 'COMPLETED': 완료한 할 일만 조회 (사용자가 잘한 요일, 생산적인 요일을 물을 때 사용)
- 'POSTPONED': 미룬 할 일만 조회 (사용자가 못한 요일, 미룬 요일을 물을 때 사용)
- 생략: 모든 액션 조회 (완료율 계산 시 사용)

반환 데이터: day_of_week(요일), count(횟수) 형태의 리스트""",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "start_date": {
                                    "type": "string",
                                    "description": "시작 날짜 (YYYY-MM-DD 형식)"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "종료 날짜 (YYYY-MM-DD 형식)"
                                },
                                "action_type": {
                                    "type": "string",
                                    "description": "액션 타입 필터. COMPLETED=완료한 할 일, POSTPONED=미룬 할 일. 생략하면 모든 액션 조회.",
                                    "enum": ["COMPLETED", "POSTPONED", "DELETED"]
                                }
                            },
                            "required": ["start_date", "end_date"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "calculate_completion_rate",
                    "description": "특정 기간의 할 일 완료율을 계산합니다.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "period": {
                                    "type": "string",
                                    "description": "기간 ('week' 또는 'month')",
                                    "enum": ["week", "month"]
                                }
                            },
                            "required": ["period"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "analyze_postpone_pattern",
                    "description": "요일별 미룸 패턴을 분석합니다. 어느 요일에 가장 많이 미루는지 확인할 수 있습니다.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "start_date": {
                                    "type": "string",
                                    "description": "시작 날짜 (YYYY-MM-DD 형식)"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "종료 날짜 (YYYY-MM-DD 형식)"
                                }
                            },
                            "required": ["start_date", "end_date"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_recent_todos",
                    "description": "최근 할 일 목록을 조회합니다.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "description": "조회할 개수 (기본값: 10)",
                                    "default": 10
                                }
                            }
                        }
                    }
                }
            }
        ]
    
    async def process_query(self, user_id: str, query: str) -> Dict:
        """
        사용자 질의 처리 (Bedrock Tool Use 워크플로우)
        
        Args:
            user_id: 사용자 ID
            query: 사용자 질의
        
        Returns:
            답변 및 출처 정보
        """
        logger.info("-" * 80)
        logger.info(f"[ChatbotService] Starting process_query")
        logger.info(f"  User ID: {user_id}")
        logger.info(f"  Query: {query}")
        logger.info("-" * 80)
        
        # 대화 컨텍스트 초기화
        messages = [
            {
                "role": "user",
                "content": [{"text": query}]
            }
        ]
        
        system_prompt = f"""# 페르소나 및 역할
당신은 사용자의 성장과 시간 관리를 돕는 'PlanIt' 서비스의 전문 AI 코치입니다.
사용자 ID: {user_id}
오늘 날짜: {datetime.now().strftime('%Y-%m-%d')}

# 핵심 미션
사용자의 할 일 관리, 생산성 향상, 목표 달성을 돕는 것이 당신의 유일한 목적입니다.

# 도메인 제한 (매우 중요!)
다음 주제에 대해서만 답변하세요:
✅ 할 일(Task) 관리 및 완료 현황
✅ 미룸 습관(Postpone) 분석 및 개선
✅ 목표(Goal) 달성률 및 진척도
✅ 생산성(Productivity) 패턴 분석
✅ 시간 관리 및 요일별 성과
✅ 완료율, 통계, 트렌드 분석

# Off-topic 질문 처리 (절대 규칙!)
다음과 같은 서비스 도메인 외 질문이 들어오면 절대 답변하지 마세요:
❌ 날씨, 뉴스, 시사
❌ 코딩, 프로그래밍, 기술 질문
❌ 일반 상식, 역사, 과학
❌ 요리, 여행, 쇼핑
❌ 수학 문제 풀이
❌ 번역, 작문
❌ 기타 PlanIt 서비스와 무관한 모든 질문

이런 질문이 들어오면 반드시 다음과 같이 정중히 거절하세요:
"저는 할 일 관리와 생산성 향상을 돕는 PlanIt AI 코치입니다. 사용자의 목표 달성과 관련된 질문을 남겨주시면 최선을 다해 답변해 드릴게요! 😊

예를 들어 이런 질문을 해보세요:
• 지난 주에 가장 생산적이었던 요일은?
• 이번 달 완료율은 얼마나 되나요?
• 어느 요일에 할 일을 가장 많이 미루나요?
• 최근 완료한 할 일을 보여주세요."

# 데이터 조회 도구 사용 규칙
제공된 도구를 사용하여 데이터베이스에서 정보를 조회하고 분석하세요.

1. query_user_action_logs 도구 사용 시:
   - action_type='COMPLETED': 완료한 할 일만 조회
   - action_type='POSTPONED': 미룬 할 일만 조회
   - action_type 없음: 모든 액션 조회

2. 사용자가 "완료를 많이 한 요일", "잘한 요일", "생산적인 요일" 등을 물으면:
   - 반드시 action_type='COMPLETED'로 조회하세요
   - 완료(COMPLETED) 횟수가 많은 요일을 찾으세요
   - 미룸(POSTPONED) 데이터는 무시하세요

3. 사용자가 "미룬 요일", "못한 요일", "안 좋은 요일" 등을 물으면:
   - 반드시 action_type='POSTPONED'로 조회하세요
   - 미룸(POSTPONED) 횟수가 많은 요일을 찾으세요

4. 요일별 완료율을 물으면:
   - 전체 로그를 조회하고
   - 요일별로 (완료 수 / 전체 수) * 100을 계산하세요

# 답변 스타일
- 친근하고 격려하는 톤 사용
- 구체적인 숫자와 데이터 기반 답변
- 실행 가능한 조언 제공
- 이모지 적절히 활용 (😊, 💪, 📊 등)"""
        
        sources = []
        max_iterations = 5  # 무한 루프 방지
        
        for iteration in range(max_iterations):
            # Bedrock Converse API 호출 (Tool Use 활성화)
            response = await self.bedrock.converse(
                messages=messages,
                system_prompt=system_prompt,
                tools=self.tools,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Tool Use 확인
            if self.bedrock.has_tool_use(response):
                # Tool 실행
                tool_use = self.bedrock.extract_tool_use(response)
                logger.info(f"Tool use detected: {tool_use['name']}")
                
                # Tool 실행
                tool_result = await self._execute_tool(
                    tool_name=tool_use['name'],
                    tool_input=tool_use['input'],
                    user_id=user_id
                )
                
                # 출처 기록
                sources.append(f"{tool_use['name']} 실행")
                
                # 대화 컨텍스트에 추가
                messages.append({
                    "role": "assistant",
                    "content": response['output']['message']['content']
                })
                
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "toolResult": {
                                "toolUseId": tool_use['toolUseId'],
                                "content": [
                                    {"json": tool_result}
                                ]
                            }
                        }
                    ]
                })
            else:
                # 최종 답변 생성
                answer = self.bedrock.extract_text(response)
                logger.info("-" * 80)
                logger.info(f"[ChatbotService] Final answer generated")
                logger.info(f"  Answer preview: {answer[:100]}...")
                logger.info(f"  Answer length: {len(answer)} chars")
                logger.info(f"  Sources used: {', '.join(sources) if sources else 'None'}")
                logger.info("-" * 80)
                
                return {
                    "answer": answer,
                    "sources": sources if sources else ["직접 답변"],
                    "generated_at": datetime.now().isoformat()
                }
        
        # 최대 반복 횟수 초과
        logger.warning("-" * 80)
        logger.warning(f"[ChatbotService] Max iterations reached")
        logger.warning(f"  Query: {query}")
        logger.warning(f"  Iterations: {max_iterations}")
        logger.warning("-" * 80)
        return {
            "answer": "죄송합니다. 질문을 처리하는 데 시간이 너무 오래 걸렸습니다. 질문을 더 구체적으로 해주시겠어요?",
            "sources": sources,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _execute_tool(
        self,
        tool_name: str,
        tool_input: Dict,
        user_id: str
    ) -> Dict:
        """
        Tool 실행 및 결과 반환
        
        Args:
            tool_name: Tool 이름
            tool_input: Tool 입력 파라미터
            user_id: 사용자 ID
        
        Returns:
            Tool 실행 결과 (JSON 직렬화 가능한 형태)
        """
        logger.info("=" * 80)
        logger.info(f"[Tool Execution] {tool_name}")
        logger.info(f"  User ID: {user_id}")
        logger.info(f"  Input Parameters: {tool_input}")
        logger.info("=" * 80)
        
        try:
            if tool_name == "query_user_action_logs":
                logger.info(f"[Tool] Querying action logs from database...")
                logger.info(f"  Query Details:")
                logger.info(f"    - user_id: {user_id}")
                logger.info(f"    - start_date: {tool_input['start_date']}")
                logger.info(f"    - end_date: {tool_input['end_date']}")
                logger.info(f"    - action_type: {tool_input.get('action_type', 'ALL (no filter)')}")
                
                results = await self.db.query_action_logs(
                    user_id=user_id,
                    start_date=tool_input['start_date'],
                    end_date=tool_input['end_date'],
                    action_type=tool_input.get('action_type')
                )
                
                logger.info(f"[Tool] Query returned {len(results)} records")
                
                # 결과 샘플 로깅
                if len(results) > 0:
                    logger.info(f"[Tool] Sample (first record): {results[0]}")
                else:
                    logger.warning("=" * 80)
                    logger.warning(f"[Tool] ⚠️ WARNING: No records found!")
                    logger.warning(f"  This means the query returned 0 results.")
                    logger.warning(f"  Possible causes:")
                    logger.warning(f"    1. user_id '{user_id}' has no data in database")
                    logger.warning(f"    2. Date range has no data: {tool_input['start_date']} ~ {tool_input['end_date']}")
                    logger.warning(f"    3. action_type filter '{tool_input.get('action_type')}' excludes all records")
                    logger.warning(f"  Run 'python check_data.py' to verify database contents")
                    logger.warning("=" * 80)
                
                # datetime 객체를 문자열로 변환
                serialized_results = []
                for row in results:
                    serialized_row = {}
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            serialized_row[key] = value.isoformat()
                        elif value is None:
                            serialized_row[key] = None
                        else:
                            serialized_row[key] = str(value) if not isinstance(value, (int, float, bool, str)) else value
                    serialized_results.append(serialized_row)
                
                # 요일별 집계 추가 (Claude가 쉽게 이해할 수 있도록)
                day_counts = {}
                for row in serialized_results:
                    day = row.get('day_of_week', 'UNKNOWN')
                    day_counts[day] = day_counts.get(day, 0) + 1
                
                return {
                    "success": True,
                    "data": serialized_results,
                    "count": len(serialized_results),
                    "summary_by_day": day_counts
                }
            
            elif tool_name == "calculate_completion_rate":
                logger.info(f"[Tool] Calculating completion rate...")
                rate = await self.db.calculate_completion_rate(
                    user_id=user_id,
                    period=tool_input['period']
                )
                logger.info(f"[Tool] Completion rate: {rate}%")
                return {
                    "success": True,
                    "completion_rate": float(rate),
                    "period": tool_input['period']
                }
            
            elif tool_name == "analyze_postpone_pattern":
                logger.info(f"[Tool] Analyzing postpone pattern...")
                pattern = await self.db.analyze_postpone_pattern(
                    user_id=user_id,
                    start_date=tool_input['start_date'],
                    end_date=tool_input['end_date']
                )
                logger.info(f"[Tool] Pattern analysis complete: worst_day={pattern.get('worst_day')}")
                return {
                    "success": True,
                    "pattern": pattern
                }
            
            elif tool_name == "get_recent_todos":
                logger.info(f"[Tool] Getting recent todos...")
                todos = await self.db.get_recent_todos(
                    user_id=user_id,
                    limit=tool_input.get('limit', 10)
                )
                logger.info(f"[Tool] Retrieved {len(todos)} todos")
                
                # datetime 객체를 문자열로 변환
                serialized_todos = []
                for row in todos:
                    serialized_row = {}
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            serialized_row[key] = value.isoformat()
                        elif value is None:
                            serialized_row[key] = None
                        else:
                            serialized_row[key] = str(value) if not isinstance(value, (int, float, bool, str)) else value
                    serialized_todos.append(serialized_row)
                
                return {
                    "success": True,
                    "todos": serialized_todos,
                    "count": len(serialized_todos)
                }
            
            else:
                logger.error(f"[Tool] Unknown tool: {tool_name}")
                return {
                    "success": False,
                    "error": f"알 수 없는 도구: {tool_name}"
                }
        
        except Exception as e:
            logger.error(f"[Tool] Execution failed: {tool_name}, error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
