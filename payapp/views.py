from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
from djmoney.money import Money

from .forms import SendForm, RequestForm, RequestResponseForm
from .models import Person, Transaction, Request
from common.util import call_currency_converter, get_current_person, admin_area, do_payment, call_timestamp_service


@requires_csrf_token
@login_required(login_url='/login/')
def home(request):
    requests = Request.objects.filter(
        (Q(to_person__user_id__exact=request.user.id) | Q(from_person__user_id__exact=request.user.id)) and
        Q(status="PENDING")
    )

    forms = [RequestResponseForm(instance=rq) for rq in requests]

    context = {
        'person': Person.objects.filter(user__exact=request.user.id)[0],
        'recent_transactions': Transaction.objects.filter(
            Q(from_person__user_id__exact=request.user.id) |
            Q(to_person__user_id__exact=request.user.id)
        ).order_by('-id')[:10:-1],
        'requests_and_forms': zip(requests, forms),
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
def send_money(request):
    if request.method == 'POST':
        form = SendForm(request.POST)
        if form.is_valid():
            form.clean()

            from_person = Person.objects.select_for_update().get(user_id=request.user.id)
            to_person = Person.objects.select_for_update().get(id=form.cleaned_data['to_person'].id)
            amount = form.cleaned_data['amount']

            result = do_payment(request=request,
                                sender=from_person,
                                recipient=to_person,
                                amount=amount)
            if result:  # if success
                form.instance.submission_datetime = call_timestamp_service()
                form.instance.from_person = from_person
                form.save()
                return redirect('home')
            else:
                # if failed, return to page with form filled as it was submitted
                return render(request, 'payapp/send.html', {'form': form})

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
            form.instance.status = "PENDING"
            form.save()
            return redirect('home')  # redirect to homepage to avoid replay attacks

    return render(request, 'payapp/request.html', {'form': form})


@login_required(login_url='/login/')
def request_response(request):
    if request.method == 'POST':
        form = RequestResponseForm(request.POST)
        if form.is_valid():
            form.clean()
            if form.cleaned_data['status'] == "PENDING":
                messages.error(request, 'Payment request was already pending')
            elif form.cleaned_data['status'] == "COMPLETED":
                by_person = form.cleaned_data['by_person']
                to_person = form.cleaned_data['to_person']
                amount = form.cleaned_data['amount']

                result = do_payment(request=request,
                                    sender=to_person,
                                    recipient=by_person,
                                    amount=amount)

                if result:  # if success
                    request_instance = Request.objects.get(by_person__exact=by_person,
                                                           to_person__exact=to_person,
                                                           amount__exact=amount,
                                                           status__exact="PENDING")
                    # make sure we update rather than create
                    form = RequestResponseForm(request.POST, instance=request_instance)
                    form.save()

                    # record this transaction
                    Transaction.objects.create(
                        from_person=to_person,
                        to_person=by_person,
                        amount=amount,
                        submission_datetime=call_timestamp_service()
                    )

            elif form.cleaned_data['status'] == "CANCELLED":
                print(form.cleaned_data)
                request_instance = Request.objects.get(by_person__exact=form.cleaned_data['by_person'],
                                                       to_person__exact=form.cleaned_data['to_person'],
                                                       amount__exact=form.cleaned_data['amount'],
                                                       status__exact="PENDING")
                # make sure we update rather than create
                form = RequestResponseForm(request.POST, instance=request_instance)
                form.save()
                messages.success(request, 'Request cancelled successfully.')
            else:
                messages.error(request, 'Invalid operation')
        else:
            print(form.errors)
            print(form.instance.amount)
            print(form.instance)

    return redirect('home')


@requires_csrf_token
@login_required(login_url='/login/')
def admin_users(request):
    admin_area(request.user)

    if request.method == 'POST':
        if request.POST['user_id']:
            user_to_promote = User.objects.get(id=int(request.POST['user_id']))

            if get_current_person(request).user.is_superuser:  # if current user is admin
                user_to_promote.is_superuser = True
                user_to_promote.is_staff = True
                user_to_promote.save()
                messages.success(request, 'Admin ' + user_to_promote.username + ' successfully promoted.')
            else:
                messages.error(request, 'You do not have permission to do this.')
        else:
            messages.error(request, 'Invalid user selected.')

        return redirect('admin-users')  # prevent form resubmission
    else:
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
