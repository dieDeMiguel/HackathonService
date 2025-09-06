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

client = QdrantClient(url="http://localhost:6333/")
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=qdrant_client.models.VectorParams(
        size=1536, distance=qdrant_client.models.Distance.COSINE  # OpenAI text-embedding-3-small
    ),
)


def get_lines_from_file(filepath):
    with open(filepath) as file:
        return file.readlines()


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


def save_embeddings_to_db(embeddings: list, payloads: list | None = None):
    """
    Uploads embeddings into Qdrant.

    Args:
        collection_name (str): Name of the Qdrant collection.
        embeddings (list): List of embeddings (each a list/array of floats).
        payloads (list, optional): List of payload dictionaries aligned with embeddings.
                                   Useful for storing metadata like text, ids, etc.
    """
    points = []
    for i, vector in enumerate(embeddings):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),  # generate unique id
                vector=vector,
                payload=payloads[i] if payloads and i < len(payloads) else {},
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {len(points)} embeddings to collection '{COLLECTION_NAME}'")
