import os
import sys
import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gimsap.settings")
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "..", ".."))
django.setup()

from items.models import Category, Item
import json
from django.core.files.temp import NamedTemporaryFile
import requests


def upload_all_gimsap_json():
    f = open("gimsap.json", 'rb')
    data = json.load(f)
    print(data)
    for item in data:
        print(item)
        r = requests.get(item.get('image'))
        print('status code', r.status_code)
        if r.status_code == 200:
            image_temp = NamedTemporaryFile()
            image_temp.write(r.content)
            image_temp.flush()
            category = Category.objects.create(name=item['title'])
            category.image.save(os.path.basename(item.get('image')), File(image_temp), save=True)
            # looping through all products under the category
            for product in item.get('products'):
                # downloading the image
                r = requests.get(product.get('image_url'))
                print('status code', r.status_code)
                if r.status_code == 200:
                    image_temp = NamedTemporaryFile()
                    image_temp.write(r.content)
                    image_temp.flush()
                    price = product.get('price')
                    new_price = price.replace('$', '')

                    item_model = Item.objects.create(
                        name=product.get('name'),
                        price=float(new_price),
                        description=product.get('description'),
                        category=category,
                        is_active=True
                    )
                    item_model.image.save(os.path.basename(product.get('image_url')), File(image_temp), save=True)


upload_all_gimsap_json()

"""
import smtplib, ssl

port = 587  # For starttls
smtp_server = "mail.gimsap.com"
sender_email = "online@gimsap.com"
receiver_email = "codertjay@gmail.com"
password = "mXnJ7IKGV8"
message = "He there message sent "

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
"""
