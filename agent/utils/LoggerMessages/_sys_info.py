import platform
import socket
import ctypes
import os, sys
from typing import Literal, Dict, List, Optional
from pydantic import Field
from ._base import BaseLogMessage


def get_monitors_info() -> List[Dict[str, int]]:
    """Uses Windows API to get monitor information (number, dimensions)."""
    monitors = []

    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()

    try:
        # Get number of monitors
        monitor_count = user32.GetSystemMetrics(80)  # SM_CMONITORS
    except AttributeError:
        monitor_count = 1  # fallback for older versions

    # Primary screen resolution
    width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    height = user32.GetSystemMetrics(1)  # SM_CYSCREEN

    monitors.append({
        "width": width,
        "height": height,
        "x": 0,
        "y": 0
    })

    return monitors


class SystemInfoMessage(BaseLogMessage):
    type: Literal["system_info"] = "system_info"

    os_name: str = Field(default_factory=platform.system)
    os_version: str = Field(default_factory=platform.version)
    platform_release: str = Field(default_factory=platform.release)
    machine_name: str = Field(default_factory=socket.gethostname)
    processor: str = Field(default_factory=platform.processor)
    architecture: str = Field(default_factory=lambda: platform.architecture()[0])
    python_version: str = Field(default_factory=platform.python_version)
    cpu_count: int = Field(default_factory=lambda: os.cpu_count() or 1)

    monitor_count: int = Field(default_factory=lambda: len(get_monitors_info()))
    monitors: List[Dict[str, int]] = Field(default_factory=get_monitors_info)

    additional_info: Optional[Dict[str, str]] = None

    display_console: bool = False  # Optional to show this in console output
