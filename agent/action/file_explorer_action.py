import os
from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import (
    register,
    SingleClickAction,
    DoubleClickAction,
    RightClickAction,
    WaitAction,
    TypeAction,
    HotKeyAction,
    ScrollAction,
)
from .common_action import OpenWindowsMenu
from .argument import Argument


# ======================================================================
# Utility functions
# ======================================================================

SPECIAL_TOKENS = {
    "ALL_SELECTED",
    "ALL_RESULTS",
    "ALL_ITEMS",
    "ALL_CLIPPED",
}

def is_special(value: str) -> bool:
    return value in SPECIAL_TOKENS


def normalize_path(path: str) -> str:
    if path is None:
        return None
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    try:
        return os.path.normpath(path)
    except Exception:
        return path


# ======================================================================
# Base class
# ======================================================================

class FileExplorerBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="file_explorer",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="File Explorer",
        description="The name of the File Explorer application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# ======================================================================
# FileExplorerLaunch
# ======================================================================

@register("FileExplorerLaunch")
class FileExplorerLaunch(FileExplorerBaseAction):
    type: str = "file_explorer_launch"

    descriptions: List[str] = [
        "Open File Explorer.",
        "Launch File Explorer.",
        "Start Windows Explorer.",
        "Run explorer.exe.",
        "Open the file manager."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "click_app_icon",
            path=[
                OpenWindowsMenu(),
                WaitAction(duration=0.1),
                TypeAction(text=self.application_name, thought=f"Type the application name '{self.application_name}' to search for it."),
                WaitAction(duration=0.1),
                SingleClickAction(thought=f"Click the first item under “Best match” in the Windows Search panel labeled “File Explorer (System)”. Do NOT use the taskbar icon."),
            ]
        )


# ======================================================================
# FileExplorerCloseWindow
# ======================================================================

@register("FileExplorerCloseWindow")
class FileExplorerCloseWindow(FileExplorerBaseAction):
    type: str = "file_explorer_close_window"

    descriptions: List[str] = [
        "Close the File Explorer window.",
        "Exit File Explorer.",
        "Shut the File Explorer window.",
        "Terminate File Explorer.",
        "Close current File Explorer.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "hotkey_close_window",
            path=[
                HotKeyAction(keys=["alt", "f4"], thought="Press Alt+F4 to close File Explorer."),
                WaitAction(duration=0.5)
            ],
        )

        self.add_path(
            "click_close_window",
            path=[
                SingleClickAction(thought="Click the 'X' button in File Explorer title bar."),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# FileExplorerOpenFolder
# ======================================================================

# @register("FileExplorerOpenFolder")
# class FileExplorerOpenFolder(FileExplorerBaseAction):
#     type: str = "file_explorer_open_folder"

#     folder_path: Argument = Argument(
#         value="C:\\Users",
#         description="Path of the folder to open."
#     )

#     descriptions: List[str] = [
#         "Open folder ${folder_path}.",
#         "Navigate to ${folder_path}.",
#         "Browse to ${folder_path}.",
#         "Go to folder ${folder_path}.",
#         "Access ${folder_path} in File Explorer.",
#     ]

#     def __init__(self, folder_path: str = "C:\\Users", **kwargs):
#         folder_path = normalize_path(folder_path)
#         super().__init__(folder_path=folder_path, **kwargs)

#         self.add_path(
#             "hotkey_open_folder",
#             path=[
#                 HotKeyAction(keys=["ctrl", "l"], thought="Focus the address bar."),
#                 WaitAction(duration=0.1),
#                 TypeAction(text=folder_path, thought=f"Type path '{folder_path}' to search for it."),
#                 WaitAction(duration=0.1),
#                 HotKeyAction(keys=["enter"], thought="Open folder."),
#                 WaitAction(duration=0.1),
#             ],
#         )


@register("FileExplorerOpenItemWithPath")
class FileExplorerOpenItemWithPath(FileExplorerBaseAction):
    type: str = "file_explorer_open_item_with_path"

    path: Argument = Argument(
        value="C:\\Users",
        description="Full path of the folder or the file to open."
    )

    descriptions: List[str] = [
        "Open the file or the folder with the given ${path}, only use it when the path is given and the item is not visible on the current screen.",
        "Go to the file or folder with the given ${path}, only use it when the path is given and the item is not visible on the current screen.",
    ]

    def __init__(self, path: str = "C:\\Users", **kwargs):
        path = normalize_path(path)
        super().__init__(path=path, **kwargs)

        self.add_path(
            "hotkey_open_item",
            path=[
                HotKeyAction(keys=["ctrl", "l"], thought="Focus the address bar."),
                WaitAction(duration=0.1),
                TypeAction(text=path, thought=f"Type path '{path}' to search for it.", end_with_enter=True),
                WaitAction(duration=0.1),
            ],
        )

@register("FileExplorerOpenItem")
class FileExplorerOpenItem(FileExplorerBaseAction):
    type: str = "file_explorer_open_item"

    target_item: Argument = Argument(
        value="example.txt",
        description="the name of the file or folder to open on the current screen"
    )

    descriptions: List[str] = [
        "Open the file or the folder on the current screen with its name ${target_item}. Use this action when the path is not given but the file or folder is visible on the current screen.",
        "Go to the file or folder with the given ${target_item}. Use this action when the path is not given but the file or folder is visible on the current screen.",
    ]

    def __init__(self, target_item: str = "example.txt", **kwargs):
        target_item = normalize_path(target_item)
        super().__init__(target_item=target_item, **kwargs)

        self.add_path(
            "click_open_item",
            path=[
                DoubleClickAction(thought=f"Select {target_item} on the current screen for double click to open it."),
                WaitAction(duration=0.1),
            ],
        )




# ======================================================================
# FileExplorerCopyItem
# ======================================================================

@register("FileExplorerCopyItem")
class FileExplorerCopyItem(FileExplorerBaseAction):
    type: str = "file_explorer_copy_item"

    source_file: Argument = Argument(
        value="example.txt",
        # allow_special_tokens=True,
        description="the item name visible on the current screen."
    )

    descriptions: List[str] = [
        "Copy file ${source_file}.",
        "Duplicate ${source_file} to clipboard.",
        "Copy selected item ${source_file}.",
        "Copy ${source_file} in File Explorer.",
        "Place ${source_file} into clipboard.",
    ]

    def __init__(self, source_file: str = "example.txt", **kwargs):
        super().__init__(source_file=source_file, **kwargs)

        self.add_path(
            "hotkey_copy",
            path=[
                SingleClickAction(thought=f"Click the item name {source_file} in the current file explorer window to select it."),
                WaitAction(duration=0.2),
                HotKeyAction(keys=["ctrl","c"], thought="Copy item."),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# FileExplorerCutItem
# ======================================================================

@register("FileExplorerCutItem")
class FileExplorerCutItem(FileExplorerBaseAction):
    type: str = "file_explorer_cut_item"

    source_file: Argument = Argument(
        value="example.txt",
        # allow_special_tokens=True,
        description="the item name visible on the current screen."
    )

    descriptions: List[str] = [
        "Cut file ${source_file}.",
        "Move ${source_file} to clipboard.",
        "Remove ${source_file} and prepare to paste.",
        "Cut selected item ${source_file}.",
        "Prepare ${source_file} to move elsewhere."
    ]

    def __init__(self, source_file: str = "example.txt", **kwargs):
        super().__init__(source_file=source_file, **kwargs)

        self.add_path(
            "hotkey_cut",
            path=[
                SingleClickAction(thought=f"Click the item name {source_file} in the current file explorer window to select it."),
                HotKeyAction(keys=["ctrl","x"], thought="Cut item."),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# FileExplorerPasteItem
# ======================================================================

@register("FileExplorerPasteHere")
class FileExplorerPasteHere(FileExplorerBaseAction):
    type: str = "file_explorer_paste_here"


    descriptions: List[str] = [
        "Paste item here. Assuming the item has already been copied or cut.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "paste_hotkey",
            path=[
                HotKeyAction(keys=["ctrl","v"], thought="Paste clipboard content."),
                WaitAction(duration=0.7),
            ],
        )


# ======================================================================
# Delete Item
# ======================================================================

@register("FileExplorerDeleteItem")
class FileExplorerDeleteItem(FileExplorerBaseAction):
    type: str = "file_explorer_delete_item"

    target_file: Argument = Argument(
        value="example.txt",
        description="Name of file to delete."
    )

    descriptions: List[str] = [
        "Delete file ${target_file}.",
        "Remove ${target_file}.",
        "Erase ${target_file}.",
        "Send ${target_file} to Recycle Bin.",
        "Clear ${target_file}.",
    ]

    def __init__(self, target_file="example.txt", **kwargs):
        super().__init__(target_file=target_file, **kwargs)

        self.add_path(
            "hotkey_delete",
            path=[
                SingleClickAction(thought=f"Select {target_file}."),
                WaitAction(duration=0.2),
                HotKeyAction(keys=["delete"], thought="Delete file."),
                WaitAction(duration=0.7),
            ],
        )


# ======================================================================
# Rename
# ======================================================================

@register("FileExplorerRenameItem")
class FileExplorerRenameItem(FileExplorerBaseAction):
    type: str = "file_explorer_rename_item"

    old_name: Argument = Argument(value="example.txt")
    new_name: Argument = Argument(value="renamed.txt")

    descriptions: List[str] = [
        "Rename ${old_name} to ${new_name}.",
        "Change name of ${old_name}.",
        "Update filename ${old_name} to ${new_name}.",
        "Edit file name from ${old_name}.",
    ]

    def __init__(self, old_name="example.txt", new_name="renamed.txt", **kwargs):
        super().__init__(old_name=old_name, new_name=new_name, **kwargs)

        self.add_path(
            "hotkey_rename",
            path=[
                SingleClickAction(thought=f"Select {old_name}."),
                WaitAction(duration=0.2),
                HotKeyAction(keys=["f2"], thought="Begin rename."),
                WaitAction(duration=0.2),
                TypeAction(text=new_name, thought="Type new name '{new_name}'."),
                WaitAction(duration=0.2),
                HotKeyAction(keys=["enter"], thought="Confirm rename."),
                WaitAction(duration=0.7),
            ],
        )


# ======================================================================
# Create New Folder
# ======================================================================

@register("FileExplorerCreateNewFolder")
class FileExplorerCreateNewFolder(FileExplorerBaseAction):
    type: str = "file_explorer_create_new_folder"

    folder_name: Argument = Argument(
        value="New Folder",
        description="Name of new folder."
    )

    descriptions: List[str] = [
        "Create new folder named ${folder_name} on the current File Explorer window.",
        "Make a directory ${folder_name} on the current File Explorer window.",
        "Add new folder ${folder_name} on the current File Explorer window.",
        "Generate folder ${folder_name} on the current File Explorer window.",
    ]

    def __init__(self, folder_name="New Folder", **kwargs):
        super().__init__(folder_name=folder_name, **kwargs)

        self.add_path(
            "hotkey_create",
            path=[
                HotKeyAction(keys=["ctrl","shift","n"], thought="Create new folder."),
                WaitAction(duration=0.3),
                TypeAction(text=folder_name, input_mode="keyboard", thought="Set folder name.", end_with_enter=True),
                WaitAction(duration=0.2),
            ],
        )


# ======================================================================
# Open File
# ======================================================================

# @register("FileExplorerOpenFile")
# class FileExplorerOpenFile(FileExplorerBaseAction):
#     type: str = "file_explorer_open_file"

#     filename: Argument = Argument(
#         value="example.txt",
#         description="File to open."
#     )

#     descriptions: List[str] = [
#         "Open file ${filename}.",
#         "Double click ${filename}.",
#         "Load document ${filename}.",
#         "View ${filename} in default program.",
#     ]

#     def __init__(self, filename="example.txt", **kwargs):
#         super().__init__(filename=filename, **kwargs)

#         self.add_path(
#             "double_click",
#             path=[
#                 DoubleClickAction(thought=f"Double click {filename} to open."),
#                 WaitAction(duration=1.2),
#             ],
#         )


# ======================================================================
# Search Item
# ======================================================================

@register("FileExplorerSearchItem")
class FileExplorerSearchItem(FileExplorerBaseAction):
    type: str = "file_explorer_search_item"

    target_item: Argument = Argument(
        value="report",
        description="Name of item to search."
    )

    descriptions: List[str] = [
        "Search for ${target_item} in File Explorer.",
        "Find ${target_item}.",
        "Look up ${target_item} in current folder.",
        "Search files containing ${target_item}.",
    ]

    def __init__(self, target_item="report", **kwargs):
        super().__init__(target_item=target_item, **kwargs)

        self.add_path(
            "hotkey_search",
            path=[
                HotKeyAction(keys=["ctrl","f"], thought="Focus File Explorer search box."),
                WaitAction(duration=0.2),
                TypeAction(text=target_item, thought=f"Type search query '{target_item}'."),
                WaitAction(duration=0.2),
                HotKeyAction(keys=["enter"], thought="Run search."),
                WaitAction(duration=1.2),
            ],
        )


@register("FileExplorerSearchRemove")
class FileExplorerSearchRemove(FileExplorerBaseAction):
    type: str = "file_explorer_search_remove"

    descriptions: List[str] = [
        "Clear the search box and return to the full folder view.",
        "Remove search query and reset search results.",
        "Clear File Explorer search.",
        "Exit search mode and show all items."
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "hotkey_search",
            path=[
                HotKeyAction(
                    keys=["ctrl", "f"],
                    thought="Focus the File Explorer search box."
                ),
                WaitAction(duration=0.2),
                HotKeyAction(
                    keys=["ctrl", "a"],
                    thought="Select all text in search box."
                ),
                WaitAction(duration=0.1),
                HotKeyAction(
                    keys=["backspace"],
                    thought="Clear the search box."
                ),
                WaitAction(duration=0.1),
                HotKeyAction(
                    keys=["enter"],
                    thought="Reset search results and return to full folder contents."
                ),
                WaitAction(duration=1.0),
            ],
        )



# ======================================================================
# Select All
# ======================================================================

@register("FileExplorerSelectAll")
class FileExplorerSelectAll(FileExplorerBaseAction):
    type: str = "file_explorer_select_all"

    descriptions: List[str] = [
        "Select all items in the folder.",
        "Highlight every file and folder.",
        "Select all contents of the directory.",
        "Choose all items.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "hotkey_select_all",
            path=[
                SingleClickAction(thought="Click the first item in the list."),
                WaitAction(duration=0.2),
                HotKeyAction(keys=["ctrl","a"], thought="Select all."),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# Toggle Hidden Items
# ======================================================================

@register("FileExplorerToggleHiddenItems")
class FileExplorerToggleHiddenItems(FileExplorerBaseAction):
    type: str = "file_explorer_toggle_hidden_items"

    descriptions: List[str] = [
        "Toggle hidden files in File Explorer.",
        "Show or hide hidden items.",
        "Display hidden files.",
        "Hide hidden files.",
        "Switch visibility of hidden items.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "toggle_hotkey",
            path=[
                SingleClickAction(thought="Click the 'View' button in the top toolbar of File Explorer."),
                WaitAction(duration=0.3),
                SingleClickAction(thought="Click the 'Show' option in the context menu of the 'View' button to open a submenu."),
                WaitAction(duration=0.3),
                SingleClickAction(thought="Click the 'Hidden Items' option in the submenu of 'Show'."),
                WaitAction(duration=0.5),
            ]
        )


# ======================================================================
# Change View
# ======================================================================

@register("FileExplorerChangeView")
class FileExplorerChangeView(FileExplorerBaseAction):
    type: str = "file_explorer_change_view"

    view_mode: Argument = Argument(
        value="Details",
        description="View mode."
    )

    descriptions: List[str] = [
        "Change view mode to ${view_mode}.",
        "Switch to ${view_mode} view.",
        "Update folder view to ${view_mode}.",
        "Change display mode to ${view_mode}.",
    ]

    def __init__(self, view_mode="Details", **kwargs):
        super().__init__(view_mode=view_mode, **kwargs)

        self.add_path(
            "click_change_view",
            path=[
                SingleClickAction(thought="Click 'View' button."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Choose '{view_mode}' mode."),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# Sort By
# ======================================================================

@register("FileExplorerSortBy")
class FileExplorerSortBy(FileExplorerBaseAction):
    type: str = "file_explorer_sort_by"

    sort_key: Argument = Argument(
        value="Name",
        description="Sort key."
    )

    descriptions: List[str] = [
        "Sort files by ${sort_key}.",
        "Arrange items based on ${sort_key}.",
        "Order folder contents by ${sort_key}.",
        "Sort current folder by ${sort_key}.",
    ]

    def __init__(self, sort_key="Name", **kwargs):
        super().__init__(sort_key=sort_key, **kwargs)

        if sort_key in ["Size", "Date created", "Categories", "Authors", "Tags", "Title"]:
            self.add_path(
                "click_sort_by_more",
                path=[
                    SingleClickAction(thought="Click 'Sort by' in the top toolbar of File Explorer to open the submenu."),
                    WaitAction(duration=0.3),
                    SingleClickAction(thought=f"Click 'More' option in the submenu of 'Sort by'."),
                    WaitAction(duration=0.3),
                    SingleClickAction(thought=f"Select '{sort_key}' in the submenu."),
                    WaitAction(duration=0.5),
            ]
            )
        else:
            self.add_path(
            "click_sort_by",
            path=[
                SingleClickAction(thought="Click 'Sort by' in the top toolbar of File Explorer."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Select '{sort_key}'."),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# Refresh View
# ======================================================================

@register("FileExplorerRefreshView")
class FileExplorerRefreshView(FileExplorerBaseAction):
    type: str = "file_explorer_refresh_view"

    descriptions: List[str] = [
        "Refresh the File Explorer view.",
        "Reload the current folder contents.",
        "Update the file list.",
        "Refresh this directory in File Explorer.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "refresh_hotkey",
            path=[
                HotKeyAction(keys=["f5"], thought="Press F5 to refresh."),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# Scroll
# ======================================================================

@register("FileExplorerScroll")
class FileExplorerScroll(FileExplorerBaseAction):
    type: str = "file_explorer_scroll"

    direction: Argument = Argument(value="down")
    amount: Argument = Argument(value=300)

    descriptions: List[str] = [
        "Scroll ${direction} in the file list.",
        "Scroll ${direction} through folder contents.",
        "Move the view ${direction} in File Explorer.",
        "Scroll the directory ${direction}.",
    ]

    def __init__(self, direction="down", amount=300, **kwargs):
        super().__init__(direction=direction, amount=amount, **kwargs)

        dy = amount

        self.add_path(
            "scroll",
            path=[
                SingleClickAction(thought="Click the first item in the file list to focus it."),
                WaitAction(duration=0.2),
                ScrollAction(direction=direction, dy=dy),
                WaitAction(duration=0.2),
            ],
        )


# ======================================================================
# Recycle Bin
# ======================================================================

@register("FileExplorerOpenRecycleBin")
class FileExplorerOpenRecycleBin(FileExplorerBaseAction):
    type: str = "file_explorer_open_recycle_bin"

    descriptions: List[str] = [
        "Open the Recycle Bin.",
        "Go to Recycle Bin.",
        "Access deleted items.",
        "Show Recycle Bin contents.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "address_bar_recycle_bin",
            path=[
                HotKeyAction(keys=["ctrl","l"]),
                WaitAction(duration=0.3),
                TypeAction(text="shell:RecycleBinFolder"),
                WaitAction(duration=0.3),
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0),
            ],
        )


@register("FileExplorerEmptyRecycleBin")
class FileExplorerEmptyRecycleBin(FileExplorerBaseAction):
    type: str = "file_explorer_empty_recycle_bin"

    descriptions: List[str] = [
        "Empty the Recycle Bin.",
        "Delete all items from Recycle Bin.",
        "Permanently clear Recycle Bin.",
        "Remove everything in Recycle Bin.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_path(
            "empty_recycle_bin",
            path=[
                
                HotKeyAction(keys=["ctrl","l"], thought="Focus the address bar."),
                WaitAction(duration=0.3),
                TypeAction(text="Recycle Bin", thought="Type the name Recycle Bin.", end_with_enter=True),
                WaitAction(duration=0.3),
                SingleClickAction(thought="In the top command bar of File Explorer, click the button labeled “Empty Recycle Bin”."
                                  "This button is located above the file list, next to “Restore all items”."
                                  "Do NOT click anything in the file list or the left navigation pane."),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["enter"], thought="Confirm empty."),
                WaitAction(duration=1.0),
            ],
        )


@register("FileExplorerRestoreItem")
class FileExplorerRestoreItem(FileExplorerBaseAction):
    type: str = "file_explorer_restore_item"

    target_item: Argument = Argument(
        value="example.txt",
        description="Item to restore."
    )

    descriptions: List[str] = [
        "Restore ${target_item} from Recycle Bin.",
        "Recover ${target_item}.",
        "Put back ${target_item}.",
        "Restore deleted item ${target_item}.",
    ]

    def __init__(self, target_item="example.txt", **kwargs):
        super().__init__(target_item=target_item, **kwargs)

        self.add_path(
            "restore_item",
            path=[
                HotKeyAction(keys=["ctrl","l"], thought="Focus the address bar."),
                WaitAction(duration=0.3),
                TypeAction(text="Recycle Bin", thought="Type the name Recycle Bin.", end_with_enter=True),
                WaitAction(duration=0.3),
                RightClickAction(thought=f"Right click {target_item}."),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click 'Restore'."),
                WaitAction(duration=1.0),
            ],
        )


# ======================================================================
# Create ZIP
# ======================================================================

@register("FileExplorerCreateZip")
class FileExplorerCreateZip(FileExplorerBaseAction):
    type: str = "file_explorer_create_zip"

    target_item: Argument = Argument(
        value="example.txt",
        description="Item to compress."
    )
    zip_name: Argument = Argument(
        value=None,
        description="Optional zip filename."
    )

    descriptions: List[str] = [
        "Compress ${target_item} into a zip file.",
        "Create zip archive from ${target_item}.",
        "Zip selected item ${target_item}.",
        "Make a compressed folder containing ${target_item}.",
    ]

    def __init__(self, target_item="example.txt", zip_name=None, **kwargs):
        super().__init__(target_item=target_item, zip_name=zip_name, **kwargs)

        self.add_path(
            "context_menu_zip",
            path=[
                SingleClickAction(thought=f"Click {target_item} to select."),
                WaitAction(duration=0.2),
                RightClickAction(thought=f"Right click {target_item}."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Click 'Compress to...' option in the context menu, which will open a submenu."),
                WaitAction(duration=0.5),
                SingleClickAction(thought=f"Click 'ZIP File' option in the compression type submenu of 'Compress to...' to select the ZIP file format."),
                WaitAction(duration=0.5),
                TypeAction(text=zip_name, input_mode="copy_paste", thought="Type new name for the compressed file."),
                WaitAction(duration=0.2),
                HotKeyAction(keys=["enter"], thought="Confirm the new name for the compressed file."),
                WaitAction(duration=0.7),
            ],
        )


# ======================================================================
# Extract All
# ======================================================================

@register("FileExplorerExtractAll")
class FileExplorerExtractAll(FileExplorerBaseAction):
    type: str = "file_explorer_extract_all"

    archive_name: Argument = Argument(
        value="example.zip",
        description="Archive to extract."
    )
    destination_folder: Argument = Argument(
        value=None,
        description="Destination folder for extraction."
    )

    descriptions: List[str] = [
        "Extract all from ${archive_name}.",
        "Unzip ${archive_name}.",
        "Decompress archive ${archive_name}.",
        "Extract files from ${archive_name}.",
    ]

    def __init__(self, archive_name="example.zip", destination_folder=None, **kwargs):
        destination_folder = normalize_path(destination_folder)
        super().__init__(
            archive_name=archive_name,
            destination_folder=destination_folder,
            **kwargs
        )

        self.add_path(
            "extract_all",
            path=[
                RightClickAction(thought=f"Right click on {archive_name} to open its context menu."
                                 "Right-click directly on its icon or name inside the file list pane."),
                WaitAction(duration=0.3),
                SingleClickAction(thought="In the context menu, click the option labeled 'Extract All...'"),
                WaitAction(duration=0.5),
                HotKeyAction(keys=["enter"], thought="Confirm extract location."),
                WaitAction(duration=1.5),
            ],
        )


# ======================================================================
# Tabs and Navigation
# ======================================================================

@register("FileExplorerNewTab")
class FileExplorerNewTab(FileExplorerBaseAction):
    type: str = "file_explorer_new_tab"

    descriptions: List[str] = [
        "Open a new tab in File Explorer.",
        "Create new File Explorer tab.",
        "Open another File Explorer tab.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "new_tab",
            path=[
                HotKeyAction(keys=["ctrl","t"]),
                WaitAction(duration=0.5),
            ],
        )


@register("FileExplorerCloseTab")
class FileExplorerCloseTab(FileExplorerBaseAction):
    type: str = "file_explorer_close_tab"

    descriptions: List[str] = [
        "Close the current tab in File Explorer.",
        "Exit active tab.",
        "Close one File Explorer tab.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "close_tab",
            path=[
                HotKeyAction(keys=["ctrl","w"]),
                WaitAction(duration=0.5),
            ],
        )


@register("FileExplorerSwitchTab")
class FileExplorerSwitchTab(FileExplorerBaseAction):
    type: str = "file_explorer_switch_tab"

    direction: Argument = Argument(value="next")

    descriptions: List[str] = [
        "Switch to ${direction} tab in File Explorer.",
        "Navigate to the ${direction} tab.",
        "Cycle through tabs.",
    ]

    def __init__(self, direction="next", **kwargs):
        super().__init__(direction=direction, **kwargs)

        keys = ["ctrl","tab"] if direction == "next" else ["ctrl","shift","tab"]

        self.add_path(
            "switch_tab",
            path=[
                HotKeyAction(keys=keys),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# Back / Forward / Up
# ======================================================================

@register("FileExplorerBack")
class FileExplorerBack(FileExplorerBaseAction):
    type: str = "file_explorer_back"

    descriptions: List[str] = [
        "Go back to previous folder.",
        "Navigate back.",
        "Return to last directory.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "back",
            path=[
                HotKeyAction(keys=["alt","left"]),
                WaitAction(duration=0.5),
            ],
        )


@register("FileExplorerForward")
class FileExplorerForward(FileExplorerBaseAction):
    type: str = "file_explorer_forward"

    descriptions: List[str] = [
        "Go forward to next folder.",
        "Navigate forward.",
        "Move to next directory.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "forward",
            path=[
                HotKeyAction(keys=["alt","right"]),
                WaitAction(duration=0.5),
            ],
        )


@register("FileExplorerUp")
class FileExplorerUp(FileExplorerBaseAction):
    type: str = "file_explorer_up"

    descriptions: List[str] = [
        "Go up one folder level.",
        "Navigate to parent directory.",
        "Move up to containing folder.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "up",
            path=[
                HotKeyAction(keys=["alt","up"]),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# New Window
# ======================================================================

@register("FileExplorerNewWindow")
class FileExplorerNewWindow(FileExplorerBaseAction):
    type: str = "file_explorer_new_window"

    descriptions: List[str] = [
        "Open a new File Explorer window.",
        "Launch another File Explorer instance.",
        "Create new Explorer window.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_path(
            "new_window",
            path=[
                HotKeyAction(keys=["ctrl","n"]),
                WaitAction(duration=0.5),
            ],
        )


# ======================================================================
# Properties
# ======================================================================

@register("FileExplorerOpenProperties")
class FileExplorerOpenProperties(FileExplorerBaseAction):
    type: str = "file_explorer_open_properties"

    target_item: Argument = Argument(
        value="example.txt",
        description="Item to view properties for."
    )

    descriptions: List[str] = [
        "Open properties for ${target_item}.",
        "View details of ${target_item}.",
        "Show properties window for ${target_item}.",
        "Access file properties.",
    ]

    def __init__(self, target_item="example.txt", **kwargs):
        super().__init__(target_item=target_item, **kwargs)

        self.add_path(
            "properties_hotkey",
            path=[
                SingleClickAction(thought=f"Click {target_item}."),
                WaitAction(duration=0.3),
                HotKeyAction(keys=["alt","enter"]),
                WaitAction(duration=1.0),
            ],
        )
