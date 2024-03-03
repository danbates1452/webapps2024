from django.db import transaction
from django.shortcuts import render, redirect
from .models import Person, Transactions, Requests


def restricted_area(check_user):
    if check_user.is_staff and check_user.is_authenticated():
        return True
    else:
        redirect('home')
        return False

# todo: need a way to map user to customer easily
def home(request):
    context = {
        'recent_transactions': Transactions.objects.filter(
            from_person=request.user,
            to_person=request.user
        ).order_by('-id')[:10:-1],
        'requests': Requests.objects.filter(
            from_person=request.user,
            cancelled=False,
            completed=False
        ),

    }
    return render(request, 'payapp/home.html', context=context)


def activity(request):
    context = {
        'activity_list': Transactions.objects.filter(
            from_person=request.user,
            to_person=request.user
        )
    }
    return render(request, 'payapp/activity.html', context=context)


def send(request):

    # clean the form, and check if they have sufficient money

    with transaction.atomic():
        pass
        # perform transaction:
        # subtract 'from' user balance (with converting currency if needed)
        # add to 'to' user balance (with converted currency)
        # save new transaction entry to db

    return None


def request(request):


    return None


def admin_users(request):
    restricted_area(request.user)

    context = {
        'customer_list': Person.objects.all()
    }

    return render(request, 'payapp/admin_users.html', context=context)


def admin_activity(request):
    restricted_area(request.user)

    context = {
        'activity_list': Transactions.objects.all()  # todo: pagination
    }
    return render(request, 'payapp/admin_activity.html', context=context)
