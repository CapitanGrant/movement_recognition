from fastapi import UploadFile, File, HTTPException
from pydantic import BaseModel, Field


class VideoBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255, description="Название файла")
    processing_time: float = Field(..., ge=0, description="Время обработки в секундах")
    movement_detected: bool = Field(..., description="Наличие движения в видео")
    error: str | None = Field(None, max_length=500, description="Сообщение об ошибке")


class VideoCreate(VideoBase):
    """Схема для создания новой записи"""
    pass


async def validate_video(file: UploadFile = File(...)) -> UploadFile:
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")
    return file