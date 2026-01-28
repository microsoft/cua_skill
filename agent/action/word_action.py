import os
from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, RightClickAction, PressKeyAction, DoubleClickAction, TripleClickAction, KeyDownAction, KeyUpAction
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

use_hotkey = True
use_mouse_click = False

assert not (use_hotkey and use_mouse_click), "Only one of `use_hotkey` and `use_mouse_click` can be True."
assert not (not use_hotkey and not use_mouse_click), "At least one of `use_hotkey` and `use_mouse_click` must be True."

class WordBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="Word",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Word",
        description="The name of the Word application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("WordLaunch")
class WordLaunch(WordBaseAction):
    type: str = "word_launch"

    descriptions: List[str] = [
        "Open Word.",
        "Launch Word.",
        "Start Word.",
        "Open the Microsoft Word.",
        "Launch the Microsoft Word.",
        "Start the Microsoft Word."
    ]

    def __init__(self, **kwargs):
        super().__init__(application_name=self.application_name, **kwargs)
        self.add_path(
            "launch_word",
            path=[
                LaunchApplication(application_name="Windows PowerShell"),
                WaitAction(duration=4.0),
                TypeAction(text="Start-Process winword", thought="Type the command 'Start-Process winword' to start Word application."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to execute the command."),
                WaitAction(duration=4.0, thought="Wait for a few seconds to let Word launch."),
            ]
        )


@register("WordCreateBlankNewDocument")
class WordCreateBlankNewDocument(WordBaseAction):
    type: str = "word_create_new_blank_document"

    descriptions: List[str] = [
        "Create a new document.",
        "Start a new document.",
        "Open a new document.",
        "Create a new Word document.",
        "Start a new Word document.",
        "Open a new Word document."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # This assumes we are on the main page of Word, not in an existing document
        # TODO: if we know that we are in an existing document, we can do hotkey Ctrl + N to create a new document directly
        self.add_path(
            "click_create_blank_document",
            path=[
                SingleClickAction(thought="Click the 'New' tab to ensure we are on the main screen."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Blank document' button to create a new document."),
                WaitAction(duration=1.0)
            ]
        )


@register("WordCreateNewDocumentFromTemplate")
class WordCreateNewDocumentFromTemplate(WordBaseAction):
    type: str = "word_create_new_document_from_template"

    template_name: Argument = Argument(
        value="",
        description="The name of the template to create the new document from.",
        frozen=False
    )

    descriptions: List[str] = [
        "Create a new document from template ${{template_name}}.",
        "Start a new document from template ${{template_name}}.",
        "Open a new document from template ${{template_name}}.",
        "Create a new Word document from template ${{template_name}}.",
        "Start a new Word document from template ${{template_name}}.",
        "Open a new Word document from template ${{template_name}}."
    ]

    def __init__(self, template_name: str = None, **kwargs):
        super().__init__(template_name=template_name, **kwargs)
        self.add_path(
            "click_create_document_from_template",
            path=[
                SingleClickAction(thought="Click the 'New' tab to ensure we are on the main screen."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Search for online templates' field to search for a target template."),
                WaitAction(duration=1.0),
                TypeAction(text=template_name if template_name is not None else "Blank", thought=f"Type the {template_name} to search for the template."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to search for the template."),
                WaitAction(duration=3.0, thought="Wait for a few seconds to let Word show the search results."),
                SingleClickAction(thought=f"Click on the target template '{template_name}' to select it."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Create' button to create a new document from the selected template."),
                WaitAction(duration=3.0, thought="Wait for a few seconds to let Word create the document.")
            ]
        )


@register("WordNameDocument")
class WordNameDocument(WordBaseAction):
    type: str = "word_name_document"
    filename: Argument = Argument(
        value=None,
        description="Name of the document file."
    )

    descriptions: List[str] = [
        "Name the document as ${{filename}}.",
        "Give the document the name as ${{filename}}.",
        "Set the document name to ${{filename}}.",
        "Rename the document to ${{filename}}.",
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)
        # No keyboard shortcut for this operation
        # self.add_path(
        #     "click_document_name",
        #     path=[
        #         SingleClickAction(thought="Click the document name text area at the top center of the Word window to focus."),
        #         WaitAction(duration=1.0),
        #         TypeAction(text=filename if filename is not None else "My Document", input_mode="copy_paste", thought=f"Type the document name '{self.filename}'."),
        #         WaitAction(duration=1.0),
        #         HotKeyAction(keys=["enter"], thought="Press Enter to confirm the new document name."),
        #         WaitAction(duration=1.0)
        #     ]
        # )
        self.add_path(
            "hotkey_document_name",
            path=[
                HotKeyAction(keys=["f12"], thought="Press F12 to open the Save As dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=filename if filename is not None else "My Document.docx", input_mode="copy_paste", thought=f"Type the file name '{filename}' to save as."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                WaitAction(duration=4.0)
            ]
        )


@register("WordOpenFile")
class WordOpenFile(WordBaseAction):
    type: str = "word_open_file"
    filename: Argument = Argument(
        value=None,
        description="Path or name of the document file to open."
    )

    descriptions: List[str] = [
        "Open document ${{filename}}.",
        "Load the file ${{filename}} in Word.",
        "Open document ${{filename}}.",
        "Open the .docx file ${{filename}}.",
        "Open ${{filename}} document."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)

        # We open the file via PowerShell to avoid issues with different Word versions
        self.add_path(
            "powershell_open_file",
            path=[
                LaunchApplication(application_name="Windows PowerShell"),
                WaitAction(duration=4.0),
                TypeAction(text=f"Start-Process \"{filename}\"", thought=f"Type the command 'Start-Process \"{filename}\"' to start Word application."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to execute the command."),
                WaitAction(duration=4.0, thought="Wait for a few seconds to let Word launch.")
            ]
        )


@register("WordSave")
class WordSave(WordBaseAction):
    type: str = "word_save"
    filename: Argument = Argument(
        value=None,
        description="Path or name of the document file to save."
    )

    descriptions: List[str] = [
        "Save the document",
        "Save the current file.",
        "Save the current document.",
        "Save the current Word file.",
        "Save the document as ${{filename}}.",
        "Save the file as ${{filename}}.",
        "Save the document as ${{filename}}.",
        "Save the .docx file as ${{filename}}.",
        "Save the document with name ${{filename}}."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)
        # We prefer using keyboard shortcuts than mouse clicks
        self.add_path(
            "hotkey_save_file",
            path=[
                HotKeyAction(keys=["ctrl", "s"], thought="Press Ctrl + S to open the Save dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=filename if filename is not None else "My Document.docx", input_mode="copy_paste", thought=f"Type the file name '{filename}' to save."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                WaitAction(duration=1.0)
            ]
        )


@register("WordSaveAs")
class WordSaveAs(WordBaseAction):
    type: str = "word_save_as"
    filename: Argument = Argument(
        value=None,
        description="Name of the document file. It must include the file extension, e.g., .docx, .pdf ..."
    )

    descriptions: List[str] = [
        "Save the document as ${{filename}}.",
        "Save the file as ${{filename}}.",
        "Save the document as ${{filename}}.",
        "Save the .docx file as ${{filename}}.",
        "Save the document with name ${{filename}}."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)
        # We prefer using keyboard shortcuts than mouse clicks
        if filename is None:
            return
        if filename.endswith(".docx"):
            
            self.add_path(
                "hotkey_save_as_file",
                path=[
                    HotKeyAction(keys=["f12"], thought="Press F12 to open the Save As dialog."),
                    WaitAction(duration=1.0),
                    TypeAction(text=filename if filename is not None else "My Document.docx", input_mode="copy_paste", thought=f"Type the file name '{filename}' to save."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                    WaitAction(duration=1.0)
                    
                ]        )
        else:
            self.add_path(
                "hotkey_save_as_file",
                path=[
                    HotKeyAction(keys=["f12"], thought="Press F12 to open the Save As dialog."),
                    WaitAction(duration=1.0),
                    TypeAction(text=filename if filename is not None else "My Document.docx", input_mode="copy_paste", thought=f"Type the file name '{filename}' to save."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the box right to Save as Type to open the dropdown menu to select the file type."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the right file type option to select the desired file type according to the file extension '{filename.split('.')[-1]}'."),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                    WaitAction(duration=1.0)
                ]        )


@register("WordExportPDF")
class WordExportPDF(WordBaseAction):
    type: str = "word_export_pdf"
    filename: Argument = Argument(
        value=None,
        description="Name of the PDF file to export."
    )

    descriptions: List[str] = [
        "Export the document as a PDF file named ${{filename}}.",
        "Save the document as a PDF file named ${{filename}}.",
        "Convert the document to a PDF file named ${{filename}}."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_export_pdf",
                path=[
                    HotKeyAction(keys=["alt", "f"], thought="Press Alt + F to open the File menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="e", thought="Press E to open the Export options."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="p", thought="Press P to select the 'Create PDF/XPS Document' option to export as PDF."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="a", thought="Press A to open the 'Create PDF/XPS' dialog."),
                    WaitAction(duration=1.0),
                    TypeAction(text=filename, input_mode="copy_paste", thought=f"Type the PDF file name '{filename}' to export."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and export the PDF file."),
                    WaitAction(duration=3.0, thought="Wait for a few seconds to let Word export the PDF file."),
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_export_pdf",
                path=[
                    SingleClickAction(thought="Click the 'File' tab to open the file menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Export' button to open the export options."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Create PDF/XPS Document' option to export as PDF."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Create PDF/XPS' button to open the save dialog."),
                    WaitAction(duration=1.0),
                    TypeAction(text=filename, input_mode="copy_paste", thought=f"Type the PDF file name '{filename}' to export."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and export the PDF file."),
                    WaitAction(duration=3.0, thought="Wait for a few seconds to let Word export the PDF file."),
                ]
            )


@register("WordMoveCursorToEnd")
class WordMoveCursorToEnd(WordBaseAction):
    type: str = "word_move_cursor_to_end"

    descriptions: List[str] = [
        "Move the cursor to the end of the document.",
        "Place the cursor at the end of the document.",
        "Go to the end of the document.",
        "Navigate to the end of the document."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_move_cursor_to_end",
            path=[
                HotKeyAction(keys=["ctrl", "end"], thought="Press Ctrl + End to move the cursor to the end of the document."),
                WaitAction(duration=1)
            ]
        )


@register("WordInsertText")
class WordInsertText(WordBaseAction):
    type: str = "word_insert_text"
    text: Argument = Argument(
        value=None,
        description="Text content to insert into the document."
    )

    descriptions: List[str] = [
        "Insert the text '${{text}}' into the document.",
        "Add the text '${{text}}' to the document.",
        "Type the text '${{text}}' into the document.",
        "Write the text '${{text}}' into the document."
    ]

    def __init__(self, text: str = None, **kwargs):
        super().__init__(text=text, **kwargs)
        self.add_path(
            "type_insert_text",
            path=[
                TypeAction(text=text if text is not None else "Sample text to insert.", input_mode="keyboard", thought=f"Type the text '{text}' into the document."),
                WaitAction(duration=1.0)
            ]
        )


@register("WordInsertImage")
class WordInsertImage(WordBaseAction):
    type: str = "word_insert_image"
    image_path: Argument = Argument(
        value=None,
        description="Path to the image file to insert."
    )

    descriptions: List[str] = [
        "Insert an image from path '${{image_path}}' into the document.",
        "Add an image from path '${{image_path}}' to the document.",
        "Insert a picture from path '${{image_path}}' into the document.",
        "Add a picture from path '${{image_path}}' to the document."
    ]

    def __init__(self, image_path: str = None, **kwargs):
        super().__init__(image_path=image_path, **kwargs)
        if image_path is None:
            return
        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_insert_image",
                path=[
                    HotKeyAction(keys=["alt", "n"], thought="Press Alt + N to switch to the Insert tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="p", thought="Press P to open the Pictures dropdown menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="d", thought="Press D to select 'This Device' option to browse for an image on the computer."),
                    WaitAction(duration=1.0),
                    
                    HotKeyAction(keys=["alt", "d"], thought="Press Alt + D to focus on the folder path input area at the top of the browse dialog."),
                    WaitAction(duration=1.0),
                    TypeAction(text=os.path.dirname(image_path), input_mode="copy_paste", thought=f"Type the path to the folder containing the file to open, '{os.path.dirname(image_path)}'."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm the folder path."),
                    WaitAction(duration=1.0),
                    
                    HotKeyAction(keys=["alt", "n"], thought="Press Alt + N to focus on the file name input area at the bottom of the browse dialog."),
                    TypeAction(text=os.path.basename(image_path), input_mode="copy_paste", thought=f"Type the file name '{os.path.basename(image_path)}' to open."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and insert the image."),
                    WaitAction(duration=4.0, thought="Wait for a few seconds to let Word insert the image."),
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_insert_image",
                path=[
                    SingleClickAction(thought="Click the 'Insert' tab to switch to the insert menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Pictures' button to open the dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'This Device' option to browse for an image on the computer."),
                    WaitAction(duration=1.0),
                    TypeAction(text=image_path if image_path is not None else "C:\\path\\to\\image.jpg", input_mode="copy_paste", thought=f"Type the image file path '{image_path}' to insert."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and insert the image."),
                    WaitAction(duration=3.0, thought="Wait for a few seconds to let Word insert the image."),
                ]
            )


@register("WordSelectAllText")
class WordSelectAllText(WordBaseAction):
    type: str = "word_select_all_text"

    descriptions: List[str] = [
        "Select all content.",
        "Select everything in the document.",
        "Select the entire document.",
        "Select all text in the document."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_select_all_text",
            path=[
                SingleClickAction(thought="Click in the center of the first word to activate the edit mode."),
                WaitAction(duration=1),
                HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select all content."),
                WaitAction(duration=1)
            ]
        )


@register("WordSetTextFontSize")
class WordSetTextFontSize(WordBaseAction):
    type: str = "word_set_text_font_size"
    font_size: Argument = Argument(
        value=None,
        description="Font size to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the font size of selected text to ${{font_size}} pt.",
        "Set font size to ${{font_size}} pt for the selected text.",
        "Update the font size of the selected text to ${{font_size}} pt.",
        "Make the font size ${{font_size}} pt for the selected text.",
        "Adjust the font size of the selected text to ${{font_size}} pt."
    ]

    def __init__(self, font_size: int = None, **kwargs):
        super().__init__(font_size=font_size, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_set_text_font_size",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="f", thought="Press F and S to focus on the font size text field. First press F."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="s", thought="Then press S to complete the focusing on the font size text field."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(font_size) if font_size is not None else "24", input_mode="copy_paste", thought=f"Type the font size '{font_size}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font size."),
                    WaitAction(duration=1.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_font_size",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the font size text field to input the desired font size."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(font_size) if font_size is not None else "24", input_mode="copy_paste", thought=f"Type the font size '{font_size}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font size."),
                    WaitAction(duration=1.0)
                ]
            )


@register("WordSetTextFontFamily")
class WordSetTextFontFamily(WordBaseAction):
    type: str = "word_set_text_font_family"
    font_family: Argument = Argument(
        value=None,
        description="Font family to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the font family of selected text to ${{font_family}}.",
        "Set font family to ${{font_family}} for the selected text.",
        "Update the font family of the selected text to ${{font_family}}.",
        "Make the font family ${{font_family}} for the selected text.",
        "Adjust the font family of the selected text to ${{font_family}}."
    ]

    def __init__(self, font_family: str = None, **kwargs):
        super().__init__(font_family=font_family, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_set_text_font_family",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="f", thought="Press F and F to focus on the font family text field. First press F."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="f", thought="Then press F again to complete the focusing on the font family text field."),
                    WaitAction(duration=1.0),
                    TypeAction(text=font_family if font_family is not None else "Arial", input_mode="copy_paste", thought=f"Type the font family '{font_family}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font family."),
                    WaitAction(duration=1.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_font_family",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the font family text field to input the desired font family."),
                    WaitAction(duration=1.0),
                    TypeAction(text=font_family if font_family is not None else "Arial", input_mode="copy_paste", thought=f"Type the font family '{font_family}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font family."),
                    WaitAction(duration=1.0)
                ]
            )


@register("WordSetTextColor")
class WordSetTextColor(WordBaseAction):
    type: str = "word_set_text_color"
    font_color: Argument = Argument(
        value=None,
        description="Color name to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the font color of selected text to ${{font_color}}.",
        "Set font color to ${{font_color}} for the selected text.",
        "Update the font color of the selected text to ${{font_color}}.",
        "Make the font color ${{font_color}} for the selected text.",
        "Adjust the font color of the selected text to ${{font_color}}."
    ]

    def __init__(self, font_color: str = None, **kwargs):
        super().__init__(font_color=font_color, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_set_text_font_color",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="f", thought="Press F and C to open the font color dropdown menu. First press F."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="c", thought="Then press C to complete the opening of the font color dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{font_color if font_color is not None else 'Black'}' color to set it for the selected text."),
                    WaitAction(duration=1.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_font_color",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the font color dropdown button to open the color selection menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{font_color if font_color is not None else 'Black'}' color to set it for the selected text."),
                    WaitAction(duration=1.0)
                ]
            )


@register("WordSetTextHighlight")
class WordSetTextHighlight(WordBaseAction):
    type: str = "word_set_text_highlight"
    highlight: Argument = Argument(
        value=None,
        description="Highlight color to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the highlight color of selected text to ${{highlight}}.",
        "Set highlight color to ${{highlight}} for the selected text.",
        "Update the highlight color of the selected text to ${{highlight}}.",
        "Make the highlight color ${{highlight}} for the selected text.",
        "Adjust the highlight color of the selected text to ${{highlight}}."
    ]

    def __init__(self, highlight: str = None, **kwargs):
        super().__init__(highlight=highlight, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_set_text_highlight",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="i", thought="Press I to open the text highlight color dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{highlight if highlight is not None else 'Yellow'}' color to set it for the selected text."),
                    WaitAction(duration=4.0)
                ]
            )

        if use_mouse_click:
            self.add_path(
                "click_set_text_highlight",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the Text Highlight Color dropdown button to open the color selection menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{highlight if highlight is not None else 'Yellow'}' color to set it for the selected text."),
                    WaitAction(duration=4.0)
                ]
            )


@register("WordSetTextStyle")
class WordSetTextStyle(WordBaseAction):
    type: str = "word_set_text_style"
    text_style: Argument = Argument(
        value=None,
        description="Text style to set for the selected text. For example, Bold, Italic, Underline, Strikethrough, Subscript, Superscript."
    )

    descriptions: List[str] = [
        "Change the text style of selected text to ${{text_style}}.",
        "Set text style to ${{text_style}} for the selected text.",
        "Update the text style of the selected text to ${{text_style}}.",
        "Make the text style ${{text_style}} for the selected text.",
        "Adjust the text style of the selected text to ${{text_style}}."
    ]

    def __init__(self, text_style: str = None, **kwargs):
        super().__init__(text_style=text_style, **kwargs)
        if text_style is None:
            return

        if use_hotkey:
            # There is a more straightforward shortcut for Bold, Italic, and Underline using Ctrl + B/I/U
            if text_style in ["Bold", "Italic", "Underline"]:
                shortcut_mapping = {
                    "Bold": "b",
                    "Italic": "i",
                    "Underline": "u"
                }
                self.add_path(
                    "hotkey_set_text_style",
                    path=[
                        HotKeyAction(keys=["ctrl", shortcut_mapping.get(text_style, "b")], thought=f"Press Ctrl + {shortcut_mapping.get(text_style, 'b').upper()} to apply the {text_style} style for the selected text."),
                        WaitAction(duration=1.0)
                    ]
                )
                return
            # We prefer using keyboard shortcuts Alt + H, 1/2/3/4/5 than mouse clicks
            key_tips_mapping = {
                "Bold": "1",
                "Italic": "2",
                "Underline": "3",
                "Strikethrough": "4",
                "Subscript": "5",
                "Superscript": "6"
            }
            self.add_path(
                "hotkey_set_text_style",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key=key_tips_mapping.get(text_style, "1"), thought=f"Press {key_tips_mapping.get(text_style, '1')} to apply the {text_style if text_style is not None else 'Bold'} style for the selected text."),
                    WaitAction(duration=1.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_style",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the '{text_style if text_style is not None else 'Bold'}' button to apply that style to the selected text."),
                    WaitAction(duration=1.0)
                ]
            )


@register("WordSetTextCase")
class WordSetTextCase(WordBaseAction):
    type: str = "word_set_text_case"
    case_option: Argument = Argument(
        value=None,
        description="Text case option to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the text case of selected text to ${{case_option}}.",
        "Set text case to ${{case_option}} for the selected text.",
        "Update the text case of the selected text to ${{case_option}}.",
        "Make the text case ${{case_option}} for the selected text.",
        "Adjust the text case of the selected text to ${{case_option}}."
    ]

    def __init__(self, case_option: str = "sentence case", **kwargs):
        super().__init__(case_option=case_option, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            key_tips_mapping = {
                "sentence case": "S",
                "lowercase": "L",
                "uppercase": "U",
                "capitalize each word": "C",
                "toggle case": "T"
            }
            self.add_path(
                "hotkey_set_text_case",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="7", thought="Press 7 to open the Change Case dropdown menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key=key_tips_mapping.get(case_option.lower(), "S"), thought=f"Press {key_tips_mapping.get(case_option.lower(), 'S')} to select the {case_option if case_option is not None else 'Sentence case'} option for the selected text."),
                    WaitAction(duration=4.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_case",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the Change Case dropdown button (the small arrow down beside the 'Aa' icon) to open the case options menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{case_option if case_option is not None else 'Sentence case'}' option to set it for the selected text."),
                    WaitAction(duration=4.0)
                ]
            )


@register("WordSetTextLineSpacing")
class WordSetTextLineSpacing(WordBaseAction):
    type: str = "word_set_text_line_spacing"
    spacing_option: Argument = Argument(
        value=None,
        description="Line spacing option to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the line spacing of selected text to ${{spacing_option}}.",
        "Set line spacing to ${{spacing_option}} for the selected text.",
        "Update the line spacing of the selected text to ${{spacing_option}}.",
        "Make the line spacing ${{spacing_option}} for the selected text.",
        "Adjust the line spacing of the selected text to ${{spacing_option}}."
    ]

    def __init__(self, spacing_option: str = "1.0", **kwargs):
        super().__init__(spacing_option=spacing_option, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            key_tips_mapping = {
                "1.0": "1",
                "1.5": "5",
                "2.0": "2",
            }
            if spacing_option in key_tips_mapping:
                self.add_path(
                    "hotkey_set_text_line_spacing",
                    path=[
                        HotKeyAction(keys=["ctrl", key_tips_mapping[spacing_option]], thought=f"Press Ctrl + {key_tips_mapping[spacing_option]} to set the line spacing to {spacing_option}."),
                        WaitAction(duration=4.0)
                    ]
                )
            else:
                self.add_path(
                    "hotkey_set_text_line_spacing",
                    path=[
                        HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                        WaitAction(duration=1.0),
                        PressKeyAction(key="k", thought="Press K to open the line spacing dropdown menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought=f"Click on the '{spacing_option if spacing_option is not None else '1.0'}' option to set it for the selected text."),
                        WaitAction(duration=4.0)
                    ]
                )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_line_spacing",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the line spacing dropdown button to open the line spacing options menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{spacing_option if spacing_option is not None else '1.0'}' option to set it for the selected text."),
                    WaitAction(duration=4.0)
                ]
            )


@register("WordInsertBullets")
class WordInsertBullets(WordBaseAction):
    type: str = "word_insert_bullets"
    bullet_style: Argument = Argument(
        value=None,
        description="Bullet style to apply to the selected text."
    )

    descriptions: List[str] = [
        "Add bullets to the selected text.",
        "Insert bullet points in the selected text.",
        "Apply bullet formatting to the selected text.",
        "Add ${{bullet_style}} bullets to selected text.",
        "Insert ${{bullet_style}} bullet points in the selected text.",
        "Apply ${{bullet_style}} bullet formatting to the selected text."
    ]

    def __init__(self, bullet_style: str = None, **kwargs):
        super().__init__(bullet_style=bullet_style, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_insert_bullets",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="u", thought="Press U to open the bullets dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{bullet_style if bullet_style is not None else 'Filled Round Bullets'}' bullet style to apply it to the selected text."),
                    WaitAction(duration=1.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_insert_bullets",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Bullets' dropdown button to open the bullet style menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{bullet_style if bullet_style is not None else 'Filled Round Bullets'}' bullet style to apply it to the selected text."),
                    WaitAction(duration=1.0)
                ]
            )


@register("WordInsertNumbering")
class WordInsertNumbering(WordBaseAction):
    type: str = "word_insert_numbering"
    numbering_style: Argument = Argument(
        value=None,
        description="Numbering style to apply to the selected text."
    )

    descriptions: List[str] = [
        "Add numbering to the selected text.",
        "Insert numbering to the selected text.",
        "Apply numbering to the selected text.",
        "Add ${{numbering_style}} numbering to selected text.",
        "Insert ${{numbering_style}} numbering to the selected text.",
        "Apply ${{numbering_style}} numbering to the selected text."
    ]

    def __init__(self, numbering_style: str = None, **kwargs):
        super().__init__(numbering_style=numbering_style, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_insert_numbering",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="n", thought="Press N to open the numbering dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{numbering_style if numbering_style is not None else '1, 2, 3...'}' numbering style to apply it to the selected text."),
                    WaitAction(duration=1.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_insert_numbering",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Numbering' dropdown button to open the numbering style menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{numbering_style if numbering_style is not None else '1, 2, 3...'}' numbering style to apply it to the selected text."),
                ]
            )


@register("WordSetParagraphAlignment")
class WordSetParagraphAlignment(WordBaseAction):
    type: str = "Word_set_paragraph_alignment"
    alignment_option: Argument = Argument(
        value=None,
        description="Paragraph alignment option to set for the selected text."
    )

    descriptions: List[str] = [
        "Set paragraph alignment of selected text to ${{alignment_option}}.",
        "Change paragraph alignment to ${{alignment_option}} for the selected text.",
        "Update paragraph alignment of the selected text to ${{alignment_option}}.",
        "Make the paragraph alignment ${{alignment_option}} for the selected text.",
        "Adjust the paragraph alignment of the selected text to ${{alignment_option}}."
    ]

    def __init__(self, alignment_option: str = None, **kwargs):
        super().__init__(alignment_option=alignment_option, **kwargs)
        if alignment_option is None:
            return
        if use_hotkey:
            # There is a more straightforward shortcut for Left, Center, Right, and Justify using Ctrl + L/E/R/J
            if alignment_option in ["Align Left", "Center", "Align Right", "Justify"]:
                shortcut_mapping = {
                    "Align Left": "l",
                    "Center": "e",
                    "Align Right": "r",
                    "Justify": "j"
                }
                self.add_path(
                    "hotkey_set_paragraph_alignment",
                    path=[
                        HotKeyAction(keys=["ctrl", shortcut_mapping.get(alignment_option, "l")], thought=f"Press Ctrl + {shortcut_mapping.get(alignment_option, 'l').upper()} to set the {alignment_option if alignment_option is not None else 'Align Left'} alignment for the selected text."),
                        WaitAction(duration=1.0)
                    ]
                )
            # We prefer using keyboard shortcuts Alt + H, AL/AC/AR/AJ/AD than mouse clicks
            key_tips_mapping = {
                "Align Left": "l",
                "Center": "c",
                "Align Right": "r",
                "Justify": "j",
                "Distributed": "d"
            }
            self.add_path(
                "hotkey_set_paragraph_alignment",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="a", thought="Press A for further selecting the paragraph alignment options."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key=key_tips_mapping.get(alignment_option, "l"), thought=f"Press {key_tips_mapping.get(alignment_option, 'l').upper()} to set the {alignment_option if alignment_option is not None else 'Align Left'} alignment for the selected text."),
                    WaitAction(duration=1.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_paragraph_alignment",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the '{alignment_option if alignment_option is not None else 'Align Left'}' button to set that alignment for the selected text."),
                    WaitAction(duration=1.0)
                ]
            )


@register("WordInsertTable")
class WordInsertTable(WordBaseAction):
    type: str = "Word_insert_table"
    rows: Argument = Argument(
        value=None,
        description="Number of rows for the table."
    )
    columns: Argument = Argument(
        value=None,
        description="Number of columns for the table."
    )

    descriptions: List[str] = [
        "Insert a table with ${{rows}} rows and ${{columns}} columns.",
        "Add a table of size ${{rows}} by ${{columns}}.",
        "Create a table with ${{rows}} rows and ${{columns}} columns.",
        "Place a table with ${{rows}} rows and ${{columns}} columns.",
        "Generate a table having ${{rows}} rows and ${{columns}} columns."
    ]

    def __init__(self, rows: int = None, columns: int = None, **kwargs):
        super().__init__(rows=rows, columns=columns, **kwargs)

        if use_hotkey:
            # otherwise, we need to type the number of rows and columns
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_insert_table",
                path=[
                    HotKeyAction(keys=["alt", "n"], thought="Press Alt + N to switch to the Insert tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="t", thought="Press T to open the Table dropdown button."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="i", thought="Press I to select the 'Insert Table...' option at the bottom of the table grid to open the insert table dialog."),
                    WaitAction(duration=1.0),

                    # the cursor is by default in the 'number of columns' input field
                    HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select the default number of columns."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(columns) if columns is not None else "10", input_mode="copy_paste", thought=f"Type the number of columns '{columns}' for the table."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["alt", "r"], thought="Press Alt + R to switch to the 'number of rows' input field."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select the default number of rows."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(rows) if rows is not None else "10", input_mode="copy_paste", thought=f"Type the number of rows '{rows}' for the table."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and insert the table."),
                    WaitAction(duration=4.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_insert_table",
                path=[
                    SingleClickAction(thought="Click the 'Insert' tab to switch to the insert menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Table' dropdownbutton to open the table grid."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Insert Table...' option at the bottom of the table grid to open the insert table dialog."),
                    WaitAction(duration=1.0),
                    
                    # delete the default number of columns, and type the desired number of columns
                    SingleClickAction(thought="Click the 'number of columns' input field to focus on it. It is the top input field in the pop-up dialog."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select the default number of columns."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(columns) if columns is not None else "10", input_mode="copy_paste", thought=f"Type the number of columns '{columns}' for the table."),
                    WaitAction(duration=1.0),

                    # delete the default number of rows, and type the desired number of rows
                    SingleClickAction(thought="Click the 'number of rows' input field to focus on it. It is the below input field in the pop-up dialog."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select the default number of rows."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(rows) if rows is not None else "10", input_mode="copy_paste", thought=f"Type the number of rows '{rows}' for the table."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and insert the table."),
                    WaitAction(duration=4.0)
                ]
            )


def select_table_cell(row_index: int, column_index: int) -> List[BaseAction]:
    move_down_actions = []
    for i in range(row_index - 1):
        move_down_actions.extend([
            HotKeyAction(keys=["down"], thought=f"Press Down Arrow key to move to the below row."),
            WaitAction(duration=1.0)
        ])
    
    move_right_actions = []
    for j in range(column_index - 1):
        move_right_actions.extend([
            HotKeyAction(keys=["tab"], thought=f"Press Tab to move to the right column."),
            WaitAction(duration=1.0)
        ])
    
    return [
        SingleClickAction(thought=f"Click on the first cell (at the left-top corner of the table, including the headers rows) of the table to focus on it. It is the leftmost cell in the headers row of the table. You should click on the middle of that cell, not the border."),
        WaitAction(duration=1.0),
        *move_down_actions,
        *move_right_actions
    ]


@register("WordInsertTableRow")
class WordInsertTableRow(WordBaseAction):
    type: str = "word_insert_table_row"
    row_index: Argument = Argument(
        value=None,
        description="The index of the row to insert."
    )

    descriptions: List[str] = [
        "Insert a row into the table at index ${{row_index}}.",
        "Add a row to the table at index ${{row_index}}.",
        "Create a new row in the table at index ${{row_index}}.",
        "Place a new row into the table at index ${{row_index}}.",
        "Generate a row in the table at index ${{row_index}}."
    ]

    def __init__(self, row_index: int = 0, **kwargs):
        super().__init__(row_index=row_index, **kwargs)

        if row_index == 1:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_insert_table_row",
                    path=[
                        *select_table_cell(row_index=row_index, column_index=1),
                        WaitAction(duration=1.0),
                        HotKeyAction(keys=["alt"], thought="Press Alt, J, and L to switch to the Table Layout tab. First press Alt."),
                        PressKeyAction(key="j", thought="Then press J."),
                        PressKeyAction(key="l", thought="Then press L to complete the switching to the Table Layout tab."),
                        WaitAction(duration=1.0),
                        PressKeyAction(key="v", thought="Press V to insert a new row above the selected row."),
                        WaitAction(duration=4.0)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_insert_table_row",
                    path=[
                        RightClickAction(thought=f"Right-click on the table row at index {row_index} to open the context menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert' option in the context menu to open the dropdown insert menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert Rows Above' option to add a new row above the selected row."),
                        WaitAction(duration=4.0)
                    ]
                )
        else:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_insert_table_row",
                    path=[
                        *select_table_cell(row_index=row_index - 1, column_index=1),
                        WaitAction(duration=1.0),
                        HotKeyAction(keys=["alt"], thought="Press Alt, J, and L to switch to the Table Layout tab. First press Alt."),
                        PressKeyAction(key="j", thought="Then press J."),
                        PressKeyAction(key="l", thought="Then press L to complete the switching to the Table Layout tab."),
                        WaitAction(duration=1.0),
                        # In older versions of Word, it requires B + E to insert a new row below
                        # In newer versions of Word, it can directly use E to insert a new row below
                        PressKeyAction(key="b", thought="Press B + E to insert a new row below the selected row. First press B."),
                        WaitAction(duration=1.0),
                        PressKeyAction(key="e", thought="Press E to insert a new row below the selected row."),
                        WaitAction(duration=4.0)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_insert_table_row",
                    path=[
                        RightClickAction(thought=f"Right-click on the table row at index {row_index - 1} to open the context menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert' option in the context menu to open the dropdown insert menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert Rows Below' option to add a new row below the selected row."),
                        WaitAction(duration=4.0)
                    ]
                )


@register("WordInsertTableColumn")
class WordInsertTableColumn(WordBaseAction):
    type: str = "word_insert_table_column"
    column_index: Argument = Argument(
        value=None,
        description="The index of the column to insert."
    )

    descriptions: List[str] = [
        "Insert a column into the table at index ${{column_index}}.",
        "Add a column to the table at index ${{column_index}}.",
        "Create a new column in the table at index ${{column_index}}.",
        "Place a new column into the table at index ${{column_index}}.",
        "Generate a column in the table at index ${{column_index}}."
    ]

    def __init__(self, column_index: int = 0, **kwargs):
        super().__init__(column_index=column_index, **kwargs)

        if column_index == 1:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_insert_table_column",
                    path=[
                        *select_table_cell(row_index=1, column_index=column_index),
                        WaitAction(duration=1.0),
                        HotKeyAction(keys=["alt"], thought="Press Alt, J, and L to switch to the Table Layout tab. First press Alt."),
                        PressKeyAction(key="j", thought="Then press J."),
                        PressKeyAction(key="l", thought="Then press L to complete the switching to the Table Layout tab."),
                        WaitAction(duration=1.0),
                        PressKeyAction(key="l", thought="Press L to insert a new column to the left of the selected column."),
                        WaitAction(duration=4.0)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_insert_table_column",
                    path=[
                        RightClickAction(thought=f"Right-click on the table column at index {column_index} to open the context menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert' option in the context menu to open the dropdown insert menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert Columns to the Left' option to add a new column to the left of the selected column."),
                        WaitAction(duration=4.0)
                    ]
                )
        else:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_insert_table_row",
                    path=[
                        *select_table_cell(row_index=1, column_index=column_index - 1),
                        WaitAction(duration=1.0),
                        HotKeyAction(keys=["alt"], thought="Press Alt, J, and L to switch to the Table Layout tab. First press Alt."),
                        PressKeyAction(key="j", thought="Then press J."),
                        PressKeyAction(key="l", thought="Then press L to complete the switching to the Table Layout tab."),
                        WaitAction(duration=1.0),
                        # In older versions of Word, it uses R to insert a new column to the right
                        # In newer versions of Word, it uses I to insert a new column to the right
                        PressKeyAction(key="r", thought="Press R to insert a new column to the right of the selected column."),
                        # PressKeyAction(key="i", thought="Press I to insert a new column to the right of the selected column."),
                        WaitAction(duration=4.0)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_insert_table_column",
                    path=[
                        RightClickAction(thought=f"Right-click on the table column at index {column_index - 1} to open the context menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert' option in the context menu to open the dropdown insert menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Insert Columns to the Right' option to add a new column to the right of the selected column."),
                        WaitAction(duration=4.0)
                    ]
                )


@register("WordDeleteTableRow")
class WordDeleteTableRow(WordBaseAction):
    type: str = "word_delete_table_row"
    row_index: Argument = Argument(
        value=None,
        description="The index of the row to delete."
    )

    descriptions: List[str] = [
        "Delete the row at index ${{row_index}} from the table.",
        "Remove the row at index ${{row_index}} from the table.",
        "Erase the row at index ${{row_index}} in the table.",
        "Clear the row at index ${{row_index}} from the table.",
        "Eliminate the row at index ${{row_index}} from the table."
    ]

    def __init__(self, row_index: int = None, **kwargs):
        super().__init__(row_index=row_index, **kwargs)
        if row_index is None:
            return
        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_delete_table_row",
                path=[
                    *select_table_cell(row_index=row_index, column_index=1),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["alt"], thought="Press Alt, J, and L to switch to the Table Layout tab. First press Alt."),
                    PressKeyAction(key="j", thought="Then press J."),
                    PressKeyAction(key="l", thought="Then press L to complete the switching to the Table Layout tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="d", thought="Press D to open the delete dropdown menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="r", thought="Press R to delete the selected row from the table."),
                    WaitAction(duration=4.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_delete_table_row",
                path=[
                    RightClickAction(thought=f"Right-click on the table row at index {row_index} to open the context menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Delete' option in the context menu to open the dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Delete Rows' option to select it."),
                    WaitAction(duration=4.0)
                ]
            )


@register("WordDeleteTableColumn")
class WordDeleteTableColumn(WordBaseAction):
    type: str = "word_delete_table_column"
    column_index: Argument = Argument(
        value=None,
        description="The index of the column to delete."
    )

    descriptions: List[str] = [
        "Delete the column at index ${{column_index}} from the table.",
        "Remove the column at index ${{column_index}} from the table.",
        "Erase the column at index ${{column_index}} in the table.",
        "Clear the column at index ${{column_index}} from the table.",
        "Eliminate the column at index ${{column_index}} from the table."
    ]

    def __init__(self, column_index: int = None, **kwargs):
        super().__init__(column_index=column_index, **kwargs)
        if column_index is None:
            return
        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_delete_table_column",
                path=[
                    *select_table_cell(row_index=1, column_index=column_index),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["alt"], thought="Press Alt, J, and L to switch to the Table Layout tab. First press Alt."),
                    PressKeyAction(key="j", thought="Then press J."),
                    PressKeyAction(key="l", thought="Then press L to complete the switching to the Table Layout tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="d", thought="Press D to open the delete dropdown menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="c", thought="Press C to delete the selected column from the table."),
                    WaitAction(duration=4.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_delete_table_column",
                path=[
                    RightClickAction(thought=f"Right-click on the table column at index {column_index} to open the context menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Delete' option in the context menu to open the dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Delete Columns' option to select it."),
                    WaitAction(duration=4.0)
                ]
            )


@register("WordDeleteTable")
class WordDeleteTable(WordBaseAction):
    type: str = "word_delete_table"

    descriptions: List[str] = [
        "Delete the entire table.",
        "Remove the whole table.",
        "Erase the complete table.",
        "Clear the entire table.",
        "Eliminate the whole table."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_delete_table",
                path=[
                    *select_table_cell(row_index=1, column_index=1),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["alt"], thought="Press Alt, J, and L to switch to the Table Layout tab. First press Alt."),
                    PressKeyAction(key="j", thought="Then press J."),
                    PressKeyAction(key="l", thought="Then press L to complete the switching to the Table Layout tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="d", thought="Press D to open the delete dropdown menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="t", thought="Press T to delete the entire table."),
                    WaitAction(duration=4.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_delete_table",
                path=[
                    RightClickAction(thought="Right-click on the table to open the context menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Delete' option in the context menu to open the dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Delete Table' option to select it."),
                    WaitAction(duration=4.0)
                ]
            )


@register("WordInsertTableCellText")
class WordInsertTableCellText(WordBaseAction):
    type: str = "word_insert_table_cell_text"
    row_index: Argument = Argument(
        value=0,
        description="Row index of the table cell."
    )
    column_index: Argument = Argument(
        value=0,
        description="Column index of the table cell."
    )
    text: Argument = Argument(
        value="",
        description="Text content to insert into the table cell."
    )

    descriptions: List[str] = [
        "Insert text '${{text}}' into the table cell at row ${{row_index}}, column ${{column_index}}.",
        "Add text '${{text}}' to the table cell located at row ${{row_index}}, column ${{column_index}}.",
        "Type text '${{text}}' into the table cell at row ${{row_index}}, column ${{column_index}}.",
        "Place text '${{text}}' in the table cell at row ${{row_index}}, column ${{column_index}}.",
        "Fill the table cell at row ${{row_index}}, column ${{column_index}} with text '${{text}}'."
    ]

    def __init__(self, row_index: int = 0, column_index: int = 0, text: str = "", **kwargs):
        super().__init__(row_index=row_index, column_index=column_index, text=text, **kwargs)
        self.add_path(
            "click_insert_table_cell_text",
            path=[
                *select_table_cell(row_index=row_index, column_index=column_index),
                WaitAction(duration=1.0),
                TypeAction(text=text if text is not None else "Sample Text", input_mode="copy_paste", thought=f"Type the text '{text}' into the selected table cell."),
                WaitAction(duration=4.0)
            ]
        )


@register("WordInsertShape")
class WordInsertShape(WordBaseAction):
    type: str = "word_insert_shape"
    shape_type: Argument = Argument(
        value=None,
        description="Name of the shape to insert."
    )

    descriptions: List[str] = [
        "Insert a ${{shape_type}} shape on the current document.",
        "Add a ${{shape_type}} shape on the current document.",
        "Create a ${{shape_type}} shape on the current document."
    ]

    def __init__(self, shape_type: str = None, **kwargs):
        super().__init__(shape_type=shape_type, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_insert_shape",
                path=[
                    HotKeyAction(keys=["alt", "n"], thought="Press Alt + N to switch to the Insert tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="s", thought="Press S and H to open the Shapes dropdown button. First press S."),
                    PressKeyAction(key="h", thought="Then press H to complete opening the Shapes dropdown button."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{shape_type if shape_type is not None else 'Rectangle'}' shape to select it."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click on any position on the slide to place the shape. You should click on an empty area on the slide to avoid overlapping with existing content."),
                    WaitAction(duration=4.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_insert_shape",
                path=[
                    SingleClickAction(thought="Click the 'Insert' tab to switch to the insert menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Shapes' dropdown button to open the shapes gallery."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{shape_type if shape_type is not None else 'Rectangle'}' shape to select it."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click on any position on the slide to place the shape. You should click on an empty area on the slide to avoid overlapping with existing content."),
                    WaitAction(duration=4.0)
                ]
            )


@register("WordMoveCursorToStart")
class WordMoveCursorToStart(WordBaseAction):
    type: str = "word_move_cursor_to_start"

    descriptions: List[str] = [
        "Move the cursor to the start of the document.",
        "Position the cursor at the beginning of the document.",
        "Place the cursor at the top of the document.",
        "Navigate to the start of the document.",
        "Set the cursor position to the beginning of the document."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "move_cursor_to_start",
            path=[
                HotKeyAction(keys=["ctrl", "home"], thought="Press Ctrl + Home to move the cursor to the start of the document."),
                WaitAction(duration=1.0)
            ]
        )

@register("WordMoveCursorLeftofText")
class WordMoveCursorLeftofText(WordBaseAction):
    type: str = "word_move_cursor_left_of_text"
    text_to_locate: Argument = Argument(
        value=None,
        description="Enter a description of the text you're looking for and provide surrounding context to help the grounding model accurately locate it. Since there may be multiple occurrences of the same text, include specific contextual details such as its position relative to headings, paragraphs, or other distinctive elements - for instance, you might specify 'the word example in the second paragraph after the heading Introduction' or 'the phrase data processing that appears in the bullet list under Key Features'."
    )

    descriptions: List[str] = [
        "Move the cursor to the left of the text described as: ${{text_to_locate}}.",
        "Position the cursor before the text matching this description: ${{text_to_locate}}.",
        "Place the cursor at the beginning of the text identified by: ${{text_to_locate}}.",
        "Navigate to the left side of the text located at: ${{text_to_locate}}.",
        "Set the cursor position before the text described by: ${{text_to_locate}}."
    ]

    def __init__(self, text_to_locate: str = None, **kwargs):
        super().__init__(text_to_locate=text_to_locate, **kwargs)
        self.add_path(
            "move_cursor_left_of_text",
            path=[
                DoubleClickAction(thought=f"Move the cursor to the center of the text described below: {text_to_locate} in the screen."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["left"]),
                WaitAction(duration=1.0)
            ]
        )


@register("WordMoveCursorRightofText")
class WordMoveCursorRightofText(WordBaseAction):
    type: str = "word_move_cursor_right_of_text"
    text_to_locate: Argument = Argument(
        value=None,
        description="Enter a description of the text you're looking for and provide surrounding context to help the grounding model accurately locate it. Since there may be multiple occurrences of the same text, include specific contextual details such as its position relative to headings, paragraphs, or other distinctive elements - for instance, you might specify 'the word example in the second paragraph after the heading Introduction' or 'the phrase data processing that appears in the bullet list under Key Features'."
    )

    descriptions: List[str] = [
        "Move the cursor to the right of the text described as: ${{text_to_locate}}.",
        "Position the cursor after the text matching this description: ${{text_to_locate}}.",
        "Place the cursor at the end of the text identified by: ${{text_to_locate}}.",
        "Navigate to the right side of the text located at: ${{text_to_locate}}.",
        "Set the cursor position after the text described by: ${{text_to_locate}}."
    ]

    def __init__(self, text_to_locate: str = None, **kwargs):
        super().__init__(text_to_locate=text_to_locate, **kwargs)
        self.add_path(
            "move_cursor_right_of_text",
            path=[
                DoubleClickAction(thought=f"Move the cursor to the center of the text described below: {text_to_locate} in the screen."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["right"]),
                WaitAction(duration=1.0)
            ]
        )


@register("WordSelectText")
class WordSelectText(WordBaseAction):
    type: str = "word_select_text"
    text_to_select: Argument = Argument(
        value=None,
        description="Enter a description of the text you're looking for and provide surrounding context to help the grounding model accurately locate it. Since there may be multiple occurrences of the same text, include specific contextual details such as its position relative to headings, paragraphs, or other distinctive elements - for instance, you might specify 'the word example in the second paragraph after the heading Introduction' or 'the phrase data processing that appears in the bullet list under Key Features'."
    )

    descriptions: List[str] = [
        "Select the text described as: ${{text_to_select}}.",
        "Highlight the text matching this description: ${{text_to_select}}.",
        "Choose the text identified by: ${{text_to_select}}.",
        "Mark the text located at: ${{text_to_select}}.",
        "Pick the text described by: ${{text_to_select}}."
    ]

    def __init__(self, text_to_select: str = None, **kwargs):
        super().__init__(text_to_select=text_to_select, **kwargs)
        self.add_path(
            "select_single_text",
            path=[
                DoubleClickAction(thought=f"Move the cursor to the center of the text described below: {text_to_select} in the screen."),
                WaitAction(duration=1.0)
            ]
        )


@register("WordSelectSentenceWithTheText")
class WordSelectSentenceWithTheText(WordBaseAction):
    type: str = "word_select_sentence_with_the_text"
    text_in_line_to_select: Argument = Argument(
        value=None,
        description="Enter a description of the text you're looking for and provide surrounding context to help the grounding model accurately locate it. Since there may be multiple occurrences of the same text, include specific contextual details such as its position relative to headings, paragraphs, or other distinctive elements - for instance, you might specify 'the word example in the second paragraph after the heading Introduction' or 'the phrase data processing that appears in the bullet list under Key Features'."
    )

    descriptions: List[str] = [
        "Select the sentence containing the text described as: ${{text_in_line_to_select}}.",
        "Highlight the sentence with the text matching this description: ${{text_in_line_to_select}}.",
        "Choose the sentence that includes the text identified by: ${{text_in_line_to_select}}.",
        "Mark the entire sentence containing the text located at: ${{text_in_line_to_select}}.",
        "Pick the sentence with the text described by: ${{text_in_line_to_select}}."
    ]

    def __init__(self, text_in_line_to_select: str = None, **kwargs):
        super().__init__(text_in_line_to_select=text_in_line_to_select, **kwargs)
        self.add_path(
            "select_sentence_with_the_text",
            path=[
                SingleClickAction(thought=f"Move the cursor to anywhere in the line that contains the text described below: {text_in_line_to_select} in the screen.", modifiers=["ctrl"]),
                WaitAction(duration=1.0)
            ]
        )


@register("WordSelectParagraphWithTheText")
class WordSelectParagraphWithTheText(WordBaseAction):
    type: str = "word_select_paragraph_with_the_text"
    text_in_paragraph_to_select: Argument = Argument(
        value=None,
        description="Enter a description of the text you're looking for and provide surrounding context to help the grounding model accurately locate it. Since there may be multiple occurrences of the same text, include specific contextual details such as its position relative to headings, paragraphs, or other distinctive elements - for instance, you might specify 'the word example in the second paragraph after the heading Introduction' or 'the phrase data processing that appears in the bullet list under Key Features'."
    )

    descriptions: List[str] = [
        "Select the paragraph containing the text described as: ${{text_in_paragraph_to_select}}.",
        "Highlight the paragraph with the text matching this description: ${{text_in_paragraph_to_select}}.",
        "Choose the paragraph that includes the text identified by: ${{text_in_paragraph_to_select}}.",
        "Mark the entire paragraph containing the text located at: ${{text_in_paragraph_to_select}}.",
        "Pick the paragraph with the text described by: ${{text_in_paragraph_to_select}}."
    ]

    def __init__(self, text_in_paragraph_to_select: str = None, **kwargs):
        super().__init__(text_in_paragraph_to_select=text_in_paragraph_to_select, **kwargs)
        self.add_path(
            "select_paragraph_with_the_text",
            path=[
                TripleClickAction(thought=f"Move the cursor to anywhere in the paragraph that contains the text described below: {text_in_paragraph_to_select} in the screen."),
                WaitAction(duration=1.0)
            ]
        )


@register("WordSelectLineWithTheText")
class WordSelectLineWithTheText(WordBaseAction):
    type: str = "word_select_line_with_the_text"
    text_in_line_to_select: Argument = Argument(
        value=None,
        description="Enter a description of the text you're looking for and provide surrounding context to help the grounding model accurately locate it. Since there may be multiple occurrences of the same text, include specific contextual details such as its position relative to headings, paragraphs, or other distinctive elements - for instance, you might specify 'the word example in the second paragraph after the heading Introduction' or 'the phrase data processing that appears in the bullet list under Key Features'."
    )

    descriptions: List[str] = [
        "Select the line containing the text described as: ${{text_in_line_to_select}}.",
        "Highlight the line with the text matching this description: ${{text_in_line_to_select}}.",
        "Choose the line that includes the text identified by: ${{text_in_line_to_select}}.",
        "Mark the entire line containing the text located at: ${{text_in_line_to_select}}.",
        "Pick the line with the text described by: ${{text_in_line_to_select}}."
    ]

    def __init__(self, text_in_line_to_select: str = None, **kwargs):
        super().__init__(text_in_line_to_select=text_in_line_to_select, **kwargs)
        self.add_path(
            "select_line_with_the_text",
            path=[
                SingleClickAction(thought=f"Move the cursor to the center of the text described below: {text_in_line_to_select} in the screen."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["home"]),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["shift", "end"]),
                WaitAction(duration=1.0)
            ]
        )


@register("WordSelectKWordsRightOfCursor")
class WordSelectKWordsRightOfCursor(WordBaseAction):
    type: str = "word_select_k_words_right_of_cursor"
    num_of_words_to_select: Argument = Argument(
        value=1,
        description="Number of words to select to the right of the current cursor position. It will perform ctrl + shift + right arrow (number of words) key presses accordingly."
    )

    descriptions: List[str] = [
        "Select ${{num_of_words_to_select}} words to the right of the cursor.",
        "Highlight the next ${{num_of_words_to_select}} words.",
        "Choose ${{num_of_words_to_select}} words after the cursor position.",
        "Mark ${{num_of_words_to_select}} words to the right.",
        "Pick the following ${{num_of_words_to_select}} words."
    ]

    def __init__(self, num_of_words_to_select: int = 1, **kwargs):
        super().__init__(num_of_words_to_select=num_of_words_to_select, **kwargs)
        self.add_path(
            "select_k_words_right_of_cursor",
            path=[
                KeyDownAction(key="ctrl"),
                KeyDownAction(key="shift"),
                PressKeyAction(key="right", presses=num_of_words_to_select, interval=0.1),
                KeyUpAction(key="ctrl"),
                KeyUpAction(key="shift"),
                WaitAction(duration=1.0)
            ]
        )


@register("WordSelectKWordsLeftOfCursor")
class WordSelectKWordsLeftOfCursor(WordBaseAction):
    type: str = "word_select_k_words_left_of_cursor"
    num_of_words_to_select: Argument = Argument(
        value=1,
        description="Number of words to select to the left of the current cursor position. It will perform ctrl + shift + left arrow (number of words) key presses accordingly."
    )

    descriptions: List[str] = [
        "Select ${{num_of_words_to_select}} words to the left of the cursor.",
        "Highlight the previous ${{num_of_words_to_select}} words.",
        "Choose ${{num_of_words_to_select}} words before the cursor position.",
        "Mark ${{num_of_words_to_select}} words to the left.",
        "Pick the preceding ${{num_of_words_to_select}} words."
    ]

    def __init__(self, num_of_words_to_select: int = 1, **kwargs):
        super().__init__(num_of_words_to_select=num_of_words_to_select, **kwargs)
        self.add_path(
            "select_k_words_left_of_cursor",
            path=[
                KeyDownAction(key="ctrl"),
                KeyDownAction(key="shift"),
                PressKeyAction(key="left", presses=num_of_words_to_select, interval=0.1),
                KeyUpAction(key="ctrl"),
                KeyUpAction(key="shift"),
                WaitAction(duration=1.0)
            ]
        )


@register("WordFindReplace")
class WordFindReplace(WordBaseAction):
    type: str = "word_find_replace"
    find_text: Argument = Argument(
        value=None,
        description="Text to find in the document."
    )
    replace_text: Argument = Argument(
        value=None,
        description="Text to replace the found text with."
    )

    descriptions: List[str] = [
        "Replace ${{find_text}} with ${{replace_text}}.",
        "Find ${{find_text}} and change to ${{replace_text}}.",
        "Swap ${{find_text}} for ${{replace_text}}.",
        "Do a find and replace: ${{find_text}} → ${{replace_text}}.",
        "Change all ${{find_text}} to ${{replace_text}}."
    ]

    def __init__(self, find_text: str = None, replace_text: str = None, **kwargs):
        super().__init__(find_text=find_text, replace_text=replace_text, **kwargs)
        
        # Ctrl + H opens the Find and Replace dialog in Word
        self.add_path(
            "hotkey_find_replace",
            path=[
                HotKeyAction(keys=["ctrl", "h"], thought="Press Ctrl + H to open the Find and Replace dialog."),
                WaitAction(duration=2.0),
                
                # The cursor is in the 'Find what' field by default
                HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select any existing text in the Find field."),
                WaitAction(duration=0.5),
                TypeAction(text=find_text if find_text is not None else "", input_mode="copy_paste", thought=f"Type the text to find: '{find_text}'."),
                WaitAction(duration=1.0),
                
                # Tab to move to the 'Replace with' field
                PressKeyAction(key="tab", thought="Press Tab to move to the 'Replace with' field."),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select any existing text in the Replace field."),
                WaitAction(duration=0.5),
                TypeAction(text=replace_text if replace_text is not None else "", input_mode="copy_paste", thought=f"Type the replacement text: '{replace_text}'."),
                WaitAction(duration=1.0),
                
                # Alt + A to Replace All
                HotKeyAction(keys=["alt", "a"], thought="Press Alt + A to replace all occurrences."),
                WaitAction(duration=2.0),
                
                # Press Escape to close the dialog
                HotKeyAction(keys=["esc"], thought="Press Escape to close the Find and Replace dialog."),
                WaitAction(duration=1.0)
            ]
        )


@register("WordInsertComment")
class WordInsertComment(WordBaseAction):
    type: str = "word_insert_comment"
    comment: Argument = Argument(
        value=None,
        description="Comment text to insert."
    )

    descriptions: List[str] = [
        "Insert a comment: ${{comment}}.",
        "Add comment ${{comment}} here.",
        "Leave a note: ${{comment}}.",
        "Comment ${{comment}} on selection.",
        "Attach comment ${{comment}}."
    ]

    def __init__(self, comment: str = None, **kwargs):
        super().__init__(comment=comment, **kwargs)
        
        # Alt + R, C opens the Review tab and inserts a new comment
        self.add_path(
            "hotkey_insert_comment",
            path=[
                HotKeyAction(keys=["alt", "r"], thought="Press Alt + R to switch to the Review tab."),
                WaitAction(duration=1.0),
                PressKeyAction(key="c", thought="Press C to insert a new comment."),
                WaitAction(duration=2.0),
                
                # Type the comment text
                TypeAction(text=comment if comment is not None else "", input_mode="copy_paste", thought=f"Type the comment text: '{comment}'."),
                WaitAction(duration=1.0),
                
                # Click outside or press Escape to finish the comment
                HotKeyAction(keys=["esc"], thought="Press Escape to finish editing the comment."),
                WaitAction(duration=1.0)
            ]
        )


@register("WordToggleTrackChanges")
class WordToggleTrackChanges(WordBaseAction):
    type: str = "word_toggle_track_changes"

    descriptions: List[str] = [
        "Toggle Track Changes.",
        "Turn Track Changes on or off.",
        "Enable/disable revision tracking.",
        "Switch Track Changes state.",
        "Toggle revision mode."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Ctrl + Shift + E toggles Track Changes in Word
        self.add_path(
            "hotkey_toggle_track_changes",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "e"], thought="Press Ctrl + Shift + E to toggle Track Changes on or off."),
                WaitAction(duration=1.0)
            ]
        )
