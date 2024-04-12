import requests
import json
import time
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

from .forms import SendForm, RequestForm
from .models import Person, Transaction, Request


def admin_area(check_user):
    if check_user.is_staff:
        return True
    else:
        return redirect('home')


# todo: need a way to map user to customer easily
@login_required(login_url='/login/')
def home(request):
    context = {
        'person': Person.objects.filter(user__exact=request.user.id),
        'recent_transactions': Transaction.objects.filter(
            from_person__user_id__exact=request.user.id,
            to_person__user_id__exact=request.user.id,
        ).order_by('-id')[:10:-1],
        'requests': Request.objects.filter(
            to_person__user_id__exact=request.user.id,
            cancelled=False,
            completed=False,
        ),
    }
    return render(request, 'payapp/home.html', context=context)


@login_required(login_url='/login/')
def activity(request):
    context = {
        'activity_list': Transaction.objects.filter(
            from_person__user_id__exact=request.user.id,
            to_person__user_id__exact=request.user.id,
        )
    }
    return render(request, 'payapp/activity.html', context=context)


CURRENCY_CONVERTER_API_URI = Site.objects.get_current().domain + '/conversion/'


def call_currency_converter(currency_from, currency_to, amount_from):
    request_uri = '/'.join([CURRENCY_CONVERTER_API_URI, currency_from, currency_to, amount_from])
    response = requests.get(request_uri)  # todo: see if this needs a different retry strategy
    json_response = response.json()

    rate = json_response['data'][0]
    amount_to = json_response['data'][1]
    return rate, amount_to


@login_required(login_url='/login/')
@requires_csrf_token
@transaction.atomic
def send_money(request):
    if request.method == 'POST':
        form = SendForm(request.POST)
        form.clean()
        if form.is_valid():
            from_person = Person.objects.select_for_update().get(name__username=form.cleaned_data['from_user'])
            to_person = Person.objects.select_for_update().get(name__username=form.cleaned_data['to_user'])

            if not from_person.active:
                messages.error(request, 'Your account is not active')
                return render(request, 'payapp/send.html', {'form': form})
            elif not to_person.active:
                messages.error(request, 'Recipient account not active')
                return render(request, 'payapp/send.html', {'form': form})

            amount = form.cleaned_data['amount']

            subtraction_amount = amount
            addition_amount = amount
            transaction_currency = form.cleaned_data['amount_currency']

            if transaction_currency != from_person.balance_currency:
                subtraction_amount = \
                    call_currency_converter(transaction_currency, from_person.balance_currency, subtraction_amount)[1]

            if transaction_currency != to_person.balance_currency:
                addition_amount = \
                    call_currency_converter(transaction_currency, to_person.balance_currency, subtraction_amount)[1]

            if from_person.balance >= subtraction_amount:  # perform transaction:
                # subtract 'from' user balance (with converting currency if needed) and save
                from_person.balance -= subtraction_amount
                from_person.save()

                # add to 'to' user balance (with converted currency) and save
                to_person.balance += addition_amount
                to_person.save()

                # save new transaction entry to db
                form.save()

                messages.success(request, f'Payment Successful: you have sent {amount} to {to_person.user.username}')
                return render(request, 'payapp/send.html')
            else:
                messages.error(request, "Insufficient funds for transaction")
                return render(request, 'payapp/send.html', {'form': form})
        else:
            return render(request, 'payapp/send.html', {'form': form})
    else:
        form = SendForm(initial={'from_user': Person.objects.get(request.user.id)})
        return render(request, 'payapp/send.html', {'form': form})


@login_required(login_url='/login/')
@requires_csrf_token
def request_money(request):
    form = RequestForm(initial={'by_user': Person.objects.get(request.user.id)})
    return render(request, 'payapp/request.html', {'form': form})


@login_required(login_url='/login/')
def admin_users(request):
    admin_area(request.user)

    context = {
        'people': Person.objects.all()
    }

    return render(request, 'payapp/admin_users.html', context=context)


def admin_activity(request):
    admin_area(request.user)

    context = {
        'activity_list': Transaction.objects.all()  # todo: pagination
    }
    return render(request, 'payapp/admin_activity.html', context=context)
