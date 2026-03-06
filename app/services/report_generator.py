"""
리포트 생성 서비스 (Context Injection 방식)
Prompt Chaining 기법으로 4단계 피드백 생성
"""
import logging
from typing import Dict
from datetime import datetime

from app.clients.bedrock_client import BedrockClient
from app.models.response import (
    GrowthFeedback,
    TimelineFeedback,
    PatternFeedback,
    SummaryFeedback,
    ReportData,
    ReportGenerationResponse,
    ChartDataPointResponse,
    DailyStatsResponse
)

logger = logging.getLogger(__name__)


# 기본 템플릿 (Bedrock 호출 실패 시 사용)
DEFAULT_TEMPLATES = {
    "growth": {
        "message": "데이터를 분석 중입니다. 잠시 후 다시 확인해주세요."
    },
    "timeline": {
        "message": "타임라인 데이터를 준비 중입니다."
    },
    "pattern": {
        "message": "패턴 분석을 진행 중입니다."
    },
    "summary": {
        "message": "종합 리포트를 생성 중입니다."
    }
}


class ReportGeneratorService:
    """리포트 생성 서비스"""
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock = bedrock_client
    
    async def generate_report(self, stats_data: Dict) -> ReportGenerationResponse:
        """
        4단계 Prompt Chaining으로 리포트 생성
        
        Args:
            stats_data: 통계 데이터
        
        Returns:
            리포트 생성 응답
        """
        logger.info("Starting report generation")
        
        # Step 1-3: 병렬로 Growth, Timeline, Pattern 피드백 생성
        growth_feedback = await self._generate_growth_feedback(stats_data['growth'])
        timeline_feedback = await self._generate_timeline_feedback(stats_data['timeline'])
        pattern_feedback = await self._generate_pattern_feedback(stats_data['pattern'])
        
        # Step 4: Summary 피드백 생성 (이전 결과 참조)
        summary_feedback = await self._generate_summary_feedback(
            growth_feedback,
            timeline_feedback,
            pattern_feedback,
            stats_data['summary']
        )
        
        # 리포트 데이터 구성
        report_data = ReportData(
            growth=growth_feedback,
            timeline=timeline_feedback,
            pattern=pattern_feedback,
            summary=summary_feedback
        )
        
        logger.info("Report generation completed successfully")
        
        return ReportGenerationResponse(
            success=True,
            report_data=report_data,
            generated_at=datetime.now().isoformat()
        )
    
    async def _generate_growth_feedback(self, growth_data: Dict) -> GrowthFeedback:
        """
        성장 피드백 생성
        
        Args:
            growth_data: 성장 데이터
        
        Returns:
            성장 피드백
        """
        try:
            system_prompt = """당신은 사용자의 할 일 관리 데이터를 분석하여 긍정적이고 동기부여가 되는 피드백을 제공하는 AI 어시스턴트입니다.

# 핵심 규칙
1. 반드시 "이전 3개월 보다 [topic_name] 분야에서 [growth_rate]% 성장했어요!"라는 문구를 포함해야 합니다.
2. 성장률이 양수일 때는 격려와 칭찬을, 음수일 때는 위로와 응원을 제공합니다.
3. 친근하고 따뜻한 톤을 유지하며, 이모지를 적절히 활용합니다.
4. 메시지는 2-3문장으로 간결하게 작성합니다.

# 출력 형식
반드시 JSON 형식으로만 응답하세요."""
            
            topic_name = growth_data.get('topic_name', '전체')
            growth_rate = growth_data.get('growth_rate', 0)
            previous_rate = growth_data.get('previous_rate', 0)
            current_rate = growth_data.get('current_rate', 0)
            
            # Few-shot 예시 포함
            user_message = f"""다음 성장 데이터를 분석하여 피드백을 생성해주세요:

주제: {topic_name}
성장률: {growth_rate}%
이전 완료율: {previous_rate}%
현재 완료율: {current_rate}%

# 출력 예시

예시 1 (성장률 양수):
입력: 주제=운동, 성장률=24%, 이전=60%, 현재=75%
출력:
{{
  "topicName": "운동",
  "growthRate": 24,
  "message": "이전 3개월 보다 운동 분야에서 24% 성장했어요! 정말 대단한 변화입니다. 꾸준한 노력이 빛을 발하고 있네요 💪"
}}

예시 2 (성장률 양수, 다른 주제):
입력: 주제=업무, 성장률=15%, 이전=55%, 현재=63%
출력:
{{
  "topicName": "업무",
  "growthRate": 15,
  "message": "이전 3개월 보다 업무 분야에서 15% 성장했어요! 업무 효율이 크게 향상되었네요. 이 추세를 계속 유지해보세요 🎯"
}}

예시 3 (성장률 음수):
입력: 주제=학습, 성장률=-10%, 이전=70%, 현재=63%
출력:
{{
  "topicName": "학습",
  "growthRate": -10,
  "message": "이전 3개월 보다 학습 분야에서 -10% 변화가 있었어요. 누구에게나 슬럼프는 있어요. 작은 목표부터 다시 시작해보는 건 어떨까요? 😊"
}}

예시 4 (성장률 0 근처):
입력: 주제=독서, 성장률=2%, 이전=50%, 현재=51%
출력:
{{
  "topicName": "독서",
  "growthRate": 2,
  "message": "이전 3개월 보다 독서 분야에서 2% 성장했어요! 꾸준함이 가장 중요합니다. 지금처럼 계속 유지해보세요 📚"
}}

# 실제 데이터로 생성
위 예시를 참고하여, 주어진 데이터로 피드백을 생성해주세요.
반드시 "이전 3개월 보다 {topic_name} 분야에서 {growth_rate}% 성장했어요!" 문구를 포함해야 합니다.

다음 JSON 형식으로 응답하세요:
{{
  "topicName": "{topic_name}",
  "growthRate": {growth_rate},
  "message": "피드백 메시지 (2-3문장, 반드시 '이전 3개월 보다...' 문구 포함)"
}}"""
            
            messages = [
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ]
            
            response = await self.bedrock.converse(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            text = self.bedrock.extract_text(response)
            parsed = self.bedrock.parse_json_response(text)
            
            return GrowthFeedback(**parsed)
        
        except Exception as e:
            logger.error(f"Growth feedback generation failed: {e}")
            return GrowthFeedback(
                topic_name=growth_data.get("topic_name", "전체"),
                growth_rate=growth_data.get("growth_rate", 0),
                message=f"이전 3개월 보다 {growth_data.get('topic_name', '전체')} 분야에서 {growth_data.get('growth_rate', 0)}% 성장했어요! 데이터를 분석 중입니다."
            )
    
    async def _generate_timeline_feedback(self, timeline_data: Dict) -> TimelineFeedback:
        """
        타임라인 피드백 생성
        
        Args:
            timeline_data: 타임라인 데이터
        
        Returns:
            타임라인 피드백
        """
        try:
            system_prompt = """당신은 사용자의 할 일 관리 데이터를 분석하여 긍정적이고 동기부여가 되는 피드백을 제공하는 AI 어시스턴트입니다.
주어진 타임라인 데이터를 분석하여 추세를 설명하는 메시지를 생성하세요.
반드시 JSON 형식으로만 응답하세요."""
            
            chart_data_str = "\n".join([
                f"- {item['month']}: {item['completion_rate']}%"
                for item in timeline_data['chart_data']
            ])
            
            user_message = f"""다음 타임라인 데이터를 분석하여 피드백을 생성해주세요:

{chart_data_str}

다음 JSON 형식으로 응답하세요:
{{
  "chartData": {timeline_data['chart_data']},
  "message": "추세 분석 메시지 (1-2문장, 긍정적인 톤)"
}}"""
            
            messages = [
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ]
            
            response = await self.bedrock.converse(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            text = self.bedrock.extract_text(response)
            parsed = self.bedrock.parse_json_response(text)
            
            # chartData를 ChartDataPointResponse로 변환
            chart_data_responses = [
                ChartDataPointResponse(**item)
                for item in parsed['chartData']
            ]
            
            return TimelineFeedback(
                chart_data=chart_data_responses,
                message=parsed['message']
            )
        
        except Exception as e:
            logger.error(f"Timeline feedback generation failed: {e}")
            chart_data_responses = [
                ChartDataPointResponse(**item)
                for item in timeline_data.get('chart_data', [])
            ]
            return TimelineFeedback(
                chart_data=chart_data_responses,
                message=DEFAULT_TEMPLATES["timeline"]["message"]
            )
    
    async def _generate_pattern_feedback(self, pattern_data: Dict) -> PatternFeedback:
        """
        패턴 피드백 생성
        
        Args:
            pattern_data: 패턴 데이터
        
        Returns:
            패턴 피드백
        """
        try:
            system_prompt = """당신은 사용자의 할 일 관리 데이터를 분석하여 긍정적이고 동기부여가 되는 피드백을 제공하는 AI 어시스턴트입니다.
주어진 요일별 패턴 데이터를 분석하여 개선 제안을 포함한 메시지를 생성하세요.
반드시 JSON 형식으로만 응답하세요."""
            
            daily_stats_str = "\n".join([
                f"- {item['day']}: 총 {item['total']}개, 완료 {item['completed']}개, 미룸 {item['postponed']}개"
                for item in pattern_data['daily_stats']
            ])
            
            # 가장 많이 미룬 요일 찾기
            worst_day_data = max(pattern_data['daily_stats'], key=lambda x: x['postponed'])
            worst_day = worst_day_data['day']
            
            # 평균 미룬 횟수 계산
            total_postponed = sum(item['postponed'] for item in pattern_data['daily_stats'])
            avg_postpone = round(total_postponed / len(pattern_data['daily_stats']), 1)
            
            user_message = f"""다음 요일별 패턴 데이터를 분석하여 피드백을 생성해주세요:

{daily_stats_str}

다음 JSON 형식으로 응답하세요:
{{
  "worstDay": "{worst_day}",
  "avgPostponeCount": {avg_postpone},
  "chartData": {pattern_data['daily_stats']},
  "message": "패턴 분석 및 개선 제안 메시지 (1-2문장, 건설적인 톤)"
}}"""
            
            messages = [
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ]
            
            response = await self.bedrock.converse(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            text = self.bedrock.extract_text(response)
            parsed = self.bedrock.parse_json_response(text)
            
            # chartData를 DailyStatsResponse로 변환
            chart_data_responses = [
                DailyStatsResponse(**item)
                for item in parsed['chartData']
            ]
            
            return PatternFeedback(
                worst_day=parsed['worstDay'],
                avg_postpone_count=parsed['avgPostponeCount'],
                chart_data=chart_data_responses,
                message=parsed['message']
            )
        
        except Exception as e:
            logger.error(f"Pattern feedback generation failed: {e}")
            worst_day_data = max(pattern_data['daily_stats'], key=lambda x: x['postponed'])
            total_postponed = sum(item['postponed'] for item in pattern_data['daily_stats'])
            avg_postpone = round(total_postponed / len(pattern_data['daily_stats']), 1)
            
            chart_data_responses = [
                DailyStatsResponse(**item)
                for item in pattern_data.get('daily_stats', [])
            ]
            
            return PatternFeedback(
                worst_day=worst_day_data['day'],
                avg_postpone_count=avg_postpone,
                chart_data=chart_data_responses,
                message=DEFAULT_TEMPLATES["pattern"]["message"]
            )
    
    async def _generate_summary_feedback(
        self,
        growth: GrowthFeedback,
        timeline: TimelineFeedback,
        pattern: PatternFeedback,
        summary_data: Dict
    ) -> SummaryFeedback:
        """
        종합 피드백 생성 (Prompt Chaining - 이전 3개 결과 참조)
        
        Args:
            growth: 성장 피드백
            timeline: 타임라인 피드백
            pattern: 패턴 피드백
            summary_data: 요약 데이터
        
        Returns:
            종합 피드백
        """
        try:
            system_prompt = """당신은 사용자의 할 일 관리 데이터를 분석하여 긍정적이고 동기부여가 되는 피드백을 제공하는 AI 어시스턴트입니다.
이전에 생성된 성장, 타임라인, 패턴 피드백을 종합하여 전체적인 평가 메시지를 생성하세요.
반드시 JSON 형식으로만 응답하세요."""
            
            user_message = f"""다음 정보를 종합하여 전체 피드백을 생성해주세요:

[성장 피드백]
{growth.message}

[타임라인 피드백]
{timeline.message}

[패턴 피드백]
{pattern.message}

[전체 통계]
- 총 할 일: {summary_data['total_tasks']}개
- 완료한 할 일: {summary_data['completed_tasks']}개
- 완료율: {summary_data['completion_rate']}%
- 달성 추세: {summary_data['achievement_trend']}

다음 JSON 형식으로 응답하세요:
{{
  "message": "종합 평가 메시지 (2-3문장, 격려와 동기부여)"
}}"""
            
            messages = [
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ]
            
            response = await self.bedrock.converse(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            text = self.bedrock.extract_text(response)
            parsed = self.bedrock.parse_json_response(text)
            
            return SummaryFeedback(**parsed)
        
        except Exception as e:
            logger.error(f"Summary feedback generation failed: {e}")
            return SummaryFeedback(
                message=DEFAULT_TEMPLATES["summary"]["message"]
            )
