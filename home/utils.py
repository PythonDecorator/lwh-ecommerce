from email.mime.image import MIMEImage
from urllib.request import urlopen

import googlemaps
from decouple import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from post_office import mail

GOOGLE_API_KEY = settings.GOOGLE_API_KEY
domain_url = config('DOMAIN_URL')
FROM_MAIL = settings.DEFAULT_FROM_EMAIL


def gimsap_send_mail_util(
        subject,
        recipient_list,
        html_message, ):
    # msg = EmailMultiAlternatives(subject, html_message, recipient_list, reply_to=["info@gimsap@gmail.com"])
    # msg.content_subtype = 'html'  # Main content is text/html
    # msg.mixed_subtype = 'related'  # This is critical, otherwise images will be displayed as attachments!
    # msg.attach_alternative(html_message, "text/html")
    # url = f"{domain_url}/static/assets/images/logo.png"
    # msg_image = MIMEImage(urlopen(url).read())
    # msg_image.add_header('Content-ID', 'image1')
    # msg.attach(msg_image)
    # msg.send(fail_silently=False)
    mail.send(
        recipient_list,
        FROM_MAIL,
        subject=subject,
        html_message=html_message,
        headers={'Reply-to': 'info@gimsap.com'},
    )

    return True


def get_reviews():
    try:
        gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
        place_name = "Gimsap African Asian Market"
        places_result = gmaps.places(place_name)
        place_id = places_result['results'][0]['place_id']
        place = gmaps.place(place_id=place_id)
        reviews = place['result']['reviews']
    except Exception as a:
        print(a)
        reviews = {}
    return reviews
