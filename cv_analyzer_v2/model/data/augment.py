import json
import random
import string
from pathlib import Path
from collections import defaultdict, Counter

random.seed(42)

TRAIN_PATH = Path(__file__).parent / "processed" / "train_data.json"
OUT_PATH   = Path(__file__).parent / "processed" / "train_data_augmented.json"

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "IBM",
    "Accenture", "Infosys", "Wipro", "TCS", "Cognizant",
    "Capgemini", "Salesforce", "Adobe", "HCL", "Deloitte",
]
LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Pune",
    "Hyderabad", "Kolkata", "Cairo", "Dubai", "London",
    "New York", "Singapore", "Toronto", "Berlin",
]
DEGREES = [
    "B.Tech", "B.E.", "B.Sc", "M.Tech", "M.Sc", "MBA",
    "Bachelor of Engineering", "Master of Science",
    "Bachelor of Technology", "Master of Computer Applications",
]
DESIGNATIONS = [
    "Software Engineer", "Senior Developer", "Data Analyst",
    "Machine Learning Engineer", "DevOps Engineer",
    "Full Stack Developer", "Backend Developer",
    "Cloud Architect", "QA Engineer", "System Administrator",
]
YEARS       = [str(y) for y in range(2010, 2024)]
EXP_PHRASES = [
    "{n} years", "{n}.5 years", "{n} years of experience",
    "over {n} years", "{n}+ years",
]

STRATEGIES = [
    ("COMPANIES_WORKED_AT", COMPANIES,    50),
    ("LOCATION",            LOCATIONS,    40),
    ("DEGREE",              DEGREES,      40),
    ("DESIGNATION",         DESIGNATIONS, 40),
    ("GRADUATION_YEAR",     YEARS,        30),
    ("YEARS_OF_EXPERIENCE", EXP_PHRASES,  70),
]


def replace_entity(text, entities, target_label, replacement):
    targets = [(s, e, l) for s, e, l in entities if l == target_label]
    if not targets:
        return None, None

    s, e, lbl = random.choice(targets)
    new_text   = text[:s] + replacement + text[e:]
    offset     = len(replacement) - (e - s)
    new_ents   = []

    for es, ee, el in entities:
        if es == s and el == lbl:
            new_ents.append((s, s + len(replacement), el))
        elif es >= e:
            new_ents.append((es + offset, ee + offset, el))
        elif ee <= s:
            new_ents.append((es, ee, el))

    return new_text, new_ents


def is_valid(text, entities):
    for s, e, _ in entities:
        if s >= e or s < 0 or e > len(text):
            return False
        span = text[s:e]
        if span != span.strip():
            return False
        if span and span[0] in string.punctuation:
            return False
    spans = sorted(entities, key=lambda x: x[0])
    for i in range(len(spans) - 1):
        if spans[i][1] > spans[i + 1][0]:
            return False
    return True


def augment_dataset(train_data):
    augmented = list(train_data)

    label_to_items = defaultdict(list)
    for item in train_data:
        for _, _, l in item["entities"]:
            label_to_items[l].append(item)

    for label, pool, n_to_add in STRATEGIES:
        items     = label_to_items[label]
        generated = 0
        attempts  = 0

        while generated < n_to_add and attempts < n_to_add * 5:
            attempts += 1
            source = random.choice(items)

            if label == "YEARS_OF_EXPERIENCE":
                n    = random.randint(1, 10)
                repl = random.choice(pool).format(n=n)
            else:
                repl = random.choice(pool)

            nt, ns = replace_entity(
                source["text"],
                [(s, e, l) for s, e, l in source["entities"]],
                label, repl
            )
            if nt and is_valid(nt, ns):
                augmented.append({
                    "text":     nt,
                    "entities": [[s, e, l] for s, e, l in ns]
                })
                generated += 1

    random.shuffle(augmented)
    return augmented


if __name__ == "__main__":
    train_data = json.loads(TRAIN_PATH.read_text(encoding="utf-8"))
    augmented  = augment_dataset(train_data)

    print(f"Original : {len(train_data)} resumes")
    print(f"Augmented: {len(augmented)} resumes")

    orig_counts = Counter(l for item in train_data  for _, _, l in item["entities"])
    aug_counts  = Counter(l for item in augmented   for _, _, l in item["entities"])

    print("\nLabel distribution:")
    for lbl, cnt in aug_counts.most_common():
        print(f"  {lbl:<25}: {orig_counts[lbl]:>4} → {cnt:>4}")

    OUT_PATH.write_text(json.dumps(augmented, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved to: {OUT_PATH}")
