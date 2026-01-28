import os
from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, RightClickAction, PressKeyAction, KeyDownAction, KeyUpAction
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

use_hotkey = True
use_mouse_click = False

assert not (use_hotkey and use_mouse_click), "Only one of `use_hotkey` and `use_mouse_click` can be True."
assert not (not use_hotkey and not use_mouse_click), "At least one of `use_hotkey` and `use_mouse_click` must be True."


class PowerPointBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="powerpoint",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="PowerPoint",
        description="The name of the PowerPoint application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("PowerPointLaunch")
class PowerPointLaunch(PowerPointBaseAction):
    type: str = "powerpoint_launch"

    descriptions: List[str] = [
        "Open PowerPoint.",
        "Launch PowerPoint.",
        "Start PowerPoint.",
        "Open the PowerPoint.",
        "Launch the PowerPoint.",
        "Start the PowerPoint."
    ]

    def __init__(self, **kwargs):
        super().__init__(application_name=self.application_name, **kwargs)
        self.add_path(
            "launch_powerpoint",
            path=[
                LaunchApplication(application_name="Windows PowerShell"),
                WaitAction(duration=3.0),
                TypeAction(text="Start-Process powerpnt", thought="Type the command 'Start-Process powerpnt' to start PowerPoint application."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to execute the command."),
                WaitAction(duration=4.0, thought="Wait for a few seconds to let PowerPoint launch."),
            ]
        )


@register("PowerPointCreateBlankNewPresentation")
class PowerPointCreateBlankNewPresentation(PowerPointBaseAction):
    type: str = "powerpoint_create_new_blank_presentation"

    descriptions: List[str] = [
        "Create a new presentation.",
        "Start a new presentation.",
        "Open a new presentation.",
        "Create a new PowerPoint presentation.",
        "Start a new PowerPoint presentation.",
        "Open a new PowerPoint presentation."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # This assumes we are on the main page of PowerPoint, not in an existing presentation
        # TODO: if we know that we are in an existing presentation, we can do hotkey Ctrl + N to create a new presentation directly
        self.add_path(
            "click_create_blank_presentation",
            path=[
                SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'New Blank Presentation' button to create a new presentation."),
                WaitAction(duration=3.0),

                HotKeyAction(keys=["esc"], thought="Press Escape to close any pop-up dialogs that may appear after opening the file."),
                WaitAction(duration=1.0)
            ]
        )


@register("PowerPointCreateNewPresentationWithCopilot")
class PowerPointCreateNewPresentationWithCopilot(PowerPointBaseAction):
    type: str = "powerpoint_create_new_presentation_with_copilot"
    copilot_instruction: Argument = Argument(
        value="Create a presentation about AI.",
        description="Instruction to give to Copilot for creating the presentation."
    )

    descriptions: List[str] = [
        "Create a new presentation via Copilot with instruction ${{copilot_instruction}}.",
        "Start a new presentation via Copilot with instruction ${{copilot_instruction}}.",
        "Open a new presentation via Copilot with instruction ${{copilot_instruction}}.",
        "Create a new PowerPoint presentation via Copilot with instruction ${{copilot_instruction}}.",
        "Start a new PowerPoint presentation via Copilot with instruction ${{copilot_instruction}}.",
        "Open a new PowerPoint presentation via Copilot with instruction ${{copilot_instruction}}."
    ]

    def __init__(self, copilot_instruction: str = None, **kwargs):
        super().__init__(copilot_instruction=copilot_instruction, **kwargs)
        # No keyboard shortcut for this operation
        self.add_path(
            "click_create_with_copilot",
            path=[
                SingleClickAction(thought="Click the 'New' tab to ensure we are on the main screen."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Create with Copilot' button to create a new presentation using Copilot."),
                WaitAction(duration=1.0),
                WaitAction(duration=3.0, thought="Wait for the Copilot pane to load."),
                SingleClickAction(thought="Click on the Copilot instruction text area to focus."),
                WaitAction(duration=1.0),
                TypeAction(text=copilot_instruction if copilot_instruction is not None else "Create a presentation about AI.", thought=f"Type the instruction to Copilot: {copilot_instruction if copilot_instruction is not None else 'Create a presentation about AI.'}"),
                HotKeyAction(keys=["enter"], thought="Press Enter to submit the instruction to Copilot."),
                WaitAction(duration=20.0, thought="Wait for a few seconds to let Copilot process the instruction."),
                SingleClickAction(thought="Click the 'Generate Slides' button to let Copilot create the presentation."),
                WaitAction(duration=20.0, thought="Wait for a few seconds to let Copilot generate the presentation."),
                WaitAction(duration=4.0, thought="Wait for a few more seconds to ensure the presentation is fully loaded."),

                HotKeyAction(keys=["esc"], thought="Press Escape to close any pop-up dialogs that may appear after opening the file."),
                WaitAction(duration=1.0)
            ]
        )


@register("PowerPointCreateNewPresentationFromTemplate")
class PowerPointCreateNewPresentationFromTemplate(PowerPointBaseAction):
    type: str = "powerpoint_create_new_presentation_from_template"
    template_name: Argument = Argument(
        value=None,
        description="Name of the template to use for the new presentation."
    )

    descriptions: List[str] = [
        "Create a new presentation from template ${{template_name}}.",
        "Start a new presentation from template ${{template_name}}.",
        "Open a new presentation from template ${{template_name}}.",
        "Create a new PowerPoint presentation from template ${{template_name}}.",
        "Start a new PowerPoint presentation from template ${{template_name}}.",
        "Open a new PowerPoint presentation from template ${{template_name}}."
    ]

    def __init__(self, template_name: str = None, **kwargs):
        super().__init__(template_name=template_name, **kwargs)
        # No keyboard shortcut for this operation
        self.add_path(
            "click_create_from_template",
            path=[
                SingleClickAction(thought="Click the 'New' tab to ensure we are on the main screen."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Search for online templates and themes' field to search for a target template."),
                WaitAction(duration=1.0),
                TypeAction(text=template_name if template_name is not None else "Blank", thought=f"Type the {template_name if template_name is not None else 'Blank'} to search for the template."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to search for the template."),
                WaitAction(duration=3.0, thought="Wait for a few seconds to let PowerPoint show the search results."),
                SingleClickAction(thought=f"Click on the target template '{template_name if template_name is not None else 'Blank'}' to select it."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Create' button to create a new presentation from the selected template."),
                WaitAction(duration=4.0, thought="Wait for a few seconds to let PowerPoint create the presentation."),

                HotKeyAction(keys=["ctrl", "space"], thought="Since now the Help pane may appear on the right side, press Ctrl + Space to open the menu."),
                WaitAction(duration=1.0),
                PressKeyAction(key="c", thought="Press C to close the Help pane."),
                WaitAction(duration=1.0),

                HotKeyAction(keys=["esc"], thought="Press Escape to close any pop-up dialogs that may appear after opening the file."),
                WaitAction(duration=1.0)
            ]
        )


@register("PowerPointNamePresentation")
class PowerPointNamePresentation(PowerPointBaseAction):
    type: str = "powerpoint_name_presentation"
    filename: Argument = Argument(
        value=None,
        description="Name of the presentation file."
    )

    descriptions: List[str] = [
        "Name the powerpoint file as ${{filename}}.",
        "Set powerpoint file name to ${{filename}}.",
        "Rename the deck file to ${{filename}}.",
        "Call the file ${{filename}}.",
        "Use ${{filename}} as the presentation file name."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)
        # In some version of PowerPoint, clicking the presentation name area does not respond
        # self.add_path(
        #     "click_presentation_name",
        #     path=[
        #         SingleClickAction(thought="Click the presentation file name area at the top of the powerpoint window to focus. It typically shows a temporary name like 'Presentation1' if the file is not yet saved."),
        #         WaitAction(duration=1.0),
        #         TypeAction(text=filename if filename is not None else "My Presentation", input_mode="copy_paste", thought=f"Type the file name '{filename if filename is not None else 'My Presentation'}'."),
        #         WaitAction(duration=1.0),
        #         HotKeyAction(keys=["enter"], thought="Press Enter to confirm the new presentation file name."),
        #         WaitAction(duration=3.0)
        #     ]
        # )
        self.add_path(
            "hotkey_presentation_name",
            path=[
                HotKeyAction(keys=["f12"], thought="Press F12 to open the Save As dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=filename if filename is not None else "My Presentation.pptx", input_mode="copy_paste", thought=f"Type the file name '{filename if filename is not None else 'My Presentation.pptx'}' to save as."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointOpenFile")
class PowerPointOpenFile(PowerPointBaseAction):
    type: str = "powerpoint_open_file"
    filename: Argument = Argument(
        value=None,
        description="Name of the presentation file."
    )

    descriptions: List[str] = [
        "Open presentation '${{filename}}'.",
        "Load the file '${{filename}}' in PowerPoint.",
        "Open deck '${{filename}}'.",
        "Open the .pptx file '${{filename}}'.",
        "Open '${{filename}}' presentation."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)

        # We open the file via PowerShell to avoid issues with different PowerPoint versions
        self.add_path(
            "powershell_open_file",
            path=[
                LaunchApplication(application_name="Windows PowerShell"),
                WaitAction(duration=3.0),
                TypeAction(text=f"Start-Process \"{filename}\"", thought=f"Type the command 'Start-Process \"{filename}\"' to start PowerPoint application."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to execute the command."),
                WaitAction(duration=4.0, thought="Wait for a few seconds to let PowerPoint launch.")
            ]
        )


@register("PowerPointSave")
class PowerPointSave(PowerPointBaseAction):
    type: str = "powerpoint_save"
    filename: Argument = Argument(
        value=None,
        description="Name of the presentation file."
    )

    descriptions: List[str] = [
        "Save the presentation with the current name.",
        "Save the current file using the current name.",
        "Save the current deck with the current name.",
        "Save the current ppt file using the current name.",
        "Save the presentation as ${{filename}}.",
        "Save the file as ${{filename}}.",
        "Save the deck as ${{filename}}.",
        "Save the .pptx file as ${{filename}}.",
        "Save the presentation with name ${{filename}}."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)
        self.add_path(
            "hotkey_save_file",
            path=[
                HotKeyAction(keys=["ctrl", "s"], thought="Press Ctrl + S to open the Save dialog."),
                WaitAction(duration=3.0),
                TypeAction(text=filename if filename is not None else "My Presentation.pptx", input_mode="copy_paste", thought=f"Type the file name '{filename if filename is not None else 'My Presentation.pptx'}' to save."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointSaveAs")
class PowerPointSaveAs(PowerPointBaseAction):
    type: str = "powerpoint_save_as"
    filename: Argument = Argument(
        value=None,
        description="Name of the presentation file."
    )

    descriptions: List[str] = [
        "Save the presentation as ${{filename}}.",
        "Save the file as ${{filename}}.",
        "Save the deck as ${{filename}}.",
        "Save the .pptx file as ${{filename}}."
    ]

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(filename=filename, **kwargs)
        self.add_path(
            "hotkey_save_as_file",
            path=[
                HotKeyAction(keys=["f12"], thought="Press F12 to open the Save As dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=filename, input_mode="copy_paste", thought=f"Type the file name '{filename}' to save as."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointAddSlide")
class PowerPointAddSlide(PowerPointBaseAction):
    type: str = "powerpoint_add_slide"
    slide_layout: Argument = Argument(
        value=None,
        description="Layout of the new slide to be added."
    )

    descriptions: List[str] = [
        "Add a new slide.",
        "Insert a new slide.",
        "Create a new slide.",
        "Add a new slide with layout as ${{slide_layout}}.",
        "Insert a new slide with layout as ${{slide_layout}}.",
        "Create a new slide with layout as ${{slide_layout}}."
    ]

    def __init__(self, slide_layout: str = None, **kwargs):
        super().__init__(slide_layout=slide_layout, **kwargs)
        
        if slide_layout is not None:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_add_new_slide_with_layout",
                    path=[
                        HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                        WaitAction(duration=1.0),
                        PressKeyAction(key="i", thought="Press I to open the New Slide dropdown menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought=f"Click on the '{slide_layout}' layout to add a new slide with that layout."),
                        WaitAction(duration=3.0)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_add_new_slide_with_layout",
                    path=[
                        SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'New Slide' button to open the dropdown menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought=f"Click on the '{slide_layout}' layout to add a new slide with that layout."),
                        WaitAction(duration=3.0)
                    ]
                )
        else:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_add_new_slide",
                    path=[
                        HotKeyAction(keys=["ctrl", "m"], thought="Press Ctrl + M to add a new slide."),
                        WaitAction(duration=3.0)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_add_new_slide",
                    path=[
                        SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'New Slide' button to add a new slide."),
                        WaitAction(duration=3.0)
                    ]
                )


@register("PowerPointChangeLayout")
class PowerPointChangeLayout(PowerPointBaseAction):
    type: str = "powerpoint_change_layout"
    slide_layout: Argument = Argument(
        value=None,
        description="Layout to change the current slide to."
    )

    descriptions: List[str] = [
        "Change the layout of the current slide to ${{slide_layout}}.",
        "Set the layout of the current slide to ${{slide_layout}}.",
        "Modify the layout of the current slide to ${{slide_layout}}."
    ]

    def __init__(self, slide_layout: str = None, **kwargs):
        super().__init__(slide_layout=slide_layout, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_change_slide_layout",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="l", thought="Press L to open the Layout dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{slide_layout}' layout to change the current slide to that layout."),
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_change_slide_layout",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Layout' button to open the dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{slide_layout}' layout to change the current slide to that layout."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointDeleteSlide")
class PowerPointDeleteSlide(PowerPointBaseAction):
    type: str = "powerpoint_delete_slide"

    descriptions: List[str] = [
        "Delete the current slide.",
        "Remove the current slide.",
        "Delete the current slide from the presentation.",
        "Remove the current slide from the presentation."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # No good keyboard shortcut for this operation (the main challenge comes from focusing on the slide thumbnail on the left sidebar)
        self.add_path(
            "click_delete_slide",
            path=[
                SingleClickAction(thought="Click the thumbnail of the current slide in the left sidebar to select it."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["delete"], thought="Press the Delete key to delete the selected slide."),
                WaitAction(duration=3.0)
            ]
        )


def place_textbox_at_position(position: str) -> List[BaseAction]:
    """
    Generate a sequence of actions to place a textbox at a specific position on the slide.
    This is after we place the textbox in the middle of the slide
    """
    path = [
        HotKeyAction(keys=["esc"], thought="Press Escape to exit the focus inside the textbox."),
        WaitAction(duration=1.0)
    ]
    if "top" in position.lower():
        path.extend([
            PressKeyAction(key="up", presses=30, interval=0.1, thought="Press the Up arrow key to move the textbox upwards."),
            WaitAction(duration=3.0)
        ])
    elif "bottom" in position.lower():
        path.extend([
            PressKeyAction(key="down", presses=30, interval=0.1, thought="Press the Down arrow key to move the textbox downwards."),
            WaitAction(duration=3.0)
        ])
    
    if "left" in position.lower():
        path.extend([
            PressKeyAction(key="left", presses=40, interval=0.1, thought="Press the Left arrow key to move the textbox leftwards."),
            WaitAction(duration=3.0)
        ])
    elif "right" in position.lower():
        path.extend([
            PressKeyAction(key="right", presses=40, interval=0.1, thought="Press the Right arrow key to move the textbox rightwards."),
            WaitAction(duration=3.0)
        ])
    
    # we want to increase the width of the text box
    path.extend([
        KeyDownAction(key="shift", thought="Hold down the Shift key to resize the textbox proportionally."),
        PressKeyAction(key="right", presses=15, interval=0.1, thought="Press the Right arrow key to increase the width of the textbox."),
        KeyUpAction(key="shift", thought="Release the Shift key after resizing the textbox."),
        WaitAction(duration=3.0)
    ])
    
    return path


@register("PowerPointInsertText")
class PowerPointInsertText(PowerPointBaseAction):
    type: str = "powerpoint_insert_text"
    text: Argument = Argument(
        value=None,
        description="Text to insert into the slide."
    )
    textbox_position: Argument = Argument(
        value=None,
        description="Position to insert the text box."
    )

    descriptions: List[str] = [
        "Insert text '${{text}}' on the current slide.",
        "Add text box '${{text}}' on the current slide.",
        "Insert text '${{text}}' at position ${{textbox_position}} on the current slide.",
        "Add text box '${{text}}' at position ${{textbox_position}} on the current slide."
    ]

    def __init__(self, text: str = None, textbox_position: str = None, **kwargs):
        super().__init__(text=text, textbox_position=textbox_position, **kwargs)

        if textbox_position is not None:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_insert_textbox",
                    path=[
                        HotKeyAction(keys=["alt", "n"], thought="Press Alt + N to switch to the Insert tab."),
                        WaitAction(duration=1.0),
                        PressKeyAction(key="x", thought="Press X to select the Text Box tool."),
                        WaitAction(duration=1.0),
                        
                        # Does not need to specify horizontal or vertical text box in the WAA version
                        # TODO: take a powerpoint version as input, and judge whether need to specify horizontal or vertical text box based on the powerpoint version
                        # PressKeyAction(key="h", thought="Press H to select horizontal text box."),
                        # WaitAction(duration=1.0),
                        
                        TypeAction(text=text if text is not None else "Sample Text", input_mode="keyboard", thought=f"Type the text '{text if text is not None else 'Sample Text'}' into the text box."),
                        WaitAction(duration=3.0),

                        *place_textbox_at_position(textbox_position)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_insert_textbox",
                    path=[
                        SingleClickAction(thought="Click the 'Insert' tab to switch to the insert menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Text Box' button (not the dropdown menu) to insert a new text box."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought=f"Click on the '{textbox_position}' area on the current displayed slide to place the text box. You should click on an empty area on the slide to avoid overlapping with existing content."),
                        WaitAction(duration=1.0),
                        TypeAction(text=text if text is not None else "Sample Text", input_mode="copy_paste", thought=f"Type the text '{text if text is not None else 'Sample Text'}' into the text box."),
                        WaitAction(duration=3.0)
                    ]
                )
        else:
            if use_hotkey:
                # We prefer using keyboard shortcuts than mouse clicks
                self.add_path(
                    "hotkey_insert_textbox",
                    path=[
                        HotKeyAction(keys=["alt", "n"], thought="Press Alt + N to switch to the Insert tab."),
                        WaitAction(duration=1.0),
                        PressKeyAction(key="x", thought="Press X to select the Text Box tool."),
                        WaitAction(duration=1.0),
                        
                        # Does not need to specify horizontal or vertical text box in the WAA version
                        # TODO: take a powerpoint version as input, and judge whether need to specify horizontal or vertical text box based on the powerpoint version
                        # PressKeyAction(key="h", thought="Press H to select horizontal text box."),
                        # WaitAction(duration=1.0),
                        
                        TypeAction(text=text if text is not None else "Sample Text", input_mode="copy_paste", thought=f"Type the text '{text if text is not None else 'Sample Text'}' into the text box."),
                        WaitAction(duration=3.0)
                    ]
                )
            
            if use_mouse_click:
                self.add_path(
                    "click_insert_textbox",
                    path=[
                        SingleClickAction(thought="Click the 'Insert' tab to switch to the insert menu."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click the 'Text Box' button (not the dropdown menu) to insert a new text box."),
                        WaitAction(duration=1.0),
                        SingleClickAction(thought="Click any place on the slide to place the text box. You should click on an empty area on the slide to avoid overlapping with existing content."),
                        WaitAction(duration=1.0),
                        TypeAction(text=text if text is not None else "Sample Text", input_mode="copy_paste", thought=f"Type the text '{text if text is not None else 'Sample Text'}' into the text box."),
                        WaitAction(duration=3.0)
                    ]
                )


@register("PowerPointInsertImage")
class PowerPointInsertImage(PowerPointBaseAction):
    type: str = "powerpoint_insert_image"
    image_path: Argument = Argument(
        value=None,
        description="Path to the image file to insert."
    )

    descriptions: List[str] = [
        "Insert an image from path '${{image_path}}' into the current slide.",
        "Add an image from path '${{image_path}}' to the current slide.",
        "Insert a picture from path '${{image_path}}' into the current slide.",
        "Add a picture from path '${{image_path}}' to the current slide."
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
                    PressKeyAction(key="p", thought="Press P and 1 to open the Pictures dropdown menu. First press P."),
                    PressKeyAction(key="1", thought="Then press 1 to complete the opening of the Pictures dropdown menu."),
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
                    WaitAction(duration=4.0, thought="Wait for a few seconds to let PowerPoint insert the image."),
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
                    
                    SingleClickAction(thought="Click the folder path input area at the top of the browse dialog to focus. You should click on the empty area in the input box (after the existing folder names, the area between the last '>' and drop down menu icon 'v') to place the cursor."),
                    WaitAction(duration=1.0),
                    TypeAction(text=os.path.dirname(image_path), input_mode="copy_paste", thought=f"Type the path to the folder containing the file to open, '{os.path.dirname(image_path)}'."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm the folder path."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the file name input area at the bottom of the browse dialog to focus."),
                    TypeAction(text=os.path.basename(image_path), input_mode="copy_paste", thought=f"Type the file name '{os.path.basename(image_path)}' to open."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and insert the image."),
                    WaitAction(duration=4.0, thought="Wait for a few seconds to let PowerPoint insert the image."),
                ]
            )


@register("PowerPointStartPresentation")
class PowerPointStartPresentation(PowerPointBaseAction):
    type: str = "powerpoint_start_presentation"

    descriptions: List[str] = [
        "Start the slideshow from the beginning.",
        "Begin the presentation from the first slide.",
        "Start presenting from the first slide.",
        "Start the slideshow."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_start_presentation",
            path=[
                HotKeyAction(keys=["f5"], thought="Press F5 to start the presentation from the beginning."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointGotoSlidePresentationMode")
class PowerPointGotoSlidePresentationMode(PowerPointBaseAction):
    type: str = "powerpoint_goto_slide_presentation_mode"
    slide_index: Argument = Argument(
        value=None,
        description="Index of the slide to go to."
    )

    descriptions: List[str] = [
        "Go to slide number ${{slide_index}}.",
        "Navigate to slide number ${{slide_index}}.",
        "Jump to slide number ${{slide_index}}.",
        "Go to slide ${{slide_index}}.",
        "Navigate to slide ${{slide_index}}.",
        "Jump to slide ${{slide_index}}."
    ]

    def __init__(self, slide_index: int = None, **kwargs):
        super().__init__(slide_index=slide_index, **kwargs)

        type_number_path = []
        for digit in str(slide_index):
            type_number_path.append(PressKeyAction(key=digit, thought=f"Type the digit '{digit}' of the slide number."))
            type_number_path.append(WaitAction(duration=2.0))

        self.add_path(
            "goto_slide_presentation_mode",
            path=type_number_path + [
                HotKeyAction(keys=["enter"], thought="Press Enter to navigate to the specified slide."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointNextSlidePresentationMode")
class PowerPointNextSlidePresentationMode(PowerPointBaseAction):
    type: str = "powerpoint_next_slide_presentation_mode"

    descriptions: List[str] = [
        "Go to next slide.",
        "Advance one slide.",
        "Move forward a slide.",
        "Next slide please.",
        "Show the following slide."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "next_slide_presentation_mode",
            path=[
                HotKeyAction(keys=["right"], thought="Press the Right Arrow key to go to the next slide."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointPreviousSlidePresentationMode")
class PowerPointPreviousSlidePresentationMode(PowerPointBaseAction):
    type: str = "powerpoint_previous_slide_presentation_mode"

    descriptions: List[str] = [
        "Go to previous slide.",
        "Move back one slide.",
        "Return to the prior slide.",
        "Back to last slide.",
        "Show the previous slide."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "previous_slide_presentation_mode",
            path=[
                HotKeyAction(keys=["left"], thought="Press the Left Arrow key to go to the previous slide."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointEndPresentation")
class PowerPointEndPresentation(PowerPointBaseAction):
    type: str = "powerpoint_end_presentation"

    descriptions: List[str] = [
        "End the slideshow.",
        "Exit presentation mode.",
        "Stop the slideshow.",
        "Leave full-screen presentation.",
        "Close the presentation view."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "end_presentation",
            path=[
                HotKeyAction(keys=["esc"], thought="Press the Escape key to end the presentation and exit slideshow mode."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointGotoSlideEditingMode")
class PowerPointGotoSlideEditingMode(PowerPointBaseAction):
    type: str = "powerpoint_goto_slide_editing_mode"
    slide_index: Argument = Argument(
        value=None,
        description="Index of the slide to go to."
    )

    descriptions: List[str] = [
        "Go to slide number ${{slide_index}}.",
        "Navigate to slide number ${{slide_index}}.",
        "Jump to slide number ${{slide_index}}.",
        "Go to slide ${{slide_index}}.",
        "Navigate to slide ${{slide_index}}.",
        "Jump to slide ${{slide_index}}."
    ]

    def __init__(self, slide_index: int = None, **kwargs):
        super().__init__(slide_index=slide_index, **kwargs)

        type_number_path = []
        for digit in str(slide_index):
            type_number_path.append(PressKeyAction(key=digit, thought=f"Type the digit '{digit}' of the slide number."))
            type_number_path.append(WaitAction(duration=2.0))

        self.add_path(
            "goto_slide_editing_mode",
            path=[
                # first enter slideshow mode
                HotKeyAction(keys=["f5"], thought="Press F5 to get into slideshow mode."),
                WaitAction(duration=1.0),
                *type_number_path,
                HotKeyAction(keys=["enter"], thought="Press Enter to navigate to the specified slide in slideshow mode."),
                WaitAction(duration=1.0),
                # then exit slideshow mode
                HotKeyAction(keys=["esc"], thought="Press the Escape key to exit slideshow mode and return to edit mode."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointNextSlideEditingMode")
class PowerPointNextSlideEditingMode(PowerPointBaseAction):
    type: str = "powerpoint_next_slide_editing_mode"

    descriptions: List[str] = [
        "Go to next slide.",
        "Advance one slide.",
        "Move forward a slide.",
        "Next slide please.",
        "Show the following slide."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # No good keyboard shortcut for this operation (the main challenge comes from focusing on the slide thumbnail on the left sidebar)
        self.add_path(
            "next_slide_editing_mode",
            path=[
                SingleClickAction(thought="Click the thumbnail of the current slide in the left sidebar to select it."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["pagedown"], thought="Press the Page Down key to go to the next slide."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointPreviousSlideEditingMode")
class PowerPointPreviousSlideEditingMode(PowerPointBaseAction):
    type: str = "powerpoint_previous_slide_editing_mode"

    descriptions: List[str] = [
        "Go to previous slide.",
        "Move back one slide.",
        "Return to the prior slide.",
        "Back to last slide.",
        "Show the previous slide."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # No good keyboard shortcut for this operation (the main challenge comes from focusing on the slide thumbnail on the left sidebar)
        self.add_path(
            "previous_slide_editing_mode",
            path=[
                SingleClickAction(thought="Click the thumbnail of the current slide in the left sidebar to select it."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["pageup"], thought="Press the Page Up key to go to the previous slide."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointAddTransition")
class PowerPointAddTransition(PowerPointBaseAction):
    type: str = "powerpoint_add_transition"
    transition_name: Argument = Argument(
        value=None,
        description="Name of the transition to add to the current slide."
    )

    descriptions: List[str] = [
        "Add a slide transition named ${{transition_name}} to the current slide.",
        "Apply a slide transition named ${{transition_name}} to the current slide.",
        "Set the slide transition of the current slide to ${{transition_name}}."
    ]

    def __init__(self, transition_name: str = None, **kwargs):
        super().__init__(transition_name=transition_name, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_add_transition",
                path=[
                    HotKeyAction(keys=["alt", "k"], thought="Press Alt + K to switch to the Transitions tab."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{transition_name if transition_name is not None else 'Fade'}' transition to apply it to the current slide."),
                    WaitAction(duration=3.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to close the transitions pane."),
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_add_transition",
                path=[
                    SingleClickAction(thought="Click the 'Transitions' tab to switch to the transitions menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{transition_name if transition_name is not None else 'Fade'}' transition to apply it to the current slide."),
                    WaitAction(duration=3.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to close the transitions pane."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointAddAnimation")
class PowerPointAddAnimation(PowerPointBaseAction):
    type: str = "powerpoint_add_animation"
    animation_name: Argument = Argument(
        value=None,
        description="Name of the animation to add to the selected object."
    )

    descriptions: List[str] = [
        "Add an animation named ${{animation_name}} to the selected object.",
        "Apply an animation named ${{animation_name}} to the selected object.",
        "Set the animation of the selected object to ${{animation_name}}."
    ]

    def __init__(self, animation_name: str = None, **kwargs):
        super().__init__(animation_name=animation_name, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks, Alt + A does not open the Animations tab, need to use key tips navigation instead
            self.add_path(
                "hotkey_add_animation",
                path=[
                    HotKeyAction(keys=["alt"], thought="Alt + A is conflict, and need to use key tips navigation instead. Press Alt to open the key tips navigation."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="a", thought="Press A to switch to the Animations tab."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{animation_name if animation_name is not None else 'Appear'}' animation to apply it to the selected object."),
                    WaitAction(duration=3.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to close the animations pane."),
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_add_animation",
                path=[
                    SingleClickAction(thought="Click the 'Animations' tab to switch to the animations menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{animation_name if animation_name is not None else 'Appear'}' animation to apply it to the selected object."),
                    WaitAction(duration=3.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to close the animations pane."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointExportPDF")
class PowerPointExportPDF(PowerPointBaseAction):
    type: str = "powerpoint_export_pdf"
    filename: Argument = Argument(
        value=None,
        description="Name of the PDF file to export."
    )

    descriptions: List[str] = [
        "Export the presentation as a PDF file named ${{filename}}.",
        "Save the presentation as a PDF file named ${{filename}}.",
        "Convert the presentation to a PDF file named ${{filename}}."
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
                    WaitAction(duration=3.0, thought="Wait for a few seconds to let PowerPoint export the PDF file."),
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
                    WaitAction(duration=3.0, thought="Wait for a few seconds to let PowerPoint export the PDF file."),
                ]
            )


@register("PowerPointSelectTextBox")
class PowerPointSelectTextBox(PowerPointBaseAction):
    type: str = "powerpoint_select_text_box"
    text: Argument = Argument(
        value=None,
        description="Content of the text box to select."
    )

    descriptions: List[str] = [
        "Select the text box containing '${{text}}'.",
        "Click on the text box with '${{text}}'.",
        "Choose the text box that has '${{text}}'.",
        "Pick the text box containing '${{text}}'.",
        "Locate and select the text box with '${{text}}'."
    ]

    def __init__(self, text: str = None, **kwargs):
        super().__init__(text=text, **kwargs)
        # We use this implementation for easier visual grounding
        self.add_path(
            "click_select_text_box",
            path=[
                SingleClickAction(thought=f"Locate and click on the text '{text}' to focus on it."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select all text in the text box."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointReplaceTextBox")
class PowerPointReplaceTextBox(PowerPointBaseAction):
    type: str = "powerpoint_replace_text_box"
    old_text: Argument = Argument(
        value=None,
        description="Content of the text box to be replaced."
    )
    new_text: Argument = Argument(
        value=None,
        description="New content to replace the old text box content."
    )

    descriptions: List[str] = [
        "Replace the text box with '${{old_text}}' to '${{new_text}}'.",
        "Change text box from '${{old_text}}' to '${{new_text}}'.",
        "Update text box text from '${{old_text}}' to '${{new_text}}'.",
        "Modify text box content from '${{old_text}}' to '${{new_text}}'.",
        "Edit text box text from '${{old_text}}' to '${{new_text}}'."
    ]

    def __init__(self, old_text: str = None, new_text: str = None, **kwargs):
        super().__init__(old_text=old_text, new_text=new_text, **kwargs)
        # We use this implementation for easier visual grounding
        self.add_path(
            "click_replace_text_box",
            path=[
                SingleClickAction(thought=f"Locate and click on the text '{old_text}' to focus on it."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select all text in the text box."),
                WaitAction(duration=1.0),
                TypeAction(text=new_text if new_text is not None else "New Text", input_mode="copy_paste", thought=f"Type the new text '{new_text if new_text is not None else 'New Text'}' to replace the old text."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointSetTextFontSize")
class PowerPointSetTextFontSize(PowerPointBaseAction):
    type: str = "powerpoint_set_text_font_size"
    font_size: Argument = Argument(
        value=None,
        description="Font size to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the font size of selected text box to ${{font_size}} pt.",
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
                    PressKeyAction(key="s", thought="Then press S to complete the focusing on the font size text field."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(font_size) if font_size is not None else "24", input_mode="copy_paste", thought=f"Type the font size '{font_size if font_size is not None else 24}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font size."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to exit the font size text field."),
                    WaitAction(duration=3.0)
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
                    TypeAction(text=str(font_size) if font_size is not None else "24", input_mode="copy_paste", thought=f"Type the font size '{font_size if font_size is not None else 24}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font size."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to exit the font size text field."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetTextFontFamily")
class PowerPointSetTextFontFamily(PowerPointBaseAction):
    type: str = "powerpoint_set_text_font_family"
    font_family: Argument = Argument(
        value=None,
        description="Font family to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the font family of selected text box to ${{font_family}}.",
        "Set font family to ${{font_family}} for the selected text box.",
        "Update the font family of the selected text box to ${{font_family}}.",
        "Make the font family ${{font_family}} for the selected text box.",
        "Adjust the font family of the selected text box to ${{font_family}}."
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
                    PressKeyAction(key="f", thought="Then press F again to complete the focusing on the font family text field."),
                    WaitAction(duration=1.0),
                    TypeAction(text=font_family if font_family is not None else "Arial", input_mode="copy_paste", thought=f"Type the font family '{font_family if font_family is not None else 'Arial'}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font family."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to exit the font family text field."),
                    WaitAction(duration=3.0)
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
                    TypeAction(text=font_family if font_family is not None else "Arial", input_mode="copy_paste", thought=f"Type the font family '{font_family if font_family is not None else 'Arial'}' to set for the selected text."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and set the font family."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to exit the font family text field."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetTextColor")
class PowerPointSetTextColor(PowerPointBaseAction):
    type: str = "powerpoint_set_text_color"
    font_color: Argument = Argument(
        value=None,
        description="Color name to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the font color of selected text box to ${{font_color}}.",
        "Set font color to ${{font_color}} for the selected text box.",
        "Update the font color of the selected text box to ${{font_color}}.",
        "Make the font color ${{font_color}} for the selected text box.",
        "Adjust the font color of the selected text box to ${{font_color}}."
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
                    PressKeyAction(key="c", thought="Then press C to complete the opening of the font color dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{font_color if font_color is not None else 'Black'}' color to set it for the selected text."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to close the font color dropdown menu."),
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_font_color",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the font color dropdown button (the small arrow down beside the font color icon 'A') to open the color selection menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{font_color if font_color is not None else 'Black'}' color to set it for the selected text."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["esc"], thought="Press Escape to close the font color dropdown menu."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetTextHighlight")
class PowerPointSetTextHighlight(PowerPointBaseAction):
    type: str = "powerpoint_set_text_highlight"
    highlight: Argument = Argument(
        value=None,
        description="Highlight color name to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the highlight color of selected text box to ${{highlight}}.",
        "Set highlight color to ${{highlight}} for the selected text box.",
        "Update the highlight color of the selected text box to ${{highlight}}.",
        "Make the highlight color ${{highlight}} for the selected text box.",
        "Adjust the highlight color of the selected text box to ${{highlight}}."
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
                    PressKeyAction(key="t", thought="Press T and C to open the text highlight color dropdown menu. First press T."),
                    PressKeyAction(key="c", thought="Then press C to complete the opening of the text highlight color dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{highlight if highlight is not None else 'Yellow'}' color to set it for the selected text."),
                    WaitAction(duration=3.0)
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
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetTextStyle")
class PowerPointSetTextStyle(PowerPointBaseAction):
    type: str = "powerpoint_set_text_style"
    text_style: Argument = Argument(
        value=None,
        description="Text style to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the text style of selected text box to ${{text_style}}.",
        "Set text style to ${{text_style}} for the selected text box.",
        "Update the text style of the selected text box to ${{text_style}}.",
        "Make the text style ${{text_style}} for the selected text box.",
        "Adjust the text style of the selected text box to ${{text_style}}."
    ]

    def __init__(self, text_style: str = "", **kwargs):
        super().__init__(text_style=text_style, **kwargs)

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
                        WaitAction(duration=3.0)
                    ]
                )
                return
            # We prefer using keyboard shortcuts Alt + H, 1/2/3/4/5 than mouse clicks
            key_tips_mapping = {
                "Bold": "1",
                "Italic": "2",
                "Underline": "3",
                "Strikethrough": "4",
                "Shadow": "5"
            }
            self.add_path(
                "hotkey_set_text_style",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key=key_tips_mapping.get(text_style, "1"), thought=f"Press {key_tips_mapping.get(text_style, '1')} to apply the {text_style if text_style is not None else 'Bold'} style for the selected text."),
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_style",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the '{text_style if text_style is not None else 'Bold'}' button to apply that style to the selected text."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetTextCase")
class PowerPointSetTextCase(PowerPointBaseAction):
    type: str = "powerpoint_set_text_case"
    case_option: Argument = Argument(
        value=None,
        description="Text case option to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the text case of selected text box to ${{case_option}}.",
        "Set text case to ${{case_option}} for the selected text box.",
        "Update the text case of the selected text box to ${{case_option}}.",
        "Make the text case ${{case_option}} for the selected text box.",
        "Adjust the text case of the selected text box to ${{case_option}}."
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
                    WaitAction(duration=3.0)
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
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetTextCharacterSpacing")
class PowerPointSetTextCharacterSpacing(PowerPointBaseAction):
    type: str = "powerpoint_set_text_character_spacing"
    spacing_option: Argument = Argument(
        value=None,
        description="Character spacing option to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the character spacing of selected text box to ${{spacing_option}}.",
        "Set character spacing to ${{spacing_option}} for the selected text box.",
        "Update the character spacing of the selected text box to ${{spacing_option}}.",
        "Make the character spacing ${{spacing_option}} for the selected text box.",
        "Adjust the character spacing of the selected text box to ${{spacing_option}}."
    ]

    def __init__(self, spacing_option: str = "Normal", **kwargs):
        super().__init__(spacing_option=spacing_option, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            key_tips_mapping = {
                "Very Tight": "I",
                "Tight": "T",
                "Normal": "N",
                "Loose": "L",
                "Very Loose": "V"
            }
            self.add_path(
                "hotkey_set_text_character_spacing",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="6", thought="Press 6 to open the character spacing dropdown menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key=key_tips_mapping.get(spacing_option, "N"), thought=f"Press {key_tips_mapping.get(spacing_option, 'N')} to select the {spacing_option if spacing_option is not None else 'Normal'} option for the selected text."),
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_text_character_spacing",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the character spacing dropdown button (the small arrow down beside) to open the spacing options menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{spacing_option if spacing_option is not None else 'Normal'}' option to set it for the selected text."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetTextLineSpacing")
class PowerPointSetTextLineSpacing(PowerPointBaseAction):
    type: str = "powerpoint_set_text_line_spacing"
    spacing_option: Argument = Argument(
        value=None,
        description="Line spacing option to set for the selected text."
    )

    descriptions: List[str] = [
        "Change the line spacing of selected text box to ${{spacing_option}}.",
        "Set line spacing to ${{spacing_option}} for the selected text box.",
        "Update the line spacing of the selected text box to ${{spacing_option}}.",
        "Make the line spacing ${{spacing_option}} for the selected text box.",
        "Adjust the line spacing of the selected text box to ${{spacing_option}}."
    ]

    def __init__(self, spacing_option: str = "1.0", **kwargs):
        super().__init__(spacing_option=spacing_option, **kwargs)

        if use_hotkey:
            # We prefer using keyboard shortcuts than mouse clicks
            self.add_path(
                "hotkey_set_text_line_spacing",
                path=[
                    HotKeyAction(keys=["alt", "h"], thought="Press Alt + H to switch to the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="k", thought="Press K to open the line spacing dropdown menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{spacing_option if spacing_option is not None else '1.0'}' option to set it for the selected text."),
                    WaitAction(duration=3.0)
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
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointInsertBullets")
class PowerPointInsertBullets(PowerPointBaseAction):
    type: str = "powerpoint_insert_bullets"
    bullet_style: Argument = Argument(
        value=None,
        description="Bullet style to apply to the selected text."
    )

    descriptions: List[str] = [
        "Add bullets to the selected text box.",
        "Insert bullet points in the selected text box.",
        "Apply bullet formatting to the selected text box.",
        "Add ${{bullet_style}} bullets to selected text box.",
        "Insert ${{bullet_style}} bullet points in the selected text box.",
        "Apply ${{bullet_style}} bullet formatting to the selected text box."
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
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_insert_bullets",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Bullets' dropdown button (the small arrow down beside the bullets icon) to open the bullet style menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{bullet_style if bullet_style is not None else 'Filled Round Bullets'}' bullet style to apply it to the selected text."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointInsertNumbering")
class PowerPointInsertNumbering(PowerPointBaseAction):
    type: str = "powerpoint_insert_numbering"
    numbering_style: Argument = Argument(
        value=None,
        description="Numbering style to apply to the selected text."
    )

    descriptions: List[str] = [
        "Add numbering to the selected text box.",
        "Insert numbering to the selected text box.",
        "Apply numbering to the selected text box.",
        "Add ${{numbering_style}} numbering to selected text box.",
        "Insert ${{numbering_style}} numbering to the selected text box.",
        "Apply ${{numbering_style}} numbering to the selected text box."
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
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_insert_numbering",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the 'Numbering' dropdown button (the small arrow down beside the numbering icon) to open the numbering style menu."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click on the '{numbering_style if numbering_style is not None else '1, 2, 3...'}' numbering style to apply it to the selected text."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointSetParagraphAlignment")
class PowerPointSetParagraphAlignment(PowerPointBaseAction):
    type: str = "powerpoint_set_paragraph_alignment"
    alignment_option: Argument = Argument(
        value="Center",
        description="Paragraph alignment option to set for the selected text."
    )

    descriptions: List[str] = [
        "Set paragraph alignment of selected text box to ${{alignment_option}}.",
        "Change paragraph alignment to ${{alignment_option}} for the selected text box.",
        "Update paragraph alignment of the selected text box to ${{alignment_option}}.",
        "Make the paragraph alignment ${{alignment_option}} for the selected text box.",
        "Adjust the paragraph alignment of the selected text box to ${{alignment_option}}."
    ]

    def __init__(self, alignment_option: str = "Center", **kwargs):
        super().__init__(alignment_option=alignment_option, **kwargs)

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
                        WaitAction(duration=3.0)
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
                    WaitAction(duration=3.0)
                ]
            )
        
        if use_mouse_click:
            self.add_path(
                "click_set_paragraph_alignment",
                path=[
                    SingleClickAction(thought="Click the 'Home' tab to ensure we are on the main screen."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the '{alignment_option if alignment_option is not None else 'Align Left'}' button to set that alignment for the selected text."),
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointInsertTable")
class PowerPointInsertTable(PowerPointBaseAction):
    type: str = "powerpoint_insert_table"
    rows: Argument = Argument(
        value=0,
        description="Number of rows for the table."
    )
    columns: Argument = Argument(
        value=0,
        description="Number of columns for the table."
    )

    descriptions: List[str] = [
        "Insert a table with ${{rows}} rows and ${{columns}} columns.",
        "Add a table of size ${{rows}} by ${{columns}}.",
        "Create a table with ${{rows}} rows and ${{columns}} columns.",
        "Place a table with ${{rows}} rows and ${{columns}} columns.",
        "Generate a table having ${{rows}} rows and ${{columns}} columns."
    ]

    def __init__(self, rows: int = 0, columns: int = 0, **kwargs):
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
                    TypeAction(text=str(columns) if columns is not None else "10", input_mode="copy_paste", thought=f"Type the number of columns '{columns if columns is not None else 10}' for the table."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["alt", "r"], thought="Press Alt + R to switch to the 'number of rows' input field."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select the default number of rows."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(rows) if rows is not None else "10", input_mode="copy_paste", thought=f"Type the number of rows '{rows if rows is not None else 10}' for the table."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and insert the table."),
                    WaitAction(duration=3.0)
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
                    TypeAction(text=str(columns) if columns is not None else "10", input_mode="copy_paste", thought=f"Type the number of columns '{columns if columns is not None else 10}' for the table."),
                    WaitAction(duration=1.0),

                    # delete the default number of rows, and type the desired number of rows
                    SingleClickAction(thought="Click the 'number of rows' input field to focus on it. It is the below input field in the pop-up dialog."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["ctrl", "a"], thought="Press Ctrl + A to select the default number of rows."),
                    WaitAction(duration=1.0),
                    TypeAction(text=str(rows) if rows is not None else "10", input_mode="copy_paste", thought=f"Type the number of rows '{rows if rows is not None else 10}' for the table."),
                    WaitAction(duration=1.0),

                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and insert the table."),
                    WaitAction(duration=3.0)
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


@register("PowerPointInsertTableRow")
class PowerPointInsertTableRow(PowerPointBaseAction):
    type: str = "powerpoint_insert_table_row"
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
                        WaitAction(duration=3.0)
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
                        WaitAction(duration=3.0)
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
                        PressKeyAction(key="e", thought="Press E to insert a new row below the selected row."),
                        WaitAction(duration=3.0)
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
                        WaitAction(duration=3.0)
                    ]
                )


@register("PowerPointInsertTableColumn")
class PowerPointInsertTableColumn(PowerPointBaseAction):
    type: str = "powerpoint_insert_table_column"
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
                        WaitAction(duration=3.0)
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
                        WaitAction(duration=3.0)
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
                        PressKeyAction(key="i", thought="Press I to insert a new column to the right of the selected column."),
                        WaitAction(duration=3.0)
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
                        WaitAction(duration=3.0)
                    ]
                )


@register("PowerPointDeleteTableRow")
class PowerPointDeleteTableRow(PowerPointBaseAction):
    type: str = "powerpoint_delete_table_row"
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
                    WaitAction(duration=3.0)
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
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointDeleteTableColumn")
class PowerPointDeleteTableColumn(PowerPointBaseAction):
    type: str = "powerpoint_delete_table_column"
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
                    WaitAction(duration=3.0)
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
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointDeleteTable")
class PowerPointDeleteTable(PowerPointBaseAction):
    type: str = "powerpoint_delete_table"

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
                    WaitAction(duration=3.0)
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
                    WaitAction(duration=3.0)
                ]
            )


@register("PowerPointInsertTableCellText")
class PowerPointInsertTableCellText(PowerPointBaseAction):
    type: str = "powerpoint_insert_table_cell_text"
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
                TypeAction(text=text if text is not None else "Sample Text", input_mode="copy_paste", thought=f"Type the text '{text if text is not None else 'Sample Text'}' into the selected table cell."),
                WaitAction(duration=3.0)
            ]
        )


@register("PowerPointInsertShape")
class PowerPointInsertShape(PowerPointBaseAction):
    type: str = "powerpoint_insert_shape"
    shape_type: Argument = Argument(
        value=None,
        description="Name of the shape to insert."
    )

    shape_position: Argument = Argument(
        value=None,
        description="Position to insert the shape on the slide."
    )

    descriptions: List[str] = [
        "Insert a ${{shape_type}} shape (at any place) on the current slide.",
        "Add a ${{shape_type}} shape (at any place) on the current slide.",
        "Create a ${{shape_type}} shape (at any place) on the current slide.",
        "Insert a ${{shape_type}} shape at position ${{shape_position}} on the current slide.",
        "Add a ${{shape_type}} shape at position ${{shape_position}} on the current slide.",
        "Create a ${{shape_type}} shape at position ${{shape_position}} on the current slide."
    ]

    def __init__(self, shape_type: str = None, shape_position: str = None, **kwargs):
        super().__init__(shape_type=shape_type, shape_position=shape_position, **kwargs)

        if shape_position is None:
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
                        SingleClickAction(thought="Click on any position on the slide to place the shape.  You should click on an empty area on the slide to avoid overlapping with existing content."),
                        WaitAction(duration=3.0)
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
                        SingleClickAction(thought="Click on any position on the slide to place the shape.  You should click on an empty area on the slide to avoid overlapping with existing content."),
                        WaitAction(duration=3.0)
                    ]
                )
        else:
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
                        SingleClickAction(thought=f"Click on the slide at the '{shape_position if shape_position is not None else 'center'}' area on the current displayed slide to place the shape. You should click on an empty area on the slide to avoid overlapping with existing content."),
                        WaitAction(duration=3.0)
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
                        SingleClickAction(thought=f"Click on the slide at the '{shape_position if shape_position is not None else 'center'}' area on the current displayed slide to place the shape. You should click on an empty area on the slide to avoid overlapping with existing content."),
                        WaitAction(duration=3.0)
                    ]
                )
