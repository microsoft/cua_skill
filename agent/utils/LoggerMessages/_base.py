import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from rich.panel import Panel

LogLevel = Literal["debug", "info", "warning", "error", "critical"]

LOG_LEVEL_VALUES = {
    "debug": 10,
    "info": 20,
    "warning": 30,
    "error": 40,
    "critical": 50
}

EXCLUDED_FIELDS = {"display_console", "save_to_disk", "console_panel_title"}

class BaseLogMessage(BaseModel):
    type: str = Field(..., description="Type of the message")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    level: LogLevel = "info"
    source: str = "system"
    display_console: bool = Field(default=True, serialization_exclude=True)
    save_to_disk: bool = Field(default=True, serialization_exclude=True)
    console_panel_title: Optional[str] = Field(default=None, serialization_exclude=True)  # used to display the console output as a panel with this title
    metadata: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return self.model_dump_json(exclude=EXCLUDED_FIELDS, exclude_none=True)
        
    def to_console(self) -> str:
        if self.console_panel_title:
            return Panel(self.to_json(), title=self.console_panel_title)
        else:
            return self.to_json()
