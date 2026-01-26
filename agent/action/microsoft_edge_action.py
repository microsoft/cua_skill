from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, RightClickAction, ScrollAction
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

class MicrosoftEdgeBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="microsoft_edge",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Microsoft Edge",
        description="The name of the Microsoft Edge application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register("MicrosoftEdgeLaunch")
class MicrosoftEdgeLaunch(MicrosoftEdgeBaseAction, LaunchApplication):
    # Canonical identifiers
    type: str = "microsoft_edge_launch"
    
    # Schema payload
    descriptions: List[str] = [
        "Open Microsoft Edge.",
        "Launch the Microsoft Edge app.",
        "Start Microsoft Edge.",
        "Run the Microsoft Edge application.",
        "Open the Microsoft Edge program."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)

@register("MicrosoftEdgeMaximizeWindow")
class MicrosoftEdgeMaximizeWindow(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_maximize_window"

    # Schema payload
    descriptions: List[str] = [
        "Maximize Microsoft Edge window.",
        "Make the Edge window full screen.",
        "Expand the Edge window.",
        "Maximize the current window.",
        "Fill the screen with the window."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_maximize_window",
            path=[
                HotKeyAction(keys=["win", "up"]),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "click_microsoft_edge_maximize_window",
            path=[
                SingleClickAction(thought="Click the Microsoft Edge maximize window button in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )

@register("MicrosoftEdgeMinimizeWindow")
class MicrosoftEdgeMinimizeWindow(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_minimize_window"

    # Schema payload
    descriptions: List[str] = [
        "Minimize Microsoft Edge window.",
        "Reduce the Edge window to taskbar.",
        "Hide the current window.",
        "Minimize the active window.",
        "Shrink the Edge window."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_minimize_window",
            path=[
                HotKeyAction(keys=["win", "down"]),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "click_microsoft_edge_minimize_window",
            path=[
                SingleClickAction(thought="Click the Microsoft Edge minimize window button in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeOpenMenu")
class MicrosoftEdgeOpenMenu(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_menu"

    # Schema payload
    descriptions: List[str] = [
        "Open the Edge menu.",
        "Open the three-dots menu.",
        "Show the browser menu.",
        "Open the settings and more menu.",
        "Access the Edge menu."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_open_menu",
            path=[
                HotKeyAction(keys=["alt", "e"]),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "click_microsoft_edge_open_menu",
            path=[
                SingleClickAction(thought="Click the Microsoft Edge menu (three dots) button in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeStartNewSearch")
class MicrosoftEdgeStartNewSearch(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_start_new_search"

    # Schema payload
    descriptions: List[str] = [
        "Focus the address bar.",
        "Select the URL bar.",
        "Go to the address bar.",
        "Start a new search in the URL bar.",
        "Place cursor in the address field."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_start_new_search",
            path=[
                HotKeyAction(keys=["ctrl", "l"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "open_microsoft_edge_start_new_search",
            path=[ 
                SingleClickAction(thought="Click the URL address bar in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )
        
@register("MicrosoftEdgeNewSearchQuery")
class MicrosoftEdgeNewSearchQuery(BaseComposeAction):
    type: str = "microsoft_edge_new_search_query"
    query: Argument = Argument(
        value="latest technology news",
        description="The query to search for in Microsoft Edge."
    )

    # Schema payload
    descriptions: List[str] = [
        "Search for ${{query}}.",
        "Look up ${{query}} online.",
        "Find results for ${{query}}.",
        "Web search: ${{query}}.",
        "Search ${{query}} via ${{engine}}."
    ]
    
    def __init__(self, query: str = "latest technology news", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "open_microsoft_edge_new_search_query",
            path=[ 
                MicrosoftEdgeStartNewSearch(thought=f"Search for the query '{query}' in Microsoft Edge"),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Enter the query '{query}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0),
            ]
        )

@register("MicrosoftEdgeOpenURL")
class MicrosoftEdgeOpenURL(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_url"
    url: Argument = Argument(
        value="https://www.bing.com",
        description="The URL to open in Microsoft Edge."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open URL ${{url}}.",
        "Navigate to ${{url}}.",
        "Go to webpage ${{url}}.",
        "Load the site at ${{url}}.",
        "Visit ${{url}}."
    ]
    
    def __init__(self, url: str = "https://www.bing.com", **kwargs) -> None:
        super().__init__(url=url, **kwargs)
        self.add_path(
            "open_microsoft_edge_url",
            path=[ 
                MicrosoftEdgeStartNewSearch(thought=f"Navigate to the search box in Microsoft Edge"),
                WaitAction(duration=1.0),
                TypeAction(text=url, input_mode="copy_paste", thought=f"Enter the URL '{url}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )

@register("MicrosoftEdgeOpenNewTab")
class MicrosoftEdgeOpenNewTab(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_new_tab"

    # Schema payload
    descriptions: List[str] = [
        "Open a new tab.",
        "Create a blank tab.",
        "Start a new browser tab.",
        "Open another tab.",
        "Add a new tab."
    ]
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_microsoft_edge_open_new_tab",
            path=[
                SingleClickAction(thought="Click the new tab button (+) in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_open_new_tab",
            path=[
                HotKeyAction(keys=["ctrl", "t"]),
                WaitAction(duration=1.0)
            ]
        )

@register("MicrosoftEdgeCloseTab")
class MicrosoftEdgeCloseTab(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_close_tab"

    # Schema payload
    descriptions: List[str] = [
        "Close the current tab.",
        "Close this tab.",
        "Exit the active tab.",
        "Close active page tab.",
        "Dismiss the current tab."
    ]
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_microsoft_edge_close_tab",
            path=[
                SingleClickAction(thought="Click the close (X) button on the current tab in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_close_tab",
            path=[
                HotKeyAction(keys=["ctrl", "w"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeSwitchTab")
class MicrosoftEdgeSwitchTab(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_switch_tab"
    index: Argument = Argument(
        value=1,
        description="The index of the tab to switch to."
    )

    # Schema payload
    descriptions: List[str] = [
        "Switch to tab #${{index}}.",
        "Activate tab number ${{index}}.",
        "Go to tab index ${{index}}.",
        "Focus tab ${{index}}.",
        "Select tab ${{index}}."
    ]

    def __init__(self, index: int = 1, **kwargs) -> None:
        super().__init__(index=index, **kwargs)
        self.add_path(
            "open_microsoft_edge_switch_tab",
            path=[
                SingleClickAction(thought=f"Click the tab number {index} in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_switch_tab",
            path=[
                HotKeyAction(keys=["ctrl", str(index)]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeReopenClosedTab")
class MicrosoftEdgeReopenClosedTab(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_reopen_close_tab"

    # Schema payload
    descriptions: List[str] = [
        "Reopen last closed tab.",
        "Restore recently closed tab.",
        "Bring back the previous tab.",
        "Recover closed tab.",
        "Reopen closed Edge tab."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_microsoft_edge_reopen_close_tab",
            path=[
                RightClickAction(thought="Right click on the tab bar area in Microsoft Edge"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the reopen tab button in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_reopen_close_tab",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "t"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeOpenHistory")
class MicrosoftEdgeOpenHistory(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_history"

    # Schema payload
    descriptions: List[str] = [
        "Open browsing history.",
        "Show Edge history.",
        "View my browsing history.",
        "Open the History panel.",
        "See past pages."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_microsoft_edge_history",
            path=[
                HotKeyAction(keys=["ctrl", "h"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_microsoft_edge_history",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the history button in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeOpenDownloads")
class MicrosoftEdgeOpenDownloads(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_downloads"

    # Schema payload
    descriptions: List[str] = [
        "Open downloads page.",
        "Show downloaded files.",
        "View Edge downloads.",
        "Open the Downloads panel.",
        "See all downloads."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_microsoft_edge_downloads",
            path=[
                HotKeyAction(keys=["ctrl", "j"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_microsoft_edge_downloads",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the downloads button in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeBookmarkPage")
class MicrosoftEdgeBookmarkPage(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_bookmark_page"
    bookmark_name: Argument = Argument(
        value="Azure Portal",
        description="The name of the bookmark to create."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add this page to Favorites with the name ${{bookmark_name}}.",
        "Bookmark the current page with the name ${{bookmark_name}}.",
        "Save page as a Favorite named ${{bookmark_name}}.",
        "Add Favorite named ${{bookmark_name}}.",
        "Star this page with the name ${{bookmark_name}}."
    ]

    def __init__(self, bookmark_name: str = "Azure Portal", **kwargs) -> None:
        super().__init__(bookmark_name=bookmark_name, **kwargs)
        self.add_path(
            "microsoft_edge_bookmark_page",
            path=[
                HotKeyAction(keys=["ctrl", "d"]),
                WaitAction(duration=1.0),
                TypeAction(text=bookmark_name, input_mode="copy_paste", thought=f"Bookmark the page with the name '{bookmark_name}' in Microsoft Edge"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_microsoft_edge_bookmark_page",
            path=[
                SingleClickAction(thought="Click the bookmark (star) button in Microsoft Edge"),
                WaitAction(duration=1.0),
                TypeAction(text=bookmark_name, input_mode="copy_paste", thought=f"Bookmark the page with the name '{bookmark_name}' in Microsoft Edge"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeDisplayBookmarkBar")
class MicrosoftEdgeDisplayBookmarkBar(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_display_bookmark_bar"
    title: Argument = Argument(
        value="Azure Portal",
        description="The title of the bookmark to open."
    )

    # Schema payload
    descriptions: List[str] = [
        "Toggle the Favorites bar.",
        "Show or hide the Favorites bar.",
        "Toggle bookmark bar visibility.",
        "Display or hide the Favorites bar.",
        "Toggle Edge Favorites bar."
    ]
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_display_bookmark_bar",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "b"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeOpenBookmark")
class MicrosoftEdgeOpenBookmark(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_bookmark"
    title: Argument = Argument(
        value="Azure Portal",
        description="The title of the bookmark to open."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open bookmark ${{title}}.",
        "Open Favorite named ${{title}}.",
        "Go to bookmark ${{title}}.",
        "Open saved site ${{title}}.",
        "Visit Favorite ${{title}}."
    ]
    
    def __init__(self, title: str = "Azure Portal", **kwargs) -> None:
        super().__init__(title=title, **kwargs)
        self.add_path(
            "hotkey_microsoft_edge_bookmark",
            path=[
                SingleClickAction(thought=f"Click the search (magnifine glass) icon in the pop up window"),
                WaitAction(duration=1.0),
                TypeAction(text=title, input_mode="copy_paste", thought=f"Search for the bookmark {title} in Microsoft Edge"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the bookmark {title} in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "open_microsoft_edge_bookmark",
            path=[
                MicrosoftEdgeDisplayBookmarkBar(),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the bookmark {title} in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )
        

@register("MicrosoftEdgeDownloadFile")
class MicrosoftEdgeDownloadFile(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_download_file"
    url: Argument = Argument(
        value="https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe",
        description="The URL of the file to download."
    )

    # Schema payload
    descriptions: List[str] = [
        "Download file from ${{url}}.",
        "Save file at ${{url}}.",
        "Fetch resource from ${{url}}.",
        "Download the file link ${{url}}.",
        "Start downloading ${{url}}."
    ]
    
    def __init__(self, url: str = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe", **kwargs) -> None:
        super().__init__(url=url, **kwargs)
        self.add_path(
            "click_microsoft_edge_download_file",
            path=[
                MicrosoftEdgeStartNewSearch(),
                WaitAction(duration=1.0),
                TypeAction(text=url, input_mode="copy_paste", thought=f"Download the file from '{url}' in Microsoft Edge"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"])

            ]
        )


@register("MicrosoftEdgeOpenInPrivate")
class MicrosoftEdgeOpenInPrivate(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_in_private"

    # Schema payload
    descriptions: List[str] = [
        "Open a new InPrivate window.",
        "Start an InPrivate session.",
        "Create InPrivate window.",
        "Open private browsing window.",
        "Begin InPrivate mode."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_open_in_private",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the new InPrivate window button in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_open_in_private",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "n"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeZoomIn")
class MicrosoftEdgeZoomIn(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_zoom_in"

    # Schema payload
    descriptions: List[str] = [
        "Zoom in.",
        "Increase zoom level.",
        "Magnify view.",
        "Make page larger.",
        "Zoom closer."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_zoom_in",
            path=[
                HotKeyAction(keys=["ctrl", "+"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_microsoft_edge_zoom_in",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the zoom in (+) button in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )  


@register("MicrosoftEdgeZoomOut")
class MicrosoftEdgeZoomOut(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_zoom_out"

    # Schema payload
    descriptions: List[str] = [
        "Zoom out.",
        "Decrease zoom level.",
        "Shrink view.",
        "Make page smaller.",
        "Zoom away."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_zoom_out",
            path=[
                HotKeyAction(keys=["ctrl", "-"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_microsoft_edge_zoom_out",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the zoom out (-) button in Microsoft Edge"),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeOpenDeveloperTools")
class MicrosoftEdgeOpenDeveloperTools(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_developer_tools"

    # Schema payload
    descriptions: List[str] = [
        "Open developer tools.",
        "Launch Edge DevTools.",
        "Inspect element.",
        "Show developer panel.",
        "Open DevTools."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_open_developer_tools",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'More tools' option in Microsoft Edge menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Developer tools' option in Microsoft Edge menu"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "right_click_microsoft_edge_open_developer_tools",
            path=[
                RightClickAction(thought="Right click the Microsoft Edge webpage."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Inspect' option in Microsoft Edge menu"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_open_developer_tools",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "i"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgePrintPage")
class MicrosoftEdgePrintPage(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_print_page"

    # Schema payload
    descriptions: List[str] = [
        "Print this page.",
        "Open print dialog.",
        "Print the current tab.",
        "Send page to printer.",
        "Start printing."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_microsoft_edge_print_page",
            path=[
                HotKeyAction(keys=["ctrl", "p"]),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeOpenSettings")
class MicrosoftEdgeOpenSettings(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_settings"

    # Schema payload
    descriptions: List[str] = [
        "Open Edge settings.",
        "Access browser settings.",
        "Open Settings page.",
        "Show Edge settings.",
        "Go to settings."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_open_settings",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the settings button in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "url_microsoft_edge_open_settings",
            path=[
                MicrosoftEdgeOpenURL(url="edge://settings/"),
                WaitAction(duration=1.0),
            ]
        )

@register("MicrosoftEdgeInstallSiteAsApp")
class MicrosoftEdgeInstallSiteAsApp(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_install_site_as_app"

    # Schema payload
    descriptions: List[str] = [
        "Install the current site as an app.",
        "Add the current site as an app.",
        "Create an app from the current site.",
        "Make the current site an app.",
        "Turn the current site into an app."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_install_site_as_app",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Apps' button in Microsoft Edge"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Install site as an app' button"),
                WaitAction(duration=1.0),
            ]
        )

@register("MicrosoftEdgeSearchSettings")
class MicrosoftEdgeSearchSettings(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_search_settings"
    setting_name: Argument = Argument(
        value="privacy settings",
        description="The name of the setting to search for in Microsoft Edge."
    )

    # Schema payload
    descriptions: List[str] = [
        "Search settings for ${{setting_name}}.",
        "Find ${{setting_name}} in Edge settings.",
        "Look up ${{setting_name}} in settings.",
        "Search Edge settings: ${{setting_name}}.",
        "Locate ${{setting_name}} in settings."
    ]

    def __init__(self, setting_name: str = "privacy settings", **kwargs) -> None:
        super().__init__(setting_name=setting_name, **kwargs)
        self.add_path(
            "url_microsoft_edge_search_settings",
            path=[
                MicrosoftEdgeOpenURL(url=f"edge://settings/?search={setting_name}"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeOpenSettingsMenu")
class MicrosoftEdgeOpenSettingsMenu(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_settings_menu"
    setting_name: Argument = Argument(
        value="downloads",
        description="The name of the setting to access in Microsoft Edge."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open settings menu ${{setting_name}}.",
        "Go to settings section ${{setting_name}}.",
        "Open settings page ${{setting_name}}.",
        "Navigate to ${{setting_name}} settings.",
        "Open Edge settings ${{setting_name}}."
    ]

    def __init__(self, setting_name: str = "downloads", **kwargs) -> None:
        super().__init__(setting_name=setting_name, **kwargs)
        self.add_path(
            "url_microsoft_edge_open_settings_menu",
            path=[
                MicrosoftEdgeOpenURL(url=f"edge://settings/{setting_name}"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeCloseWindow")
class MicrosoftEdgeCloseWindow(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_close_window"

    # Schema payload
    descriptions: List[str] = [
        "Close the Edge window.",
        "Exit the browser window.",
        "Close current window.",
        "Quit this Edge window.",
        "Close the active window."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_close_window",
            path=[
                SingleClickAction(thought="Click the close window button in Microsoft Edge"),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_close_window",
            path=[
                HotKeyAction(keys=["alt", "f4"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeTurnDoNotTrackRequestsOn")
class MicrosoftEdgeTurnDoNotTrackRequestsOn(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_turn_do_not_track_requests_on"

    # Schema payload
    descriptions: List[str] = [
        "Enable Do Not Track requests.",
        "Turn on Do Not Track.",
        "Set 'Do Not Track' to on.",
        "Enable sending Do Not Track requests.",
        "Turn Do Not Track to enabled."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_turn_do_not_track_requests_on",
            path=[
                MicrosoftEdgeSearchSettings(setting_name="do not track"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the do not track requests toggle button in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeOpenProfileSettings")
class MicrosoftEdgeOpenProfileSettings(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_profile_settings"

    # Schema payload
    descriptions: List[str] = [
        "Open profile settings.",
        "Go to Edge profiles.",
        "Open Profiles settings page.",
        "Access profile settings.",
        "Open the Profiles section."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_open_profile_settings",
            path=[
                MicrosoftEdgeOpenSettings(),
                WaitAction(duration=1.0)
            ]
        )


@register("MicrosoftEdgeEditProfile")
class MicrosoftEdgeEditProfile(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_edit_profile"

    # Schema payload
    descriptions: List[str] = [
        "Open the profile edit dialog.",
        "Edit profile settings.",
        "Open edit profile.",
        "Go to profile edit.",
        "Change profile settings."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_edit_profile",
            path=[
                MicrosoftEdgeOpenProfileSettings(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the edit pencil icon under the \"Profiles\" section"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeChangeProfileName")
class MicrosoftEdgeChangeProfileName(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_change_profile_name"
    profile_name: Argument = Argument(
        value="Mike",
        description="The name of the profile to change."
    )

    # Schema payload
    descriptions: List[str] = [
        "Change profile name to ${{profile_name}}.",
        "Rename profile to ${{profile_name}}.",
        "Set profile name as ${{profile_name}}.",
        "Update profile name to ${{profile_name}}.",
        "Use ${{profile_name}} as the profile name."
    ]

    def __init__(self, profile_name: str = "Mike", **kwargs) -> None:
        super().__init__(profile_name=profile_name, **kwargs)
        self.add_path(
            "click_microsoft_edge_change_profile_name",
            path=[
                MicrosoftEdgeEditProfile(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the profile name input box in Microsoft Edge Profile Settings"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "a"]),
                WaitAction(duration=1.0),
                TypeAction(text=profile_name, input_mode="copy_paste", thought=f"Change the profile name to '{profile_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the update profile button in Microsoft Edge Profile Settings"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeClearCookiesAndOtherSiteDataOnClose")
class MicrosoftEdgeClearCookiesAndOtherSiteDataOnClose(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_clear_on_close"

    # Schema payload
    descriptions: List[str] = [
        "Set my cookies and other site data to clear on close.",
        "Every time I close Microsoft Edge, clear my cookies and other site data.",
        "Clear my cookies and other site data on close.",
        "Clear my cookies and other site data when I close Microsoft Edge."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_clear_browsing_data_on_close",
            path=[
                MicrosoftEdgeSearchSettings(setting_name="clear browsing data on close"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the toggle radio button for \"Cookies and other site data\""),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeSetFontSize")
class MicrosoftEdgeSetFontSize(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_set_font_size"
    font_size: Argument = Argument(
        value="Very large",
        description="The font size to set."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set font size to ${{font_size}}.",
        "Change page font size to ${{font_size}}.",
        "Use ${{font_size}} font size.",
        "Update font size setting to ${{font_size}}.",
        "Make text size ${{font_size}}."
    ]

    def __init__(self, font_size: str = "Very large", **kwargs) -> None:
        super().__init__(font_size=font_size, **kwargs)
        self.add_path(
            "click_microsoft_edge_set_font_size",
            path=[
                MicrosoftEdgeOpenSettingsMenu(setting_name="appearance/fonts"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Front size\" dropdown menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the \"{font_size}\" option in the \"Front size\" dropdown in Microsoft Edge Settings"),
                WaitAction(duration=1.0)
            ]
        )
        


@register("MicrosoftEdgeOpenClearBrowsingDataMenu")
class MicrosoftEdgeOpenClearBrowsingDataMenu(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_open_clear_browsing_data_menu"

    # Schema payload
    descriptions: List[str] = [
        "Open Clear browsing data menu.",
        "Show the clear browsing data options.",
        "Open clear browsing data settings.",
        "Go to Clear browsing data.",
        "Open the clearing data menu."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_open_clear_browsing_data_menu",
            path=[
                MicrosoftEdgeOpenSettings(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Privacy, search and services\" button in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Clear browsing data\" button in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Choose what to clear\" button"),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "hotkey_microsoft_edge_open_clear_browsing_data_menu",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "delete"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_microsoft_edge_open_clear_browsing_data_menu_fast",
            path=[
                MicrosoftEdgeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Delete browsing data\" button"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeDeleteBrowsingData")
class MicrosoftEdgeDeleteBrowsingData(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_delete_browsing_data"

    # Schema payload
    descriptions: List[str] = [
        "Clear browsing data now.",
        "Delete browsing data.",
        "Erase selected browsing data.",
        "Clear data of selected type.",
        "Remove browsing data now."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_delete_browsing_data",
            path=[
                MicrosoftEdgeOpenClearBrowsingDataMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Browsing history\" option in the \"Choose what to clear\" menu in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Clear now\" button in the \"Choose what to clear\" menu in Microsoft Edge Settings"),
                WaitAction(duration=1.0)
            ]
        )

@register("MicrosoftEdgeChangeDownloadLocation")
class MicrosoftEdgeChangeDownloadLocation(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_change_download_location"
    download_location: Argument = Argument(
        value="C:\\Users\\YourUsername\\Downloads",
        description="The new download location path."
    )

    # Schema payload
    descriptions: List[str] = [
        "Change download location to ${{download_location}}.",
        "Set downloads folder to ${{download_location}}.",
        "Update download directory to ${{download_location}}.",
        "Use ${{download_location}} as download location.",
        "Change the downloads path to ${{download_location}}."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_microsoft_edge_change_download_location",
            path=[
                MicrosoftEdgeOpenSettingsMenu(setting_name="downloads"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Change\" button in the \"Location\" section in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeChangeDefaultSearchEngine")
class MicrosoftEdgeChangeDefaultSearchEngine(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_change_default_search_engine"
    default_search_engine: Argument = Argument(
        value="DuckDuckGo",
        description="The new default search engine."
    )

    # Schema payload
    descriptions: List[str] = [
        "Change default search engine to ${{default_search_engine}}.",
        "Set search engine to ${{default_search_engine}}.",
        "Use ${{default_search_engine}} for address bar searches.",
        "Update default search to ${{default_search_engine}}.",
        "Switch default search engine to ${{default_search_engine}}."
    ]

    def __init__(self, default_search_engine: str = "DuckDuckGo", **kwargs) -> None:
        super().__init__(default_search_engine=default_search_engine, **kwargs)
        self.add_path(
            "click_microsoft_edge_change_default_search_engine",
            path=[
                MicrosoftEdgeOpenSettingsMenu(setting_name="privacy/services/search"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the dropdown menu in the \"Seach Engine used in the address bar\" section in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the {default_search_engine} option in the \"Browser selection\" dropdown in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
            ]
        )


@register("MicrosoftEdgeSetMicrosoftDefenderSmartScreen")
class MicrosoftEdgeSetMicrosoftDefenderSmartScreen(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_set_microsoft_defender_smart_screen"
    enabled: Argument = Argument(
        value=True,
        description="Whether to enable Microsoft Defender SmartScreen."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set Microsoft Defender SmartScreen to ${{enabled}}.",
        "Turn ${{enabled}} SmartScreen.",
        "${{enabled}} Microsoft Defender SmartScreen.",
        "Change SmartScreen to ${{enabled}}.",
        "Enable or disable SmartScreen."
    ]

    def __init__(self, enabled: bool = True, **kwargs) -> None:
        super().__init__(enabled=enabled, **kwargs)
        self.add_path(
            "click_microsoft_edge_set_microsoft_defender_smart_screen",
            path=[
                MicrosoftEdgeOpenSettingsMenu(setting_name="privacy/security"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Enable Microsoft Defender Smart Screen\" toggle button in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
            ]
        )

@register("MicrosoftEdgeSetMicrosofEnhancedSecurity")
class MicrosoftEdgeSetMicrosofEnhancedSecurity(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_set_microsoft_enhanced_security"
    enabled: Argument = Argument(
        value=True,
        description="Whether to enable Microsoft Enhanced Security."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set Microsoft Enhanced Security to ${{enabled}}.",
        "Turn ${{enabled}} Enhanced Security.",
        "${{enabled}} Microsoft Enhanced Security.",
        "Change Enhanced Security to ${{enabled}}.",
        "Enable or disable Enhanced Security."
    ]

    def __init__(self, enabled: bool = True, **kwargs) -> None:
        super().__init__(enabled=enabled, **kwargs)
        self.add_path(
            "click_microsoft_edge_set_microsoft_enhanced_security",
            path=[
                MicrosoftEdgeOpenSettingsMenu(setting_name="privacy/security"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Enhance your security on the web\" toggle button in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
            ]
        )

@register("MicrosoftEdgeSetCustomHomeSite")
class MicrosoftEdgeSetCustomHomeSite(BaseComposeAction):
    # Canonical identifiers
    type: str = "microsoft_edge_set_custom_home_site"
    custom_home_site: Argument = Argument(
        value="https://www.google.com",
        description="The new custom home site URL."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set custom home site to ${{url}}.",
        "Add custom start page ${{url}}.",
        "Use ${{url}} as home site.",
        "Set startup page to ${{url}}.",
        "Add ${{url}} to startup sites."
    ]

    def __init__(self, custom_home_site: str = "https://www.google.com", **kwargs) -> None:
        super().__init__(custom_home_site=custom_home_site, **kwargs)
        self.add_path(
            "click_microsoft_edge_set_custom_home_site",
            path=[
                MicrosoftEdgeOpenSettingsMenu(setting_name="startHomeNTP"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Open custom sites\" button in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Add site\" button in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the textbox in the \"Add site\" bar in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                TypeAction(text=custom_home_site, input_mode="copy_paste", thought=f"Set the custom home site to '{custom_home_site}' in Microsoft Edge Settings"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Add\" button in Microsoft Edge Settings"),
                WaitAction(duration=1.0)
            ]
        )


