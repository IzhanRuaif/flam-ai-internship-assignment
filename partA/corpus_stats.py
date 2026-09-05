import pandas as pd
from pathlib import Path

INPUT_FILE = Path("partA/data/flores_parallel_1000.csv")

def main():
    df = pd.read_csv(INPUT_FILE)
    languages = ["english", "hindi", "tamil", "kannada"]

    print("\nCORPUS STATISTICS")
    print("=" * 60)
    print(f"Parallel sentences: {len(df)}")

    for language in languages:
        sentences = df[language].astype(str)
        char_counts = sentences.str.len()
        word_counts = sentences.apply(lambda x: len(x.split()))

        print(f"\n{language.upper()}")
        print(f"Average characters/sentence: {char_counts.mean():.2f}")
        print(f"Average whitespace words/sentence: {word_counts.mean():.2f}")
        print(f"Min characters: {char_counts.min()}")
        print(f"Max characters: {char_counts.max()}")

if __name__ == "__main__":
    main()