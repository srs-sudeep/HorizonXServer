import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
import aiofiles
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)
DEFAULT_UPLOAD_DIR = Path(settings.UPLOAD_DIR or "uploads")
DEFAULT_MAX_SIZE = settings.MAX_FILE_SIZE or 10 * 1024 * 1024


class FileUploadService:
    """Service for handling file uploads."""

    def __init__(self):
        self.upload_dir = DEFAULT_UPLOAD_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = {
            "image": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
            "document": {".pdf", ".doc", ".docx", ".txt", ".rtf"},
            "video": {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"},
            "audio": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
        }

        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different services
        (self.upload_dir / "files").mkdir(exist_ok=True)

    def _validate_file(self, file: UploadFile) -> bool:
        """Validate file type and size."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Check file size
        if file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {self.max_file_size/1024/1024:.1f}MB",
            )

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        allowed_exts = set()
        for category_exts in self.allowed_extensions.values():
            allowed_exts.update(category_exts)

        if file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_ext}' not allowed. Allowed: {', '.join(allowed_exts)}",
            )

        return True

    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename to avoid conflicts."""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_ext}"

    async def save_file(self, file: UploadFile, subfolder: str = "files") -> dict:
        """Save uploaded file and return file info."""
        try:
            # Validate file
            self._validate_file(file)

            # Generate unique filename
            unique_filename = self._generate_unique_filename(file.filename)

            # Create file path
            file_path = self.upload_dir / subfolder / unique_filename

            # Ensure subfolder exists
            (self.upload_dir / subfolder).mkdir(parents=True, exist_ok=True)

            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # Get file size
            file_size = len(content)

            logger.info(f"File saved: {file_path}")

            return {
                "original_filename": file.filename,
                "saved_filename": unique_filename,
                "file_path": str(file_path.relative_to(self.upload_dir)),
                "file_size": file_size,
                "mimetype": file.content_type,
                "full_path": str(file_path),
            }

        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""
        try:
            full_path = self.upload_dir / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted: {full_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """Generate URL for file access."""
        return f"/api/v1/files{file_path}"


# Global instance
file_upload_service = FileUploadService()
