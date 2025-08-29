from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings



from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(user_email, property_name, start_date, end_date, total_price):
    subject = "Booking Confirmation"
    message = (
        f"Dear Customer,\n\n"
        f"Your booking for {property_name} from {start_date} to {end_date} "
        f"has been successfully confirmed.\n\n"
        f"Total Price: ${total_price}\n\n"
        f"Thank you for booking with us!"
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
    return f"Email sent to {user_email}"
