from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator


class PayAppMoneyField(MoneyField):
    # subclass with baked in kwargs to avoid code reuse
    def __init__(self, **kwargs):
        kwargs.update({
            'decimal_places': 2,
            'default': 0,  # todo: remember to push this to 1000 * gbp conversion rate on user creation
            'default_currency': 'GBP',
            'max_digits': 11,
            'validators': [
                MinMoneyValidator(0)
            ]
        })
        super().__init__(**kwargs)


class Person(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)  # disable users rather than deleting them to preserve history
    balance = PayAppMoneyField()


class Transactions(models.Model):
    from_person = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name='transactions_from')
    to_person = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name='transactions_to')
    amount = PayAppMoneyField()
    submission_datetime = models.DateTimeField()


class Requests(models.Model):
    by_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='requests_by')
    to_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='requests_to')
    amount = PayAppMoneyField()
    completed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
