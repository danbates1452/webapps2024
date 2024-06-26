from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from bootstrap_customizer import urls as bootstrap_customizer_urls
from django.views.generic import RedirectView

from register import views as register_views


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('bootstrap_customizer/', include(bootstrap_customizer_urls)),
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon.ico')),

    path('', include('payapp.urls')),
    path('register/', register_views.register_user, name='register'),
    path('login/', register_views.login_user, name='login'),
    path('logout/', register_views.logout_user, name='logout'),
    path('conversion/', include('conversion.urls')),
    path('timestamp/', include('timestampapp.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
