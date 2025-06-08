from django.db import models
from api.models.user import User
from api.models.role import Role

class LeaveType(models.Model):
    leave_type_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    days = models.PositiveIntegerField()  # Restrict to non-negative numbers
    is_active = models.BooleanField(default=True)  # Admin can disable instead of deleting

    def __str__(self):
        return self.name
    

class LeaveRequest(models.Model):
    request_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.FloatField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='leave_attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ], default='Pending')
    note = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.days = (self.end_date - self.start_date).days + 1
        else:
            self.days = None
        super().save(*args, **kwargs)

class LeaveSetting(models.Model):
    # Working Hours
    working_hours_start = models.TimeField(default='09:00')
    working_hours_end = models.TimeField(default='17:00')
    is_flexible_hours_enabled = models.BooleanField(default=False)

    # Working Days
    is_weekday_workday = models.BooleanField(default=True)
    is_weekend_workday = models.BooleanField(default=False)

    # Leave Cycle
    # CharField to store the choice, e.g., 'annual' or 'join_date'
    cycle_type = models.CharField(max_length=20, default='annual')

    # This ensures there is only one settings object in the database
    singleton_id = models.PositiveIntegerField(primary_key=True, default=1, editable=False)

    def __str__(self):
        return "Company Leave Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(LeaveSetting, self).save(*args, **kwargs)