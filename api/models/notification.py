from django.db import models
from api.models.user import User

class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('leave', 'Leave'),
        ('holiday', 'Holiday'),
        ('custom', 'Custom'),
        ('office', 'Office'),
    ]
    users = models.ManyToManyField(User, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.notif_type}"
