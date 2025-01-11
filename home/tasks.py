from celery import shared_task
from decouple import config
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string

from home.models import Contact
from home.utils import gimsap_send_mail_util


@shared_task
def send_support_message(subject, message):
    gimsap_send_mail_util(
        subject=subject,
        recipient_list=[config('ADMIN_MAIL'), config('CUSTOMER_SUPPORT')],
        html_message=render_to_string(
            'email_templates/email_base.html',
            {
                'title': subject,
                'message': f"<p> {message}</p>"
            })
        ,
    )
    return True


@shared_task
def send_customers_message(email=None, all_users=None, subject='', message=''):
    if email:
        gimsap_send_mail_util(
            subject=subject,
            recipient_list=[config('ADMIN_MAIL'), config('CUSTOMER_SUPPORT')],
            html_message=render_to_string(
                'email_templates/email_base.html',
                {
                    'title': subject,
                    'message': f"<p> {message}</p>"
                })
        )

    if all_users:
        print('all users')
        for user in User.objects.all():
            gimsap_send_mail_util(
                subject=subject,
                recipient_list=[user.email],
                html_message=render_to_string(
                    'email_templates/email_base.html',
                    {
                        'title': subject,
                        'message': f"<p> {message}</p>"
                    })
            )
    Contact.objects.create(message=message, email='info@gimsap.com', subject=subject, name='Gimsap')
    return True
