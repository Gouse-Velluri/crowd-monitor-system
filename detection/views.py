import base64
import logging
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class DetectFromImageView(APIView):
    """
    POST /api/detection/detect/
    Body: { "image": "<base64 jpeg/png>", "mode": "yolo" }
    Returns: { "count": 5 }
    """

    def post(self, request):
        image_b64 = request.data.get('image')
        mode = request.data.get('mode', 'yolo')

        if not image_b64:
            return Response({'error': 'image field required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            img_bytes = base64.b64decode(image_b64)
            import cv2
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return Response({'error': f'Invalid image: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        from detection.detector import get_detector
        detector = get_detector(mode)
        count = detector.detect_from_frame(frame)

        return Response({'count': count, 'mode': mode})


class DetectAndUpdateView(APIView):
    """
    POST /api/detection/detect/<location_id>/
    Runs detection on a camera and immediately updates the location.
    """

    def post(self, request, location_id):
        from locations.models import Location, CrowdLog
        from locations.views import _broadcast_update
        from alerts.utils import check_and_trigger_alerts
        from detection.detector import get_detector

        try:
            location = Location.objects.get(pk=location_id, is_active=True)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=404)

        mode = request.data.get('mode', 'yolo')
        detector = get_detector(mode)

        source = location.camera_url or 0
        if isinstance(source, str) and source.isdigit():
            source = int(source)

        count = detector.detect_from_camera(source=source, duration_seconds=2)
        location.update_count(count)

        CrowdLog.objects.create(
            location=location,
            people_count=count,
            density_level=location.density_level,
            occupancy_percentage=location.occupancy_percentage,
            source='AI',
        )

        check_and_trigger_alerts(location)
        _broadcast_update(location)

        return Response({
            'location_id': location.id,
            'location_name': location.name,
            'count': count,
            'density_level': location.density_level,
        })
