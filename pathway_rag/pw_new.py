import os
import logging
import pathway as pw
from typing import List, Dict, Any
from pathway.udfs import DiskCache, ExponentialBackoffRetryStrategy
from pathway.xpacks.llm import embedders, llms, parsers, prompts
from pathway.xpacks.llm.question_answering import AdaptiveRAGQuestionAnswerer
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.servers import DocumentStoreServer
from pathway.stdlib.indexing import UsearchKnnFactory, TantivyBM25Factory, HybridIndexFactory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

os.environ["PATHWAY_PERSISTENT_STORAGE"] = "./persistence_data"

load_dotenv()
# Configure text splitting parameters for document chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=800)

class DocumentProcessor:
    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        # Configure environment and logging
        os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/4.00/tessdata"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        self.host = host
        self.port = port
        self.app = None 
        self.vector_store = None
        
        # Initialize LLM components with Ollama backend
        self.chat = llms.LiteLLMChat(
            model="1/1",
            retry_strategy=ExponentialBackoffRetryStrategy(max_retries=6),
            cache_strategy=DiskCache(),
            temperature=0.0,
        )
        self.parser = parsers.ParseUnstructured(mode="paged")
        self.embedder = embedders.LiteLLMEmbedder(
            capacity=30,
            model='voyage/voyage-3',
            retry_strategy=ExponentialBackoffRetryStrategy(max_retries=6),
            cache_strategy=DiskCache(),
        )

    def initialize_vector_store(self, path1):
        """Initialize document store with provided file path"""
        source1 = pw.io.fs.read(path=path1, with_metadata=True, format="binary", mode="streaming")

        usearch = UsearchKnnFactory(embedder=self.embedder)
        bm25 = TantivyBM25Factory(ram_budget=524288000, in_memory_index=True)
        factories = [usearch, bm25]
        retriever_factory = HybridIndexFactory(factories, k=60)
        
        self.vector_store = DocumentStore.from_langchain_components(
            retriever_factory=retriever_factory,
            docs=[source1],
            parser=self.parser,
            splitter=text_splitter,
        )

    def initialize_user_store(self, path2):
        """Initialize document store with provided file path"""
        source2 = pw.io.fs.read(path=path2, with_metadata=True, format="binary", mode="streaming")

        usearch = UsearchKnnFactory(embedder=self.embedder)
        bm25 = TantivyBM25Factory(ram_budget=524288000, in_memory_index=True)
        factories = [usearch, bm25]
        retriever_factory = HybridIndexFactory(factories, k=60)

        self.knowledge_store = DocumentStore.from_langchain_components(
            retriever_factory=retriever_factory,
            docs=[source2],
            parser=self.parser,
            splitter=text_splitter,
        )

    def setup_question_answerer(self):
        """Configure RAG-based question answering system"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
            
        self.app = AdaptiveRAGQuestionAnswerer(
            llm=self.chat,
            indexer=self.vector_store,
            long_prompt_template=prompts.prompt_citing_qa,
        )
        self.app.build_server(host=self.host, port=self.port)

    def run_server(self):
        """Run question answering server"""
        if not self.app:
            raise ValueError("Question answerer not configured")
            
        logging.info(f"Server started on http://{self.host}:{self.port}")
        self.app.run_server()

    def setup_document_server(self):
        """Configure document store server"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
            
        self.app1 = DocumentStoreServer(
            host=self.host,
            port=4004,
            document_store=self.vector_store
        )

    def setup_knowledge_server(self):
        """Configure document store server"""
        if not self.knowledge_store:
            raise ValueError("Knowledge store not initialized")
            
        self.app2 = DocumentStoreServer(
            host=self.host,
            port=4006,
            document_store=self.knowledge_store
        )
        
    def run_server1(self):
        """Run document server"""
        self.app1.run_server1()
        print("VS live")
    def run_server2(self):
        self.app2.run_server2()
        print("KS live ")

def main():
    # Initialize data directory for document storage
    data_dir = "../RACCOON/Agents/LATS/temp_rag_space"

    knowledge_dir = "/home/rdk/kb_1002"
    # os.makedirs(knowledge_dir,exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    
    # Set up and start servers
    processor = DocumentProcessor()
    processor.initialize_vector_store(data_dir)
    # processor.initialize_user_store(knowledge_dir)
    processor.setup_question_answerer()
    processor.setup_document_server()
    # processor.setup_knowledge_server()
    
    persistence_backend = pw.persistence.Backend.filesystem("./state/")
    persistence_config = pw.persistence.Config(persistence_backend)
    # pw.run(
    #     # monitoring_level=pw.MonitoringLevel.NONE,
    #     # persistence_config=persistence_config,)
    pw.run()
    
    try:
        processor.run_server1()
        # processor.run_server2()
        # Run the question answering server
        #processor.run_server()
    except KeyboardInterrupt:
        logging.info("Shutting down server...")

if __name__ == "__main__":
    main()




