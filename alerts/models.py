from django.db import models


class Alert(models.Model):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_RESOLVED = 'RESOLVED'

    TYPE_OVERCROWD = 'OVERCROWD'
    TYPE_SPIKE = 'SPIKE'
    TYPE_PROLONGED = 'PROLONGED'

    STATUS_CHOICES = [(STATUS_ACTIVE, 'Active'), (STATUS_RESOLVED, 'Resolved')]
    TYPE_CHOICES = [
        (TYPE_OVERCROWD, 'Overcrowding'),
        (TYPE_SPIKE, 'Sudden Spike'),
        (TYPE_PROLONGED, 'Prolonged High Density'),
    ]

    location = models.ForeignKey(
        'locations.Location', on_delete=models.CASCADE, related_name='alerts'
    )
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    people_count_at_trigger = models.PositiveIntegerField(default=0)
    occupancy_at_trigger = models.FloatField(default=0)

    class Meta:
        ordering = ['-triggered_at']

    def __str__(self):
        return f"[{self.alert_type}] {self.location.name} @ {self.triggered_at:%Y-%m-%d %H:%M}"

    def resolve(self):
        from django.utils import timezone
        self.status = self.STATUS_RESOLVED
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at'])
