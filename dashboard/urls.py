from django.urls import path

from .views import DashBoardView, CouponCreateListView, CouponDeleteView

app_name = 'dashboard'
urlpatterns = [
    path('', DashBoardView.as_view(), name='dashboard_page'),
    path('coupon_create_list/', CouponCreateListView.as_view(), name='coupon_create_list'),
    path('coupon_delete/<int:pk>/', CouponDeleteView.as_view(), name='coupon_delete'),

]
