import random

def generate_setting_value(setting_name_arg: str, rules: dict, **kwargs):
    """
    Dependent value generator for WindowsSettingsSetValue.
    Expects the pipeline to call with a context dict containing the
    already-chosen argument values, and to pass those into **kwargs**,
    e.g. kwargs.get(setting_name_arg) yields the resolved setting_name.
    """
    setting_name = kwargs.get(setting_name_arg)
    spec = rules.get(setting_name) or rules.get("__default__") or {"type": "options", "options": ["Apply"]}

    t = spec.get("type")
    if t == "number":
        min_v = int(spec.get("min", 0))
        max_v = int(spec.get("max", 100))
        step  = int(spec.get("step", 1))
        suffix = spec.get("suffix", "")
        # choose a multiple of step in [min, max]
        candidates = list(range(min_v, max_v + 1, step)) or [min_v, max_v]
        val = random.choice(candidates)
        return f"{val}{suffix}" if suffix else val

    # default: options
    options = spec.get("options") or ["Apply"]
    return random.choice(options)
