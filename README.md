# FastAPI Vector DB Example

This is a simple FastAPI project with a vector database service (in-memory example).

## How to run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

## API
- POST `/add-vector` with JSON body `{ "vector": [1.0, 2.0, 3.0] }`

---

Replace the in-memory vector DB with a real one (e.g., Pinecone, Qdrant, FAISS) as needed.
