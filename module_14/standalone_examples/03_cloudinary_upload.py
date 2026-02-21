"""
03. Cloudinary File Upload
==========================

Demonstrates uploading, transforming, and deleting files on Cloudinary.
Used in contacts_api for avatar uploads.

Requirements:
    pip install cloudinary
    Free account at https://cloudinary.com (no credit card needed)

Set environment variables or edit the credentials below:
    CLOUDINARY_CLOUD_NAME=your-cloud-name
    CLOUDINARY_API_KEY=your-api-key
    CLOUDINARY_API_SECRET=your-api-secret
"""

import os
import io
import cloudinary
import cloudinary.uploader
import cloudinary.api


# ============================================================
# CONFIGURATION
# ============================================================

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "your-cloud-name"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "your-api-key"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "your-api-secret"),
    secure=True,
)


# ============================================================
# SECTION 1: Upload from file path (simplest case)
# ============================================================

def upload_from_path(file_path: str, public_id: str = None) -> dict:
    """
    Upload a file by path.
    public_id: optional name for the file in Cloudinary.
    Returns Cloudinary response with url, public_id, format, etc.
    """
    result = cloudinary.uploader.upload(
        file_path,
        public_id=public_id,
        folder="contacts_app/avatars",  # organize files in folders
        overwrite=True,                  # replace existing file with same public_id
    )
    return result


# ============================================================
# SECTION 2: Upload from bytes (FastAPI UploadFile)
# ============================================================
"""
FastAPI's UploadFile provides the file as bytes.
Cloudinary accepts a file-like object (BytesIO), bytes directly,
or a base64 data URL.
"""

def upload_from_bytes(file_bytes: bytes, filename: str, user_id: int) -> str:
    """
    Upload avatar from bytes (as received from FastAPI UploadFile).
    Returns the secure URL of the uploaded file.
    """
    # Use user_id as the public_id so each user has one avatar
    # Uploading again with the same public_id replaces the old avatar
    public_id = f"contacts_app/avatars/user_{user_id}"

    result = cloudinary.uploader.upload(
        io.BytesIO(file_bytes),
        public_id=public_id,
        overwrite=True,
        resource_type="image",
        # Optional: eager transformations (generated on upload, cached at CDN)
        eager=[
            {"width": 200, "height": 200, "crop": "fill", "gravity": "face"}
        ],
    )

    return result["secure_url"]


# ============================================================
# SECTION 3: URL-based transformations
# ============================================================
"""
Cloudinary's killer feature: image transformations via URL parameters.
The same uploaded image can be served in different sizes/formats
without re-uploading.

Original:  https://res.cloudinary.com/myapp/image/upload/v1/avatars/user_42.jpg
200x200:   https://res.cloudinary.com/myapp/image/upload/c_fill,h_200,w_200/avatars/user_42.jpg
Thumbnail: https://res.cloudinary.com/myapp/image/upload/c_thumb,w_50/avatars/user_42.jpg
WebP:      https://res.cloudinary.com/myapp/image/upload/f_webp,q_80/avatars/user_42.jpg
"""

from cloudinary import CloudinaryImage


def get_avatar_urls(public_id: str) -> dict:
    """Generate different size URLs for the same uploaded image."""
    image = CloudinaryImage(public_id)
    return {
        "original": image.build_url(),
        "avatar_200": image.build_url(
            width=200, height=200, crop="fill", gravity="face"
        ),
        "thumbnail_50": image.build_url(
            width=50, height=50, crop="thumb"
        ),
        "webp_optimized": image.build_url(
            format="webp", quality=80, width=400
        ),
    }


# ============================================================
# SECTION 4: Validate MIME type before uploading (security)
# ============================================================
"""
Never trust the client to send the right file type.
Always validate MIME type server-side before uploading to Cloudinary.

In contacts_api, we check: image/jpeg, image/png, image/webp
"""

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE_MB = 5


def validate_image(file_bytes: bytes, content_type: str) -> None:
    """
    Validate file before uploading.
    Raises ValueError with descriptive message on failure.
    """
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Invalid file type: {content_type}. "
            f"Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"File too large: {size_mb:.1f}MB. Maximum: {MAX_FILE_SIZE_MB}MB"
        )

    # Basic magic bytes check (file signature)
    # JPEG starts with FF D8 FF
    # PNG starts with 89 50 4E 47
    magic_bytes = {
        "image/jpeg": b"\xff\xd8\xff",
        "image/png": b"\x89PNG",
        "image/webp": b"RIFF",
        "image/gif": b"GIF",
    }
    expected_magic = magic_bytes.get(content_type)
    if expected_magic and not file_bytes.startswith(expected_magic):
        raise ValueError(
            "File content doesn't match declared content type. "
            "Possible file extension spoofing."
        )


# ============================================================
# SECTION 5: Delete a file
# ============================================================

def delete_avatar(public_id: str) -> dict:
    """Delete file from Cloudinary by public_id."""
    return cloudinary.uploader.destroy(public_id)


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    print("Cloudinary Upload Demo")
    print("=" * 50)
    print()
    print("To run this demo, set environment variables:")
    print("  export CLOUDINARY_CLOUD_NAME=your-cloud-name")
    print("  export CLOUDINARY_API_KEY=your-api-key")
    print("  export CLOUDINARY_API_SECRET=your-api-secret")
    print()

    # Demo without real upload: show what the service layer looks like
    print("=== How contacts_api uses this (app/services/cloudinary.py) ===")
    print("""
from fastapi import UploadFile, HTTPException

async def upload_avatar(file: UploadFile, user_id: int) -> str:
    file_bytes = await file.read()

    # 1. Validate before uploading
    try:
        validate_image(file_bytes, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 2. Upload to Cloudinary
    url = upload_from_bytes(file_bytes, file.filename, user_id)

    return url
    """)

    print("=== URL transformation examples ===")
    urls = get_avatar_urls("contacts_app/avatars/user_42")
    for name, url in urls.items():
        print(f"  {name}:\n    {url}")

    print()
    print("=== Validation examples ===")

    # Valid case
    fake_jpeg = b"\xff\xd8\xff" + b"0" * 100
    try:
        validate_image(fake_jpeg, "image/jpeg")
        print("  ✅ Valid JPEG accepted")
    except ValueError as e:
        print(f"  ❌ {e}")

    # Wrong type
    try:
        validate_image(b"fake content", "application/pdf")
        print("  ❌ PDF should have been rejected")
    except ValueError as e:
        print(f"  ✅ PDF rejected: {e}")

    # Extension spoofing
    try:
        validate_image(b"fake content", "image/jpeg")
    except ValueError as e:
        print(f"  ✅ Spoofed extension rejected: {e}")
