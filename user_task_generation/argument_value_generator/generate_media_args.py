import random
from typing import List, Dict, Any, Optional

def generate_media_file_path(
    media_type: str = "video",
    include_resolution: bool = True,
    extensions: Optional[List[str]] = None,
    **kwargs
) -> str:
    """
    Generate a realistic media file path with absolute Windows path.
    
    Args:
        media_type: Type of media - "video", "audio", or "mixed"
        include_resolution: Whether to include resolution in video filenames
        extensions: List of valid file extensions
        **kwargs: Additional parameters for future extensibility
    
    Returns:
        A generated absolute media file path string (Windows format)
    """
    
    # Default extensions based on media type
    if extensions is None:
        if media_type == "video":
            extensions = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mpg", ".mpeg", ".m4v"]
        elif media_type == "audio":
            extensions = [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"]
        else:  # mixed
            extensions = [".mp4", ".avi", ".mkv", ".mp3", ".wav", ".flac"]
    
    # Windows drive letters
    drives = ["C:", "D:"]
    
    # Common Windows base directories
    base_paths = [
        "Users\\{user}\\Videos",
        "Users\\{user}\\Music",
        "Users\\{user}\\Documents\\Media",
        "Users\\{user}\\Downloads",
        "Users\\{user}\\Desktop",
        "Media",
        "Videos",
        "Music",
        "Recordings",
        "Content",
        "MediaLibrary",
    ]
    
    # Common usernames
    usernames = ["User", "Admin", "John", "Jane", "Public", "Owner", "Default"]
    
    # Optional subdirectories
    subdirs = [
        "", # No subdirectory
        "Projects",
        "Work",
        "Personal",
        "Archive",
        "New",
        "2024",
        "2023",
        "Collection",
        "Library",
        "Favorites",
    ]
    
    # Video filename templates
    video_names = [
        "movie", "film", "video", "clip", "recording", "documentary", "tutorial",
        "episode", "trailer", "teaser", "highlights", "compilation", "vlog",
        "presentation", "lecture", "webinar", "interview", "review", "gameplay",
        "music_video", "short_film", "animation", "demo", "preview", "sample"
    ]
    
    # Audio filename templates
    audio_names = [
        "song", "track", "music", "audio", "podcast", "audiobook", "recording",
        "mix", "album", "single", "soundtrack", "score", "theme", "intro",
        "outro", "jingle", "ringtone", "sample", "loop", "beat"
    ]
    
    # Common prefixes/descriptors
    prefixes = [
        "best", "new", "old", "classic", "modern", "amazing", "awesome",
        "great", "favorite", "top", "popular", "trending", "viral", "latest",
        "exclusive", "special", "bonus", "deluxe", "extended", "remix"
    ]
    
    # Common suffixes/descriptors
    suffixes = [
        "final", "draft", "copy", "original", "edited", "remastered",
        "enhanced", "restored", "hd", "uhd", "4k", "8k", "hq", "lq"
    ]
    
    # Resolution options for video
    resolutions = [
        "720p", "1080p", "1440p", "2160p", "4K", "8K",
        "HD", "FHD", "UHD", "SD", "HQ", "HDR"
    ]
    
    # Years for dated content
    years = list(range(2018, 2025))
    
    # TV/Series patterns
    series_patterns = [
        "S{:02d}E{:02d}",  # S01E01
        "Season{}_Episode{}",  # Season1_Episode1
        "s{}e{}",  # s1e1
        "{:02d}x{:02d}"  # 01x01
    ]
    
    # Choose base name based on media type
    if media_type == "audio":
        base_names = audio_names
    else:
        base_names = video_names
    
    # Randomly select components
    base_name = random.choice(base_names)
    extension = random.choice(extensions)
    
    # Build filename with various patterns
    pattern = random.randint(1, 10)
    
    if pattern == 1:
        # Simple: name.ext
        filename = f"{base_name}{extension}"
    
    elif pattern == 2:
        # With prefix: prefix_name.ext
        prefix = random.choice(prefixes)
        filename = f"{prefix}_{base_name}{extension}"
    
    elif pattern == 3:
        # With suffix: name_suffix.ext
        suffix = random.choice(suffixes)
        filename = f"{base_name}_{suffix}{extension}"
    
    elif pattern == 4:
        # With number: name_01.ext
        number = random.randint(1, 99)
        filename = f"{base_name}_{number:02d}{extension}"
    
    elif pattern == 5:
        # With year: name_2023.ext
        year = random.choice(years)
        filename = f"{base_name}_{year}{extension}"
    
    elif pattern == 6:
        # Series format (for video)
        if media_type == "video" and random.random() < 0.7:
            pattern_format = random.choice(series_patterns)
            season = random.randint(1, 10)
            episode = random.randint(1, 24)
            series_code = pattern_format.format(season, episode)
            show_name = random.choice(["show", "series", "program", base_name])
            filename = f"{show_name}_{series_code}{extension}"
        else:
            # Fallback to numbered
            filename = f"{base_name}_{random.randint(1, 999):03d}{extension}"
    
    elif pattern == 7:
        # With date: name_20231225.ext
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        year = random.choice(years)
        filename = f"{base_name}_{year}{month:02d}{day:02d}{extension}"
    
    elif pattern == 8:
        # Multiple descriptors: prefix_name_suffix_number.ext
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        number = random.randint(1, 99)
        filename = f"{prefix}_{base_name}_{suffix}_{number:02d}{extension}"
    
    elif pattern == 9:
        # Part format: name_part1.ext
        part = random.randint(1, 5)
        filename = f"{base_name}_part{part}{extension}"
    
    else:
        # Version format: name_v2.ext
        version = random.randint(1, 5)
        filename = f"{base_name}_v{version}{extension}"
    
    # Add resolution for video files if requested
    if media_type == "video" and include_resolution and random.random() < 0.6:
        resolution = random.choice(resolutions)
        name_parts = filename.rsplit('.', 1)
        filename = f"{name_parts[0]}_{resolution}.{name_parts[1]}"
    
    # Sometimes add brackets or parentheses
    if random.random() < 0.2:
        extra_info = random.choice([
            "[OFFICIAL]", "(OFFICIAL)", "[FULL]", "(FULL)", 
            "[COMPLETE]", "(HD)", "[4K]", "(NEW)", "[2024]"
        ])
        name_parts = filename.rsplit('.', 1)
        filename = f"{name_parts[0]}_{extra_info}.{name_parts[1]}"
    
    # Clean up multiple underscores and spaces
    filename = filename.replace("__", "_")
    filename = filename.replace(" ", "_")
    
    # Build the absolute Windows path
    drive = random.choice(drives)
    base_path = random.choice(base_paths)
    
    # Replace {user} placeholder if present
    if "{user}" in base_path:
        username = random.choice(usernames)
        base_path = base_path.replace("{user}", username)
    
    # Optionally add subdirectory
    subdir = random.choice(subdirs)
    
    # Construct the full path
    if subdir:
        full_path = f"{drive}\\{base_path}\\{subdir}\\{filename}"
    else:
        full_path = f"{drive}\\{base_path}\\{filename}"
    
    return full_path


def generate_subtitle_filename(
    extensions: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
    **kwargs
) -> str:
    """
    Generate a realistic subtitle filename.
    
    Args:
        extensions: List of subtitle file extensions
        languages: List of language codes
        **kwargs: Additional parameters
    
    Returns:
        A generated subtitle filename string
    """
    
    if extensions is None:
        extensions = [".srt", ".sub", ".ass", ".ssa", ".vtt"]
    
    if languages is None:
        languages = ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"]
    
    # Base video names that might have subtitles
    video_names = [
        "movie", "film", "episode", "documentary", "series",
        "show", "video", "lecture", "presentation", "interview"
    ]
    
    base_name = random.choice(video_names)
    extension = random.choice(extensions)
    language = random.choice(languages)
    
    # Different subtitle naming patterns
    pattern = random.randint(1, 6)
    
    if pattern == 1:
        # name.en.srt
        filename = f"{base_name}.{language}{extension}"
    elif pattern == 2:
        # name_english.srt
        lang_names = {
            "en": "english", "es": "spanish", "fr": "french",
            "de": "german", "it": "italian", "pt": "portuguese",
            "ru": "russian", "zh": "chinese", "ja": "japanese", "ko": "korean"
        }
        lang_name = lang_names.get(language, language)
        filename = f"{base_name}_{lang_name}{extension}"
    elif pattern == 3:
        # name_EN_subtitles.srt
        filename = f"{base_name}_{language.upper()}_subtitles{extension}"
    elif pattern == 4:
        # name.S01E01.en.srt (for series)
        season = random.randint(1, 10)
        episode = random.randint(1, 24)
        filename = f"{base_name}.S{season:02d}E{episode:02d}.{language}{extension}"
    elif pattern == 5:
        # name_2023_en.srt
        year = random.randint(2018, 2024)
        filename = f"{base_name}_{year}_{language}{extension}"
    else:
        # name_subs_en.srt
        filename = f"{base_name}_subs_{language}{extension}"
    
    return filename


def generate_stream_url(
    providers: Optional[List[str]] = None,
    protocols: Optional[List[str]] = None,
    **kwargs
) -> str:
    """
    Generate a realistic streaming URL.
    
    Args:
        providers: List of streaming providers
        protocols: List of streaming protocols
        **kwargs: Additional parameters
    
    Returns:
        A generated streaming URL string
    """
    
    if providers is None:
        providers = ["youtube", "vimeo", "twitch", "dailymotion", "generic"]
    
    if protocols is None:
        protocols = ["http", "https", "rtsp", "rtmp", "mms"]
    
    provider = random.choice(providers)
    
    if provider == "youtube":
        video_ids = [
            "dQw4w9WgXcQ", "9bZkp7q19f0", "kJQP7kiw5Fk",
            "3JZ_D3ELwOQ", "L_jWHffIx5E", "0KSOMA3QBU0"
        ]
        video_id = random.choice(video_ids)
        urls = [
            f"https://www.youtube.com/watch?v={video_id}",
            f"https://youtu.be/{video_id}",
            f"https://youtube.com/v/{video_id}"
        ]
        return random.choice(urls)
    
    elif provider == "vimeo":
        video_id = random.randint(100000000, 999999999)
        return f"https://vimeo.com/{video_id}"
    
    elif provider == "twitch":
        channels = ["gaming", "esports", "music", "creative", "irl"]
        channel = random.choice(channels)
        return f"https://www.twitch.tv/{channel}"
    
    elif provider == "dailymotion":
        video_id = f"x{random.randint(100000, 999999)}"
        return f"https://www.dailymotion.com/video/{video_id}"
    
    else:  # generic stream
        protocol = random.choice(protocols)
        servers = [
            "stream.example.com", "media.server.net", "video.cdn.org",
            "live.broadcast.tv", "content.provider.com"
        ]
        server = random.choice(servers)
        
        if protocol in ["rtsp", "rtmp"]:
            port = random.choice([554, 1935, 8554])
            stream_name = random.choice(["live", "stream", "channel1", "feed"])
            return f"{protocol}://{server}:{port}/{stream_name}"
        elif protocol == "mms":
            return f"mms://{server}/stream"
        else:
            paths = ["stream.m3u8", "live/playlist.m3u8", "video.mp4", "broadcast"]
            path = random.choice(paths)
            return f"{protocol}://{server}/{path}"


# Test the functions if run directly
if __name__ == "__main__":
    print("Testing generate_media_file_path:")
    for _ in range(5):
        print(f"  Video: {generate_media_file_path('video', True)}")
    for _ in range(3):
        print(f"  Audio: {generate_media_file_path('audio', False)}")
    
    print("\nTesting generate_subtitle_filename:")
    for _ in range(5):
        print(f"  {generate_subtitle_filename()}")
    
    print("\nTesting generate_stream_url:")
    for _ in range(5):
        print(f"  {generate_stream_url()}")
