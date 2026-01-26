from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction 
from .common_action import LaunchApplication, OpenRun, SwitchtoFocusApp, MaximizeActiveWindow
from .argument import Argument

__all__ = []

class VLCBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="vlc",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="VLC Media Player",
        description="The name of the VLC application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register("VLCOpenMediaFile")
class VLCOpenMediaFile(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_open_media_file"
    file_path: Argument = Argument(
        value="C:\\Users\\Docker\\Videos\\sample.mp4",
        description="Full absolute path to the media file to open in VLC. Must be a valid Windows path with drive letter. Supports various media formats: video files (.mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .m4v, .mpg, .mpeg), audio files (.mp3, .wav, .flac, .aac, .ogg, .wma, .m4a), and other media containers. Use double backslashes (\\\\) for Windows paths. Examples: 'C:\\\\Users\\\\Docker\\\\Videos\\\\movie.mp4', 'D:\\\\Music\\\\song.mp3', 'C:\\\\Media\\\\video.mkv'. The file must exist at the specified location."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open media file ${{file_path}}.",
        "Play file ${{file_path}}.",
        "Open ${{file_path}} in VLC.",
        "Load media ${{file_path}}.",
        "Start playing ${{file_path}}."
    ]

    def __init__(self, file_path: str = "C:\\Users\\Docker\\Videos\\sample.mp4", **kwargs) -> None:
        super().__init__(file_path=file_path, **kwargs)
        file_path_value = self.file_path.value if hasattr(self.file_path, 'value') else self.file_path
        self.add_path(
            "open_media_file",
            path=[
                OpenRun(thought=f"Open the Run dialog to launch {self.application_name}."),
                WaitAction(duration=1.0),
                TypeAction(text=f"vlc {file_path_value}", thought=f"Type the file path '{file_path_value}' into the Run dialog.", input_mode="copy_paste"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to open the media file in VLC."),
                WaitAction(duration=3.0)
            ]
        )

@register("VLCSetInterfaceSettingsWithCheckbox")
class VLCSetInterfaceSettingsWithCheckbox(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_set_interface_settings_with_checkbox"
    setting_name: Argument = Argument(
        value="Start in minimal view mode",
        description="Name of the checkbox setting in VLC Simple Preferences Interface tab. Available options in 'Look and feel' section: 'Show controls in full screen mode', 'Integrate video in interface', 'Start in minimal view mode', 'Show systray icon', 'Resize interface to video size', 'Pause playback when minimized', 'Use a dark palette'. Available options in 'Playlist and Instances' section: 'Allow only one instance', 'Use only one instance when started from file manager', 'Display playlist tree', 'Enqueue items into playlist in one instance mode', 'Pause on the last frame of a video'. Available options in 'Privacy / Network Interaction' section: 'Activate updates notifier', 'Save recently played items', 'Allow metadata network access'. Use exact checkbox label text."
    )
    enable: Argument = Argument(
        value=True,
        description="Whether to enable (check) or disable (uncheck) the setting. True = check/enable the checkbox, False = uncheck/disable the checkbox."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set ${{setting_name}} to ${{enable}}.",
        "Toggle ${{setting_name}} setting.",
        "Change ${{setting_name}} preference.",
        "Configure ${{setting_name}} option.",
        "Modify ${{setting_name}} in preferences."
    ]

    def __init__(self, setting_name: str = "Start in minimal view mode", enable: bool = True, **kwargs) -> None:
        super().__init__(setting_name=setting_name, enable=enable, **kwargs)
        enable_value = self.enable.value if hasattr(self.enable, 'value') else self.enable
        setting_name_value = self.setting_name.value if hasattr(self.setting_name, 'value') else self.setting_name
        action_word = "check/enable" if enable_value else "uncheck/disable"
        self.add_path(
            "set_interface_checkbox",
            path=[
                HotKeyAction(keys=["ctrl", "p"], thought="Press Ctrl+P to open VLC Simple Preferences."),
                WaitAction(duration=2.0),
                SingleClickAction(thought="Click on 'Interface' tab at the top of the preferences window."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on the checkbox '{setting_name_value}' to {action_word} it."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Save' button to apply the setting."),
                WaitAction(duration=2.0)
            ]
        )

@register("VLCPlayPause")
class VLCPlayPause(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_play_pause"

    # Schema payload
    descriptions: List[str] = [
        "Play/Pause.",
        "Toggle playback.",
        "Pause or resume.",
        "Toggle Play/Pause.",
        "Hit play/pause button."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_play_pause",
            path=[
                HotKeyAction(keys=["space"], thought="Press Space to toggle play/pause."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_play_pause",
            path=[
                SingleClickAction(thought="Click the Play/Pause button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCStop")
class VLCStop(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_stop"

    # Schema payload
    descriptions: List[str] = [
        "Stop playback.",
        "Stop the media.",
        "End playback now.",
        "Stop player.",
        "Stop video."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_stop",
            path=[
                HotKeyAction(keys=["s"], thought="Press 's' to stop playback."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_stop",
            path=[
                SingleClickAction(thought="Click the Stop button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCToggleMute")
class VLCToggleMute(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_toggle_mute"

    # Schema payload
    descriptions: List[str] = [
        "Toggle mute.",
        "Mute/unmute audio.",
        "Audio mute on/off.",
        "Silence/restore audio.",
        "Mute sound."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_mute",
            path=[
                HotKeyAction(keys=["m"], thought="Press 'm' to toggle mute."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_mute",
            path=[
                SingleClickAction(thought="Click the mute button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCToggleFullscreen")
class VLCToggleFullscreen(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_toggle_fullscreen"

    # Schema payload
    descriptions: List[str] = [
        "Toggle fullscreen.",
        "Enter/exit fullscreen.",
        "Fullscreen on/off.",
        "Switch fullscreen mode.",
        "Go fullscreen."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_fullscreen",
            path=[
                HotKeyAction(keys=["f"], thought="Press 'f' to toggle fullscreen mode."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_fullscreen",
            path=[
                SingleClickAction(thought="Click the fullscreen button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCAdjustVolume")
class VLCAdjustVolume(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_adjust_volume"
    value: Argument = Argument(
        value=50,
        description="Volume level to set in VLC. Must be an integer from 0 to 125 (VLC allows volume up to 125% for amplification). 0 = muted/silent, 50 = half volume, 100 = normal/default volume (100%), 125 = maximum amplified volume. Common values: 0 (mute), 25 (quiet), 50 (medium), 75 (loud), 100 (normal max), 125 (amplified max). Use integer numbers only without % symbol."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set volume to ${{value}}%.",
        "Adjust volume ${{value}} percent.",
        "Volume level ${{value}}%.",
        "Use ${{value}}% volume.",
        "Change volume to ${{value}}%."
    ]

    def __init__(self, value: int = 50, **kwargs) -> None:
        super().__init__(value=value, **kwargs)
        value_actual = self.value.value if hasattr(self.value, 'value') else self.value
        self.add_path(
            "click_volume_slider",
            path=[
                SingleClickAction(thought=f"Click on the volume slider to set volume to {value_actual}%. (volume range: 0% to 125%)."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCSetMaxVolume")
class VLCSetMaxVolume(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_set_max_volume"
    value: Argument = Argument(
        value=200,
        description="Maximum volume level to set in VLC preferences. Must be an integer from 100 to 200 (VLC allows volume amplification up to 200% through preferences). 100 = normal/default maximum volume (100%), 125 = standard amplified volume, 150 = high amplification, 200 = maximum possible amplification (200%). This setting changes the maximum volume limit in VLC preferences, allowing the volume slider to go beyond the normal 100% limit. Use this when you need louder audio output for quiet media files. Use integer numbers only without % symbol."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set max volume to ${{value}}%.",
        "Increase max volume to ${{value}} percent.",
        "Set maximum volume level to ${{value}}%.",
        "Change max volume limit to ${{value}}%.",
        "Allow volume up to ${{value}}%.",
        "Amplify volume to ${{value}}%.",
        "Set volume amplification to ${{value}}%."
    ]

    def __init__(self, value: int = 200, **kwargs) -> None:
        super().__init__(value=value, **kwargs)
        value_actual = self.value.value if hasattr(self.value, 'value') else self.value
        self.add_path(
            "menu_set_max_volume",
            path=[
                HotKeyAction(keys=["ctrl", "p"], thought="Press Ctrl+P to open VLC preferences."),
                WaitAction(duration=2.0),
                MaximizeActiveWindow(thought="Maximize the preferences window to show all settings without scrolling."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'All' radio button at the bottom left to show all settings (Simple/All toggle)."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on the search box at the top of the preferences window."),
                WaitAction(duration=1.0),
                TypeAction(text="Qt", thought="Type 'Qt' to search for Qt interface settings."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Qt' in the search results to show Qt interface settings."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on the 'Maximum Volume displayed' input field."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"], thought="Select all text in the max volume input field."),
                WaitAction(duration=0.5),
                TypeAction(text=str(value_actual), thought=f"Type the maximum volume value '{value_actual}'."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Save' button to apply the new maximum volume setting."),
                WaitAction(duration=2.0)
            ]
        )


@register("VLCChangePlaybackSpeed")
class VLCChangePlaybackSpeed(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_change_playback_speed"
    action: Argument = Argument(
        value="Speed up",
        description="Direction to adjust playback speed. Use one of these exact values: 'Speed up' (increase playback speed, play faster, accelerate), 'Slow down' (decrease playback speed, play slower, decelerate), 'Faster' (same as speed up), 'Slower' (same as slow down), 'Increase' (make faster), 'Decrease' (make slower). This incrementally adjusts speed by one step each time. Common use cases: speed up for quickly reviewing content, slow down for detailed analysis or learning."
    )

    # Schema payload
    descriptions: List[str] = [
        "${{action}} playback speed.",
        "${{action}} the playback.",
        "${{action}} playback rate.",
        "Make playback ${{action}}.",
        "${{action}} speed."
    ]

    def __init__(self, action: str = "Speed up", **kwargs) -> None:
        super().__init__(action=action, **kwargs)
        
        # Determine if we should speed up or slow down based on action parameter
        action_value = self.action.value if hasattr(self.action, 'value') else self.action
        is_speed_up = str(action_value).lower() in ["speed up", "increase", "faster"]
        
        self.add_path(
            "hotkey_speed_adjust",
            path=[
                HotKeyAction(keys=["+"] if is_speed_up else ["-"], 
                            thought=f"{action_value} playback speed using +/- keys."),
                WaitAction(duration=1.0)
            ]
        )
        
        self.add_path(
            "menu_speed_adjust",
            path=[
            SingleClickAction(thought="Click on Playback menu."),
            WaitAction(duration=1.0),
            SingleClickAction(thought="Click on Speed submenu."),
            WaitAction(duration=1.0),
            SingleClickAction(thought=f"Click on {'Faster' if is_speed_up else 'Slower'} speed option."),
            WaitAction(duration=1.0)
            ]
        )

@register("VLCSeekToTime")
class VLCSeekToTime(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_seek_to_time"
    time: Argument = Argument( 
        value="00:00:00",
        description="Timestamp to seek/jump to in the media. Must use exact format HH:MM:SS (hours:minutes:seconds) with leading zeros and colons as separators. Hours: 00-23, Minutes: 00-59, Seconds: 00-59. Examples: '00:00:00' (start of video), '00:01:23' (1 minute 23 seconds), '00:30:45' (30 minutes 45 seconds), '01:15:30' (1 hour 15 minutes 30 seconds), '02:00:00' (2 hours). This allows precise navigation to any point in the media timeline."
    )

    # Schema payload
    descriptions: List[str] = [
        "Seek to ${{time}}.",
        "Jump to ${{time}}.",
        "Seek position ${{time}}.",
        "Go to ${{time}}.",
        "Skip to ${{time}}."
    ]

    def __init__(self, time: str = "00:00:00", **kwargs) -> None: 
        super().__init__(time=time, **kwargs)
        time_value = self.time.value if hasattr(self.time, 'value') else self.time
        self.add_path(
            "hotkey_seek",
            path=[
                HotKeyAction(keys=["ctrl", "t"], thought="Press Ctrl+T to open seek dialog."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on the time input field in the seek dialog."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"], thought="Select existing time in the input field."),
                WaitAction(duration=1.0),
                TypeAction(text=time_value, thought=f"Type the time {time_value}."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to seek to the specified time."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_seek",
            path=[
                SingleClickAction(thought="Click on the Playback menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Jump to Specific Time' submenu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on the time input field in the seek dialog."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"], thought="Select existing time in the input field."),
                WaitAction(duration=1.0),
                TypeAction(text=time_value, thought=f"Type the time {time_value}."), 
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to confirm."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCSnapshot")
class VLCSnapshot(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_snapshot"

    # Schema payload
    descriptions: List[str] = [
        "Take video snapshot.",
        "Capture frame image.",
        "Snapshot current frame.",
        "Save a snapshot.",
        "Take screenshot."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_snapshot",
            path=[
                HotKeyAction(keys=["shift", "s"], thought="Press Shift+S to take a snapshot."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_snapshot",
            path=[
                SingleClickAction(thought="Click on the Video menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Take Snapshot' option."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCOpenSubtitleFile")
class VLCOpenSubtitleFile(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_open_subtitle_file"
    file_name: Argument = Argument(
        value="subtitle.srt",
        description="Name of the subtitle file including extension. Common subtitle formats: .srt (SubRip, most common), .sub (MicroDVD/SubViewer), .ass/.ssa (Advanced SubStation Alpha, supports styling), .vtt (WebVTT), .idx/.sub (DVD subtitles). Examples: 'movie.srt', 'episode_01.ass', 'subtitles_english.vtt', 'film.sub'. The filename should match or relate to the video file for easy identification."
    )
    file_path: Argument = Argument(
        value="C:\\Users\\Docker\\Videos",
        description="Full absolute directory path containing the subtitle file. Must be a valid Windows directory path with drive letter. Use double backslashes (\\\\) for Windows paths. Examples: 'C:\\\\Users\\\\Docker\\\\Videos', 'D:\\\\Movies\\\\Subtitles', 'C:\\\\Media\\\\Subs'. The directory must exist and contain the subtitle file specified in file_name. Typically subtitle files are stored in the same directory as the video file."
    )

    # Schema payload
    descriptions: List[str] = [
        "Load subtitle ${{file_name}} from ${{file_path}}.",
        "Open subtitle file ${{file_name}} at ${{file_path}}.",
        "Add subtitle ${{file_name}} from ${{file_path}}.",
        "Attach subs file ${{file_name}} from ${{file_path}}.",
        "Import subtitle ${{file_name}} from ${{file_path}}."
    ]

    def __init__(self, file_name: str = "subtitle.srt", file_path: str = "C:\\Users\\Docker\\Videos", **kwargs) -> None:
        super().__init__(file_name=file_name, file_path=file_path, **kwargs)
        file_name_value = self.file_name.value if hasattr(self.file_name, 'value') else self.file_name
        file_path_value = self.file_path.value if hasattr(self.file_path, 'value') else self.file_path
        self.add_path(
            "menu_open_subtitle",
            path=[
                SingleClickAction(thought="Click on the Subtitle menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Add Subtitle File' option."),
                WaitAction(duration=1.0),
                TypeAction(text=file_name_value, input_mode="copy_paste", thought=f"Enter file name: '{file_name_value}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Open dialog. Specifically, click the small blank space immediately to the right of the current folder path text, inside the address bar, to activate text editing mode. Do not click outside the address bar or on the file list area."),
                WaitAction(duration=1.0),
                TypeAction(text=file_path_value, input_mode="copy_paste", thought=f"Enter file path: '{file_path_value}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to make sure file path is set"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Open button"),
                WaitAction(duration=2.0)
            ]
        )

@register("VLCToggleSubtitles")
class VLCToggleSubtitles(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_toggle_subtitles"

    # Schema payload
    descriptions: List[str] = [
        "Toggle subtitles.",
        "Subtitles on/off.",
        "Show/hide subtitles.",
        "Enable or disable subs.",
        "Switch subtitles."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_subtitle_toggle",
            path=[
                HotKeyAction(keys=["shift", "v"], thought="Press 'Shift+V' to toggle subtitles."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCCycleSubtitleTrack")
class VLCCycleSubtitleTrack(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_cycle_subtitle_track"

    # Schema payload
    descriptions: List[str] = [
        "Switch subtitle track.",
        "Cycle subtitle channel.",
        "Change subtitle track.",
        "Next subtitle track.",
        "Select different subtitles."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_cycle_subtitle",
            path=[
                HotKeyAction(keys=["v"], thought="Press 'v' to cycle subtitle tracks."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCOpenNetworkStream")
class VLCOpenNetworkStream(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_open_network_stream"
    url: Argument = Argument(
        value="http://example.com/stream.m3u8",
        description="Network URL of the media stream to play. Must be a valid HTTP/HTTPS/RTSP/MMS URL. Supported protocols and formats: HTTP/HTTPS streaming (m3u8 for HLS, mpd for DASH), RTSP streams (rtsp://), MMS protocol (mms://), direct media links (.mp4, .mp3, etc.). Examples: 'http://example.com/stream.m3u8' (HLS stream), 'https://stream.example.com/live.mp4' (HTTP video), 'rtsp://camera.local:554/stream' (RTSP camera), 'http://radio.station.com/stream.mp3' (HTTP audio stream). The URL must be accessible and provide a compatible media format."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open network stream ${{url}}.",
        "Play URL ${{url}}.",
        "Stream from ${{url}}.",
        "Open network media ${{url}}.",
        "Load stream ${{url}}."
    ]

    def __init__(self, url: str = "http://example.com/stream.m3u8", **kwargs) -> None:
        super().__init__(url=url, **kwargs)
        url_value = self.url.value if hasattr(self.url, 'value') else self.url
        self.add_path(
            "hotkey_open_network",
            path=[
                HotKeyAction(keys=["ctrl", "n"], thought="Press Ctrl+N to open network stream dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=url_value, thought=f"Type the URL '{url_value}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to play the network stream."),
                WaitAction(duration=3.0)
            ]
        )
        self.add_path(
            "menu_open_network",
            path=[
                SingleClickAction(thought="Click on the Media menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Open Network Stream' option."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on the URL input field."),
                WaitAction(duration=1.0),
                TypeAction(text=url_value, thought=f"Type the URL '{url_value}'."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Play button."),
                WaitAction(duration=3.0)
            ]
        )

@register("VLCCycleAudioTrack")
class VLCCycleAudioTrack(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_cycle_audio_track"

    # Schema payload
    descriptions: List[str] = [
        "Switch audio track.",
        "Cycle audio channel.",
        "Change audio track.",
        "Next audio track.",
        "Select different audio."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_cycle_audio",
            path=[
                HotKeyAction(keys=["b"], thought="Press 'b' to cycle audio tracks."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCSetAspectRatio")
class VLCSetAspectRatio(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_set_aspect_ratio"
    ratio: Argument = Argument(
        value="Default",
        description="Video aspect ratio to apply. Available options: 'Default' (use video's original aspect ratio), '16:9' (widescreen, modern standard for HD content, 1.78:1), '16:10' (widescreen computer monitors, 1.6:1), '4:3' (classic TV/older content, 1.33:1), '1:1' (square, 1:1), '5:4' (old computer monitors, 1.25:1), '2.21:1' (cinema scope), '2.35:1' (anamorphic widescreen), '2.39:1' (modern cinema). Use exact format with colon separator or 'Default'. Common use cases: 16:9 for modern videos, 4:3 for old TV shows, Default to respect original format."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set aspect ratio ${{ratio}}.",
        "Aspect ${{ratio}}.",
        "Use ${{ratio}} aspect.",
        "Change aspect to ${{ratio}}.",
        "Apply ${{ratio}} ratio."
    ]

    def __init__(self, ratio: str = "Default", **kwargs) -> None:
        super().__init__(ratio=ratio, **kwargs)
        ratio_value = self.ratio.value if hasattr(self.ratio, 'value') else self.ratio
        self.add_path(
            "menu_aspect_ratio",
            path=[
                SingleClickAction(thought="Click on the Video menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Aspect Ratio' submenu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on the '{ratio_value}' aspect ratio option."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCSetAudioDelay")
class VLCSetAudioDelay(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_set_audio_delay"
    ms: Argument = Argument(
        value=0,
        description="Audio synchronization delay in milliseconds to fix audio/video sync issues. Must be an integer (positive or negative). Positive values delay audio (audio plays later than video, use when audio is ahead). Negative values advance audio (audio plays earlier than video, use when audio is behind). Range: typically -10000 to +10000 ms (-10 to +10 seconds). Examples: 0 (no delay, default sync), 500 (delay audio by 0.5 seconds), -300 (advance audio by 0.3 seconds), 1000 (delay audio by 1 second), -2000 (advance audio by 2 seconds). Use this to synchronize out-of-sync audio with video."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set audio delay ${{ms}} ms.",
        "Audio delay ${{ms}} milliseconds.",
        "Adjust audio delay to ${{ms}}.",
        "Use ${{ms}} ms audio delay.",
        "Sync audio by ${{ms}} ms."
    ]

    def __init__(self, ms: int = 0, **kwargs) -> None:
        super().__init__(ms=ms, **kwargs)
        ms_value = self.ms.value if hasattr(self.ms, 'value') else self.ms
        # covert ms to s
        s = ms_value / 1000.0
        self.add_path(
            "click_audio_delay",
            path=[
                SingleClickAction(thought="Click on the Tools menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Track Synchronization' option."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on the Audio Track Synchronization input box."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"], thought="Select existing value in the audio delay input box."),
                WaitAction(duration=1.0),
                TypeAction(text=str(s), thought=f"Enter audio delay value '{s}' s."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Close button to apply the audio delay."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCSetSubtitleDelay")
class VLCSetSubtitleDelay(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_set_subtitle_delay"
    ms: Argument = Argument(
        value=0,
        description="Subtitle synchronization delay in milliseconds to fix subtitle timing issues. Must be an integer (positive or negative). Positive values delay subtitles (subtitles appear later than video, use when subtitles appear too early). Negative values advance subtitles (subtitles appear earlier than video, use when subtitles appear too late). Range: typically -10000 to +10000 ms (-10 to +10 seconds). Examples: 0 (no delay, default sync), 500 (delay subtitles by 0.5 seconds), -300 (advance subtitles by 0.3 seconds), 1000 (delay subtitles by 1 second), -2000 (advance subtitles by 2 seconds). Use this to synchronize out-of-sync subtitles with video dialogue."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set subtitle delay ${{ms}} ms.",
        "Sub delay ${{ms}} milliseconds.",
        "Adjust subtitle delay to ${{ms}}.",
        "Use ${{ms}} ms subtitle delay.",
        "Sync subtitles by ${{ms}} ms."
    ]

    def __init__(self, ms: int = 0, **kwargs) -> None:
        super().__init__(ms=ms, **kwargs)
        ms_value = self.ms.value if hasattr(self.ms, 'value') else self.ms
        self.add_path(
            "click_subtitle_delay",
            path=[
                SingleClickAction(thought="Click on the Tools menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Track Synchronization' option."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on the Subtitle Track Synchronization input box."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"], thought="Select existing value in the subtitle delay input box."),
                WaitAction(duration=1.0),
                TypeAction(text=str(ms_value), thought=f"Enter subtitle delay value '{ms_value}' ms."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the Close button to apply the subtitle delay."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCToggleAlwaysOnTop")
class VLCToggleAlwaysOnTop(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_toggle_always_on_top"

    # Schema payload
    descriptions: List[str] = [
        "Toggle always on top.",
        "Always on top on/off.",
        "Keep player on top.",
        "Set window always on top.",
        "Pin/unpin window."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.add_path(
            "context_menu_always_on_top",
            path=[
                SingleClickAction(thought="Click on the View menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Always on Top' in context menu."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCOpenPlaylistView")
class VLCOpenPlaylistView(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_open_playlist_view"

    # Schema payload
    descriptions: List[str] = [
        "Open playlist view.",
        "Show playlist panel.",
        "Open the playlist.",
        "Display playlist window.",
        "View playlist."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_playlist",
            path=[
                HotKeyAction(keys=["ctrl", "l"], thought="Press Ctrl+L to open playlist view."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_playlist",
            path=[
                SingleClickAction(thought="Click View menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the playlist option."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCEnqueueMediaFile")
class VLCEnqueueMediaFile(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_enqueue_media_file"
    file_name: Argument = Argument(
        value="vlc_sample_1.mp4",
        description="Name of the media file to add to the playlist queue, including file extension. Supports various media formats: video files (.mp4, .avi, .mkv, .mov, .wmv, .flv, .webm), audio files (.mp3, .wav, .flac, .aac, .ogg, .m4a). Examples: 'movie.mp4', 'song.mp3', 'video_clip.avi', 'music_track.flac', 'episode_01.mkv'. The file will be added to the playlist without immediately starting playback."
    )
    file_path: Argument = Argument(
        value="C:\\Users\\Docker\\Videos",
        description="Full absolute directory path containing the media file to enqueue. Must be a valid Windows directory path with drive letter. Use double backslashes (\\\\) for Windows paths. Examples: 'C:\\\\Users\\\\Docker\\\\Videos', 'D:\\\\Music', 'C:\\\\Media\\\\Movies'. The directory must exist and contain the media file specified in file_name."
    )

    # Schema payload
    descriptions: List[str] = [
        "Enqueue file ${{file_name}} from ${{file_path}}.",
        "Add ${{file_name}} in ${{file_path}} to queue.",
        "Queue media ${{file_name}} from ${{file_path}}.",
        "Add ${{file_name}} from ${{file_path}} to playlist.",
        "Append ${{file_name}} located at ${{file_path}}."
    ]

    def __init__(self, file_name: str = "vlc_sample_1.mp4", file_path: str = "C:\\Users\\Docker\\Videos", **kwargs) -> None:
        super().__init__(file_name=file_name, file_path=file_path, **kwargs)
        file_name_value = self.file_name.value if hasattr(self.file_name, 'value') else self.file_name
        file_path_value = self.file_path.value if hasattr(self.file_path, 'value') else self.file_path
        self.add_path(
            "drag_drop_enqueue",
            path=[
                SingleClickAction(thought="Click on Media menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Open File...' option."),
                WaitAction(duration=1.0),
                TypeAction(text=file_name_value, input_mode="copy_paste", thought=f"Enter file name: '{file_name_value}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the editable area of the address bar in the Open dialog to activate text editing mode."),
                WaitAction(duration=1.0),
                TypeAction(text=file_path_value, input_mode="copy_paste", thought=f"Enter file path: '{file_path_value}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to navigate to the directory."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Open' button to add to playlist."),
                WaitAction(duration=2.0)
            ]
        )

@register("VLCNextTrack")
class VLCNextTrack(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_next_track"

    # Schema payload
    descriptions: List[str] = [
        "Next track.",
        "Skip to next.",
        "Play next item.",
        "Go to next media.",
        "Next in playlist."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_next",
            path=[
                HotKeyAction(keys=["n"], thought="Press 'n' to skip to next track."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_next",
            path=[
                SingleClickAction(thought="Click the Next button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCPreviousTrack")
class VLCPreviousTrack(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_previous_track"

    # Schema payload
    descriptions: List[str] = [
        "Previous track.",
        "Go back to previous.",
        "Play previous item.",
        "Go to previous media.",
        "Previous in playlist."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_previous",
            path=[
                HotKeyAction(keys=["p"], thought="Press 'p' to go to previous track."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_previous",
            path=[
                SingleClickAction(thought="Click the Previous button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCToggleLoop")
class VLCToggleLoop(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_toggle_loop"

    # Schema payload
    descriptions: List[str] = [
        "Toggle loop.",
        "Loop on/off.",
        "Enable/disable loop.",
        "Repeat playback.",
        "Set loop mode."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_loop",
            path=[
                HotKeyAction(keys=["l"], thought="Press 'l' to toggle loop mode."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_loop",
            path=[
                SingleClickAction(thought="Click the loop button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCToggleShuffle")
class VLCToggleShuffle(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_toggle_shuffle"

    # Schema payload
    descriptions: List[str] = [
        "Toggle shuffle.",
        "Shuffle on/off.",
        "Enable/disable shuffle.",
        "Random playback.",
        "Set shuffle mode."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_shuffle",
            path=[
                HotKeyAction(keys=["r"], thought="Press 'r' to toggle random mode."),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_shuffle",
            path=[
                SingleClickAction(thought="Click the random button in VLC."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCClearPlaylist")
class VLCClearPlaylist(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_clear_playlist"

    # Schema payload
    descriptions: List[str] = [
        "Clear playlist.",
        "Empty the playlist.",
        "Remove all items.",
        "Clear all media.",
        "Reset playlist."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.add_path(
            "hotkey_clear_playlist",
            path=[
                HotKeyAction(keys=["ctrl", "w"], thought="Press Ctrl+W to clear playlist."),
                WaitAction(duration=1.0)
            ]
        )

@register("VLCOpenPreferences")
class VLCOpenPreferences(VLCBaseAction):
    # Canonical identifiers
    type: str = "vlc_open_preferences"

    # Schema payload
    descriptions: List[str] = [
        "Open preferences.",
        "Go to settings.",
        "Open VLC settings.",
        "Access preferences.",
        "Configure VLC."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_preferences",
            path=[
                HotKeyAction(keys=["ctrl", "p"], thought="Press Ctrl+P to open preferences."),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "menu_preferences",
            path=[
                SingleClickAction(thought="Click on the Tools menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Preferences' option."),
                WaitAction(duration=2.0)
            ]
        )
