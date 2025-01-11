import operator
from functools import reduce

from django.db.models import Q
from textblob import TextBlob


def query_items(query, item):
    query_list = []
    correct_query = TextBlob(str(query)).correct()
    price_query = 0
    if isinstance(query, str):
        price_query = 0
    query_list += query.split()
    query_list = sorted(query_list, key=lambda x: x[-1])
    print(query_list)
    query = reduce(
        operator.or_,
        (Q(name=x) |
         Q(name__contains=x) |
         Q(name__icontains=x) |
         Q(name__contains=x) |
         Q(name__in=[x]) |
         Q(category__name__icontains=x) |
         Q(description__icontains=x) |
         Q(description__contains=x) |
         Q(description__in=[x]) |
         Q(price=price_query) |
         Q(slug__contains=x) for x in query_list)
    )
    object_list = item.filter(query).distinct().reverse()
    print(object_list)
    return object_list
