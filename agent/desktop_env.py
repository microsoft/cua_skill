import io
import os
import pyautogui
from .utils.LoggerMessages import *
import subprocess
import win32gui
import win32process
import win32con
import psutil

def enum_windows_for_process(target_process_name):
    windows = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                if target_process_name.lower() in process.name().lower():
                    windows.append(hwnd)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    win32gui.EnumWindows(callback, None)
    return windows

def is_program_running(target_process_name):
    windows = enum_windows_for_process(target_process_name)
    if not windows:
        print(f"No visible windows found for '{target_process_name}'.")
        return False
    else:
        print(f"Found {len(windows)} visible windows for '{target_process_name}'.")
        return True

def is_window_maximized(target_process_name, window_index=0):
    windows = enum_windows_for_process(target_process_name)
    placement = win32gui.GetWindowPlacement(windows[0])
    return placement[1] == win32con.SW_SHOWMAXIMIZED

def maximize_windows_of_process(process_name):
    windows = enum_windows_for_process(process_name)
    if not windows:
        print(f"No visible windows found for '{process_name}'.")
        return
    for hwnd in windows:
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] != win32con.SW_SHOWMAXIMIZED:
            print(f"Maximizing window {hwnd} of {process_name}")
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        else:
            print(f"Window {hwnd} of {process_name} is already maximized.")            

class DesktopEnv:
    def __init__(self, 
        name: str = "DesktopEnv", 
        platform: str = "Windows",
        url: str = None,
        screen_height: int = None,
        screen_width: int = None,
        observation_type: str = "screenshot",
        observe_screenshot_in_bytes: bool = True,
        logger = None
        ):
        self.name = name
        self.platform = platform
        self.url = url
        self.screen_height = screen_height if screen_height is not None else pyautogui.size().height
        self.screen_width = screen_width if screen_width is not None else pyautogui.size().width
        self.observation_type = observation_type
        self.observe_screenshot_in_bytes = observe_screenshot_in_bytes
        self.logger = logger
        self.active_tool = None

    def __repr__(self):
        return f"DesktopEnv: {self.name}, platform: {self.platform}, url: {self.url}, \
                screen_height: {self.screen_height}, screen_width: {self.screen_width}, \
                observation_type: {self.observation_type}"

    def get_observation(self, target_resolution: tuple = None, calibrate_env_before_observe: bool = False) -> dict:
        if calibrate_env_before_observe:
            self.calibrate()
        screenshot_info = self.get_screenshot(target_resolution=target_resolution)
        screenshot = screenshot_info["screenshot"]
        if self.observe_screenshot_in_bytes:
            image_bytes_io = io.BytesIO()
            screenshot.save(image_bytes_io, format="PNG")  # Save the image as a PNG in memory
            screenshot = image_bytes_io.getvalue() 

        return {
            "screenshot": screenshot,
            "screenshot_resolution": screenshot_info["screenshot_resolution"],
        }

    def get_screenshot(self, target_resolution=None):
        screenshot = pyautogui.screenshot()
        if target_resolution is not None:
            screenshot = screenshot.resize(target_resolution)
        width, height = screenshot.size
        return {
            "screenshot": screenshot,
            "screenshot_resolution": (width, height)
        }
    
    def reset(self):
        self.logger.info(LogMessage(message=f"--> Environment Reset", save_to_disk=False))
        pass
    
    def step(self, action):
        try:
            exec(action)
        except Exception as e: 
            self.logger.error(f"{self.name} [red]error[/red] executing action: {action}")

    def launch_tool(self, tool_name, tool_list = None):
        if tool_list is None:
            tool_list = self.tool_list

        def launch(tool):
            if tool["name"].lower() == "settings":
                os.startfile("ms-settings:")
            else:
                executable = tool.get('full_path_executable', tool['executable'])
                if executable is None:
                    return False
                subprocess.Popen(executable)
            return True

        if tool_name not in self.tool_dict:
            self.logger.error(f"[Error] Tool '{tool_name}' not found.")
            return

        tool = self.tool_dict[tool_name]
        self.logger.info(f"[Info] Launching tool '{tool_name}'.")

        launch(tool)
        # Use for calibration
        self.active_tool = tool

    def calibrate(self):
        self.logger.info(LogMessage(message=f"--> Calibrating Environment", save_to_disk=False))

        if not hasattr(self, 'active_tool') or not self.active_tool:
            self.logger.error("[Calibrate] No active tool defined.")
            return

        try:
            # 1. Close unrelated programs
            exclude_list = ['powershell.exe', 'openconsole.exe', 'windowsterminal.exe', 'explorer.exe',
                            'fileexplorer.exe', 'python.exe', 'snippingtool.exe', 'ms-teams.exe']

            # Add active tool process to the exclude list
            tool_name = self.active_tool.get("name", None).lower()

            if tool_name is None:
                self.logger.info("[Calibrate] Active tool name is None. No need to calibrate.")
                return 

            if tool_name == "settings":
                exclude_list.extend(["systemsettings.exe", "applicationframehost.exe"])  # actual Settings process
            else:
                exe = self.active_tool.get('executable')
                if isinstance(exe, list):
                    process_path = exe[0]
                else:
                    process_path = exe
                active_process_name = os.path.basename(process_path).lower()
                exclude_list.append(active_process_name)

            windows = []
            win32gui.EnumWindows(lambda hwnd, _: windows.append(hwnd) if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) else None, None)

            for hwnd in windows:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    name = proc.name().lower()
                    if name not in exclude_list:
                        print(f"[Calibrate] Closing window: {win32gui.GetWindowText(hwnd)} (process: {name})")
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 2. Special handling for Settings
            if tool_name == "settings":
                def find_settings_window():
                    hwnds = []
                    def callback(hwnd, _):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if "settings" in title.lower():
                                hwnds.append(hwnd)
                    win32gui.EnumWindows(callback, None)
                    return hwnds

                hwnds = find_settings_window()

                # Check if it's already in front
                foreground_hwnd = win32gui.GetForegroundWindow()
                if hwnds and foreground_hwnd == hwnds[0]:
                    self.logger.info("[Calibrate] 'Settings' window is already in front. Skipping maximize.")
                    return

                if hwnds:
                    hwnd = hwnds[0]
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    win32gui.SetForegroundWindow(hwnd)
                    self.logger.info("[Calibrate] Maximized and brought 'Settings' to front.")
                else:
                    self.logger.warning("[Calibrate] Could not find 'Settings' window.")
                return


            # 3. Maximize the selected tool
            self.logger.info(f"[Calibrate] Maximizing windows for process: {active_process_name}")
            maximize_windows_of_process(active_process_name)

        except Exception as e:
            self.logger.error(f"[Calibrate] Error while calibrating environment: {e}")

    def tool_is_open(self, tool_name: str, screenshot: bytes = None) -> bool:
        """
        Check if the process corresponding to tool_name has visible windows open.
        """
        tool = self.tool_dict.get(tool_name)
        if not tool:
            self.logger.error(f"[ToolCheck] Tool '{tool_name}' not found in tool list.")
            return False

        # Handle tools with executable as string or list
        exe = tool.get("executable")
        if isinstance(exe, list):
            exe_path = exe[0]
        else:
            exe_path = exe

        process_name = os.path.basename(exe_path).lower()  # normalize
        hwnds = enum_windows_for_process(process_name)
        if not hwnds:
            return False

        # Bring first matching window to front
        hwnd = hwnds[0]
        try:
            # Restore if minimized
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            self.logger.info(f"[ToolCheck] Brought window of '{tool_name}' (process: {process_name}) to front.")
        except Exception as e:
            self.logger.warning(f"[ToolCheck] Could not bring '{tool_name}' to front: {e}")

        return True

    @property
    def tool_list(self):
        return TOOL_LIST
    
    @property
    def tool_dict(self):
        return {tool['name']: tool for tool in TOOL_LIST}

TOOL_LIST = [
    {
        "name": "Microsoft Edge",
        "description": "Web browser for internet access and web-based tasks.",
        "executable": "msedge.exe",
        "full_path_executable": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "capabilities": ["browse", "search", "open URL", "online task"]
    },
    {
        "name": "File Explorer",
        "description": "Used to navigate and manage files and folders.",
        "executable": "explorer.exe",
        "capabilities": ["open folder", "browse files", "move files", "copy files"]
    },
    {
        "name": "Notepad",
        "description": "Lightweight text editor for quick notes or edits.",
        "executable": "notepad.exe",
        "capabilities": ["edit text", "write note", "view .txt"]
    },
    {
        "name": "Calculator",
        "description": "Performs basic and scientific calculations.",
        "executable": "calc.exe",
        "capabilities": ["calculate", "math", "convert units"]
    },
    {
        "name": "Paint",
        "description": "Simple image editing and drawing tool.",
        "executable": "mspaint.exe",
        "capabilities": ["edit image", "draw", "screenshot markup"]
    },
    {
        "name": "PowerPoint",
        "description": "Create and edit presentations.",
        "executable": "powerpnt.exe",
        "full_path_executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\powerpnt.exe",
        "capabilities": ["create slides", "edit presentation", "design slide"]
    },
    {
        "name": "Word",
        "description": "Word processor for rich text documents.",
        "executable": "winword.exe",
        "full_path_executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\winword.exe",
        "capabilities": ["write document", "edit report", "format text"]
    },
    {
        "name": "Excel",
        "description": "Spreadsheet tool for data and analysis.",
        "executable": "excel.exe",
        "full_path_executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\excel.exe",
        "capabilities": ["edit spreadsheet", "calculate table", "plot chart"]
    },
    {
        "name": "Outlook",
        "description": "Email client for managing emails and calendars.",
        "executable": "outlook.exe",
        "full_path_executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\outlook.exe",
        "capabilities": ["send email", "manage calendar", "view email"]
    },
    {
        "name": "Snipping Tool",
        "description": "Capture screenshots or portions of the screen.",
        "executable": "snippingtool.exe",
        "capabilities": ["screenshot", "capture screen"]
    },
    {
        "name": "Settings",
        "description": "Access system settings and configurations.",
        "executable": "ms-settings:",
        "capabilities": ["change settings", "system configuration"]
    },
    {
        "name": "Amazon",
        "Prequisite": "Microsoft Edge",
        "description": "Online shopping platform.",
        "executable": ["C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", "https://www.amazon.com"],
        "capabilities": ["browse", "search", "online shopping"]
    },
    {
        "name": "Bing Search",
        "Prequisite": "Microsoft Edge",
        "description": "Search engine for finding information online.",
        "executable": ["C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", "https://www.bing.com"],
        "capabilities": ["search", "general question and answer", "online task"]
    },
    {
        "name": "MSExpense",
        "description": "Expense management tool for tracking and reporting expenses for Microsoft Employee.",
        "executable": ["C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", "https://myexpense.operations.dynamics.com/"],
        "capabilities": ["expense tracking", "reporting", "Microsoft Employee tool"],
        "RAG": [
        "Create a new expense report",
        "Add expenses to an existing report",
        ]
    },
    {
        "name": "ClipChamp",
        "description": "Screen recording and video editing tool.",
        "executable": None,
        "capabilities": ["screen recording", "video editing"]
    }
    # ,
    # {
    #   "name": "Terminal",
    #   "description": "Windows Terminal for shell or CLI commands.",
    #   "executable": "wt.exe",
    #   "capabilities": ["run command", "terminal", "powershell"]
    # }
]
