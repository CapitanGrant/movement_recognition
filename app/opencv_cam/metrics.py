from prometheus_client import Counter, Histogram, Gauge


# Metrics
VIDEO_PROCESSED = Counter(
    'video_processed_total',
    'Total number of videos processed',
    ['status']
)

VIDEO_PROCESSING_TIME = Histogram(
    'video_processing_time_seconds',
    'Time spent processing videos',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

VIDEO_DURATION = Histogram(
    'video_duration_seconds',
    'Duration of processed videos',
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

MOVEMENT_DETECTED = Counter(
    'movement_detected_total',
    'Total number of videos with movement detected'
)

ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Number of active requests being processed'
)


def record_video_metrics(status: str, processing_time: float, duration: float, has_movement: bool):
    """Record metrics for video processing"""
    VIDEO_PROCESSED.labels(status=status).inc()
    VIDEO_PROCESSING_TIME.observe(processing_time)
    VIDEO_DURATION.observe(duration)

    if has_movement:
        MOVEMENT_DETECTED.inc()