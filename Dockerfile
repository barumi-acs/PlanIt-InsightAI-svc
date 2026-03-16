# Multi-stage build for runtime image size and non-root execution
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
	&& rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH
ENV PORT=8085
ENV GRPC_PORT=9095
ENV APP_MODE=http

COPY --from=builder /opt/venv /opt/venv
COPY ./app ./app
COPY ./proto ./proto

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /opt/venv
USER appuser

EXPOSE 8085 9095

CMD ["sh", "-c", "if [ \"$APP_MODE\" = \"grpc\" ]; then python -m app.main_grpc; else python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8085}; fi"]

