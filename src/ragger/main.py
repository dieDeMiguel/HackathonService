from pathlib import Path
from ragger.embed import save_embeddings_to_db, get_content_from_file, embed_sentences, hybrid_chunking


CURRENT_DIR = Path(".").resolve()


def main():
    print("🔄 Reading and processing multiple data sources with hybrid chunking...")
    
    # Lista de archivos a procesar
    data_files = [
        CURRENT_DIR / "src" / "ragger" / "test_data.md",
        CURRENT_DIR / "src" / "ragger" / "system_prompt_data.md"
    ]
    
    all_chunks = []
    
    # Procesar cada archivo
    for filepath in data_files:
        if filepath.exists():
            print(f"📖 Processing: {filepath.name}")
            
            # Leer contenido completo del archivo
            content = get_content_from_file(filepath)
            
            # Aplicar chunking híbrido
            file_chunks = hybrid_chunking(content, "system_knowledge")
            
            # Agregar metadata del archivo fuente
            for chunk in file_chunks:
                chunk["source_file"] = filepath.name
                chunk["file_type"] = "ticket_sales" if "test_data" in filepath.name else "system_knowledge"
            
            all_chunks.extend(file_chunks)
            print(f"  ✅ Created {len(file_chunks)} chunks from {filepath.name}")
        else:
            print(f"  ⚠️  File not found: {filepath.name}")
    
    print(f"📊 Total semantic chunks created: {len(all_chunks)}")
    
    # Extraer textos para embeddings
    chunk_texts = [chunk["text"] for chunk in all_chunks]
    
    print("🤖 Generating OpenAI embeddings...")
    embs = embed_sentences(chunk_texts)
    
    print("💾 Saving to Qdrant with enriched metadata...")
    save_embeddings_to_db(embs, all_chunks)


if __name__ == "__main__":
    main()
