# 1단계: Builder Stage
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2단계: Runtime Stage (최종 이미지)
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH
ENV PORT=8085
ENV GRPC_PORT=9095
ENV APP_MODE=http

#  [수정 1] 유저를 먼저 생성합니다.
RUN useradd -m -u 1000 appuser

#  [수정 2] COPY 할 때 처음부터 appuser 권한으로 가져와서 레이어 용량 뻥튀기를 막습니다.
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./proto ./proto

USER appuser

EXPOSE 8085 9095

#  [수정 3] exec를 추가하여 EKS(K8s)의 SIGTERM(종료 신호)을 앱이 직접 받도록 수정합니다.
# --log-config 제거하여 PlanIt 표준 JSON 로깅 사용
CMD ["sh", "-c", "if [ \"$APP_MODE\" = \"grpc\" ]; then exec python -m app.main_grpc; else exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8085} --log-config /dev/null; fi"]