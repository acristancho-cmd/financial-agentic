# Script de prueba para endpoints de Super Agente Financiero API
# Ejecutar con: .\test.ps1

$baseUrl = "http://localhost:8000"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Super Agente Financiero API - Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[1/5] Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✓ Health Check OK" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}

Write-Host "`n[2/5] Root Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "✓ Root Endpoint OK" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}

Write-Host "`n[3/5] Single Ticker (AAPL)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/dividends?ticker=AAPL" -Method Get
    Write-Host "✓ Single Ticker OK" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}

Write-Host "`n[4/5] Multiple Tickers (AAPL, TSLA, ECOPETROL)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/dividends?tickers=AAPL,TSLA,ECOPETROL" -Method Get
    Write-Host "✓ Multiple Tickers OK" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}

Write-Host "`n[5/5] Colombian Ticker (ECOPETROL)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/dividends?ticker=ECOPETROL" -Method Get
    Write-Host "✓ Colombian Ticker OK" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Tests Completados" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan


