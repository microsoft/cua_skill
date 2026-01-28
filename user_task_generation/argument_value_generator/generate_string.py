#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
argument_value_generator.py

Realistic phrase generation for task arguments (names, titles, short phrases).
- Domain-aware lexicons (ppt/excel/word/finance/sales/research/engineering/marketing/design/legal/healthcare/education/gaming/ai/data/security)
- Length and regex constraints
- Naming styles: title/sentence/lower/upper/snake/kebab/camel/pascal
- Optional numeric suffix and minimum-length padding
"""

from __future__ import annotations
import re
import random
from typing import Optional, List, Dict, Iterable

# ----------------------------
# Core word banks (general)
# ----------------------------

_ADJ_BASE = [
    "Creative", "Modern", "Elegant", "Dynamic", "Agile", "Smart", "Global",
    "Strategic", "Reliable", "Efficient", "Bold", "Insightful", "Compact",
    "Minimal", "Express", "Premium", "Rapid", "Secure", "Unified", "Pro",
    "Advanced", "Next", "Essential", "Prime", "Ultra", "Core", "Edge",
    "Portable", "Robust", "Scalable", "Modular"
]

_NOUN_BASE = [
    "Deck", "Plan", "Roadmap", "Overview", "Brief", "Summary", "Proposal",
    "Update", "Report", "Review", "Concept", "Demo", "Showcase", "Outline",
    "Launch", "Metrics", "Analysis", "Vision", "Strategy", "Guide", "Notes",
    "Checklist", "Schedule", "Tracker", "Dashboard"
]

_VERB_BASE = [
    "Launch", "Create", "Design", "Draft", "Build", "Present", "Share",
    "Refine", "Explore", "Highlight", "Summarize", "Compare", "Validate",
    "Compile", "Organize", "Plan"
]

# ----------------------------
# Domain lexicons
# (only alnum/space/underscore friendly tokens to pass default pattern)
# ----------------------------

_NOUN_PPT = [
    "Slide", "Template", "Layout", "Title", "Content", "Transition",
    "Theme", "Presentation", "Storyboard", "Agenda", "Section",
    "Master", "Slide Notes"
]

_NOUN_EXCEL = [
    "Workbook", "Worksheet", "Sheet", "Pivot Table", "Formula", "Chart",
    "Table", "Range", "Macro", "Data Model"
]

_NOUN_WORD = [
    "Document", "Section", "Heading", "Paragraph", "Style", "Template",
    "Footnote", "Caption", "Index", "Table of Contents"
]

_NOUN_FINANCE = [
    "Budget", "Forecast", "Revenue", "Margin", "PnL", "Cashflow", "Ledger",
    "Invoice", "Expense", "ROI", "Projection", "Plan FY", "Quarterly Report"
]

_NOUN_SALES = [
    "Pipeline", "Leads", "Account", "Quota", "Campaign", "Opportunity",
    "Prospect", "Win Rate", "Funnel", "Territory", "Playbook"
]

_NOUN_RESEARCH = [
    "Paper", "Experiment", "Dataset", "Results", "Ablation", "Appendix",
    "Baseline", "Method", "Survey", "Review", "Benchmark", "Protocol"
]

_NOUN_ENGINEERING = [
    "Spec", "Design", "Implementation", "Module", "Service", "API",
    "Client", "Server", "Release", "Changelog", "Backlog", "Sprint"
]

_NOUN_MARKETING = [
    "Campaign", "Brief", "Persona", "Positioning", "Narrative", "Launch",
    "Content", "KPI", "Plan", "Calendar", "Messaging"
]

_NOUN_DESIGN = [
    "Mockup", "Wireframe", "Prototype", "Concept", "Style Guide",
    "Icon Set", "Palette", "Grid", "Component", "Pattern"
]

_NOUN_LEGAL = [
    "Contract", "Agreement", "NDA", "Terms", "Policy", "Compliance",
    "License", "Clause", "Addendum"
]

_NOUN_HEALTHCARE = [
    "Clinical", "Trial", "Cohort", "Patient", "Protocol", "Outcome",
    "Chart", "Note", "Pathway", "Screening"
]

_NOUN_EDUCATION = [
    "Syllabus", "Lecture", "Assignment", "Quiz", "Rubric", "Module",
    "Lesson", "Curriculum"
]

_NOUN_GAMING = [
    "Level", "Quest", "Patch Notes", "Build", "Loadout", "Strategy",
    "Event", "Season"
]

_NOUN_AI = [
    "Model", "Training", "Dataset", "Checkpoint", "Weights", "Latency",
    "Throughput", "Distillation", "LoRA", "Inference", "Benchmark",
    "Metrics", "Prompt", "Evaluator", "Reranker"
]

_NOUN_DATA = [
    "ETL", "Pipeline", "Dashboard", "Warehouse", "Lake", "Metric",
    "Cohort", "Schema", "Catalog", "Snapshot", "Query"
]

_NOUN_SECURITY = [
    "Audit", "Risk", "Threat", "Mitigation", "Incident", "Policy",
    "Access", "Token", "Key", "Control", "Remediation"
]

# Domain-specific adjectives
_ADJ_TIME = ["Q1", "Q2", "Q3", "Q4", "FY2024", "FY2025", "Monthly", "Quarterly", "Weekly"]
_ADJ_BIZ  = ["Executive", "Enterprise", "Team", "Internal", "External"]
_ADJ_TECH = ["Distributed", "Parallel", "On Device", "Serverless", "Cloud", "Edge", "Offline", "Realtime"]

# Topic aliasing (normalize input to a canonical topic)
_TOPIC_ALIASES: Dict[str, str] = {
    "ppt": "powerpoint",
    "powerpoint": "powerpoint",
    "office": "powerpoint",
    "slides": "powerpoint",
    "excel": "excel",
    "word": "word",
    "finance": "finance",
    "sales": "sales",
    "research": "research",
    "eng": "engineering",
    "engineering": "engineering",
    "mkt": "marketing",
    "marketing": "marketing",
    "design": "design",
    "legal": "legal",
    "health": "healthcare",
    "healthcare": "healthcare",
    "edu": "education",
    "education": "education",
    "game": "gaming",
    "gaming": "gaming",
    "ai": "ai",
    "ml": "ai",
    "data": "data",
    "security": "security",
}

# Canonical topic -> extra noun/adjective banks
_TOPIC_BANKS: Dict[str, Dict[str, List[str]]] = {
    "powerpoint": {"noun": _NOUN_PPT, "adj": []},
    "excel": {"noun": _NOUN_EXCEL, "adj": []},
    "word": {"noun": _NOUN_WORD, "adj": []},
    "finance": {"noun": _NOUN_FINANCE, "adj": _ADJ_TIME + _ADJ_BIZ},
    "sales": {"noun": _NOUN_SALES, "adj": _ADJ_TIME + _ADJ_BIZ},
    "research": {"noun": _NOUN_RESEARCH, "adj": _ADJ_TECH + _ADJ_TIME},
    "engineering": {"noun": _NOUN_ENGINEERING, "adj": _ADJ_TECH},
    "marketing": {"noun": _NOUN_MARKETING, "adj": _ADJ_TIME + _ADJ_BIZ},
    "design": {"noun": _NOUN_DESIGN, "adj": []},
    "legal": {"noun": _NOUN_LEGAL, "adj": []},
    "healthcare": {"noun": _NOUN_HEALTHCARE, "adj": []},
    "education": {"noun": _NOUN_EDUCATION, "adj": []},
    "gaming": {"noun": _NOUN_GAMING, "adj": []},
    "ai": {"noun": _NOUN_AI, "adj": _ADJ_TECH},
    "data": {"noun": _NOUN_DATA, "adj": _ADJ_TECH},
    "security": {"noun": _NOUN_SECURITY, "adj": []},
}

_STOPWORDS_TITLECASE_LOWER = {
    "a","an","and","as","at","but","by","for","in","of","on","or","the","to","vs","via"
}

# ----------------------------
# Utilities
# ----------------------------

def _title_case(s: str) -> str:
    words = s.split()
    if not words:
        return s
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i != 0 and lw in _STOPWORDS_TITLECASE_LOWER:
            out.append(lw)
        else:
            out.append(lw.capitalize())
    return " ".join(out)

def _apply_style(text: str, style: str, sep: Optional[str]) -> str:
    style = (style or "title").lower()
    if style == "title":
        return _title_case(text)
    if style == "sentence":
        t = text.strip()
        return t[:1].upper() + t[1:].lower() if t else t
    if style == "lower":
        return text.lower()
    if style == "upper":
        return text.upper()
    words = re.split(r"\s+", text.strip())
    if style == "snake":
        return "_".join(w.lower() for w in words if w)
    if style == "kebab":
        return "-".join(w.lower() for w in words if w)
    if style == "camel":
        parts = [w for w in words if w]
        return (parts[0].lower() + "".join(p.capitalize() for p in parts[1:])) if parts else ""
    if style == "pascal":
        return "".join(w.capitalize() for w in words if w)
    # custom separator override
    if sep is not None:
        return (sep.join(words)).strip(sep)
    return text

def _sanitize_to_pattern(s: str, pattern: str) -> str:
    """
    Best-effort sanitizer: if doesn't match, strip to alnum/_/space (common default).
    """
    if re.fullmatch(pattern, s):
        return s
    s2 = re.sub(r"[^A-Za-z0-9_ ]+", "", s)
    s2 = re.sub(r"\s+", " ", s2).strip()
    if not re.fullmatch(pattern, s2):
        s2 = re.sub(r"[^A-Za-z0-9]+", "", s2)
    return s2

def _canonical_topic(topic: Optional[str]) -> Optional[str]:
    if topic is None:
        return None
    t = str(topic).strip().lower()
    return _TOPIC_ALIASES.get(t, t)

def _topic_adjectives(topic: Optional[str]) -> List[str]:
    t = _canonical_topic(topic)
    if t and t in _TOPIC_BANKS and _TOPIC_BANKS[t]["adj"]:
        return _TOPIC_BANKS[t]["adj"]
    return []

def _topic_nouns(topic: Optional[str]) -> List[str]:
    t = _canonical_topic(topic)
    if t and t in _TOPIC_BANKS and _TOPIC_BANKS[t]["noun"]:
        return _TOPIC_BANKS[t]["noun"]
    return []

def _pick_structure(topic: Optional[str]) -> str:
    """
    Return a phrase template structure key with a slight bias to names.
    """
    roll = random.random()
    if roll < 0.55:
        return "adj_noun"
    if roll < 0.85:
        return "noun_noun"
    return "verb_noun"

def _sample_words(topic: Optional[str]) -> List[str]:
    nouns = _NOUN_BASE + _topic_nouns(topic)
    adjs  = _ADJ_BASE + _topic_adjectives(topic)
    verbs = _VERB_BASE

    structure = _pick_structure(topic)
    if structure == "adj_noun":
        return [random.choice(adjs), random.choice(nouns)]
    if structure == "noun_noun":
        return [random.choice(nouns), random.choice(nouns)]
    # verb_noun
    return [random.choice(verbs), random.choice(nouns)]

# ----------------------------
# Public generator
# ----------------------------

def generate_string(
    max_length: int,
    min_length: int = 0,
    pattern: str = r"[a-zA-Z0-9_ ]+",
    topic: Optional[str] = "powerpoint",
    style: str = "title",
    min_words: int = 2,
    max_words: int = 3,
    separator: Optional[str] = None,
    ensure_min: bool = True,
    allow_number_suffix: bool = True,
    number_suffix_prob: float = 0.15,
    **kwargs
) -> str:
    """
    Generate a realistic short phrase (e.g., names, titles) under constraints.

    Args:
        max_length: Hard cap on length (>= 1).
        min_length: Soft minimum; we try to reach it.
        pattern: Fullmatch regex the result must satisfy.
        topic: Domain hint (e.g., 'ppt','excel','word','finance','sales','research','ai').
        style: 'title'|'sentence'|'lower'|'upper'|'snake'|'kebab'|'camel'|'pascal'
        min_words / max_words: word count range before styling.
        separator: Custom join char; overrides style joiner if provided.
        ensure_min: If below min_length, attempt to pad lightly.
        allow_number_suffix: Optionally add a small numeric suffix (e.g., "2").
        number_suffix_prob: Probability to add that suffix.

    Returns:
        A phrase that fits length + pattern constraints.
    """
    max_length = max(1, int(max_length))
    min_length = max(0, int(min_length))
    assert min_words >= 1 and max_words >= min_words

    for _ in range(24):  # multiple attempts to satisfy constraints
        wc = random.randint(min_words, max_words)
        words: List[str] = []
        while len(words) < wc:
            words.extend(_sample_words(topic))
        words = words[:wc]

        base = " ".join(words)

        if allow_number_suffix and random.random() < number_suffix_prob:
            base = f"{base} {random.randint(2, 9)}"

        text = _apply_style(base, style, separator)

        if len(text) > max_length:
            # drop trailing words to fit
            if separator is None:
                parts = text.split()
                while len(" ".join(parts)) > max_length and len(parts) > 1:
                    parts.pop()
                text = " ".join(parts)
            else:
                parts = re.split(rf"{re.escape(separator)}", text)
                while len(separator.join(parts)) > max_length and len(parts) > 1:
                    parts.pop()
                text = separator.join(parts)
            if len(text) > max_length:
                text = text[:max_length].rstrip(" _-")

        if ensure_min and len(text) < min_length:
            pad_token = "Pro" if style not in {"snake","kebab","camel","pascal"} else "pro"
            candidate = (text + ((separator or " ")) + pad_token).strip()
            if len(candidate) <= max_length:
                text = candidate

        text = _sanitize_to_pattern(text, pattern)
        text = text[:max_length].strip()

        if len(text) >= min_length and re.fullmatch(pattern, text or ""):
            return text

    # Fallback conservative phrase
    fallback = "Project"
    fallback = _apply_style(fallback, style, separator)
    fallback = _sanitize_to_pattern(fallback, pattern)[:max_length].strip()
    if len(fallback) < min_length:
        pad_token = "X" if style not in {"snake","kebab","camel","pascal"} else "x"
        fallback = (fallback + " " + pad_token).strip()[:max_length]
        fallback = _sanitize_to_pattern(fallback, pattern)
    return fallback or "Name"

# ----------------------------
# Registry for your pipeline
# ----------------------------

ARGUMENT_GENERATORS: Dict[str, callable] = {
    "generate_string": generate_string,
}

__all__ = [
    "generate_string",
    "ARGUMENT_GENERATORS",
]

# ----------------------------
# Demo
# ----------------------------
if __name__ == "__main__":
    random.seed(42)

    topics = ["powerpoint", "excel", "word", "finance", "sales", "research",
              "engineering", "marketing", "design", "legal", "healthcare",
              "education", "gaming", "ai", "data", "security"]

    print("=== Title-style examples ===")
    for t in topics:
        print(f"{t:12s} ->", generate_string(24, topic=t, style="title"))

    print("\n=== Snake/kebab/camel/pascal ===")
    print("snake :", generate_string(24, topic="ai", style="snake"))
    print("kebab :", generate_string(24, topic="data", style="kebab"))
    print("camel :", generate_string(24, topic="research", style="camel"))
    print("pascal:", generate_string(24, topic="engineering", style="pascal"))

    print("\n=== Min/Max length and pattern ===")
    print(generate_string(16, min_length=12, topic="sales", style="title"))
    print(generate_string(14, min_length=10, topic="finance", style="title"))
