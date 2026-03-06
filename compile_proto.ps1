# Proto 컴파일 스크립트 (Windows PowerShell)
# Usage: .\compile_proto.ps1

Write-Host "Compiling proto file..." -ForegroundColor Green

python -m grpc_tools.protoc `
  -I.\proto `
  --python_out=.\app\grpc_generated `
  --grpc_python_out=.\app\grpc_generated `
  .\proto\chat_service.proto

if ($LASTEXITCODE -eq 0) {
    Write-Host "Proto compilation successful!" -ForegroundColor Green
    Write-Host "Generated files:" -ForegroundColor Cyan
    Get-ChildItem .\app\grpc_generated\*.py | ForEach-Object { Write-Host "  - $($_.Name)" }
} else {
    Write-Host "Proto compilation failed!" -ForegroundColor Red
    exit 1
}
