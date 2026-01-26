from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction, DoubleClickAction
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

def parse_to_datetime(date_str: str):
    from dateutil import parser
    if isinstance(date_str, Argument):
        date_str = date_str.value
    try:
        dt = parser.parse(date_str)
        return dt
    except Exception as e:
        raise ValueError(f"Unable to parse date string '{date_str}': {e}")


class CalculatorBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="calculator",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Calculator",
        description="The name of the Calculator application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("CalculatorLaunch")
class CalculatorLaunch(CalculatorBaseAction, LaunchApplication):
    # Canonical identifiers
    type: str = "calculator_launch"

    # Schema payload
    descriptions: List[str] = [
        "Open Calculator.",
        "Launch the Calculator app.",
        "Start Calculator.",
        "Run the Calculator application.",
        "Open the Calculator program."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)


@register("CalculatorOpenMenu")
class CalculatorOpenMenu(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_open_menu"

    # Schema payload
    descriptions: List[str] = [
        "Open the menu in Calculator.",
        "Access the menu in the Calculator app.",
        "Click on the menu icon in Calculator.",
        "Open the options menu in Calculator.",
        "Navigate to the menu in the Calculator application.",
        "Open the side menu.",
        "Show the Calculator navigation drawer.",
        "Open the hamburger menu.",
        "Expand the left navigation.",
        "Show the mode list."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "open_calculator_menu",
            path=[
                SingleClickAction(thought="Click the menu button (☰) in the Calculator app"),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorSwitchMode")
class CalculatorSwitchMode(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_switch_mode"
    mode_name: Argument = Argument(
        value="Standard", 
        description="The mode to switch the Calculator to, e.g., Standard, Scientific, Programmer, Date Calculation, Converter."
    )

    # Schema payload
    descriptions: List[str] = [
        "Switch mode to ${{mode_name}}.",
        "Change Calculator to ${{mode_name}} mode.",
        "Go to ${{mode_name}}.",
        "Select the ${{mode_name}} workspace.",
        "Open ${{mode_name}} view."
    ]

    def __init__(self, mode_name: str = "Standard", **kwargs) -> None:
        super().__init__(mode_name=mode_name, **kwargs)
        self.add_path(
            "switch_calculator_mode",
            path=[
                CalculatorOpenMenu(),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click on the '{self.mode_name}' option in the menu to switch to {self.mode_name} mode."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorEnterNumber")
class CalculatorEnterNumber(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_enter_number"
    number: Argument = Argument(
        value=None, 
        description="The number to enter into the Calculator, can be an integer or decimal."
    )

    # Schema payload
    descriptions: List[str] = [
        "Enter the number {number}.",
        "Input {number}.",
        "Type in {number}.",
        "Press the buttons for {number}.",
        "Key in {number}."
    ]

    def __init__(self, number: str = "0", **kwargs) -> None:
        super().__init__(number=number, **kwargs)
        self.add_path(
            "copy_paste_number",
            path=[
                TypeAction(text=number, input_mode="copy_paste", thought=f"Enter the number '{number}'.", end_with_enter=False),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorAdd")
class CalculatorAdd(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_add"

    # Schema payload
    descriptions: List[str] = [
        "Perform addition operation.",
        "Add numbers together.",
        "Calculate the sum.",
        "Use the plus function.",
        "Execute addition.",
        "Add two numbers.",
        "Calculate the total.",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_add",
            path=[
                HotKeyAction(keys=["shift", "="]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_add",
            path=[
                SingleClickAction(thought="Click the plus (+) button in the Calculator."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorSubtract")
class CalculatorSubtract(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_subtract"

    # Schema payload
    descriptions: List[str] = [
        "Press minus.",
        "Use the subtraction operator.",
        "Subtract the next value.",
        "Click −.",
        "Start a subtraction."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_subtract",
            path=[
                HotKeyAction(keys=["-"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_subtract",
            path=[
                SingleClickAction(thought="Click the minus (−) button in the Calculator."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorMultiply")
class CalculatorMultiply(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_multiply"

    # Schema payload
    descriptions: List[str] = [
        "Press multiply.",
        "Use the multiplication operator.",
        "Multiply the next value.",
        "Click ×.",
        "Start a multiplication."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_multiply",
            path=[
                HotKeyAction(keys=["shift", "8"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_multiply",
            path=[
                SingleClickAction(thought="Click the multiply (×) button in the Calculator."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorDivide")
class CalculatorDivide(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_divide"

    # Schema payload
    descriptions: List[str] = [
        "Press divide.",
        "Use the division operator.",
        "Divide by the next value.",
        "Click ÷.",
        "Start a division."
    ]


    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_divide",
            path=[
                HotKeyAction(keys=["/"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_divide",
            path=[
                SingleClickAction(thought="Click the divide (÷) button in the Calculator."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorEquals")
class CalculatorEquals(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_equals"

    # Schema payload
    descriptions: List[str] = [
        "Press equals.",
        "Calculate the result.",
        "Get the answer.",
        "Click =.",
        "Show the result."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_equals",
            path=[
                HotKeyAction(keys=["enter"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_equals",
            path=[
                SingleClickAction(thought="Click the equals (=) button in the Calculator. This is a blue button at the bottom right corner."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorClearEntry")
class CalculatorClearEntry(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_clear_entry"

    # Schema payload
    descriptions: List[str] = [
        "Clear the current entry.",
        "Press CE to clear entry.",
        "Erase the last input.",
        "Click the Clear Entry button.",
        "Reset the current number."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_clear_entry",
            path=[
                HotKeyAction(keys=["esc"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_clear_entry",
            path=[
                SingleClickAction(thought="Click the Clear Entry (CE) button in the Calculator."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorClearAll")
class CalculatorClearAll(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_clear_all"

    # Schema payload
    descriptions: List[str] = [
        "Clear all entries.",
        "Press C to clear all.",
        "Erase everything.",
        "Click the Clear button.",
        "Reset the calculator."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "hotkey_clear_all",
            path=[
                HotKeyAction(keys=["esc"]),
                WaitAction(duration=1.0)
            ]
        )
        self.add_path(
            "click_clear_all",
            path=[
                SingleClickAction(thought="Click the Clear (C) button in the Calculator."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorToggleSign")
class CalculatorToggleSign(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_toggle_sign"
    base_number: Argument = Argument(
        value=None,
        description="The number whose sign to toggle. If not provided, the current number in the Calculator will be used."
    )

    # Schema payload
    descriptions: List[str] = [
        "Toggle the sign of the current number.",
        "Change positive to negative or vice versa.",
        "Press the ± button.",
        "Switch the sign of the input.",
        "Make the number negative or positive.",
        "Toggle the sign of {base_number}."
        "Change {base_number} to its negative or positive form.",
        "Press the ± button for {base_number}.",
        "Switch the sign of the input number {base_number}.",
        "Make {base_number} negative or positive."
    ]

    def __init__(self, base_number: float = None, **kwargs) -> None:
        super().__init__(base_number=base_number, **kwargs)
        if self.base_number is None:
            self.add_path(
                "click_toggle_sign_without_base_number",
                path=[
                    SingleClickAction(thought="Click the ± button in the Calculator to change the sign."),
                    WaitAction(duration=1.0)
                ]
            )
        else:
            self.add_path(
                "click_toggle_sign_with_base_number",
                path=[
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the number '{self.base_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the ± button in the Calculator to change the sign of {self.base_number}."),
                    WaitAction(duration=1.0)
                ]
            )


@register("CalculatorReciprocal")
class CalculatorReciprocal(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_reciprocal"
    base_number: Argument = Argument(
        value=None,
        description="The number to calculate the reciprocal for. If not provided, the current number in the Calculator will be used."
    )

    # Schema payload
    descriptions: List[str] = [
        "Calculate the reciprocal (1/{base_number}).",
        "Compute 1 divided by the number {base_number}.",
        "Press 1/x.",
        "Find the inverse value of {base_number}.",
        "Get reciprocal of {base_number}."
    ]

    def __init__(self, base_number: float = None, **kwargs) -> None:
        super().__init__(base_number=base_number, **kwargs)
        if self.base_number is None:
            self.add_path(
                "click_reciprocal_without_base_number",
                path=[
                    SingleClickAction(thought="Click the '1/x' button in the Calculator to compute the reciprocal."),
                    WaitAction(duration=1.0)
                ]
            )
        else:
            self.add_path(
                "click_reciprocal_with_base_number",
                path=[
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the number '{self.base_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the '1/x' button in the Calculator to compute the reciprocal of {self.base_number}."),
                    WaitAction(duration=1.0)
                ]
            )


@register("CalculatorSquare")
class CalculatorSquare(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_square"
    base_number: Argument = Argument(
        value=None,
        description="The number to square. If not provided, the current number in the Calculator will be used."
    )

    # Schema payload
    descriptions: List[str] = [
        "Square the number of {base_number}.",
        "Compute {base_number} squared.",
        "Multiply {base_number} by itself.",
        "Compute {base_number}^2.",
        "Calculate the square of {base_number}."
    ]

    def __init__(self, base_number: float = None, **kwargs) -> None:
        super().__init__(base_number=base_number, **kwargs)
        if self.base_number is None:
            self.add_path(
                "click_square_root_without_base_number",
                path=[
                    SingleClickAction(thought="Click the 'x²' button in the Calculator to compute the square."),
                    WaitAction(duration=1.0)
                ]
            )
        else:
            self.add_path(
                "click_square_with_base_number",
                path=[
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the number '{self.base_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the 'x²' button in the Calculator to compute the square of {self.base_number}."),
                    WaitAction(duration=1.0)
                ]
            )


@register("CalculatorSquareRoot")
class CalculatorSquareRoot(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_square_root"
    base_number: Argument = Argument(
        value=None,
        description="The number to find the square root of. If not provided, the current number in the Calculator will be used."
    )

    # Schema payload
    descriptions: List[str] = [
        "Find the square root of {base_number}.",
        "Compute √{base_number}.",
        "Press root.",
        "Get square root value.",
        "Calculate √{base_number}."
    ]

    def __init__(self, base_number: float=None, **kwargs) -> None:
        super().__init__(base_number=base_number, **kwargs)
        if base_number is None:
            self.add_path(
                "click_square_root_without_base_number",
                path=[
                    SingleClickAction(thought="Click the '√' button in the Calculator to compute the square root."),
                    WaitAction(duration=1.0)
                ]
            )
        else:
            self.add_path(
                "click_square_root_with_base_number",
                path=[
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the number '{self.base_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the '√' button in the Calculator to compute the square root of {self.base_number}."),
                    WaitAction(duration=1.0)
                ]
            )


@register("CalculatorConstantPi")
class CalculatorConstantPi(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_constant_pi"

    # Schema payload
    descriptions: List[str] = [
        "Insert the constant π (pi).",
        "Use the pi symbol.",
        "Press π button.",
        "Get the value of pi.",
        "Calculate with pi."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_pi",
            path=[
                SingleClickAction(thought="Click the 'π' button in the Calculator to insert the constant π."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorConstantE")
class CalculatorConstantE(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_constant_e"

    # Schema payload
    descriptions: List[str] = [
        "Insert the constant e.",
        "Use the e symbol.",
        "Press e button.",
        "Get the value of e.",
        "Calculate with e."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_e",
            path=[
                SingleClickAction(thought="Click the 'e' button in the Calculator to insert the constant e."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorOpenParenthesis")
class CalculatorOpenParenthesis(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_open_parenthesis"
    _base_description: str = "("

    # Schema payload
    descriptions: List[str] = [
        "Press the open parenthesis button.",
        "Insert an opening parenthesis.",
        "Click ( button.",
        "Start a new group with (.",
        "Use ( to begin parentheses."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_paren_open",
            path=[
                SingleClickAction(thought="Click the '(' button in the Calculator app."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorCloseParenthesis")
class CalculatorCloseParenthesis(CalculatorBaseAction):
    # Canonical identifiers
    type: str = "calculator_close_parenthesis"
    _base_description: str = ")"

    # Schema payload
    descriptions: List[str] = [
        "Press the close parenthesis button.",
        "Insert a closing parenthesis.",
        "Click ) button.",
        "End a group with ).",
        "Use ) to close parentheses."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "click_paren_close",
            path=[
                SingleClickAction(thought="Click the ')' button in the Calculator app."),
                WaitAction(duration=1.0)
            ]
        )


@register("CalculatorTenPowerX")
class CalculatorTenPowerX(CalculatorBaseAction):
    type: str = "calculator_ten_power_x"
    base_number: Argument = Argument(
        value=None,
        description="The exponent for the calculation. If not provided, the current number in the Calculator will be used."
    )

    # Schema payload
    descriptions: List[str] = [
        "Calculate 10 to the power of {base_number}.",
        "Compute 10^{base_number}.",
        "Press 10^x.",
        "Get 10 raised to {base_number}.",
        "Calculate 10^{base_number}."
    ]

    def __init__(self, base_number: float=None, **kwargs) -> None:
        super().__init__(base_number=base_number, **kwargs)
        if base_number is None:
            self.add_path(
                "click_ten_power_without_base_number",
                path=[
                    SingleClickAction(thought="Click the '10^x' button in the Calculator to compute 10 to the power of a number."),
                    WaitAction(duration=1.0)
                ]
            )
        else:
            self.add_path(
                "click_ten_power_with_base_number",
                path=[
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the number '{self.base_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the '10^x' button in the Calculator to compute 10 to the power of {self.base_number}."),
                    WaitAction(duration=1.0)
                ]
            )

@register("CalculatorPowerXY")
class CalculatorPowerXY(CalculatorBaseAction):
    type: str = "calculator_power_x_y"
    base_number: Argument = Argument(
        value=None,
        description="The base number for the exponentiation."
    )
    power_number: Argument = Argument(
        value=None,
        description="The exponent for the calculation."
    )

    descriptions: List[str] = [
        "Raise {base_number} to the power {power_number}.",
        "Compute {base_number}^{power_number}.",
        "Calculate {base_number} power to {power_number}",
        "Set exponent {power_number} for {base_number}.",
        "Compute {base_number} to the {power_number}."
    ]

    def __init__(self, base_number: float=None, power_number: float=None, **kwargs):
        super().__init__(base_number=base_number, power_number=power_number, **kwargs)
        if self.base_number is not None and self.power_number is not None:
            self.add_path(
                "click_power_xy_with_base_power_number",
                path=[
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the base number '{self.base_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the 'x^y' button in the Calculator to compute {self.base_number} to the power of {self.power_number}."),
                    WaitAction(duration=1.0),
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the power number '{self.power_number}' into the Calculator."),
                    WaitAction(duration=1.0)
                ]
            )
        else:
            self.add_path(
                "click_power_xy_without_base_power_number",
                path = [
                    SingleClickAction(thought=f"Click the 'x^y' button in the Calculator to compute {self.base_number} to the power of {self.power_number}."),
                    WaitAction(duration=1.0)
                ]
            )


@register("CalculatorExp")
class CalculatorExp(CalculatorBaseAction):
    type: str = "calculator_exp"
    power_number: Argument = Argument(
        value=None,
        description="The exponent for the calculation."
    )
    coefficient_number: Argument = Argument(
        value=1.0,
        description="The coefficient for the exponential function."
    )
    base_number: Argument = Argument(
        value=None,
        description="The base number for the calculation."
    )

    descriptions: List[str] = [
        "Compute exp of {power_number}.",
        "Get e^{power_number}.",
        "Compute exp{power_number}.",
        "Calculate exponential of {power_number}.",
        "Compute {coefficient_number}e^{power_number}.",
        "Calculate {coefficient_number}e{power_number}",
        "Insert exponential function of {power_number}."
    ]

    def __init__(self, coefficient_number: float=None, power_number: float=None, base_number: float=None, **kwargs):
        super().__init__(coefficient_number=coefficient_number, power_number=power_number, base_number=base_number, **kwargs)
        if self.base_number is not None and self.power_number is not None:
            self.add_path(
                "click_exp_with_coefficient_power_number",
                path = [
                    CalculatorEnterNumber(number=self.coefficient_number, thought=f"Enter the coefficient number '{self.coefficient_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the 'exp' button in the Calculator to compute {self.coefficient_number}e{self.power_number}."),
                    WaitAction(duration=1.0),
                    CalculatorEnterNumber(number=self.power_number, thought=f"Enter the power number '{self.power_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                ]
            )
        elif self.power_number is not None:
            self.add_path(
                "click_exp_with_power_number",
                path = [
                    SingleClickAction(thought=f"Click the 'exp' button in the Calculator to compute exp({self.power_number})."),
                    WaitAction(duration=1.0),
                    CalculatorEnterNumber(number=self.power_number, thought=f"Enter the power number '{self.power_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                ]
            )
        else:
            self.add_path(
                "click_exp_without_coefficient_power_number",
                path = [
                    SingleClickAction(thought=f"Click the 'exp' button in the Calculator to compute exp({self.power_number})."),
                    WaitAction(duration=1.0)
                ]
            )

@register("CalculatorFactorial")
class CalculatorFactorial(CalculatorBaseAction):
    type: str = "calculator_factorial"
    base_number: Argument = Argument(
        value=None,
        description="The base number for the factorial calculation."
    )

    descriptions: List[str] = [
        "Compute factorial of {base_number}.",
        "Compute {base_number}!.",
        "Find {base_number} factorial.",
        "Press factorial button.",
        "Calculate {base_number}!."
    ]

    def __init__(self, base_number: float=None, **kwargs):
        super().__init__(base_number=base_number, **kwargs)
        if self.base_number is not None:
            self.add_path(
                "click_factorial_with_base_number",
                path = [
                    CalculatorEnterNumber(number=self.base_number, thought=f"Enter the base number '{self.base_number}' into the Calculator."),
                    WaitAction(duration=1.0),
                    SingleClickAction(thought=f"Click the Factorial '!' button in the Calculator to compute {self.base_number}!."),
                    WaitAction(duration=1.0),
                ]
            )
        else:
            self.add_path(
                "click_factorial_without_base_number",
                path = [
                    SingleClickAction(thought=f"Click the Factorial '!' button in the Calculator."),
                    WaitAction(duration=1.0),
                ]
            )


@register("CalculatorModulo")
class CalculatorModulo(CalculatorBaseAction):
    type: str = "calculator_modulo"
    """
    TODO
    """


@register("CalculatorAbs")
class CalculatorAbs(CalculatorBaseAction):
    type: str = "calculator_abs"
    """
    TODO
    """


@register("CalculatorLog10")
class CalculatorLog10(CalculatorBaseAction):
    type: str = "calculator_log10"
    """
    TODO
    """


@register("CalculatorLn")
class CalculatorLn(CalculatorBaseAction):
    type: str = "calculator_ln"
    """
    TODO
    """


"""
TODO
"""
@register("CalculatorSetFromUnit")
class ConverterSetFromUnit(CalculatorBaseAction):
    type: str = "converter_set_from_unit"
    unit: Argument = Argument(
        value=None,
        description="The from-unit to set in the converter."
    )

    descriptions: List[str] = [
        "Set from-unit to {unit}.",
        "Choose source unit {unit}.",
        "Pick input unit {unit}.",
        "Switch the up unit to {unit}.",
        "Select from-unit as {unit}."
    ]

    def __init__(self, unit: str=None, **kwargs):
        super().__init__(unit=unit, **kwargs)
        # self.add_path(
        #     "click_select_from_unit",
        #     path = [
        #     ]
        # )


@register("ConverterSetToUnit")
class ConverterSetToUnit(CalculatorBaseAction):
    type: str = "converter_set_to_unit"
    unit: Argument = Argument(
        value=None,
        description="The to-unit to set in the converter."
    )

    descriptions: List[str] = [
        "Set to-unit to {unit}.",
        "Choose target unit {unit}.",
        "Pick output unit {unit}.",
        "Switch the bottom unit to {unit}.",
        "Select to-unit as {unit}."
    ]

    def __init__(self, unit: str=None, **kwargs):
        super().__init__(unit=unit, **kwargs)
        # self.add_path(
        #     "click_select_to_unit",
        #     path = [
        #     ]
        # )


@register("ConverterSetToUnit")
class ConverterEnterAmount(CalculatorBaseAction):
    type: str = "converter_set_to_unit"
    unit: Argument = Argument(
        value=None,
        description="The to-unit to set in the converter."
    )

    descriptions: List[str] = [
        "Set to-unit to {unit}.",
        "Choose target unit {unit}.",
        "Pick output unit {unit}.",
        "Switch the bottom unit to {unit}.",
        "Select to-unit as {unit}."
    ]

    def __init__(self, unit: str=None, **kwargs):
        super().__init__(unit=unit, **kwargs)
        # self.add_path(
        #     "click_select_to_unit",
        #     path = [
        #     ]
        # )


@register("CalculatorSetYear")
class CalculatorSetYear(CalculatorBaseAction):
    type: str = "calculator_set_year"
    year: Argument = Argument(
        value=None,
        description="The year to set in the date difference calculator."
    )

    descriptions: List[str] = [
        "Set year to {year}.",
        "Choose year {year}.",
        "Pick the year as {year}.",
        "Input year {year}.",
        "Select year {year}."
    ]

    def __init__(self, year: str=None, **kwargs):
        super().__init__(year=year, **kwargs)
        self.add_path(
            "click_set_year",
            path = [
                SingleClickAction(thought=f"Click the month-year label on the 'Left Side' of the date picker header, Not the arrow buttons."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the month-year label on the 'Left Side' of the date picker header again, Not the arrow buttons."),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click the {self.year} on the year selection view to set the year to {self.year}."),
                WaitAction(duration=1.0),
            ]
        )


@register("CalculatorSetStartDate")
class CalculatorSetStartDate(CalculatorBaseAction):
    type: str = "calculator_set_start_date"
    start_date: Argument = Argument(
        value=None,
        description="The start date to set in the date difference calculator."
    )

    descriptions: List[str] = [
        "Set start date to {start_date}.",
        "Choose start date {start_date}.",
        "Pick the starting date as {start_date}.",
        "Input start date {start_date}.",
        "Select start date {start_date}."
    ]

    def __init__(self, start_date: str=None, **kwargs):
        super().__init__(start_date=start_date, **kwargs)
        if self.start_date.value:
            self.start_date = parse_to_datetime(self.start_date)
            self.add_path(
                "click_set_start_date",
                path = [
                    WaitAction(duration=5.0, thought="Waiting for the date difference calculator to load. It is observed to take longer than other modes."),
                    SingleClickAction(thought=f"Click the date field in the Calculator underneath 'From' to set start date."),
                    WaitAction(duration=1.0),
                    # Set year
                    CalculatorSetYear(year=self.start_date.year, thought=f"Set the year to {self.start_date.year}."),
                    WaitAction(duration=1.0),
                    # Set month
                    SingleClickAction(thought=f"Click the {self.start_date.month} cell in the month-selection grid."),
                    WaitAction(duration=1.0),
                    # Set day
                    SingleClickAction(thought=f"Click the {self.start_date.day} cell in the day-selection grid."),
                    WaitAction(duration=1.0),
                ]
            )


@register("CalculatorSetEndDate")
class CalculatorSetEndDate(CalculatorBaseAction):
    type: str = "calculator_set_end_date"
    end_date: Argument = Argument(
        value=None,
        description="The end date to set in the date difference calculator."
    )

    descriptions: List[str] = [
        "Set end date to {end_date}.",
        "Choose end date {end_date}.",
        "Pick the ending date as {end_date}.",
        "Input end date {end_date}.",
        "Select end date {end_date}."
    ]


    def __init__(self, end_date: str=None, **kwargs):
        super().__init__(end_date=end_date, **kwargs)
        if self.end_date.value:
            self.end_date = parse_to_datetime(self.end_date)
            self.add_path(
                "click_set_end_date",
                path = [
                    WaitAction(duration=5.0, thought="Waiting for the date difference calculator to load. It is observed to take longer than other modes."),
                    SingleClickAction(thought=f"Click the date field in the Calculator underneath 'To', Not 'From', to set end date."),
                    WaitAction(duration=1.0),
                    # Set year
                    CalculatorSetYear(year=self.end_date.year, thought=f"Set the year to {self.end_date.year}."),
                    WaitAction(duration=1.0),
                    # Set month
                    SingleClickAction(thought=f"Click the {self.end_date.month} cell in the month-selection grid."),
                    WaitAction(duration=1.0),
                    # Set day
                    SingleClickAction(thought=f"Click the {self.end_date.day} cell in the day-selection grid."),
                    WaitAction(duration=1.0),
                ]
            )


@register("CalculatorComputeDateDifference")
class CalculatorComputeDateDifference(CalculatorBaseAction):
    type: str = "calculator_compute_date_difference"
    start_date: Argument = Argument(
        value=None,
        description="The start date for the date difference calculation."
    )
    end_date: Argument = Argument(
        value=None,
        description="The end date for the date difference calculation."
    )

    descriptions: List[str] = [
        "Compute the difference between {start_date} and {end_date}.",
        "Calculate days between {start_date} and {end_date}.",
        "Find date difference from {start_date} to {end_date}.",
        "Get number of days between {start_date} and {end_date}.",
        "Calculate duration from {start_date} to {end_date}."
    ]

    def __init__(self, start_date: str=None, end_date: str=None, **kwargs):
        super().__init__(start_date=start_date, end_date=end_date, **kwargs)
        # self.add_path(
        #     "click_compute_date_difference",
        #     path = [
        #         SingleClickAction(thought=f"Click the 'Date Difference' option in the Calculator to compute the difference between {self.start_date} and {self.end_date}."),
        #     ]
        # )