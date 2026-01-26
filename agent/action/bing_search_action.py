from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import (
    register, 
    SingleClickAction, 
    DoubleClickAction, 
    RightClickAction,
    WaitAction, 
    TypeAction, 
    HotKeyAction
)
from .argument import Argument
from .common_action import LaunchApplication
from .microsoft_edge_action import MicrosoftEdgeOpenURL
from .argument import Argument

__all__ = []

class BingSearchBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="bing_search",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Bing Search",
        description="The name of the Bing Search application.",
        frozen=True
    )
    base_application_name: Argument = Argument(
        value="Microsoft Edge",
        description="The name of the base application.",
        frozen=True
    )
    base_url: Argument = Argument(
        value="https://www.bing.com",
        description="The base URL for Bing Search.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register("BingSearchLaunch")
class BingSearchLaunch(BingSearchBaseAction, LaunchApplication):
    # Canonical identifiers
    type: str = "bing_search_launch"
    
    # Schema payload
    descriptions: List[str] = [
      "Open Bing Search.",
      "Launch the Bing app.",
      "Start Bing search engine.",
      "Run Bing.",
      "Open the Bing application."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.base_application_name.value, **kwargs) # Assuming Bing Search is accessed via Microsoft Edge

@register("BingSearchQuery")
class BingSearchQuery(BingSearchBaseAction):
    type: str = "bing_search_query"
    descriptions: List[str] = [
      "Search for ${{query}}.",
      "Look up ${{query}} on Bing.",
      "Find results about ${{query}}.",
      "Search Bing for ${{query}}.",
      "Look for information about ${{query}}."
    ]
    query: Argument = Argument(
        value="search term",
        description="Search query for Bing."
    )

    def __init__(self, query: str = "search term", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "input_text_query_and_enter_in_default_bing_search_box",
            path=[
                SingleClickAction(thought="Navigate to the search box on the current search page."),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Enter the query '{query}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )


@register("BingOpenImageSearch")
class BingOpenImageSearch(BingSearchBaseAction):
    type: str = "bing_open_image_search"
    descriptions: List[str] = [
      "Search images for ${{query}}.",
      "Look up pictures of ${{query}}.",
      "Find images about ${{query}}.",
      "Show image results for ${{query}}.",
      "Look for photos of ${{query}}."
    ]
    query: Argument = Argument(
        value="search term",
        description="Search query for image search."
    )

    def __init__(self, query: str = "search term", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "input_text_query_and_select_image_in_bing_search",
            path=[
                BingSearchQuery(query=query),
                SingleClickAction(thought="Navigate to 'image' tab option to check search results of images."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingOpenVideoSearch")
class BingOpenVideoSearch(BingSearchBaseAction):
    type: str = "bing_open_video_search"
    descriptions: List[str] = [
      "Search videos for ${{query}}.",
      "Look up videos of ${{query}}.",
      "Find video results about ${{query}}.",
      "Show video results for ${{query}}.",
      "Look for video content about ${{query}}."
    ]
    query: Argument = Argument(
        value="search term",
        description="Search query for video search."
    )

    def __init__(self, query: str = "search term", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "input_text_query_and_select_video_in_bing_search",
            path=[
                BingSearchQuery(query=query),
                SingleClickAction(thought="Navigate to 'video' tab option to check search results of videos."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingOpenNewsSearch")
class BingOpenNewsSearch(BingSearchBaseAction):
    type: str = "bing_open_news_search"
    descriptions: List[str] = [
      "Search news for ${{query}}.",
      "Look up news articles about ${{query}}.",
      "Find news results about ${{query}}.",
      "Show news results for ${{query}}.",
      "Look for news content about ${{query}}."
    ]
    query: Argument = Argument(
        value="search term",
        description="Search query for news search."
    )

    def __init__(self, query: str = "search term", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "input_text_query_and_select_news_in_bing_search",
            path=[
                BingSearchQuery(query=query),
                SingleClickAction(thought="Navigate to 'news' tab option to check search results of news."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingSearchMaps")
class BingOpenMaps(BingSearchBaseAction):
    type: str = "bing_search_maps"
    descriptions: List[str] = [
      "Search maps for ${{query}}.",
      "Look up locations of ${{query}}.",
      "Find map results about ${{query}}.",
      "Show map results for ${{query}}.",
      "Look for map content about ${{query}}."
    ]
    query: Argument = Argument(
        value="search term",
        description="Search query for maps search."
    )

    def __init__(self, query: str = "search term", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "input_text_query_and_select_maps_in_bing_search",
            path=[
                BingSearchQuery(query=query),
                SingleClickAction(thought="Navigate to 'maps' tab option to check search results of maps."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingSearchShopping")
class BingSearchShopping(BingSearchBaseAction):
    type: str = "bing_search_shopping"
    descriptions: List[str] = [
      "Search shopping results for ${{query}}.",
      "Look up products related to ${{query}}.",
      "Find shopping deals about ${{query}}.",
      "Show shopping results for ${{query}}.",
      "Look for product information about ${{query}}."
    ]
    query: Argument = Argument(
        value="search term",
        description="Search query for shopping search."
    )

    def __init__(self, query: str = "search term", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "input_text_query_and_select_shop_in_bing_search",
            path=[
                BingSearchQuery(query=query),
                SingleClickAction(thought="Navigate to 'shopping' tab option to check search results of shopping."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingOpenResult")
class BingOpenResult(BingSearchBaseAction): 
    type: str = "bing_open_result"
    descriptions: List[str] = [
      "Open result ${{index}}.",
      "Click on result ${{index}}.",
      "Go to the ${{index}} result.",
      "Select search result ${{index}}.",
      "Open search item number ${{index}}."
    ]
    index: Argument = Argument(
        value=1,
        description="Index of the search result to open."
    )

    def __init__(self, index: int = 1, **kwargs) -> None:
        super().__init__(index=index, **kwargs)
        self.add_path(
            "bing_open_search_result_by_index",
            path=[
                SingleClickAction(thought=f"Navigate to the {index}-th search result in the current Bing Search result page, skipping any promotional items or modules before the search results."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingSaveResult") # Not implemented yet, requires clarification on "save" action
class BingSaveResult(BingSearchBaseAction): 
    type: str = "bing_save_result"
    descriptions: List[str] = [
      "Save result ${{index}}.",
      "Bookmark result ${{index}}.",
      "Add result ${{index}} to favorites.",
      "Store search result ${{index}}.",
      "Keep result ${{index}} for later."
    ]
    index: Argument = Argument(
        value=1,
        description="Index of the search result to save."
    )

    def __init__(self, index: int = 1, **kwargs) -> None:
        super().__init__(index=index, **kwargs)
        # Not yet implemented

@register("BingSearchVoice")
class BingSearchVoice(BingSearchBaseAction):
    type: str = "bing_search_voice"
    descriptions: List[str] = [
      "Search by voice.",
      "Start a voice search.",
      "Use microphone for search.",
      "Speak query for Bing.",
      "Voice search mode."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "bing_voice_search",
            path=[
                SingleClickAction(thought="Navigate to the 'voice search' button in the search box."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingTranslateText") # needs clarification on source lanaguage. 
class BingTranslateText(BingSearchBaseAction):
    type: str = "bing_translate_text"
    descriptions: List[str] = [
      "Translate ${{text}} to ${{language}}.",
      "Convert ${{text}} into ${{language}}.",
      "Translate ${{text}}.",
      "Get translation of ${{text}} in ${{language}}.",
      "Show ${{text}} in ${{language}}."
    ]
    text: Argument = Argument(
        value="text to translate",
        description="Text to be translated."
    )
    language: Argument = Argument(
        value="target language",
        description="Target language for translation."
    )

    def __init__(self, text: str = "text to translate", language: str = "target language", **kwargs) -> None:
        super().__init__(text=text, language=language, **kwargs)
        self.add_path(
            "bing_translate_text",
            path=[
                # select target language
                SingleClickAction(thought=f"Select the box of target language in the translation options, typically on the right side."),
                WaitAction(duration=1.0),
                TypeAction(text=language, input_mode="copy_paste", thought=f"Enter the target language: '{language}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0),
                # enter translation text (english default)
                SingleClickAction(thought="Navigate to the translation input area."),
                WaitAction(duration=1.0),
                TypeAction(text=text, input_mode="copy_paste", thought=f"Enter the text to be translated: '{text}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )


@register("BingCheckWeather") # needs clarification on the difference between this and BingSearchQuery. may discard.
class BingCheckWeather(BingSearchBaseAction):
    type: str = "bing_check_weather"
    descriptions: List[str] = [
      "Check weather in ${{location}}.",
      "Show forecast for ${{location}}.",
      "Look up weather ${{location}}.",
      "Weather update ${{location}}.",
      "See weather details for ${{location}}."
    ]
    location: Argument = Argument(
        value="location",
        description="Location to check weather for."
    )

    def __init__(self, location: str = "location", **kwargs) -> None:
        super().__init__(location=location, **kwargs)

@register("BingCheckStock") # needs clarification on the difference between this and BingSearchQuery. may discard.
class BingCheckStock(BingSearchBaseAction):
    type: str = "bing_check_stock"
    descriptions: List[str] = [
      "Check stock price of ${{ticker}}.",
      "Show ${{ticker}} stock.",
      "Look up share price for ${{ticker}}.",
      "Get stock info ${{ticker}}.",
      "View current ${{ticker}} stock."
    ]
    ticker: Argument = Argument(
        value="stock ticker",
        description="Stock ticker symbol to check."
    )

    def __init__(self, ticker: str = "stock ticker", **kwargs) -> None:
        super().__init__(ticker=ticker, **kwargs)

@register("BingSearchDefinition") # needs clarification on the difference between this and BingSearchQuery. may discard.
class BingSearchDefinition(BingSearchBaseAction):
    type: str = "bing_search_definition"
    descriptions: List[str] = [
      "Define ${{term}}.",
      "Get definition of ${{term}}.",
      "Look up ${{term}}.",
      "Find meaning of ${{term}}.",
      "Show me ${{term}}."
    ]
    term: Argument = Argument(
        value="term",
        description="Term to get definition for."
    )

    def __init__(self, term: str = "term", **kwargs) -> None:
        super().__init__(term=term, **kwargs)
        # not yet implemented


@register("BingSearchNearby") # needs clarification on the difference between this and BingSearchQuery. may discard.
class BingSearchNearby(BingSearchBaseAction):
    type: str = "bing_search_nearby"
    descriptions: List[str] = [
      "Search nearby for ${{place_type}}.",
      "Find ${{place_type}} near me.",
      "Look up close ${{place_type}}.",
      "Locate nearby ${{place_type}}.",
      "Search for ${{place_type}} around here."
    ]
    place_type: Argument = Argument(
        value="place type",
        description="Type of place to search for nearby."
    )

    def __init__(self, place_type: str = "place type", **kwargs) -> None:
        super().__init__(place_type=place_type, **kwargs)

@register("BingOpenSettings") 
class BingOpenSettings(BingSearchBaseAction):
    type: str = "bing_open_settings_from_bing_homepage"
    descriptions: List[str] = [
      "Open Bing settings.",
      "Go to preferences.",
      "Change Bing options.",
      "Open search settings.",
      "Show Bing configurations."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_bing_settings",
            path=[
                SingleClickAction(thought="Click the right-up menu bar (three horizontal lines) button in Microsoft Edge Profile Settings. Do not click on the browswer settings."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'Settings' option in the dropdown menu"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click on 'More' option in the dropdown menu to open the full settings page"),
                WaitAction(duration=1.0),
            ]
        )

@register("BingChangeSetting") # needs clarification on the setting. may divide into multiple primitive actions
class BingChangeSetting(BingSearchBaseAction):
    type: str = "bing_change_setting"
    descriptions: List[str] = [
      "Change Bing setting ${{setting_name}} to ${{value}}.",
      "Update search setting ${{setting_name}}.",
      "Modify ${{setting_name}} option in Bing.",
      "Set Bing ${{setting_name}} to ${{value}}.",
      "Adjust ${{setting_name}} in Bing preferences."
    ]
    setting_name: Argument = Argument(
        value="setting name",
        description="Name of the setting to change."
    )
    value: Argument = Argument(
        value="setting value",
        description="Value to set for the setting."
    )

    def __init__(self, setting_name: str = "setting name", value: str = "setting value", **kwargs) -> None:
        super().__init__(setting_name=setting_name, value=value, **kwargs)

# potential useful primitive actions to add later: copilot search and copilot chat
@register("BingCopilotSearch")
class BingCopilotSearch(BingSearchBaseAction):
    type: str = "bing_copilot_search"
    descriptions: List[str] = [
      "Search videos for ${{query}}.",
      "Look up videos of ${{query}}.",
      "Find video results about ${{query}}.",
      "Show video results for ${{query}}.",
      "Look for video content about ${{query}}."
    ]
    query: Argument = Argument(
        value="search term",
        description="Search query for Copilot search."
    )

    def __init__(self, query: str = "search term", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "input_text_query_and_select_copilot_search",
            path=[
                BingSearchQuery(query=query),
                SingleClickAction(thought="Navigate to 'search' tab option to start the copilot search. Note that it is next to 'ALL' under the search box."),
                WaitAction(duration=1.0)
            ]
        )

@register("BingOpenCopilotChat") # this can be accessible via https://copilot.microsoft.com/ (alt)
class BingOpenCopilotChat(BingSearchBaseAction):
    type: str = "bing_copilot_chat"
    descriptions: List[str] = [
      "Open Bing chat.",
      "Go to chat.",
      "Change Bing chat options.",
      "Open chat settings."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "start_copilot_from_searchbox_icon",
            path=[
                SingleClickAction(thought="Navigate to 'Copilot' icon near the search box to start Microsoft Copilot"),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "start_copilot_from_tab",
            path=[
                SingleClickAction(thought="Navigate to 'Copilot' tab option on the top bar to start Microsoft Copilot"),
                WaitAction(duration=1.0)
            ]
        )