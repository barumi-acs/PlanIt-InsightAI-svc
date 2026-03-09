"""
PlanIt-InsightAI Service - gRPC Server 실행 스크립트
Java Insight-svc에서 호출하는 gRPC 서버만 실행합니다.
"""
import subprocess
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("PlanIt-InsightAI Service - Starting gRPC Server")
    print("=" * 60)
    print()
    print("[INFO] gRPC Server will start on port 9095")
    print("[INFO] This service is called by Insight-svc (Java)")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "app.main_grpc"])
    except KeyboardInterrupt:
        print("\n\nShutting down gRPC server...")
        print("Server stopped.")
