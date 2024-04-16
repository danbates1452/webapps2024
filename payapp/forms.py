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
        exclude = ('by_person', 'status')
        labels = {
            'to_person': 'Recipient'
        }


class RequestResponseForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'
        widgets = {'by_person': forms.HiddenInput(),
                   'to_person': forms.HiddenInput(),
                   #'amount': forms.HiddenInput()
                   }
        # Only non-hidden will be status
