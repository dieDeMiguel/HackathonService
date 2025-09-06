from pathlib import Path
from ragger.embed import save_embeddings_to_db, get_lines_from_file, embed_sentences


CURRENT_DIR = Path(".").resolve()


def main():
    print("Reading data")
    filepath = CURRENT_DIR / "src" / "ragger" / "test_data.md"
    lines = get_lines_from_file(filepath)
    embs = embed_sentences(lines)
    save_embeddings_to_db(embs)


if __name__ == "__main__":
    main()
