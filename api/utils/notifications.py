from django.core.mail import send_mail, BadHeaderError
from api.models.notification import Notification

def send_email_notification(users, subject, message):
    for user in users:
        if user.email:
            try:
                send_mail(subject, message, None, [user.email])
            except Exception:
                # If email fails, just skip and continue
                pass

def send_in_app_notification(users, title, message, notif_type):
    notif = Notification.objects.create(
        title=title,
        message=message,
        notif_type=notif_type
    )
    notif.users.set(users)
    notif.save()
