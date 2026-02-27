from django.db import models
from django.conf import settings


class Location(models.Model):
    DENSITY_LOW = 'LOW'
    DENSITY_MEDIUM = 'MEDIUM'
    DENSITY_HIGH = 'HIGH'

    DENSITY_CHOICES = [
        (DENSITY_LOW, 'Low'),
        (DENSITY_MEDIUM, 'Medium'),
        (DENSITY_HIGH, 'High'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    capacity_limit = models.PositiveIntegerField(default=100)
    current_count = models.PositiveIntegerField(default=0)
    density_level = models.CharField(
        max_length=10, choices=DENSITY_CHOICES, default=DENSITY_LOW
    )
    is_active = models.BooleanField(default=True)
    camera_url = models.CharField(
        max_length=500, blank=True,
        help_text='RTSP URL or webcam index (e.g., 0, 1, rtsp://...)'
    )
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.density_level})"

    @property
    def occupancy_percentage(self):
        if self.capacity_limit == 0:
            return 0
        return round((self.current_count / self.capacity_limit) * 100, 1)

    def calculate_density(self):
        low_thresh = settings.CROWD_LOW_THRESHOLD
        high_thresh = settings.CROWD_HIGH_THRESHOLD
        pct = self.current_count / self.capacity_limit if self.capacity_limit else 0

        if pct < low_thresh:
            return self.DENSITY_LOW
        elif pct < high_thresh:
            return self.DENSITY_MEDIUM
        else:
            return self.DENSITY_HIGH

    def update_count(self, count: int):
        self.current_count = max(0, count)
        self.density_level = self.calculate_density()
        self.save(update_fields=['current_count', 'density_level', 'last_updated'])


class CrowdLog(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='logs'
    )
    people_count = models.PositiveIntegerField()
    density_level = models.CharField(max_length=10)
    occupancy_percentage = models.FloatField()
    source = models.CharField(
        max_length=20,
        choices=[('AI', 'AI Detection'), ('MANUAL', 'Manual Entry')],
        default='AI'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['location', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.location.name} @ {self.timestamp:%Y-%m-%d %H:%M} — {self.people_count} people"
