from pathlib import Path
from ragger.embed import save_embeddings_to_db, get_content_from_file, embed_sentences, hybrid_chunking


CURRENT_DIR = Path(".").resolve()


def main():
    print("🔄 Reading and processing data with hybrid chunking...")
    filepath = CURRENT_DIR / "src" / "ragger" / "test_data.md"
    
    # Leer contenido completo del archivo
    content = get_content_from_file(filepath)
    
    # Aplicar chunking híbrido
    chunks = hybrid_chunking(content)
    
    print(f"📊 Created {len(chunks)} semantic chunks")
    
    # Extraer textos para embeddings
    chunk_texts = [chunk["text"] for chunk in chunks]
    
    print("🤖 Generating OpenAI embeddings...")
    embs = embed_sentences(chunk_texts)
    
    print("💾 Saving to Qdrant with enriched metadata...")
    save_embeddings_to_db(embs, chunks)


if __name__ == "__main__":
    main()
