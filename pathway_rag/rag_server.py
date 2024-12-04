from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from urllib.parse import quote
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import time 
import multiprocessing
import gunicorn.app.base

app = FastAPI()
load_dotenv('../.env')

# OpenAI client configuration
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

api_key = os.getenv('OPEN_AI_API_KEY_30')
client = OpenAI(api_key=api_key)

# Add VoyageAI configuration
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
VOYAGE_RERANK_URL = "https://api.voyageai.com/v1/rerank"

class Query(BaseModel):
    query: str
    source : str
    max_tokens: int = 1000
    num_docs: int = 5

class AnswerResponse(BaseModel):
    answer: str

def rerank_documents(query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rerank documents using VoyageAI reranker."""
    if not is_rerank_service_available():
        print("Reranking service is not available. Using original document order.")
        return documents

    try:
        # Extract text from documents
        doc_texts = [doc.get('text', '') for doc in documents]
        
        headers = {
            "Authorization": f"Bearer {VOYAGE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "documents": doc_texts,
            "model": "rerank-2",  # Using their recommended model
            "return_documents": True
        }
        
        response = requests.post(VOYAGE_RERANK_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        reranked_results = response.json()
        
        # Reconstruct documents with reranked order and scores
        reranked_docs = []
        for result in reranked_results["data"]:
            original_doc = documents[result["index"]]
            original_doc["relevance_score"] = result["relevance_score"]
            reranked_docs.append(original_doc)
        print(reranked_docs)
        return reranked_docs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during reranking: {str(e)}")

def query_retrieval_service(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Query the local retrieval service for relevant documents."""
    try:
        encoded_query = quote(query)
        response = requests.get(f"http://localhost:4004/v1/retrieve?query={encoded_query}&k={k}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying retrieval service: {str(e)}")

def format_context(documents: List[Dict[str, Any]]) -> str:
    """Format retrieved documents into context string."""
    formatted_docs = []
    for i, doc in enumerate(documents, 1):
        formatted_docs.append(f"Document {i} (Score: {doc.get('relevance_score', 'N/A')}):\n{doc.get('text', '')}")
    return "\n\n".join(formatted_docs)

def generate_answer_openai(query: str, source: str,retrieved_docs: List[Dict[str, Any]], max_tokens: int = 1000) -> str:
    """Generate an answer using OpenAI model."""
    try:
        context = format_context(retrieved_docs)
        print(source)
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a precise and factual research assistant. Answer questions based solely on the provided context.
                    Important Instructions:
                    - Base your answer ONLY on the provided context documents
                    - Use quotes when directly quoting text
                    - If information isn't available in the context, state: "This information is not available in the provided documents."
                    - If you find conflicting information, point it out"""

                },
                {
                    "role": "user",
                    "content": f"""Context:\n{context}\n\nQuestion: {query}\n\n This from {source} always add this.if its a url like https://bbcnews.com/ give it completely. If not a url then just mention the {source}  with relevant context from provided else dont add ANYTHING."""
                }
            ],
            temperature=0.3,
            top_p=0.9,
            max_tokens=max_tokens,
            model=model_name
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer with OpenAI: {str(e)}")
def is_rerank_service_available() -> bool:
    """Check if the VoyageAI reranking service is available."""
    try:
        headers = {
            "Authorization": f"Bearer {VOYAGE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": "test query",
            "documents": ["test document"],
            "model": "rerank-2",
            "return_documents": True
        }
        
        response = requests.post(VOYAGE_RERANK_URL, headers=headers, json=payload, timeout=5)
        return response.status_code == 200
    except Exception:
        return False
@app.post("/generate", response_model=AnswerResponse)
async def generate(query_request: Query):
    """
    Generate an answer for a given query using retrieved documents and OpenAI LLM.
    Returns only the final answer from the LLM.
    """
    # Retrieve relevant documents
    start = time.time()
    retrieved_docs = query_retrieval_service(query_request.query, query_request.num_docs)
    
    # Rerank the retrieved documents
    reranked_docs = rerank_documents(query_request.query, retrieved_docs)
    # Generate answer using OpenAI with reranked documents
    answer = generate_answer_openai(
        query_request.query, 
        query_request.source, 
        reranked_docs,
        query_request.max_tokens
    )
    end = time.time()
    print(end-start)
    return AnswerResponse(answer=answer)

if __name__ == "__main__":

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '0.0.0.0:4005',
        'workers': 12,
        'worker_class': 'uvicorn.workers.UvicornWorker',
        'timeout': 120,
        'graceful_timeout': 60,
        'keepalive': 5,      
    }
    StandaloneApplication(app, options).run()