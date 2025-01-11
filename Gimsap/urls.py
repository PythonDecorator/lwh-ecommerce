from decouple import config
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import urls
from home import views

urls.handler404 = views.view_404
urls.handler500 = views.view_500
urls.handler403 = views.view_403
urls.handler400 = views.view_400

admin_url = config('ADMIN_URL', default='admin')
urlpatterns = [
    path('', include('home.urls'), name='home'),
    path('admin/', admin.site.urls, name='admin'),
    path('product/', include('items.urls'), name='items'),
    path('user/', include('users.urls')),
    path('order/', include('orders.urls')),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

# todo
# move avatar for not loggedin
