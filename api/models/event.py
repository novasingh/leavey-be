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
        if self.date:
            # Automatically fill day name from date
            self.day = self.date.strftime('%A')  # e.g. 'Monday', 'Tuesday'
        super().save(*args, **kwargs)