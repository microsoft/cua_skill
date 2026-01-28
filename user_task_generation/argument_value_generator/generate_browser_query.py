import random, datetime

def generate_browser_query(
    mode: str = "web",
    language: str = "English",
    allow_operators: bool = True,
    min_terms: int = 2,
    max_terms: int = 7,
    seed: int | None = None,
) -> str:
    """
    Generate a realistic Bing query string.
    `mode` in {"web","images","videos","news"} controls templates & vocab.
    """

    rng = random.Random(seed)
    year = datetime.date.today().year

    # Core topic pools (broad + deep)
    companies = ["Microsoft","Apple","Google","NVIDIA","Amazon","Meta","Tesla","OpenAI","AMD","Intel"]
    tech = ["AI","machine learning","Python","Docker","Kubernetes","PostgreSQL","Rust","TypeScript","React","LLM"]
    consumer = ["best laptops","noise cancelling headphones","4K monitor","espresso machine","air purifier","robot vacuum"]
    howto = ["how to speed up PC","how to reset router","how to make iced coffee","how to file taxes","how to change a tire"]
    travel = ["Japan travel tips","things to do in Paris","NYC restaurants","cheap flights to London","EWR to SFO"]
    health = ["intermittent fasting","vitamin D benefits","flu symptoms","best running plan","sleep hygiene"]
    edu = ["calculus derivative rules","photosynthesis steps","entropy definition","neural network backprop"]
    finance = ["mortgage rates", "ETF vs mutual fund", "how to buy treasury bills", "NVDA earnings", "AAPL guidance"]
    sports = ["NBA standings", "FIFA highlights", "Marathon training", "Premier League table"]
    culture = ["top Netflix shows", "Oscar predictions", "best podcasts", "book recommendations"]

    # Media-specific pools
    img_styles = ["wallpaper 4k", "logo ideas", "UI inspiration", "minimalist poster", "isometric", "flat design", "infographic"]
    vid_styles = ["tutorial", "walkthrough", "review", "compilation", "lecture", "keynote", "unboxing"]
    news_hooks = ["earnings", "acquires", "IPO", "regulation", "antitrust", "outage", "security breach", "partnership", "layoffs"]

    # Helper to maybe add operators
    def maybe_ops(q: str) -> str:
        if not allow_operators or rng.random() < 0.75:
            return q
        op = rng.choice(["site:", "filetype:", "intitle:", "after:", "before:"])
        if op in ("site:"):
            domain = rng.choice(["microsoft.com","github.com","arxiv.org","nytimes.com","wikipedia.org","reddit.com"])
            return f'{q} site:{domain}'
        if op == "filetype:":
            ext = rng.choice(["pdf","pptx","docx","xlsx"])
            return f'{q} filetype:{ext}'
        if op == "intitle:":
            kw = rng.choice(["guide","cheatsheet","reference","best","tutorial"])
            return f'{q} intitle:{kw}'
        if op == "after:":
            return f'{q} after:{year-1}-01-01'
        if op == "before:":
            return f'{q} before:{year}-01-01'
        return q

    # Build a topic seed
    seed_pool = companies + tech + consumer + howto + travel + health + edu + finance + sports + culture
    topic = rng.choice(seed_pool)

    # Mode-specific templates
    if mode == "images":
        tmpl = rng.choice([
            "{topic} {style}",
            "{topic} aesthetic",
            "photos of {topic}",
            "{topic} reference images",
            "{topic} texture pack",
            "{topic} moodboard",
        ])
        style = rng.choice(img_styles)
        q = tmpl.format(topic=topic, style=style)

    elif mode == "videos":
        tmpl = rng.choice([
            "{topic} {style}",
            "{topic} full {style}",
            "{topic} {style} {year}",
            "best {topic} {style}",
        ])
        style = rng.choice(vid_styles)
        q = tmpl.format(topic=topic, style=style, year=year)

    elif mode == "news":
        hook = rng.choice(news_hooks)
        tmpl = rng.choice([
            "{company} {hook} {year}",
            "latest {company} {hook}",
            "{hook} {company}",
            "{company} {hook} analysis",
        ])
        q = tmpl.format(company=rng.choice(companies), hook=hook, year=year)

    else:  # "web"
        web_tmps = [
            "{topic}",
            "what is {topic}",
            "best {topic} {year}",
            "how to {verb} {obj}",
            "{topic} vs {alt}",
            "top 10 {topic}",
            "{topic} guide",
            "{topic} near me",
        ]
        verbs = ["install","optimize","learn","compare","choose","cook","plan","fix","secure","deploy"]
        objs  = ["docker","resume","travel itinerary","python env","wifi","home server","budget","laptop","monitor"]
        alt   = rng.choice(companies + tech + consumer).split()[0]
        tmpl = rng.choice(web_tmps)
        q = tmpl.format(
            topic=topic,
            year=year,
            verb=rng.choice(verbs),
            obj=rng.choice(objs),
            alt=alt
        )

    # Length shaping (approx by adding/removing terms)
    # If too short, append qualifier; if too long, trim last word
    qualifiers = ["beginner", "advanced", "2025", "tips", "best practices", "examples", "step by step"]
    words = q.split()
    if len(words) < min_terms and rng.random() < 0.7:
        words += rng.sample(qualifiers, k=min(min_terms - len(words), len(qualifiers)))
    while len(words) > max_terms and len(words) > min_terms:
        words.pop()
    q = " ".join(words)

    return maybe_ops(q)
