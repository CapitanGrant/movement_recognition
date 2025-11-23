from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.dao.database import Base


class VideoAnalysis(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    processing_time: Mapped[float] = mapped_column(Float, nullable=False) # время анализа
    movement_detected: Mapped[bool] = mapped_column(Boolean, nullable=False) # обнаружены движения или нет
    error: Mapped[str] = mapped_column(String, nullable=True)
