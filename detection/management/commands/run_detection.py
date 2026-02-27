"""
Django management command to continuously poll camera feeds
and update crowd counts.

Usage:
    python manage.py run_detection
    python manage.py run_detection --mode haar --interval 10
"""

import time
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run continuous crowd detection for all active locations with cameras.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode', default='yolo', choices=['yolo', 'haar'],
            help='Detection mode (default: yolo)'
        )
        parser.add_argument(
            '--interval', type=int, default=settings.DETECTION_INTERVAL,
            help='Seconds between detection runs (default: 5)'
        )
        parser.add_argument(
            '--location', type=int, default=None,
            help='Only process this location ID'
        )

    def handle(self, *args, **options):
        from detection.detector import get_detector
        from locations.models import Location
        from locations.views import _broadcast_update
        from locations.models import CrowdLog
        from alerts.utils import check_and_trigger_alerts

        mode = options['mode']
        interval = options['interval']
        location_id = options['location']

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting crowd detection | mode={mode} | interval={interval}s"
            )
        )

        detector = get_detector(mode)

        while True:
            qs = Location.objects.filter(is_active=True).exclude(camera_url='')
            if location_id:
                qs = qs.filter(pk=location_id)

            for location in qs:
                try:
                    source = location.camera_url
                    # Convert numeric string to int for local webcam
                    if source.isdigit():
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

                    self.stdout.write(
                        f"  [{location.name}] count={count} density={location.density_level}"
                    )

                except Exception as e:
                    logger.error(f"Detection error for {location.name}: {e}")

            time.sleep(interval)
