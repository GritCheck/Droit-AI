from fastapi import APIRouter, Depends, HTTPException
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from app.core.config import get_settings
from app.core.auth import get_current_user

router = APIRouter()
settings = get_settings()

@router.get("/")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """
    List all CUAD contracts available in storage container.
    """
    try:
        blob_service_client = BlobServiceClient(
            account_url=f"https://{settings.azure_storage_account}.blob.core.windows.net",
            credential=DefaultAzureCredential()
        )
        container_client = blob_service_client.get_container_client(settings.azure_storage_container)
        
        blobs = container_client.list_blobs()
        return [{"name": b.name, "size": b.size, "created_at": b.creation_time} for b in blobs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage Error: {str(e)}")
