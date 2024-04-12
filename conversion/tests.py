from django.test import TestCase
from common.util import call_currency_converter


class CallCurrencyConverterTestCase(TestCase):
    def setUp(self):
        currencies = ['GBP', 'USD', 'EUR']

    def test1(self):
        result = call_currency_converter('GBP', 'GBP', 1)
        self.assertEquals()