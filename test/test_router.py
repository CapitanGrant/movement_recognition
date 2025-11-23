from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from fastapi import UploadFile
import io

from app.opencv_cam.router import video_analyzer


class TestAnalyzeVideo:
    """Тесты для эндпоинта /analyze"""

    @pytest.fixture
    def mock_video_file(self):
        """Фикстура для создания mock видео файла"""
        return UploadFile(
            filename="test_video.mp4",
            file=io.BytesIO(b"fake video content")
        )

    @pytest.fixture
    def mock_session(self):
        """Фикстура для создания mock сессии базы данных"""
        session = AsyncMock()
        return session

    @pytest.fixture
    def mock_analysis_result(self):
        """Фикстура для создания mock результата анализа"""
        return {
            "has_movement": True,
            "movement_percentage": 15.5,
            "duration": 10.0,
            "processing_time": 2.5,
            "status": "completed"
        }

    @pytest.mark.asyncio
    async def test_analyze_video_success(
            self,
            mock_video_file,
            mock_session,
            mock_analysis_result
    , client):
        """Тест успешного анализа видео"""
        video_analyzer.analyze_video = MagicMock(return_value=mock_analysis_result)

        with patch('app.opencv_cam.router.VideoAnalysisDAO.add') as mock_dao:
            mock_dao.return_value = AsyncMock()
            mock_dao.return_value.id = 1

            with patch('app.opencv_cam.router.ACTIVE_REQUESTS') as mock_metrics:
                mock_metrics.inc = MagicMock()

                response = client.post(
                    "/analyze",
                    files={"file": ("test_video.mp4", mock_video_file.file, "video/mp4")}
                )

        assert response.status_code == 200
        data = response.json()

        assert data["analysis_id"] == 1
        assert data["filename"] == "test_video.mp4"
        assert data["has_movement"] is True
        assert data["movement_percentage"] == 15.5
        assert data["duration"] == 10.0
        assert data["processing_time"] == 2.5
        assert data["status"] == "completed"

        mock_metrics.inc.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_video_not_video_file(self, client):
        """Тест загрузки не видео файла"""
        response = client.post(
            "/analyze",
            files={"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        )

        assert response.status_code == 400
        assert "File must be a video" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_video_with_error_in_analysis(
            self,
            mock_video_file,
            mock_session
    , client):
        """Тест анализа видео с ошибкой в процессе анализа"""
        error_result = {
            "has_movement": False,
            "movement_percentage": 0.0,
            "duration": 0.0,
            "processing_time": 0.0,
            "status": "error",
            "error_message": "Analysis failed"
        }
        video_analyzer.analyze_video = MagicMock(return_value=error_result)

        with patch('app.opencv_cam.router.VideoAnalysisDAO.add') as mock_dao:
            mock_dao.return_value = AsyncMock()
            mock_dao.return_value.id = 1

            with patch('app.opencv_cam.router.ACTIVE_REQUESTS') as mock_metrics:
                mock_metrics.inc = MagicMock()

                response = client.post(
                    "/analyze",
                    files={"file": ("test_video.mp4", mock_video_file.file, "video/mp4")}
                )

        assert response.status_code == 200
        data = response.json()
        assert data["error_message"] == "Analysis failed"
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_analyze_video_dao_exception(
            self,
            mock_video_file,
            mock_analysis_result
    , client):
        """Тест исключения при сохранении в базу данных"""
        video_analyzer.analyze_video = MagicMock(return_value=mock_analysis_result)

        with patch('app.opencv_cam.router.VideoAnalysisDAO.add') as mock_dao:
            mock_dao.side_effect = Exception("Database error")

            with patch('app.opencv_cam.router.ACTIVE_REQUESTS') as mock_metrics:
                mock_metrics.inc = MagicMock()

                response = client.post(
                    "/analyze",
                    files={"file": ("test_video.mp4", mock_video_file.file, "video/mp4")}
                )

        assert response.status_code == 500
        assert "Ошибка сервера" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_video_analyzer_exception(self, mock_video_file, client):
        """Тест исключения в анализаторе видео"""
        video_analyzer.analyze_video = MagicMock(side_effect=Exception("Analyzer error"))

        with patch('app.opencv_cam.router.ACTIVE_REQUESTS') as mock_metrics:
            mock_metrics.inc = MagicMock()

            response = client.post(
                "/analyze",
                files={"file": ("test_video.mp4", mock_video_file.file, "video/mp4")}
            )

        assert response.status_code == 500
        assert "Ошибка сервера" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_video_no_filename(self, client):
        """Тест загрузки видео без имени файла"""
        response = client.post(
            "/analyze",
            files={"file": ("", io.BytesIO(b"video content"), "video/mp4")}
        )

        assert response.status_code == 422


