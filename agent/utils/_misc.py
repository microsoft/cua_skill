import json
from types import SimpleNamespace

import io
import requests
from PIL import Image, ImageDraw, ImageFont
from typing import List
import textwrap

class Misc:
    @staticmethod
    def namespace_to_dict(obj):
        """
        Recursively converts a SimpleNamespace (or structure containing it)
        into a regular dictionary that can be serialized or inspected easily.
        """
        # If the object is a SimpleNamespace, convert its attributes to dict entries
        if isinstance(obj, SimpleNamespace):
            return {k: Misc.namespace_to_dict(v) for k, v in vars(obj).items()}

        # If it's a list, recursively convert each item
        elif isinstance(obj, list):
            return [Misc.namespace_to_dict(item) for item in obj]

        # If it's already a dict, recursively convert each value
        elif isinstance(obj, dict):
            return {k: Misc.namespace_to_dict(v) for k, v in obj.items()}

        # Base case: it's a primitive (str, int, float, etc.), return as-is
        else:
            return obj

    @staticmethod
    def file_to_namespace(path):
        """
        Loads a JSON file and returns its contents as a nested SimpleNamespace,
        allowing attribute-style access to keys (e.g., data.user.name).
        """
        try:
            # Open the JSON file safely using a context manager
            with open(path, 'r') as f:
                # Use object_hook to convert each JSON object into a SimpleNamespace
                return json.load(f, object_hook=lambda d: SimpleNamespace(**d))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON file: {e}")
            return SimpleNamespace()

    @staticmethod
    def dict_to_namespace(d):
        """
        Recursively converts a dictionary (or structure containing it)
        into a SimpleNamespace for attribute-style access.
        """
        if isinstance(d, dict):
            return SimpleNamespace(**{k: Misc.dict_to_namespace(v) for k, v in d.items()})
        elif isinstance(d, list):
            return [Misc.dict_to_namespace(item) for item in d]
        else:
            return d

    # @staticmethod
    # def get_screenshot(target_resolution=None):
    #     screenshot = pyautogui.screenshot()
    #     if target_resolution is not None:
    #         screenshot = screenshot.resize(target_size)
    #     return screenshot

    @staticmethod
    def get_plan(task, screenshot, config=None, session_logger=None):
        """
        test function created by RGAL to debug plans without the need to fire up the Agent class
        """
        if not config:
            raise ValueError("config is not initialized.")
        if not session_logger:
            raise ValueError("session_logger is not initialized.")

        if screenshot is None:
            screenshot = Misc.get_screenshot()

        session_logger.info(f"planning to do {task}")

        image_bytes_io = io.BytesIO()
        screenshot.save(image_bytes_io, format="PNG")  # Save the image as a PNG in memory
        screenshot_bytes = image_bytes_io.getvalue() 

        files = {"screenshot": screenshot_bytes, "task": task}

        try:
            response = requests.post(config.planning.local_url, files=files)
            if response.status_code == 200:
                plan_str = response.json()["plan"]
            else:
                plan_str = ''
                session_logger.error(f"Error: {response.text}")
        except requests.RequestException as e:
            plan_str = ''
            session_logger.error(f"Request failed: {e}")

        return plan_str

    @staticmethod
    def _draw_circle(draw:ImageDraw.ImageDraw, center, radius):
        circle_radius = radius  # Use the radius passed in

        # Define four semi-transparent colors
        colors = [
            (255, 0, 0, 50),     # Red
            (0, 255, 0, 50),     # Green
            (0, 0, 255, 50),     # Blue
            (255, 255, 0, 50)    # Yellow
        ]

        # Optional: adjust slight offsets so the colors are more visible layered
        radii = [radius, radius-10, radius-20, radius-30]

        for color, circle_radius in zip(colors, radii):
            draw.ellipse(
                (
                    center[0] - circle_radius,
                    center[1] - circle_radius,
                    center[0] + circle_radius,
                    center[1] + circle_radius,
                ),
                fill=color,
                outline=(0, 0, 0, 255),
                width=2
            )

    @staticmethod
    def _draw_rectangle(draw:ImageDraw.ImageDraw, rect):
        x, y, w, h = rect
        rect_outline_color = (0, 0, 0, 255)  # Black solid border

        # Define four semi-transparent colors
        colors = [
            (255, 0, 0, 50),     # Red
            (0, 255, 0, 50),     # Green
            (0, 0, 255, 50),     # Blue
            (255, 255, 0, 50)    # Yellow
        ]

        offsets = [30,20,10,0]

        for color, offset in zip(colors, offsets):
            draw.rectangle(
                (x - offset, y - offset, x + w + offset, y + h + offset ),
                fill=color,
                outline=rect_outline_color,  # Black solid frame
                width=2,  # Border thickness
            )

    @staticmethod
    def _draw_text_with_outline(
        draw: ImageDraw.ImageDraw,
        position,
        text,
        font,
        text_color,
        outline_color,
        thickness,
        background_color=None,
        padding=10
    ):
        x, y = position

        # Get accurate bounding box of the text
        bbox = draw.textbbox((x, y), text, font=font)
        x0, y0, x1, y1 = bbox
        text_width = x1 - x0
        text_height = y1 - y0

        # Optional: draw background rectangle with padding
        if background_color:
            bg_rect = [
                x0 - padding,
                y0 - padding,
                x1 + padding,
                y1 + padding
            ]
            draw.rectangle(bg_rect, fill=background_color)

        # Draw outline by offsetting in multiple directions
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

    @staticmethod
    def _draw_text(draw: ImageDraw.ImageDraw, text: str, position):
        from PIL import ImageFont

        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            font = ImageFont.load_default()

        text_color = (255, 255, 0, 255)       # Yellow text
        outline_color = (0, 0, 0, 255)        # Black outline
        background_color = (200, 150, 200, 120)     # Semi-transparent black
        outline_thickness = 2
        padding = 10

        Misc._draw_text_with_outline(
            draw,
            position,
            text,
            font,
            text_color,
            outline_color,
            outline_thickness,
            background_color=background_color,
            padding=padding
        )

    @staticmethod
    def get_commands_debug_image(image:Image, commands_debug_info:List, text:str = None):

        # Convert bytes back into a PIL Image
        if (isinstance(image, bytes)):
            image = Image.open(io.BytesIO(image))

        image = image.convert("RGBA")

        # Create a new transparent overlay
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))  # Fully transparent
        draw = ImageDraw.Draw(overlay)

        if text:
            Misc._draw_text(draw, text, (20,20))

        for c in commands_debug_info:
            match c["type"]:
                case "SINGLE_CLICK" | "DOUBLE_CLICK" | "RIGHT_CLICK" | "MOVE_ABS":
                    # circle
                    x, y = c["location"]

                    Misc._draw_circle(draw, (x, y), 50)

                case "DRAG":
                    # circle
                    sx, sy, ex, ey = c["location"]

                    Misc._draw_rectangle(draw, (sx, sy, abs(ex-sx)+1, abs(ey-sy)+1))

                case "SCROLL":
                    pass

                case _:
                    raise Exception("should not get here")


        # Composite the overlay onto the image
        image = Image.alpha_composite(image, overlay)

        return image

    @staticmethod
    def wrap_text_lines(text:str, width=40) -> str:
        # Split into lines and wrap each one
        wrapped_lines = []
        for line in text.splitlines():
            wrapped_lines.extend(textwrap.wrap(line, width=width) or [""])  # keep empty lines

        # Join back into a single string
        warpped_text = "\n".join(wrapped_lines)
        return warpped_text


    @staticmethod
    def is_json_serializable(value):
        """
        Check if a given value can be safely serialized to JSON.

        Args:
            value: Any Python object.

        Returns:
            bool: True if the value can be serialized with `json.dumps()`, False otherwise.
        """        
        try:
            json.dumps(value)
            return True
        except (TypeError, OverflowError):
            return False

    @staticmethod
    def filter_serializable(obj):
        """
        Recursively filter a dictionary or list to include only JSON-serializable values.

        Args:
            obj: A dictionary, list, or other object.

        Returns:
            A new object with only JSON-serializable values.
            Non-serializable values are removed or replaced with None.
        """        
        if isinstance(obj, dict):
            return {k: Misc.filter_serializable(v) for k, v in obj.items() if Misc.is_json_serializable(v)}
        elif isinstance(obj, list):
            return [Misc.filter_serializable(item) for item in obj if Misc.is_json_serializable(item)]
        elif Misc.is_json_serializable(obj):
            return obj
        else:
            return None  # or skip entirely

    @staticmethod
    def safe_to_json(obj):
        """
        Convert an object to a pretty-printed JSON string, safely skipping non-serializable fields.

        Args:
            obj: Any object (ideally a dict-like or a class instance with a __dict__).

        Returns:
            str: A JSON-formatted string of the serializable parts of the object.
        """        
        if hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
        elif isinstance(obj, dict):
            obj_dict = obj
        else:
            return json.dumps(str(obj))  # fallback: convert to string

        filtered = Misc.filter_serializable(obj_dict)
        return json.dumps(filtered, indent=2)