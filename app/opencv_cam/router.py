from typing import Dict

from fastapi import APIRouter, HTTPException, UploadFile, Response, Depends
from prometheus_client import generate_latest
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.session_maker import TransactionSessionDep
from app.opencv_cam.dao import VideoAnalysisDAO
from app.opencv_cam.metrics import ACTIVE_REQUESTS
from app.opencv_cam.schemas import VideoCreate, validate_video
from app.opencv_cam.video_analizer_controller import VideoAnalyzer

router = APIRouter(prefix="", tags=["Cam API"])
video_analyzer = VideoAnalyzer()


@router.post("/analyze")
async def get_analyze_video(
        file: UploadFile = Depends(validate_video),
        session: AsyncSession = TransactionSessionDep
) -> Dict:
    """Принимает видеофайл, запускает анализ и возвращает результат"""
    try:
        ACTIVE_REQUESTS.inc()

        analysis_result = video_analyzer.analyze_video(file)
        filename = file.filename or "unknown"

        db_analysis = VideoCreate(
            filename=filename,
            processing_time=analysis_result["processing_time"],
            movement_detected=analysis_result["has_movement"],
            error=analysis_result.get("error_message")
        )

        db_save_analysis = await VideoAnalysisDAO.add(session=session, values=db_analysis)

        response_data = {
            "analysis_id": db_save_analysis.id,
            "filename": filename,
            "has_movement": analysis_result["has_movement"],
            "movement_percentage": analysis_result["movement_percentage"],
            "duration": analysis_result["duration"],
            "processing_time": analysis_result["processing_time"],
            "status": analysis_result["status"]
        }

        if analysis_result.get("error_message"):
            response_data["error_message"] = analysis_result["error_message"]

        return response_data
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера. Повторите попытку позже")


@router.get("/metrics")
async def get_metrics():
    """Отдаёт метрики в формате Prometheus"""
    return Response(generate_latest(), media_type="text/plain")