
from enum import IntEnum
import re
import string
import logging
from io import BytesIO
import base64

def get_screenshot(target_resolution=None, env=None):
    if env is None:
        import pyautogui
        screenshot = pyautogui.screenshot()
    else: 
        env.get_screenshot()
    
    if target_resolution is not None:
        screenshot = screenshot.resize(target_resolution)
    return screenshot

class Status(IntEnum):
    INITIAL = 1
    SUCCESS = 2
    FAILURE = 3
    IN_PROGRESS = 4
    STUCK = 5
    TIMEOUT = 6
    CANCELED = 7
    ENV_ERROR = 8
    CALL_USER = 9

def remove_surrounding_punctuation(s):
    return s.strip(string.punctuation)


def get_next_word_after_keywords(text, keyword_list):
    match_keyword = None
    for keyword in keyword_list:
        if keyword in text:
            match_keyword = keyword
            break
    if match_keyword is None:
        return None
    tokens = text.strip().split()
    idx = tokens.index(match_keyword)
    return remove_surrounding_punctuation(tokens[idx+1])


def get_target_str_after_keywords(text, keywords):
    pattern = rf'({"|".join(keywords)})\s*"([^"]+)"'
    match = re.search(pattern, text)

    return match.group(2) if match else None


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Create formatter and add it to the handler
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s', 
                                      datefmt='%Y-%m-%d %H:%M:%S')
        ch.setFormatter(formatter)

        # Add handler to the logger
        logger.addHandler(ch)
        logger.propagate = False

    return logger

def pil_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")  # You can change this to "JPEG" or other formats
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def escape_single_quotes(text):
    # Match single quotes that are not already escaped (does not match \')
    pattern = r"(?<!\\)'"
    return re.sub(pattern, r"\\'", text)
