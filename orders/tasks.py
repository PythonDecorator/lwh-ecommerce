import time

from celery import shared_task
from decouple import config
from django.template.loader import render_to_string

from home.utils import gimsap_send_mail_util


@shared_task
def successful_order_message_for_pickup(email, first_name, last_name, ref_code, price, pickup_name, pickup_location):
    gimsap_send_mail_util(
        subject="Order was Successful",
        recipient_list=[email],
        html_message=render_to_string(
            'email_templates/email_base.html',
            {
                'title': "Order was Successful",
                'message': f"<h4>Hi 👋 {first_name} -{last_name} </h4>"
                           f"<p>You just made an order at this price rate  ${price}."
                           f"You can get your order at this location <strong>{pickup_location}</strong>"
                           f" and the name of the place is {pickup_name}.</p>"
                           f"<p> The reference code is <span><strong>{ref_code}</strong></span> which could be use if you would like "
                           f"to contact customer support if having any issues .</p>"

            })
    )

    # added sleep to slow down processing to prevent issues on the mail server
    time.sleep(10)

    gimsap_send_mail_util(
        subject="Customer Just made an active Order",
        recipient_list=[config('ADMIN_MAIL'), config('CUSTOMER_SUPPORT')],
        html_message=render_to_string(
            'email_templates/email_base.html',
            {
                'title': "Customer Just made an active Order",
                'message': f"<h4>Hi 👋 Gimsap </h4>"
                           f"A customer named {first_name} -{last_name} -{email} has made an order at this price rate "
                           f"<strong>${price}</strong> ."
                           f" Customer will be picking up order at this location <strong>{pickup_location}</strong>."
                           f" and the name of the place is <strong>{pickup_name}</strong>.<br/>"
                           f" The reference code is <span><strong>{ref_code}</strong></span>"
                           f" which could be used to get info about the order.</p> "
            })

    )
    return True


@shared_task
def successful_order_message_for_shipping(
        email,
        first_name,
        last_name,
        phone_number,
        ref_code,
        price,
        country,
        state,
        apartment_address,
        zip_code,
        routine,
        routine_price):
    gimsap_send_mail_util(
        subject="Order was Successful",
        recipient_list=[email],
        html_message=render_to_string(
            'email_templates/email_base.html',
            {
                'title': "Order was Successful",
                'message': f"<p>Hi 👋 {first_name} -{last_name} </p>"
                           f"<p>You just made an order at this price rate <span><strong>${price}</strong></span>. <br/>"
                           f" The reference code is of your order is <span><strong>{ref_code}</strong></span>"
                           f" Which could be use if you would like "
                           f"to contact customer support if having any issues .</p>"
                           f"<div>Your order will be delivered .</div>"
                           f"<ul>"
                           f"<li>Country: {country}</li>"
                           f"<li>State: {state}</li>"
                           f"<li>Apartment Address: {apartment_address}</li>"
                           f"<li>Zip Code: {zip_code}</li>"
                           f"<li>Routine: {routine}</li>"
                           f"<li>Routine Price: {routine_price}</li>"
                           f" .</ul>"

            })

    )

    # added sleep to slow down processing to prevent issues on the mail server
    time.sleep(10)

    gimsap_send_mail_util(
        subject="Customer Just made an active Order",
        recipient_list=[config('ADMIN_MAIL'), config('CUSTOMER_SUPPORT')],
        html_message=render_to_string(
            'email_templates/email_base.html',
            {
                'title': "Customer Just made an active Order",
                'message': f"<h3>Hi 👋 Gimsap </h3>"
                           f"<p/> A customer named {first_name} -{last_name} just made an order at this price rate ${price}. <br/>"
                           f"The reference code is <strong>{ref_code}</strong>"
                           f" which could be used to get info about the order.</p> "
                           f"<div>The order should be delivered at.</div>"
                           f"<ul>"
                           f"<li>Country: {country}</li>"
                           f"<li>State: {state}</li>"
                           f"<li>Apartment Address: {apartment_address}</li>"
                           f"<li>Zip Code: {zip_code}</li>"
                           f"<li>Routine: {routine}</li>"
                           f"<li>Routine Price: ${routine_price}</li>"
                           f"<li>Customer Email: {email}</li>"
                           f"<li>Customer Phone number: {phone_number}</li>"
                           f" </ul>"
            })

    )
    return True
