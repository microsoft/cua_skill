from typing import Any, Dict, List

from .common_action import LaunchApplication

from .compose_action import BaseComposeAction
from .base_action import register, SingleClickAction, WaitAction, TypeAction, HotKeyAction
from .argument import Argument

__all__ = []

class NotepadBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="notepad",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Notepad",
        description="The name of the Notepad application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("NotepadLaunch")
class NotepadLaunch(NotepadBaseAction, LaunchApplication):
    # Canonical identifiers
    type: str = "notepad_launch"
    
    # Schema payload
    descriptions: List[str] = [
        "Launch Notepad.",
        "Open Notepad application.",
        "Start Notepad program.",
        "Run Notepad app.",
        "Open Notepad."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)


@register("NotepadCreateNewFile")
class NotepadCreateNewFile(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_create_new_file"
    
    # Schema payload
    descriptions: List[str] = [
        "Open a new file.",
        "Start a new document.",
        "Create a fresh file.",
        "Make a blank file.",
        "New file."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_create_new_file_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "n"], thought="Use Ctrl+N to create new file"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_create_new_file_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open File menu with Alt+F"),
                WaitAction(duration=0.5),
                TypeAction(text="n", thought="Press N to create a new file"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_create_new_file_tab",
            path=[
                SingleClickAction(thought="Click the add new tab button to create a new file"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_create_new_file_menu",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the New option"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadExitApp")
class NotepadExitApp(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_exit_app"
    
    # Schema payload
    descriptions: List[str] = [
        "Exit notepad.",
        "Close notepad.",
        "Quit notepad.",
        "Leave notepad.",
        "End notepad."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_exit_hotkey",
            path=[
                HotKeyAction(keys=["alt", "f4"], thought="Use Alt+F4 to exit Notepad"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_exit_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open File menu with Alt+F"),
                WaitAction(duration=0.5),
                TypeAction(text="x", thought="Press X to exit Notepad"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_exit",
            path=[
                SingleClickAction(thought="Click the close button to exit Notepad"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadFindReplaceAll")
class NotepadFindReplaceAll(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_find_replace_all"
    find_what: Argument = Argument(
        value="hello",
        description="The text string to search for and replace in the document. Can be any text string including words, phrases, or special characters. Case-sensitive by default in Windows Notepad. Examples: 'hello' (single word), 'Hello World' (phrase with spaces), 'old_name' (with underscore), '123' (numbers). Use this to identify all occurrences of specific text that needs to be changed. The text must exist in the document to be replaced."
    )
    replace_with: Argument = Argument(
        value="hi",
        description="The new text string that will replace all occurrences of find_what. Can be any text string including words, phrases, special characters, or even an empty string (to delete the found text). Examples: 'hi' (replacement word), 'Greetings' (different phrase), 'new_name' (with underscore), '' (empty string to remove text). The replacement will be applied to all matching occurrences in the entire document when using Replace All function."
    )

    # Schema payload
    descriptions: List[str] = [
        "Replace `${{find_what}}` with `${{replace_with}}`.",
        "Swap all `${{find_what}}` to `${{replace_with}}`.",
        "Change every `${{find_what}}` to `${{replace_with}}`.",
        "Do a replace: `${{find_what}}` → `${{replace_with}}`.",
        "Replace all of `${{find_what}}` with `${{replace_with}}`."
    ]

    def __init__(self, find_what: str = "hello", replace_with: str = "hi", **kwargs) -> None:
        super().__init__(find_what=find_what, replace_with=replace_with, **kwargs)
        self.add_path(
            "notepad_find_replace_all_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "h"], thought="Open Replace dialog with Ctrl+H"),
                WaitAction(duration=1.0),
                TypeAction(text=find_what, input_mode="copy_paste", thought=f"Enter text to find: '{find_what}'"),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["tab"], thought="Move to replace field"),
                WaitAction(duration=0.5),
                TypeAction(text=replace_with, input_mode="copy_paste", thought=f"Enter replacement text: '{replace_with}'"),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["alt", "a"], thought="Click Replace All button"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_find_replace_all",
            path=[
                HotKeyAction(keys=["alt", "e"], thought="Open Edit menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Replace option"),
                WaitAction(duration=1.0),
                TypeAction(text=find_what, input_mode="copy_paste", thought=f"Enter text to find: '{find_what}'"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the replace input field"),
                WaitAction(duration=0.5),
                TypeAction(text=replace_with, input_mode="copy_paste", thought=f"Enter replacement text: '{replace_with}'"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Replace All button"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadFindText")
class NotepadFindText(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_find_text"
    query: Argument = Argument(
        value="hello",
        description="The text string to search for in the document. Can be any text including single words, phrases with spaces, numbers, or special characters. Case-sensitive by default in Windows Notepad. Examples: 'hello' (single word), 'Hello World' (phrase with spaces), 'function_name' (with underscore), 'TODO' (common code marker), '2023' (year/number). The search will find and highlight the next occurrence of this text in the document starting from the current cursor position. If not found, Notepad will show a message indicating the text was not found."
    )

    # Schema payload
    descriptions: List[str] = [
        "Find `${{query}}`.",
        "Search for `${{query}}`.",
        "Look for `${{query}}`.",
        "Locate `${{query}}`.",
        "Search `${{query}}`."
    ]

    def __init__(self, query: str = "hello", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        # Get actual value from Argument if needed
        query_value = self.query.value if hasattr(self.query, 'value') else self.query
        self.add_path(
            "notepad_find_text_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "f"], thought="Open Find dialog with Ctrl+F"),
                WaitAction(duration=1.0),
                TypeAction(text=query_value, input_mode="copy_paste", thought=f"Enter search query: '{query_value}'"),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["enter"], thought="Press Enter to find next"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_find_text",
            path=[
                SingleClickAction(thought="Click the Edit menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Find option"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the find input field"),
                WaitAction(duration=0.5),
                TypeAction(text=query_value, input_mode="copy_paste", thought=f"Enter search query: '{query_value}'"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Find Next button"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadGoToLine")
class NotepadGoToLine(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_go_to_line"
    line_num: Argument = Argument(
        value=1,
        description="The line number to jump to in the document. Must be a positive integer starting from 1 (first line). The value should be within the valid range of the document's total line count. Examples: 1 (first line, beginning of document), 10 (tenth line), 100 (hundredth line), 500 (line 500). If the specified line number exceeds the total number of lines in the document, the cursor will move to the last line. Use this to quickly navigate to specific locations in large text files, especially useful for debugging code or reviewing specific sections referenced by line numbers."
    )

    # Schema payload
    descriptions: List[str] = [
        "Jump to line `${{line_num}}`.",
        "Go to line `${{line_num}}`.",
        "Move to line `${{line_num}}`.",
        "Navigate to line `${{line_num}}`.",
        "Line `${{line_num}}`, please."
    ]

    def __init__(self, line_num: int = 1, **kwargs) -> None:
        super().__init__(line_num=line_num, **kwargs)
        # Get actual value from Argument if needed
        line_num_value = self.line_num.value if hasattr(self.line_num, 'value') else self.line_num
        self.add_path(
            "notepad_go_to_line_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "g"], thought="Open Go To Line dialog with Ctrl+G"),
                WaitAction(duration=1.0),
                TypeAction(text=str(line_num_value), input_mode="copy_paste", thought=f"Enter line number: {line_num_value}"),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["enter"], thought="Press Enter to go to line"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_go_to_line",
            path=[
                SingleClickAction(thought="Click the Edit menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Go To option"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the line number input field"),
                WaitAction(duration=0.5),
                TypeAction(text=str(line_num_value), input_mode="copy_paste", thought=f"Enter line number: {line_num_value}"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Go To button"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadInsertDateTime")
class NotepadInsertDateTime(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_insert_datetime"
    
    # Schema payload
    descriptions: List[str] = [
        "Insert current date/time.",
        "Insert timestamp.",
        "Insert datetime.",
        "Insert date.",
        "Insert time."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_insert_datetime_hotkey",
            path=[
                HotKeyAction(keys=["f5"], thought="Insert current date and time with F5"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_insert_datetime_menu",
            path=[
                HotKeyAction(keys=["alt", "e"], thought="Open Edit menu with Alt+E"),
                WaitAction(duration=0.5),
                TypeAction(text="d", thought="Press D to insert date/time"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_insert_datetime",
            path=[
                SingleClickAction(thought="Click the Edit menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Date/Time option"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadPrintFile")
class NotepadPrintFile(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_print_file"
    
    # Schema payload
    descriptions: List[str] = [
        "Print the document.",
        "Send to printer.",
        "Print this file.",
        "Print now.",
        "Print."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_print_file_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "p"], thought="Open Print dialog with Ctrl+P"),
                WaitAction(duration=2.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to print with default settings"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_print_file_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open File menu with Alt+F"),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["p"], thought="Press P to print"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_print_file",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Print option"),
                WaitAction(duration=1.0)
            ]
        )

@register("NotepadSaveAsFile")
class NotepadSaveAsFile(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_save_as_file"
    path: Argument = Argument(
        value="C:\\Users\\Docker\\Documents",
        description="Full absolute directory path where the file will be saved. Must be a valid Windows directory path with drive letter. Use double backslashes (\\\\) for Windows paths. Examples: 'C:\\\\Users\\\\Docker\\\\Documents' (user documents folder), 'D:\\\\Work\\\\Projects' (custom work directory), 'C:\\\\Temp' (temporary folder). The directory must exist or be accessible. Common locations: Documents folder, Desktop, specific project folders. If the directory doesn't exist, the save operation will fail."
    )
    file_name: Argument = Argument(
        value="document.txt",
        description="Name of the file to save, including the file extension. Common extensions: .txt (plain text, default), .md (Markdown), .log (log files), .csv (comma-separated values), .json (JSON data), .xml (XML data), .html (HTML files), .css (CSS files), .js (JavaScript), .py (Python), .java (Java), .cpp (C++), .bat (batch files), .ps1 (PowerShell scripts). Examples: 'document.txt', 'notes.md', 'data.csv', 'readme.txt', 'script.bat'. The filename should not contain invalid characters: \\ / : * ? \" < > |"
    )

    # Schema payload
    descriptions: List[str] = [
        "Save as `${{file_name}}` located in `${{path}}`.",
        "Store a copy `${{file_name}}` to `${{path}}`.",
        "Use Save As and name it `${{file_name}}` in `${{path}}`.",
        "Save this file as `${{file_name}}` to `${{path}}`.",
        "Create a new file `${{file_name}}` at `${{path}}`."
    ]

    def __init__(self, path: str = "C:\\Users\\Docker\\Documents", file_name: str = "document.txt", **kwargs) -> None:
        super().__init__(path=path, file_name=file_name, **kwargs)
        self.add_path(
            "notepad_save_as_file_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "s"], thought="Open Save As dialog"),
                WaitAction(duration=2.0),
                TypeAction(text=file_name, input_mode="copy_paste", thought=f"Enter file name: '{file_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Save As dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=0.5),
                TypeAction(text=path, input_mode="copy_paste", thought=f"Enter file path: '{path}'"),
                WaitAction(duration=1.0),                
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),                
                SingleClickAction(thought="Click the Save button"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_save_as_file_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open File menu with Alt+F"),
                WaitAction(duration=0.5),
                TypeAction(text="a", thought="Press A to open Save As dialog"),
                WaitAction(duration=2.0),
                TypeAction(text=file_name, input_mode="copy_paste", thought=f"Enter file name: '{file_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Save As dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=0.5),
                TypeAction(text=path, input_mode="copy_paste", thought=f"Enter file path: '{path}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),                
                SingleClickAction(thought="Click the Save button"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_click_save_as_file",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=1),
                SingleClickAction(thought="Click the Save As option"),
                WaitAction(duration=1.0),
                TypeAction(text=file_name, input_mode="copy_paste", thought=f"Enter file name: '{file_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Save As dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=1.0),
                TypeAction(text=path, input_mode="copy_paste", thought=f"Enter file path: '{path}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),  
                SingleClickAction(thought="Click the Save button"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadSaveFile")
class NotepadSaveFile(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_save_file"
    
    # Schema payload
    descriptions: List[str] = [
        "Save the current file.",
        "Store your changes.",
        "Click save to keep edits.",
        "Save what's open now.",
        "Write changes to disk."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_save_file_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "s"], thought="Save current file with Ctrl+S"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_save_file_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open File menu with Alt+F"),
                WaitAction(duration=0.5),
                TypeAction(text="s", thought="Press S to save"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_save_file",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Save option"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadTypeText")
class NotepadTypeText(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_type_text"
    text: Argument = Argument(
        value="Hello, world!",
        description="The text content to type into the Notepad document. Can be any string including letters, numbers, spaces, punctuation, special characters, and line breaks. Supports Unicode characters. Examples: 'Hello, world!' (greeting with punctuation), 'This is a test.' (sentence), 'Line 1\\nLine 2' (multi-line with line break), '123 Main St.' (address with numbers), 'user@example.com' (email), 'TODO: Fix bug' (note with special formatting). The text will be inserted at the current cursor position. Can include markdown syntax if working in a markdown file."
    )

    # Schema payload
    descriptions: List[str] = [
        "Type: `${{text}}`.",
        "Write `${{text}}`.",
        "Enter `${{text}}`.",
        "Add `${{text}}` to the document.",
        "Insert `${{text}}` here."
    ]

    def __init__(self, text: str = "Hello, world!", **kwargs) -> None:
        super().__init__(text=text, **kwargs)
        self.add_path(
            "notepad_type_text",
            path=[
                TypeAction(text=text, input_mode="copy_paste", thought=f"Type text: '{text}'"),
                WaitAction(duration=0.5)
            ]
        )


@register("NotepadWordWrap")
class NotepadWordWrap(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_word_wrap"
    
    # Schema payload
    descriptions: List[str] = [
        "Toggle word wrap.",
        "Enable word wrap.",
        "Disable word wrap.",
        "Wrap text.",
        "Unwrap text."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_word_wrap_menu",
            path=[
                HotKeyAction(keys=["alt", "v"], thought="Open View menu with Alt+V"),
                WaitAction(duration=0.5),
                TypeAction(text="w", thought="Press W to toggle Word Wrap"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_word_wrap",
            path=[
                SingleClickAction(thought="Click the View menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Word Wrap option"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadZoomIn")
class NotepadZoomIn(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_zoom_in"
    times: Argument = Argument(
        value=1,
        description="Number of times to incrementally increase the zoom level. Must be a positive integer (1 or greater). Each increment increases the zoom by one step (typically 10% each time). Examples: 1 (zoom in once, increase by ~10%), 3 (zoom in three times, increase by ~30%), 5 (zoom in five times, increase by ~50%). Useful for making text more readable or focusing on details. Maximum zoom is typically 500% in Notepad. Use higher values to make text significantly larger for accessibility or presentation purposes."
    )

    # Schema payload
    descriptions: List[str] = [
        "Zoom in `${{times}}`×.",
        "Increase zoom `${{times}}`×.",
        "Make text bigger `${{times}}`×.",
        "Zoom closer `${{times}}`×.",
        "Enlarge `${{times}}`×."
    ]

    def __init__(self, times: int = 1, **kwargs) -> None:
        super().__init__(times=times, **kwargs)
        # Get actual value from Argument if needed
        times_value = self.times.value if hasattr(self.times, 'value') else self.times
        path_actions = []
        for _ in range(times_value):
            path_actions.extend([
                HotKeyAction(keys=["ctrl", "plus"], thought="Zoom in with Ctrl++"),
                WaitAction(duration=0.5)
            ])
        
        self.add_path(
            "notepad_zoom_in_hotkey",
            path=path_actions
        )
        
        click_actions = []
        for _ in range(times_value):
            click_actions.extend([
                SingleClickAction(thought="Click the View menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Zoom option"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Zoom In option"),
                WaitAction(duration=0.5)
            ])
        
        self.add_path(
            "notepad_click_zoom_in",
            path=click_actions
        )


@register("NotepadZoomOut")
class NotepadZoomOut(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_zoom_out"
    times: Argument = Argument(
        value=1,
        description="Number of times to incrementally decrease the zoom level. Must be a positive integer (1 or greater). Each decrement decreases the zoom by one step (typically 10% each time). Examples: 1 (zoom out once, decrease by ~10%), 3 (zoom out three times, decrease by ~30%), 5 (zoom out five times, decrease by ~50%). Useful for viewing more content on screen or getting an overview of the document. Minimum zoom is typically 10% in Notepad. Use higher values to fit more text on screen for document overview or to reduce text size."
    )

    # Schema payload
    descriptions: List[str] = [
        "Zoom out `${{times}}`×.",
        "Decrease zoom `${{times}}`×.",
        "Make text smaller `${{times}}`×.",
        "Zoom away `${{times}}`×.",
        "Reduce `${{times}}`×."
    ]

    def __init__(self, times: int = 1, **kwargs) -> None:
        super().__init__(times=times, **kwargs)
        # Get actual value from Argument if needed
        times_value = self.times.value if hasattr(self.times, 'value') else self.times
        path_actions = []
        for _ in range(times_value):
            path_actions.extend([
                HotKeyAction(keys=["ctrl", "minus"], thought="Zoom out with Ctrl+-"),
                WaitAction(duration=0.5)
            ])
        
        self.add_path(
            "notepad_zoom_out_hotkey",
            path=path_actions
        )
        
        click_actions = []
        for _ in range(times_value):
            click_actions.extend([
                SingleClickAction(thought="Click the View menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Zoom option"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Zoom Out option"),
                WaitAction(duration=0.5)
            ])
        
        self.add_path(
            "notepad_click_zoom_out",
            path=click_actions
        )


@register("NotepadZoomReset")
class NotepadZoomReset(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_zoom_reset"
    
    # Schema payload
    descriptions: List[str] = [
        "Reset zoom to default.",
        "Restore original zoom level.",
        "Return to normal zoom.",
        "Set zoom back to 100%.",
        "Default zoom level."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_zoom_reset_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "0"], thought="Reset zoom to default with Ctrl+0"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_zoom_reset",
            path=[
                SingleClickAction(thought="Click the View menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Zoom option"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Restore Default Zoom option"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadBoldMarkdown")
class NotepadBoldMarkdown(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_bold_markdown"
    text: Argument = Argument(
        value="Important",
        description="The text content to format as bold using Markdown syntax. Can be any string including words, phrases, or sentences. The text will be wrapped with double asterisks (**text**) or double underscores (__text__) to create bold formatting in Markdown. Examples: 'Important' (single word emphasis), 'Critical Information' (phrase), 'Warning: Do not delete' (sentence with punctuation). This is useful for emphasizing key points in Markdown documents (.md files). The bold formatting will be visible when the Markdown is rendered."
    )

    # Schema payload
    descriptions: List[str] = [
        "Bold `${{text}}`.",
        "Make `${{text}}` bold.",
        "Bold the text `${{text}}`.",
        "Apply bold to `${{text}}`.",
        "Strong `${{text}}`."
    ]

    def __init__(self, text: str = "Important", **kwargs) -> None:
        super().__init__(text=text, **kwargs)
        self.add_path(
            "notepad_bold_markdown_syntax",
            path=[
                TypeAction(text=f"**{text}**", input_mode="copy_paste", thought=f"Type bold markdown syntax: '**{text}**'"),
                WaitAction(duration=0.5)
            ]
        )


@register("NotepadClearFormatting")
class NotepadClearFormatting(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_clear_formatting"
    
    # Schema payload
    descriptions: List[str] = [
        "Clear formatting.",
        "Remove styles.",
        "Plain text now.",
        "Reset formatting.",
        "Strip formatting."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_clear_formatting_select_all",
            path=[
                HotKeyAction(keys=["ctrl", "space"], thought="Clear formatting with Ctrl+Space"),
                WaitAction(duration=0.5)
            ]
        )
        self.add_path(
            "notepad_clear_formatting_click",
            path=[
                SingleClickAction(thought="Click the clear formatting button"),
                WaitAction(duration=0.5)
            ]
        )


@register("NotepadCloseTab")
class NotepadCloseTab(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_close_tab"
    tab_name: Argument = Argument(
        value="Untitled",
        description="The name of the tab/document to close as displayed in the Notepad tab bar. Can be the filename (e.g., 'document.txt', 'notes.md') or the default name for unsaved files ('Untitled', 'Untitled-1', 'Untitled-2', etc.). Examples: 'Untitled' (new unsaved document), 'readme.txt' (saved text file), 'notes.md' (Markdown file), 'TODO.txt' (named text file). If the document has unsaved changes, Notepad will prompt to save before closing. Use this to close specific tabs in multi-tab Notepad sessions."
    )

    # Schema payload
    descriptions: List[str] = [
        "Close the tab ${{tab_name}}.",
        "Shut this ${{tab_name}} tab.",
        "Exit current tab.",
        "Close current tab.",
        "Close ${{tab_name}}.",
        "End ${{tab_name}}."
    ]

    def __init__(self, tab_name: str = "Untitled", **kwargs) -> None:
        super().__init__(tab_name=tab_name, **kwargs)
        self.add_path(
            "notepad_close_tab_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "w"], thought=f"Close tab '{tab_name}' with Ctrl+W"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_close_tab",
            path=[
                SingleClickAction(thought=f"Click the close button on tab '{tab_name}'"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadCloseWindow")
class NotepadCloseWindow(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_close_window"
    
    # Schema payload
    descriptions: List[str] = [
        "Close the window.",
        "Shut Notepad window.",
        "Exit current window.",
        "Close it.",
        "End window."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_close_window_hotkey",
            path=[
                HotKeyAction(keys=["alt", "f4"], thought="Close window with Alt+F4"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "notepad_click_close_window",
            path=[
                SingleClickAction(thought="Click the window close button"),
                WaitAction(duration=1.0)
            ]
        )


@register("NotepadCopilotRewrite")
class NotepadCopilotRewrite(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_copilot_rewrite"
    
    # Schema payload
    descriptions: List[str] = [
        "Let Copilot rewrite.",
        "Ask Copilot to rewrite.",
        "Rewrite with Copilot.",
        "Rephrase text via Copilot.",
        "Have Copilot rewrite."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_copilot_rewrite_select",
            path=[
                SingleClickAction(thought="Click on Copilot menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on Copilot rewrite option"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_copilot_rewrite_right_click",
            path=[
                SingleClickAction(button="right", thought="Right-click to open context menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on Copilot rewrite option"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadCopilotSummarize")
class NotepadCopilotSummarize(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_copilot_summarize"
    
    # Schema payload
    descriptions: List[str] = [
        "Let Copilot summarize.",
        "Ask Copilot to summarize.",
        "Summarize with Copilot.",
        "Make a summary via Copilot.",
        "Have Copilot summarize."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_copilot_summarize_select",
            path=[
                SingleClickAction(thought="Click on Copilot menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on Copilot summarize option"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_copilot_summarize_right_click",
            path=[
                SingleClickAction(button="right", thought="Right-click to open context menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on Copilot summarize option"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadCopilotWrite")
class NotepadCopilotWrite(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_copilot_write"
    
    # Schema payload
    descriptions: List[str] = [
        "Let Copilot write.",
        "Ask Copilot to write.",
        "Write with Copilot.",
        "Generate text via Copilot.",
        "Have Copilot write."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_copilot_write",
            path=[
                SingleClickAction(thought="Click on Copilot menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on Copilot write option"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_copilot_write_right_click",
            path=[
                SingleClickAction(button="right", thought="Right-click to open context menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on Copilot write option"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadInsertBulletedList")
class NotepadInsertBulletedList(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_insert_bulleted_list"
    items: Argument = Argument(
        value=["First item", "Second item", "Third item"],
        description="List of text items to insert as a bulleted list using Markdown syntax. Must be a list/array of strings. Each item will be formatted with a leading dash and space ('- item') according to Markdown bullet list syntax. Examples: ['First item', 'Second item', 'Third item'] (simple list), ['Buy groceries', 'Call doctor', 'Finish report'] (to-do items), ['Introduction', 'Methods', 'Results', 'Conclusion'] (document sections). Each item should be a single line of text. Use this for creating unordered lists in Markdown documents where item order doesn't matter. The list will be formatted with each item on a new line."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add bullets: `${{items}}`.",
        "Insert bullet list `${{items}}`.",
        "Bulleted list: `${{items}}`.",
        "List with bullets `${{items}}`.",
        "Bullets `${{items}}`."
    ]

    def __init__(self, items: List[str] = None, **kwargs) -> None:
        if items is None:
            items = ["First item", "Second item", "Third item"]
        super().__init__(items=items, **kwargs)
        
        # Get actual value from Argument if needed
        items_value = self.items.value if hasattr(self.items, 'value') else self.items
        
        # Build markdown syntax for bulleted list
        path_actions = []
        for i, item in enumerate(items_value):
            path_actions.append(
                TypeAction(text=f"- {item}", input_mode="copy_paste", thought=f"Type bullet item in markdown syntax: '- {item}'")
            )
            if i < len(items_value) - 1:
                path_actions.extend([
                    WaitAction(duration=0.3),
                    HotKeyAction(keys=["enter"], thought="Start new line for next bullet"),
                    WaitAction(duration=0.3)
                ])
            else:
                path_actions.append(WaitAction(duration=0.5))

        self.add_path(
            "notepad_insert_bulleted_list_syntax",
            path=path_actions
        )


@register("NotepadInsertHeading")
class NotepadInsertHeading(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_insert_heading"
    level: Argument = Argument(
        value=1,
        description="Heading level for Markdown formatting. Must be an integer from 1 to 6. Level 1 (#) is the largest/most important heading (typically for document title), level 6 (######) is the smallest/least important heading (for minor subsections). Examples: 1 (# Title - main document title, largest), 2 (## Section - major sections), 3 (### Subsection - subsections), 4 (#### Minor heading - minor subsections), 5 (##### Subheading - detailed subsections), 6 (###### Smallest heading - finest granularity). Use hierarchically: H1 for title, H2 for chapters, H3 for sections within chapters, etc. Common usage: 1-3 for most documents."
    )
    text: Argument = Argument(
        value="Introduction",
        description="The heading text content to display. Can be any string including letters, numbers, spaces, and punctuation. Should be concise and descriptive. Examples: 'Introduction' (document section), 'Chapter 1: Getting Started' (book chapter), 'API Reference' (technical documentation), 'Project Overview' (project docs), 'Quick Start Guide' (tutorial section), 'Installation Instructions' (setup section). Best practices: keep headings short (2-8 words), use title case, be descriptive. Avoid ending headings with periods."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add H`${{level}}` heading `${{text}}`.",
        "Insert heading `${{text}}`.",
        "Heading `${{text}}`, level `${{level}}`.",
        "Put heading `${{text}}`.",
        "New heading `${{text}}`."
    ]

    def __init__(self, level: int = 1, text: str = "Introduction", **kwargs) -> None:
        super().__init__(level=level, text=text, **kwargs)
        
        # Get actual values from Argument if needed
        level_value = self.level.value if hasattr(self.level, 'value') else self.level
        text_value = self.text.value if hasattr(self.text, 'value') else self.text
        
        # Generate markdown heading syntax with correct number of # symbols
        heading_prefix = "#" * level_value
        self.add_path(
            "notepad_insert_heading_syntax",
            path=[
                TypeAction(text=f"{heading_prefix} {text_value}", input_mode="copy_paste", thought=f"Type heading in markdown syntax: '{heading_prefix} {text_value}'"),
                WaitAction(duration=0.5)
            ]
        )


@register("NotepadInsertLinkMarkdown")
class NotepadInsertLinkMarkdown(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_insert_link_markdown"
    text: Argument = Argument(
        value="Click here",
        description="The visible link text (anchor text) that will be displayed and clickable in the rendered Markdown. Can be any descriptive string. Examples: 'Click here' (call to action), 'Read more' (continuation link), 'Official documentation' (documentation link), 'GitHub repository' (code repository), 'Download now' (download link), 'Learn more about Python' (descriptive link). Best practices: use descriptive text that indicates where the link leads, avoid generic text like 'click here', make it clear what users will find when clicking."
    )
    url: Argument = Argument(
        value="https://example.com",
        description="The full URL (web address) that the link will point to. Must be a valid URL with protocol. Supported protocols: https:// (secure web, preferred), http:// (web), ftp:// (file transfer), mailto: (email). Examples: 'https://example.com' (website), 'https://github.com/user/repo' (GitHub), 'https://docs.python.org/3/' (documentation), 'mailto:user@example.com' (email link), 'https://example.com/page.html#section' (specific section). Use absolute URLs for external links. Internal anchors can use '#section' format."
    )

    # Schema payload
    descriptions: List[str] = [
        "Link `${{text}}` to `${{url}}`.",
        "Add link `${{text}}` → `${{url}}`.",
        "Insert link `${{text}}` with URL `${{url}}`.",
        "Hyperlink `${{text}}` with URL `${{url}}`.",
        "URL for `${{text}}` is `${{url}}`."
    ]

    def __init__(self, text: str = "Click here", url: str = "https://example.com", **kwargs) -> None:
        super().__init__(text=text, url=url, **kwargs)
                
        self.add_path(
            "notepad_insert_link_markdown_syntax",
            path=[
                TypeAction(text=f"[{text}]({url})", input_mode="copy_paste", thought=f"Type link in markdown syntax: '[{text}]({url})'"),
                WaitAction(duration=0.5)
            ]
        )


@register("NotepadInsertNumberedList")
class NotepadInsertNumberedList(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_insert_numbered_list"
    items: Argument = Argument(
        value=["First step", "Second step", "Third step"],
        description="List of text items to insert as a numbered/ordered list using Markdown syntax. Must be a list/array of strings. Each item will be formatted with a number, period, and space ('1. item', '2. item', etc.) according to Markdown ordered list syntax. Examples: ['First step', 'Second step', 'Third step'] (sequential steps), ['Open the application', 'Click Settings', 'Enable the feature'] (instructions), ['Gather ingredients', 'Preheat oven', 'Mix ingredients', 'Bake for 30 minutes'] (recipe steps). Use this for creating ordered lists in Markdown documents where sequence/order matters. Each item should be a single line of text. The numbers will auto-increment starting from 1."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add numbers: `${{items}}`.",
        "Numbered list `${{items}}`.",
        "List with numbers `${{items}}`.",
        "Insert numbered list `${{items}}`.",
        "Numbers `${{items}}`."
    ]

    def __init__(self, items: List[str] = None, **kwargs) -> None:
        if items is None:
            items = ["First step", "Second step", "Third step"]
        super().__init__(items=items, **kwargs)
        
        # Get actual value from Argument if needed
        items_value = self.items.value if hasattr(self.items, 'value') else self.items
        
        # Build markdown syntax for numbered list
        path_actions = []
        for i, item in enumerate(items_value):
            number = i + 1
            path_actions.append(
                TypeAction(text=f"{number}. {item}", input_mode="copy_paste", thought=f"Type numbered item in markdown syntax: '{number}. {item}'")
            )
            if i < len(items_value) - 1:
                path_actions.extend([
                    WaitAction(duration=0.3),
                    HotKeyAction(keys=["enter"], thought="Start new line for next numbered item"),
                    WaitAction(duration=0.3)
                ])
            else:
                path_actions.append(WaitAction(duration=0.5))

        self.add_path(
            "notepad_insert_numbered_list_syntax",
            path=path_actions
        )


@register("NotepadItalicMarkdown")
class NotepadItalicMarkdown(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_italic_markdown"
    text: Argument = Argument(
        value="emphasized",
        description="The text content to format as italic using Markdown syntax. Can be any string including words, phrases, or short sentences. The text will be wrapped with single asterisks (*text*) or single underscores (_text_) to create italic formatting in Markdown. Examples: 'emphasized' (single word), 'important note' (phrase), 'see chapter 3' (reference), 'e.g.' (abbreviation), 'Lorem ipsum' (Latin/foreign phrases). Use for: emphasis, foreign words, book/movie titles, technical terms, variable names in documentation. The italic formatting will be visible when the Markdown is rendered. Note: italics are lighter emphasis than bold."
    )

    # Schema payload
    descriptions: List[str] = [
        "Italicize `${{text}}`.",
        "Make `${{text}}` italic.",
        "Italic the text `${{text}}`.",
        "Apply italic to `${{text}}`.",
        "Emphasize `${{text}}`."
    ]

    def __init__(self, text: str = "emphasized", **kwargs) -> None:
        super().__init__(text=text, **kwargs)
        self.add_path(
            "notepad_italic_markdown_syntax",
            path=[
                TypeAction(text=f"*{text}*", input_mode="copy_paste", thought=f"Type italic markdown syntax: '*{text}*'"),
                WaitAction(duration=0.5)
            ]
        )


@register("NotepadNewMarkdownTab")
class NotepadNewMarkdownTab(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_new_markdown_tab"
    
    # Schema payload
    descriptions: List[str] = [
        "Open new Markdown tab.",
        "Create Markdown file.",
        "Start Markdown document.",
        "New Markdown tab.",
        "Markdown tab please."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_click_new_markdown_tab",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the New Markdown Tab option"),
                WaitAction(duration=0.5)
            ]
        )
        self.add_path(
            "notepad_new_markdown_tab_hotkey",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open new Markdown tab with Alt+F"),
                WaitAction(duration=1.0),
                TypeAction(text="m", thought="Press M to select New Markdown Tab"),
                WaitAction(duration=0.5)
            ]
        )


@register("NotepadNewWindow")
class NotepadNewWindow(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_new_window"
    
    # Schema payload
    descriptions: List[str] = [
        "Open new window.",
        "Create new Notepad window.",
        "Start fresh window.",
        "New Notepad instance.",
        "Open fresh Notepad."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_new_window_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "n"], thought="Open new Notepad window with Ctrl+Shift+N"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_new_window_run",
            path=[
                HotKeyAction(keys=["win", "r"], thought="Open Run dialog"),
                WaitAction(duration=1.0),
                TypeAction(text="notepad", input_mode="copy_paste", thought="Type 'notepad' to launch new instance"),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["enter"], thought="Press Enter to open new window"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_click_new_window",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the New Window option"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadOpenFile")
class NotepadOpenFile(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_open_file"
    path: Argument = Argument(
        value="C:\\Users\\Docker\\Documents",
        description="Full absolute directory path containing the file to open. Must be a valid Windows directory path with drive letter. Use double backslashes (\\\\) for Windows paths. Examples: 'C:\\\\Users\\\\Docker\\\\Documents' (user documents), 'D:\\\\Work\\\\Notes' (custom work folder), 'C:\\\\Projects\\\\Code' (project directory). The directory must exist and be accessible. Common locations: Documents, Desktop, Downloads, specific project folders. The file specified in file_name must exist within this directory."
    )
    file_name: Argument = Argument(
        value="document.txt",
        description="Name of the file to open, including the file extension. Notepad can open various text-based formats: .txt (plain text, default), .md (Markdown), .log (log files), .csv (data), .json (JSON), .xml (XML), .html (HTML), .css (CSS), .js (JavaScript), .py (Python), .java (Java), .cpp (C++), .bat (batch), .ps1 (PowerShell), .ini (config files), .cfg (configuration). Examples: 'document.txt', 'readme.md', 'notes.txt', 'data.csv', 'config.json', 'script.bat'. The file must exist at the specified path."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open file ${{file_name}} at ${{path}}.",
        "Load file ${{file_name}} at ${{path}}.",
        "Open file ${{file_name}} at ${{path}} in Notepad.",
        "Access file ${{file_name}} at ${{path}}.",
        "Load file ${{file_name}} at ${{path}}."
    ]

    def __init__(self, path: str = "C:\\Users\\Docker\\Documents\\", file_name: str = "document.txt", **kwargs) -> None:
        super().__init__(path=path, file_name=file_name, **kwargs)
        self.add_path(
            "notepad_open_file_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "o"], thought="Open File dialog with Ctrl+O"),
                WaitAction(duration=2.0),
                TypeAction(text=file_name, input_mode="copy_paste", thought=f"Enter file name: '{file_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Open dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=1.0),
                TypeAction(text=path, input_mode="copy_paste", thought=f"Enter file path: '{path}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Open button"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_open_file_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open File menu with Alt+F"),
                WaitAction(duration=0.5),
                TypeAction(text="o", thought="Press O to select Open option"),
                WaitAction(duration=2.0),
                TypeAction(text=file_name, input_mode="copy_paste", thought=f"Enter file name: '{file_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Open dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=1.0),
                TypeAction(text=path, input_mode="copy_paste", thought=f"Enter file path: '{path}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Open button"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_click_open_file",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click the Open option"),
                WaitAction(duration=2.0),
                TypeAction(text=file_name, input_mode="copy_paste", thought=f"Enter file name: '{file_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Open dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=1.0),
                TypeAction(text=path, input_mode="copy_paste", thought=f"Enter file path: '{path}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Open button"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadOpenRecentFile")
class NotepadOpenRecentFile(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_open_recent_file"
    index: Argument = Argument(
        value=1,
        description="Position/index of the file in the Recent Files list to open. Must be a positive integer starting from 1 (most recent file). The Recent Files list shows recently opened documents in reverse chronological order. Examples: 1 (most recently opened file, first in list), 2 (second most recent), 3 (third most recent), 5 (fifth most recent). The index must be within the available recent files (typically Notepad keeps 10-20 recent files). Use 1 for the last file you worked on, 2 for the one before that, etc. If the index exceeds the number of recent files, the action will fail."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open recent file #`${{index}}`.",
        "Load recent item `${{index}}`.",
        "Open from recent list #`${{index}}`.",
        "Recent file number `${{index}}`.",
        "Recent file #`${{index}}`."
    ]

    def __init__(self, index: int = 1, **kwargs) -> None:
        super().__init__(index=index, **kwargs)
        # Get actual value from Argument if needed
        index_value = self.index.value if hasattr(self.index, 'value') else self.index
        self.add_path(
            "notepad_open_recent_file_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open Recent files with Alt+F"),
                WaitAction(duration=1.0),
                TypeAction(text="r", thought="Press R to select Recent files submenu"),
                WaitAction(duration=1.0),
                TypeAction(text=str(index_value), input_mode="key", thought=f"Select recent file #{index_value}"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_click_open_recent_file",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Recent files submenu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click recent file #{index_value}"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadPageSetup")
class NotepadPageSetup(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_page_setup"
    
    # Schema payload
    descriptions: List[str] = [
        "Open page setup.",
        "Configure page settings.",
        "Set up page layout.",
        "Adjust page options.",
        "Page setup dialog."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_page_setup_menu",
            path=[
                HotKeyAction(keys=["alt", "f"], thought="Open Page Setup with Alt+F"),
                WaitAction(duration=1.0),
                TypeAction(text="u", thought="Press U to select Page Setup option"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_click_page_setup",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Page Setup option"),
                WaitAction(duration=2.0)
            ]
        )


@register("NotepadSaveAllFiles")
class NotepadSaveAllFiles(NotepadBaseAction):
    # Canonical identifiers
    type: str = "notepad_save_all_files"
    
    # Schema payload
    descriptions: List[str] = [
        "Save all open files.",
        "Store all documents.",
        "Save everything.",
        "Keep all changes.",
        "Write all files."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "notepad_save_all_files_hotkey",
            path=[
                HotKeyAction(keys=["ctrl", "alt", "s"], thought="Save all files with Ctrl+Alt+S"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "notepad_click_save_all_files",
            path=[
                SingleClickAction(thought="Click the File menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Save All option"),
                WaitAction(duration=2.0)
            ]
        )