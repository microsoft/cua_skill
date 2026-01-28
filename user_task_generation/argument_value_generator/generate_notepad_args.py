import random
from typing import List, Dict, Any, Optional

def generate_filename(
    extensions: Optional[List[str]] = None,
    prefixes: Optional[List[str]] = None,
    **kwargs
) -> str:
    """
    Generate a realistic filename for Notepad files.
    
    Args:
        extensions: List of file extensions to choose from
        prefixes: List of prefixes/base names for the file
        **kwargs: Additional parameters for future extensibility
    
    Returns:
        A generated filename string
    """
    
    if extensions is None:
        extensions = [".txt", ".md", ".log", ".ini", ".cfg", ".json", ".xml", ".csv"]
    
    if prefixes is None:
        prefixes = [
            "document", "notes", "todo", "meeting", "project", "ideas", "draft",
            "report", "summary", "readme", "config", "settings", "output", "data",
            "backup", "log", "memo", "minutes", "agenda", "plan", "list", "schedule"
        ]
    
    # Additional descriptors
    descriptors = [
        "new", "old", "final", "temp", "tmp", "latest", "updated", "revised",
        "backup", "copy", "draft", "v1", "v2", "v3", "test", "sample"
    ]
    
    # Date patterns
    dates = [
        f"{random.randint(2020, 2024)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}",
        f"{random.randint(1, 12):02d}{random.randint(1, 28):02d}",
        f"{random.randint(2020, 2024)}"
    ]
    
    prefix = random.choice(prefixes)
    extension = random.choice(extensions)
    
    # Different naming patterns
    pattern = random.randint(1, 8)
    
    if pattern == 1:
        # Simple: prefix.ext
        filename = f"{prefix}{extension}"
    elif pattern == 2:
        # With number: prefix_01.ext
        number = random.randint(1, 99)
        filename = f"{prefix}_{number:02d}{extension}"
    elif pattern == 3:
        # With descriptor: prefix_descriptor.ext
        descriptor = random.choice(descriptors)
        filename = f"{prefix}_{descriptor}{extension}"
    elif pattern == 4:
        # With date: prefix_20240101.ext
        date = random.choice(dates)
        filename = f"{prefix}_{date}{extension}"
    elif pattern == 5:
        # Descriptor + prefix: descriptor_prefix.ext
        descriptor = random.choice(descriptors)
        filename = f"{descriptor}_{prefix}{extension}"
    elif pattern == 6:
        # With multiple parts: prefix_descriptor_01.ext
        descriptor = random.choice(descriptors)
        number = random.randint(1, 99)
        filename = f"{prefix}_{descriptor}_{number}{extension}"
    elif pattern == 7:
        # Uppercase variant
        filename = f"{prefix.upper()}{extension}"
    else:
        # With underscore separator and number
        filename = f"{prefix}{random.randint(1, 999)}{extension}"
    
    return filename


def generate_text_content(
    content_type: str = "general",
    min_length: int = 5,
    max_length: int = 100,
    **kwargs
) -> str:
    """
    Generate text content for typing into Notepad.
    
    Args:
        content_type: Type of content - "general", "code", "list", "sentence", "paragraph"
        min_length: Minimum length of generated text
        max_length: Maximum length of generated text
        **kwargs: Additional parameters
    
    Returns:
        Generated text content string
    """
    
    if content_type == "general":
        templates = [
            "This is a sample text document.",
            "Hello, this is a test.",
            "Important notes for the meeting.",
            "Quick reminder: check the status.",
            "Project notes and updates.",
            "To-do list for today.",
            "Meeting minutes from last session.",
            "Summary of key points.",
            "Draft version of the document.",
            "Configuration settings and parameters.",
            "Log entry for system monitoring.",
            "User feedback and comments.",
            "Research findings and observations.",
            "Action items and next steps.",
            "Review comments and suggestions.",
            "Technical specifications and requirements.",
            "Documentation updates needed.",
            "Ideas for improvement.",
            "Contact information and details.",
            "Reference materials and links."
        ]
        return random.choice(templates)
    
    elif content_type == "code":
        code_snippets = [
            "def hello_world():\n    print('Hello, World!')",
            "for i in range(10):\n    print(i)",
            "import os\nimport sys",
            "class MyClass:\n    def __init__(self):\n        pass",
            "if __name__ == '__main__':\n    main()",
            "try:\n    # code here\nexcept Exception as e:\n    print(e)",
            "def process_data(data):\n    return data.strip()",
            "const getData = async () => {\n  return await fetch(url);\n}",
            "function calculateTotal(items) {\n  return items.reduce((a, b) => a + b);\n}",
            "SELECT * FROM users WHERE active = 1;"
        ]
        return random.choice(code_snippets)
    
    elif content_type == "list":
        items = [
            "First item\nSecond item\nThird item",
            "- Task one\n- Task two\n- Task three",
            "1. Step one\n2. Step two\n3. Step three",
            "TODO: Review document\nTODO: Update code\nTODO: Test changes",
            "Buy groceries\nPay bills\nCall dentist",
            "Monday: Meeting\nTuesday: Review\nWednesday: Presentation",
            "Project A - In Progress\nProject B - Complete\nProject C - Not Started"
        ]
        return random.choice(items)
    
    elif content_type == "sentence":
        sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "A journey of a thousand miles begins with a single step.",
            "All that glitters is not gold.",
            "Actions speak louder than words.",
            "Better late than never.",
            "Every cloud has a silver lining.",
            "Practice makes perfect.",
            "Time is money.",
            "Knowledge is power.",
            "Fortune favors the bold."
        ]
        return random.choice(sentences)
    
    elif content_type == "paragraph":
        paragraphs = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "In today's digital age, technology has transformed the way we work and communicate. Remote collaboration tools have become essential.",
            "The project is progressing well with most milestones achieved. The team has shown great dedication and collaborative spirit.",
            "After careful analysis of the data, we can conclude that the implementation was successful and met all the requirements.",
            "This document contains important information regarding the upcoming changes. Please review carefully and provide feedback.",
            "The meeting was productive and covered all agenda items. Action items have been assigned to respective team members.",
            "Research indicates that regular breaks and proper time management lead to increased productivity and better work-life balance.",
            "Customer feedback has been overwhelmingly positive. The new features have significantly improved user experience."
        ]
        return random.choice(paragraphs)
    
    else:
        # Default to general
        return "Sample text content."


def generate_list_items(
    list_type: str = "bullet",
    item_count: int = 3,
    content_type: str = "general",
    **kwargs
) -> list:
    """
    Generate list items for Notepad insertion.
    
    Args:
        list_type: Type of list - "bullet", "numbered", "checkbox"
        item_count: Number of items to generate
        content_type: Type of content for items - "general", "tasks", "steps", "topics"
        **kwargs: Additional parameters
    
    Returns:
        List containing formatted list items
    """
    
    if content_type == "general":
        items_pool = [
            "First item", "Second item", "Third item", "Fourth item", "Fifth item",
            "Important point", "Key information", "Main topic", "Critical detail",
            "Essential element", "Core component", "Primary focus", "Major aspect"
        ]
    elif content_type == "tasks":
        items_pool = [
            "Review documents", "Update spreadsheet", "Send email", "Schedule meeting",
            "Complete report", "Check status", "Follow up", "Submit request",
            "Verify data", "Test feature", "Fix bug", "Deploy changes",
            "Create backup", "Update configuration", "Review code"
        ]
    elif content_type == "steps":
        items_pool = [
            "Open the application", "Navigate to settings", "Select the option",
            "Enter the information", "Click the button", "Verify the result",
            "Save the changes", "Close the window", "Restart the service",
            "Check the logs", "Test the functionality", "Confirm the update"
        ]
    elif content_type == "topics":
        items_pool = [
            "Introduction", "Background", "Methodology", "Results", "Discussion",
            "Conclusion", "References", "Appendix", "Summary", "Overview",
            "Analysis", "Recommendations", "Future work", "Limitations"
        ]
    else:
        items_pool = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    
    # Randomly select items
    selected_items = random.sample(items_pool, min(item_count, len(items_pool)))
    
    # Format based on list type and return as list
    if list_type == "bullet":
        return [f"- {item}" for item in selected_items]
    elif list_type == "numbered":
        return [f"{i+1}. {item}" for i, item in enumerate(selected_items)]
    elif list_type == "checkbox":
        return [f"[ ] {item}" for item in selected_items]
    else:
        return selected_items


def generate_url(
    include_protocol: bool = True,
    domains: Optional[List[str]] = None,
    **kwargs
) -> str:
    """
    Generate a URL for link insertion.
    
    Args:
        include_protocol: Whether to include http/https protocol
        domains: List of domains to choose from
        **kwargs: Additional parameters
    
    Returns:
        Generated URL string
    """
    
    if domains is None:
        domains = [
            "example.com", "github.com", "microsoft.com", "google.com",
            "stackoverflow.com", "docs.microsoft.com", "w3schools.com",
            "developer.mozilla.org", "openai.com", "python.org",
            "wikipedia.org", "reddit.com", "medium.com", "dev.to"
        ]
    
    protocols = ["http://", "https://"]
    
    domain = random.choice(domains)
    
    # Sometimes add path
    if random.random() < 0.5:
        paths = [
            "docs", "about", "contact", "products", "services",
            "blog", "news", "support", "help", "faq",
            "api", "documentation", "tutorial", "guide"
        ]
        path = random.choice(paths)
        url = f"{domain}/{path}"
    else:
        url = domain
    
    if include_protocol:
        protocol = random.choice(protocols)
        url = f"{protocol}{url}"
    
    return url


def generate_file_path(
    base_paths: Optional[List[str]] = None,
    extensions: Optional[List[str]] = None,
    file_names: Optional[List[str]] = None,
    **kwargs
) -> str:
    """
    Generate a file path for opening files.
    
    Args:
        base_paths: List of base directory paths
        extensions: List of file extensions
        file_names: List of file names to choose from
        **kwargs: Additional parameters
    
    Returns:
        Generated file path string
    """
    
    if base_paths is None:
        base_paths = [
            "C:\\Users\\Documents",
            "C:\\Users\\Desktop",
            "C:\\Users\\Downloads",
            "C:\\temp",
            "D:\\documents",
            "C:\\Users\\Public\\Documents"
        ]
    
    if extensions is None:
        extensions = [".txt", ".md", ".log", ".ini", ".cfg", ".json", ".xml"]
    
    if file_names is None:
        file_names = [
            "document", "notes", "readme", "todo", "file", "log",
            "config", "settings", "manual", "guide", "instructions",
            "data", "output", "report", "summary", "memo"
        ]
    
    base_path = random.choice(base_paths)
    file_name = random.choice(file_names)
    extension = random.choice(extensions)
    
    # Sometimes add number to filename
    if random.random() < 0.4:
        file_name = f"{file_name}_{random.randint(1, 99):02d}"
    
    # Sometimes add subdirectory
    if random.random() < 0.3:
        subdirs = ["work", "personal", "projects", "archive", "backup", "temp"]
        subdir = random.choice(subdirs)
        return f"{base_path}\\{subdir}\\{file_name}{extension}"
    
    return f"{base_path}\\{file_name}{extension}"


# Test the functions if run directly
if __name__ == "__main__":
    print("Testing generate_filename:")
    for _ in range(5):
        print(f"  {generate_filename()}")
    
    print("\nTesting generate_text_content:")
    print(f"  General: {generate_text_content('general')}")
    print(f"  Code: {generate_text_content('code')}")
    print(f"  List: {generate_text_content('list')}")
    
    print("\nTesting generate_list_items:")
    print("  Bullet list:")
    print(generate_list_items('bullet', 3, 'tasks'))
    print("\n  Numbered list:")
    print(generate_list_items('numbered', 3, 'steps'))
    
    print("\nTesting generate_url:")
    for _ in range(3):
        print(f"  {generate_url()}")
    
    print("\nTesting generate_file_path:")
    for _ in range(5):
        print(f"  {generate_file_path()}")