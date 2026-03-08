# Report Service Proto 컴파일 스크립트 (PowerShell)
# Python gRPC 코드 생성

Write-Host "Compiling report_service.proto..." -ForegroundColor Green

# proto 디렉토리로 이동
Set-Location proto

# Python gRPC 코드 생성
python -m grpc_tools.protoc `
    -I. `
    --python_out=. `
    --grpc_python_out=. `
    report_service.proto

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ report_service.proto compiled successfully!" -ForegroundColor Green
    Write-Host "Generated files:" -ForegroundColor Cyan
    Write-Host "  - report_service_pb2.py" -ForegroundColor Cyan
    Write-Host "  - report_service_pb2_grpc.py" -ForegroundColor Cyan
} else {
    Write-Host "✗ Failed to compile report_service.proto" -ForegroundColor Red
    exit 1
}

# 원래 디렉토리로 복귀
Set-Location ..

Write-Host "`nDone! You can now run the gRPC server:" -ForegroundColor Green
Write-Host "  python -m app.main_grpc_report" -ForegroundColor Yellow
