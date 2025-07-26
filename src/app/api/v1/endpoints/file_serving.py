from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from src.core.config import settings
from src.app.api.deps import has_permission

router = APIRouter()


@router.get("/files/{file_path:path}")
async def serve_file(
    file_path: str, current_user: dict = Depends(has_permission("file", "read"))
):
    """Serve uploaded files."""
    full_path = Path(settings.UPLOAD_DIR) / file_path

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Security: Ensure file is within upload directory
    try:
        full_path.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(
        path=full_path, filename=full_path.name, media_type="application/octet-stream"
    )
