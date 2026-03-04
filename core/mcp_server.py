"""
mcp_server.py — FastAPI server providing an OpenAI-compatible API.
Exposes local Ollama models and remote providers as a unified API.
"""
from __future__ import annotations

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.model_service import router as model_router
from models.chat_session import ChatTurn

app = FastAPI(title="Orchestrator MCP Server")

# ── Models ────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096
    stream: Optional[bool] = False

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/v1/models")
async def list_models():
    models = model_router.all_model_names()
    return {
        "object": "list",
        "data": [{"id": m, "object": "model", "created": 1234567, "owned_by": "orchestrator"} for m in models]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    if not request.stream:
        # Synchronous completion (collect tokens)
        content = ""
        try:
            for token in model_router.resolve_stream(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                content += token
            
            return {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1234567,
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop"
                }]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Streaming completion
    async def event_generator():
        try:
            for token in model_router.resolve_stream(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                yield f"data: {{\"choices\":[{{\"delta\":{{\"content\":\"{token}\"}},\"index\":0,\"finish_reason\":null}}]}}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

def run_server(host: str = "127.0.0.1", port: int = 8080):
    uvicorn.run(app, host=host, port=port)
