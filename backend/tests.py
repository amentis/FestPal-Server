from django.test import TestCase
from django.utils import timezone
from  .models import Festival, InvalidInputOrDifferentCurrencyError

def create_festival():
    return Festival(name = 'test',
                    description = 'test',
                    country = 'test',
                    city = 'test',
                    address = 'test',
                    genre = 'test',
                    prices = '3e 50e 200e',
                    uploader = 'test',
                    official = False,
                    first_uploaded = timezone.now(),
                    last_modified = timezone.now())


class FestivalMethodTests(TestCase):
    def test_price_is_in_range_correct_input_in_range(self):
        """
        price_is_in_range() should return True if the currency strings are equal,
        none of the inputs are negative numbers and at least one of the prices
        fits within the requirements
        """
        festival = create_festival()

        self.assertTrue(festival.price_is_in_range('5e', '100e'))
        self.assertTrue(festival.price_is_in_range('5 e', '100 e'))

        festival.prices='$3 $50 $200'

        self.assertTrue(festival.price_is_in_range('$3', '$100'))
        self.assertTrue(festival.price_is_in_range('$ 3', '$ 100'))

    def test_price_is_in_range_correct_input_outside_range(self):
        """
        price_is_in_range() should return False without throwing an exception if the
        currency strings are equal, none of the inputs are negative numbers and no prices
        satisfy the requirements
        """
        festival = create_festival()

        self.assertFalse(festival.price_is_in_range('1e', '10e'))
        self.assertFalse(festival.price_is_in_range('1 e', '10 e'))

        festival.prices = '$25 $50 $200'

        self.assertFalse(festival.price_is_in_range('$1', '$10'))
        self.assertFalse(festival.price_is_in_range('$ 1', '$ 10'))

    def test_price_is_in_range_currency_mismatch(self):
        """
        price_is_in_range() should throw InvalidInputOrDifferentCurrencyError
        if the currency strings do not match
        """
        festival = create_festival()

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('$3', '$5')

    def test_price_is_in_range_negative_value(self):
        """
        price_is_in_range() should throw InvalidInputOrDifferentCurrencyError
        if any of the values provided is negative
        """
        festival = create_festival()

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('3e', '-5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '-5e')


class ReadMultipleFestivalsTests(TestCase):
    pass