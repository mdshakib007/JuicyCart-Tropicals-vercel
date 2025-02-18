from django.db.models.signals import post_save
from django.dispatch import receiver
from order.models import Order
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@receiver(post_save, sender=Order)
def send_order_status_email(sender, instance, created, **kwargs):
    if created:
        subject = "Order Placed Successfully"
        template = 'order/order_placed.html'
        message_context = {
            'order': instance,
            'status': instance.status,
        }
    else:
        subject = f"Order Status Updated: {instance.status}"
        template = 'order/order_status_update.html'
        message_context = {
            'order': instance,
            'status': instance.status,
        }

    # Render email content
    email_body = render_to_string(template, message_context)
    email = EmailMultiAlternatives(subject, '', to=[instance.customer.user.email])
    email.attach_alternative(email_body, 'text/html')
    email.send()
