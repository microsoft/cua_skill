from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, DoubleClickAction, PressKeyAction
from .common_action import LaunchApplication
from .argument import Argument


class ExcelBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="Excel",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Excel",
        description="The name of the Excel application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("ExcelLaunch")
class ExcelLaunch(ExcelBaseAction, LaunchApplication):
    type: str = "excel_launch"

    descriptions: List[str] = [
        "Open Excel.",
        "Launch the Excel app.",
        "Start Excel.",
        "Run the Excel application.",
        "Open the Excel program."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)

        self.add_path(
            "launch_excel",
            path=[
                LaunchApplication(application_name="Windows PowerShell"),
                WaitAction(duration=3.0),
                TypeAction(text="Start-Process excel", thought="Type the command 'Start-Process excel' to start Excel application."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to execute the command."),
                WaitAction(duration=3.0),
            ]
        )


@register("ExcelCreateNewWorkbook")
class ExcelCreateNewWorkbook(ExcelBaseAction):
    type: str = "excel_create_new_workbook"

    descriptions: List[str] = [
        "Open a new workbook in Excel.",
        "Create a new Excel workbook.",
        "Start a new workbook in the Excel application.",
        "Generate a new workbook in Excel."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_create_new_workbook",
            path = [
                SingleClickAction(thought="Click on 'Blank workbook' to create a new workbook."),
                WaitAction(duration=3.0)
            ]
        )


@register("ExcelOpenFile")
class ExcelOpenFile(ExcelBaseAction):
    type: str = "excel_open_file"

    file_path: Argument = Argument(
        value="",
        description="The full path to the existing Excel workbook to be opened."
    )

    descriptions: List[str] = [
        "Open an existing workbook located at ${{file_path}} in Excel.",
        "Load the Excel workbook from the specified file path.",
        "Access the existing Excel file at the given location.",
        "Open the workbook stored at ${{file_path}} in the Excel application."
    ]

    def __init__(self, file_path="", **kwargs) -> None:
        super().__init__(file_path=file_path, **kwargs)
        self.add_path(
            "open_existing_workbook",
            path = [
                LaunchApplication(application_name="Windows PowerShell"),
                WaitAction(duration=3.0),
                TypeAction(text=f"Start-Process excel {self.file_path}", thought=f"Input the command to start Excel with the file {self.file_path}."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to open the specified workbook."),
                WaitAction(duration=3.0),
            ]
        )


@register("ExcelSave")
class ExcelSave(ExcelBaseAction):
    type: str = "excel_save"
    filename: Argument = Argument(
        value=None,
        description="Path or name of the workbook file to save."
    )

    descriptions: List[str] = [
        "Save the current Excel workbook.",
        "Save the current file.",
        "Save the Excel file.",
        "Save the workbook as ${{filename}}.",
        "Save the file as ${{filename}}.",
        "Save the .xlsx file as ${{filename}}.",
        "Save the workbook with name ${{filename}}."
    ]

    def __init__(self, filename: str = None, **kwargs) -> None:
        super().__init__(filename=filename, **kwargs)
        self.add_path(
            "hotkey_save_file",
            path = [
                HotKeyAction(keys=["ctrl", "s"], thought="Press Ctrl + S to open the Save dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=filename if filename is not None else "My Workbook.xlsx", input_mode="copy_paste", thought=f"Type the file name '{filename}' to save."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelSaveAs")
class ExcelSaveAs(ExcelBaseAction):
    type: str = "excel_save_as"
    filename: Argument = Argument(
        value=None,
        description="Name of the workbook file. It must include the file extension, e.g., .xlsx, .csv, .pdf ..."
    )

    descriptions: List[str] = [
        "Save the workbook as ${{filename}}.",
        "Save the file as ${{filename}}.",
        "Save the Excel file as ${{filename}}.",
        "Save the .xlsx file as ${{filename}}.",
        "Save the workbook with name ${{filename}}."
    ]

    def __init__(self, filename: str = None, **kwargs) -> None:
        super().__init__(filename=filename, **kwargs)
        if filename is None:
            return
        if filename.endswith(".xlsx") or "." not in filename:
            self.add_path(
                "hotkey_save_as_file",
                path=[
                    HotKeyAction(keys=["f12"], thought="Press F12 to open the Save As dialog."),
                    WaitAction(duration=1.0),
                    TypeAction(text=filename if filename is not None else "My Workbook.xlsx", input_mode="copy_paste", thought=f"Type the file name '{filename}' to save."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                    WaitAction(duration=3.0)
                ]
            )
        else:
            self.add_path(
                "hotkey_save_as_file",
                path=[
                    HotKeyAction(keys=["f12"], thought="Press F12 to open the Save As dialog."),
                    WaitAction(duration=1.0),
                    TypeAction(text=filename if filename is not None else "My Workbook.xlsx", input_mode="copy_paste", thought=f"Type the file name '{filename}' to save."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought="Click the box right to Save as Type to open the dropdown menu to select the file type."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the right file type option to select the desired file type according to the file extension '{filename.split('.')[-1]}'."),
                    HotKeyAction(keys=["enter"], thought="Press Enter to confirm and save the file."),
                    WaitAction(duration=3.0)
                ]
            )


@register("ExcelRenameSheet")
class ExcelRenameSheet(ExcelBaseAction):
    type: str = "excel_rename_sheet"

    target_sheet_name: Argument = Argument(
        value="Sheet1",
        description="The current name of the sheet to be renamed."
    )
    new_sheet_name: Argument = Argument(
        value="Renamed Sheet1",
        description="The new name for the current sheet."
    )

    descriptions: List[str] = [
        "Rename the current sheet to a ${{new_sheet_name}}.",
        "Update the current sheet name to the given title ${{new_sheet_name}}.",
        "Modify the name of the current sheet to ${{new_sheet_name}}.",
        "Rename the sheet ${{target_sheet_name}} to ${{new_sheet_name}}.",
        "Update the sheet name ${{target_sheet_name}} to the given title ${{new_sheet_name}}.",
        "Modify the name of the sheet ${{target_sheet_name}} to ${{new_sheet_name}}."
    ]

    def __init__(self, target_sheet_name="Sheet1", new_sheet_name="Renamed Sheet1", **kwargs) -> None:
        super().__init__(target_sheet_name=target_sheet_name, new_sheet_name=new_sheet_name, **kwargs)

        if target_sheet_name:
            # Need to first focus on the target sheet tab
            focus_tab_path = [
                HotKeyAction(keys=["ctrl", "g"], thought="Press 'Ctrl + G' to open the 'Go To' dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=target_sheet_name + "!A1", thought=f"Type the target sheet name '{target_sheet_name}' to focus on the sheet tab."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to navigate to the target sheet."),
                WaitAction(duration=1.0)
            ]
        else:
            focus_tab_path = []

        self.add_path(
            "hotkey_rename_sheet",
            path = focus_tab_path + [
                HotKeyAction(keys=["alt", "h"], thought=f"Press 'Alt + H' to open the Home tab."),
                WaitAction(duration=1.0),
                PressKeyAction(key="o", thought=f"Press 'O' to open the Format menu."),
                WaitAction(duration=1.0),
                PressKeyAction(key="r", thought=f"Press 'R' to select the Rename Sheet option."),
                WaitAction(duration=1.0),
                TypeAction(text=new_sheet_name, thought=f"Type the new sheet name '{self.new_sheet_name}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to confirm the new sheet name."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelCreateNewSheet")
class ExcelCreateNewSheet(ExcelBaseAction):
    type: str = "excel_create_new_sheet"
    sheet_name: Argument = Argument(
        value=None,
        description="The name of the new sheet to be created."
    )
    
    descriptions: List[str] = [
        "Create a new sheet in the current Excel workbook.",
        "Add a new sheet to the workbook.",
        "Insert a new sheet into the Excel workbook.",
        "Create a new sheet in the current Excel workbook named ${{sheet_name}}.",
        "Add a new sheet to the workbook with the specified name ${{sheet_name}}.",
        "Insert a new sheet into the Excel workbook and name it ${{sheet_name}}.",
    ]

    def __init__(self, sheet_name=None, **kwargs) -> None:
        super().__init__(sheet_name=sheet_name, **kwargs)
        
        if sheet_name:
            self.add_path(
                "hotkey_create_new_sheet_and_rename",
                path = [
                    HotKeyAction(keys=["shift", "f11"], thought="Press 'Shift + F11' to create a new sheet in the workbook."),
                    WaitAction(duration=1.0),
                    
                    # Then rename the newly created sheet
                    HotKeyAction(keys=["alt", "h"], thought=f"Press 'Alt + H' to open the Home tab."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="o", thought=f"Press 'O' to open the Format menu."),
                    WaitAction(duration=1.0),
                    PressKeyAction(key="r", thought=f"Press 'R' to select the Rename Sheet option."),
                    WaitAction(duration=1.0),
                    TypeAction(text=sheet_name, thought=f"Type the new sheet name '{self.sheet_name}'."),
                    WaitAction(duration=1.0),
                    HotKeyAction(keys=["enter"], thought="Press 'Enter' to confirm the new sheet name."),
                    WaitAction(duration=1.0)
                ]
            )
        else:
            self.add_path(
                "hotkey_create_new_sheet",
                path = [
                    HotKeyAction(keys=["shift", "f11"], thought="Press 'Shift + F11' to create a new sheet in the workbook."),
                    WaitAction(duration=1.0)
                ]
            )


@register("ExcelGoToSheet")
class ExcelGoToSheet(ExcelBaseAction):
    type: str = "excel_go_to_sheet"
    target_sheet_name: Argument = Argument(
        value=None,
        description="The name of the sheet to navigate to."
    )

    descriptions: List[str] = [
        "Navigate to the sheet named ${{target_sheet_name}} in Excel.",
        "Go to the sheet ${{target_sheet_name}} in the current workbook.",
        "Select the sheet ${{target_sheet_name}} according to the provided name.",
        "Switch to the sheet named ${{target_sheet_name}} in the Excel workbook."
    ]

    def __init__(self, target_sheet_name=None, **kwargs) -> None:
        super().__init__(target_sheet_name=target_sheet_name, **kwargs)
        if target_sheet_name:
            self.add_path(
            "hotkey_go_to_sheet",
            path = [
                HotKeyAction(keys=["ctrl", "g"], thought="Press 'Ctrl + G' to open the 'Go To' dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=target_sheet_name + "!A1", thought=f"Type the target sheet name '{target_sheet_name}' to navigate to the sheet."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to navigate to the target sheet."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelDeleteSheet")
class ExcelDeleteSheet(ExcelBaseAction):
    type: str = "excel_delete_sheet"
    target_sheet_name: Argument = Argument(
        value=None,
        description="The name of the sheet to be deleted."
    )

    descriptions: List[str] = [
        "Delete the current sheet in Excel.",
        "Remove the current sheet from the workbook.",
        "Delete the active sheet in the Excel workbook.",
        "Delete the sheet named ${{target_sheet_name}} in Excel.",
        "Remove the sheet ${{target_sheet_name}} from the current workbook.",
        "Delete the sheet named ${{target_sheet_name}} in the Excel workbook."
    ]

    def __init__(self, target_sheet_name=None, **kwargs) -> None:
        super().__init__(target_sheet_name=target_sheet_name, **kwargs)
        
        if target_sheet_name:
            focus_tab_path = [
                HotKeyAction(keys=["ctrl", "g"], thought="Press 'Ctrl + G' to open the 'Go To' dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=target_sheet_name + "!A1", thought=f"Type the target sheet name '{target_sheet_name}' to focus on the sheet tab."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to navigate to the target sheet."),
                WaitAction(duration=1.0)
            ]
        else:
            focus_tab_path = []

        self.add_path(
            "hotkey_delete_sheet",
            path = focus_tab_path + [
                WaitAction(duration=1.0),
                HotKeyAction(keys=["alt", "h"], thought=f"Press 'Alt + H' to open the Home tab."),
                WaitAction(duration=1.0),
                PressKeyAction(key="d", thought=f"Press 'D' to open the Delete menu."),
                WaitAction(duration=1.0),
                PressKeyAction(key="s", thought=f"Press 'S' to select the Delete Sheet option."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelSelectCells")
class ExcelSelectCells(ExcelBaseAction):
    type: str = "excel_select_cells"
    target_cells: Argument = Argument(
        value=None,
        description="The cell or range of cells to navigate to."
    )

    descriptions: List[str] = [
        "Navigate to cell ${{target_cells}} in the current sheet.",
        "Go to the specified cell ${{target_cells}} in the current worksheet.",
        "Select the active cell ${{target_cells}} in the current sheet according to the provided location.",
        "Move to cell ${{target_cells}} in the current worksheet."
    ]

    def __init__(self, target_cells=None, **kwargs) -> None:
        super().__init__(target_cells=target_cells, **kwargs)
        if target_cells:
            self.add_path(
            "hotkey_go_to_cell",
            path = [
                HotKeyAction(keys=["ctrl", "g"], thought="Press 'Ctrl + G' to open the 'Go To' dialog."),
                WaitAction(duration=1.0),
                TypeAction(text=target_cells, thought=f"Type the target cells '{target_cells}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to navigate to the target cells."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelSetCellValue")
class ExcelSetCellValue(ExcelBaseAction):
    type: str = "excel_set_cell_value"
    target_cell: Argument = Argument(
        value="A1",
        description="The cell where the value will be set."
    )
    value: Argument = Argument(
        value="100",
        description="The value to be set in the specified cell."
    )

    descriptions: List[str] = [
        "Set the value of cell ${{target_cell}} to ${{value}}.",
        "Update the specified cell ${{target_cell}} with the given value ${{value}} in Excel.",
        "Change the content of cell ${{target_cell}} to ${{value}} in the current worksheet.",
        "Enter the value ${{value}} into cell ${{target_cell}} in Excel."
    ]

    def __init__(self, target_cell="A1", value="100", **kwargs) -> None:
        super().__init__(target_cell=target_cell, value=value, **kwargs)
        self.add_path(
            "set_cell_value",
            path = [
                ExcelSelectCells(target_cells=self.target_cell),
                WaitAction(duration=1.0),
                TypeAction(text=value, thought=f"Type the cell value '{value}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to confirm the cell value."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelSetCellFormula")
class ExcelSetCellFormula(ExcelBaseAction):
    type: str = "excel_set_cell_formula"
    formula: Argument = Argument(
        value="=SUM(A2:A9)",
        description="The full Excel formula to insert, starting with '=', followed by the function name and its arguments (including any cell ranges), for example: '=SUM(A2:A9)'."
    )
    target_cell: Argument = Argument(
        value=None,
        description="The cell where the function will be inserted. For example: A1"
    )

    descriptions: List[str] = [
        "Insert the formula ${{formula}} into cell ${{target_cell}}.",
        "Add the specified formula ${{formula}} to the given cell ${{target_cell}} in Excel.",
        "Type the formula ${{formula}} into cell ${{target_cell}} in the current worksheet.",
        "Enter the formula ${{formula}} at cell ${{target_cell}} in Excel."
    ]

    def __init__(self, formula=None, target_cell=None, **kwargs) -> None:
        super().__init__(formula=formula, target_cell=target_cell, **kwargs)
        
        self.add_path(
            "insert_formula",
            path = [
                ExcelSelectCells(target_cells=target_cell),
                WaitAction(duration=1.0),
                TypeAction(text=formula, thought=f"Type the formula '{formula}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to confirm the formula."),
            ]
        )


@register("ExcelSelectRows")
class ExcelSelectRows(ExcelBaseAction):
    type: str = "excel_select_rows"
    target_rows: Argument = Argument(
        value="1",
        description="The row numbers to be selected, separated by semicolons, e.g., '1;3;5'."
    )

    descriptions: List[str] = [
        "Select row number ${{target_rows}} in the current worksheet.",
        "Focus on the specified row ${{target_rows}} in the current worksheet.",
        "Highlight the specified row ${{target_rows}} in the current sheet.",
        "Navigate to row number ${{target_rows}} in the current workbook.",
    ]

    def parse_rows(self, target_rows: str) -> List[int]:
        """
        Expect target_rows: 1;3;5 -> [1,3,5]
        """
        if not target_rows:
            return []
        rows = []
        for part in target_rows.split(";"):
            rows.append(int(part))
        return rows

    def __init__(self, target_rows="1", **kwargs) -> None:
        super().__init__(target_rows=target_rows, **kwargs)
        self.target_rows.value = self.parse_rows(self.target_rows.value)

        self.add_path(
            "select_rows",
            path = [
                HotKeyAction(keys=["ctrl", "g"], thought="Press 'Ctrl+G' to open the 'Go To' dialog."),
                WaitAction(duration=1.0),
                TypeAction(
                    text=",".join([f"{row}:{row}" for row in self.target_rows.value]),
                    thought=f"Type the target row number '{self.target_rows.value}'.",
                ),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to go to the specified row."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelSelectColumns")
class ExcelSelectColumns(ExcelBaseAction):
    type: str = "excel_select_columns"
    target_columns: Argument = Argument(
        value="A",
        description="The column letters to be selected, separated by semicolons, e.g., 'A;C;E'."
    )

    descriptions: List[str] = [
        "Select column ${{target_columns}} in the current worksheet.",
        "Focus on the specified column ${{target_columns}} in the current worksheet.",
        "Highlight the specified column ${{target_columns}} in the current sheet.",
        "Navigate to column ${{target_columns}} in the current workbook.",
    ]

    def parse_columns(self, target_columns: str) -> List[str]:
        """
        Expect target_columns: A;C;E -> [A,C,E]
        """
        if not target_columns:
            return []
        columns = []
        for part in target_columns.split(";"):
            columns.append(part.strip().upper())
        return columns

    def __init__(self, target_columns="A", **kwargs) -> None:
        super().__init__(target_columns=target_columns, **kwargs)
        self.target_columns.value = self.parse_columns(self.target_columns.value)

        self.add_path(
            "select_columns",
            path = [
                HotKeyAction(keys=["ctrl", "g"], thought="Press 'Ctrl+G' to open the 'Go To' dialog."),
                WaitAction(duration=1.0),
                TypeAction(
                    text=",".join([f"{col}:{col}" for col in self.target_columns.value]),
                    thought=f"Type the target column letters '{self.target_columns.value}'.",
                ),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to go to the specified column."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelAutoFillDown")
class ExcelAutoFillDown(ExcelBaseAction):
    type: str = "excel_auto_fill_down"
    start_cell: Argument = Argument(
        value="A1",
        description="The starting cell for the auto-fill operation."
    )
    end_cell: Argument = Argument(
        value="A10",
        description="The ending cell for the auto-fill operation."
    )

    descriptions: List[str] = [
        "Auto-fill from the ${{start_cell}} to ${{end_cell}} using the value or formula from the starting cell.",
        "Populate the column with values or formulas from the ${{start_cell}} down to the ${{end_cell}}.",
    ]

    def __init__(self, start_cell="A1", end_cell="A10", **kwargs) -> None:
        super().__init__(start_cell=start_cell, end_cell=end_cell, **kwargs)
        self.add_path(
            "auto_fill_down",
            path = [
                ExcelSelectCells(target_cells=f"{start_cell}:{end_cell}"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "d"], thought="Press 'Ctrl + D' to auto-fill the column with the function.")
            ]
        )


@register("ExcelAutoFillRight")
class ExcelAutoFillRight(ExcelBaseAction):
    type: str = "excel_auto_fill_right"
    start_cell: Argument = Argument(
        value="A1",
        description="The starting cell for the auto-fill operation."
    )
    end_cell: Argument = Argument(
        value="J1",
        description="The ending cell for the auto-fill operation."
    )

    descriptions: List[str] = [
        "Auto-fill from the ${{start_cell}} to ${{end_cell}} to the right using the value or formula from the starting cell.",
        "Populate the row with values or formulas from the ${{start_cell}} to the ${{end_cell}} to the right.",
    ]

    def __init__(self, start_cell="A1", end_cell="J1", **kwargs) -> None:
        super().__init__(start_cell=start_cell, end_cell=end_cell, **kwargs)
        self.add_path(
            "auto_fill_right",
            path = [
                ExcelSelectCells(target_cells=f"{start_cell}:{end_cell}"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "r"], thought="Press 'Ctrl + R' to auto-fill the row with the function.")
            ]
        )


@register("ExcelAutoSum")
class ExcelAutoSum(ExcelBaseAction):
    type: str = "excel_auto_sum"
    target_cells: Argument = Argument(
        value=None,
        description="The range of cells to be summed."
    )
    result_cell: Argument = Argument(
        value=None,
        description="The cell where the AutoSum result will be placed."
    )

    descriptions: List[str] = [
        "AutoSum cells in the range ${{target_cells}} and place the result in ${{result_cell}}.",
        "Calculate the sum of the specified cells ${{target_cells}} using AutoSum and display the result in ${{result_cell}}.",
        "Use AutoSum to add up the values in ${{target_cells}} and put the result in ${{result_cell}}.",
        "Sum the values from ${{target_cells}} with AutoSum and show the result in ${{result_cell}}."
    ]
    
    def __init__(self, target_cells=None, result_cell=None, **kwargs) -> None:
        super().__init__(target_cells=target_cells, result_cell=result_cell, **kwargs)

        self.add_path(
            "auto_sum",
            path = [
                ExcelSelectCells(target_cells=result_cell),
                WaitAction(duration=1.0),
                TypeAction(text=f"=SUM({target_cells})", thought=f"Type the SUM formula for cells '{target_cells}'."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to confirm the SUM formula."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelFormatCellValue")
class ExcelFormatCellValue(ExcelBaseAction):
    type: str = "excel_format_cell_value"
    target_cells: Argument = Argument(
        value="A1:A10",
        description="The range of cells to be formatted."
    )
    format_type: Argument = Argument(
        value="Currency",
        description="The type of formatting to apply (e.g., Currency, Percentage, Date)."
    )

    descriptions: List[str] = [
        "Format the cells in the range ${{target_cells}} as ${{format_type}}.",
        "Apply ${{format_type}} formatting to the specified cell range ${{target_cells}} in Excel.",
        "Change the format of cells ${{target_cells}} to ${{format_type}} in the current worksheet.",
        "Set the cell format of the range ${{target_cells}} to ${{format_type}} in Excel."
    ]

    def __init__(self, target_cells="A1:A10", format_type="Currency", **kwargs) -> None:
        super().__init__(target_cells=target_cells, format_type=format_type, **kwargs)
        
        self.add_path(
            "format_cell_value",
            path = [
                ExcelSelectCells(target_cells=target_cells),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["ctrl", "1"], thought="Press 'Ctrl + 1' to open the Format Cells dialog."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on the '{format_type}' category in the dropdown menu of Category to select the desired format."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to apply the formatting and close the dialog."),
                WaitAction(duration=1.0)
            ]
        )


@register("ExcelDrawChartOverData")
class ExcelDrawChartOverData(ExcelBaseAction):
    type: str = "excel_draw_chart_over_data"

    chart_type: Argument = Argument(
        value="Bar",
        description="The type of chart to be created (e.g., Bar, Line, Pie)."
    )
    target_cells: Argument = Argument(
        value="A1:B10",
        description="The range of data to be used for the chart."
    )

    descriptions: List[str] = [
        "Create a ${{chart_type}} chart using data from the range ${{target_cells}}.",
        "Draw a ${{chart_type}} chart based on the specified data range ${{target_cells}} in Excel.",
        "Generate a ${{chart_type}} chart from the data in cells ${{target_cells}} in the current worksheet.",
        "Insert a ${{chart_type}} chart using the data from ${{target_cells}} in Excel."
    ]

    def __init__(self, chart_type="Bar", target_cells="A1:B10", **kwargs) -> None:
        super().__init__(chart_type=chart_type, target_cells=target_cells, **kwargs)
        
        self.add_path(
            "insert_chart_dialog",
            path = [
                ExcelSelectCells(target_cells=target_cells),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["alt", "n"], thought="Press 'Alt + N' to open the Insert tab."),
                WaitAction(duration=1.0),
                PressKeyAction(key="r", thought="Press 'R' to open Recommended Charts."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["right"], thought="Press 'Right Arrow' to switch to 'All Charts' tab."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on the '{chart_type}' chart type in the list to select it."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' to select the chart type."),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press 'Enter' again to insert the chart."),
                WaitAction(duration=3.0)
            ]
        )
