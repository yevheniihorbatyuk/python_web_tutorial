"""
MinIO S3-compatible storage client.

Handles file uploads, downloads, and presigned URLs for model artifacts.
"""

from minio import Minio
from minio.error import S3Error
from io import BytesIO
from typing import BinaryIO

from app.config import get_settings

settings = get_settings()


class MinIOClient:
    """MinIO S3-compatible storage client."""

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error checking/creating bucket: {e}")

    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: dict | None = None
    ) -> str:
        """
        Upload file to MinIO.

        Args:
            file_data: File data stream
            object_name: Object name/path in bucket
            content_type: MIME type
            metadata: Optional metadata dict

        Returns:
            Full path (bucket/object_name)

        Raises:
            Exception: If upload fails
        """
        try:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning

            self.client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                length=file_size,
                content_type=content_type,
                metadata=metadata
            )

            return f"{self.bucket_name}/{object_name}"
        except S3Error as e:
            raise Exception(f"Error uploading file: {e}")

    def download_file(self, object_name: str) -> BytesIO:
        """
        Download file from MinIO.

        Args:
            object_name: Object name/path in bucket

        Returns:
            File data as BytesIO

        Raises:
            Exception: If download fails
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = BytesIO(response.read())
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise Exception(f"Error downloading file: {e}")

    def delete_file(self, object_name: str) -> None:
        """
        Delete file from MinIO.

        Args:
            object_name: Object name/path in bucket

        Raises:
            Exception: If deletion fails
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error as e:
            raise Exception(f"Error deleting file: {e}")

    def get_presigned_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """
        Get presigned URL for file download.

        Args:
            object_name: Object name/path in bucket
            expires_seconds: URL expiry in seconds (default 1 hour)

        Returns:
            Presigned download URL

        Raises:
            Exception: If URL generation fails
        """
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires_seconds)
            )
            return url
        except S3Error as e:
            raise Exception(f"Error generating presigned URL: {e}")


# Singleton instance
minio_client = MinIOClient()
