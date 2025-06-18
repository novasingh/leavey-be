from django.db import models
from api.models.user import User

class NotificationSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_setting')
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    # Add more fields as needed (e.g., per-type preferences)

    def __str__(self):
        return f"Notification settings for {self.user.email}"
