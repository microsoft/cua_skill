from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction 
from .common_action import LaunchApplication
from .argument import Argument
from .microsoft_edge_action import MicrosoftEdgeLaunch, MicrosoftEdgeOpenURL

__all__ = []

class YoutubeBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="youtube",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Youtube",
        description="The name of the Youtube application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register("YoutubeLaunch")
class YoutubeLaunch(YoutubeBaseAction):
    # Canonical identifiers
    type: str = "youtube_launch"
    
    # Schema payload
    descriptions: List[str] = [
        "Open YouTube.",
        "Launch the YouTube app.",
        "Start YouTube.",
        "Run the YouTube application.",
        "Open the video app YouTube."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "launch_youtube_in_edge",
            path=[
                MicrosoftEdgeLaunch(),
                WaitAction(duration=2.0),
                MicrosoftEdgeOpenURL(url="https://www.youtube.com")
            ]
        )



@register("YoutubeOpenSearchMenu")
class YoutubeOpenSearchMenu(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_open_search_menu"

    # Schema payload
    descriptions: List[str] = [
        "Open the search menu in YouTube.",
        "Access the search menu in the YouTube app.",
        "Click on the search bar in YouTube.",
        "Open the search menu in YouTube.",
        "Navigate to the search menu in the YouTube application."
    ]

    search_bar_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Search bar in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_youtube_search_menu",
            path=[
                SingleClickAction(thought="Click the search bar in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )


@register("YoutubeSearchVideo")
class YoutubeSearchVideo(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_search_video"

    # Schema payload
    descriptions: List[str] = [
        "Search for video ${{query}}.",
        "Look up ${{query}} on YouTube.",
        "Find videos about ${{query}}.",
        "Search YouTube for ${{query}}.",
        "Look for ${{query}} content."
    ]

    def __init__(self, query: str = "tutorial", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "search_youtube_video",
            path=[
                YoutubeOpenSearchMenu(),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Search for the video '{query}' on YouTube."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )


@register("YoutubePlayVideo")
class YoutubePlayVideo(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_play_video"
    video_name: str = "tutorial"  # e.g., Standard, Scientific, Programmer, Date Calculation, Converter.

    # Schema payload
    descriptions: List[str] = [
        "Play the video titled ${{video_title}}.",
        "Start playing ${{video_title}}.",
        "Watch video ${{video_title}}.",
        "Play ${{video_title}} on YouTube.",
        "Begin playback of ${{video_title}}."
    ]

    def __init__(self, video_title: str = "tutorial", **kwargs) -> None:
        super().__init__(video_title=video_title, **kwargs)
        self.add_path(
            "play_youtube_video",
            path=[
                SingleClickAction(thought=f"Click on the title '{self.video_title}'"),
                WaitAction(duration=1.0)
            ]
        )


@register("YoutubePauseVideo")
class YoutubePauseVideo(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_pause_video"

    # Schema payload
    descriptions: List[str] = [
        "Pause the video.",
        "Stop playback.",
        "Pause YouTube video.",
        "Pause now.",
        "Pause current video."
    ]

    pause_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Pause button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "pause_youtube_video",
            path=[
                SingleClickAction(thought="Click the pause button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeResumeVideo")
class YoutubeResumeVideo(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_resume_video"

    # Schema payload
    descriptions: List[str] = [
        "Resume the video.",
        "Continue playback.",
        "Unpause the video.",
        "Keep playing.",
        "Resume now."
    ]

    resume_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Resume button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "resume_youtube_video",
            path=[
                SingleClickAction(thought="Click the resume button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeSkipForward")
class YoutubeSkipForward(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_skip_forward"

    # Schema payload
    descriptions: List[str] = [
        "Skip forward 5 seconds.",
        "Jump ahead 5 seconds.",
        "Move forward 5 seconds.",
        "Go 5 seconds ahead.",
        "Skip 5 seconds."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "skip_forward_youtube_video",
            path=[
                HotKeyAction(keys=["Right"]),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeSkipBackward")
class YoutubeSkipBackward(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_skip_backward"

    # Schema payload
    descriptions: List[str] = [
        "Skip backward 5 seconds.",
        "Jump backward 5 seconds.",
        "Move backward 5 seconds.",
        "Go 5 seconds backward.",
        "Skip 5 seconds backward."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "skip_backward_youtube_video",
            path=[
                HotKeyAction(keys=["Left"]),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeAdjustVolumeUp")
class YoutubeAdjustVolumeUp(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_adjust_volume_up"

    # Schema payload
    descriptions: List[str] = [
        "Increase volume by 10%.",
        "Turn up the volume 10%.",
        "Change volume by 10% up.",
        "Set volume at 10% percent up."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "adjust_youtube_volume_up",
            path=[
                HotKeyAction(keys=["up"]),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeAdjustVolumeDown")
class YoutubeAdjustVolumeDown(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_adjust_volume_down"

    # Schema payload
    descriptions: List[str] = [
        "Decrease volume by 10%.",
        "Turn down the volume 10%.",
        "Change volume by 10% down.",
        "Set volume at 10% percent down."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "adjust_youtube_volume_down",
            path=[
                HotKeyAction(keys=["down"]),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeFullscreen")
class YoutubeFullscreen(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_fullscreen"

    # Schema payload
    descriptions: List[str] = [
        "Enter fullscreen mode.",
        "Maximize the video.",
        "Watch video in fullscreen.",
        "Expand to fullscreen.",
        "Go full screen."
    ]

    fullscreen_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Fullscreen button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "fullscreen_youtube_video",
            path=[
                SingleClickAction(thought="Click the fullscreen button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_fullscreen",
            path=[
                HotKeyAction(keys=["f"]),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeExitFullscreen")
class YoutubeExitFullscreen(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_exit_fullscreen"

    # Schema payload
    descriptions: List[str] = [
        "Exit fullscreen mode.",
        "Minimize the video.",
        "Leave fullscreen.",
        "Go back to windowed view.",
        "Exit full screen."
    ]

    exit_fullscreen_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Exit fullscreen button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "exit_fullscreen_youtube_video",
            path=[
                SingleClickAction(thought="Click the exit fullscreen button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_exit_fullscreen",
            path=[
                HotKeyAction(keys=["esc"]),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeLikeVideo")
class YoutubeLikeVideo(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_like_video"

    # Schema payload
    descriptions: List[str] = [
        "Like this video.",
        "Give a thumbs up.",
        "Add a like to this video.",
        "Press the like button.",
        "Save as liked video."
    ]

    like_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Like button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "like_youtube_video",
            path=[
                SingleClickAction(thought="Click the like button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )
        

@register("YoutubeDislikeVideo")
class YoutubeDislikeVideo(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_dislike_video"

    # Schema payload
    descriptions: List[str] = [
        "Dislike this video.",
        "Give a thumbs up.",
        "Add a dislike to this video.",
        "Press the dislike button.",
        "Save as disliked video."
    ]

    dislike_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Dislike button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "dislike_youtube_video",
            path=[
                SingleClickAction(thought="Click the dislike button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeSubscribeChannel")
class YoutubeSubscribeChannel(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_subscribe_channel"
    channel_name: str = "MrBeast"

    # Schema payload
    descriptions: List[str] = [
        "Subscribe to channel ${{channel_name}}.",
        "Follow ${{channel_name}}.",
        "Subscribe ${{channel_name}} on YouTube.",
        "Join channel ${{channel_name}}.",
        "Subscribe to ${{channel_name}}."
    ]

    subscribe_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Subscribe button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, channel_name: str = "MrBeast", **kwargs) -> None:
        super().__init__(channel_name=channel_name, **kwargs)
        self.add_path(
            "subscribe_youtube_channel",
            path=[
                SingleClickAction(thought=f"Click the subscribe button in the YouTube app for {self.channel_name}"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeUnsubscribeChannel")
class YoutubeUnsubscribeChannel(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_unsubscribe_channel"
    channel_name: str = "MrBeast"

    # Schema payload
    descriptions: List[str] = [
        "Unsubscribe from channel ${{channel_name}}.",
        "Unfollow ${{channel_name}}.",
        "Unsubscribe ${{channel_name}} on YouTube.",
        "Leave channel ${{channel_name}}.",
        "Unsubscribe from ${{channel_name}}."
    ]

    unsubscribe_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Unsubscribe button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, channel_name: str = "MrBeast", **kwargs) -> None:
        super().__init__(channel_name=channel_name, **kwargs)
        self.add_path(
            "unsubscribe_youtube_channel",
            path=[
                SingleClickAction(thought=f"Click the unsubscribe button in the YouTube app for {self.channel_name}"),
                WaitAction(duration=1.0)
            ]
        )


@register("YoutubeClickCommentSection")
class YoutubeClickCommentSection(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_click_comment_section"

    # Schema payload
    descriptions: List[str] = [
        "Click the comment section.",
        "Open the comment section.",
        "Go to the comment section.",
        "Navigate to the comment section.",
        "Go to the comment section."
    ]

    comment_section_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "New comment section button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_comment_section",
            path=[
                SingleClickAction(thought="Click the new comment section button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )


@register("YoutubeCommentVideo")
class YoutubeCommentVideo(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_comment_video"
    comment: str = "Great video!"

    # Schema payload
    descriptions: List[str] = [
        "Add comment ${{comment}} on this video.",
        "Post ${{comment}} as comment.",
        "Write ${{comment}} below the video.",
        "Comment ${{comment}} on this video.",
        "Leave a comment: ${{comment}}."
    ]

    post_comment_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Post comment button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, comment: str = "Great video!", **kwargs) -> None:
        super().__init__(comment=comment, **kwargs)
        self.add_path(
            "comment_youtube_video",
            path=[
                SingleClickAction(thought=f"Type the comment '{self.comment}' in the comment section"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the post comment button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeOpenVideoOptionsMenu")
class YoutubeOpenVideoOptionsMenu(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_open_video_options_menu"

    # Schema payload
    descriptions: List[str] = [
        "Open the video options menu.",
        "Access the video options menu.",
        "Go to the video options menu.",
        "Navigate to the video options menu.",
        "Go to the video options menu."
    ]

    video_options_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Video options menu button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_video_options_menu",
            path=[
                SingleClickAction(thought="Click the video options menu button (...) in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeOpenSaveVideoOption")
class YoutubeOpenSaveVideoOption(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_open_save_video_option_menu"

    # Schema payload
    descriptions: List[str] = [
        "Open the save video option menu.",
        "Access the save video option menu.",
        "Go to the save video option menu.",
        "Navigate to the save video option menu.",
        "Go to the save video option menu."
    ]

    save_video_option_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Save video option button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_save_video_option_menu",
            path=[
                SingleClickAction(thought="Click the \"Save\" video option button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )


@register("YoutubeSaveToWatchLater")
class YoutubeSaveToWatchLater(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_save_to_watch_later"

    # Schema payload
    descriptions: List[str] = [
        "Save this video to Watch Later.",
        "Add to Watch Later list.",
        "Keep this video for later.",
        "Save for later viewing.",
        "Mark video to watch later."
    ]

    watch_later_video_option_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Watch Later save video option button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_watch_later_video_option",
            path=[
                SingleClickAction(thought="Click the checkbox next to the \"Watch Later\" option button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeOpenVideoSettings")
class YoutubeOpenVideoSettings(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_open_video_settings"

    # Schema payload
    descriptions: List[str] = [
        "Open the video settings.",
        "Access the video settings.",
        "Go to the video settings.",
        "Navigate to the video settings.",
        "Go to the video settings."
    ]

    video_settings_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Video settings button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_video_settings_button",
            path=[
                SingleClickAction(thought="Click the video settings button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )


@register("YoutubeOpenPlaybackSpeedOptions")
class YoutubeOpenPlaybackSpeedOptions(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_open_playback_speed_options"

    # Schema payload
    descriptions: List[str] = [
        "Open the playback speed options.",
        "Access the playback speed options.",
        "Go to the playback speed options.",
        "Navigate to the playback speed options.",
        "Go to the playback speed options."
    ]

    playback_speed_options_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Playback speed options button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_playback_speed_options_button",
            path=[
                SingleClickAction(thought="Click the playback speed options button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeChangePlaybackSpeed")
class YoutubeChangePlaybackSpeed(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_change_playback_speed"
    speed: str = "1.25"

    # Schema payload
    descriptions: List[str] = [
        "Change playback speed to ${{speed}}x.",
        "Set speed at ${{speed}}.",
        "Play video at ${{speed}} times speed.",
        "Adjust playback rate to ${{speed}}x.",
        "Change video speed to ${{speed}}."
    ]

    playback_speed_option_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Playback speed option button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, speed: str = "1.25", **kwargs) -> None:
        super().__init__(speed=speed, **kwargs)
        self.add_path(
            "click_playback_speed_option_button",
            path=[
                SingleClickAction(thought=f"Click the playback speed option button in the YouTube app for {self.speed}x"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeEnableCaptions")
class YoutubeEnableCaptions(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_enable_captions"

    # Schema payload
    descriptions: List[str] = [
        "Turn on captions.",
        "Enable subtitles.",
        "Show closed captions.",
        "Activate subtitles.",
        "Display captions."
    ]

    enable_captions_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Enable captions button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_enable_captions_button",
            path=[
                SingleClickAction(thought="Click the enable captions button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )

@register("YoutubeDisableCaptions")
class YoutubeDisableCaptions(BaseComposeAction):
    # Canonical identifiers
    type: str = "youtube_disable_captions"

    # Schema payload
    descriptions: List[str] = [
        "Turn on captions.",
        "Enable subtitles.",
        "Show closed captions.",
        "Activate subtitles.",
        "Display captions."
    ]

    disable_captions_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Disable captions button in the YouTube app.",
        "require_grounding": True
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_disable_captions_button",
            path=[
                SingleClickAction(thought="Click the disable captions button in the YouTube app"),
                WaitAction(duration=1.0)
            ]
        )
