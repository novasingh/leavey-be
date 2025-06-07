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
        ('Cancelled', 'Cancelled'),
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



# class LeaveRequest(models.Model):
#     request_id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
#     leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name='leave_requests')
#     start_date = models.DateField()
#     end_date = models.DateField()
#     message = models.TextField(blank=True, null=True)
#     attachment = models.FileField(upload_to='leave_attachments/', blank=True, null=True)
#     days = models.IntegerField(blank=True, null=True)  # New DB column
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         # Calculate days before saving
#         if self.start_date and self.end_date:
#             self.days = (self.end_date - self.start_date).days + 1
#         else:
#             self.days = None
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"LeaveRequest({self.request_id}) by {self.user}"

class LeaveSummary(models.Model):
    summary_id = models.BigAutoField(primary_key=True)
    request = models.ForeignKey('LeaveRequest', on_delete=models.CASCADE, related_name='summaries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_summaries')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name='leave_summaries')  # Adjust if LeaveType model exists
    start_date = models.DateField()
    end_date = models.DateField()
    days_taken = models.FloatField(blank=True, null=True)  # Auto-calculated
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leave_summaries')
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-calculate days_taken
        if self.start_date and self.end_date:
            self.days_taken = (self.end_date - self.start_date).days + 1
        else:
            self.days_taken = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"LeaveSummary({self.summary_id}) for request {self.request_id}"

class LeaveApproval(models.Model):
    approval_id = models.BigAutoField(primary_key=True)
    summary = models.ForeignKey(LeaveSummary, on_delete=models.CASCADE, related_name='approvals')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_approvals')
    action = models.CharField(max_length=10, choices=[('Approved', 'Approved'), ('Rejected', 'Rejected')])
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update the status in LeaveSummary when approval is made
        if self.action == 'Approved':
            self.summary.status = 'Approved'
            self.summary.rejection_reason = None
        elif self.action == 'Rejected':
            self.summary.status = 'Rejected'
            self.summary.rejection_reason = self.message
        self.summary.reviewed_by = self.manager
        self.summary.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"LeaveApproval({self.approval_id}) for summary {self.summary_id} by {self.manager}"