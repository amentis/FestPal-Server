from django.test import TestCase
from django.utils import timezone
from  .models import Festival, InvalidInputOrDifferentCurrencyError
from django.core.urlresolvers import reverse
import json


class FestivalMethodTests(TestCase):


    @staticmethod
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

    def test_price_is_in_range_correct_input_in_range(self):
        """
        price_is_in_range() should return True if the currency strings are equal,
        none of the inputs are negative numbers and at least one of the prices
        fits within the requirements
        """
        festival = self.create_festival()

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
        festival = self.create_festival()

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
        festival = self.create_festival()

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('$3', '$5')

    def test_price_is_in_range_negative_value(self):
        """
        price_is_in_range() should throw InvalidInputOrDifferentCurrencyError
        if any of the values provided is negative
        """
        festival = self.create_festival()

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('3e', '-5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '-5e')


class ReadMultipleFestivalsTests(TestCase):


    @staticmethod
    def create_festival():
        return Festival.objects.create(name = 'test',
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

    def test_empty_db(self):
        """
        read_multiple_festivals() is to return an empty JSON data document
        if there are no festivals in the database
        """
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(not data)

    def test_less_records_available_than_requested(self):
        """
        read_multiple_festivals() is to return the amount of available festivals in case
        that number is lesser than the number requested
        """
        self.create_festival()
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_records_available_equal_or_more_than_requested(self):
        """
        read_multiple_festivals() is to return the requested number of records in case
        the database has that many records
        """
        self.create_festival()
        self.create_festival()
        self.create_festival()
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 3)
        self.create_festival()
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(len(data), 3)

    def test_filter_does_not_satisfy_any_results(self):
        """
        read_multiple_festivals() is to return empty JSON data document in case no records
        satisfy the filter
        """
        self.create_festival()
        response = self.client.post('/backend/mult/fest/', {
            'num': 3,
            'name': 'test',
            'country': 'test',
            'city': 'asdf'
        })
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_filter_satisfied_results(self):
        """
        read_multiple_festivals() is to return between 1 and num results, depending on how
        many satisfy the filter
        """
        self.create_festival()
        fest1 = self.create_festival()
        fest1.city='testest'
        fest2 = self.create_festival()
        fest2.prices='1000e'
        response = self.client.post('/backend/mult/fest/', {
            'num': 3,
            'min_price': '20e',
            'max_price': '60e'
        })
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

class ReadFestivalConcertsTests(TestCase):


    @staticmethod
    def create_festival():
        return Festival.objects.create(name = 'test',
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

    @staticmethod
    def create_concert(festival):
        return Concert.objects.create(festival = festival,
                                      artist = 'test',
                                      start = timezone.now() + timedelta(days=2, hours=1),
                                      end = timezone.now() + timedelta(days=2, hours=2),
                                      first_uploaded = timezone.now(),
                                      last_modified = timezone.now()
        )

    def test_invalid_festival(self):
        """
        read_festival_concerts() is to return an empty JSON data document
        if festival id is invalid
        """
        response = self.client.post('/backend/mult/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(not data)

    def test_empty_festival(self):
        """
        read_festival_concerts() is to return an empty JSON data document
        if festival is found but empty
        """
        self.create_festival()
        response = self.client.post('/backend/mult/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(not data)

    def test_valid_festival(self):
        """
        read_festival_concerts() is to return all concerts in the festival
        """
        self.create_festival()
        self.create_concert(0)
        self.create_concert(0)
        self.create_concert(0)
        response = self.client.post('/backend/mult/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 3)