from typing import Literal
from pydantic import Field
from ._base import BaseLogMessage
import rich
from rich.text import Text
from rich.panel import Panel

class LogMessage(BaseLogMessage):
    # type: Literal["log"] = "log"
    type: str = Field(default="log", description="Type of the message")
    message: str

    def to_console(self) -> str:
        text = f"[[bold green]{self.level}[/bold green]] [[bold green]{self.source}[/bold green]] {self.message}"
        if self.console_panel_title:
            return Panel(text, title=self.console_panel_title)
        else:
            return text


class TaskAndPlanMessage(BaseLogMessage):
    type: Literal["task_and_plan"] = "task_and_plan"
    task: str
    plan: str

    def to_console(self) -> str:
        # return f"[[bold green]{self.level}[/bold green]] [[bold green]{self.source}[/bold green]] {self.task}\n{self.plan}"

        text = Text()
        text.append(f"Task: {self.task}\n", style="green")
        text.append(f"Plan:\n", style="white")
        text.append(f"{self.plan}", style="cyan")

        return Panel(text, title="Task and Plan")
