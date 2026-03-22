from typing import List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str = Field(..., description="Model name")
    messages: List[Message] = Field(..., description="Chat messages")
    stream: bool = Field(default=False, description="Stream responses")
    temperature: Optional[float] = Field(default=0.9, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2, le=2)
    presence_penalty: Optional[float] = Field(default=None, ge=-2, le=2)
    stop: Optional[List[str]] = Field(default=None)
