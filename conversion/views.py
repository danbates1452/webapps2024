from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.core.exceptions import ValidationError
from decimal import Decimal

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

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
    return currency


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def convert(request, currency1, currency2, amount_of_currency1):
    try:
        currency1 = validate_currency(currency1)
        currency2 = validate_currency(currency2)
        amount_of_currency1 = abs(float(amount_of_currency1))

        if currency1 == currency2:
            rate = 1
        else:
            rate = currency_map[currency1][currency2]

        converted_amount = Decimal(rate * amount_of_currency1)

        data = [rate, converted_amount]
        # serialized_data = serializers.serialize("json", data)

        return Response(data=data)

    except ValidationError as error:
        messages.add_message(request, messages.ERROR, error)
        print(error)  # todo: remove in submission
        serialized_error = serializers.serialize("json", error)
        return Response(data=serialized_error, status=422)
