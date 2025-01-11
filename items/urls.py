from django.urls import path

from items.views import ItemsListView, ItemsDetailView, CategoryView, FeaturedListView, SaveReviewView, DeleteReview, \
    ItemCreateView, ItemUpdateView, ItemDeleteView, ActiveAndInActiveItemsListView, InActiveItemsListView, \
    CategoryDeleteView, CategoryCreateListView

app_name = 'items'
urlpatterns = [
    path('items/', ItemsListView.as_view(), name='items'),
    path('featured_items/', FeaturedListView.as_view(), name='featured_items'),
    path('items/<str:slug>/', ItemsDetailView.as_view(), name='item_detail'),
    path('category/<int:id>/', CategoryView.as_view(), name='category'),
    path('save_review/', SaveReviewView.as_view(), name='save_review'),
    path('delete_review/', DeleteReview.as_view(), name='delete_review'),

    #     dashboard
    path('dashboard_items/', ActiveAndInActiveItemsListView.as_view(), name='dashboard_items'),
    path('active_items_list/', ActiveAndInActiveItemsListView.as_view(), name='active_items_list'),
    path('inactive_inactive_list/', InActiveItemsListView.as_view(), name='inactive_inactive_list'),

    path('item_create/', ItemCreateView.as_view(), name='item_create'),
    path('item_update/<int:id>/', ItemUpdateView.as_view(), name='item_update'),
    path('item_delete/<int:pk>/', ItemDeleteView.as_view(), name='item_delete'),

    path('category_list_create/', CategoryCreateListView.as_view(),
         name='dashboard_category_list_create'),
    path('category_delete/<int:pk>/', CategoryDeleteView.as_view(),
         name='dashboard_category_delete'),

]
