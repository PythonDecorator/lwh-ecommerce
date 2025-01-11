import csv

from django.http import HttpResponse

from items.models import Item
from dashboard.tasks import create_item_task


#  this is used to export all products in csv format
def export_products_csv():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Products.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ["id", 'name', 'price', 'discount_price', 'is_active', 'tax', 'view_count', 'category__id', 'category__name',
         'description'
         ])

    items = Item.objects.all().values_list("id", 'name', 'price', 'discount_price', 'is_active', 'tax',
                                           'view_count', 'category__id', 'category__name', 'description')
    for item in items:
        writer.writerow(item)
    return response


def read_products_csv(product_csv):
    # making it a task to enable updating faster
    decoded_file = product_csv.read().decode('utf-8').splitlines()
    create_item_task(decoded_file)
