from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field


class ContentPart(BaseModel, extra="ignore"):
    type: str = "text"
    text: Optional[str] = None


class Message(BaseModel, extra="ignore"):
    role: str = Field(..., description="Role: system, user, assistant, or developer")
    content: Union[str, List[ContentPart]] = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel, extra="ignore"):
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
