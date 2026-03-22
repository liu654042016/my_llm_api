from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse

from src.core.router import Router, RouterError
from src.core.health import HealthChecker
from src.core.logging import RequestLogger
from src.schemas.requests import ChatCompletionRequest


router = APIRouter()

# Global router instance (initialized in main.py)
_router: Router | None = None
_health_checker: HealthChecker | None = None


def set_router(r: Router) -> None:
    global _router
    _router = r


def set_health_checker(h: HealthChecker) -> None:
    global _health_checker
    _health_checker = h


@router.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> Response:
    """OpenAI-compatible chat completions endpoint."""
    if _router is None:
        raise HTTPException(status_code=500, detail="Router not initialized")
    messages = [msg.dict() for msg in request.messages]
    try:
        response = await _router.route(
            messages=messages,
            model=request.model,
            stream=request.stream,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop,
        )

        if request.stream:
            return StreamingResponse(
                response.aiter_bytes(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
            )
        else:
            return Response(content=response.content, media_type="application/json")
    except RouterError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/health")
async def health() -> dict[str, Any]:
    """Health endpoint."""
    if _health_checker is None:
        return {"status": "ok", "adapters": []}
    statuses = await _health_checker.check_all()
    return {
        "status": "ok" if all(s.healthy for s in statuses) else "degraded",
        "adapters": [
            {
                "name": s.adapter_name,
                "healthy": s.healthy,
                "latency_ms": s.latency_ms,
                "error": s.error,
            }
            for s in statuses
        ],
    }
