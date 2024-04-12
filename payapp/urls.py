from django.urls import include, path
from .views import home, activity, send_money, request_money, admin_users, admin_activity


urlpatterns = [
    path('', home, name='home'),
    path('home/', home,),
    path('activity/', activity, name='activity'),
    path('send/', send_money, name='send'),
    path('request/', request_money, name='request'),
    path('admin-users/', admin_users, name='admin-users'),
    path('admin-activity', admin_activity, name='admin-activity'),
]