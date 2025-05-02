from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

from config import QDRANT_URL, MODEL_NAME


class NeuralSearcher:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.model = SentenceTransformer(MODEL_NAME, device="cpu")
        self.qdrant_client = QdrantClient(QDRANT_URL)

    def search(self, text: str, context_messages: Optional[List[Dict]] = None):
        # Combine current message with context messages for neural search
        search_text = text
        if context_messages:
            context_text = " ".join([msg["content"] for msg in context_messages if msg["role"] == "user"])
            search_text = f"{context_text} {text}"

        vector = self.model.encode(search_text).tolist()

        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=None,
            limit=5,
        )

        payloads = [hit.payload for hit in search_result]
        return payloads
