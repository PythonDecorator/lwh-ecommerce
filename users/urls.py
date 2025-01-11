from django.urls import path

from .views import ProfilePageView, UpdateUserProfileAPIView

app_name = 'user'
urlpatterns = [
    path('profile/', ProfilePageView.as_view(), name='profile_page'),
    path('update_profile_api/', UpdateUserProfileAPIView.as_view(), name='update_profile_api')
]
