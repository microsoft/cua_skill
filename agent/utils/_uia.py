import os, sys

if sys.platform.startswith("win"):
    import pywinauto
    import pyautogui
    import win32gui
    import win32con
    from pywinauto.uia_element_info import UIAElementInfo
    from pywinauto.application import Application
    from pywinauto.controls.uiawrapper import UIAWrapper

import json
from collections import Counter

def rectangles_overlap(rect1, rect2):
    """
    Check if two rectangles overlap.
    
    Each rectangle is a dictionary:
    {"x": left, "y": top, "width": width, "height": height}
    
    Returns True if they overlap, False otherwise.
    """
    # Get the boundaries of both rectangles
    x1, y1, w1, h1 = rect1["x"], rect1["y"], rect1["width"], rect1["height"]
    x2, y2, w2, h2 = rect2["x"], rect2["y"], rect2["width"], rect2["height"]

    # Compute right and bottom edges
    r1_right, r1_bottom = x1 + w1, y1 + h1
    r2_right, r2_bottom = x2 + w2, y2 + h2

    # Check for non-overlapping conditions
    if x1 >= r2_right or x2 >= r1_right:  # One is completely to the right of the other
        return False
    if y1 >= r2_bottom or y2 >= r1_bottom:  # One is completely below the other
        return False

    return True  # They overlap

class WindowHandler:
    """
    Handles a specific window using UIA 3, allowing queries of all controls,
    exporting control information for an LLM prompt, and enabling automation.
    """
    def __init__(self, hwnd):
        """Initialize with a window handle (hwnd)."""
        self.hwnd = hwnd
        self.app = pywinauto.Application(backend="uia").connect(handle=hwnd)
        self.window = self.app.window(handle=hwnd)
        self.controls = None # self.extract_controls()
        self.controls_flat = None # self.extract_controls()
        self.class_name = win32gui.GetClassName(self.hwnd)
        self.title = win32gui.GetWindowText(self.hwnd)

        rect = self.window.rectangle()
        self.rectangle = {"x": int(rect.left), "y": int(rect.top), "width": int(rect.width()), "height": int(rect.height())}

        if (self.class_name == "Shell_TrayWnd"):
            self.title = "Taskbar"

    def __str__(self):
        """Defines a human-readable string representation of the object."""
        return f"WindowHandler(hwnd={self.hwnd}, title='{self.title}')"

    def __repr__(self):
        """Defines a developer-friendly string representation."""
        return f"WindowHandler(hwnd={self.hwnd}, title='{self.title}')"

    def extract_controls(self):
        """Extract all controls (buttons, inputs, etc.) within the window."""
        controls = []

        def _recursive_extract(container, ctrl, level=0):
            try:
                rect = ctrl.rectangle()
                ctrl_info = {}

                ctrl_info["automation_id"] = ctrl.automation_id()
                ctrl_info['class_name'] = ctrl.friendly_class_name()
                try:
                    ctrl_info['control_type'] = ctrl.control_type()
                except:
                    pass

                ctrl_info['rectangle'] = {"x": int(rect.left), "y": int(rect.top), "width": int(rect.width()), "height": int(rect.height())}
                ctrl_info['text'] = str(ctrl.window_text())
                ctrl_info['is_visible'] = ctrl.is_visible()
                ctrl_info['is_enabled'] = ctrl.is_enabled()

                try:
                    ctrl_info['is_clickable'] = ctrl.is_enabled() and ctrl.control_type().lower() in ['button', 'hyperlink']
                except:
                    pass

                try:
                    ctrl_info['is_active'] = ctrl.has_keyboard_focus()
                except:
                    pass

                ctrl_info["native_window"] = ctrl
                ctrl_info["children"] = []

                # controls.append(ctrl_info)
                container.append(ctrl_info)
                for child in ctrl.children():
                    _recursive_extract(ctrl_info["children"], child, level + 1)
            except:
                pass  # Ignore inaccessible controls

        _recursive_extract(controls, self.window)
        return controls

    def get_control_summary(self):
        """Return a formatted summary of controls for an LLM prompt."""
        if (not self.controls):
            self.controls = self.extract_controls()

            # for debug purposes - create a flat list of the controls
            if (True):
                self.controls_flat = []
                def recursive_scan(current_controls):
                    for c in current_controls:
                        self.controls_flat.append(c)
                        recursive_scan(c["children"])
                recursive_scan(self.controls)
                    


        res = []
        for index, c in enumerate(self.controls):
            if c.get("class_name", "") not in [
                "Button",
                "MenuItem",
                "Edit",
                "Document",
                "ListItem",
                "TreeItem",
                "DataItem",
                "Hyperlink",
                "RadioButton",
                "TabItem",
            ]:
                continue

            class_name = c.get('class_name', '').strip('\n').strip('\r').strip()
            text = c.get('text', '').strip('\n').strip('\r').strip()

            # from text, get only first line
            if ('\n' in text or '\r' in text):
                try:
                    text = text.splitlines()[0]
                except:
                    text = ''

            if (len(text) > 50):
                text = text[0:48] + "..."

            text = text.replace("\\", "-")

            if (text):
                desc = f"{text} - {class_name}"
                res.append(f"{index}. {desc}")
                
        return '\n'.join(res)

        return [{"class_name": c.get("class_name", ""), "text": c.get("text", ""), "automation_id": c.get("automation_id", "?")} for c in self.controls]

        return [{"class_name": c.get("class_name", ""), "text": c.get("text", ""), "automation_id": c.get("automation_id", "?")} for c in self.controls]
        return json.dumps(self.controls, indent=2)



    def get_control_summary2(self, max_text_length = 50):
        """Return a formatted summary of controls for an LLM prompt."""
        if (not self.controls):
            self.controls = self.extract_controls()

            # for debug purposes - create a flat list of the controls
            if (True):
                self.controls_flat = []
                def recursive_scan(current_controls):
                    for c in current_controls:
                        self.controls_flat.append(c)
                        recursive_scan(c["children"])
                recursive_scan(self.controls)

        def more_than_half_non_ascii(s: str) -> bool:
            non_ascii_count = sum(1 for char in s if ord(char) > 127)
            return non_ascii_count > len(s) / 2

        def _recursive_scan(text_lines, text_controls, controls, level = 0):
            for c in controls:
                # filter non-visible elements and all their children
                if (c["rectangle"]['width'] and c["rectangle"]['height']):
                    if (not rectangles_overlap(self.rectangle, c["rectangle"])):
                        continue

                # msg = f"{' '*level}{c["text"]} - {c["class_name"]}"
                text = c["text"].strip('\n').strip('\r').strip()
                class_name = c["class_name"].strip('\n').strip('\r').strip()
                auto_id = c["automation_id"]

                # from text, get only first line

                if ('\n' in text or '\r' in text):
                    try:
                        text = text.splitlines()[0]
                    except:
                        text = ''

                if (len(text) > max_text_length):
                    text = text[0:max_text_length-2] + "..."

                text = text.replace("\\", "-")

                if (text and not more_than_half_non_ascii(text)):
                    if class_name in [
                        "Button",
                        "MenuItem",
                        "Edit",
                        "Document",
                        "ListItem",
                        "TreeItem",
                        "DataItem",
                        "Hyperlink",
                        "RadioButton",
                        "TabItem",
                        "Static",
                    ]:
                        index = len(text_lines)
                        # msg = f"{index+1}. {text} - {class_name} - {auto_id}"
                        msg = f"{text} - {class_name}"
                        text_lines.append(msg)
                        res_controls.append(c)
                

                # huristic - it's it's a hyperlink, skip children
                if (c["class_name"] == "Hyperlink"):
                    continue

                _recursive_scan(text_lines, text_controls, c["children"], level+2)


        res_text = []
        res_controls = []
        _recursive_scan(res_text, res_controls, self.controls, 0)

        # new - remove duplicate controls and add the indexes
        counts = Counter(res_text)
        no_dups = [(s,c) for (s, c) in zip(res_text, res_controls) if counts[s] == 1]
        # seperate the list and create the indexes
        res_text = [f"{index+1}. {s}" for index, (s, c) in enumerate(no_dups)]
        res_controls = [c for s, c in no_dups]

        return '\n'.join(res_text), res_controls



    def click_control(self, automation_id):
        """Click a control by matching its Automation ID."""
        try:
            ctrl = self.window.child_window(auto_id=automation_id)
            ctrl.click()
            return True
        except:
            return False

    def type_in_control(self, automation_id, input_text):
        """Type text into a control identified by its Automation ID."""
        try:
            ctrl = self.window.child_window(auto_id=automation_id)
            if ctrl.friendly_class_name().lower() == 'edit':
                ctrl.type_keys(input_text, with_spaces=True)
                return True
        except:
            return False

    def get_window_title(self):
        """Return the window's title."""
        return win32gui.GetWindowText(self.hwnd)

    def activate(self):
        """Activate the window and bring it to the front. If minimized, restore it first."""
        if win32gui.IsIconic(self.hwnd):  # Check if the window is minimized
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)  # Restore window
        try:
            win32gui.SetForegroundWindow(self.hwnd)  # Bring to front
        except:
            pass

class DesktopHandler:
    """
    Handles the entire desktop, tracking all open windows and allowing interaction.
    """
    def __init__(self):
        """Initialize the desktop handler and scan windows."""
        self.windows = self.get_all_windows()
    
    def get_all_windows(self):
        """Retrieve all active windows and store their handlers."""
        # global RG
        windows = []
        def callback(hwnd, extra):
            txt = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            msg = f"{txt}  -- {class_name}  {True if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) else False}"
            # print(msg) 
            # RG.append(msg)
            if (class_name == "Shell_TrayWnd"):
                txt = "Taskbar"
            if win32gui.IsWindowVisible(hwnd) and txt:
                windows.append(WindowHandler(hwnd))
        win32gui.EnumWindows(callback, None)
        return windows
    
    def get_active_window(self):
        """Retrieve the currently active window."""
        hwnd = win32gui.GetForegroundWindow()
        return WindowHandler(hwnd) if hwnd else None
    
    def find_window_by_title(self, title):
        """Find a window by its title."""
        for window in self.windows:
            if title.lower() in window.get_window_title().lower():
                return window
        return None
    
    def list_open_windows(self):
        """Return a list of open window titles."""
        return [win.get_window_title() for win in self.windows]
    
    def take_screenshot(self, filename="screenshot.png"):
        """Capture a screenshot of the entire screen."""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
    
    def bring_window_to_foreground(self, title):
        """Bring a window to the foreground by title."""
        window = self.find_window_by_title(title)
        if window:
            win32gui.SetForegroundWindow(window.hwnd)
            return True
        return False
    
    def get_desktop_summary(self):
        """Return a summary of all open windows for LLM prompt."""
        return json.dumps([{'title': win.get_window_title()} for win in self.windows], indent=2)

    def get_taskbar(self):
        for w in self.windows:
            if (w.class_name == "Shell_TrayWnd"):
                return w
        return None

    def get_mouse_position(self):
         return pyautogui.position()


    def get_control_at_point(self, x:int, y:int):
        # given a location on the screen finds the window and control at that location
        try:
            element_info = UIAElementInfo.from_point(x, y)
            if not element_info:
                return {'error': 'No element found at that point'}, None

            # Find the nearest ancestor with a valid window handle
            current = element_info
            while current and (current.handle is None or current.handle == 0):
                current = current.parent

            if not current or current.handle is None:
                return {'error': 'No ancestor with a valid window handle found'}, None

            # Connect to the application
            try:
                app = Application(backend="uia").connect(handle=current.handle)
                window = app.window(handle=current.handle)
            except Exception:
                window = None

            # Try to wrap the original control (even if it has no handle)
            try:
                control = UIAWrapper(element_info)
            except Exception:
                control = None

            try:
                help_text = control.get_properties().get('help_text', None)
            except Exception:
                help_text = None
            
            # Determine real window title
            try:
                raw_window_title = window.window_text() if window else None
                if window and window.element_info.class_name == "Shell_TrayWnd":
                    raw_window_title = "System Taskbar"
            except Exception:
                raw_window_title = None

            return {
                'window_title': raw_window_title,
                'window_title': window.window_text() if window else None,
                'window_handle': current.handle,
                'control_name': control.window_text() if control else element_info.name,
                'control_type': control.friendly_class_name() if control else element_info.control_type,
                'automation_id': control.automation_id() if control else element_info.automation_id,
                'help_text': help_text,
                'handle': element_info.handle,
                'rectangle': element_info.rectangle
            }

        except Exception as e:
            return {'error': str(e)}, None

