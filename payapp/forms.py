from django import forms
from .models import Transaction, Request


class SendForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ('submission_datetime', 'from_person',)
        labels = {
            'to_person': 'Recipient'
        }


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        exclude = ('by_person', 'completed', 'cancelled')
