"""
Cloudinary upload service.

Validates MIME type from the first bytes before sending to Cloudinary —
this prevents accepting non-image files that are merely renamed to .jpg.

Free Cloudinary tier: 25 GB storage, 25 GB bandwidth / month — plenty
for a demo app, and no credit card required.
"""

import cloudinary
import cloudinary.uploader

from fastapi import UploadFile, HTTPException, status

from app.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

# Magic bytes for allowed image formats
_ALLOWED_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"GIF8": "image/gif",
    b"RIFF": "image/webp",  # RIFF....WEBP — simplified check
}

MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


async def upload_avatar(file: UploadFile, user_id: int) -> str:
    """
    Validate and upload a user avatar to Cloudinary.

    Returns the secure HTTPS URL of the uploaded image.
    Raises HTTP 422 on invalid file type or size exceeded.
    """
    data = await file.read()

    # Size check
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File too large. Maximum allowed size is {MAX_SIZE_BYTES // (1024*1024)} MB.",
        )

    # MIME type check via magic bytes
    if not _is_image(data):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid file type. Only JPEG, PNG, GIF, and WebP images are accepted.",
        )

    result = cloudinary.uploader.upload(
        data,
        public_id=f"contacts_api/avatars/user_{user_id}",
        overwrite=True,
        resource_type="image",
    )
    return result["secure_url"]


def _is_image(data: bytes) -> bool:
    for signature in _ALLOWED_SIGNATURES:
        if data[: len(signature)] == signature:
            return True
    return False
