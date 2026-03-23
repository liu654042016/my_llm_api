from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from src.core.router import Router, RouterError
from src.core.health import HealthChecker
from src.core.logging import RequestLogger
from src.schemas.requests import ChatCompletionRequest


logger = logging.getLogger(__name__)


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


@router.api_route("/v1/chat/completions", methods=["POST"])
async def chat_completions_raw(request: Request) -> Response:
    body = await request.body()
    try:
        import json
        data = json.loads(body)
        body_model = ChatCompletionRequest(**data)
    except Exception as e:
        logger.info(f"VALIDATION ERROR: {e}")
        return Response(content=str(e), status_code=422, media_type="text/plain")
    
    if _router is None:
        raise HTTPException(status_code=500, detail="Router not initialized")
    
    messages = []
    for msg in body_model.messages:
        content = msg.content
        if isinstance(content, list):
            text_parts = [p.text for p in content if hasattr(p, 'text') and p.text]
            content = " ".join(text_parts) if text_parts else ""
        messages.append({"role": msg.role, "content": content})
    
    response = await _router.route(
        messages=messages,
        model=body_model.model,
        stream=body_model.stream,
        temperature=body_model.temperature,
        max_tokens=body_model.max_tokens,
        top_p=body_model.top_p,
        frequency_penalty=body_model.frequency_penalty,
        presence_penalty=body_model.presence_penalty,
        stop=body_model.stop,
    )

    if body_model.stream:
        return StreamingResponse(
            response.aiter_bytes(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    else:
        return Response(content=response.content, media_type="application/json")
    try:
        response = await _router.route(
            messages=messages,
            model=body.model,
            stream=body.stream,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            top_p=body.top_p,
            frequency_penalty=body.frequency_penalty,
            presence_penalty=body.presence_penalty,
            stop=body.stop,
        )

        if body.stream:
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
