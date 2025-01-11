from datetime import timedelta

from celery import shared_task
from django.template.loader import render_to_string
from django.utils import timezone

from home.utils import gimsap_send_mail_util


def send_custom_user_email(email, password, first_name, last_name):
    gimsap_send_mail_util(
        subject="Gimsap Account Created",
        recipient_list=[email],
        html_message=render_to_string(
            'email_templates/email_base.html',
            {
                'title': "Account Was Created Using Email",
                'message': f"<p>Hi 👋 {first_name} -{last_name} </p>"
                           f"<p>Gimsap Account was created using a secured password and "
                           f"email provided by you to keep track of your order and also signin. you can change the "
                           f"password at your account at your leisure time on our website. "
                           f"</p>"
                           f"<ul>"
                           f"<li>Email: {email}</li>"
                           f"<li>Password: {password}</li>"
                ,

            }))
    return True


@shared_task
def auto_delete_order_from_in_active_customer():
    """
    We currently use this to delete customer created that doesnt have any order in his history
    2 days ago
    :return:
    """
    from users.models import Customer
    #  loop through all
    try:

        two_days_ago = timezone.now() - timedelta(days=2, seconds=1, hours=1)
        for item in Customer.objects.all():
            #  if he is not signed in currently
            if not item.user:
                #  if the customer was  created is 10 days ago

                if item.timestamp < two_days_ago:
                    #  if he has no order we delete it
                    if item.order_set.count() == 0:
                        item.delete()
                        print("deleted")
    except Exception as a:
        print("error", a)
