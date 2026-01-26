
from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, DummyAction, SingleClickAction, HotKeyAction, WaitAction, TypeAction, PressKeyAction, KeyDownAction, KeyUpAction
from .argument import Argument

@register("OpenWindowsMenu")
class OpenWindowsMenu(BaseComposeAction):
    type: str = "open_windows_menu"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "click_start",
            path=[
                SingleClickAction(thought="Click the Windows Start button. It is the Windows logo icon (four white squares) located at the bottom center of the taskbar. Do not click the widgets icon on the left."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_win",
            path=[
                HotKeyAction(keys=["win"], thought="Press the Windows key on the keyboard to open the Start menu."), 
                WaitAction(duration=1.0)
            ]
        )


@register("OpenSearchBar")
class OpenSearchBar(BaseComposeAction):
    type: str = "open_search_bar"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "click_search_bar",
            path=[
                SingleClickAction(thought="Click the Windows Search bar"),
                WaitAction(duration=1.0)
            ]
        )

@register("OpenRun")
class OpenRun(BaseComposeAction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_win_r",
            path=[
                HotKeyAction(keys=["win", "r"], thought="Press the Windows + R keys on the keyboard to open the Run dialog."),
                WaitAction(duration=1.0)
            ]
        )


@register("LaunchApplication")
class LaunchApplication(BaseComposeAction):
    type: str = "launch_application"
    application_name: Argument = Argument(
        value="application_name",
        description="Name of the application to launch."
    )

    def __init__(self, application_name: str = "application_name", **kwargs) -> None:
        super().__init__(application_name=application_name, **kwargs)
        self.add_path(
            "click_app_icon",
            path=[
                OpenWindowsMenu(),
                WaitAction(duration=1.0),
                TypeAction(text=self.application_name, thought=f"Type the application name '{self.application_name}' to search for it."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on the icon for '{self.application_name}' to launch it."),
            ]
        )


@register("MaximizeActiveWindow")
class MaximizeActiveWindow(BaseComposeAction):
    type: str = "maximize_active_window"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "keyboard_maximize_active_window",
            path=[
                KeyDownAction(key="alt"),
                PressKeyAction(key="space"),
                KeyUpAction(key="alt"),
                PressKeyAction(key="x"),
            ]
        )



@register("SwitchtoFocusApp")
class SwitchtoFocusApp(BaseComposeAction):
    type: str = "switch_to_focus_app"
    application_name: Argument = Argument(
        value="application_name",
        description="Name of the application to switch to."
    )
    descriptions: List[str] = ["Switch to the application window (that is already launched) with the given name."]

    def __init__(self, application_name: str = "application_name", **kwargs) -> None:
        super().__init__(application_name=application_name, **kwargs)
        self.add_path(
            "select_app_focus",
            path=[
                HotKeyAction(keys=["win", "tab"]),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on '{self.application_name}' to switch to it. If there are multiple windows for this application, click on the most recent one."),
            ]
        )




if __name__ == "__main__":
    open_windows_menu_op = OpenWindowsMenu()

    launch_app_op = LaunchApplication()

    # IMPORTANT: pass filename and directory separately to avoid PermissionError
    dot = open_windows_menu_op.build_dot(vertical=True)
    dot.render(
        filename="open_windows_menu",  # base filename (no extension)
        directory=R"./",  # output directory
        format="png",
        view=False,
        cleanup=True,
    )

    dot = launch_app_op.build_dot(vertical=True)
    dot.render(
        filename="launch_app",
        directory=R"./",
        format="png",
        view=False,
        cleanup=True,
    )

