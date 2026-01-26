from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction 
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

class WindowsSettingsBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="windows_settings",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Settings",
        description="The name of the Windows Settings application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("WindowsSettingsOpenApp")
class WindowsSettingsOpenApp(WindowsSettingsBaseAction, LaunchApplication):
    # Canonical identifiers
    type: str = "windows_settings_open_app"
    
    # Schema payload
    descriptions: List[str] = [
        "Open Windows Settings.",
        "Launch the Settings app.",
        "Start Settings.",
        "Run Windows Settings.",
        "Open the Settings application."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)


@register("WindowsSettingsNavigatePage")
class WindowsSettingsNavigatePage(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_navigate_page"
    page: Argument = Argument(
        value="System > Display",
        description="Settings page path using ' > ' separator for navigation hierarchy. Must match exact page names from Windows Settings. Examples: 'System > Display' for display settings, 'Network & internet > Wi-Fi' for WiFi settings, 'Personalization > Background' for background settings, 'Privacy & security > Camera' for camera privacy settings. Available pages include: System (Display, Sound, Notifications, Power & battery, Storage, Multitasking, Activation, About, Clipboard), Bluetooth & devices (Devices, Bluetooth, Printers & scanners, Mouse, Keyboard, Pen & Windows Ink), Network & internet (Wi-Fi, Ethernet, VPN, Proxy, Dial-up, Mobile hotspot), Personalization (Background, Colors, Themes, Lock screen, Start, Taskbar), Apps (Installed apps, Default apps, Startup), Accounts (Your info, Email & accounts, Sign-in options, Family, Access work or school), Time & language (Date & time, Language & region, Typing), Privacy & security (General, Camera, Microphone, Location, Windows Security, App permissions), Gaming (Game Mode, Xbox Game Bar, Captures), Accessibility (Text size, Narrator, Magnifier, High contrast), Windows Update."
    )

    # Schema payload
    descriptions: List[str] = [
        "Go to Settings page ${{page}}.",
        "Open ${{page}} in Settings.",
        "Navigate to ${{page}} section.",
        "Switch to ${{page}} settings.",
        "Open the ${{page}} panel."
    ]

    def __init__(self, page: str = "System > Display", **kwargs) -> None:
        super().__init__(page=page, **kwargs)
        
        # Parse the page path
        page_parts = str(self.page).split(" > ")
        
        self.add_path(
            "direct_navigation",
            path=[
                SingleClickAction(thought=f"In the Settings window left navigation, click category '{page_parts[0]}' to begin focusing on '{self.page}'."),
                WaitAction(duration=0.5),
                SingleClickAction(thought=f"In the '{page_parts[0]}' section, open sub-page '{page_parts[-1]}' to focus the target settings page '{self.page}'.") if len(page_parts) > 1 else WaitAction(duration=0.2),
                WaitAction(duration=1.0)
            ]
        )


@register("WindowsSettingsToggleSwitch")
class WindowsSettingsToggleSwitch(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_toggle_switch"
    setting_name: Argument = Argument(
        value="Night light",
        description="Name of the toggle switch setting to change its on/off state. Must match the exact label shown in Windows Settings UI. Supported toggles include: 'Night light' (reduces blue light from screen), 'Location services' (allows apps to access device location), 'Camera access' (enables camera for apps), 'Microphone access' (enables microphone for apps), 'Notifications' (shows notification banners), 'HDR' (High Dynamic Range display), 'Game Mode' (optimizes PC for gaming), 'Clipboard history' (saves multiple clipboard items), 'Touchpad' (enables/disables touchpad), 'Battery saver' (reduces background activity to save battery), 'Auto brightness' (adjusts screen brightness automatically), 'Mobile hotspot' (shares internet connection), 'Metered connection' (limits data usage), 'Dark mode' (uses dark theme), 'Focus assist' (silences notifications during certain times), 'Storage Sense' (automatically frees up disk space), 'Windows Spotlight' (shows different lock screen images), 'Taskbar auto-hide' (hides taskbar until mouse hover), 'Show desktop icons' (shows/hides desktop icons), 'Snap windows' (enables window snapping), 'Virtual desktops' (allows multiple desktops), 'Taskbar badges' (shows notification badges), 'Do Not Disturb' (silences all notifications)."
    )

    # Schema payload
    descriptions: List[str] = [
        "Toggle ${{setting_name}}.",
        "Switch ${{setting_name}}.",
        "Change ${{setting_name}} state.",
        "Flip ${{setting_name}}.",
        "Turn ${{setting_name}} on or off."
    ]

    def __init__(self, setting_name: str = "Night light", **kwargs) -> None:
        super().__init__(setting_name=setting_name, **kwargs)
        self.add_path(
            "click_toggle",
            path=[
                SingleClickAction(thought=f"Click on the toggle switch for '{self.setting_name}' to change its state."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsSetValue")
class WindowsSettingsSetValue(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_set_value"
    setting_name: Argument = Argument(
        value="Display brightness",
        description="Name of the setting control to adjust. Must exactly match the label in Windows Settings. Supported settings: 'Display brightness' (screen brightness level), 'Volume' (system sound level), 'Scale' (text and UI scaling), 'Text size' (text scaling only), 'Refresh rate' (monitor refresh rate in Hz), 'Power mode' (performance vs battery mode), 'Screen timeout' (time before screen turns off), 'Output device' (audio output selection), 'Input device' (microphone input selection), 'Mouse pointer size' (cursor size adjustment)."
    )
    value: Argument = Argument(
        value="50%",
        description="The value to set for the specified setting. Format depends on setting_name: For 'Display brightness' use percentage with % symbol (0% to 100%, step 5, e.g., '25%', '50%', '75%'); For 'Volume' use percentage (0% to 100%, step 5, e.g., '30%', '65%'); For 'Scale' use percentage options ('100%', '125%', '150%', '175%', '200%'); For 'Text size' use percentage options ('100%', '110%', '125%', '150%'); For 'Refresh rate' use Hz format ('60 Hz', '75 Hz', '120 Hz', '144 Hz'); For 'Power mode' use full option names ('Best power efficiency', 'Balanced', 'Best performance'); For 'Screen timeout' use time format with unit ('5 minutes', '10 minutes', '15 minutes', '20 minutes', '25 minutes', '30 minutes', 'Never'); For 'Output device' use device name ('Speakers (Realtek® Audio)', 'Headphones (Bluetooth)', 'HDMI (Monitor)'); For 'Input device' use device name ('Microphone Array', 'USB Microphone', 'Line In'); For 'Mouse pointer size' use number (1 to 15, e.g., '1', '8', '15')."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set ${{setting_name}} to ${{value}}.",
        "Change ${{setting_name}} value to ${{value}}.",
        "Update ${{setting_name}} with ${{value}}.",
        "Adjust ${{setting_name}} = ${{value}}.",
        "Apply ${{value}} to ${{setting_name}}."
    ]

    def __init__(self, setting_name: str = "Display brightness", value: str = "50%", **kwargs) -> None:
        super().__init__(setting_name=setting_name, value=value, **kwargs)
        
        # Determine the type of control based on setting name
        setting_str = str(self.setting_name).strip()
        value_str = str(self.value).strip()
        
        # Define settings metadata: control type and any required navigation steps
        # Based on windows_settings_primitive_operation.json
        settings_config = {
            "Display brightness": {
                "control": "slider",
                "nav_steps": [
                    SingleClickAction(thought="Click on 'Night light' to access brightness slider."), WaitAction(duration=0.5),
                    WaitAction(duration=0.2)
                ]
            },
            "Volume": {
                "control": "slider",
                "nav_steps": []
            },
            "Text size": {
                "control": "slider",
                "nav_steps": []
            },
            "Mouse pointer size": {
                "control": "slider",
                "nav_steps": []
            },
            "Scale": {
                "control": "dropdown",
                "nav_steps": []
            },
            "Power mode": {
                "control": "dropdown",
                "nav_steps": []
            },
            "Screen timeout": {
                "control": "dropdown",
                "nav_steps": [
                    SingleClickAction(thought="Click on 'Screen and sleep' to access screen timeout settings."),
                    WaitAction(duration=0.8)
                ]
            },
            "Output device": {
                "control": "dropdown",
                "nav_steps": []
            },
            "Input device": {
                "control": "dropdown",
                "nav_steps": []
            },
            "Refresh rate": {
                "control": "dropdown",
                "nav_steps": [
                    SingleClickAction(thought="Click on 'Advanced display' link to access refresh rate settings."),
                    WaitAction(duration=0.8)
                ]
            }
        }
        
        # Get configuration for this setting
        if setting_str not in settings_config:
            # Fallback: assume it's a simple click-based control
            action_path = [
                SingleClickAction(thought=f"Click on the control for '{self.setting_name}'."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Select or type '{self.value}' for '{self.setting_name}'."),
                WaitAction(duration=0.5)
            ]
            self.add_path("generic_set_value", path=action_path)
            return
        
        config = settings_config[setting_str]
        control_type = config["control"]
        nav_steps = config["nav_steps"]
        
        # Build the complete action path
        action_path = []
        
        # Add navigation steps if needed
        if nav_steps:
            action_path.extend(nav_steps)
        
        # Add control-specific interaction
        if control_type == "dropdown":
            action_path.extend([
                SingleClickAction(thought=f"Click on the '{self.setting_name}' dropdown."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Select '{self.value}' from the dropdown options."),
                WaitAction(duration=0.5)
            ])
            
        elif control_type == "slider":
            action_path.extend([
                SingleClickAction(thought=f"Click on the slider bar for '{self.setting_name}' at the position corresponding to '{self.value}' to set the value directly."),
                WaitAction(duration=0.5)
            ])
        else:
            # Generic text input or other control
            action_path.extend(
                "text_input",
                path=[
                    SingleClickAction(thought=f"Click on the input field for '{self.setting_name}'."),
                    WaitAction(duration=0.3),
                    HotKeyAction(keys=["ctrl", "a"], thought="Select all existing text."),
                    TypeAction(text=value_str, thought=f"Type '{self.value}'."),
                    WaitAction(duration=0.5)
                ]
            )
        self.add_path("set_value", path=action_path)


@register("WindowsSettingsSearchAndNavigate")
class WindowsSettingsSearchAndNavigate(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_search_and_navigate"
    query: Argument = Argument(
        value="Bluetooth",
        description="Keyword or phrase to search within Windows Settings. Use descriptive terms that appear in setting names. Examples: 'Bluetooth' (for Bluetooth settings), 'Wi-Fi' (for wireless network settings), 'Night light' (for blue light filter), 'Display brightness' (for screen brightness control), 'Scale' (for display scaling), 'Text size' (for text scaling), 'Sound output' (for audio output device), 'Microphone' (for microphone settings), 'Notifications' (for notification settings), 'Power & battery' (for power settings), 'Battery saver' (for battery saving mode), 'Sleep' (for sleep settings), 'Language & region' (for language settings), 'Date & time' (for time settings), 'Camera privacy' (for camera permissions), 'Microphone privacy' (for microphone permissions), 'Location privacy' (for location services), 'Personalization background' (for wallpaper settings), 'Themes' (for theme settings), 'HDR' (for HDR display settings), 'Game Mode' (for gaming optimization), 'Clipboard history' (for clipboard settings), 'VPN' (for VPN settings), 'Ethernet' (for wired network settings), 'Mobile hotspot' (for hotspot settings), 'Mouse pointer size' (for cursor size), 'Accessibility' (for accessibility features), 'Windows Update' (for system updates), 'Storage' (for disk storage), 'Default apps' (for default program settings), 'Startup apps' (for startup programs), 'Dark mode' (for dark theme), 'Focus assist' (for do not disturb), 'Taskbar' (for taskbar settings), 'Start menu' (for start menu customization), 'Lock screen' (for lock screen settings), 'Proxy settings' (for network proxy), 'Sign-in options' (for login settings)."
    )

    # Schema payload
    descriptions: List[str] = [
        "Search Settings for ${{query}} and navigate to it.",
        "Look up ${{query}} in Settings and open it.",
        "Find ${{query}} option and navigate to it.",
        "Search for ${{query}} within Settings and open it.",
        "Locate ${{query}} setting and navigate to it."
    ]

    def __init__(self, query: str = "Bluetooth", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "search_and_navigate",
            path=[
                SingleClickAction(thought="Click on the search box at the top of Settings."),
                WaitAction(duration=0.3),
                TypeAction(text=str(self.query), thought=f"Type '{self.query}' in the search box."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on the '{self.query}' search result to navigate to that settings page."),
                WaitAction(duration=1.0)
            ]
        )


@register("WindowsSettingsResetToDefault")
class WindowsSettingsResetToDefault(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_reset_to_default"
    setting_name: Argument = Argument(
        value="Display brightness",
        description="Name of the setting to reset to its default value. Must match the exact setting name in Windows Settings. Resettable settings include: 'Display brightness', 'Volume', 'Scale', 'Text size', 'Refresh rate', 'Power mode', 'Screen timeout (on battery)', 'Screen timeout (plugged in)', 'Output device', 'Input device', 'Mouse pointer size', 'DNS mode', 'Proxy', 'Wallpaper fit', 'Date & time format', 'Night light', 'Location services', 'Camera access', 'Microphone access', 'Notifications', 'HDR', 'Game Mode', 'Clipboard history', 'Touchpad', 'Battery saver', 'Auto brightness', 'Mobile hotspot', 'Metered connection'."
    )

    # Schema payload
    descriptions: List[str] = [
        "Reset ${{setting_name}} to default.",
        "Restore default for ${{setting_name}}.",
        "Reset setting ${{setting_name}}.",
        "Go back to default for ${{setting_name}}.",
        "Return ${{setting_name}} to default state."
    ]

    def __init__(self, setting_name: str = "Display brightness", **kwargs) -> None:
        super().__init__(setting_name=setting_name, **kwargs)
        self.add_path(
            "click_reset_button",
            path=[
                SingleClickAction(thought=f"Click on the 'Reset' or 'Restore default' button for '{self.setting_name}'."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsCheckForUpdates")
class WindowsSettingsCheckForUpdates(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_check_for_updates"

    # Schema payload
    descriptions: List[str] = [
        "Check for Windows updates.",
        "Search for updates.",
        "Check for system updates.",
        "Look for Windows updates.",
        "Scan for available updates."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_check_updates",
            path=[
                SingleClickAction(thought="Click on the 'Check for updates' button."),
                WaitAction(duration=2.0)
            ]
        )


@register("WindowsSettingsChangeTheme")
class WindowsSettingsChangeTheme(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_change_theme"
    theme: Argument = Argument(
        value="Dark",
        description="Windows theme/mode to apply. Available options: 'Light' (light theme for all system UI), 'Dark' (dark theme for all system UI), 'Custom' (custom theme allowing separate app/system mode). Use exact capitalization as shown."
    )

    # Schema payload
    descriptions: List[str] = [
        "Change theme to ${{theme}}.",
        "Set theme to ${{theme}}.",
        "Apply ${{theme}} theme.",
        "Switch to ${{theme}} theme.",
        "Use ${{theme}} theme."
    ]

    def __init__(self, theme: str = "Dark", **kwargs) -> None:
        super().__init__(theme=theme, **kwargs)
        self.add_path(
            "select_theme",
            path=[
                SingleClickAction(thought=f"Click on the '{self.theme}' theme option or dropdown."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsChangeAccentColor")
class WindowsSettingsChangeAccentColor(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_change_accent_color"
    color: Argument = Argument(
        value="Blue",
        description="Windows accent color to apply. Available preset colors: 'Blue' (default Windows blue), 'Red' (red accent), 'Green' (green accent), 'Purple' (purple accent), 'Orange' (orange accent), 'Pink' (pink accent), 'Gray' (gray accent), 'Custom' (custom RGB color - requires additional color picker interaction). Use exact capitalization as shown."
    )

    # Schema payload
    descriptions: List[str] = [
        "Change accent color to ${{color}}.",
        "Set accent color to ${{color}}.",
        "Apply ${{color}} accent color.",
        "Use ${{color}} as accent.",
        "Switch accent color to ${{color}}."
    ]

    def __init__(self, color: str = "Blue", **kwargs) -> None:
        super().__init__(color=color, **kwargs)
        self.add_path(
            "select_color",
            path=[
                SingleClickAction(thought=f"Click on the '{self.color}' color option in the accent color picker."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsAddLanguage")
class WindowsSettingsAddLanguage(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_add_language"
    language: Argument = Argument(
        value="Spanish (Spain)",
        description="Language pack to add to Windows. Use full language name with region in parentheses format. Available languages: 'English (United States)', 'Spanish (Spain)', 'French (France)', 'German (Germany)', 'Chinese (Simplified)', 'Chinese (Traditional)', 'Japanese', 'Korean', 'Portuguese (Brazil)', 'Russian', 'Italian', 'Arabic', 'Hindi', 'Dutch', 'Polish', 'Turkish'. Must match exact format with region specification where applicable."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add language ${{language}}.",
        "Install language ${{language}}.",
        "Add ${{language}} to Windows.",
        "Install ${{language}} language pack.",
        "Add ${{language}} language support."
    ]

    def __init__(self, language: str = "Spanish (Spain)", **kwargs) -> None:
        super().__init__(language=language, **kwargs)
        self.add_path(
            "add_language_flow",
            path=[
                SingleClickAction(thought="Click on the 'Add a language' button."),
                WaitAction(duration=0.5),
                TypeAction(text=str(self.language), thought=f"Type '{self.language}' in the search box."),
                WaitAction(duration=0.5),
                SingleClickAction(thought=f"Click on '{self.language}' in the search results."),
                WaitAction(duration=0.3),
                SingleClickAction(thought="Click 'Next' or 'Install' button."),
                WaitAction(duration=2.0)
            ]
        )


@register("WindowsSettingsRemoveLanguage")
class WindowsSettingsRemoveLanguage(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_remove_language"
    language: Argument = Argument(
        value="Spanish (Spain)",
        description="Language pack to remove from Windows. Use full language name with region in parentheses format. Must match one of the installed languages: 'English (United States)', 'Spanish (Spain)', 'French (France)', 'German (Germany)', 'Chinese (Simplified)', 'Chinese (Traditional)', 'Japanese', 'Korean', 'Portuguese (Brazil)', 'Russian', 'Italian', 'Arabic', 'Hindi', 'Dutch', 'Polish', 'Turkish'. Must match exact format with region specification where applicable."
    )

    # Schema payload
    descriptions: List[str] = [
        "Remove language ${{language}}.",
        "Uninstall language ${{language}}.",
        "Delete ${{language}} from Windows.",
        "Remove ${{language}} language pack.",
        "Uninstall ${{language}} language support."
    ]

    def __init__(self, language: str = "Spanish (Spain)", **kwargs) -> None:
        super().__init__(language=language, **kwargs)
        self.add_path(
            "remove_language_flow",
            path=[
                SingleClickAction(thought=f"Click on '{self.language}' in the language list."),
                WaitAction(duration=0.3),
                SingleClickAction(thought="Click on the three-dot menu or 'Remove' button."),
                WaitAction(duration=0.3),
                SingleClickAction(thought="Click 'Remove' to confirm."),
                WaitAction(duration=1.0)
            ]
        )


@register("WindowsSettingsSetDisplayLanguage")
class WindowsSettingsSetDisplayLanguage(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_set_display_language"
    language: Argument = Argument(
        value="English (United States)",
        description="Display language for Windows system UI and menus. Must be one of the installed languages. Available options: 'English (United States)', 'Spanish (Spain)', 'French (France)', 'German (Germany)', 'Chinese (Simplified)', 'Chinese (Traditional)', 'Japanese', 'Korean', 'Portuguese (Brazil)', 'Russian', 'Italian', 'Arabic'. This requires the language pack to be already installed. Use exact format with region specification."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set display language to ${{language}}.",
        "Change Windows language to ${{language}}.",
        "Switch display language to ${{language}}.",
        "Use ${{language}} as display language.",
        "Set system language to ${{language}}."
    ]

    def __init__(self, language: str = "English (United States)", **kwargs) -> None:
        super().__init__(language=language, **kwargs)
        self.add_path(
            "set_display_language",
            path=[
                SingleClickAction(thought="Click on the 'Windows display language' dropdown."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Click on '{self.language}' in the dropdown."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsSetTimeZone")
class WindowsSettingsSetTimeZone(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_set_timezone"
    timezone: Argument = Argument(
        value="(UTC-08:00) Pacific Time (US & Canada)",
        description="Time zone to set for the system. Must use exact format with UTC offset and location. Available time zones: '(UTC-12:00) International Date Line West', '(UTC-08:00) Pacific Time (US & Canada)', '(UTC-07:00) Mountain Time (US & Canada)', '(UTC-06:00) Central Time (US & Canada)', '(UTC-05:00) Eastern Time (US & Canada)', '(UTC+00:00) Dublin, Edinburgh, Lisbon, London', '(UTC+01:00) Amsterdam, Berlin, Bern, Rome', '(UTC+08:00) Beijing, Chongqing, Hong Kong, Urumqi', '(UTC+09:00) Tokyo, Seoul', '(UTC+10:00) Canberra, Melbourne, Sydney'. Use exact format including UTC offset and location names."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set time zone to ${{timezone}}.",
        "Change time zone to ${{timezone}}.",
        "Switch to ${{timezone}} time zone.",
        "Update time zone to ${{timezone}}.",
        "Use ${{timezone}} time zone."
    ]

    def __init__(self, timezone: str = "(UTC-08:00) Pacific Time (US & Canada)", **kwargs) -> None:
        super().__init__(timezone=timezone, **kwargs)
        self.add_path(
            "set_timezone",
            path=[
                SingleClickAction(thought="Click on the 'Time zone' dropdown."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Click on '{self.timezone}' in the dropdown list."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsSetDefaultApp")
class WindowsSettingsSetDefaultApp(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_set_default_app"
    file_type: Argument = Argument(
        value="Web browser",
        description="Type of file or protocol to set default application for. Available categories: 'Web browser' (HTTP/HTTPS links), 'Email' (mailto links and email files), 'Music player' (audio files like MP3, WAV), 'Video player' (video files like MP4, AVI), 'Photo viewer' (image files like JPG, PNG), 'PDF reader' (PDF documents), 'Maps' (location/map links), 'Calendar' (calendar files and events). Use exact category name as shown."
    )
    app_name: Argument = Argument(
        value="Microsoft Edge",
        description="Name of the application to set as default handler. Must be an installed application on the system. Common examples: For web browser: 'Microsoft Edge', 'Google Chrome', 'Mozilla Firefox'; For email: 'Outlook', 'Mail', 'Thunderbird'; For music: 'Windows Media Player', 'Groove Music', 'VLC media player'; For video: 'Movies & TV', 'VLC media player', 'Windows Media Player'; For photos: 'Photos', 'Paint', 'Adobe Photoshop'; For PDF: 'Microsoft Edge', 'Adobe Acrobat Reader', 'Chrome'. Use the exact application name as it appears in Windows."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set default app for ${{file_type}} to ${{app_name}}.",
        "Change default ${{file_type}} app to ${{app_name}}.",
        "Make ${{app_name}} default for ${{file_type}}.",
        "Use ${{app_name}} for ${{file_type}} by default.",
        "Set ${{app_name}} as default ${{file_type}} handler."
    ]

    def __init__(self, file_type: str = "Web browser", app_name: str = "Microsoft Edge", **kwargs) -> None:
        super().__init__(file_type=file_type, app_name=app_name, **kwargs)
        self.add_path(
            "set_default_app",
            path=[
                SingleClickAction(thought=f"Click on the current default app for '{self.file_type}'."),
                WaitAction(duration=0.5),
                SingleClickAction(thought=f"Select '{self.app_name}' from the list of available apps."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsToggleStartupApp")
class WindowsSettingsToggleStartupApp(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_toggle_startup_app"
    app_name: Argument = Argument(
        value="OneDrive",
        description="Name of the application to enable or disable at Windows startup. Must match the exact name shown in the Startup apps list. Common startup apps include: 'OneDrive' (Microsoft cloud storage), 'Microsoft Teams' (communication app), 'Spotify' (music player), 'Discord' (chat app), 'Steam' (game platform), 'Adobe Creative Cloud' (Adobe services), 'Dropbox' (cloud storage), 'Slack' (work communication), 'Zoom' (video conferencing). The app must be installed and appear in the startup apps list. Use exact application name as it appears in the list."
    )

    # Schema payload
    descriptions: List[str] = [
        "Toggle ${{app_name}} startup.",
        "Toggle startup for ${{app_name}}.",
        "Switch ${{app_name}} startup state.",
        "Change ${{app_name}} startup status.",
        "Toggle whether ${{app_name}} starts on boot."
    ]

    def __init__(self, app_name: str = "OneDrive", **kwargs) -> None:
        super().__init__(app_name=app_name, **kwargs)
        self.add_path(
            "toggle_startup_app",
            path=[
                SingleClickAction(thought=f"Click on the toggle switch for '{self.app_name}' to change its startup state."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsRenamePC")
class WindowsSettingsRenamePC(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_rename_pc"
    new_name: Argument = Argument(
        value="MyPC",
        description="New name for the computer. Must be a valid Windows computer name: alphanumeric characters only (letters A-Z, a-z, numbers 0-9, hyphens allowed), maximum 15 characters, no spaces or special characters except hyphens. Examples: 'MyPC', 'WorkLaptop', 'Home-Desktop', 'Gaming-Rig', 'Office-PC'. The name should be descriptive and unique on the network."
    )

    # Schema payload
    descriptions: List[str] = [
        "Rename PC to ${{new_name}}.",
        "Change computer name to ${{new_name}}.",
        "Set PC name to ${{new_name}}.",
        "Rename this PC to ${{new_name}}.",
        "Change device name to ${{new_name}}."
    ]

    def __init__(self, new_name: str = "MyPC", **kwargs) -> None:
        super().__init__(new_name=new_name, **kwargs)
        self.add_path(
            "rename_pc",
            path=[
                SingleClickAction(thought="Click on the 'Rename this PC' button."),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["ctrl", "a"], thought="Select all text in the name field."),
                TypeAction(text=str(self.new_name), thought=f"Type the new PC name '{self.new_name}'."),
                WaitAction(duration=0.3),
                SingleClickAction(thought="Click 'Next' or 'Save' button."),
                WaitAction(duration=1.0)
            ]
        )


@register("WindowsSettingsConfigureNotifications")
class WindowsSettingsConfigureNotifications(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_configure_notifications"
    app_name: Argument = Argument(
        value="Microsoft Teams",
        description="Name of the application to configure notification settings for. Must match the exact app name shown in Windows notification settings. Common apps: 'Microsoft Teams' (work communication), 'Outlook' (email), 'Microsoft Edge' (browser), 'Chrome' (browser), 'Spotify' (music), 'Discord' (chat), 'Slack' (work chat), 'WhatsApp' (messaging), 'Telegram' (messaging), 'Mail' (Windows mail app), 'Calendar' (Windows calendar), 'Photos' (Windows photos app), 'Windows Security' (antivirus), 'Microsoft Store' (app store). The app must be installed and have notification permissions. Use exact name as shown in the notifications list."
    )

    # Schema payload
    descriptions: List[str] = [
        "Toggle notifications for ${{app_name}}.",
        "Toggle ${{app_name}} notifications.",
        "Switch ${{app_name}} notification state.",
        "Change ${{app_name}} notification status.",
        "Configure notifications for ${{app_name}}."
    ]

    def __init__(self, app_name: str = "Microsoft Teams", **kwargs) -> None:
        super().__init__(app_name=app_name, **kwargs)
        self.add_path(
            "configure_notifications",
            path=[
                SingleClickAction(thought=f"Click on '{self.app_name}' in the notifications list."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Click on the toggle to change notification state for '{self.app_name}'."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsSetFocusAssist")
class WindowsSettingsSetFocusAssist(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_set_focus_assist"
    mode: Argument = Argument(
        value="Priority only",
        description="Focus Assist mode to control notification behavior. Available modes: 'Off' (all notifications shown normally), 'Priority only' (only priority notifications from selected contacts and apps), 'Alarms only' (only alarms, no other notifications). Use exact capitalization and full mode name as shown."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set Focus Assist to ${{mode}}.",
        "Change Focus Assist mode to ${{mode}}.",
        "Switch Focus Assist to ${{mode}}.",
        "Configure Focus Assist as ${{mode}}.",
        "Use ${{mode}} Focus Assist."
    ]

    def __init__(self, mode: str = "Priority only", **kwargs) -> None:
        super().__init__(mode=mode, **kwargs)
        self.add_path(
            "set_focus_assist",
            path=[
                SingleClickAction(thought=f"Click on the '{self.mode}' option in Focus Assist settings."),
                WaitAction(duration=0.5)
            ]
        )

@register("WindowsSettingsConfigureMouseSpeed")
class WindowsSettingsConfigureMouseSpeed(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_configure_mouse_speed"
    speed: Argument = Argument(
        value="6 (Medium)",
        description="Mouse pointer speed level from 1 (slowest) to 11 (fastest). Use format: number followed by descriptor in parentheses. Available options: '1 (Slow)', '2', '3', '4', '5', '6 (Medium)', '7', '8', '9', '10', '11 (Fast)'. The middle value '6 (Medium)' is the default setting. Use exact format with number and descriptor as shown."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set mouse speed to ${{speed}}.",
        "Change mouse pointer speed to ${{speed}}.",
        "Adjust mouse sensitivity to ${{speed}}.",
        "Configure mouse speed as ${{speed}}.",
        "Set cursor speed to ${{speed}}."
    ]

    def __init__(self, speed: str = "6 (Medium)", **kwargs) -> None:
        super().__init__(speed=speed, **kwargs)
        self.add_path(
            "set_mouse_speed",
            path=[
                SingleClickAction(thought=f"Click and drag the mouse speed slider to '{self.speed}'."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsEnableRemoteDesktop")
class WindowsSettingsEnableRemoteDesktop(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_enable_remote_desktop"

    # Schema payload
    descriptions: List[str] = [
        "Enable Remote Desktop.",
        "Turn on Remote Desktop.",
        "Activate Remote Desktop.",
        "Allow Remote Desktop connections.",
        "Enable RDP."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "enable_rdp",
            path=[
                SingleClickAction(thought="Click the toggle to enable Remote Desktop."),
                WaitAction(duration=0.5),
                SingleClickAction(thought="If confirmation dialog appears, click 'Confirm' or 'OK'."),
                WaitAction(duration=0.5)
            ]
        )


@register("WindowsSettingsDisableRemoteDesktop")
class WindowsSettingsDisableRemoteDesktop(WindowsSettingsBaseAction):
    # Canonical identifiers
    type: str = "windows_settings_disable_remote_desktop"

    # Schema payload
    descriptions: List[str] = [
        "Disable Remote Desktop.",
        "Turn off Remote Desktop.",
        "Deactivate Remote Desktop.",
        "Disallow Remote Desktop connections.",
        "Disable RDP."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "disable_rdp",
            path=[
                SingleClickAction(thought="Click the toggle to disable Remote Desktop."),
                WaitAction(duration=0.5)
            ]
        )