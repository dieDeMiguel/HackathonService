from sentence_transformers import SentenceTransformer
import qdrant_client
from qdrant_client.models import PointStruct
import uuid
from qdrant_client import QdrantClient


model = SentenceTransformer("all-MiniLM-L6-v2")


COLLECTION_NAME = "HACKATHON_COLLECTION"

client = QdrantClient(url="http://localhost:6333/")
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=qdrant_client.models.VectorParams(
        size=384, distance=qdrant_client.models.Distance.COSINE
    ),
)


def get_lines_from_file(filepath):
    with open(filepath) as file:
        return file.readlines()


def embed_sentences(sentences):
    return model.encode(sentences)


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
