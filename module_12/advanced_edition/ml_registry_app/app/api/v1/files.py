"""
File upload and download API endpoints.

Handles model artifact uploads to MinIO and downloads.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models.user import User
from app.auth.dependencies import get_current_user
from app.storage.minio_client import minio_client

router = APIRouter()

# Allowed file extensions for ML models
ALLOWED_EXTENSIONS = {".pkl", ".joblib", ".pt", ".pth", ".h5", ".pb", ".onnx", ".model"}


@router.post("/upload")
async def upload_model_file(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Upload ML model file to MinIO.

    Args:
        file: Model file to upload
        current_user: Current authenticated user

    Returns:
        Upload confirmation with file path

    Raises:
        HTTPException: If file type not allowed or upload fails
    """
    # Validate file type (basic check)
    if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Generate object name with user prefix
    object_name = f"users/{current_user.id}/models/{file.filename}"

    try:
        file_path = minio_client.upload_file(
            file.file,
            object_name,
            content_type=file.content_type or "application/octet-stream",
            metadata={"uploaded_by": current_user.username}
        )

        return {
            "filename": file.filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/download/{path:path}")
async def download_model_file(
    path: str,
    current_user: Annotated[User, Depends(get_current_user)]
) -> StreamingResponse:
    """
    Download ML model file from MinIO.

    Args:
        path: File path in storage
        current_user: Current authenticated user

    Returns:
        File stream for download

    Raises:
        HTTPException: If file not found
    """
    # Extract object name from path (remove bucket prefix if present)
    object_name = path.split("/", 1)[-1] if "/" in path else path

    try:
        file_data = minio_client.download_file(object_name)

        return StreamingResponse(
            file_data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={object_name.split('/')[-1]}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}"
        )


@router.get("/presigned-url/{path:path}")
async def get_presigned_download_url(
    path: str,
    current_user: Annotated[User, Depends(get_current_user)],
    expires_seconds: int = 3600
) -> dict:
    """
    Get presigned URL for direct download.

    Args:
        path: File path in storage
        current_user: Current authenticated user
        expires_seconds: URL expiry in seconds

    Returns:
        Presigned URL and expiry time

    Raises:
        HTTPException: If URL generation fails
    """
    object_name = path.split("/", 1)[-1] if "/" in path else path

    try:
        url = minio_client.get_presigned_url(object_name, expires_seconds)
        return {"url": url, "expires_in_seconds": expires_seconds}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error generating URL: {str(e)}"
        )
