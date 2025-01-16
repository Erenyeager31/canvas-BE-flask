import pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os
from dotenv import load_dotenv
load_dotenv()

class ContextRetriever:
    def __init__(self):
        # Get API key from environment variables
        api_key = os.getenv('PINECONE_API_KEY')
        index_name = os.getenv('PINECONE_INDEX_NAME')
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables.")

        # Initialize Pinecone
        self.pc = pinecone.Pinecone(api_key=api_key)
        self.index_name = index_name

        # Initialize the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Get the existing index
        if index_name not in self.pc.list_indexes().names():
            raise ValueError(f"Index '{index_name}' does not exist. Please initialize it first.")

        self.index = self.pc.Index(index_name)

    def retrieve_context(self, topic: str, top_k: int = 5) -> List[Dict]:
        """Retrieve context based on the topic passed as an argument."""
        try:
            # Generate embedding for the topic
            topic_embedding = self.model.encode(topic)

            # Query Pinecone index
            results = self.index.query(
                vector=topic_embedding.tolist(),
                top_k=top_k,
                include_metadata=True
            )

            # Format results
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    'text': match['metadata']['text'],
                    'source': match['metadata']['filename'],
                    'score': match['score']
                })

            return formatted_results

        except Exception as e:
            print(f"Error during context retrieval: {str(e)}")
            return []
    
# Example usage
# index_name = "<your_index_name>"
retriever = ContextRetriever()
topic = "Rainbow table attack"
context = retriever.retrieve_context(topic, top_k=5)
for i, result in enumerate(context, 1):
    print(f"\nResult {i} (Score: {result['score']:.3f})")
    print(f"Source: {result['source']}")
    print(f"Text: {result['text'][:200]}...")