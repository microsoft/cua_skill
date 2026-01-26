import os
import io
import json
import time
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
from .LoggerMessages import *
from ._session_logger import SessionLogger
from . import Config, DesktopHandler, WindowHandler
import re
from typing import Dict, List, Any


def _export_snapshot(screenshot: Image.Image, taskbar_txt: str, tb_control: List[Dict[str, Any]], active_txt: str, active_control: List[Dict[str, Any]], output_dir: str = "."):
    """
    Export the screenshot as a PNG and the UIA controls snapshot as a JSON file
    with a consistent timestamp-based naming convention.
    """
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    png_name = f"snapshot_{timestamp}.png"
    json_name_summary = f"control_summary_{timestamp}.json"
    json_name_ctrl = f"control_items_{timestamp}.json"


    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save screenshot
    png_path = os.path.join(output_dir, png_name)
    screenshot.save(png_path, format="PNG")

    # Save JSON data
    snapshot_data = {
        "taskbar_controls": taskbar_txt,
        "active_window_controls": active_txt
    }
    json_path = os.path.join(output_dir, json_name_summary)
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(snapshot_data, jf, indent=2, ensure_ascii=False)

    ctrl_data = {
        "tb_controls": tb_control,
        "aw_controls": active_control
    }

    def to_serializable(obj):
        # called for objects that aren’t natively JSON serializable
        return str(obj)

    json_name_ctrl_path = os.path.join(output_dir, json_name_ctrl)
    with open(json_name_ctrl_path, "w", encoding="utf-8") as jf:
        json.dump(ctrl_data, jf, default=to_serializable, indent=2, ensure_ascii=False)

    return png_path, json_path, json_name_ctrl_path


class UIAGrounding:
    """
    Handle UIA grounding and produce debug images and exports.
    """
    def __init__(self, config: Config, session_logger: SessionLogger = None, export_mode: bool = False):
        self.config = config
        self.session_logger = session_logger
        self.export_mode = export_mode
        self.reset()

    def reset(self):
        self.task = None
        self.screenshot = None
        self.g_coordinate = None
        self.uia_coordinate = None
        self.control_rect = None

    def _is_point_inside_rectangle(self, px, py, rx, ry, rw, rh):
        return rx <= px <= rx + rw and ry <= py <= ry + rh

    def _draw_text_with_outline(self, draw, position, text, font, text_color, outline_color, thickness):
        x, y = position
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx or dy:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=text_color)

    def get_debug_image(self) -> Image.Image:
        text = f"Task: [{self.task}]"
        rect = self.control_rect
        coord = self.g_coordinate

        if rect and coord:
            inside = self._is_point_inside_rectangle(coord[0], coord[1], rect["x"], rect["y"], rect["width"], rect["height"])
            text += " - UIA and Grounding - " + ("AGREE" if inside else "DISAGREE")
        elif rect:
            text += " - UIA Only"
        elif coord:
            text += " - Grounding Only"
        else:
            text += " - ?? Should not happen ??"

        base_img = self.screenshot.convert("RGBA")
        overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Draw grounding circle
        if coord:
            cx, cy = coord
            r = 50
            draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255,0,0,128), outline=(0,0,0), width=3)

        # Draw UIA rectangle
        if rect:
            x, y, w, h = rect["x"], rect["y"], rect["width"], rect["height"]
            draw.rectangle((x, y, x+w, y+h), fill=(0,0,255,128), outline=(0,0,0), width=3)

        # Draw text
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except IOError:
            font = ImageFont.load_default()
        self._draw_text_with_outline(draw, (10, base_img.height//2 - 40), text, font, (255,255,0), (0,0,0), 2)

        return Image.alpha_composite(base_img, overlay)

    def generate_coordinate(self, task: str, screenshot: Image.Image):
        self.reset()
        self.task = task
        self.screenshot = screenshot if isinstance(screenshot, Image.Image) else Image.open(io.BytesIO(screenshot))

        d = DesktopHandler()
        tb_summary, tb_controls = d.get_taskbar().get_control_summary2(max_text_length=50) if d.get_taskbar() else ("", [])
        aw_summary, aw_controls = d.get_active_window().get_control_summary2(max_text_length=50) if d.get_active_window() else ("", [])

        if self.export_mode:
            _export_snapshot(self.screenshot, tb_summary, tb_controls, aw_summary, aw_controls)

        # Prepare payload
        img_buf = io.BytesIO()
        self.screenshot.save(img_buf, format="PNG")
        encoded = base64.b64encode(img_buf.getvalue()).decode()

        payload = {
            "files": {
                "method": "EMBED",
                "grounding_url": self.config.grounding.uia_grounding.fallback_grounding_url,
                "uia_llm_url": self.config.grounding.uia_grounding.llm_url,
                "screenshot": encoded,
                "action": task,
                "taskbar_controls": tb_summary,
                "active_window_controls": aw_summary,
                "always_run_grounding": self.config.grounding.uia_grounding.always_run_fallback_grounding,
                "embed_threshold": self.config.grounding.uia_grounding.embed_threshold,
            }
        }
        res = requests.post(self.config.grounding.uia_grounding.grounding_url, json=payload).json()
        if self.session_logger:
            self.session_logger.debug(LogMessage(message=json.dumps(res, indent=4), console_panel_title="UIAGrounding Result - DEBUG"))

        # Process UIA result
        uia = res.get("uia_result", {})
        idx = uia.get("index", 0) - 1
        cont = uia.get("container_list", "").upper()
        control = None
        if idx >= 0:
            if cont == "TASKBAR" and idx < len(tb_controls):
                control = tb_controls[idx]
            elif cont == "ACTIVE" and idx < len(aw_controls):
                control = aw_controls[idx]
        if control:
            rect = control["rectangle"]
            self.control_rect = rect
            self.uia_coordinate = [rect["x"] + rect["width"]//2, rect["y"] + rect["height"]//2]

        self.g_coordinate = res.get("coordinate")
        return self.uia_coordinate or self.g_coordinate


class UIAGroundingWithOffline(UIAGrounding):
    def __init__(self, config: Config, session_logger: SessionLogger = None, export_mode: bool = False):
        self.config = config
        self.session_logger = None
        self.export_mode = False
        self.reset()

    def parse_ui_elements(self, raw: str) -> Dict[int, Dict[str, str]]:
        pattern = r'''
        "                                      # opening quote for the key
        (?P<key>taskbar_controls|active_window_controls)
        "\s*:\s*"                              # closing quote/key, colon, opening quote for the value
        (?P<value>[^"]*?)                      # lazily capture anything up to the next quote
        "                                      # closing quote for the value
        '''
        matches = re.finditer(pattern, raw, re.DOTALL | re.VERBOSE)

        result = {}
        for m in matches:
            key = m.group("key")
            val = m.group("value")
            result[key] = val

        return result

    """
    Load UIA data from a saved JSON and ground offline.
    """
    def generate_from_uia_json(self, task: str, screenshot: Image.Image, uia_summary_path: str, ctrl_path: str):
        self.reset()
        self.task = task
        self.screenshot = screenshot if isinstance(screenshot, Image.Image) else Image.open(io.BytesIO(screenshot))

        with open(uia_summary_path, 'r', encoding='utf-8') as f:
            tree = json.load(f)

        with open(ctrl_path, 'r', encoding='utf-8') as f:
            ctrl_tree = json.load(f)

        # summary text for LLM
        tb_summary = tree['taskbar_controls']
        aw_summary = tree['active_window_controls']

        # ctrl info for extracting bboxes
        tb_ctrl = ctrl_tree['tb_controls']
        aw_ctrl = ctrl_tree['aw_controls']
        # Prepare payload same as base
        buf = io.BytesIO()
        self.screenshot.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode()

        payload = {"files": {**{
            "method": "EMBED",
            "grounding_url": self.config.grounding.uia_grounding.fallback_grounding_url,
            "uia_llm_url": self.config.grounding.uia_grounding.llm_url,
            "screenshot": encoded,
            "action": task,
            "taskbar_controls": tb_summary,
            "active_window_controls": aw_summary,
            "always_run_grounding": self.config.grounding.uia_grounding.always_run_fallback_grounding,
            "embed_threshold": self.config.grounding.uia_grounding.embed_threshold,
        }}}
        res = requests.post(self.config.grounding.uia_grounding.grounding_url, json=payload).json()
        if self.session_logger:
            self.session_logger.debug(LogMessage(message=json.dumps(res, indent=4), console_panel_title="UIAGroundingWithOffline Result"))

        # Process UIA
        uia = res.get("uia_result", {})
        idx = uia.get("index", 0) - 1
        cont = uia.get("container_list", "").upper()
        control = None
        if idx >= 0:
            if cont == "TASKBAR" and idx < len(tb_ctrl): control = tb_ctrl[idx]
            elif cont == "ACTIVE" and idx < len(aw_ctrl): control = aw_ctrl[idx]
        if control:
            r = control["rectangle"]
            self.control_rect = r
            self.uia_coordinate = [r["x"] + r["width"]//2, r["y"] + r["height"]//2]

        self.g_coordinate = res.get("coordinate")
        return self.uia_coordinate or self.g_coordinate
