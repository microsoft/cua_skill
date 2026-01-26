# vs_code_actions.py

from typing import Any, Dict, List, Optional
from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, RightClickAction, ScrollAction
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

# ---------- Core app control ----------


class VSCodeBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="vs_code",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Visual Studio Code",
        description="The name of the Visual Studio Code application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register("VSCodeLaunch")
class VSCodeLaunch(VSCodeBaseAction, LaunchApplication):
    type: str = "vscode_launch"
    # Windows-friendly: Win+R → "code" → Enter
    descriptions: List[str] = [
        "Open Visual Studio Code.",
        "Launch VS Code.",
        "Start Visual Studio Code.",
        "Open the VS Code app.",
        "Run VS Code."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)
        


@register("VSCodeOpenFile")
class VSCodeOpenFile(VSCodeBaseAction):
    type: str = "vscode_open_file"
    file_path: Argument = Argument(
        value="agent/action/chrome_actions.py",
        description="Absolute or relative path of the file to open."
    )

    descriptions: List[str] = [
        "Open file ${{file_path}}.",
        "Load file ${{file_path}} in VS Code.",
        "Open the file at ${{file_path}}.",
        "Open ${{file_path}} in the editor.",
        "Open ${{file_path}}."
    ]

    def __init__(self, file_path: str = "agent/action/chrome_actions.py", **kwargs) -> None:
        super().__init__(file_path=file_path, **kwargs)
        self.add_path("open_file", path=[
            HotKeyAction(keys=["Ctrl", "o"], thought="Open 'Open File' dialog"),
            WaitAction(duration=1.0),
            TypeAction(text=file_path, input_mode="copy_paste", thought="Enter file path"),
            HotKeyAction(keys=["Enter"], thought="Confirm open"),
            WaitAction(duration=1.0)
        ])


@register("VSCodeOpenFolder")
class VSCodeOpenFolder(VSCodeBaseAction):
    type: str = "vscode_open_folder"
    folder_path: Argument = Argument(
        value=".",
        description="Absolute or relative path of the folder to open."
    )

    descriptions: List[str] = [
        "Open folder ${{folder_path}} in VS Code.",
        "Open the workspace folder ${{folder_path}}.",
        "Load folder ${{folder_path}}.",
        "Open directory ${{folder_path}}.",
        "Open ${{folder_path}} folder."
    ]

    def __init__(self, folder_path: str = ".", **kwargs) -> None:
        super().__init__(folder_path=folder_path, **kwargs)
        self.add_path("open_folder", path=[
            # VS Code uses a key chord for 'Open Folder': Ctrl+K, then Ctrl+O
            HotKeyAction(keys=["Ctrl", "k", "o"], thought="Start 'Open Folder' chord"),
            WaitAction(duration=1.0),
            TypeAction(text=folder_path, input_mode="copy_paste", thought="Enter folder path"),
            WaitAction(duration=1.0),
            HotKeyAction(keys=["Enter"], thought="Confirm open"),
            WaitAction(duration=1.0),
            HotKeyAction(keys=["Enter"], thought="Confirm open"),
            WaitAction(duration=1.0)
        ])


@register("VSCodeNewUntitledFile")
class VSCodeNewUntitledFile(BaseComposeAction):
    type: str = "vscode_new_untitled"
    descriptions: List[str] = [
        "Create a new untitled file.",
        "Start a new file.",
        "Open a new empty file.",
        "Create a blank file.",
        "New untitled file."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("new_file", path=[
            HotKeyAction(keys=["Ctrl", "n"], thought="New untitled file"),
            WaitAction(duration=1.0)
        ])


@register("VSCodeSaveAs")
class VSCodeSaveAs(BaseComposeAction):
    type: str = "vscode_save_as"
    file_path: Argument = Argument(
        value="quick_notes.md",
        description="Full path (including filename) to save the current file as."
    )

    descriptions: List[str] = [
        "Save current file as ${{file_path}}.",
        "Save as ${{file_path}}.",
        "Save editor to ${{file_path}}.",
        "Save the file to ${{file_path}}.",
        "Export file as ${{file_path}}."
    ]

    def __init__(self, file_path: str = "quick_notes.md", **kwargs) -> None:
        super().__init__(file_path=file_path, **kwargs)
        self.add_path("save_as", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "s"], thought="Open Save As dialog"),
            WaitAction(duration=1.0),
            TypeAction(text=file_path, input_mode="copy_paste", thought="Enter full save path"),
            HotKeyAction(keys=["Enter"], thought="Save"),
            WaitAction(duration=1.0)
        ])


# ---------- Command Palette helpers ----------

@register("VSCodeRunCommand")
class VSCodeRunCommand(BaseComposeAction):
    type: str = "vscode_run_command"
    command_text: Argument = Argument(
        value="Format Document",
        description="Exact text of the command to run from the Command Palette."
    )

    descriptions: List[str] = [
        "Run command ${{command_text}}.",
        "Execute ${{command_text}} from Command Palette.",
        "Use command: ${{command_text}}.",
        "Run VS Code command ${{command_text}}.",
        "Execute command ${{command_text}}."
    ]

    def __init__(self, command_text: str = "Format Document", **kwargs) -> None:
        super().__init__(command_text=command_text, **kwargs)
        self.add_path("run_cmd", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=1.0),
            TypeAction(text=command_text, input_mode="copy_paste", thought=f"Search command '{command_text}'"),
            HotKeyAction(keys=["Enter"], thought="Execute command"),
            WaitAction(duration=1.0)
        ])


# ---------- Editing & find/replace ----------

@register("VSCodeFindReplaceInActiveFile")
class VSCodeFindReplaceInActiveFile(BaseComposeAction):
    type: str = "vscode_find_replace_active_file"
    find_text: Argument = Argument(
        value="foo",
        description="Text to search for within the active editor."
    )
    replace_text: Argument = Argument(
        value="bar",
        description="Replacement text for each match."
    )

    descriptions: List[str] = [
        "Replace all ${{find_text}} with ${{replace_text}} in the active file.",
        "Find ${{find_text}} and replace with ${{replace_text}}.",
        "Replace ${{find_text}} using ${{replace_text}} across the file.",
        "Replace occurrences of ${{find_text}} with ${{replace_text}}.",
        "Perform replace all: ${{find_text}} -> ${{replace_text}}."
    ]

    def __init__(self, find_text: str = "foo", replace_text: str = "bar", **kwargs) -> None:
        super().__init__(find_text=find_text, replace_text=replace_text, **kwargs)
        self.add_path("replace_all", path=[
            HotKeyAction(keys=["Ctrl", "h"], thought="Open Replace UI"),
            WaitAction(duration=1.0),
            TypeAction(text=find_text, input_mode="copy_paste", thought="Type find text"),
            HotKeyAction(keys=["Tab"], thought="Move to Replace input"),
            TypeAction(text=replace_text, input_mode="copy_paste", thought="Type replace text"),
            WaitAction(duration=1.0),
            HotKeyAction(keys=["Ctrl", "Alt", "Enter"], thought="Run Replace All"),
            WaitAction(duration=1.0)
        ])


@register("VSCodeIndentLineRange")
class VSCodeIndentLineRange(BaseComposeAction):
    type: str = "vscode_indent_range"
    start_line: Argument = Argument(
        value=1,
        description="First line number in the range to indent."
    )
    end_line: Argument = Argument(
        value=3,
        description="Last line number in the range to indent."
    )
    indent_count: Argument = Argument(
        value=1,
        description="Number of tab indents to apply to the selected range."
    )

    descriptions: List[str] = [
        "Indent lines ${{start_line}} to ${{end_line}} by ${{indent_count}} tab(s).",
        "Increase indent of lines ${{start_line}}-${{end_line}} by ${{indent_count}}.",
        "Indent selection from line ${{start_line}} to ${{end_line}} ${{indent_count}} tab(s).",
        "Add ${{indent_count}} tab(s) to lines ${{start_line}} through ${{end_line}}.",
        "Indent the specified line range."
    ]

    def __init__(self, start_line: int = 1, end_line: int = 3, indent_count: int = 1, **kwargs) -> None:
        super().__init__(start_line=start_line, end_line=end_line, indent_count=indent_count, **kwargs)
        selects = [
            HotKeyAction(keys=["Ctrl", "g"], thought="Go to line"),
            TypeAction(text=str(start_line), input_mode="copy_paste", thought="Enter start line"),
            HotKeyAction(keys=["Enter"], thought="Move cursor"),
            WaitAction(duration=0.2),
        ]
        # Select down to end_line
        for _ in range(max(0, end_line - start_line + 1)):
            selects += [HotKeyAction(keys=["Shift", "Down"], thought="Extend selection")]
        # Indent N times
        for _ in range(max(1, indent_count)):
            selects += [HotKeyAction(keys=["Tab"], thought="Indent selection")]
        self.add_path("indent", path=selects + [WaitAction(duration=1.0)])


# ---------- Settings (UI-first) ----------

@register("VSCodeOpenSettingsUI")
class VSCodeOpenSettingsUI(BaseComposeAction):
    type: str = "vscode_open_settings_ui"
    descriptions: List[str] = [
        "Open Settings.",
        "Open Settings UI.",
        "Show settings.",
        "Open preferences.",
        "Open configuration settings."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("open_settings", path=[
            HotKeyAction(keys=["Ctrl", ","], thought="Open Settings UI"),
            WaitAction(duration=1.0),
        ])


# ---------- New primitives implemented ----------

@register("VSCodeFormatDocument")
class VSCodeFormatDocument(BaseComposeAction):
    type: str = "vscode_format_document"
    descriptions: List[str] = [
        "Format the current document.",
        "Format document.",
        "Apply formatting to the active file.",
        "Reformat the open file.",
        "Format the file in the editor."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("format_document", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Format Document", input_mode="copy_paste", thought="Search 'Format Document'"),
            HotKeyAction(keys=["Enter"], thought="Execute format"),
            WaitAction(duration=1.0),
        ])


@register("VSCodeToggleWordWrap")
class VSCodeToggleWordWrap(BaseComposeAction):
    type: str = "vscode_toggle_word_wrap"
    descriptions: List[str] = [
        "Toggle word wrap.",
        "Enable/disable word wrap.",
        "Switch word wrap.",
        "Toggle wrapping of long lines.",
        "Toggle the editor word wrap."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("toggle_word_wrap", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Toggle Word Wrap", input_mode="copy_paste", thought="Search 'Toggle Word Wrap'"),
            HotKeyAction(keys=["Enter"], thought="Toggle word wrap"),
            WaitAction(duration=0.5),
        ])


@register("VSCodeToggleLineComment")
class VSCodeToggleLineComment(BaseComposeAction):
    type: str = "vscode_toggle_line_comment"
    descriptions: List[str] = [
        "Toggle line comment.",
        "Comment/uncomment the current line.",
        "Toggle comment on the selected line(s).",
        "Add or remove line comment.",
        "Toggle line commenting."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("toggle_line_comment", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Toggle Line Comment", input_mode="copy_paste", thought="Search 'Toggle Line Comment'"),
            HotKeyAction(keys=["Enter"], thought="Toggle line comment"),
            WaitAction(duration=0.5),
        ])


@register("VSCodeCreateIntegratedTerminal")
class VSCodeCreateIntegratedTerminal(BaseComposeAction):
    type: str = "vscode_create_integrated_terminal"
    descriptions: List[str] = [
        "Create a new integrated terminal.",
        "Open a new terminal in VS Code.",
        "Start a new integrated terminal.",
        "Create terminal.",
        "New integrated terminal."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("create_terminal", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Terminal: Create New Integrated Terminal", input_mode="copy_paste", thought="Search terminal creation command"),
            HotKeyAction(keys=["Enter"], thought="Create new integrated terminal"),
            WaitAction(duration=1.0),
        ])


@register("VSCodeToggleTerminal")
class VSCodeToggleTerminal(BaseComposeAction):
    type: str = "vscode_toggle_terminal"
    descriptions: List[str] = [
        "Toggle the terminal panel.",
        "Show/hide the terminal.",
        "Toggle terminal visibility.",
        "Open or close the terminal.",
        "Toggle the integrated terminal."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("toggle_terminal", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="View: Toggle Terminal", input_mode="copy_paste", thought="Search 'Toggle Terminal'"),
            HotKeyAction(keys=["Enter"], thought="Toggle terminal"),
            WaitAction(duration=0.5),
        ])


@register("VSCodeOpenUserSettingsJSON")
class VSCodeOpenUserSettingsJSON(BaseComposeAction):
    type: str = "vscode_open_user_settings_json"
    descriptions: List[str] = [
        "Open User Settings (JSON).",
        "Open user settings JSON.",
        "Open the user settings file (JSON).",
        "Show user settings JSON.",
        "Open user settings JSON."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("open_user_settings_json", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Preferences: Open User Settings (JSON)", input_mode="copy_paste", thought="Search user settings JSON"),
            HotKeyAction(keys=["Enter"], thought="Open user settings.json"),
            WaitAction(duration=1.0),
        ])


@register("VSCodeOpenDefaultSettingsJSON")
class VSCodeOpenDefaultSettingsJSON(BaseComposeAction):
    type: str = "vscode_open_default_settings_json"
    descriptions: List[str] = [
        "Open Default Settings (JSON).",
        "Open default settings JSON.",
        "Open the default settings file (JSON).",
        "Show default settings JSON.",
        "Open default settings JSON."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("open_default_settings_json", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Preferences: Open Default Settings (JSON)", input_mode="copy_paste", thought="Search default settings JSON"),
            HotKeyAction(keys=["Enter"], thought="Open default settings.json"),
            WaitAction(duration=1.0),
        ])


@register("VSCodeUpdateSettingsJSON")
class VSCodeUpdateSettingsJSON(BaseComposeAction):
    type: str = "vscode_update_settings_json"
    settings_content: Argument = Argument(
        value='{\n    "editor.fontSize": 14\n}',
        description="The JSON content to set in the settings file."
    )

    descriptions: List[str] = [
        "After opening user settings JSON, update vscode settings with provided content.",
        "After opening user settings JSON, set user settings JSON to specified content.",
        "After opening user settings JSON, replace user settings.json with new content.",
        "After opening user settings JSON, update the user settings file (JSON).",
        "After opening user settings JSON, modify user settings JSON."
    ]

    def __init__(self, settings_content: str = "", **kwargs) -> None:
        super().__init__(settings_content=settings_content, **kwargs)
        self.add_path("update_settings_json", path=[
            HotKeyAction(keys=["Ctrl", "a"], thought="Select all content in settings.json"),
            WaitAction(duration=0.5),
            HotKeyAction(keys=["Backspace"], thought="Delete existing content"),
            TypeAction(text=settings_content, input_mode="copy_paste", thought="Update settings content", line_by_line=False),
            WaitAction(duration=0.5),
            HotKeyAction(keys=["Ctrl", "s"], thought="Save settings.json"),
            WaitAction(duration=0.5),
        ])


@register("VSCodeOpenKeyboardShortcuts")
class VSCodeOpenKeyboardShortcuts(BaseComposeAction):
    type: str = "vscode_open_keyboard_shortcuts"
    descriptions: List[str] = [
        "Open Keyboard Shortcuts.",
        "Show keyboard shortcuts.",
        "Open the keybindings editor.",
        "Open shortcuts settings.",
        "Open keyboard mappings."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("open_keyboard_shortcuts_hotkey", path=[
            HotKeyAction(keys=["Ctrl", "k", "s"], thought="Open Keyboard Shortcuts"),
            WaitAction(duration=1.0),
        ])

@register("VSCodeOpenDefaultKeyboardShortcuts")
class VSCodeOpenDefaultKeyboardShortcuts(BaseComposeAction):
    type: str = "vscode_open_default_keyboard_shortcuts"
    descriptions: List[str] = [
        "Open Default Keyboard Shortcuts.",
        "Show default keyboard shortcuts.",
        "Open the default keybindings editor.",
        "Open default shortcuts settings.",
        "Open default keyboard mappings."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("open_default_keyboard_shortcuts", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Preferences: Open Default Keyboard Shortcuts", input_mode="copy_paste", thought="Search default keyboard shortcuts"),
            HotKeyAction(keys=["Enter"], thought="Open default keyboard shortcuts"),
            WaitAction(duration=1.0),
        ])

@register("VSCodeGoToFile")
class VSCodeGoToFile(BaseComposeAction):
    type: str = "vscode_go_to_file"
    file_path: Argument = Argument(
        value="README.md",
        description="Path or filename to open via Quick Open."
    )
    descriptions: List[str] = [
        "Quick open file ${{file_path}}.",
        "Go to file ${{file_path}}.",
        "Open quickly the file ${{file_path}}.",
        "Search and open file ${{file_path}}.",
        "Use quick open to open ${{file_path}}."
    ]

    def __init__(self, file_path: str = "README.md", **kwargs) -> None:
        super().__init__(file_path=file_path, **kwargs)
        self.add_path("quick_open_file", path=[
            HotKeyAction(keys=["Ctrl", "p"], thought="Open Quick Open"),
            WaitAction(duration=0.5),
            TypeAction(text=file_path, input_mode="copy_paste", thought="Type file path to open"),
            HotKeyAction(keys=["Enter"], thought="Open selected file"),
            WaitAction(duration=0.8),
        ])


@register("VSCodeReloadWindow")
class VSCodeReloadWindow(BaseComposeAction):
    type: str = "vscode_reload_window"
    descriptions: List[str] = [
        "Reload VS Code window.",
        "Reload the current window.",
        "Restart the VS Code window.",
        "Reload editor window.",
        "Reload the workspace window."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("reload_window", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "p"], thought="Open Command Palette"),
            WaitAction(duration=0.5),
            TypeAction(text="Reload Window", input_mode="copy_paste", thought="Search 'Reload Window'"),
            HotKeyAction(keys=["Enter"], thought="Reload VS Code window"),
            WaitAction(duration=1.5),
        ])


@register("VSCodeOpenExtensionsView")
class VSCodeOpenExtensionsView(BaseComposeAction):
    type: str = "vscode_open_extensions_view"
    descriptions: List[str] = [
        "Open Extensions view.",
        "Show extensions.",
        "Open the extensions sidebar.",
        "Open extensions marketplace.",
        "View installed extensions."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path("open_extensions", path=[
            HotKeyAction(keys=["Ctrl", "Shift", "x"], thought="Open Extensions view"),
            WaitAction(duration=1.0),
        ])


@register("VSCodeGoToLine")
class VSCodeGoToLine(BaseComposeAction):
    type: str = "vscode_go_to_line"
    line_number: Argument = Argument(
        value=1,
        description="Line number to navigate to within the active editor."
    )
    descriptions: List[str] = [
        "Go to line ${{line_number}}.",
        "Jump to line ${{line_number}}.",
        "Navigate to line ${{line_number}}.",
        "Move cursor to line ${{line_number}}.",
        "Go to line number ${{line_number}}."
    ]

    def __init__(self, line_number: int = 1, **kwargs) -> None:
        super().__init__(line_number=line_number, **kwargs)
        self.add_path("go_to_line", path=[
            HotKeyAction(keys=["Ctrl", "g"], thought="Open Go to Line"),
            WaitAction(duration=0.2),
            TypeAction(text=str(line_number), input_mode="copy_paste", thought="Enter target line number"),
            HotKeyAction(keys=["Enter"], thought="Jump to line"),
            WaitAction(duration=0.5),
        ])
