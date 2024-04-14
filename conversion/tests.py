from django.test import TestCase
from common.util import call_currency_converter


class CallCurrencyConverterTestCase(TestCase):
    def setUp(self):
        self.currency_map = {
            'GBP': {
                'USD': 1.3,
                'EUR': 1.1,
            },
            'USD': {
                'GBP': 0.7,
                'EUR': 0.8,
            },
            'EUR': {
                'GBP': 0.9,
                'USD': 1.2,
            },
        }

    def testExpectedBehaviour(self):
        amounts_to_convert = [1, 5, 100, 10000, -1, -100000000000000, 0.5, -0.5]
        for amount in amounts_to_convert:
            for currency1, conversion_matrix in self.currency_map.items():
                for currency2, expected_rate in conversion_matrix.items():
                    expected_converted_value = abs(expected_rate * amount)
                    actual_rate, actual_converted_value = call_currency_converter(currency1, currency2, amount)
                    # For debugging
                    # print("---", currency1, currency2)
                    # print('---', expected_rate, actual_rate)
                    # print(amount, expected_converted_value, actual_converted_value)
                    # print('\n')
                    self.assertEqual(expected_rate, actual_rate)
                    self.assertEqual(expected_converted_value, actual_converted_value)
                    self.assertNotEqual(amount, actual_converted_value)
