import json

from django.test import TestCase
from django.utils import timezone

from  .models import Festival, Concert, InvalidInputOrDifferentCurrencyError


def create_festival(name):
    return Festival(name = name,
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


def create_concert(festival, artist):
    return Concert.objects.create(festival = festival,
                                  artist = artist,
                                  start = timezone.now() + timezone.timedelta(days = 2, hours = 1),
                                  end = timezone.now() + timezone.timedelta(days = 2, hours = 2),
                                  first_uploaded = timezone.now(),
                                  last_modified = timezone.now()
                                  )

class FestivalMethodTests(TestCase):


    def test_price_is_in_range_correct_input_in_range(self):
        """
        price_is_in_range() is to return True if the currency strings are equal,
        none of the inputs are negative numbers and at least one of the prices
        fits within the requirements
        """
        festival = create_festival('test')

        self.assertTrue(festival.price_is_in_range('5e', '100e'))
        self.assertTrue(festival.price_is_in_range('5 e', '100 e'))

        festival.prices='$3 $50 $200'

        self.assertTrue(festival.price_is_in_range('$3', '$100'))
        self.assertTrue(festival.price_is_in_range('$ 3', '$ 100'))

    def test_price_is_in_range_correct_input_outside_range(self):
        """
        price_is_in_range() is to return False without throwing an exception if the
        currency strings are equal, none of the inputs are negative numbers and no prices
        satisfy the requirements
        """
        festival = create_festival('test')

        self.assertFalse(festival.price_is_in_range('4e', '10e'))
        self.assertFalse(festival.price_is_in_range('4 e', '10 e'))

        festival.prices = '$25 $50 $200'

        self.assertFalse(festival.price_is_in_range('$1', '$10'))
        self.assertFalse(festival.price_is_in_range('$ 1', '$ 10'))

    def test_price_is_in_range_currency_mismatch(self):
        """
        price_is_in_range() should throw InvalidInputOrDifferentCurrencyError
        if the currency strings do not match
        """
        festival = create_festival('test')

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('$3', '$5')

    def test_price_is_in_range_negative_value(self):
        """
        price_is_in_range() is to throw InvalidInputOrDifferentCurrencyError
        if any of the values provided is negative
        """
        festival = create_festival('test')

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
        festival = create_festival('test')

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('10e', '5e')

    def test_only_min_value_is_defined(self):
        """
        price_is_in_range() is to return all results higher than min_price
        """
        festival = create_festival('test')

        self.assertTrue(festival.price_is_in_range('5e'))
        self.assertTrue(festival.price_is_in_range('5 e'))

        festival.prices = '$3 $50 $200'

        self.assertTrue(festival.price_is_in_range('$3'))
        self.assertTrue(festival.price_is_in_range('$ 3'))

        def test_only_max_value_is_defined(self):
            """
            price_is_in_range() is to return all results lower than max_price
            """
            festival = create_festival('test')

            self.assertTrue(festival.price_is_in_range(max_price='100e'))
            self.assertTrue(festival.price_is_in_range(max_price='100 e'))

            festival.prices = '$3 $50 $200'

            self.assertTrue(festival.price_is_in_range(max_price='$100'))
            self.assertTrue(festival.price_is_in_range(max_price='$ 100'))

class ReadMultipleFestivalsTests(TestCase):


    def test_empty_db(self):
        """
        read_multiple_festivals() is to return an empty JSON data document
        if there are no festivals in the database
        """
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_less_records_available_than_requested(self):
        """
        read_multiple_festivals() is to return the amount of available festivals in case
        that number is lesser than the number requested
        """
        create_festival('test')
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 1)

    def test_records_available_equal_or_more_than_requested(self):
        """
        read_multiple_festivals() is to return the requested number of records in case
        the database has that many records
        """
        create_festival('test')
        create_festival('testest')
        create_festival('testestest')
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)
        create_festival('testestestest')
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(len(data), 3)

    def test_filter_does_not_satisfy_any_results(self):
        """
        read_multiple_festivals() is to return empty JSON data document in case no records
        satisfy the filter
        """
        create_festival('test')
        response = self.client.post('/backend/mult/fest/', {
            'num': 3,
            'name': 'test',
            'country': 'test',
            'city': 'asdf'
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 0)

    def test_filter_satisfied_results(self):
        """
        read_multiple_festivals() is to return between 1 and num results, depending on how
        many satisfy the filter
        """
        create_festival('test')
        fest1 = create_festival('testest')
        fest1.city='testest'
        fest1.save()
        fest2 = create_festival('testestest')
        fest2.prices='1000e'
        fest2.save()
        response = self.client.post('/backend/mult/fest/', {
            'num': 3,
            'min_price': '20e',
            'max_price': '60e'
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 2)

class ReadFestivalConcertsTests(TestCase):


    def test_invalid_festival(self):
        """
        read_festival_concerts() is to return an empty JSON data document
        if festival id is invalid
        """
        response = self.client.post('/backend/mult/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_empty_festival(self):
        """
        read_festival_concerts() is to return an empty JSON data document
        if festival is found but empty
        """
        festival = create_festival('test')
        response = self.client.post('/backend/mult/conc/', {'id': festival.pk })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_valid_festival(self):
        """
        read_festival_concerts() is to return all concerts in the festival
        """
        festival = create_festival('test')
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/mult/conc/', {'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)


class ReadFestivalInfoTests(TestCase):
    def test_no_festival_found(self):
        """
        read_festival_info() is to return empty JSON data document if festival
        is not found
        """
        festival = create_festival('test')
        response = self.client.post('/backend/r/fest/', {'id': festival.pk + 1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data)

    def test_festival_found(self):
        """
        read_festival_info() is to return an JSON data document containing the data
        of the festival found
        """
        festival = create_festival('test')
        response = self.client.post('/backend/r/fest/', {'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data)
        self.assertEqual(data['name'], festival.name)


class WriteFestivalInfoTests(TestCase):
    def test_correct_input(self):
        response = self.client.post('/backend/w/fest/',
                                    {'name': 'test',
                                     'description': 'test',
                                     'country': 'test',
                                     'city': 'test',
                                     'address': 'test',
                                     'genre': 'test',
                                     'prices': '0e',
                                     'uploader': 'test',
                                     'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Festival.objects.get(name = 'test'))

    def test_missing_fields(self):
        response = self.client.post('/backend/w/fest/',
                                    {'name': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Festival.objects.get(name = 'test'))


class ReadConcertInfoTests(TestCase):
    def test_no_concert_found(self):
        response = self.client.post('/backend/r/conc/', {'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data)
        festival = create_festival('test')
        response = self.client.post('/backend/r/conc/', {'fest': festival.pk, 'artist': 'test'})
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data)

    def test_concert_found(self):
        festival = create_festival('test')
        create_concert(festival, 'test')
        response = self.client.post('/backend/r/conc/', {'fest': festival.pk, 'artist': 'test'})
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data)


class DeleteFestivalTests(TestCase):
    def test_no_matching_festivals(self):
        create_festival('test')
        create_festival('testest')
        create_festival('testestest')
        response = self.client.post('/backend/d/fest/', {'id': 15})
        data = Festival.objects.all()
        self.assertEqual(len(data), 3)

    def test_festival_matches(self):
        create_festival('test')
        create_festival('testest')
        festival = create_festival('testestest')
        response = self.client.post('/backend/d/fest/', {'id': festival.pk})
        data = Festival.objects.all()
        self.assertEqual(len(data), 2)


class DeleteConcertsTests(TestCase):
    def test_no_concert_found(self):
        festival = create_festival('test')
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/d/conc/', {'fest': festival.pk + 1, 'artist': 'asdf'})
        self.assertEqual(response.status_code, 200)
        data = Concert.objects.all()
        self.assertEqual(len(data), 3)
        response = self.client.post('/backend/d/conc/', {'fest': festival.pk, 'artist': 'asdf'})
        data = Concert.objects.all()
        self.assertEqual(len(data), 3)

    def test_concert_found(self):
        festival = create_festival('test')
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/d/conc/', {'fest': festival.pk, 'artist': 'test'})
        data = Concert.objects.all()
        self.assertEqual(len(data), 2)
