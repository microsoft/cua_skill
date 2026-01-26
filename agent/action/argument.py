class Argument:
    value: any
    description: str = ""
    _frozen: bool = False

    def __init__(
        self, 
        value: any,
        description: str = "",
        frozen: bool = False
    ):
        if isinstance(value, Argument):
            inner = value
            self.value = inner.value
            self.description = description or inner.description
            self._frozen = frozen or inner._frozen
        else:
            self.value = value
            self.description = description
            self._frozen = frozen

        

    def __setattr__(self, name, value):
        # block changing .value if frozen
        if hasattr(self, "_frozen"):
            if name == "value" and getattr(self, "_frozen", False):
                raise AttributeError(f"This {name} Argument.value is frozen and cannot be modified to {value}.")
        super().__setattr__(name, value)

    def __repr__(self):
        return f"{self.value}"

    def __getattr__(self, name):
        return getattr(self.value, name)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, Argument):
            return self.value == other.value
        return self.value == other