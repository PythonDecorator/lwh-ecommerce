import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gimsap.settings")
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "..", ".."))
django.setup()

from django.http import HttpResponse
import csv
from items.models import Item


def export_products_csv():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    with open('./Products.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["id", 'name', 'price', 'discount_price', 'is_active', 'tax', 'view_count', 'description'
             ])

        users = Item.objects.all().values_list("id", 'name', 'price', 'discount_price', 'is_active', 'tax',
                                               'view_count', 'description')
        for user in users:
            writer.writerow(user)
    return response


def read_products_csv():
    with open('./Products.csv', 'r') as fp:
        # You can also put the relative path of csv file
        # with respect to the manage.py file
        for row in csv.DictReader(fp):
            try:
                print(row)
                item = Item.objects.get(id=int(row.get("id")))
                if item:
                    item.name = row.get("name")
                    #  if the  price is not "" because the csv returns and empty
                    #  string, so it cant be added
                    if row.get("price") != "":
                        item.price = row.get("price")
                    if row.get("discount_price") != "":
                        item.discount_price = row.get("discount_price")
                    item.is_active = row.get("is_active")
                    item.tax = row.get("tax")
                    item.view_count = row.get("view_count")
                    item.description = row.get("description")
                    item.save()
            except Exception as a:
                print(a)


read_products_csv()
