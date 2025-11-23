from app.dao.base import BaseDAO
from app.opencv_cam.models import VideoAnalysis


class VideoAnalysisDAO(BaseDAO[VideoAnalysis]):
    model = VideoAnalysis