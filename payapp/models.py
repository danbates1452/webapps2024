from datetime import datetime

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

    def __str__(self):
        return self.user.__str__() + ' (inactive)' if not self.active else self.user.__str__()

    class Meta:
        ordering = ("user", "active")


class Transaction(models.Model):
    from_person = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name='transactions_from')
    to_person = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name='transactions_to')
    amount = PayAppMoneyField()
    submission_datetime = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return ' '.join([self.from_person.user.__str__(),
                         self.to_person.user.__str__(),
                         self.amount.__str__(),
                         self.submission_datetime.__str__()
                         ])

    class Meta:
        ordering = ("submission_datetime", "from_person", "amount")


class Request(models.Model):
    by_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='requests_by')
    to_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='requests_to')
    amount = PayAppMoneyField()

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        COMPLETED = "COMPLETED"
        CANCELLED = "CANCELLED"

    status = models.CharField(choices=StatusChoices, default=StatusChoices.PENDING, max_length=9)

    def __str__(self):
        return ' '.join([self.by_person.user.__str__(),
                         self.to_person.user.__str__(),
                         self.amount.__str__(),
                         self.status
                         ])

    class Meta:
        ordering = ("by_person", "status", "amount")
