from django.contrib import admin
from .models import User, Role, Department, LeaveType, LeaveRequest, LeaveSummary, LeaveApproval, Event

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_email_verified', 'date_joined')
    list_filter = ('is_active', 'is_email_verified', 'role', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'days')
    search_fields = ('name', 'description')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'request_id', 'user', 'leave_type', 'start_date', 'end_date',
        'days', 'attachment', 'status', 'note', 'created_at', 'updated_at'
    )
    list_filter = (
        'leave_type', 'status', 'user', 'start_date', 'end_date'
    )
    search_fields = (
        'user__username', 'user__email', 'leave_type__name'
    )
    readonly_fields = ('days', 'created_at', 'updated_at')

# admin.site.register(LeaveRequest, LeaveRequestAdmin)
# class LeaveRequestAdmin(admin.ModelAdmin):
#     list_display = ('request_id', 'user', 'leave_type', 'start_date', 'end_date', 'days', 'created_at', 'updated_at')
#     list_filter = ('leave_type', 'user', 'start_date', 'end_date')
#     search_fields = ('user__username', 'leave_type__name')

@admin.register(LeaveSummary)
class LeaveSummaryAdmin(admin.ModelAdmin):
    list_display = ('summary_id', 'user', 'leave_type', 'start_date', 'end_date', 'days_taken', 'status', 'reviewed_by', 'created_at', 'updated_at')
    list_filter = ('status', 'leave_type', 'user', 'reviewed_by')
    search_fields = ('user__username', 'leave_type__name')

@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('approval_id', 'summary', 'manager', 'action', 'created_at', 'updated_at')
    list_filter = ('action', 'manager')
    search_fields = ('manager__username',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('day', 'date', 'holiday_name', 'holiday_type')
    list_filter = ('day', 'date', 'holiday_name', 'holiday_type')
    search_fields = ('day', 'date', 'holiday_name', 'holiday_type')
    readonly_fields = ('day',)

