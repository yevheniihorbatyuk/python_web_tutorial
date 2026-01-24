"""
Storage package.

Handles integration with MinIO and other storage backends.
"""

from app.storage.minio_client import minio_client

__all__ = ["minio_client"]
