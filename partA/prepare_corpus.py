from datasets import load_dataset
from pathlib import Path
import csv
import unicodedata

LANGUAGES = {
    "english": "eng_Latn",
    "hindi": "hin_Deva",
    "tamil": "tam_Taml",
    "kannada": "kan_Knda",
}

TARGET_SIZE = 1000
SPLIT = "devtest"
OUTPUT_DIR = Path("partA/data")
OUTPUT_FILE = OUTPUT_DIR / "flores_parallel_1000.csv"

def normalize_text(text: str) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.strip()
    return text

def load_language(language_code: str):
    print(f"Loading {language_code}...")
    dataset = load_dataset("facebook/flores", language_code, split=SPLIT)
    return dataset

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    datasets = {}
    for language_name, language_code in LANGUAGES.items():
        datasets[language_name] = load_language(language_code)

    print("\nChecking alignment...")
    common_ids = None
    for language_name, dataset in datasets.items():
        ids = set(dataset["id"])
        if common_ids is None:
            common_ids = ids
        else:
            common_ids = common_ids.intersection(ids)
    common_ids = sorted(common_ids)
    print(f"Common sentence IDs found: {len(common_ids)}")

    rows = []
    lookups = {}
    for language_name, dataset in datasets.items():
        lookups[language_name] = {row["id"]: row["sentence"] for row in dataset}

    removed_empty = 0
    for sentence_id in common_ids:
        row = {"id": sentence_id}
        valid = True
        for language_name in LANGUAGES:
            text = lookups[language_name][sentence_id]
            text = normalize_text(text)
            if not text:
                valid = False
                break
            row[language_name] = text
        if valid:
            rows.append(row)
        else:
            removed_empty += 1
        if len(rows) == TARGET_SIZE:
            break

    if len(rows) < TARGET_SIZE:
        raise RuntimeError(f"Only {len(rows)} valid parallel sentences found. Target was {TARGET_SIZE}.")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["id", "english", "hindi", "tamil", "kannada"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print("\n" + "=" * 60)
    print("CORPUS CONSTRUCTION COMPLETE")
    print("=" * 60)
    print(f"English sentences: {len(rows)}")
    print(f"Hindi sentences: {len(rows)}")
    print(f"Tamil sentences: {len(rows)}")
    print(f"Kannada sentences: {len(rows)}")
    print(f"\nParallel sentence IDs retained: {len(rows)}")
    print(f"Empty/invalid rows removed: {removed_empty}")
    print("Unicode normalization: NFC")
    print(f"\nOutput file:")
    print(OUTPUT_FILE.resolve())

if __name__ == "__main__":
    main()