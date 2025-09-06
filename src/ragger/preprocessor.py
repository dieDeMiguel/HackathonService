import qdrant_client
from qdrant_client.models import PointStruct
import uuid
from qdrant_client import QdrantClient


MODEL = "model-name"
COLLECTION_NAME = "HACKATHON_COLLECTION"

client = QdrantClient(url="http://localhost:6333/")
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=qdrant_client.models.VectorParams(
        size=384, distance=qdrant_client.models.Distance.COSINE
    ),
)


def upload_embeddings(collection_name: str, embeddings: list, payloads: list = None):
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

    client.upsert(collection_name=collection_name, points=points)
    print(f"✅ Uploaded {len(points)} embeddings to collection '{collection_name}'")


def embed_sentence(s: str, model) -> list[float]: ...


def save_embedding(sentence: str, emb: list[float], db): ...


def preprocess_line(s: str) -> str: ...


def preprocess_file(filepath, db):
    with open(filepath) as file:
        for line in file:
            sentence = preprocess_line(line)
            emb = embed_sentence(sentence, model=MODEL)
            save_embedding(sentence, emb, db)


if __name__ == "__main__":
    preprocess_file("path-to-local-file")
