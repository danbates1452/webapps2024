from decimal import Decimal
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.db import transaction
from django.shortcuts import redirect
from djmoney.money import Money
from requests.adapters import HTTPAdapter, Retry

from payapp.models import Person


def get_current_person(request):
    return Person.objects.filter(user__exact=request.user.id)[0]


def admin_area(check_user):
    if check_user.is_staff and check_user.is_superuser:
        return True
    else:
        return redirect('home')


SITE_URI = 'https://' + Site.objects.get_current().domain
CURRENCY_CONVERTER_API_URI = SITE_URI + '/conversion'
TIMESTAMP_SERVICE_API_URI = SITE_URI + '/timestamp'
retry_strategy = Retry(total=settings.LOCAL_API_RETRY_MAX_RETRIES,
                       backoff_factor=settings.LOCAL_API_RETRY_BACKOFF_FACTOR,
                       status_forcelist=settings.LOCAL_API_RETRY_STATUS_FORCELIST
                       )


def call_api(uri, verify_certificate=False):
    # SSL certificate checking is disabled as ours is self-signed and will cause an error
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
    response = session.get(uri, verify=verify_certificate)
    return response.json()


def call_currency_converter(currency_from, currency_to, amount_from):
    request_uri = '/'.join([CURRENCY_CONVERTER_API_URI, currency_from, currency_to, str(amount_from)])

    json_response = call_api(request_uri)
    rate = json_response[0]
    amount_to = json_response[1]
    return rate, amount_to


def call_timestamp_service():
    return str(call_api(TIMESTAMP_SERVICE_API_URI))


def unpack_form_errors(errors):
    return [element for sublist in errors.values() for element in sublist]


@transaction.atomic
def do_payment(request, sender, recipient, amount):
    current_person = get_current_person(request)

    sender_noun = 'Sender'
    recipient_noun = 'Recipient'
    if sender == current_person:
        sender_noun = 'Your'
    elif recipient == current_person:
        recipient_noun = 'Your'

    inactivity_message = ' account is not currently active.'
    if not sender.active:
        messages.error(request, sender_noun + inactivity_message)
        return False
    if not recipient.active:
        messages.error(request, recipient_noun + inactivity_message)
        return False

    value = Decimal(amount.amount)
    transaction_currency = amount.currency

    subtraction_value, addition_value = value, value
    if transaction_currency != sender.balance_currency:
        subtraction_value = call_currency_converter(str(transaction_currency), sender.balance_currency, value)[1]
    if transaction_currency != recipient.balance_currency:
        addition_value = call_currency_converter(str(transaction_currency), recipient.balance_currency, value)[1]

    if sender.balance.amount >= subtraction_value:
        sender.balance -= Money(subtraction_value, sender.balance_currency)
        sender.save()

        recipient.balance += Money(addition_value, recipient.balance_currency)
        recipient.save()

        messages.success(request, f'Payment Successful: you have sent {amount} to {recipient.user.username}')
        return True  # imply success
    else:
        messages.error(request, 'Insufficient funds for transaction')
    return False
