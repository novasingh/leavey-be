from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from api.models.notification import Notification

def send_email_notification(users, subject, message, template=None, context=None):
    for user in users:
        if user.email:
            try:
                html_message = None
                if template and context:
                    context = context.copy()
                    context['user'] = user
                    html_message = render_to_string(template, context)
                    plain_message = strip_tags(html_message)
                else:
                    plain_message = message
                send_mail(
                    subject,
                    plain_message,
                    None,
                    [user.email],
                    html_message=html_message if template and context else None,
                    fail_silently=True,
                )
            except Exception:
                pass

def send_in_app_notification(users, title, message, notif_type):
    notif = Notification.objects.create(
        title=title,
        message=message,
        notif_type=notif_type
    )
    notif.users.set(users)
    notif.save()
