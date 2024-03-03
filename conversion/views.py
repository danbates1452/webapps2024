from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer

currency_map = {
    'GBP': {
        'USD': 1.3,
        'EUR': 1.1,
    },
    'USD': {
        'GBP': 0.7,
        'EUR': 0.8,
    },
    'EUR': {
        'GBP': 0.9,
        'USD': 1.2,
    },
}


def validate_currency(currency):
    if currency not in settings.CURRENCIES:
        raise ValidationError(
            message="%(currency) is not a valid currency on this system.",
            params={'currency': currency}
        )


def convert(request):
    if request.GET:
        try:
            currency1 = validate_currency(request.GET['currency1'])
            currency2 = validate_currency(request.GET['currency2'])
            amount_of_currency1 = request.GET['amount_of_currency1']

            if currency1 == currency2:
                rate = 1
            else:
                rate = currency_map[currency1][currency2]

            converted_amount = Decimal(rate * amount_of_currency1)

            return Response(data=ListSerializer(data=[rate, converted_amount], allow_empty=False))

        except ValidationError as e:
            messages.add_message(request, messages.ERROR, e)
            print(e)  # todo: remove in submission
            return Response(data=ListSerializer(data=e, allow_empty=False))
