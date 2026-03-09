@echo off
echo Starting PlanIt-InsightAI gRPC Server...
echo.
echo [INFO] gRPC Server will start on port 50051
echo [INFO] This service is called by Insight-svc (Java)
echo.

python -m app.main_grpc

echo.
echo gRPC Server stopped.
pause
