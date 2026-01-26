from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import register, BaseAction, SingleClickAction, WaitAction, TypeAction, HotKeyAction 
from .common_action import LaunchApplication
from .argument import Argument

__all__ = []

class ClockBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="clock",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Clock",
        description="The name of the Clock application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@register("ClockOpenApp")
class ClockOpenApp(ClockBaseAction, LaunchApplication):
    # Canonical identifiers
    type: str = "clock_open_app"
    
    # Schema payload
    descriptions: List[str] = [
        "Open Clock.",
        "Launch the Clock app.",
        "Start Windows Clock.",
        "Run the Clock application.",
        "Open Alarms & Clock."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(application_name=self.application_name, **kwargs)


@register("ClockSwitchTab")
class ClockSwitchTab(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_switch_tab"
    tab: Argument = Argument(
        value="Alarms",
        description="Clock application tab/section to navigate to. Available tabs: 'Alarms' (manage alarm clocks), 'World Clock' (view times in different cities/time zones), 'Timer' (countdown timers), 'Stopwatch' (elapsed time measurement), 'Focus' (focus session/pomodoro timer). Use exact tab name with proper capitalization as shown in the Windows Clock app."
    )

    # Schema payload
    descriptions: List[str] = [
        "Switch to ${{tab}} tab.",
        "Go to the ${{tab}} section.",
        "Open the ${{tab}} view.",
        "Navigate to ${{tab}}.",
        "Change tab to ${{tab}}."
    ]

    def __init__(self, tab: str = "Alarms", **kwargs) -> None:
        super().__init__(tab=tab, **kwargs)
        self.add_path(
            "click_switch_tab",
            path=[
                SingleClickAction(thought=f"Click on the '{self.tab}' tab to switch view."),
                WaitAction(duration=1.0)
            ]
        )


@register("ClockCreateAlarm")
class ClockCreateAlarm(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_create_alarm"
    time: Argument = Argument(
        value="07:00",
        description="Alarm time in 24-hour format HH:MM or 12-hour format with AM/PM. For 24-hour: use 00:00 to 23:59 (e.g., '07:00' for 7 AM, '19:30' for 7:30 PM, '00:00' for midnight, '12:00' for noon). For 12-hour: append space and AM/PM (e.g., '07:00 AM', '07:30 PM', '12:00 PM' for noon, '12:00 AM' for midnight). Use two-digit format with leading zeros and colon separator. Common examples: '06:00' (6 AM wake-up), '22:00' (10 PM bedtime), '07:30 AM' (7:30 morning), '08:00 PM' (8 evening)."
    )
    label: Argument = Argument(
        value="Morning Alarm",
        description="Descriptive text label/name for the alarm to help identify its purpose. Can be any text string up to approximately 50 characters. Examples: 'Morning Alarm' (general wake-up), 'Work Start' (weekday work time), 'Medication Reminder' (daily medicine), 'Gym Time' (exercise schedule), 'School Bus' (children's schedule), 'Meeting Alert' (appointment reminder), 'Lunch Break' (midday break). Use clear, descriptive names that indicate the alarm's purpose."
    )
    repeat_days: Argument = Argument(
        value="Weekdays",
        description="Recurring schedule pattern for when the alarm should repeat. Must use one of these exact preset values: 'None' (one-time alarm, no repeat), 'Weekdays' (Monday through Friday, work/school days), 'Weekends' (Saturday and Sunday), 'Everyday' (all 7 days of the week, daily alarm), 'Mon,Wed,Fri' (Monday, Wednesday, Friday pattern), 'Tue,Thu' (Tuesday, Thursday pattern). Use exact string matching with proper capitalization and comma separators. Common use cases: 'Weekdays' for work alarms, 'Everyday' for medication reminders, 'Weekends' for leisure activities, 'None' for one-time appointments."
    )
    snooze_minutes: Argument = Argument(
        value="10",
        description="Snooze duration in minutes when the alarm is snoozed. Must be a positive integer representing minutes. Common snooze intervals: '5' (5 minutes, short snooze), '10' (10 minutes, standard snooze), '15' (15 minutes, longer snooze), '20' (20 minutes), '30' (30 minutes, half hour). Typical range: 1 to 60 minutes. The alarm will ring again after this many minutes when snoozed. Most users prefer 5-10 minutes."
    )
    enabled: Argument = Argument(
        value="true",
        description="Whether the alarm is active/enabled immediately after creation. Must be exactly 'true' or 'false' (lowercase string). 'true' = alarm is enabled and will ring at scheduled time, 'false' = alarm is created but disabled/inactive and will not ring until manually enabled. Use 'true' for alarms that should start working immediately, 'false' for alarms to be enabled later."
    )

    # Schema payload
    descriptions: List[str] = [
        "Create an alarm at ${{time}} labeled ${{label}} repeating ${{repeat_days}} with snooze ${{snooze_minutes}} minutes and enabled ${{enabled}}.",
        "Set alarm for ${{time}} labeled ${{label}} repeating ${{repeat_days}} with snooze ${{snooze_minutes}} minutes and enabled ${{enabled}}.",
        "Add alarm ${{label}} at ${{time}} repeating ${{repeat_days}} with snooze ${{snooze_minutes}} minutes and enabled ${{enabled}}.",
        "Create alarm at ${{time}} labeled ${{label}} with snooze ${{snooze_minutes}} minutes repeating ${{repeat_days}} and enabled ${{enabled}}.",
        "Set a new alarm for ${{time}} named ${{label}} repeating ${{repeat_days}} with snooze ${{snooze_minutes}} minutes and enabled ${{enabled}}."
    ]   

    def __init__(self, time: str = "07:00", label: str = "Morning Alarm", 
                 repeat_days: str = "Weekdays", snooze_minutes: str = "10", 
                 enabled: str = "true", **kwargs) -> None:
        super().__init__(time=time, label=label, repeat_days=repeat_days, 
                        snooze_minutes=snooze_minutes, enabled=enabled, **kwargs)
        # Parse time into hour, minute, meridiem (AM/PM)
        time_parts = str(self.time).strip().split()
        hm_part = time_parts[0]
        meridiem = time_parts[1].upper() if len(time_parts) > 1 else None

        hour_str, minute_str = hm_part.split(":")
        raw_hour = int(hour_str)

        if meridiem is None:
            meridiem = "p" if raw_hour >= 12 else "a"

        # Convert to 12-hour display if needed
        if raw_hour == 0:
            hour_display = "12"
        elif raw_hour > 12:
            hour_display = f"{raw_hour - 12:02d}"
        else:
            hour_display = f"{raw_hour:02d}"

        minute_display = f"{int(minute_str):02d}"

        # Decompose repeat_days into atomic day selection operations
        allowed_repeat_days = {
            "None",
            "Weekdays",
            "Weekends",
            "Everyday",
            "Mon,Wed,Fri",
            "Tue,Thu"
        }

        repeat_value = str(self.repeat_days).strip()
        if repeat_value not in allowed_repeat_days:
            repeat_value = "None"

        pattern_days = {
            "Weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "Weekends": ["Sat", "Sun"],
            "Everyday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Mon,Wed,Fri": ["Mon", "Wed", "Fri"],
            "Tue,Thu": ["Tue", "Thu"]
        }

        if repeat_value == "None":
            repeat_actions: List[BaseAction] = [
                WaitAction(duration=0.2)
            ]
        else:
            repeat_actions = [
            SingleClickAction(thought="Open repeat day selection."),
            WaitAction(duration=0.3)
            ]
            for day in pattern_days[repeat_value]:
                repeat_actions.append(SingleClickAction(thought=f"Select {day}."))
                repeat_actions.append(WaitAction(duration=0.2))

        self.add_path(
            "create_alarm",
            path=[
            SingleClickAction(thought="Click the add alarm button."),
            WaitAction(duration=1.0),

            SingleClickAction(thought="Focus the hour field."),
            TypeAction(thought=f"Enter hour '{hour_display}'.", text=hour_display),
            WaitAction(duration=0.4),

            SingleClickAction(thought="Focus the minute field."),
            TypeAction(thought=f"Enter minutes '{minute_display}'.", text=minute_display),
            WaitAction(duration=0.4),

            SingleClickAction(thought=f"Click the AM/PM (meridiem) selector field to enable changing between AM and PM."),
            TypeAction(thought=f"Set period to '{meridiem}'.", text=meridiem),
            WaitAction(duration=0.4),

            SingleClickAction(thought="Locate and click the alarm label input field (e.g., placeholder 'Label' or 'Alarm name')."),
            TypeAction(thought=f"Type label '{self.label}'.", text=self.label),
            WaitAction(duration=0.5),

            *repeat_actions,

            SingleClickAction(thought="Click Snooze Time dropdown inside the alarm editor (avoid bottom-left global settings)."),
            WaitAction(duration=0.3),
            SingleClickAction(thought=f"Set snooze to {self.snooze_minutes} minutes."),
            WaitAction(duration=0.5),

            SingleClickAction(thought="Save the alarm."),
            WaitAction(duration=1.0)
            ]
        )


@register("ClockEditAlarm")
class ClockEditAlarm(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_edit_alarm"
    alarm_identifier: Argument = Argument(
        value="Morning Alarm",
        description="Identifier to locate the existing alarm to edit. Can be either the alarm's label/name (e.g., 'Morning Alarm', 'Work Start') or its time in HH:MM format (e.g., '07:00', '19:30'). The identifier should uniquely identify the target alarm in the alarm list. If multiple alarms have the same label or time, the first matching alarm will be selected. Use the exact label text or time format as displayed in the alarm list."
    )
    new_time: Argument = Argument(
        value="07:30",
        description="New alarm time to set in 24-hour format HH:MM or 12-hour format with AM/PM. For 24-hour: use 00:00 to 23:59 (e.g., '07:30' for 7:30 AM, '19:00' for 7 PM). For 12-hour: append space and AM/PM (e.g., '07:30 AM', '08:00 PM'). Use two-digit format with leading zeros and colon separator. Examples: '06:30' (change to 6:30 AM), '20:00' (change to 8 PM), '08:30 AM' (8:30 morning)."
    )
    new_label: Argument = Argument(
        value="Updated Alarm",
        description="New descriptive text label/name for the alarm. Can be any text string up to approximately 50 characters. Examples: 'Updated Alarm' (generic update), 'Early Wake Up' (earlier time), 'Late Start' (later time), 'Weekend Alarm' (schedule change), 'New Schedule' (routine change). Use clear, descriptive names that reflect the alarm's updated purpose or schedule."
    )
    new_repeat_days: Argument = Argument(
        value="Everyday",
        description="New recurring schedule pattern for the alarm. Must use one of these exact preset values: 'None' (one-time alarm, disable repeat), 'Weekdays' (Monday through Friday), 'Weekends' (Saturday and Sunday), 'Everyday' (all 7 days, daily), 'Mon,Wed,Fri' (Monday, Wednesday, Friday), 'Tue,Thu' (Tuesday, Thursday). Use exact string with proper capitalization and comma separators. Common updates: 'Weekdays' to 'Everyday' for continuous schedule, 'None' to 'Weekdays' to make recurring."
    )
    new_snooze_minutes: Argument = Argument(
        value="15",
        description="New snooze duration in minutes. Must be a positive integer representing minutes. Common values: '5' (shorter snooze), '10' (standard), '15' (longer snooze), '20', '30'. Typical range: 1 to 60 minutes. Updates how long the alarm will wait before ringing again after being snoozed. Examples: change from '10' to '15' for more sleep time, or '10' to '5' for quicker wake-up."
    )
    enabled: Argument = Argument(
        value="true",
        description="Whether the alarm should be active/enabled after editing. Must be exactly 'true' or 'false' (lowercase string). 'true' = alarm remains or becomes enabled and will ring, 'false' = alarm becomes disabled and will not ring. Use 'true' to keep alarm active after changes, 'false' to temporarily disable after editing."
    )

    # Schema payload
    descriptions: List[str] = [
        "Edit alarm ${{alarm_identifier}} to time ${{new_time}} label ${{new_label}} repeat ${{new_repeat_days}} snooze ${{new_snooze_minutes}} minutes and enabled ${{enabled}}.",
        "Update alarm ${{alarm_identifier}} with time ${{new_time}} label ${{new_label}} repeat ${{new_repeat_days}} snooze ${{new_snooze_minutes}} minutes and enabled ${{enabled}}.",
        "Change alarm ${{alarm_identifier}} to ${{new_time}} labeled ${{new_label}} repeating ${{new_repeat_days}} with snooze ${{new_snooze_minutes}} minutes and enabled ${{enabled}}.",
        "Modify alarm ${{alarm_identifier}} setting time ${{new_time}} label ${{new_label}} repeat ${{new_repeat_days}} snooze ${{new_snooze_minutes}} minutes and enabled ${{enabled}}.",
        "Set alarm ${{alarm_identifier}} to ${{new_time}} named ${{new_label}} repeating ${{new_repeat_days}} with snooze ${{new_snooze_minutes}} minutes and enabled ${{enabled}}."
    ]

    def __init__(self, alarm_identifier: str = "Morning Alarm", new_time: str = "07:30",
                 new_label: str = "Updated Alarm", new_repeat_days: str = "Everyday",
                 new_snooze_minutes: str = "15", enabled: str = "true", **kwargs) -> None:
        super().__init__(alarm_identifier=alarm_identifier, new_time=new_time,
                        new_label=new_label, new_repeat_days=new_repeat_days,
                        new_snooze_minutes=new_snooze_minutes, enabled=enabled, **kwargs)
        
        # Parse time into hour, minute, meridiem (AM/PM)
        time_parts = str(self.new_time).strip().split()
        hm_part = time_parts[0]
        meridiem = time_parts[1].upper() if len(time_parts) > 1 else None

        hour_str, minute_str = hm_part.split(":")
        raw_hour = int(hour_str)

        if meridiem is None:
            meridiem = "p" if raw_hour >= 12 else "a"

        # Convert to 12-hour display if needed
        if raw_hour == 0:
            hour_display = "12"
        elif raw_hour > 12:
            hour_display = f"{raw_hour - 12:02d}"
        else:
            hour_display = f"{raw_hour:02d}"

        minute_display = f"{int(minute_str):02d}"

        # Decompose repeat_days into atomic day selection operations
        allowed_repeat_days = {
            "None",
            "Weekdays",
            "Weekends",
            "Everyday",
            "Mon,Wed,Fri",
            "Tue,Thu"
        }

        repeat_value = str(self.new_repeat_days).strip()
        if repeat_value not in allowed_repeat_days:
            repeat_value = "None"

        pattern_days = {
            "Weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "Weekends": ["Sat", "Sun"],
            "Everyday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Mon,Wed,Fri": ["Mon", "Wed", "Fri"],
            "Tue,Thu": ["Tue", "Thu"]
        }

        if repeat_value == "None":
            repeat_actions: List[BaseAction] = [
                WaitAction(duration=0.2)
            ]
        else:
            repeat_actions = [
                SingleClickAction(thought="Open repeat day selection."),
                WaitAction(duration=0.3)
            ]
            for day in pattern_days[repeat_value]:
                repeat_actions.append(SingleClickAction(thought=f"Select {day}."))
                repeat_actions.append(WaitAction(duration=0.2))
        
        self.add_path(
            "edit_alarm",
            path=[
                SingleClickAction(thought=f"Click on alarm '{self.alarm_identifier}' to edit."),
                WaitAction(duration=1.0),
                
                SingleClickAction(thought="Focus the hour field."),
                TypeAction(thought=f"Update hour to '{hour_display}'.", text=hour_display),
                WaitAction(duration=0.4),
                
                SingleClickAction(thought="Focus the minute field."),
                TypeAction(thought=f"Update minutes to '{minute_display}'.", text=minute_display),
                WaitAction(duration=0.4),
                
                SingleClickAction(thought=f"Click the AM/PM (meridiem) selector field to enable changing between AM and PM."),
                TypeAction(thought=f"Set period to '{meridiem}'.", text=meridiem),
                WaitAction(duration=0.4),
                
                SingleClickAction(thought="Locate and click the alarm label input field (e.g., placeholder 'Label' or 'Alarm name')."),
                TypeAction(thought=f"Update label to '{self.new_label}'.", text=self.new_label),
                WaitAction(duration=0.5),
                
                *repeat_actions,
                
                SingleClickAction(thought="Click Snooze Time dropdown inside the alarm editor (avoid bottom-left global settings)."),
                WaitAction(duration=0.3),
                SingleClickAction(thought=f"Set snooze to {self.new_snooze_minutes} minutes."),
                WaitAction(duration=0.5),
                
                SingleClickAction(thought="Save changes."),
                WaitAction(duration=1.0)
            ]
        )


@register("ClockToggleAlarm")
class ClockToggleAlarm(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_toggle_alarm"
    alarm_identifier: Argument = Argument(
        value="Morning Alarm",
        description="Identifier to locate the alarm to enable/disable. Can be either the alarm's label/name (e.g., 'Morning Alarm', 'Work Reminder') or its time in HH:MM format (e.g., '07:00', '19:30'). Should uniquely identify the target alarm in the alarm list. Use the exact label text or time format as displayed in the alarm list."
    )
    enabled: Argument = Argument(
        value="true",
        description="Desired state for the alarm after toggling. Must be exactly 'true' or 'false' (lowercase string). 'true' = enable the alarm so it will ring at scheduled time, 'false' = disable the alarm so it will not ring. Use 'true' to activate a disabled alarm, 'false' to deactivate an active alarm without deleting it."
    )

    # Schema payload
    descriptions: List[str] = [
        "Turn ${{enabled}} alarm ${{alarm_identifier}}.",
        "Set alarm ${{alarm_identifier}} to ${{enabled}}.",
        "Toggle alarm ${{alarm_identifier}} to ${{enabled}}.",
        "Enable/disable alarm ${{alarm_identifier}} as ${{enabled}}.",
        "Switch alarm ${{alarm_identifier}} ${{enabled}}."
    ]

    def __init__(self, alarm_identifier: str = "Morning Alarm", enabled: str = "true", **kwargs) -> None:
        super().__init__(alarm_identifier=alarm_identifier, enabled=enabled, **kwargs)
        self.add_path(
            "toggle_alarm",
            path=[
                SingleClickAction(thought=f"Click toggle switch for alarm '{self.alarm_identifier}'."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockDeleteAlarm")
class ClockDeleteAlarm(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_delete_alarm"
    alarm_identifier: Argument = Argument(
        value="Morning Alarm",
        description="Identifier to locate the alarm to permanently delete. Can be either the alarm's label/name (e.g., 'Morning Alarm', 'Daily Reminder') or its time in HH:MM format (e.g., '07:00', '19:30'). Should uniquely identify the target alarm in the alarm list. The alarm will be completely removed and cannot be recovered. Use the exact label text or time format as displayed."
    )

    # Schema payload
    descriptions: List[str] = [
        "Delete alarm ${{alarm_identifier}}.",
        "Remove the alarm ${{alarm_identifier}}.",
        "Erase alarm named ${{alarm_identifier}}.",
        "Delete the alarm labeled ${{alarm_identifier}}.",
        "Remove alarm identified by ${{alarm_identifier}}."
    ]

    def __init__(self, alarm_identifier: str = "Morning Alarm", **kwargs) -> None:
        super().__init__(alarm_identifier=alarm_identifier, **kwargs)
        self.add_path(
            "delete_alarm",
            path=[
                SingleClickAction(thought=f"Right-click on alarm '{self.alarm_identifier}'."),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click delete option."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockAddWorldCity")
class ClockAddWorldCity(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_add_world_city"
    city: Argument = Argument(
        value="New York",
        description="Name of the city to add to World Clock for time zone tracking. Can be major cities worldwide. Examples: 'New York' (US Eastern), 'Los Angeles' (US Pacific), 'London' (UK/GMT), 'Paris' (Central European), 'Tokyo' (Japan), 'Sydney' (Australia), 'Dubai' (UAE), 'Singapore', 'Hong Kong', 'Moscow' (Russia), 'Berlin' (Germany), 'Toronto' (Canada), 'Beijing' (China), 'Mumbai' (India), 'São Paulo' (Brazil), 'Mexico City'. Use commonly recognized city names. The app will show the current time in that city's time zone."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add world clock city ${{city}}.",
        "Add ${{city}} to World Clock.",
        "Create a world clock for ${{city}}.",
        "Track time in ${{city}}.",
        "Add city ${{city}} to world clocks."
    ]

    def __init__(self, city: str = "New York", **kwargs) -> None:
        super().__init__(city=city, **kwargs)
        self.add_path(
            "add_world_city",
            path=[
                SingleClickAction(thought="Click add city button."),
                WaitAction(duration=1.0),
                TypeAction(thought=f"Type city name '{self.city}'.", text=self.city),
                WaitAction(duration=0.5),
                SingleClickAction(thought=f"Select the '{self.city}' from the dropdown menu."),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click add city button."),
                WaitAction(duration=1.0)
            ]
        )


@register("ClockRemoveWorldCity")
class ClockRemoveWorldCity(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_remove_world_city"
    city: Argument = Argument(
        value="New York",
        description="Name of the city to remove from World Clock display. Must match an existing city in your world clock list. Examples: 'New York', 'London', 'Tokyo', 'Paris', 'Sydney', etc. Use the exact city name as displayed in the world clock list. The city entry will be completely removed from the world clock display."
    )

    # Schema payload
    descriptions: List[str] = [
        "Remove world clock city ${{city}}.",
        "Delete ${{city}} from World Clock.",
        "Remove city ${{city}} from clocks.",
        "Erase world clock entry for ${{city}}.",
        "Clear city ${{city}} from World Clock."
    ]

    def __init__(self, city: str = "New York", **kwargs) -> None:
        super().__init__(city=city, **kwargs)
        self.add_path(
            "remove_world_city",
            path=[
                SingleClickAction(thought=f"Right-click on city '{self.city}'."),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click remove option."),
                WaitAction(duration=1.0)
            ]
        )


@register("ClockCreateTimer")
class ClockCreateTimer(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_create_timer"
    duration_minutes: Argument = Argument(
        value="10",
        description="Timer countdown duration in minutes. Must be a positive integer representing total minutes for the countdown. Durations greater than 60 minutes are automatically split into hours and minutes when entered into the timer UI. Common durations: '1' (1 minute, quick task), '5' (5 minutes, short break), '10' (10 minutes, standard task), '15' (15 minutes, quarter hour), '20' (20 minutes), '25' (25 minutes, pomodoro), '30' (30 minutes, half hour), '45' (45 minutes), '60' (1 hour, long session), '90' (90 minutes, maximum deep work). Typical range: 1 to 999 minutes. Examples: '10' for cooking, '25' for focused work session, '5' for quick break."
    )
    label: Argument = Argument(
        value="Pomodoro",
        description="Descriptive text label/name for the timer to identify its purpose. Can be any text string up to approximately 50 characters. Examples: 'Pomodoro' (focused work session), 'Cooking' (food preparation), 'Study Session' (learning time), 'Break Time' (rest period), 'Exercise' (workout duration), 'Tea Steeping' (beverage preparation), 'Meeting' (time limit), 'Meditation' (mindfulness practice). Use clear names that indicate what the timer is for."
    )

    # Schema payload
    descriptions: List[str] = [
        "Create a ${{duration_minutes}} minute timer called ${{label}}.",
        "Set timer for ${{duration_minutes}} minutes.",
        "Add timer ${{label}} for ${{duration_minutes}} minutes.",
        "Start a timer of ${{duration_minutes}} minutes named ${{label}}.",
        "Create timer ${{label}} of ${{duration_minutes}} minutes."
    ]

    def __init__(self, duration_minutes: str = "10", label: str = "Pomodoro", **kwargs) -> None:
        super().__init__(duration_minutes=duration_minutes, label=label, **kwargs)

        # The timer UI separates hours and minutes, so convert the total duration
        # input (in minutes) into individual fields that respect UI constraints.
        try:
            total_minutes = int(float(self.duration_minutes.value))
        except (TypeError, ValueError):
            total_minutes = 1

        total_minutes = max(1, min(total_minutes, 999))
        hours_value = total_minutes // 60
        minutes_value = total_minutes % 60
        hours_text = str(hours_value)
        minutes_text = f"{minutes_value:02d}"

        hours_actions = [
            SingleClickAction(thought="Focus on hours input."),
            WaitAction(duration=0.5),
            TypeAction(thought=f"Enter hours '{hours_text}'.", text=hours_text),
            WaitAction(duration=0.5),
        ]

        minutes_actions = [
            SingleClickAction(thought="Focus on minutes input."),
            WaitAction(duration=0.5),
            TypeAction(thought=f"Enter minutes '{minutes_text}'.", text=minutes_text),
            WaitAction(duration=0.5),
        ]

        self.add_path(
            "create_timer",
            path=[
                SingleClickAction(thought="Click add timer button."),
                WaitAction(duration=1.0),
                *hours_actions,
                *minutes_actions,
                SingleClickAction(thought="Locate and click the timer name input field (e.g., placeholder 'Name' or 'Timer name')."),
                WaitAction(duration=0.5),
                TypeAction(thought=f"Type timer label '{self.label}'.", text=self.label, input_mode="copy_paste"),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Save timer."),
                WaitAction(duration=1.0)
            ]
        )


@register("ClockStartTimer")
class ClockStartTimer(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_start_timer"
    label: Argument = Argument(
        value="Pomodoro",
        description="Label/name of the timer to start the countdown. Must match an existing timer in the timer list. Examples: 'Pomodoro' (start work session), 'Cooking' (begin cooking countdown), 'Study Session' (start study time), 'Break Time' (begin break), 'Exercise' (start workout timer). Use the exact label text as displayed in the timer list. Starting a timer begins the countdown from its configured duration."
    )

    # Schema payload
    descriptions: List[str] = [
        "Start timer ${{label}}.",
        "Begin the timer named ${{label}}.",
        "Run timer ${{label}} now.",
        "Start the ${{label}} countdown.",
        "Resume timer ${{label}}."
    ]

    def __init__(self, label: str = "Pomodoro", **kwargs) -> None:
        super().__init__(label=label, **kwargs)
        self.add_path(
            "start_timer",
            path=[
            SingleClickAction(thought=f"Locate timer entry whose label text matches '{self.label}' in the timer list, then click its Start (play) button to begin the countdown."),
            WaitAction(duration=0.5)
            ]
        )


@register("ClockPauseTimer")
class ClockPauseTimer(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_pause_timer"
    label: Argument = Argument(
        value="Pomodoro",
        description="Label/name of the timer to pause. Must match a currently running timer in the timer list. Examples: 'Pomodoro' (pause work session), 'Cooking' (pause cooking timer), 'Study Session' (pause study time). Use the exact label text as displayed. Pausing a timer stops the countdown while preserving the remaining time, allowing you to resume later from where it stopped."
    )

    # Schema payload
    descriptions: List[str] = [
        "Pause timer ${{label}}.",
        "Stop the timer ${{label}}.",
        "Pause the ${{label}} countdown.",
        "Hold timer named ${{label}}.",
        "Temporarily stop timer ${{label}}."
    ]

    def __init__(self, label: str = "Pomodoro", **kwargs) -> None:
        super().__init__(label=label, **kwargs)
        self.add_path(
            "pause_timer",
            path=[
                SingleClickAction(thought=f"Click pause button for timer '{self.label}'."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockResetTimer")
class ClockResetTimer(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_reset_timer"
    label: Argument = Argument(
        value="Pomodoro",
        description="Label/name of the timer to reset to its original duration. Must match an existing timer in the timer list. Examples: 'Pomodoro' (reset work session timer), 'Cooking' (reset cooking timer to full time), 'Study Session' (restart study timer). Use the exact label text as displayed. Resetting a timer returns it to its configured duration, clearing any elapsed time."
    )

    # Schema payload
    descriptions: List[str] = [
        "Reset timer ${{label}}.",
        "Clear the ${{label}} timer.",
        "Reset countdown ${{label}} to start.",
        "Restart timer named ${{label}}.",
        "Reset the timer ${{label}} back to zero."
    ]

    def __init__(self, label: str = "Pomodoro", **kwargs) -> None:
        super().__init__(label=label, **kwargs)
        self.add_path(
            "reset_timer",
            path=[
                SingleClickAction(thought=f"Click reset button for timer '{self.label}'."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockDeleteTimer")
class ClockDeleteTimer(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_delete_timer"
    label: Argument = Argument(
        value="Pomodoro",
        description="Label/name of the timer to permanently delete. Must match an existing timer in the timer list. Examples: 'Pomodoro' (remove work timer), 'Cooking' (remove cooking timer), 'Old Timer' (remove unused timer). Use the exact label text as displayed. The timer will be completely removed and cannot be recovered. All its settings and remaining time will be lost."
    )

    # Schema payload
    descriptions: List[str] = [
        "Delete timer ${{label}}.",
        "Remove the timer named ${{label}}.",
        "Erase timer ${{label}}.",
        "Delete the ${{label}} countdown.",
        "Remove timer called ${{label}}."
    ]

    def __init__(self, label: str = "Pomodoro", **kwargs) -> None:
        super().__init__(label=label, **kwargs)
        self.add_path(
            "delete_timer",
            path=[
                SingleClickAction(thought=f"Right-click on timer '{self.label}'."),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Click delete option."),
                WaitAction(duration=1.0)
            ]
        )


@register("ClockStartStopwatch")
class ClockStartStopwatch(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_start_stopwatch"

    # Schema payload
    descriptions: List[str] = [
        "Start stopwatch.",
        "Begin the stopwatch.",
        "Run the stopwatch now.",
        "Start timing with the stopwatch.",
        "Begin stopwatch timing."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "start_stopwatch",
            path=[
                SingleClickAction(thought="Click start button on stopwatch."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockLapStopwatch")
class ClockLapStopwatch(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_lap_stopwatch"

    # Schema payload
    descriptions: List[str] = [
        "Record a lap on the stopwatch.",
        "Add a lap time.",
        "Mark a lap now.",
        "Lap the stopwatch.",
        "Capture a lap."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "lap_stopwatch",
            path=[
                SingleClickAction(thought="Click lap button on stopwatch."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockPauseStopwatch")
class ClockPauseStopwatch(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_pause_stopwatch"

    # Schema payload
    descriptions: List[str] = [
        "Pause the stopwatch.",
        "Stop the stopwatch.",
        "Hold the stopwatch timing.",
        "Pause timing now.",
        "Temporarily stop the stopwatch."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "pause_stopwatch",
            path=[
                SingleClickAction(thought="Click pause button on stopwatch."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockResetStopwatch")
class ClockResetStopwatch(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_reset_stopwatch"

    # Schema payload
    descriptions: List[str] = [
        "Reset the stopwatch.",
        "Clear stopwatch time.",
        "Reset timing to zero.",
        "Restart the stopwatch.",
        "Reset stopwatch back to 00:00."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "reset_stopwatch",
            path=[
                SingleClickAction(thought="Click reset button on stopwatch."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockStartFocusSession")
class ClockStartFocusSession(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_start_focus_session"
    duration_minutes: Argument = Argument(
        value="25",
        description="Focus session duration in minutes for concentrated work without distractions. Must be a positive integer. Common focus session durations: '15' (15 minutes, short focus), '20' (20 minutes, medium focus), '25' (25 minutes, standard pomodoro), '30' (30 minutes, half hour focus), '45' (45 minutes, deep work), '50' (50 minutes, extended focus), '60' (1 hour, long session), '90' (90 minutes, maximum deep work). Typical range: 15 to 90 minutes. The pomodoro technique recommends 25-minute sessions with 5-minute breaks."
    )

    # Schema payload
    descriptions: List[str] = [
        "Start a ${{duration_minutes}} minute focus session.",
        "Begin focus for ${{duration_minutes}} minutes.",
        "Run focus session for ${{duration_minutes}} minutes.",
        "Start focus session for ${{duration_minutes}} minutes.",
        "Begin a focus session of ${{duration_minutes}} minutes."
    ]

    def __init__(self, duration_minutes: str = "25", **kwargs) -> None:
        super().__init__(duration_minutes=duration_minutes, **kwargs)
        self.add_path(
            "start_focus_session",
            path=[
                SingleClickAction(thought="Click mins input for focus session."),
                WaitAction(duration=1.0),
                TypeAction(thought=f"Enter duration '{self.duration_minutes}' minutes.", text=self.duration_minutes),
                WaitAction(duration=0.5),
                SingleClickAction(thought="Start the focus session."),
                WaitAction(duration=1.0)
            ]
        )


@register("ClockPauseFocusSession")
class ClockPauseFocusSession(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_pause_focus_session"

    # Schema payload
    descriptions: List[str] = [
        "Pause focus session.",
        "Temporarily stop focus.",
        "Hold the focus session.",
        "Pause current focus.",
        "Stop the focus timer."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "pause_focus_session",
            path=[
                SingleClickAction(thought="Click pause button on focus session."),
                WaitAction(duration=0.5)
            ]
        )


@register("ClockResetFocusSession")
class ClockResetFocusSession(ClockBaseAction):
    # Canonical identifiers
    type: str = "clock_reset_focus_session"

    # Schema payload
    descriptions: List[str] = [
        "Reset focus session.",
        "Reset the focus session now.",
        "Reset the focus session.",
        "Reset current focus.",
        "Reset the focus timer."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "reset_focus_session",
            path=[
                SingleClickAction(thought="Click reset button on focus session."),
                WaitAction(duration=0.5)
            ]
        )
