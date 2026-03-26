import asyncio
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from app.core.config import get_settings
from tenacity import retry, stop_after_attempt, wait_exponential

settings = get_settings()

class LegalEmbedder:
    def __init__(self):
        endpoint = settings.azure_openai_endpoint
        deployment = settings.azure_openai_embedding_deployment
        
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not configured")
        if not deployment:
            raise ValueError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT not configured")
            
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version="2024-02-15-preview",
            azure_ad_token_provider=DefaultAzureCredential().get_token
        )
        self.deployment = deployment

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def embed_text(self, text: str) -> list:
        """Generate embeddings with error handling and validation"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) > 8000:  # Prevent token limit issues
            raise ValueError("Text too long for embedding (max 8000 characters)")
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.embeddings.create(
                    input=text.strip(),
                    model=self.deployment
                )
            )
            
            if not response.data or len(response.data) == 0:
                raise RuntimeError("No embedding returned from OpenAI")
                
            return response.data[0].embedding
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
