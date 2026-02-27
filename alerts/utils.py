import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def check_and_trigger_alerts(location):
    """
    Evaluate alert conditions for a location after a count update.
    Called from any place that updates crowd count.
    """
    from .models import Alert

    alert_threshold = settings.CROWD_ALERT_THRESHOLD
    pct = location.current_count / location.capacity_limit if location.capacity_limit else 0

    # ── 1. Overcrowding alert ──────────────────────────────────────────────
    if pct >= alert_threshold:
        # Avoid duplicate active alerts of the same type
        existing = Alert.objects.filter(
            location=location,
            alert_type=Alert.TYPE_OVERCROWD,
            status=Alert.STATUS_ACTIVE,
        ).first()

        if not existing:
            alert = Alert.objects.create(
                location=location,
                alert_type=Alert.TYPE_OVERCROWD,
                message=(
                    f"{location.name} has exceeded {alert_threshold*100:.0f}% capacity. "
                    f"Current: {location.current_count}/{location.capacity_limit} "
                    f"({pct*100:.1f}%)"
                ),
                people_count_at_trigger=location.current_count,
                occupancy_at_trigger=location.occupancy_percentage,
            )
            _send_notifications(alert)
            logger.warning(f"ALERT: {alert}")

    else:
        # Resolve open overcrowd alerts when density drops
        Alert.objects.filter(
            location=location,
            alert_type=Alert.TYPE_OVERCROWD,
            status=Alert.STATUS_ACTIVE,
        ).update(status=Alert.STATUS_RESOLVED, resolved_at=timezone.now())

    # ── 2. Sudden spike alert ──────────────────────────────────────────────
    _check_spike(location)


def _check_spike(location):
    """Trigger alert if count jumps >30% in the last two readings."""
    from locations.models import CrowdLog
    from .models import Alert

    logs = CrowdLog.objects.filter(location=location).order_by('-timestamp')[:2]
    if len(logs) < 2:
        return

    latest, previous = logs[0].people_count, logs[1].people_count
    if previous == 0:
        return

    spike_ratio = (latest - previous) / previous
    if spike_ratio > 0.30:
        existing = Alert.objects.filter(
            location=location,
            alert_type=Alert.TYPE_SPIKE,
            status=Alert.STATUS_ACTIVE,
        ).first()
        if not existing:
            alert = Alert.objects.create(
                location=location,
                alert_type=Alert.TYPE_SPIKE,
                message=(
                    f"Sudden spike at {location.name}: "
                    f"{previous} → {latest} people (+{spike_ratio*100:.0f}%)"
                ),
                people_count_at_trigger=latest,
                occupancy_at_trigger=location.occupancy_percentage,
            )
            _send_notifications(alert)


def _send_notifications(alert):
    """Send email/console notification for an alert."""
    from django.core.mail import send_mail
    from django.conf import settings

    subject = f"[CrowdMonitor] {alert.alert_type} — {alert.location.name}"
    body = alert.message

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.ALERT_EMAIL_FROM,
            recipient_list=settings.ALERT_EMAIL_TO,
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")

    logger.info(f"NOTIFICATION SENT: {subject} | {body}")
