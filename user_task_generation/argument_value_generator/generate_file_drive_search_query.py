import random
from typing import Iterable, Optional, Sequence

def generate_file_drive_search_query(
    use_filters_prob: float = 0.3,
    min_terms: int = 1,
    max_terms: int = 5,
    max_filters: int = 2,
    allowed_filters: Optional[Iterable[str]] = None,
    seed: Optional[int] = None,
) -> str:
    """
    Generate a realistic OneDrive search query.
    Returns strings like:
      - 'invoice'
      - '"meeting notes" type:pdf modified:this week'
      - 'project alpha path:Projects/Project Alpha shared:with me'
    """

    rng = random.Random(seed)

    # Base vocabulary (multi-word tokens included; quoting applied below)
    base_terms: Sequence[str] = [
        "invoice", "contract", "proposal", "budget", "roadmap", "okr",
        "meeting notes", "status report", "timesheet", "travel itinerary",
        "offer letter", "design spec", "resume", "presentation", "slides",
        "diagram", "photos 2025", "expenses", "quarterly report", "NDA", "RFP",
        "org announcement", "sprint backlog", "release notes", "architecture"
    ]

    # Common folders/paths (used in path: filter)
    folder_paths: Sequence[str] = [
        "Finance/Invoices", "Finance/Expenses", "Legal/Contracts",
        "HR/Recruiting", "Work/Reports", "Work/Designs",
        "Projects/Project Alpha", "Projects/Project Beta", "Projects/2025/Quarterly",
        "Shared/Team A", "Shared/Team B", "Photos/2025/Trips", "Meeting Notes"
    ]

    # Filter templates supported by our dataset
    default_filters = {
        "type": ["pdf", "docx", "xlsx", "pptx", "jpg", "png", "zip", "txt"],
        "tag": ["contract", "invoice", "draft", "final", "to-review", "approved"],
        "owner": ["me"],  # avoid PII
        "shared": ["with me"],
        "modified": ["today", "yesterday", "this week", "last week", "this month", "last month"],
        "path": folder_paths,
        # Optional extras — keep realistic/safe for synthetic search
        "ext": ["pdf", "docx", "xlsx", "pptx", "png", "jpg"],
    }

    # Restrict which filter keys can be used (if specified)
    if allowed_filters:
        default_filters = {k: v for k, v in default_filters.items() if k in set(allowed_filters)}

    # 1) Build base terms
    k_terms = rng.randint(max(1, min_terms), max(min_terms, max_terms))
    chosen_terms = rng.sample(base_terms, k=min(k_terms, len(base_terms)))

    def quote_if_needed(t: str) -> str:
        return f'"{t}"' if " " in t else t

    parts = [quote_if_needed(t) for t in chosen_terms]

    # 2) Maybe add filters
    if rng.random() < use_filters_prob and default_filters:
        filt_keys = list(default_filters.keys())
        rng.shuffle(filt_keys)
        n_filters = rng.randint(1, min(max_filters, len(filt_keys)))
        for key in filt_keys[:n_filters]:
            val = rng.choice(default_filters[key])
            # path: needs quoting if it has spaces/slashes
            if key == "path":
                val_str = f'"{val}"' if any(c in val for c in (" ", "/")) else val
                parts.append(f'path:{val_str}')
            elif key in ("type", "ext", "tag", "owner", "shared", "modified"):
                parts.append(f'{key}:{val}')
            # ignore unknown keys silently

    return " ".join(parts)
