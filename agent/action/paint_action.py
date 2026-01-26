from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, DoubleClickAction, DragAction
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

class PaintBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="Paint",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Paint",
        description="The name of the Paint application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("PaintLaunch")
class PaintLaunch(PaintBaseAction, LaunchApplication):
    type: str = "paint_launch"

    instructions: List[str] = [
        "Open Paint.",
        "Launch Paint.",
        "Start Paint.",
        "Open the Paint.",
        "Launch the Paint.",
        "Start the Paint."
    ]

    def __init__(self, **kwargs):
        super().__init__(application_name=self.application_name, **kwargs)


@register("PaintSave")
class PaintSave(PaintBaseAction):
    type: str = "paint_save"

    file_name: Argument = Argument(
        value="image.png",
        description="The name of the file to save the image as."
    )
    location: Argument = Argument(
        value="Downloads",
        description="The location to save the image in. E.g., 'documents', 'downloads', 'desktop'."
    )

    instructions: List[str] = [
        "Save the paint image as {file_name} in the {location} folder.",
        "Save the current paint image with the name {file_name} to the {location} directory.",
        "Store the paint image as {file_name} in my {location}."
    ]

    def __init__(self, file_name="image.png", location="Downloads", **kwargs):
        super().__init__(file_name=file_name, location=location, **kwargs)
        self.add_path(
            "hotkey_save",
            path = [
                HotKeyAction(keys=["ctrl", "s"], thought="Use the hotkey 'ctrl s' to open the 'Save' dialog in the Home tab of Paint."),
                WaitAction(duration=1.0),
                DoubleClickAction(thought="Click inside the text box to the right of the 'File name', label at the bottom of the Save dialog to select the entire file name."),
                WaitAction(duration=1.0),
                TypeAction(text=file_name, thought=f"Type the filename '{file_name}'."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Save dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=1.0),
                TypeAction(text=location, thought=f"Type the location '{location}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Save' button to save the image."),
                WaitAction(duration=1.0)
            ]
        )



@register("PaintSaveAs")
class PaintSaveAs(PaintBaseAction):
    type: str = "paint_save_as"

    file_name: Argument = Argument(
        value="image.png",
        description="The name of the file to save the image as."
    )
    location: Argument = Argument(
        value="documents",
        description="The location to save the image in. E.g., 'documents', 'downloads', 'desktop'."
    )
    output_format = Argument(
        value="PNG",
        description="The format to save the image in. E.g., 'PNG', 'JPEG', 'BMP', 'GIF'."
    )

    instructions: List[str] = [
        "Save the paint image as {file_name} in the {location} folder.",
        "Save the current paint image with the name {file_name} to the {location} directory.",
        "Store the paint image as {file_name} in my {location}."
    ]

    def __init__(self, file_name="image.png", location="Downloads", output_format="PNG", **kwargs):
        super().__init__(file_name=file_name, location=location, output_format=output_format, **kwargs)
        self.add_path(
            "click_save_as",
            path = [
                SingleClickAction(thought="Click the 'File' menu in Paint."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Save As' option from the File menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the '{output_format}' option for saving the image."),
                WaitAction(duration=1.0),
                DoubleClickAction(thought="Click inside the text box to the right of the 'File name', label at the bottom of the Save As dialog to select the entire file name."),
                WaitAction(duration=1.0),
                TypeAction(text=file_name, thought=f"Type the filename '{file_name}'."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Save As dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=1.0),
                TypeAction(text=location, thought=f"Type the location '{location}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),   
                SingleClickAction(thought="Click the 'Save' button to save the image."),
                WaitAction(duration=1.0)
            ]
        )


@register("PaintChangeCanvasSize")
class PaintChangeCanvasSize(PaintBaseAction):
    type: str = "paint_change_canvas_size"

    width: Argument = Argument(
        value=800,
        description="The width of the canvas in pixels."
    )
    height: Argument = Argument(
        value=800,
        description="The height of the canvas in pixels."
    )

    instructions: List[str] = [
        "Change the canvas size to {width}x{height} pixels.",
        "Set the canvas dimensions to {width} pixels wide and {height} pixels high.",
        "Adjust the canvas size to be {width} by {height} pixels."
    ]

    def __init__(self, width=800, height=600, **kwargs):
        super().__init__(width=width, height=height, **kwargs)
        self.add_path(
            "hot_key_click_canvas_size",
            path = [
                HotKeyAction(keys=["ctrl", "e"], thought="Use the hotkey 'ctrl e' to open the 'Resize' dialog in the Home tab of Paint."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Pixels' radio button to set the units to pixels."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click inside the 'Width' input field to set the canvas width."),
                WaitAction(duration=1.0),
                TypeAction(text=str(width), thought=f"Type the width '{width}' in the Width field."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click inside the 'Height' input field to set the canvas height."),
                WaitAction(duration=1.0),
                TypeAction(text=str(height), thought=f"Type the height '{height}' in the Vertical field."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'OK' button to apply the new canvas size."),
                WaitAction(duration=1.0)
            ]
        )

        # self.add_path(
        #     "hot_key_click_canvas_size",
        #     path = [
        #         HotKeyAction(keys=["ctrl", "w"], thought="Use the hotkey 'ctrl w' to open the 'Resize' dialog in the Home tab of Paint."),
        #         WaitAction(duration=1.0),
        #         SingleClickAction(thought="Click the 'Pixels' radio button to set the units to pixels."),
        #         WaitAction(duration=1.0),
        #         SingleClickAction(thought="Click inside the 'Horizontal' input field to set the canvas width."),
        #         WaitAction(duration=1.0),
        #         TypeAction(text=str(width), thought=f"Type the width '{width}' in the Horizontal field."),
        #         WaitAction(duration=1.0),
        #         SingleClickAction(thought="Click inside the 'Vertical' input field to set the canvas height."),
        #         WaitAction(duration=1.0),
        #         TypeAction(text=str(height), thought=f"Type the height '{height}' in the Vertical field."),
        #         WaitAction(duration=1.0),
        #         SingleClickAction(thought="Click the 'OK' button to apply the new canvas size."),
        #         WaitAction(duration=1.0)
        #     ]
        # )


@register("PaintPickColor")
class PaintPickColor(PaintBaseAction):
    type: str = "paint_pick_color"

    color: Argument = Argument(
        value="red",
        description="The color to pick. E.g., 'red', 'blue', 'green', 'yellow'."
    )


@register("PaintFitCanvasToWindow")
class PaintFitCanvasToWindow(PaintBaseAction):
    type: str = "paint_fit_to_window"
    width: Argument = Argument(
        value=3840,
        description="The width of the window in pixels."
    )
    height: Argument = Argument(
        value=600,
        description="The height of the window in pixels."
    )
    
    instructions: List[str] = [
        "Fit the canvas to the window before drawing.",
        "Adjust the canvas size to fit within the window before drawing.",
        "Resize the canvas to fit within the window before drawing."
    ]
    
    def __init__(self, width=3840, height=1600, **kwargs):
        super().__init__(width=width, height=height, **kwargs)
        # self.add_path(
        #     "hot_key_click_fit_to_window",
        #     path = [
        #         SingleClickAction(thought="Click the 'Fit to Window' button in Microsoft Paint. It locates on the bottom-right of the windows. It is the small rectangular button whose icon is a circle with four short bracket marks around it, located to the left of the zoom-percentage box (e.g., '100%'). Do not click the zoom percentage, the slider, the +/- icons, or anything near the top of the window."),
        #         WaitAction(duration=1.0)
        #     ]
        # )
        
        self.add_path(
            "change_canvas_size_fit_to_window",
            path = [
                PaintChangeCanvasSize(width=self.width, height=self.height),
                WaitAction(duration=1.0)
            ]
        )


@register("PaintDrawShape")
class PaintDrawShape(PaintBaseAction):
    type: str = "paint_draw_shape"

    shape: Argument = Argument(
        value="circle",
        description="The shape to draw. E.g., 'circle', 'square', 'rectangle', 'triangle'."
    )
    outline_color: Argument = Argument(
        value="red",
        description="The color of the shape outline. E.g., 'red', 'blue', 'green', 'yellow'. 'none' means no outline color for outline."
    )
    fill_color: Argument = Argument(
        value="red",
        description="The color of the shape to draw. E.g., 'red', 'blue', 'green', 'yellow'. 'none' means no fill color."
    )
    start_coordinates_percentage_on_canvas: Argument = Argument(
        value=[0.1, 0.1],
        description="The starting coordinates on the canvas as percentages [x_percentage, y_percentage]. E.g., [0.1, 0.1] for 10% from top-left. If not specified, use the default [0.1, 0.1]."
    )
    end_coordinates_percentage_on_canvas: Argument = Argument(
        value=[0.8, 0.8],
        description="The ending coordinates on the canvas as percentages [x_percentage, y_percentage]. E.g., [0.8, 0.8] for 80% from top-left. If not specified, use the default [0.8, 0.8]."
    )
    canvas_width: Argument = Argument(
        value=1920,
        description="The width of the canvas in pixels."
    )
    canvas_height: Argument = Argument(
        value=1080,
        description="The height of the canvas in pixels."
    )
    # Canvas padding as a percentage of the canvas size
    padding_percentage: float = 0.1
    
    instructions: List[str] = [
        "Draw a {color} {shape} on the canvas.",
        "Create a {shape} filled with {color} color on the canvas.",
        "Sketch a {shape} in {color} on the drawing area."
    ]

    def configure_from_env(self, env = None):
        if hasattr(env, "screen_width") and hasattr(env, "screen_height"):
            self.canvas_width.value = env.screen_width
            self.canvas_height.value = env.screen_height
        elif hasattr(env, "vm_screen_size"):
            self.canvas_width.value = env.vm_screen_size["width"]
            self.canvas_height.value = env.vm_screen_size["height"]


    def get_start_end_coordinates(self) -> Dict[str, List[int]]:
        self.canvas_width.value = float(self.canvas_width.value)
        self.canvas_height.value = float(self.canvas_height.value)
        start_values = self.process_listlike_str(self.start_coordinates_percentage_on_canvas.value)
        start_values = [float(v) for v in start_values]
        end_values = self.process_listlike_str(self.end_coordinates_percentage_on_canvas.value)
        end_values = [float(v) for v in end_values]
        start_x = int(start_values[0] * self.canvas_width.value) + int(self.padding_percentage * self.canvas_width.value)
        start_y = int(start_values[1] * self.canvas_height.value) + int(self.padding_percentage * self.canvas_height.value)
        end_x = int(end_values[0] * self.canvas_width.value) - int(self.padding_percentage * self.canvas_width.value)
        end_y = int(end_values[1] * self.canvas_height.value) - int(self.padding_percentage * self.canvas_height.value)
        return [start_x, start_y], [end_x, end_y]
    
    def __init__(self, shape="circle", fill_color="red", outline_color="red", canvas_width=3840, canvas_height=1600, start_coordinates_percentage_on_canvas=[0.1, 0.1], end_coordinates_percentage_on_canvas=[0.8, 0.8], **kwargs):
        super().__init__(shape=shape, fill_color=fill_color, outline_color=outline_color, canvas_width=canvas_width, canvas_height=canvas_height, start_coordinates_percentage_on_canvas=start_coordinates_percentage_on_canvas, end_coordinates_percentage_on_canvas=end_coordinates_percentage_on_canvas, **kwargs)
        # self.add_path(
        #     "draw_shape_path",
        #     path = [
        #         SingleClickAction(thought=f"Pick the '{outline_color}' color from the color palette."),
        #         WaitAction(duration=1.0),
        #         SingleClickAction(thought=f"Choose the '{shape}' shape from the Shapes panel."),
        #         WaitAction(duration=1.0),
        #         DragAction(thought=f"Click and drag to draw a {outline_color} {shape} from {self.start_coordinates_percentage_on_canvas} to {self.end_coordinates_percentage_on_canvas} on the canvas.",
        #             thought_for_start_coordinate=f"The start point should be just inside the '{self.start_coordinate_raw_location}' corner of the drawing canvas (not in the toolbar, not in the gray border).",
        #             thought_for_end_coordinate=f"The end point should be just inside the '{self.end_coordinate_raw_location}' corner of the drawing canvas (not in the toolbar, not in the gray border).",
        #             duration=2.0),
        #         WaitAction(duration=1.0),
        #         HotKeyAction(keys=["b"], thought="Select the 'Fill' option to fill the shape with color."),
        #         WaitAction(duration=1.0),
        #         SingleClickAction(thought=f"Pick the '{fill_color}' color from the color palette."),
        #         WaitAction(duration=1.0),
        #         SingleClickAction(thought=f"Click inside the drawn {shape} to fill it with the '{fill_color}' color."),
        #         WaitAction(duration=1.0)
        #     ]
        # )
        start_coordinates, end_coordinates = self.get_start_end_coordinates()
        self.add_path(
            "fit_windows_draw_shape",
            path = [
                SingleClickAction(thought=f"Pick the '{outline_color}' color from the color palette."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Choose the '{shape}' shape from the Shapes panel."),
                WaitAction(duration=1.0),
                DragAction(
                    thought=f"Click and drag to draw a {outline_color} {shape} from {self.start_coordinates_percentage_on_canvas} to {self.end_coordinates_percentage_on_canvas} on the canvas.",\
                    start_coordinate=start_coordinates,
                    end_coordinate=end_coordinates,
                    duration=2.0),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["b"], thought="Select the 'Fill' option to fill the shape with color."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Pick the '{fill_color}' color from the color palette."),
                WaitAction(duration=1.0),
                DoubleClickAction(
                    thought=f"Click the central point of the drawn {shape} to fill it with the '{fill_color}' color.", 
                    coordinate=[int((start_coordinates[0] + end_coordinates[0]) / 2), int((start_coordinates[1] + end_coordinates[1]) / 2)]),
                WaitAction(duration=1.0)
            ]
        )