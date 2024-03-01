from django.contrib import admin
from django.urls import include, path
from payapp import views as payapp_views


urlpatterns = [
    #path('admin/', <>, name='admin'), #todo: admin panel inside payapp?
    path('activity/', payapp_views.activity, name='activity'),
    path('send/', payapp_views.send, name='send'),
    path('request/', payapp_views.request, name='request'),

    path('admin-users/', payapp_views.admin_users, name='admin users'),
    path('admin-activity', payapp_views.admin_activity, name='admin activity'),
]