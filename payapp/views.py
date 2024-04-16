from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
from djmoney.money import Money

from .forms import SendForm, RequestForm
from .models import Person, Transaction, Request
from common.util import call_currency_converter, get_current_person, admin_area


@login_required(login_url='/login/')
def home(request):
    context = {
        'person': Person.objects.filter(user__exact=request.user.id)[0],
        'recent_transactions': Transaction.objects.filter(
            Q(from_person__user_id__exact=request.user.id) |
            Q(to_person__user_id__exact=request.user.id)
        ).order_by('-id')[:10:-1],
        'requests': Request.objects.filter(
            (Q(to_person__user_id__exact=request.user.id) | Q(from_person__user_id__exact=request.user.id)) and
            Q(status=Request.StatusChoices.PENDING)
        ),
    }



    return render(request, 'payapp/home.html', context=context)


@login_required(login_url='/login/')
def activity(request):
    context = {
        'activity_list': Transaction.objects.filter(
            Q(from_person__user_id__exact=request.user.id) |
            Q(to_person__user_id__exact=request.user.id)
        )  # user is either exactly the sender or recipient
    }
    return render(request, 'payapp/activity.html', context=context)


@login_required(login_url='/login/')
@requires_csrf_token
@transaction.atomic
def send_money(request):
    if request.method == 'POST':
        form = SendForm(request.POST)
        if form.is_valid():
            form.clean()

            from_person = Person.objects.select_for_update().get(user_id=request.user.id)
            to_person = Person.objects.select_for_update().get(id=form.cleaned_data['to_person'].id)

            if not from_person.active:
                messages.error(request, 'Your account is not active')
                return render(request, 'payapp/send.html', {'form': form})
            elif not to_person.active:
                messages.error(request, 'Recipient account not active')
                return render(request, 'payapp/send.html', {'form': form})

            amount = Decimal(form.cleaned_data['amount'].amount)

            subtraction_amount = amount
            addition_amount = amount
            transaction_currency = str(form.cleaned_data['amount'].currency)

            if transaction_currency != from_person.balance_currency:
                subtraction_amount = \
                    call_currency_converter(transaction_currency, from_person.balance_currency, subtraction_amount)[1]

            if transaction_currency != to_person.balance_currency:
                addition_amount = \
                    call_currency_converter(transaction_currency, to_person.balance_currency, subtraction_amount)[1]

            if from_person.balance.amount >= subtraction_amount:  # perform transaction:
                # subtract 'from' user balance (with converting currency if needed) and save
                from_person.balance -= Money(subtraction_amount, from_person.balance.currency)
                from_person.save()

                # add to 'to' user balance (with converted currency) and save
                to_person.balance += Money(addition_amount, to_person.balance.currency)
                to_person.save()

                # add from_person to the transaction
                form.instance.from_person = from_person
                # save new transaction entry to db
                form.save()

                messages.success(request, f'Payment Successful: you have sent {amount} to {to_person.user.username}')
                return redirect('home')
            else:
                messages.error(request, "Insufficient funds for transaction")
                return render(request, 'payapp/send.html', {'form': form})
        else:
            return render(request, 'payapp/send.html', {'form': form})
    else:
        form = SendForm(initial={'from_user': get_current_person(request)})
        return render(request, 'payapp/send.html', {'form': form})


@login_required(login_url='/login/')
@requires_csrf_token
def request_money(request):
    by_person = get_current_person(request)
    form = RequestForm(initial={
        'by_person': by_person,
        'amount_currency': by_person.balance.currency
    })
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            form.clean()

            if not by_person.active:
                messages.error(request, 'Your account is not active.')
                return render(request, 'payapp/request.html', {'form': form})
            elif not form.cleaned_data['to_person'].active:
                messages.error(request, 'Requested account is not active.')
                return render(request, 'payapp/request.html', {'form': form})

            form.instance.by_person = by_person
            form.instance.status = Request.StatusChoices.PENDING
            form.save()
            return redirect('home')  # redirect to homepage to avoid replay attacks

    return render(request, 'payapp/request.html', {'form': form})


@login_required(login_url='/login/')
def request_response(request):
    # todo: have this process one of two possible request responses from the homepage
    # refuse (cancel), accept (completed)
    if request.method == 'POST':
        response = True if request.POST.get('Accept', '') == 'Accept' else False  # True = Accepted, False = Refused

        by_person_id = request.POST.get('by_person_id')
        to_person_id = request.POST.get('to_person_id')
        currency = request.POST.get('currency')
        amount_object = Money(Decimal(request.POST.get('amount')), currency=currency)
        status = request.POST.get('status')

        target_request = Request.objects.get(
            by_person_id=by_person_id,
            to_person_id=to_person_id,
            amount=amount_object,
            status__=status
        )[0]
        print(by_person_id)

        if target_request:  # if exists
            with transaction.atomic:
                by_person = Person.objects.get(id=by_person_id)[0]
                to_person = Person.objects.get(id=to_person_id)[0]

                if not by_person.active:
                    messages.error(request, 'Sender account is not active')
                    return redirect('home')
                elif not to_person.active:
                    messages.error(request, 'Recipient account not active')
                    return redirect('home')

                if response:  # accepted
                    amount = Decimal(amount_object.amount)

                    subtraction_amount = amount
                    addition_amount = amount
                    transaction_currency = str(amount_object.currency)

                    if transaction_currency != by_person.balance_currency:
                        subtraction_amount = \
                            call_currency_converter(transaction_currency, by_person.balance_currency, subtraction_amount)[1]

                    if transaction_currency != to_person.balance_currency:
                        addition_amount = \
                            call_currency_converter(transaction_currency, to_person.balance_currency, subtraction_amount)[1]

                    if by_person.balance.amount >= subtraction_amount:  # perform transaction:
                        # subtract 'from' user balance (with converting currency if needed) and save
                        by_person.balance -= Money(subtraction_amount, by_person.balance.currency)
                        by_person.save()

                        # add to 'to' user balance (with converted currency) and save
                        to_person.balance += Money(addition_amount, to_person.balance.currency)
                        to_person.save()

                        target_request.status = Request.StatusChoices.COMPLETED

                        messages.success(request, f'Payment Successful: you have sent {amount} to {by_person.user.username}')
                        return redirect('home')
                    else:
                        messages.error(request, "Insufficient funds for transaction")
                else:
                    target_request.status = Request.StatusChoices.CANCELLED
                    target_request.save()
                    messages.success(request, 'Request Denied Successfully.')

    return redirect('home')


@login_required(login_url='/login/')
def admin_users(request):
    admin_area(request.user)

    context = {
        'people': Person.objects.all()
    }

    return render(request, 'payapp/admin_users.html', context=context)


@login_required(login_url='/login/')
def admin_activity(request):
    admin_area(request.user)

    context = {
        'activity_list': Transaction.objects.all()  # todo: pagination
    }
    return render(request, 'payapp/admin_activity.html', context=context)
