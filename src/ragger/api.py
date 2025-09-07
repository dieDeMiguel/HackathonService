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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
