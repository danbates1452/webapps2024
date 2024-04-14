from django.urls import include, path, register_converter
from .views import convert
from decimal import Decimal

urlpatterns = [
    path('<str:currency1>/<str:currency2>/<str:amount_of_currency1>', convert),
]
