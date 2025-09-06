from pathlib import Path
from ragger.embed import save_embeddings_to_db, get_lines_from_file, embed_sentences


CURRENT_DIR = Path(".").resolve()


def main():
    print("Reading data")
    filepath = CURRENT_DIR / "src" / "ragger" / "test_data.md"
    lines = get_lines_from_file(filepath)
    
    # Filtrar líneas vacías y limpiar
    clean_lines = [line.strip() for line in lines if line.strip()]
    
    print(f"Processing {len(clean_lines)} lines")
    embs = embed_sentences(clean_lines)
    
    # Crear payloads con el texto
    payloads = [{"text": line.strip()} for line in clean_lines]
    
    save_embeddings_to_db(embs, payloads)


if __name__ == "__main__":
    main()
