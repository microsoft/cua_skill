import json
from pathlib import Path
from typing import Any, Dict

from ._dot_dict import DotDict  # Import the updated DotDict with flags

class Config(DotDict):
    """
    A dynamic configuration class that loads settings from a JSON file.
    All fields are determined by the JSON file itself, with no predefined attributes.
    Supports missing key handling with configurable behavior.

    Args:
        data (dict, optional): Dictionary of configuration settings.
        raise_on_missing (bool): If True, raises an exception for missing keys.
                                 If False, returns `default_value` instead.
        default_value (Any): The value to return when accessing a missing key
                             (only used if `raise_on_missing` is False).

    Example:
        config = Config.load("config.json", raise_on_missing=False, default_value="N/A")
        print(config.api_endpoint)  # Access fields dynamically
    """

    def __init__(self, data=None, raise_on_missing=True, default_value=None):
        """
        Initializes the Config instance with dynamic attributes.

        Args:
            data (dict, optional): Dictionary of configuration settings.
            raise_on_missing (bool): Whether to raise an exception for missing keys.
            default_value (Any): Default value to return if `raise_on_missing=False`.
        """
        super().__init__(data or {}, raise_on_missing=raise_on_missing, default_value=default_value)

    def save(self, file_path: str):
        """
        Saves the current configuration to a JSON file.

        Args:
            file_path (str): The path to the JSON file where the config will be saved.

        Example:
            config.save("config.json")
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self, f, indent=4)

    @classmethod
    def load(cls, file_path: str, raise_on_missing=True, default_value=None):
        """
        Loads configuration from a JSON file with optional missing key behavior.

        Args:
            file_path (str): The path to the JSON file.
            raise_on_missing (bool): Whether to raise an exception for missing keys.
            default_value (Any): Default value to return if a key is missing.

        Returns:
            Config: A new Config instance populated with data from the JSON file.

        If the file does not exist, returns an empty Config instance.

        Example:
            config = Config.load("config.json", raise_on_missing=False, default_value="N/A")
        """
        if not Path(file_path).exists():
            return cls(raise_on_missing=raise_on_missing, default_value=default_value)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file: {e}")
            return cls(raise_on_missing=raise_on_missing, default_value=default_value)
        
        return cls(data, raise_on_missing=raise_on_missing, default_value=default_value)
