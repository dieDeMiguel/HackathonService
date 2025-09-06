import fastapi
from app.services import service


from app.services.preprocessor import preprocessor
from app.data import test_data
from app.services.preprocessor import embed


app = fastapi.FastAPI()


@app.get("/")
def read_root():
    service.search()


def search():
    for sentence in test_data.dta.split("\n"):
        embedded_vector = embed.embed_sentences(sentence)
        preprocessor.upload_embeddings(
            "HACKATHON_COLLECTION", [embedded_vector], [{"text": sentence}]
        )
