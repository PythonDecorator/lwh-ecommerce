from django.urls import path

from .views import WishListView, CheckoutView, ApplyCouponView, AddToCartView, RemoveFromCartView, RemoveSingleFromCart, \
    MakePaymentView, ChangePickUpLocationView, ChangeShippingRoutineView, OrderHistoryListView, OrderHistoryDetailView, \
    UpdateShippingAddressView, OrderedOrderListView, NotOrderedOrderListView, OrderListView, OrderDetailUpdateView, \
    OrderDeleteView, PickupCreateListView, PickupDeleteView, ShippingRoutineCreateListView, ShippingRoutineDeleteView, \
    CreatPaypalOrderView, CapturePaypalOrderView

app_name = 'order'
urlpatterns = [

    # paypal url for communication
    path('create_paypal_order/', CreatPaypalOrderView.as_view(), name='create_paypal_order'),
    path('capture_paypal_order/', CapturePaypalOrderView.as_view(), name='capture_paypal_order'),

    # home page
    path('wishlist/', WishListView.as_view(), name='wishlist'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('ApplyCoupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('addToCart/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove_from_cart/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('remove_single_from_cart/', RemoveSingleFromCart.as_view(), name='remove_single_from_cart'),
    path('make_payment/<int:id>/', MakePaymentView.as_view(), name='make_payment'),
    path('change_pickup_location/', ChangePickUpLocationView.as_view(), name='change_pickup_location'),
    path('change_shipping_routine/', ChangeShippingRoutineView.as_view(), name='change_shipping_routine'),
    path('update_shipping_address/', UpdateShippingAddressView.as_view(), name='update_shipping_address'),
    path('order_history/', OrderHistoryListView.as_view(), name='order_history'),
    path('order_history_detail/<int:id>/', OrderHistoryDetailView.as_view(), name='order_history_detail'),

    #     dashboard
    path('order_list/', OrderListView.as_view(), name='dashboard_order_list'),
    path('active_order_list/', OrderedOrderListView.as_view(), name='dashboard_active_order_list'),
    path('inactive_order_list/', NotOrderedOrderListView.as_view(), name='dashboard_inactive_order_list'),
    path('dashboard_order_detail_update/<int:id>/', OrderDetailUpdateView.as_view(),
         name='dashboard_order_detail_update'),
    path('dashboard_order_delete/<int:pk>/', OrderDeleteView.as_view(),
         name='dashboard_order_delete'),
    path('pickup_list_create/', PickupCreateListView.as_view(),
         name='dashboard_pickup_list_create'),
    path('pickup_delete/<int:pk>/', PickupDeleteView.as_view(),
         name='dashboard_pickup_delete'),
    path('routine_list_create/', ShippingRoutineCreateListView.as_view(),
         name='dashboard_routine_list_create'),
    path('routine_delete/<int:pk>/', ShippingRoutineDeleteView.as_view(),
         name='dashboard_routine_delete'),

]
