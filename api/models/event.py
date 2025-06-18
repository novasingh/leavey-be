from django.db import models
import datetime

HOLIDAY_TYPE_CHOICES = [
    ('Public Holiday', 'Public Holiday'),
    ('Company Birthday', 'Company Birthday'),
    ('Company Holiday', 'Company Holiday'),
]

class Event(models.Model):
    day = models.CharField(max_length=20, blank=True)
    date = models.DateField()              # e.g., 2025-06-17
    holiday_name = models.CharField(max_length=100)  # e.g., Eid Adha
    holiday_type = models.CharField(max_length=50, choices=HOLIDAY_TYPE_CHOICES)

    # def _str_(self):
    #     return f"{self.holiday_name} on {self.date}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_date = None
        if not is_new:
            old = Event.objects.get(pk=self.pk)
            old_date = old.date
        if self.date:
            # Automatically fill day name from date
            self.day = self.date.strftime('%A')  # e.g. 'Monday', 'Tuesday'
        super().save(*args, **kwargs)
        # Notification logic
        from api.utils.notifications import send_email_notification, send_in_app_notification
        from api.models.user import User
        # Notify all users on new or changed holiday
        if is_new or (old_date and self.date != old_date):
            users = User.objects.filter(is_active=True)
            send_email_notification(users, f"New Holiday: {self.holiday_name}", f"{self.holiday_name} is on {self.date}.")
            send_in_app_notification(users, f"New Holiday: {self.holiday_name}", f"{self.holiday_name} is on {self.date}.", 'holiday')