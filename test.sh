#!/bin/bash
# Script de prueba para endpoints de Super Agente Financiero API
# Ejecutar con: bash test.sh o ./test.sh

BASE_URL="http://localhost:8000"

echo "========================================"
echo "  Super Agente Financiero API - Tests"
echo "========================================"

echo ""
echo "[1/5] Health Check..."
curl -s "$BASE_URL/health" | python -m json.tool 2>/dev/null || curl -s "$BASE_URL/health"

echo ""
echo "[2/5] Root Endpoint..."
curl -s "$BASE_URL/" | python -m json.tool 2>/dev/null || curl -s "$BASE_URL/"

echo ""
echo "[3/5] Single Ticker (AAPL)..."
curl -s "$BASE_URL/api/v1/dividends?ticker=AAPL" | python -m json.tool 2>/dev/null || curl -s "$BASE_URL/api/v1/dividends?ticker=AAPL"

echo ""
echo "[4/5] Multiple Tickers (AAPL, TSLA, ECOPETROL)..."
curl -s "$BASE_URL/api/v1/dividends?tickers=AAPL,TSLA,ECOPETROL" | python -m json.tool 2>/dev/null || curl -s "$BASE_URL/api/v1/dividends?tickers=AAPL,TSLA,ECOPETROL"

echo ""
echo "[5/5] Colombian Ticker (ECOPETROL)..."
curl -s "$BASE_URL/api/v1/dividends?ticker=ECOPETROL" | python -m json.tool 2>/dev/null || curl -s "$BASE_URL/api/v1/dividends?ticker=ECOPETROL"

echo ""
echo "========================================"
echo "  Tests Completados"
echo "========================================"


