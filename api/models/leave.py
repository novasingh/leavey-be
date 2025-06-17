from django.db import models
from api.models.user import User
from api.models.role import Role

class LeaveType(models.Model):
    leave_type_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default="#000000")

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
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old = LeaveRequest.objects.get(pk=self.pk)
            old_status = old.status
        if self.start_date and self.end_date:
            self.days = (self.end_date - self.start_date).days + 1
        else:
            self.days = None
        super().save(*args, **kwargs)
        # Notification logic
        from api.utils.notifications import send_email_notification, send_in_app_notification
        # Notify manager on new leave request
        if is_new:
            manager = self.user.department.manager if hasattr(self.user, 'department') and self.user.department else None
            if manager:
                send_email_notification([manager], "New Leave Request", f"{self.user.get_full_name()} has requested leave.")
                send_in_app_notification([manager], "New Leave Request", f"{self.user.get_full_name()} has requested leave.", 'leave')
        # Notify employee on approval/rejection
        elif old_status and self.status in ['Approved', 'Rejected'] and self.status != old_status:
            send_email_notification([self.user], f"Leave {self.status}", f"Your leave request has been {self.status.lower()}.")
            send_in_app_notification([self.user], f"Leave {self.status}", f"Your leave request has been {self.status.lower()}.", 'leave')

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
        # Notification logic for office timing change
        from api.utils.notifications import send_email_notification, send_in_app_notification
        from api.models.user import User
        # Notify all users if working hours change
        if self.pk == 1 and (self.working_hours_start != '09:00' or self.working_hours_end != '17:00'):
            users = User.objects.filter(is_active=True)
            send_email_notification(users, "Office Timing Changed", f"New office hours: {self.working_hours_start} - {self.working_hours_end}")
            send_in_app_notification(users, "Office Timing Changed", f"New office hours: {self.working_hours_start} - {self.working_hours_end}", 'office')