from django.urls import include, path, register_converter
from views import convert
from decimal import Decimal


class DecimalConverter:
    regex = "^(\d+\.\d{2})$"

    def to_python(self, value):
        return Decimal(value)

    def to_url(self, value):
        return str(value)


register_converter(DecimalConverter, "decimal")

urlpatterns = [
    path('<str:currency1>/<str:currency2>/<decimal:amount_of_currency1>', convert),
]
