import os
import json
import re
import ast
import shutil
from pathlib import Path
from datetime import datetime
from threading import Lock
from .LoggerMessages._base import BaseLogMessage
from rich.console import Console

from .LoggerMessages._base import LOG_LEVEL_VALUES, LogLevel
from .LoggerMessages import LogMessage

from ._session_logger_utils import scan_and_replace_images, reset_unique_image_filename_id
from logging import Logger as PythonLogger
import copy
import uuid


def sanitize_filename(filename):
    # Define a regex pattern for invalid characters
    invalid_chars = r'[\/:*?"<>|]'
    # Replace them with underscore
    safe_filename = re.sub(invalid_chars, '_', filename)
    return safe_filename

class SessionLogger:
    def __init__(self, config=None, remote_logger=None, explicit_log_dir=None):
        self.remote_logger = remote_logger if isinstance(remote_logger, PythonLogger) else None
        self.config = config

        self.explicit_log_dir = explicit_log_dir

        reset_unique_image_filename_id()
        if (self.explicit_log_dir):
            base_log_dir = self.explicit_log_dir
            self.base_log_dir = Path(base_log_dir)
            self.base_log_dir.mkdir(parents=True, exist_ok=True)
            self.session_dir = self.base_log_dir
        else:            
            base_log_dir = "./logs" if not self.config else self.config.log_dir
            self.base_log_dir = Path(base_log_dir)
            self.session_dir = self._create_new_session_dir()
        
        base_log_file = "log.jsonl" if not self.config else f"{self.config.log_file}"
        self.log_file = self.session_dir / base_log_file
        self.lock = Lock()

        self.console = Console(record=True)

        self.minimum_level: LogLevel = "info" if not self.config else self.config.log_level

    def _remote_log(self, message: BaseLogMessage):
        if self.remote_logger:
            getattr(self.remote_logger, message.level)(message.to_json())

    def _create_new_session_dir(self) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_path = self.base_log_dir / timestamp
        session_path.mkdir(parents=True, exist_ok=True)
        return session_path

    def log(self, message: BaseLogMessage):
        if self.config and not self.config.enable:
            return  # if debug is not enabled - skip all messages

        if not self._should_log(message.level):
            return  # Skip messages below the minimum level        

        if True:
            # replace image data in the message by links to image files that are saved in the same log-folder
            message = scan_and_replace_images(message, output_dir=str(self.session_dir), images_tag=sanitize_filename(f"{message.type}_{message.source}"))

        line = message.to_json()

        with self.lock:
            self._remote_log(message)
            if message.save_to_disk:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")

            if message.display_console:
                console_line = message.to_console()
                # consoline line might be a string or a rich panel
                self.console.print(console_line)

    def _should_log(self, level: LogLevel) -> bool:
        return LOG_LEVEL_VALUES[level] >= LOG_LEVEL_VALUES[self.minimum_level]

    def _handle_non_message_types(self, msg) -> BaseLogMessage:
        if isinstance(msg, str):
            return LogMessage(message=msg)
        
        return msg

    def save_all_to_html(self):
        # Export the recorded output to HTML
        html = self.console.export_html(inline_styles=True, clear=False)

        # Save to file 
        html_file = self.session_dir / "_console_output.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html) 

    # Convenience methods
    def debug(self, msg: BaseLogMessage): msg = self._handle_non_message_types(msg); msg.level = "debug"; self.log(msg)
    def info(self, msg: BaseLogMessage): msg = self._handle_non_message_types(msg); msg.level = "info"; self.log(msg)
    def warning(self, msg: BaseLogMessage): msg = self._handle_non_message_types(msg); msg.level = "warning"; self.log(msg)
    def error(self, msg: BaseLogMessage): msg = self._handle_non_message_types(msg); msg.level = "error"; self.log(msg)
    def critical(self, msg: BaseLogMessage): msg = self._handle_non_message_types(msg); msg.level = "critical"; self.log(msg)

    def convert(self):
        if self.session_dir == self.base_log_dir:
            convert_log_dir = os.path.join(Path(self.base_log_dir).parent, 'converted_log')
        else:
            convert_log_dir = os.path.join(Path(self.base_log_dir), 'converted_log')

        convert_log = {}
        convert_log['id'] = str(uuid.uuid4())

        logs = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():  # skip empty lines
                    obj = json.loads(line)
                    logs.append(obj)
    
        operation_dict = {}
        convert_log['operations'] = []
        skipped_actions = ['WaitAction', 'DummyAction']
        step = 0
        for log in logs:
            if log['type'] == 'agent_start':
                convert_log['instruction'] = log['message'].split('Task Description: ')[-1].strip()
                convert_log['domain'] = log['message'].split('Task Domain: ')[-1].split('\n')[0].strip()

                convert_log_dir = os.path.join(convert_log_dir, convert_log['domain'], convert_log['id'])
                self.convert_log_dir = convert_log_dir
                os.makedirs(convert_log_dir, exist_ok=True)
            
            if log['type'] == 'agent_operation_start':
                # Commit previous operation dict
                if len(operation_dict) > 0:
                    convert_log['operations'].append(operation_dict)
                operation_dict = {}
                operation_info = parse_operation_and_arguments(log['message'])
                operation_dict['operation'] = operation_info['operation']
                operation_dict['arguments'] = operation_info['arguments']
                operation_dict['steps'] = []


            if log['type'] == 'before_after_observation_action':
                action_str = log['metadata']['action']
                action_dict = parse_action_to_json(action_str)
                if action_dict['action'] in skipped_actions:
                    if len(action_dict['arguments']['thought']) == 0:
                        continue
                action_dict['before_observation'] = copy.deepcopy(log['metadata']['before_observation'])
                action_dict['before_observation']['screenshot'] = f"step_{step}_action_{action_dict['action']}_before_observation.png"                
                shutil.copy(
                    os.path.join(self.session_dir, log['metadata']['before_observation']['screenshot']),
                    os.path.join(convert_log_dir, action_dict['before_observation']['screenshot']),
                )
                action_dict['after_observation'] = copy.deepcopy(log['metadata']['after_observation'])
                action_dict['after_observation']['screenshot'] = f"step_{step}_action_{action_dict['action']}_after_observation.png"
                shutil.copy(
                    os.path.join(self.session_dir, log['metadata']['after_observation']['screenshot']),
                    os.path.join(convert_log_dir, action_dict['after_observation']['screenshot']),
                )
                action_dict['executable_action'] = log['metadata']['executable_action']
                operation_dict['steps'].append(action_dict)

                step += 1

        # Commit the last operation dict if it exists
        if len(operation_dict) > 0:
            convert_log['operations'].append(operation_dict)

        with open(os.path.join(convert_log_dir, 'log.json'), 'w', encoding='utf-8') as f:
            print("Converting log to JSON", convert_log_dir)
            json.dump(normalize_log(convert_log), f, indent=4)


class LogIterator:
    def __init__(self, file_path, filters=None):
        """
        Initialize the LogIterator.

        :param file_path: Path to the JSONL file.
        :param filters: Dictionary of filters to apply (e.g., {"type": "error", "source": "auth"}).
        """
        self.file_path = file_path
        self.filters = filters or {}

    def _matches_filters(self, log_entry):
        for key, value in self.filters.items():
            if key not in log_entry or log_entry[key] != value:
                return False
        return True

    def __iter__(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    if self._matches_filters(log_entry):
                        yield log_entry
                except json.JSONDecodeError:
                    continue  # Skip malformed lines


def _safe_literal(v: str):
    """Try to parse Python literal, otherwise return as a string."""
    v = v.strip()
    if v.endswith(","):
        v = v[:-1].strip()
    try:
        return ast.literal_eval(v)
    except Exception:
        return v


def parse_action_to_json(s: str):
    """
    Convert a raw action string into:
    {
        "action": "<ActionClassName>",
        "arguments": { ... }
    }
    """
    # Extract class/action name
    m_class = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", s)
    if not m_class:
        raise ValueError("Cannot parse action name")
    action_name = m_class.group(1)

    # Extract arguments body { ... }
    m_args = re.search(r"arguments=\{(.*)\}\)\s*$", s)
    if not m_args:
        # fallback: match until the last closing brace
        m_args = re.search(r"arguments=\{(.*)\}", s)
        if not m_args:
            raise ValueError("Cannot parse arguments")
    args_body = m_args.group(1).strip()

    # Parse all key-value pairs inside the arguments dict
    kv_pattern = re.compile(r"'([^']+)':\s*")
    matches = list(kv_pattern.finditer(args_body))

    arguments = {}
    for i, m in enumerate(matches):
        key = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(args_body)
        raw_val = args_body[start:end].strip()
        arguments[key] = _safe_literal(raw_val)

    return {
        "action": action_name,
        "arguments": arguments
    }


def normalize_log(example: dict) -> dict:
    """Reorder fields and add a unique id."""
    return {
        "id": example.get("id", str(uuid.uuid4())),
        "instruction": example["instruction"],
        "domain": example["domain"],
        "operations": example["operations"],
    }


# def parse_operation_and_arguments(line: str):
#     """
#     Parse only the operation name and its arguments from a CUA operation line.
#     Example:
#       Starting Operation: ExcelLaunch(id=excel_launch_1, type=excel_launch, arguments={'application_name': Excel, 'description_present': False})
#     Returns:
#       { "operation": "ExcelLaunch",
#         "arguments": { ... } }
#     """

#     # Extract operation name
#     op_match = re.search(r"Starting Operation:\s*([A-Za-z0-9_]+)\s*\(", line)
#     if not op_match:
#         raise ValueError("Operation name not found.")
#     operation = op_match.group(1)

#     # Extract arguments={...}
#     arg_match = re.search(r"arguments\s*=\s*(\{.*\})\s*\)?$", line)
#     if not arg_match:
#         raise ValueError("Arguments section not found.")
#     raw_args = arg_match.group(1)

#     # Fix bare identifiers inside the dict (e.g., Excel → 'Excel')
#     raw_args_fixed = re.sub(
#         r"(:\s*)([A-Za-z_][A-Za-z0-9_]*)",
#         lambda m: f"{m.group(1)}'{m.group(2)}'",
#         raw_args
#     )

#     arguments = ast.literal_eval(raw_args_fixed)

#     return {
#         "operation": operation,
#         "arguments": arguments
#     }

# def parse_operation_and_arguments(line: str):
#     # Extract operation name
#     op_match = re.search(r"Starting Operation:\s*([A-Za-z0-9_]+)\s*\(", line)
#     if not op_match:
#         raise ValueError("Operation name not found.")
#     operation = op_match.group(1)

#     # Extract interior of arguments={...}
#     args_match = re.search(r"arguments\s*=\s*\{(.*)\}\s*\)?$", line)
#     if not args_match:
#         raise ValueError("Arguments section not found.")

#     args_str = args_match.group(1).strip()

#     # --- Robust key=value parser ---
#     arguments = {}
#     for part in re.split(r",\s*(?=[a-zA-Z_]+\s*=)", args_str):
#         print(part)
#         key, value = part.split("=", 1)
#         key = key.strip()
#         value = value.strip()

#         # Remove stray quotes
#         value = value.strip("'\"")

#         arguments[key] = value

#     return {
#         "operation": operation,
#         "arguments": arguments
#     }


def _split_top_level_commas(s: str):
    """
    Split string on commas that are not inside [], {}, (), or quotes.
    """
    parts = []
    buf = []
    depth_round = depth_square = depth_curly = 0
    in_single = in_double = False
    prev = ""

    for ch in s:
        if ch == "'" and not in_double and prev != "\\":
            in_single = not in_single
        elif ch == '"' and not in_single and prev != "\\":
            in_double = not in_double
        elif not in_single and not in_double:
            if ch == "(":
                depth_round += 1
            elif ch == ")":
                depth_round -= 1
            elif ch == "[":
                depth_square += 1
            elif ch == "]":
                depth_square -= 1
            elif ch == "{":
                depth_curly += 1
            elif ch == "}":
                depth_curly -= 1
            elif ch == "," and depth_round == depth_square == depth_curly == 0:
                parts.append("".join(buf).strip())
                buf = []
                prev = ch
                continue

        buf.append(ch)
        prev = ch

    if buf:
        parts.append("".join(buf).strip())
    return parts



def parse_operation_and_arguments(line: str):
    """
    Parse only the operation name and its arguments from a CUA operation line.
    """
    # ---- 1) Operation name ----
    op_match = re.search(r"Starting Operation:\s*([A-Za-z0-9_]+)\s*\(", line)
    if not op_match:
        raise ValueError("Operation name not found.")
    operation = op_match.group(1)

    # ---- 2) Extract arguments body inside {...} ----
    arg_match = re.search(r"arguments\s*=\s*\{(.*)\}\s*\)?$", line)
    if not arg_match:
        raise ValueError("Arguments section not found.")
    args_body = arg_match.group(1).strip()

    # ---- 3) Split into `'key': value` parts at top level ----
    parts = _split_top_level_commas(args_body)

    arguments = {}
    for part in parts:
        if ":" not in part:
            raise ValueError(f"Malformed argument part (no colon found): {part}")

        key_part, value_part = part.split(":", 1)
        key_part = key_part.strip()
        value_part = value_part.strip()

        # keys are quoted: use literal_eval to unquote safely
        key = ast.literal_eval(key_part)

        raw = value_part

        # ---- 4) Parse value ----
        # Lists / dicts / tuples
        if raw.startswith(("[", "{", "(")):
            value = ast.literal_eval(raw)
        # Booleans / None / numbers
        elif raw in ("True", "False", "None") or re.fullmatch(r"-?\d+(\.\d+)?", raw):
            value = ast.literal_eval(raw)
        else:
            # Treat everything else as a string; strip quotes if present
            if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
                raw = raw[1:-1]
            value = raw

        arguments[key] = value

    return {
        "operation": operation,
        "arguments": arguments,
    }