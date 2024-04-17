from django.urls import path

from .views import timestamp_view

urlpatterns = [
    path('', timestamp_view, name='timestamp')
]
