import os, random, time

def generate_snip_filename(
    directory="captures",
    prefix_options=None,
    extensions=None,
    timestamp_format="%Y-%m-%d_%H-%M-%S",
):
    """
    Generate a realistic filename for Snipping Tool output (image or video).

    Examples:
      captures/Screenshot_2025-10-05_19-55-03.png
      captures/Recording_2025-10-05_19-55-10.mp4
    """
    prefix_options = prefix_options or ["Screenshot", "Snip", "Capture", "Annotation", "Recording"]
    extensions = extensions or [".png", ".jpg", ".jpeg", ".mp4", ".webm"]

    # Pick an extension and align the prefix (video → likely 'Recording')
    ext = random.choice(extensions)
    if ext in (".mp4", ".webm"):
        bias_prefixes = ["Recording", "Capture"]
        prefix = random.choice(bias_prefixes + prefix_options)
    else:
        prefix = random.choice(prefix_options)

    timestamp = time.strftime(timestamp_format)
    filename = f"{prefix}_{timestamp}{ext}"
    # ensure directory prefix exists in path string (creation left to caller)
    return os.path.join(directory, filename)