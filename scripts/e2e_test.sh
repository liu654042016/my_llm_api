#!/usr/bin/env bash
set -euo pipefail

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

echo "[TEST] Starting uvicorn server..."
uvicorn src.api.main:app --host "$HOST" --port "$PORT" > /tmp/uvicorn.log 2>&1 &
SERVER_PID=$!

echo "[TEST] Waiting for server to be ready..."
TIMEOUT=${TIMEOUT:-60}
START_TS=$(date +%s)
while true; do
  if curl -sSf http://$HOST:$PORT/health >/dev/null 2>&1; then
    echo "[TEST] Health endpoint OK."
    break
  fi
  sleep 2
  NOW_TS=$(date +%s)
  ELAPSED=$((NOW_TS-START_TS))
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "[TEST] Timeout waiting for health endpoint after ${TIMEOUT}s."
    break
  fi
fi

echo "[TEST] Running non-streaming chat completions test..."
START_CURL=$(date +%s%3N)
RESPONSE=$(curl -s -w "%{http_code}" -X POST http://$HOST:$PORT/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-5","messages": [{"role": "user", "content": "你好"}],"temperature": 1.0}')
# Separate body and status code
HTTP_CODE=${RESPONSE: -3}
BODY=${RESPONSE:0: -3}
echo "$BODY" | tee /tmp/e2e_response.json
END_CURL=$(date +%s%3N)
LATENCY=$((END_CURL-START_CURL))

echo "[TEST] Chat test HTTP code: $HTTP_CODE, latency: ${LATENCY}ms"

echo "[TEST] Running health check..."
curl -s http://$HOST:$PORT/health | tee /tmp/health.txt

echo "[TEST] Cleaning up server..."
kill "$SERVER_PID" || true
wait "$SERVER_PID" 2>/dev/null || true

echo "[TEST] Done. See /tmp/e2e_response.json and /tmp/health.txt for details."
