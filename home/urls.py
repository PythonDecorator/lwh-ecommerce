from django.urls import path

from home.views import HomePageView, ContactView, AboutView, OffersListView, FaqView, FaqCreateListView, FaqDeleteView, \
    DashboardContactCreateListView, \
    DashboardContactDeleteView, DashboardContactDetailView, SubscribeView, TermsPageView, PrivacyPolicyPageView, \
    ShippingPolicyPageView, RefundPolicyPageView, signup_redirect_view

app_name = 'home'
urlpatterns = [
    path('', HomePageView.as_view(), name='home_page'),
    path('contact/', ContactView.as_view(), name='contact_page'),
    path('about/', AboutView.as_view(), name='about_page'),
    path('offers/', OffersListView.as_view(), name='offer_page'),
    path('terms_and_condition/', TermsPageView.as_view(), name='terms_and_condition'),
    path('privacy_policy/', PrivacyPolicyPageView.as_view(), name='privacy_policy'),
    path('shipping_policy/', ShippingPolicyPageView.as_view(), name='shipping_policy'),
    path('refund_policy/', RefundPolicyPageView.as_view(), name='refund_policy'),

    # api
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),

    path('faq/', FaqView.as_view(), name='faq_page'),
    path('faq_list_create/', FaqCreateListView.as_view(),
         name='dashboard_faq_list_create'),
    path('faq_delete/<int:pk>/', FaqDeleteView.as_view(),
         name='dashboard_faq_delete'),

    path('contact_list_create/', DashboardContactCreateListView.as_view(),
         name='dashboard_contact_list_create'),

    path('contact_delete/<int:pk>/', DashboardContactDeleteView.as_view(),
         name='dashboard_contact_delete'),

    path('contact_detail/<int:pk>/', DashboardContactDetailView.as_view(),
         name='dashboard_contact_detail'),

    path('accounts/signup/None/', signup_redirect_view, name='signup_redirect')

]
