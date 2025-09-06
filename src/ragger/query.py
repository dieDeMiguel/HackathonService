from qdrant_client import QdrantClient

from ragger.embed import embed_sentences


def main():
    COLLECTION_NAME = "HACKATHON_COLLECTION"

    client = QdrantClient(url="http://localhost:6333/")

    query = "TODO"

    query_vector = embed_sentences(query)[0]

    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=5,  # Return 5 closest points
    )

    print(hits)


if __name__ == "__main__":
    main()
