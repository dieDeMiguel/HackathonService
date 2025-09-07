import os
from openai import OpenAI
import qdrant_client
from qdrant_client.models import PointStruct
import uuid
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

COLLECTION_NAME = "HACKATHON_COLLECTION"

# Use environment variables for Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

# Initialize Qdrant client with proper configuration
if qdrant_api_key:
    # Qdrant Cloud with API key
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=qdrant_api_key,
        timeout=30,
        prefer_grpc=False
    )
else:
    # Local Qdrant without API key
    client = QdrantClient(
        url=QDRANT_URL,
        timeout=30,
        prefer_grpc=False
    )

# Don't recreate collection here - let the API endpoint handle it
# client.recreate_collection(
#     collection_name=COLLECTION_NAME,
#     vectors_config=qdrant_client.models.VectorParams(
#         size=1536, distance=qdrant_client.models.Distance.COSINE  # OpenAI text-embedding-3-small
#     ),
# )


def get_lines_from_file(filepath):
    with open(filepath) as file:
        return file.readlines()


def hybrid_chunking(content):
    """
    Chunking híbrido mejorado que mantiene contexto de secciones completas
    Especialmente optimizado para información de grupos y fixtures
    """
    chunks = []
    current_section = ""
    current_title = ""
    current_subsections = []
    
    # Límite de caracteres por chunk (optimizado para embeddings)
    MAX_CHUNK_SIZE = 1200
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#'):
            # Guardar chunk anterior si existe
            if current_section.strip():
                chunk_text = f"{current_title}\n\n{current_section.strip()}"
                
                # Si el chunk es muy largo, dividirlo inteligentemente
                if len(chunk_text) > MAX_CHUNK_SIZE:
                    # Buscar puntos de división naturales para información de grupos
                    if "GROUP" in chunk_text and "**GROUP" in chunk_text:
                        # Dividir por grupos individuales
                        group_sections = chunk_text.split("**GROUP")
                        base_header = group_sections[0]
                        
                        for i, group_section in enumerate(group_sections[1:], 1):
                            if group_section.strip():
                                group_chunk = f"{base_header}\n\n**GROUP{group_section.strip()}"
                                chunks.append({
                                    "text": group_chunk,
                                    "title": f"{current_title.strip('#').strip()} - Group {chr(64+i)}",
                                    "section_type": "group_fixture",
                                    "char_count": len(group_chunk),
                                    "subsections": [f"Group {chr(64+i)} Fixture"],
                                    "chunk_index": len(chunks)
                                })
                    else:
                        # División por subsecciones para otros tipos de contenido largo
                        if current_subsections and len(current_subsections) > 1:
                            subsection_parts = current_section.split('###')
                            if len(subsection_parts) > 1:
                                for j, part in enumerate(subsection_parts[1:], 1):
                                    if part.strip():
                                        subsection_title = current_subsections[j-1] if j-1 < len(current_subsections) else f"Part {j}"
                                        subsection_chunk = f"{current_title}\n\n### {subsection_title}\n{part.strip()}"
                                        chunks.append({
                                            "text": subsection_chunk,
                                            "title": current_title.strip('#').strip(),
                                            "section_type": "content",
                                            "char_count": len(subsection_chunk),
                                            "subsections": [subsection_title],
                                            "chunk_index": len(chunks)
                                        })
                            else:
                                # Si no se puede dividir, mantener como chunk único
                                chunks.append({
                                    "text": chunk_text,
                                    "title": current_title.strip('#').strip(),
                                    "section_type": "content",
                                    "char_count": len(chunk_text),
                                    "subsections": current_subsections.copy(),
                                    "chunk_index": len(chunks)
                                })
                        else:
                            chunks.append({
                                "text": chunk_text,
                                "title": current_title.strip('#').strip(),
                                "section_type": "content",
                                "char_count": len(chunk_text),
                                "subsections": current_subsections.copy(),
                                "chunk_index": len(chunks)
                            })
                else:
                    # Chunk normal si no es muy largo
                    chunks.append({
                        "text": chunk_text,
                        "title": current_title.strip('#').strip(),
                        "section_type": "content",
                        "char_count": len(chunk_text),
                        "subsections": current_subsections.copy(),
                        "chunk_index": len(chunks)
                    })
            
            # Determinar nivel de header
            header_level = len(line) - len(line.lstrip('#'))
            
            # Si es un header principal (## o menos #), iniciar nueva sección
            if header_level <= 2:
                current_title = line
                current_section = ""
                current_subsections = []
            else:
                # Si es subsección (###), agregar a subsecciones
                current_subsections.append(line.strip('#').strip())
                current_section += line + "\n"
        else:
            current_section += line + "\n"
    
    # Guardar último chunk (aplicar la misma lógica)
    if current_section.strip():
        chunk_text = f"{current_title}\n\n{current_section.strip()}"
        
        if len(chunk_text) > MAX_CHUNK_SIZE:
            if "GROUP" in chunk_text and "**GROUP" in chunk_text:
                group_sections = chunk_text.split("**GROUP")
                base_header = group_sections[0]
                
                for i, group_section in enumerate(group_sections[1:], 1):
                    if group_section.strip():
                        group_chunk = f"{base_header}\n\n**GROUP{group_section.strip()}"
                        chunks.append({
                            "text": group_chunk,
                            "title": f"{current_title.strip('#').strip()} - Group {chr(64+i)}",
                            "section_type": "group_fixture",
                            "char_count": len(group_chunk),
                            "subsections": [f"Group {chr(64+i)} Fixture"],
                            "chunk_index": len(chunks)
                        })
            else:
                chunks.append({
                    "text": chunk_text,
                    "title": current_title.strip('#').strip(),
                    "section_type": "content",
                    "char_count": len(chunk_text),
                    "subsections": current_subsections.copy(),
                    "chunk_index": len(chunks)
                })
        else:
            chunks.append({
                "text": chunk_text,
                "title": current_title.strip('#').strip(),
                "section_type": "content",
                "char_count": len(chunk_text),
                "subsections": current_subsections.copy(),
                "chunk_index": len(chunks)
            })
    
    return chunks


def get_content_from_file(filepath):
    """
    Lee el archivo completo como string para chunking híbrido
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()


def embed_sentences(sentences):
    """
    Generate embeddings using OpenAI text-embedding-3-small model
    """
    # Convertir a lista si es una sola cadena
    if isinstance(sentences, str):
        sentences = [sentences]
    
    # Llamar a OpenAI API
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=sentences
    )
    
    # Extraer embeddings
    embeddings = [data.embedding for data in response.data]
    
    # Si solo había una oración, devolver un solo embedding
    if len(embeddings) == 1 and len(sentences) == 1:
        return embeddings[0]
    
    return embeddings


def save_embeddings_to_db(embeddings: list, chunks: list | None = None):
    """
    Uploads embeddings into Qdrant with enriched metadata.

    Args:
        embeddings (list): List of embeddings (each a list/array of floats).
        chunks (list, optional): List of chunk dictionaries with metadata.
    """
    points = []
    for i, vector in enumerate(embeddings):
        # Crear payload enriquecido
        if chunks and i < len(chunks):
            chunk = chunks[i]
            payload = {
                "text": chunk["text"],
                "title": chunk.get("title", ""),
                "section_type": chunk.get("section_type", "content"),
                "char_count": chunk.get("char_count", 0),
                "subsections": chunk.get("subsections", []),
                "source_file": chunk.get("source_file", "unknown"),
                "file_type": chunk.get("file_type", "content"),
                "chunk_index": i
            }
        else:
            payload = {"text": f"Chunk {i}", "chunk_index": i}
        
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),  # generate unique id
                vector=vector,
                payload=payload,
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {len(points)} embeddings to collection '{COLLECTION_NAME}'")
    
    # Mostrar estadísticas de chunks
    if chunks:
        avg_chars = sum(chunk.get("char_count", 0) for chunk in chunks) / len(chunks)
        print(f"📊 Average chunk size: {avg_chars:.0f} characters")
        print(f"📋 Sections processed: {len(set(chunk.get('title', '') for chunk in chunks))}")
