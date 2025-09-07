from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import qdrant_client
from qdrant_client import QdrantClient
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Search API", version="1.0.0")

# Configuración
COLLECTION_NAME = "HACKATHON_COLLECTION"
# Use Railway internal URL if available, fallback to localhost for local development
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Inicializar clientes
client = QdrantClient(url=QDRANT_URL)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    score_threshold: Optional[float] = 0.3

class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict = {}

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int

@app.get("/")
def read_root():
    return {"message": "RAG Search API is running", "status": "ok"}

@app.get("/health")
def health_check():
    try:
        # Verificar conexión a Qdrant
        collection_info = client.get_collection(COLLECTION_NAME)
        return {
            "status": "healthy",
            "qdrant_connection": "ok",
            "collection_status": collection_info.status,
            "points_count": collection_info.points_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    try:
        logger.info(f"Searching for: {request.query}")
        
        # Generar embedding para la consulta usando OpenAI
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=[request.query]
        )
        query_vector = response.data[0].embedding
        
        # Buscar en Qdrant
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=request.limit,
            score_threshold=request.score_threshold,
            with_payload=True
        )
        
        # Formatear resultados
        results = []
        for hit in search_result:
            # Extraer texto del payload
            text = hit.payload.get("text", "No content available")
            
            result = SearchResult(
                id=str(hit.id),
                text=text,
                score=hit.score,
                metadata=hit.payload
            )
            results.append(result)
        
        logger.info(f"Found {len(results)} results")
        
        return SearchResponse(
            results=results,
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/collection/info")
def get_collection_info():
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        return {
            "collection_name": COLLECTION_NAME,
            "status": collection_info.status,
            "points_count": collection_info.points_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count,
            "config": collection_info.config.dict()
        }
    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")

@app.post("/populate")
def populate_collection():
    """Populate the Qdrant collection with embeddings from the data files"""
    try:
        from pathlib import Path
        from ragger.embed import save_embeddings_to_db, get_content_from_file, embed_sentences, hybrid_chunking
        
        logger.info("Starting to populate Qdrant collection...")
        
        # Create collection if it doesn't exist
        try:
            client.get_collection(COLLECTION_NAME)
            logger.info(f"Collection {COLLECTION_NAME} already exists")
        except Exception:
            logger.info(f"Creating collection {COLLECTION_NAME}")
            import qdrant_client
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qdrant_client.models.VectorParams(
                    size=1536, distance=qdrant_client.models.Distance.COSINE
                ),
            )
        
        # Process data files
        current_dir = Path("/app")  # Railway container path
        data_files = [
            current_dir / "src" / "ragger" / "test_data.md",
            current_dir / "src" / "ragger" / "system_prompt_data.md"
        ]
        
        all_chunks = []
        
        for filepath in data_files:
            if filepath.exists():
                logger.info(f"Processing: {filepath.name}")
                content = get_content_from_file(filepath)
                file_chunks = hybrid_chunking(content)
                
                for chunk in file_chunks:
                    chunk["source_file"] = filepath.name
                    chunk["file_type"] = "ticket_sales" if "test_data" in filepath.name else "system_knowledge"
                
                all_chunks.extend(file_chunks)
                logger.info(f"Created {len(file_chunks)} chunks from {filepath.name}")
            else:
                logger.warning(f"File not found: {filepath}")
        
        if not all_chunks:
            raise HTTPException(status_code=404, detail="No data files found to process")
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        
        # Generate embeddings
        chunk_texts = [chunk["text"] for chunk in all_chunks]
        logger.info("Generating OpenAI embeddings...")
        embs = embed_sentences(chunk_texts)
        
        # Save to Qdrant
        logger.info("Saving to Qdrant...")
        save_embeddings_to_db(embs, all_chunks)
        
        return {
            "status": "success",
            "message": f"Successfully populated collection with {len(all_chunks)} chunks",
            "chunks_processed": len(all_chunks),
            "files_processed": [f.name for f in data_files if f.exists()]
        }
        
    except Exception as e:
        logger.error(f"Failed to populate collection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to populate collection: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
