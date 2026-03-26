import asyncio
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.identity import DefaultAzureCredential
from app.core.config import get_settings
from tenacity import retry, stop_after_attempt, wait_exponential

settings = get_settings()

class LegalDocumentParser:
    def __init__(self):
        # Using Managed Identity - no keys needed in code!
        endpoint = settings.azure_doc_intel_endpoint
        if not endpoint:
            raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT not configured")
        self.client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=DefaultAzureCredential()
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def parse_contract(self, blob_url: str) -> list:
        """Parse contract PDF with error handling and validation"""
        if not blob_url or not blob_url.startswith(('http://', 'https://')):
            raise ValueError("Invalid blob URL provided")
        
        try:
            # We use the configured model to get tables and checkboxes 
            # which are common in Master Service Agreements (MSAs)
            poller = self.client.begin_analyze_document_from_url(
                settings.document_intelligence_model, 
                blob_url
            )
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: poller.result()
            )

            pages = []
            for page in result.pages:
                # Fix string concatenation efficiency
                line_contents = [line.content for line in page.lines if line.content]
                content = " ".join(line_contents)
                
                if content.strip():  # Only add pages with content
                    pages.append({
                        "page_number": page.page_number,
                        "content": content.strip()
                    })
            
            if not pages:
                raise ValueError("No content found in document")
                
            return pages
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse document: {str(e)}")
