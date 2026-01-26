from typing import Literal, Optional, List
from ._base import BaseLogMessage

class PromptAndResponseMessage(BaseLogMessage):
    type: Literal["prompt_and_response"] = "prompt_and_response"
    prompt: str
    response: str
    images: Optional[List[str]] = None