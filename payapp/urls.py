from django.urls import include, path
from .views import home, activity, send, request, admin_users, admin_activity


urlpatterns = [
    path('', home, name='home'),
    path('home/', home,),
    path('activity/', activity, name='activity'),
    path('send/', send, name='send'),
    path('request/', request, name='request'),
    path('admin-users/', admin_users, name='admin users'),
    path('admin-activity', admin_activity, name='admin activity'),
]