from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from djmoney.money import Money

from common.util import call_currency_converter
from payapp.models import Person


class RegisterForm(UserCreationForm):
    currency = forms.ChoiceField(choices=[('GBP', 'GBP'), ('USD', 'USD'), ('EUR', 'EUR')], initial='GBP')

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "currency"]

    def save(self, commit=True):
        saved_object = super(RegisterForm, self).save(commit=commit)
        # on save, create a person with the selected currency
        cleaned_currency = self.cleaned_data['currency']
        rate = call_currency_converter('GBP', cleaned_currency, 1000)[0]
        # converted_starting_balance = call_currency_converter('GBP', cleaned_currency, 1000)[1]
        converted_starting_balance = Money(1000 * rate, currency=cleaned_currency)
        Person.objects.create(user=saved_object, balance=converted_starting_balance)
        return saved_object
