from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Protocol, Callable, Tuple, Type, ClassVar
import time
import subprocess
import shlex
import itertools
import threading
from .argument import Argument
import ast

# ---------- BASE Action ----------

_OP_REGISTRY: Dict[str, Type["BaseAction"]] = {}

def register(action_type: str):
    def deco(cls):
        _OP_REGISTRY[action_type] = cls
        return cls
    return deco


EXECUTABLE_ACTIONS = {
    "SingleClickAction",
    "DoubleClickAction",
    "TripleClickAction",
    "RightClickAction",
    "MoveAction",
    "DragAction",
    "ScrollAction",
    "TypeAction",
    "PressKeyAction",
    "KeyDownAction",
    "KeyUpAction",
    "HotKeyAction",
    "ScreenshotAction",
    "CopyAction",
    "PasteAction",
    "SwitchWindowAction",
    "WaitAction",
    "FinishAction",
    "ErrorEnvAction",
    "CallUserAction",
    "PassAction",
}


COMMON_EXECUTABLE_ACTIONS = {
    "SingleClickAction",
    "DoubleClickAction",
    "RightClickAction",
    "MoveAction",
    "DragAction", 
    "TripleClickAction",
    "ScrollAction",
    "TypeAction",
    "PressKeyAction",
    "HotKeyAction",
    "CopyAction",
    "PasteAction",
    "SwitchWindowAction",
    "WaitAction",
    # "ScreenUnderstandingAction"
}


class BaseAction(ABC):
    type: str = "base"

    def __init__(self, **kwargs: Any):
        # per-subclass counter → readable ids like open_windows_menu_1, click_3, ...
        cls = self.__class__
        if not hasattr(cls, "_counter"):
            cls._counter = itertools.count(1)  # type: ignore[attr-defined]
        n = next(cls._counter)  # type: ignore[attr-defined]
        self.id: str = f"{self.type}_{n}"

        for k, v in kwargs.items():
            # 1) If an instance attribute already exists and is Argument → update it
            inst_arg = self.__dict__.get(k, None)
            if isinstance(inst_arg, Argument):
                inst_arg.value = v
                continue

            # 2) If there is a class-level default Argument → clone it into the instance
            class_attr = getattr(self.__class__, k, None)
            if isinstance(class_attr, Argument):
                # define a small clone helper if Argument doesn't have one
                cloned = Argument(
                    value=v,
                    description=getattr(class_attr, "description", None),
                )
                setattr(self, k, cloned)
                continue

            # 3) Otherwise, just set the attribute directly
            if k not in {"type", "id", "name"}:
                setattr(self, k, Argument(value=v))
            else:
                setattr(self, k, v)

        if not hasattr(self, "name"):
            self.name = self.id

    @property
    def arguments_str(self) -> str:
        """Short title for graph visualization."""
        if not self.arguments:
            return self.type
        return ", ".join(f"{k}: {v}" for k, v in self.arguments.items())

    @property
    def arguments(self) -> Dict[str, Any]:
        """
        Return only the attributes that were provided through **kwargs
        when the action was constructed.
        """
        reserved = {"type", "id", "name"}
        return {k: v for k, v in vars(self).items() if isinstance(v, Argument) and not k.startswith("_") and k not in reserved}

    @arguments.setter
    def arguments(self, value: Dict[str, Any]):
        for k, v in value.items():
            setattr(self, k, v)

    def get_gui_code(self) -> str:
        """Return an executable GUI code snippet (Python) reflecting this op."""
        pass

    # ---- Factory helpers ----
    @staticmethod
    def from_action(action_type: str, **kwargs: Any) -> "BaseAction":
        cls = _OP_REGISTRY.get(action_type, UnknownAction)
        return cls(**kwargs)

    @staticmethod
    def from_json(step: Dict[str, Any]) -> "BaseAction":
        IGNORED_FIELDS = {""}
        action_type = step.get("primitive_operation", "unknown")
        kwargs = {k: v for k, v in step.items() if k not in IGNORED_FIELDS | {"primitive_operation"}}
        # extract parmaeters from arguments field if exists
        if "arguments" in kwargs and isinstance(kwargs["arguments"], dict):
            arguments = kwargs.pop("arguments")
            kwargs.update(arguments)
        return BaseAction.from_action(
            action_type=action_type,
            **kwargs
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, type={self.type}, arguments={self.arguments})"
    
    def process_listlike_str(self, value):
        if isinstance(value, str):
            value = value.strip()
            if "[" in value and "]" in value:
                # Remove brackets and parse as comma-separated values
                content = value.strip("[]")
                if content:
                    try:
                        parsed = ast.literal_eval(value)
                        if isinstance(parsed, list):
                            return parsed
                        else:
                            return [parsed] if parsed else []
                    except:
                        return [key.strip() for key in content.split(",") if key.strip()]
                else:
                    return []
            elif "+" in value:
                return [key.strip() for key in value.split("+")]
            else:
                # Single key without brackets
                return [value] if value else []
        elif isinstance(value, list):
            return value
        return value

    def configure_from_env(self, env = None):
        """Configure the action based on the environment {env}."""
        pass


@register("SingleClickAction")
class SingleClickAction(BaseAction):
    type: str = "click"
    coordinate: Argument = Argument(
        value=None,
        description="The (x, y) coordinate to click on the screen."
    )
    button: Argument = Argument(
        value="left",
        description="The mouse button to click (left, right, middle)."
    )
    modifiers: Argument = Argument(
        value=None,
        description="Any keyboard modifiers to hold while clicking."
    )

    def __init__(self, thought: str = "", coordinate: Tuple[float, float] = None, button: str = "left", modifiers: str = None, **kwargs):
        super().__init__(thought=thought, coordinate=coordinate, button=button, modifiers=modifiers, **kwargs)

    def get_gui_code(self) -> str:
        x, y = self.coordinate.value if self.coordinate.value else (None, None)
        btn = self.button.value
        mods = self.process_listlike_str(self.modifiers.value)
        return (
            "import pyautogui\n"
                f"{'for m in ' + repr(mods) + ': pyautogui.keyDown(m)' if mods else ''}\n"
            f"pyautogui.click({repr(x)}, {repr(y)}, button={repr(btn)})\n"
                f"{'for m in ' + repr(list(reversed(mods))) + ': pyautogui.keyUp(m)' if mods else ''}\n"
        )

    @property
    def require_grounding(self) -> bool:
        return self.coordinate.value is None

    def call_grounding_model(
        self,
        grounding_expertise: None,
        observation: Any):
        refined_coordinate = grounding_expertise.predict(
            action_description=self.thought,
            observation=observation
        )
        self.coordinate.value = refined_coordinate


@register("DoubleClickAction")
class DoubleClickAction(BaseAction):
    type: str = "double_click"
    coordinate: Argument = Argument(
        value=None,
        description="The (x, y) coordinate to double-click on the screen."
    )
    button: Argument = Argument(
        value="left",
        description="The mouse button to double-click (left, right, middle)."
    )

    def __init__(self, thought: str = "", coordinate: Tuple[float, float] = None, button: str = "left", **kwargs):
        super().__init__(thought=thought, coordinate=coordinate, button=button, **kwargs)

    def get_gui_code(self) -> str:
        x, y = self.coordinate.value if self.coordinate.value else (None, None)
        btn = self.button.value
        return (
            "\nimport pyautogui"
            f"\npyautogui.doubleClick({repr(x)}, {repr(y)}, button={repr(btn)})"
        )

    @property
    def require_grounding(self) -> bool:
        return self.coordinate.value is None

    def call_grounding_model(
        self,
        grounding_expertise: None,
        observation: Any):
        refined_coordinate = grounding_expertise.predict(
            action_description=self.thought,
            observation=observation
        )
        self.coordinate.value = refined_coordinate

@register("TripleClickAction")
class TripleClickAction(BaseAction):
    type: str = "triple_click"
    coordinate: Argument = Argument(
        value=None,
        description="The (x, y) coordinate to triple-click on the screen."
    )
    button: Argument = Argument(
        value="left",
        description="The mouse button to triple-click (left, right, middle)."
    )

    def __init__(self, thought: str = "", coordinate: Tuple[float, float] = None, button: str = "left", **kwargs):
        super().__init__(thought=thought, coordinate=coordinate, button=button, **kwargs)

    def get_gui_code(self) -> str:
        x, y = self.coordinate.value if self.coordinate.value else (None, None)
        btn = self.button.value
        return (
            "\nimport pyautogui"
            f"\npyautogui.tripleClick({repr(x)}, {repr(y)}, button={repr(btn)})"
        )

    @property
    def require_grounding(self) -> bool:
        return self.coordinate.value is None

    def call_grounding_model(
        self,
        grounding_expertise: None,
        observation: Any):
        refined_coordinate = grounding_expertise.predict(
            action_description=self.thought,
            observation=observation
        )
        self.coordinate.value = refined_coordinate


@register("RightClickAction")
class RightClickAction(BaseAction):
    type: str = "right_click"
    coordinate: Argument = Argument(
        value=None,
        description="The (x, y) coordinate to right-click on the screen."
    )

    def __init__(self, thought: str = "", coordinate: Tuple[float, float] = None, **kwargs):
        super().__init__(thought=thought, coordinate=coordinate, **kwargs)

    def get_gui_code(self) -> str:
        x, y = self.coordinate.value if self.coordinate.value else (None, None)
        return (
            "\nimport pyautogui"
            f"\npyautogui.click({repr(x)}, {repr(y)}, button='right')"
        )

    @property
    def require_grounding(self) -> bool:
        return self.coordinate.value is None

    def call_grounding_model(
        self,
        grounding_expertise: None,
        observation: Any):
        refined_coordinate = grounding_expertise.predict(
            action_description=self.thought,
            observation=observation
        )
        self.coordinate.value = refined_coordinate


@register("MoveAction")
class MoveAction(BaseAction):
    type: str = "move_abs"
    coordinate: Argument = Argument(
        value=None,
        description="The (x, y) coordinate to move the mouse."
    )
    duration: Argument = Argument(
        value=0.0,
        description="Seconds to move the mouse."
    )
    
    def __init__(self, thought: str = "", coordinate: Tuple[float, float] = None, duration: float = 0.0, **kwargs):
        super().__init__(thought=thought, coordinate=coordinate, duration=duration, **kwargs)

    def get_gui_code(self) -> str:
        x, y = self.coordinate.value if self.coordinate.value else (None, None)
        d = self.duration.value
        return (
            "\nimport pyautogui"
            f"\npyautogui.moveTo({x}, {y}, duration={d})"
        )

    @property
    def require_grounding(self) -> bool:
        return self.coordinate.value is None

    def call_grounding_model(
        self,
        grounding_expertise: None,
        observation: Any):
        refined_coordinate = grounding_expertise.predict(
            action_description=self.thought,
            observation=observation
        )
        self.coordinate.value = refined_coordinate


@register("DragAction")
class DragAction(BaseAction):
    type: str = "drag"
    start_coordinate: Argument = Argument(
        value=None,
        description="The (x, y) coordinate to start dragging from."
    )
    end_coordinate: Argument = Argument(
        value=None,
        description="The (x, y) coordinate to drag to."
    )
    duration: Argument = Argument(
        value=2.0,
        description="Seconds to drag the mouse."
    )
    thought_for_start_coordinate = Argument(
        value="",
        description="The thought or description for the start coordinate."
    )
    thought_for_end_coordinate = Argument(
        value="",
        description="The thought or description for the end coordinate."
    )

    def __init__(self, thought: str = "", start_coordinate: Tuple[float, float] = None, end_coordinate: Tuple[float, float] = None, duration: float = 2.0, **kwargs):
        super().__init__(thought=thought, start_coordinate=start_coordinate, end_coordinate=end_coordinate, duration=duration, **kwargs)

    def get_gui_code(self) -> str:
        x1, y1 = self.start_coordinate.value if self.start_coordinate.value else (None, None)
        x2, y2 = self.end_coordinate.value if self.end_coordinate.value else (None, None)
        d = self.duration.value
        return (
            "\nimport pyautogui"
            f"\npyautogui.moveTo({x1}, {y1})"
            f"\npyautogui.mouseDown()"
            f"\npyautogui.dragTo({x2}, {y2}, duration={d}, button='left')"
            f"\npyautogui.mouseUp()"
        )

    @property
    def require_grounding(self) -> bool:
        return self.start_coordinate.value is None or self.end_coordinate.value is None

    def call_grounding_model(
        self,
        grounding_expertise: None,
        observation: Any):
        refined_start_coordinate = grounding_expertise.predict(
            action_description=self.thought_for_start_coordinate.value,
            observation=observation
        )
        self.start_coordinate.value = refined_start_coordinate

        refined_end_coordinate = grounding_expertise.predict(
            action_description=self.thought_for_end_coordinate.value,
            observation=observation
        )
        self.end_coordinate.value = refined_end_coordinate


@register("ScrollAction")
class ScrollAction(BaseAction):
    type: str = "scroll"
    dx: Argument = Argument(
        value=0,
        description="Horizontal scroll amount."
    )
    dy: Argument = Argument(
        value=0,
        description="Vertical scroll amount."
    )
    direction: Argument = Argument(
        value="up",
        description="Scroll direction (up, down, left, right)."
    )

    def __init__(self, thought: str = "", dx: int = 0, dy: int = 0, direction: str = "up", **kwargs):
        super().__init__(thought=thought, dx=dx, dy=dy, direction=direction, **kwargs)

    def get_gui_code(self) -> str:
        if isinstance(self.dx.value, str):
            self.dx.value = int(self.dx.value)
        if isinstance(self.dy.value, str):
            self.dy.value = int(self.dy.value)
        dx = abs(self.dx.value)
        dy = abs(self.dy.value)
        direction = self.direction.value
        if "up" in direction:
            return (
                "\nimport pyautogui"
                f"\npyautogui.scroll({dy})\n"
            )
        elif "down" in direction:
            return (
                "\nimport pyautogui"
                f"\npyautogui.scroll(-{dy})\n"
            )
        elif "left" in direction:
            return (
                "\nimport pyautogui"
                f"\npyautogui.hscroll(-{dx})\n"
            )
        elif "right" in direction:
            return (
                "\nimport pyautogui"
                f"\npyautogui.hscroll({dx})\n"
            )


@register("TypeAction")
class TypeAction(BaseAction):
    type: str = "type"
    input_mode: Argument = Argument(
        value="keyboard",
        description="Input mode (keyboard or copy_paste)."
    )
    text: Argument = Argument(
        value="",
        description="Text to type."
    )
    end_with_enter: Argument = Argument(
        value=True,
        description="Whether to end with Enter key."
    )
    line_by_line: Argument = Argument(
        value=True,
        description="Whether to type each line separately (adds Enter between lines)."
    )
    

    def __init__(self, thought: str = "", input_mode: str = "keyboard", text: str = "", end_with_enter: bool = True, line_by_line: bool = True, **kwargs):
        super().__init__(
            thought=thought,
            input_mode=input_mode,
            text=text,
            end_with_enter=end_with_enter,
            line_by_line=line_by_line,
            **kwargs
        )

    def get_gui_code(self) -> str:
        text = self.text.value

        # Fast path: type or paste the full text without adding per-line Enters.
        if not self.line_by_line.value:
            pyautogui_code = "import pyautogui"
            pyautogui_code += "\nimport pyperclip"
            pyautogui_code += f"\npyperclip.copy({repr(text)})"
            pyautogui_code += "\npyautogui.hotkey('ctrl', 'v')"
            if self.end_with_enter.value:
                pyautogui_code += "\npyautogui.press('enter')"
            return pyautogui_code

        lines = text.split("\n")
        pyautogui_code = "import pyautogui"
        for i, line in enumerate(lines):
            line = line.strip()
            if self.input_mode.value == "keyboard":
                pyautogui_code += f"\npyautogui.write({repr(line)}, interval=0.05)"
            elif self.input_mode.value == "copy_paste":
                """Use clipboard paste to input text (faster, more reliable for long text)."""
                pyautogui_code += "\nimport pyperclip"
                pyautogui_code += f"\npyperclip.copy({repr(line)})"
                pyautogui_code += "\npyautogui.hotkey('ctrl', 'v')"
            if i < len(lines) - 1 and self.end_with_enter.value:
                pyautogui_code += "\npyautogui.press('enter')"

        return pyautogui_code


@register("PressKeyAction")
class PressKeyAction(BaseAction):
    type: str = "press_key"
    key: Argument = Argument(
        value=None,
        description="The key to press."
    )
    presses: Argument = Argument(
        value=1,
        description="Number of times to press the key."
    )
    interval: Argument = Argument(
        value=0.0,
        description="Seconds between key presses."
    )

    def __init__(self, thought: str = "", key: str = "", presses: int = 1, interval: float = 0.1, **kwargs):
        super().__init__(thought=thought, key=key, presses=presses, interval=interval, **kwargs)

    def get_gui_code(self) -> str:
        key = self.key.value
        presses = self.presses.value if self.presses.value else 1
        interval = self.interval.value if self.interval.value else 0.1
        return (
            "\nimport pyautogui"
            f"\npyautogui.press({repr(key)}, presses={presses}, interval={interval})"
        )


@register("KeyDownAction")
class KeyDownAction(BaseAction):
    type: str = "key_down"
    key: Argument = Argument(value=None, description="The key to hold down.")

    def __init__(self, thought: str = "", key: str = "", **kwargs):
        super().__init__(thought=thought, key=key, **kwargs)

    def get_gui_code(self) -> str:
        key = self.key.value
        return (
           "\nimport pyautogui"
           f"\npyautogui.keyDown({repr(key)})"
        )


@register("KeyUpAction")
class KeyUpAction(BaseAction):
    type: str = "key_up"
    key: Argument = Argument(value=None, description="The key to release.")

    def __init__(self, thought: str = "", key: str = "", **kwargs):
        super().__init__(thought=thought, key=key, **kwargs)

    def get_gui_code(self) -> str:
        key = self.key.value
        return (
            "\nimport pyautogui"
            f"\npyautogui.keyUp({repr(key)})"
        )


@register("HotKeyAction")
class HotKeyAction(BaseAction):
    type: str = "hot_key"
    keys: Argument = Argument(
        value=None,
        description="The keys to press together. It must be a list of strings. Do not use '+' to join keys."
    )

    def __init__(self, thought: str = "", keys: Optional[list[str]] = None, **kwargs):
        super().__init__(thought=thought, keys=keys, **kwargs)


    def get_gui_code(self) -> str:
        key_content = self.process_listlike_str(self.keys.value)
        return (
            "\nimport pyautogui"
            f"\npyautogui.hotkey({', '.join([repr(k) for k in key_content])})"
        )


@register("ScreenshotAction")
class ScreenshotAction(BaseAction):
    type: str = "screenshot"

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        path = self.arguments.get("path", "screenshot.png")
        return (
            "\nimport pyautogui"
            f"\npyautogui.screenshot({repr(path)})\n"
        )


@register("CopyAction")
class CopyAction(BaseAction):
    type: str = "copy"

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        return "import pyautogui\npyautogui.hotkey('ctrl','c')\n"


@register("PasteAction")
class PasteAction(BaseAction):
    type: str = "paste"

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        return "import pyautogui\npyautogui.hotkey('ctrl','v')\n"


@register("SwitchWindowAction")
class SwitchWindowAction(BaseAction):
    type: str = "switch_window"
    direction: Argument = Argument(
        value="next",
        description="Direction to switch window (next or prev)."
    )

    def __init__(self, thought: str = "", direction: str = "next", **kwargs):
        super().__init__(thought=thought, direction=direction, **kwargs)

    def get_gui_code(self) -> str:
        direction = self.direction.value
        if direction == "prev":
            return "import pyautogui\npyautogui.hotkey('alt','shift','tab')\n"
        return "import pyautogui\npyautogui.hotkey('alt','tab')\n"


@register("WaitAction")
class WaitAction(BaseAction):
    type: str = "wait"
    duration: Argument = Argument(
        value=0.5,
        description="Seconds to wait."
    )

    def __init__(self, thought: str = "", duration: float = 0.5, **kwargs):
        super().__init__(thought=thought, duration=duration, **kwargs)

    def get_gui_code(self) -> str:
        return "import time\n" f"time.sleep({self.duration.value})\n"


@register("FinishAction")
class FinishAction(BaseAction):
    type: str = "finish"

    def get_gui_code(self) -> str:
        return "# FINISH: no-op marker\n"


@register("ErrorEnvAction")
class ErrorEnvAction(BaseAction):
    type: str = "error_env"

    def get_gui_code(self) -> str:
        return "# Meet Some Env Error\n"


@register("CallUserAction")
class CallUserAction(BaseAction):
    type: str = "call_user"

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        return "print('[CALL_USER] Awaiting user input/approval to continue.')\n"


@register("PassAction")
class PassAction(BaseAction):
    type: str = "pass"

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        return "# PASS: no-op\n"

@register("ScreenUnderstandingAction")
class ScreenUnderstandingAction(BaseAction):
    type: str = "screen_understanding"
    descriptions: List[str] = [
        "Analyze and understand the current screen content to answer questions or extract information"
    ]

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        return "print('[SCREEN_UNDERSTANDING] Analyzing screen content.')\n"


@register("UnknownAction")
class UnknownAction(BaseAction):
    type: str = "unknown"

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        return "raise NotImplementedError('Unknown action')\n"


@register("DummyAction")
class DummyAction(BaseAction):
    type: str = "dummy_action"
    name: str = "dummy_action"

    def __init__(self, thought: str = "", **kwargs):
        super().__init__(thought=thought, **kwargs)

    def get_gui_code(self) -> str:
        return "# For placeholder purposes\n"