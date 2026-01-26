from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from typing import Literal
from .LoggerMessages import BaseLogMessage
from dataclasses import asdict
import json

@dataclass
class ExecutionResult:
    success: bool
    message: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    children: List['ExecutionResult'] = field(default_factory=list)
    context: Optional[str] = None

    # Optional dictionary to store structured metadata for this execution step.
    # This can include timing, IDs, config values, debug info, etc.
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def add_child(self, child: 'ExecutionResult'):
        self.children.append(child)
        if not child.success:
            self.success = False
            self.errors.extend(child.errors)

    def as_dict(self):
        return asdict(self)
    
    def as_message(self):
        return ExecutionResultMessage(execution_result=self, display_console=False)


class ExecutionResultMessage(BaseLogMessage):
    type: Literal["execution_result"] = "execution_result"
    execution_result: ExecutionResult

    class Config:       # allow to use non-pydantic types in the class
        arbitrary_types_allowed = True    

    def to_json(self) -> str:
        return json.dumps(self.execution_result.as_dict())
        
    def to_console(self) -> str:
        return self.to_json()
        