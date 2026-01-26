

class DotDict(dict):
    """
    A dictionary that allows dot notation access to its keys.
    
    Features:
    - Supports dot notation access (`config.key`)
    - Optionally raises an exception or returns a default value on missing keys
    - Converts nested dictionaries into `DotDict` automatically

    Args:
        data (dict, optional): Initial dictionary data.
        raise_on_missing (bool): If True, raises AttributeError for missing keys.
                                 If False, returns `default_value` instead.
        default_value (Any): The value to return when a missing key is accessed (if `raise_on_missing=False`).

    Example:
        d = DotDict({"name": "Alice"}, raise_on_missing=True)
        print(d.name)  # Alice
        print(d.age)   # Raises AttributeError

        d = DotDict({"name": "Alice"}, raise_on_missing=False, default_value="N/A")
        print(d.age)   # "N/A"
    """

    def __init__(self, data=None, raise_on_missing=True, default_value=None):
        """Initialize DotDict with optional data, exception flag, and default return value."""
        super().__init__(data or {})
        self.raise_on_missing = raise_on_missing
        self.default_value = default_value

    def __getattr__(self, name):
        """
        Enables dot notation access for dictionary keys.
        If `raise_on_missing` is False, returns `default_value` instead of raising an error.
        """
        try:
            value = self[name]
            if isinstance(value, dict):  # Convert nested dictionaries into DotDict
                return DotDict(value, self.raise_on_missing, self.default_value)
            return value
        except KeyError:
            if self.raise_on_missing:
                raise AttributeError(f"'DotDict' object has no attribute '{name}'")
            return self.default_value  # Return default value if key is missing

    def __setattr__(self, name, value):
        """Allows setting dictionary values using dot notation."""
        if name in {"raise_on_missing", "default_value"}:  # Store internal attributes normally
            super().__setattr__(name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        """Allows deleting dictionary keys using dot notation."""
        if name in self:
            del self[name]
        else:
            if self.raise_on_missing:
                raise AttributeError(f"'DotDict' object has no attribute '{name}'")

    def get(self, key, default=None):
        """
        Overrides the default `get` method to respect `raise_on_missing` behavior.

        Example:
            d.get("missing_key", "default")  # Returns "default" instead of self.default_value
        """
        if key in self:
            return self[key]
        return default if default is not None else (self.default_value if not self.raise_on_missing else None)


