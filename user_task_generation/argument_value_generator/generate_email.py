import random, re
from typing import Optional, Sequence

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

FIRST = ["alex","sam","jordan","morgan","taylor","jamie","casey","riley","chris","kelly","drew","avery","bailey","charlie","devon","hayden"]
LAST = ["lee","kim","chen","garcia","patel","nguyen","martinez","rodriguez","johnson","williams","brown","davis","wilson","thomas","moore","clark"]
ROLES = ["info","support","sales","billing","admin","hr","legal","ops","team","security","research","faculty"]
DEPTS = ["eng","it","finance","ops","marketing","legal","hr","cs","ee","bio"]

# Realistic organizations and schools
ORG_COMPANIES = [
    "contoso", "fabrikam", "northwind", "adatum", "globex", "initech", "cyberdyne",
    "umbrella", "soylent", "acme", "starkindustries", "wayneenterprises", "blackmesa",
    "megacorp", "omnicorp", "hooli", "massive", "blueorigin", "openai", "microsoft",
    "amazon", "google", "nvidia", "deepmind"
]
ORG_SCHOOLS = [
    "mit", "stanford", "harvard", "berkeley", "oxford", "cambridge", "caltech",
    "princeton", "yale", "columbia", "cornell", "ucla", "usc", "cmu", "ethz", "tsinghua",
    "pku", "ntu", "nthu", "tokyo"
]
ORG_PUBLIC = ["nasa", "noaa", "who", "unesco", "doe", "nih", "epa"]

def generate_email(
    max_length: int = 40,
    min_length: int = 6,
    organization: Optional[str] = None,
    domains: Optional[Sequence[str]] = None,
    seed: Optional[int] = None,
) -> str:
    """Generate a realistic email address (corporate, academic, or public)."""
    rng = random.Random(seed)

    # --- Domain selection ---
    if domains:
        pool = list(dict.fromkeys(d.lower() for d in domains))
    else:
        org_type = rng.choices(["company", "school", "public"], weights=[0.65, 0.25, 0.10])[0]
        if organization:
            base = re.sub(r"[^a-z0-9\-]", "", organization.lower())
        else:
            base = rng.choice(ORG_COMPANIES if org_type == "company"
                              else ORG_SCHOOLS if org_type == "school"
                              else ORG_PUBLIC)

        tlds = ["com","io","ai","co","edu"] if org_type != "public" else ["gov","org"]
        pool = [f"{base}.{t}" for t in tlds]
        if org_type == "school":
            pool += [f"{d}.{base}.edu" for d in rng.sample(DEPTS, k=min(2, len(DEPTS)))]
        elif org_type == "company":
            pool += [f"{d}.{base}.com" for d in rng.sample(DEPTS, k=min(3, len(DEPTS)))]
        elif org_type == "public":
            pool += [f"{d}.{base}.gov" for d in rng.sample(DEPTS, k=min(2, len(DEPTS)))]

        pool += ["outlook.com", "gmail.com", "yahoo.com"]
        pool = list(dict.fromkeys(pool))

    # --- Local part generation ---
    if rng.random() < 0.15:
        local = rng.choice(ROLES)
    else:
        f, l = rng.choice(FIRST), rng.choice(LAST)
        sep = rng.choice([".", "_", "-", ""])
        local = rng.choice([f"{f}{sep}{l}", f"{f[0]}{sep}{l}", f"{l}{sep}{f}"])
        if rng.random() < 0.2:
            local += str(rng.randint(1, 9999))
        if rng.random() < 0.1:
            local += "+" + rng.choice(["news","alerts","lab","project","ta","student","backup"])

    domain = rng.choice(pool)
    email = f"{local}@{domain}".lower()

    # --- Adjust length and validate ---
    if len(email) > max_length:
        email = f"{local[:max(3, max_length-len(domain)-1)]}@{domain}".lower()
    while len(email) < min_length:
        email = email.replace("@", str(rng.randint(0,9)) + "@", 1)

    if not EMAIL_RE.match(email):
        email = f"info@{pool[0] if pool else 'example.com'}"

    return email
