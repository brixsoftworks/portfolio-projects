import os
import chromadb
from chromadb.utils import embedding_functions

class CodeRAGEngine:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        # We use a fast, lightweight sentence transformer suitable for code
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="codebase", 
            embedding_function=self.embedding_fn
        )
        self.is_ingested = False

    def ingest_repository(self, repo_path: str):
        """Parses all Python files in the repo, chunks them, and stores them in ChromaDB."""
        if self.is_ingested:
            return
            
        docs = []
        metadatas = []
        ids = []
        
        chunk_id = 0
        for root, _, files in os.walk(repo_path):
            if ".venv" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    with open(full_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        
                    # Simple chunking by lines (approx 50 lines per chunk)
                    lines = code.split('\n')
                    chunk_size = 50
                    for i in range(0, len(lines), chunk_size):
                        chunk = '\n'.join(lines[i:i+chunk_size])
                        docs.append(chunk)
                        metadatas.append({"file": full_path, "start_line": i})
                        ids.append(f"chunk_{chunk_id}")
                        chunk_id += 1
                        
        if docs:
            # Clear existing data for fresh ingestion
            try:
                self.client.delete_collection("codebase")
                self.collection = self.client.create_collection(
                    name="codebase", 
                    embedding_function=self.embedding_fn
                )
            except Exception:
                pass
                
            # Batch add to avoid hitting limits
            batch_size = 100
            for i in range(0, len(docs), batch_size):
                self.collection.add(
                    documents=docs[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )
        self.is_ingested = True

    def query_context(self, code_snippet: str, n_results: int = 3) -> str:
        """Finds related code chunks across the entire repository."""
        if not self.is_ingested:
            return ""
            
        results = self.collection.query(
            query_texts=[code_snippet],
            n_results=n_results
        )
        
        context = []
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            context.append(f"--- From {meta['file']} ---\n{doc}")
            
        return "\n\n".join(context)
