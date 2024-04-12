import requests
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from payapp.models import Person


def get_current_person(request):
    return Person.objects.filter(user__exact=request.user.id)


def admin_area(check_user):
    if check_user.is_staff:
        return True
    else:
        return redirect('home')


CURRENCY_CONVERTER_API_URI = 'https://' + Site.objects.get_current().domain + '/conversion'


def call_currency_converter(currency_from, currency_to, amount_from):
    request_uri = '/'.join([CURRENCY_CONVERTER_API_URI, currency_from, currency_to, str(amount_from)])
    response = requests.get(request_uri)  # todo: see if this needs a different retry strategy
    json_response = response.json()

    rate = json_response['data'][0]
    amount_to = json_response['data'][1]
    return rate, amount_to


def unpack_form_errors(errors):
    return [element for sublist in errors.values() for element in sublist]