from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, RightClickAction, ScrollAction
from .common_action import LaunchApplication, SwitchtoFocusApp
from .argument import Argument

__all__ = []

class ChromeBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="chrome",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Chrome",
        description="The name of the Chrome application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register("ChromeLaunch")
class ChromeLaunch(ChromeBaseAction, LaunchApplication):
    # Canonical identifiers
    type: str = "chrome_launch"
    
    # Schema payload
    descriptions: List[str] = [
        "Open Google Chrome.",
        "Launch Chrome browser.",
        "Start Chrome.",
        "Run the Chrome application.",
        "Open the Chrome app."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)


@register("ChromeOpenURL")
class ChromeOpenURL(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_url"
    url: Argument = Argument(
        value="https://www.google.com",
        description="URL to open in Chrome."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open website ${{url}}.",
        "Navigate to ${{url}}.",
        "Go to ${{url}}.",
        "Load page ${{url}}.",
        "Visit ${{url}} in Chrome."
    ]

    def __init__(self, url: str = "https://www.google.com", **kwargs) -> None:
        super().__init__(url=url, **kwargs)
        self.add_path(
            "open_chrome_url",
            path=[ 
                SingleClickAction(thought="Click the URL address bar in Chrome"),
                WaitAction(duration=1.0),
                TypeAction(text=url, input_mode="copy_paste", thought=f"Enter the URL '{url}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to navigate to the URL."),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_url",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["Ctrl", "l"], thought="Press Ctrl+L to open the URL address bar in Chrome"),
                WaitAction(duration=2.0),
                TypeAction(text=url, input_mode="copy_paste", thought=f"Enter the URL '{url}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to navigate to the URL."),
                WaitAction(duration=2.0)
            ]
        )


@register("ChromeNewTab")
class ChromeNewTab(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_new_tab"

    # Schema payload
    descriptions: List[str] = [
        "Open a new tab.",
        "Create a new Chrome tab.",
        "Start a blank tab.",
        "Open another tab.",
        "Add new tab in Chrome."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_chrome_new_tab",
            path=[
                SingleClickAction(thought="Click the new tab button (+) in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeCloseTab")
class ChromeCloseTab(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_close_tab"

    # Schema payload
    descriptions: List[str] = [
        "Close current tab.",
        "Shut this tab.",
        "Exit the tab.",
        "Close the active tab.",
        "Remove this tab."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_chrome_close_tab",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "w"], thought="Press Ctrl+W to close the current tab"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeSwitchTab")
class ChromeSwitchTab(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_switch_tab"
    index: Argument = Argument(
        value=1,
        description="Index of the tab to switch to."
    )

    # Schema payload
    descriptions: List[str] = [
        "Switch to tab ${{index}}.",
        "Change to tab number ${{index}}.",
        "Go to tab ${{index}}.",
        "Move to tab ${{index}} in Chrome.",
        "Switch Chrome to tab ${{index}}."
    ]

    def __init__(self, index: int = 1, **kwargs) -> None:
        super().__init__(index=index, **kwargs)
        self.add_path(
            "hotkey_chrome_switch_tab",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", str(index)]),
                WaitAction(duration=1.0)
            ]
        )

@register("ChromeReopenClosedTab")
class ChromeReopenClosedTab(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_reopen_close_tab"

    # Schema payload
    descriptions: List[str] = [
        "Reopen last closed tab.",
        "Restore recently closed tab.",
        "Reopen previous closed tab.",
        "Bring back last closed tab.",
        "Recover closed Chrome tab."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_chrome_reopen_close_tab",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "shift", "t"], thought="Press Ctrl+Shift+T to reopen the last closed tab"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeOpenHistory")
class ChromeOpenHistory(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_history"

    # Schema payload
    descriptions: List[str] = [
        "Open browsing history.",
        "Show Chrome history.",
        "View my history in Chrome.",
        "Check past browsing history.",
        "See Chrome history."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_chrome_history",
            path=[
                HotKeyAction(keys=["ctrl", "h"], thought="Press Ctrl+H to open Chrome history"),
                WaitAction(duration=1.0)
            ]
        )

@register("ChromeSearchHistory")
class ChromeSearchHistory(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_search_history"
    query: Argument = Argument(
        value="wikipedia",
        description="Query to search for in Chrome history."
    )

    # Schema payload
    descriptions: List[str] = [
        "Search Chrome history for ${{query}}.",
        "Look up history entries for ${{query}}.",
        "Find history entries for ${{query}}.",
        "Search Chrome history for ${{query}}."
    ]

    def __init__(self, query: str = "wikipedia", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "click_chrome_search_history",
            path=[
                SingleClickAction(thought="Click the \"Search history\" box"),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Search for the query '{query}' in Chrome"),
                WaitAction(duration=1.0)
            ]
        )

@register("ChromeSortHistoryByGroup")
class ChromeSortHistoryByGroup(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_sort_history_by_group"
    
    # Schema payload
    descriptions: List[str] = [
        "Switch Chrome History to the 'By group' view.",
        "Group Chrome browsing history entries by topic in the History page.",
        "Open the 'By group' tab to cluster related Chrome history items together.",
        "Arrange Chrome history so visits are grouped into topic-based cards instead of a time-ordered list."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_sort_history_by_group",
            path=[
                SingleClickAction(thought="Click the \"By group\" button in Chrome history page"),
                WaitAction(duration=1.0)
            ]
        )

@register("ChromeDeleteGroupHistory")
class ChromeDeleteGroupHistory(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_delete_group_history"
    
    # Schema payload
    descriptions: List[str] = [
        "Open Chrome's History controls to delete visited pages.",
        "Use the History page to delete selected browsing records.",
        "Open the dialog to remove specific entries from Chrome browsing history.",
        "Delete site visits from the Chrome History view (e.g., a group or selection).",
        "Remove chosen URLs from Chrome's recorded history without clearing cookies or cache."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_delete_group_history",
            path=[
                SingleClickAction(thought="Click in the middle of the verticle three dots located under the \"By group\" menu on the Chrome history page. Do NOT click the three menu dots on the top bar."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Delete all from history\" button"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the \"Delete\" button"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeClearBrowsingData")
class ChromeClearBrowsingData(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_clear_browsing_data"

    # Schema payload
    descriptions: List[str] = [
        "Clear browsing history.",
        "Delete cache and cookies.",
        "Erase browsing data.",
        "Remove Chrome history and cache.",
        "Clear cookies and history."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "clear_chrome_browsing_data",
            path=[
                HotKeyAction(keys=["ctrl", "shift", "delete"], thought="Press Ctrl+Shift+Delete to clear browsing data"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_chrome_clear_browsing_data",
            path=[
                SingleClickAction(thought="Click the Chrome menu (three dots) button in Chrome"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the delete browsing data button in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeOpenDownloads")
class ChromeOpenDownloads(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_downloads"

    # Schema payload
    descriptions: List[str] = [
        "Open downloads page.",
        "View downloaded files.",
        "Check my Chrome downloads.",
        "Show list of downloads.",
        "See all downloaded items."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_chrome_downloads",
            path=[
                HotKeyAction(keys=["ctrl", "j"], thought="Press Ctrl+J to open downloads page"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_chrome_downloads",
            path=[
                SingleClickAction(thought="Click the Chrome menu (three dots) button in Chrome"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the downloads button in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeBookmarkPage")
class ChromeBookmarkPage(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_bookmark_page"

    # Schema payload
    descriptions: List[str] = [
        "Bookmark this page.",
        "Add current page to bookmarks.",
        "Save page to bookmarks.",
        "Bookmark the active tab.",
        "Add this site to bookmarks."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "chrome_bookmark_page",
            path=[
                HotKeyAction(keys=["ctrl", "d"], thought="Press Ctrl+D to bookmark the current page"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_chrome_bookmark_page",
            path=[
                SingleClickAction(thought="Click the bookmark (star) button in Chrome"),
                WaitAction(duration=1.0),
            ]
        )


@register("ChromeOpenBookmark")
class ChromeOpenBookmark(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_bookmark"
    title: Argument = Argument(
        value="Google",
        description="Title of the bookmark to open."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open bookmark ${{title}}.",
        "Go to bookmarked page ${{title}}.",
        "Open site ${{title}} from bookmarks.",
        "Load bookmark ${{title}}.",
        "Visit ${{title}} bookmark."
    ]

    def __init__(self, title: str = "Google", **kwargs) -> None:
        super().__init__(title=title, **kwargs)
        self.add_path(
            "open_chrome_bookmark",
            path=[
                SingleClickAction(thought=f"Click the bookmark {title} in Chrome"),
                WaitAction(duration=1.0)
            ]
        )

@register("ChromeSearchWeb")
class ChromeSearchWeb(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_search_web"
    query: Argument = Argument(
        value="weather today",
        description="Search query for the web."
    )

    # Schema payload
    descriptions: List[str] = [
        "Search the web for ${{query}}.",
        "Google ${{query}}.",
        "Find results for ${{query}}.",
        "Look up ${{query}}.",
        "Search online: ${{query}}."
    ]

    def __init__(self, query: str = "weather today", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "click_chrome_search_web",
            path=[
                SingleClickAction(thought="Click the search box in Chrome"),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Search for the query '{query}' in Chrome"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_search_web",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "l"], thought="Press Ctrl+L to open the search box in Chrome"),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Search for the query '{query}' in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeDownloadFile")
class ChromeDownloadFile(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_download_file"
    url: Argument = Argument(
        value="https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe",
        description="URL of the file to download."
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
            "click_chrome_download_file",
            path=[
                SingleClickAction(thought="Click the URL address bar in Chrome"),
                WaitAction(duration=1.0),
                TypeAction(text=url, input_mode="copy_paste", thought=f"Download the file from '{url}' in Chrome"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_download_file",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "l"], thought="Press Ctrl+L to open the search box in Chrome"),
                WaitAction(duration=1.0),
                TypeAction(text=url, input_mode="copy_paste", thought=f"Download the file from '{url}' in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeOpenIncognito")
class ChromeOpenIncognito(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_incognito"

    # Schema payload
    descriptions: List[str] = [
        "Open incognito window.",
        "Start private browsing.",
        "Launch Chrome incognito mode.",
        "New incognito window.",
        "Open Chrome private session."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_open_incognito",
            path=[
                ChromeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the new incognito window button in Chrome"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_open_incognito",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "shift", "n"], thought="Press Ctrl+Shift+N to open the new incognito window in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeZoomIn")
class ChromeZoomIn(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_zoom_in"

    # Schema payload
    descriptions: List[str] = [
        "Zoom in Chrome.",
        "Increase zoom level.",
        "Enlarge the webpage.",
        "Magnify page view.",
        "Zoom closer in Chrome."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_zoom_in",
            path=[
                ChromeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the zoom in (+) button in Chrome"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_zoom_in",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "plus"], thought="Press Ctrl++ to zoom in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeZoomOut")
class ChromeZoomOut(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_zoom_out"

    # Schema payload
    descriptions: List[str] = [
        "Zoom out Chrome.",
        "Decrease zoom level.",
        "Reduce page zoom.",
        "Zoom out on the page.",
        "Shrink page view."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_zoom_out",
            path=[
                ChromeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the zoom out (-) button in Chrome"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_zoom_out",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "minus"], thought="Press Ctrl+- to zoom out Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeDeveloperTools")
class ChromeDeveloperTools(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_developer_tools"

    # Schema payload
    descriptions: List[str] = [
        "Open developer tools.",
        "Inspect element with DevTools.",
        "Show Chrome developer panel.",
        "Launch Chrome DevTools.",
        "Debug with developer tools."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_developer_tools",
            path=[
                ChromeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'More tools' option in Chrome menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Developer tools' option in Chrome menu"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "right_click_chrome_developer_tools",
            path=[
                RightClickAction(thought="Right click the Chrome webpage."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Inspect' option in Chrome menu"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_developer_tools",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "shift", "c"], thought="Press Ctrl+Shift+C to inspect the element in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromePrintPage")
class ChromePrintPage(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_print_page"

    # Schema payload
    descriptions: List[str] = [
        "Print this page.",
        "Send current page to printer.",
        "Print webpage.",
        "Start printing tab.",
        "Print the active page."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_print_page",
            path=[
                ChromeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the print button in Chrome menu"),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "right_click_chrome_print_page",
            path=[
                RightClickAction(thought="Right click the Chrome webpage."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the print button in Chrome menu"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "hotkey_chrome_print_page",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["ctrl", "p"], thought="Press Ctrl+P to print the page in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeOpenSettings")
class ChromeOpenSettings(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_settings"

    # Schema payload
    descriptions: List[str] = [
        "Open Chrome settings.",
        "Access Chrome settings.",
        "Open Chrome settings.",
        "Start Chrome settings.",
        "Open the active settings."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_open_settings",
            path=[
                ChromeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the settings button in Chrome"),
                WaitAction(duration=1.0),
            ]
        )


@register("ChromeSearchSettings")
class ChromeSearchSettings(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_search_settings"
    setting_name: Argument = Argument(
        value="privacy settings",
        description="Name of the setting to search for."
    )

    # Schema payload
    descriptions: List[str] = [
        "Search Chrome settings for ${{setting_name}}.",
        "Search the active settings for ${{setting_name}}.",
        "Search the settings for ${{setting_name}}.",
        "Find the settings for ${{setting_name}}."
    ]

    def __init__(self, setting_name: str = "privacy settings", **kwargs) -> None:
        super().__init__(setting_name=setting_name, **kwargs)
        self.add_path(
            "click_chrome_search_settings",
            path=[
                SingleClickAction(thought="Click the settings search box in Chrome"),
                WaitAction(duration=1.0),
                TypeAction(text=setting_name, input_mode="copy_paste", thought=f"Search for the setting name '{setting_name}' in Chrome"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought=f"Press Enter to search for the setting name '{setting_name}' in Chrome"),
                WaitAction(duration=1.0)
            ]
        )


@register("ChromeOpenSpecificSettingsPage")
class ChromeOpenSpecificSettingsPage(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_specific_settings_page"
    subpage_url: Argument = Argument(
        value="cookies",
        description="URL of the settings page to navigate to."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open ${{subpage_url}} in Chrome settings.",
        "Access ${{subpage_url}} in Chrome settings.",
        "Start ${{subpage_url}} in Chrome settings.",
        "Open the ${{subpage_url}} settings page in Chrome."
    ]

    def __init__(self, subpage_url: str = "cookies", **kwargs) -> None:
        super().__init__(subpage_url=subpage_url, **kwargs)
        if subpage_url.startswith("chrome://settings/"):
            subpage_url = subpage_url[len("chrome://settings/"):]
        self.add_path(
            "click_chrome_open_specific_settings_page",
            path=[
                ChromeOpenURL(url=f"chrome://settings/{subpage_url}"),
                WaitAction(duration=2.0)
            ]
        )


@register("ChromeBlockThirdPartyCookies")
class ChromeBlockThirdPartyCookies(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_block_third_party_cookies"

    # Schema payload
    descriptions: List[str] = [
        "Block third party cookies.",
        "Disable third party cookies.",
        "Block third party cookies.",
        "Block third party cookies."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_block_third_party_cookies",
            path=[
                SingleClickAction(thought="Click the 'Block third party cookies' option in Chrome"),
                WaitAction(duration=2.0)
            ]
        )


@register("ChromeAllowThirdPartyCookies")
class ChromeAllowThirdPartyCookies(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_allow_third_party_cookies"

    # Schema payload
    descriptions: List[str] = [
        "Allow third party cookies.",
        "Enable third party cookies.",
        "Allow third party cookies.",
        "Allow third party cookies."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_allow_third_party_cookies",
            path=[
                SingleClickAction(thought="Click the 'Allow third party cookies' option in Chrome"),
                WaitAction(duration=2.0)
            ]
        )

@register("ChromeOpenMenu")
class ChromeOpenMenu(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_open_menu"

    # Schema payload
    descriptions: List[str] = [
        "Open Chrome menu.",
        "Access Chrome menu.",
        "Start Chrome menu.",
        "Open the active Chrome menu."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_open_menu",
            path=[
                SingleClickAction(thought="Click the Chrome menu (three dots) button in Chrome"),
                WaitAction(duration=1.0),
            ]
        )
        self.add_path(
            "hotkey_chrome_open_menu",
            path=[
                SwitchtoFocusApp(application_name=self.application_name),
                HotKeyAction(keys=["alt", "e"], thought="Press Alt+E to open the Chrome menu"),
                WaitAction(duration=1.0),
            ]
        )

@register("ChromeCreateDesktopShortcut")
class ChromeCreateDesktopShortcut(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_create_desktop_shortcut"
    shortcut_name: Argument = Argument(
        value="StackOverflow",
        description="Name of the desktop shortcut to create."
    )

    # Schema payload
    descriptions: List[str] = [
        "Create a desktop shortcut to the current site called ${{shortcut_name}}.",
        "Add a desktop shortcut for this page called ${{shortcut_name}}.",
        "Create shortcut on desktop called ${{shortcut_name}}.",
        "Create a desktop shortcut for the current site called ${{shortcut_name}}."
    ]

    def __init__(self, shortcut_name: str = "StackOverflow", **kwargs) -> None:
        super().__init__(shortcut_name=shortcut_name, **kwargs)
        self.add_path(
            "click_chrome_open_menu",
            path=[
                ChromeOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Cast, save, and share' option in Chrome menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Create shortcut' button in the 'Cast, save, and share' menu"),
                WaitAction(duration=1.0),
                TypeAction(text=shortcut_name, input_mode="copy_paste", thought=f"Enter the shortcut name '{shortcut_name}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Create' button in the 'Create shortcut' dialog"),
                WaitAction(duration=1.0),
            ]
        )


@register("ChromeSetFontSize")
class ChromeSetFontSize(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_set_font_size"
    font_size: Argument = Argument(
        value="Large",
        description="Size of the font to set."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set font size to ${{font_size}}.",
        "Change font size to ${{font_size}}.",
        "Use ${{font_size}} font size.",
        "Update font size setting to ${{font_size}}.",
        "Make text size ${{font_size}}."
    ]

    def __init__(self, font_size: str = "Large", **kwargs) -> None:
        super().__init__(font_size=font_size, **kwargs)
        self.add_path(
            "click_chrome_set_font_size",
            path=[
                ChromeOpenSpecificSettingsPage(subpage_url="appearance"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the scroll bar on the very right of the chrome settings page"),
                WaitAction(duration=1.0),
                ScrollAction(direction="down", duration=2.0),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Front size' dropdown menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the '{font_size}' option in the 'Front size' dropdown in Chrome Settings"),
                WaitAction(duration=1.0),
            ]
        )

@register("ChromeSetDefaultSearchEngine")
class ChromeSetDefaultSearchEngine(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_set_default_search_engine"
    engine: Argument = Argument(
        value="Bing",
        description="Search engine to set as default."
    )

    # Schema payload
    descriptions: List[str] = [
        "Set default search engine to ${{engine}}.",
        "Change default search to ${{engine}}.",
        "Use ${{engine}} for address bar searches."
    ]

    def __init__(self, engine: str = "Bing", **kwargs) -> None:
        super().__init__(engine=engine, **kwargs)
        self.add_path(
            "click_chrome_set_font_size",
            path=[
                ChromeOpenSpecificSettingsPage(subpage_url="search"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Change' button in the Search engine used"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the '{engine}' radio button option"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Set as default' button"),
                WaitAction(duration=1.0)
            ]
        )

@register("ChromeAddBookmarkFolder")
class ChromeAddBookmarkFolder(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_add_bookmark_folder"
    folder_name: Argument = Argument(
        value="My Bookmarks",
        description="Name of the bookmark folder to add."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add a bookmark folder called ${{folder_name}}.",
        "Create a new folder named ${{folder_name}} on the bookmarks bar.",
        "Add a folder to bookmarks called ${{folder_name}}."
    ]

    def __init__(self, folder_name: str = "Favorites", **kwargs) -> None:
        super().__init__(folder_name=folder_name, **kwargs)
        self.add_path(
            "click_chrome_set_font_size",
            path=[
                RightClickAction(thought="Right click on the bookmarks bar"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Add folder' option"),
                WaitAction(duration=1.0),
                TypeAction(text=folder_name, input_mode="copy_paste", thought=f"Enter the folder name '{folder_name}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought=f"Press Enter to confirm the folder name"),
                WaitAction(duration=1.0),
            ]
        )

@register("ChromeSetEnhancedProtection")
class ChromeSetEnhancedProtection(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_set_enhanced_protection"

    # Schema payload    
    descriptions: List[str] = [
        "Set enhanced protection to on.",
        "Change enhanced protection to on.",
        "Enable enhanced protection."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_set_enhanced_protection",
            path=[
                ChromeOpenSpecificSettingsPage(subpage_url="security"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the 'Enhanced protection' radio button"),
                WaitAction(duration=1.0),
            ]
        )

@register("ChromeChangeSiteDataSettings")
class ChromeChangeSiteDataSettings(ChromeBaseAction):
    # Canonical identifiers
    type: str = "chrome_change_site_data_settings"

    # Schema payload    
    descriptions: List[str] = [
        "Change site data settings on chrome",
        "Modify site data settings on chrome",
        "Adjust site data settings on chrome"
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_chrome_change_site_data_settings",
            path=[
                ChromeOpenSpecificSettingsPage(subpage_url="content/siteData"),
                WaitAction(duration=1.0),
            ]
        )


@register("ChromeChangeDefaultSideDataBehaviour")
class ChromeChangeDefaultSideDataBehaviour(ChromeBaseAction):
    type: str = "chrome_change_default_side_data_behaviour"
    behaviour: Argument = Argument(
        value="Delete data sites have saved to your device when you close all windows",
        description="Behaviour of the default side data."
    )

    # Schema payload    
    descriptions: List[str] = [
        "Change default side data behaviour on chrome to ${{behaviour}",
        "The behaviour of the default side data should be set to ${{behaviour}}"
        "The default side data behaviour should be set to ${{behaviour}}"
    ]

    def __init__(self, behaviour: str = "Delete data sites have saved to your device when you close all windows", **kwargs) -> None:
        super().__init__(behaviour=behaviour, **kwargs)
        self.add_path(
            "click_chrome_change_default_side_data_behaviour",
            path=[
                ChromeOpenSpecificSettingsPage(subpage_url="content/siteData"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the '{behaviour}' radio button"),
                WaitAction(duration=1.0),
            ]
        )