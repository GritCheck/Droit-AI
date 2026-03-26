import asyncio
import logging
from typing import Dict, Any
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.parser import LegalDocumentParser
from app.core.embedder import LegalEmbedder

logger = logging.getLogger(__name__)
settings = get_settings()

async def ingest_document(blob_name: str, blob_url: str) -> Dict[str, Any]:
    """Ingest document with comprehensive error handling and validation"""
    if not blob_name or not blob_name.strip():
        raise ValueError("Blob name cannot be empty")
    
    if not blob_url or not blob_url.startswith(('http://', 'https://')):
        raise ValueError("Invalid blob URL provided")
    
    parser = LegalDocumentParser()
    embedder = LegalEmbedder()
    
    try:
        # 1. Parse PDF with Document Intelligence
        logger.info(f"Parsing {blob_name}...")
        pages = await parser.parse_contract(blob_url)
        
        if not pages:
            raise ValueError("No pages found in document")
        
        # 2. Prepare documents for Search Index
        search_docs = []
        for page in pages:
            text_content = page.get("content", "")
            page_number = page.get("page_number", 0)
            
            if not text_content.strip():
                continue  # Skip empty pages
            
            # Generate vector for the page content
            vector = await embedder.embed_text(text_content)
            
            # Generate unique ID to prevent collisions
            safe_blob_name = blob_name.replace('.', '-').replace('/', '-')
            doc_id = f"{safe_blob_name}-p{page_number}"
            
            search_docs.append({
                "id": doc_id,
                "content": text_content,
                "content_vector": vector,
                "document_name": blob_name,
                "page_number": page_number,
                "clause_type": "Uncategorized"  # You can add logic to classify this later
            })
        
        if not search_docs:
            raise ValueError("No valid content found to index")
        
        # 3. Upload to Azure AI Search
        search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=DefaultAzureCredential()
        )
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def upload_documents():
            return search_client.upload_documents(documents=search_docs)
        
        result = await asyncio.get_event_loop().run_in_executor(
            None, upload_documents
        )
        
        logger.info(f"Successfully indexed {len(search_docs)} pages from {blob_name}")
        
        return {
            "success": True,
            "document_name": blob_name,
            "pages_processed": len(search_docs),
            "upload_result": str(result)
        }
        
    except Exception as e:
        logger.error(f"Failed to ingest {blob_name}: {str(e)}")
        return {
            "success": False,
            "document_name": blob_name,
            "error": str(e),
            "pages_processed": 0
        }

if __name__ == "__main__":
    # Test with one of your CUAD blobs
    test_url = f"https://{settings.azure_storage_account}.blob.core.windows.net/documents/sample_contract.pdf"
    
    async def main():
        result = await ingest_document("sample_contract.pdf", test_url)
        print(f"Ingestion result: {result}")
    
    asyncio.run(main())
