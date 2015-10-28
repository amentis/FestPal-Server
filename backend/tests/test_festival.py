from django.test import TestCase

from backend.models import InvalidInputOrDifferentCurrencyError
from backend.tests.helpers import create_festival, create_user


class FestivalMethodTests(TestCase):
    def test_empty_prices_string_in_fest(self):
        """
        price_is_in_range() should treat empty prices string in the festival as a 0 value of any
        currency
        """
        festival = create_festival('test', create_user())

        self.assertTrue(festival.price_is_in_range(max_price='$10'))
        self.assertFalse(festival.price_is_in_range(min_price='5e'))
        self.assertFalse(festival.price_is_in_range('5e', '10e'))

    def test_price_is_in_range_correct_input_in_range(self):
        """
        price_is_in_range() is to return True if the currency strings are equal,
        none of the inputs are negative numbers and at least one of the prices
        fits within the requirements
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertTrue(festival.price_is_in_range('5e', '100e'))
        self.assertTrue(festival.price_is_in_range('5 e', '100 e'))

        festival.prices = '$3 $50 $200'
        festival.save()

        self.assertTrue(festival.price_is_in_range('$3', '$100'))
        self.assertTrue(festival.price_is_in_range('$ 3', '$ 100'))

    def test_price_is_in_range_correct_input_outside_range(self):
        """
        price_is_in_range() is to return False without throwing an exception if the
        currency strings are equal, none of the inputs are negative numbers and no prices
        satisfy the requirements
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertFalse(festival.price_is_in_range('4e', '10e'))
        self.assertFalse(festival.price_is_in_range('4 e', '10 e'))

        festival.prices = '$25 $50 $200'
        festival.save()

        self.assertFalse(festival.price_is_in_range('$1', '$10'))
        self.assertFalse(festival.price_is_in_range('$ 1', '$ 10'))

    def test_price_is_in_range_currency_mismatch(self):
        """
        price_is_in_range() should throw InvalidInputOrDifferentCurrencyError
        if the currency strings do not match
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('$3', '$5')

    def test_price_is_in_range_negative_value(self):
        """
        price_is_in_range() is to throw InvalidInputOrDifferentCurrencyError
        if any of the values provided is negative
        """
        festival = create_festival('test', create_user())

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('3e', '-5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '-5e')

    def test_min_value_is_higher_than_max_value(self):
        """
        price_is_in_range() is to throw InvalidInputOrDifferentCurrencyError
        if max_value is higher than min_value
        """
        festival = create_festival('test', create_user())

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('10e', '5e')

    def test_only_min_value_is_defined(self):
        """
        price_is_in_range() is to return all results higher than min_price
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertTrue(festival.price_is_in_range('5e'))
        self.assertTrue(festival.price_is_in_range('5 e'))

        festival.prices = '$3 $50 $200'
        festival.save()

        self.assertTrue(festival.price_is_in_range('$3'))
        self.assertTrue(festival.price_is_in_range('$ 3'))

    def test_only_max_value_is_defined(self):
        """
        price_is_in_range() is to return all results lower than max_price
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertTrue(festival.price_is_in_range(max_price='100e'))
        self.assertTrue(festival.price_is_in_range(max_price='100 e'))

        festival.prices = '$3 $50 $200'
        festival.save()

        self.assertTrue(festival.price_is_in_range(max_price='$100'))
        self.assertTrue(festival.price_is_in_range(max_price='$ 100'))
