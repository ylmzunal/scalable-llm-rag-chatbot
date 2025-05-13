import os
import logging
import argparse
import uuid
from typing import List, Dict, Any, Optional
import asyncio
import httpx
import json
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Document processing
def load_documents(directory_path: str) -> List[Dict[str, Any]]:
    """
    Load documents from a directory.
    
    Args:
        directory_path: Path to the directory containing documents
        
    Returns:
        List of document dictionaries
    """
    logger.info(f"Loading documents from {directory_path}")
    
    # Configure loaders for different file types
    loaders = {
        ".txt": DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader),
        ".pdf": DirectoryLoader(directory_path, glob="**/*.pdf", loader_cls=PyPDFLoader),
        ".csv": DirectoryLoader(directory_path, glob="**/*.csv", loader_cls=CSVLoader),
        ".md": DirectoryLoader(directory_path, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    }
    
    # Load documents
    all_docs = []
    for ext, loader in loaders.items():
        try:
            docs = loader.load()
            logger.info(f"Loaded {len(docs)} documents with extension {ext}")
            all_docs.extend(docs)
        except Exception as e:
            logger.error(f"Error loading documents with extension {ext}: {str(e)}")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(all_docs)
    logger.info(f"Split {len(all_docs)} documents into {len(chunks)} chunks")
    
    # Format chunks for vector database
    formatted_docs = []
    for i, chunk in enumerate(chunks):
        doc_id = str(uuid.uuid4())
        formatted_docs.append({
            "id": doc_id,
            "text": chunk.page_content,
            "metadata": {
                "source": chunk.metadata.get("source", f"chunk_{i}"),
                "page": chunk.metadata.get("page", None)
            }
        })
    
    return formatted_docs

async def upload_to_vector_db(documents: List[Dict[str, Any]], api_url: str) -> None:
    """
    Upload documents to the vector database via the API.
    
    Args:
        documents: List of document dictionaries
        api_url: URL of the API
    """
    logger.info(f"Uploading {len(documents)} documents to vector database")
    
    # Split into batches to avoid large requests
    batch_size = 50
    batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, batch in enumerate(batches):
            try:
                logger.info(f"Uploading batch {i+1}/{len(batches)} ({len(batch)} documents)")
                response = await client.post(
                    f"{api_url}/documents",
                    json={"documents": batch}
                )
                response.raise_for_status()
                logger.info(f"Successfully uploaded batch {i+1}")
            except Exception as e:
                logger.error(f"Error uploading batch {i+1}: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description="Load documents into the vector database")
    parser.add_argument("--dir", type=str, required=True, help="Directory containing documents")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="API URL")
    args = parser.parse_args()
    
    # Load documents
    documents = load_documents(args.dir)
    
    # Upload to vector database
    await upload_to_vector_db(documents, args.api_url)
    
    logger.info("Document loading complete")

if __name__ == "__main__":
    asyncio.run(main()) 