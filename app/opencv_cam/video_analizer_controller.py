import os
import tempfile
import time
from typing import Dict
import cv2


class VideoAnalyzer:
    def __init__(self, movement_threshold: float = 1000.0, min_contour_area: int = 500):
        self.movement_threshold = movement_threshold
        self.min_contour_area = min_contour_area

    def analyze_video(self, video_file) -> Dict:
        start_time = time.time()
        tmp_path = None

        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(video_file.file.read())
                tmp_path = tmp_file.name

            # Анализ видео
            has_movement, movement_percentage, duration = self._detect_movement(tmp_path)
            processing_time = time.time() - start_time

            return {
                "has_movement": has_movement,
                "movement_percentage": round(movement_percentage, 2),
                "duration": round(duration, 2),
                "processing_time": round(processing_time, 2),
                "status": "completed"
            }

        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "has_movement": False,
                "movement_percentage": 0.0,
                "duration": 0.0,
                "processing_time": round(processing_time, 2),
                "status": "failed",
                "error_message": str(e)
            }
        finally:
            # Очистка временного файла
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _detect_movement(self, video_path: str) -> tuple[bool, float, float]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError("Cannot open video file")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames == 0:
                raise ValueError("Video has no frames")

            duration = total_frames / fps if fps > 0 else 0
            prev_frame = None
            frames_with_movement = 0
            frame_count = 0
            skip_frames = max(1, int(fps // 2))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                if frame_count % skip_frames != 0:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if prev_frame is None:
                    prev_frame = gray
                    continue

                frame_diff = cv2.absdiff(prev_frame, gray)
                thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)

                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                movement_detected = any(
                    cv2.contourArea(contour) > self.min_contour_area
                    for contour in contours
                )

                if movement_detected:
                    frames_with_movement += 1

                prev_frame = gray

            analyzed_frames = max(1, frame_count // skip_frames)
            movement_percentage = (frames_with_movement / analyzed_frames) * 100
            has_movement = movement_percentage > 10.0

            return has_movement, movement_percentage, duration

        finally:
            cap.release()