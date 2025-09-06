from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_sentences(sentences: list[str]) -> list[float]:
    return model.encode(sentences)


def save_embedding(sentence: str, emb: list[float], db): ...


if __name__ == "__main__":

    sentences = [
        "The weather is lovely today.",
        "It's so sunny outside!",
        "He drove to the stadium.",
    ]
    out = embed_sentences(sentences)
    print(out.shape)
    print(out)
