import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import shutil

class ImageService:
    UPLOAD_DIR = Path("app/static/uploads")
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_SIZE = 5 * 1024 * 1024
    
    @classmethod
    async def save_image(cls, file: UploadFile, folder: str, resize: Optional[tuple[int, int]] = None) -> str:
        upload_path = cls.UPLOAD_DIR / folder
        upload_path.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Неподдерживаемый формат")
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > cls.MAX_SIZE:
            raise HTTPException(400, f"Файл слишком большой")
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_path / unique_name
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if resize:
            cls.resize_image(file_path, resize)
        return f"/static/uploads/{folder}/{unique_name}"
    
    @classmethod
    def resize_image(cls, path: Path, size: tuple[int, int]):
        try:
            img = Image.open(path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(path, optimize=True, quality=85)
        except Exception as e:
            print(f"Error: {e}")
