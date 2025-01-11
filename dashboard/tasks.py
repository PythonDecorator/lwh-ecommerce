import csv

from celery import shared_task

from items.models import Item, Category


@shared_task
def create_item_task(decoded_file):
    #  read the csv in dictionary format
    for row in csv.DictReader(decoded_file):
        try:
            #  get the item
            item = Item.objects.get(id=int(row.get("id")))
            if item:
                item.name = row.get("name")
                item.description = row.get("description")
                #  if the  price is not "" because the csv returns and empty
                #  string, so it cant be added
                if row.get("price") != "":
                    print(row.get("price"))
                    item.price = row.get("price")
                if row.get("discount_price") != "":
                    print(row.get("discount_price"))
                    item.discount_price = row.get("discount_price")
                if row.get("is_active") != "":
                    item.is_active = row.get("is_active").title()
                if row.get("tax") != "":
                    item.tax = row.get("tax").title()
                if row.get("view_count") != "":
                    item.view_count = int(row.get("view_count"))
                item.save()
                #  update the category  the id of the category provided but i check if it exist in the database first
                if row.get("category__id") != "":
                    if item.category_id != int(row.get("category__id")):
                        category = Category.objects.get(id=int(row.get("category__id")))
                        if category:
                            item.category = category
                            item.save()
                print("Updated")
        except Exception as a:
            print("The error was ", a)
