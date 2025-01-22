import pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Union
import os
from dotenv import load_dotenv
import io
from werkzeug.datastructures import FileStorage
import re
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

        self.chunk_size = 5
        self.chunk_overlap = 2

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
        
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex pattern matching.
        Handles common sentence endings (., !, ?) while accounting for common abbreviations.
        """
        # Clean the text
        text = text.strip()
        
        # Split on sentence endings followed by capital letters
        # This pattern looks for ., !, or ? followed by spaces and a capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        # Further clean the sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _create_chunks(self, text: str) -> List[str]:
        """
        Create overlapping chunks from the input text.
        Each chunk contains a specified number of sentences with overlap.
        """
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        chunks = []
        
        # Create chunks with overlap
        for i in range(0, len(sentences), self.chunk_size - self.chunk_overlap):
            chunk = sentences[i:i + self.chunk_size]
            if chunk:  # Only add non-empty chunks
                chunks.append(" ".join(chunk))
        
        return chunks

    def _process_file(self, file: Union[FileStorage, io.BytesIO]) -> str:
        """
        Process the uploaded file and return its content as text.
        """
        if isinstance(file, FileStorage):
            content = file.read()
        else:
            content = file.read()
            
        # Try different encodings if UTF-8 fails
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Unable to decode file content with supported encodings")

    def upload_context(self, files: List[Union[FileStorage, io.BytesIO]], filenames: List[str]):
        """
        Process uploaded files, create chunks, and upload to Pinecone.
        
        Args:
            files: List of file objects (either FileStorage or BytesIO)
            filenames: List of filenames corresponding to the files
        """
        try:
            total_chunks = 0
            batch_size = 100  # Number of vectors to upload at once
            vectors_batch = []
            
            for file, filename in zip(files, filenames):
                # Process file content
                text_content = self._process_file(file)
                
                # Create chunks from the text
                chunks = self._create_chunks(text_content)
                
                # Generate embeddings for chunks
                chunk_embeddings = self.model.encode(chunks)
                
                # Prepare vectors for batch upload
                for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
                    vector_id = f"{filename}_chunk_{i}"
                    vectors_batch.append({
                        'id': vector_id,
                        'values': embedding.tolist(),
                        'metadata': {
                            'text': chunk,
                            'filename': filename,
                            'chunk_index': i
                        }
                    })
                    
                    # Upload batch if it reaches the batch size
                    if len(vectors_batch) >= batch_size:
                        self.index.upsert(vectors=vectors_batch)
                        total_chunks += len(vectors_batch)
                        vectors_batch = []
            
            # Upload any remaining vectors
            if vectors_batch:
                self.index.upsert(vectors=vectors_batch)
                total_chunks += len(vectors_batch)
            
            return{
                'status': 'success',
                # 'total_chunks': total,
                'message': f"Successfully uploaded {total_chunks} chunks to the index."
            }
            
        except Exception as e:
            print(f"Error during context upload: {str(e)}")
            raise