from django.db import models
import re

class Client(models.Model):
    name = models.CharField(max_length=30)
    read_access = models.BooleanField(default=True)
    write_access = models.BooleanField(default=False)
    delete_access = models.BooleanField(default=False)
    vote_access = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Festival(models.Model):
    name = models.CharField(max_length=400)
    description = models.CharField(max_length=800, blank=True)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=90, blank=True)
    address = models.CharField(max_length=200, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    prices = models.CharField(max_length=400, blank=True)
    uploader = models.CharField(max_length=200, blank=True)
    official = models.BooleanField(default=False)
    downloads = models.BigIntegerField(default=0)
    voters = models.BigIntegerField(default=0)
    rank = models.SmallIntegerField(default=0)
    first_uploaded = models.DateTimeField()
    last_modified = models.DateTimeField()

    def __str__(self):
        return self.name

    def price_is_in_range(self, min_price=None, max_price=None):
        if min_price==None and max_price==None:
            raise ValueError("Either min_price or max_price should be defined")
        if min_price != None:
            min_price_formatted = self._separate_value_from_currency(min_price)
            if min_price_formatted == []:
                raise InvalidInputOrDifferentCurrencyError('Invalid min_price.')
            if min_price_formatted[0] < 0:
                raise InvalidInputOrDifferentCurrencyError('Negative min_price.')
        if max_price != None:
            max_price_formatted = self._separate_value_from_currency(max_price)
            if max_price_formatted == []:
                raise InvalidInputOrDifferentCurrencyError('Invalid max_price')
            if max_price_formatted[0] < 0:
                raise InvalidInputOrDifferentCurrencyError('Negative max_price')
        if min_price != None and max_price != None:
            if min_price_formatted[1] != max_price_formatted[1]:
                raise InvalidInputOrDifferentCurrencyError('min_price and max_price currency mismatch')
            if min_price_formatted[0] > max_price_formatted[0]:
                raise InvalidInputOrDifferentCurrencyError('min_price higher than max_price')
        for price in self.prices.split(" "):
            price_formatted = self._separate_value_from_currency(price)
            if (min_price!=None):
                if min_price_formatted[1] != price_formatted[1]:
                    raise InvalidInputOrDifferentCurrencyError('Input currency and currency in record mismatch')
            if (max_price!=None):
                if max_price_formatted[1] != price_formatted[1]:
                    raise InvalidInputOrDifferentCurrencyError('Input currency and currency in record mismatch')
            if min_price!= None and max_price==None:
                if min_price_formatted[0] < price_formatted[0]:
                    return True
            elif min_price==None and max_price!=None:
                if price_formatted[0] < max_price_formatted[0]:
                    return True
            else:
                if min_price_formatted[0] < price_formatted[0] & price_formatted[0] < max_price_formatted[0]:
                    return True
        return False

    @staticmethod
    def _separate_value_from_currency(price):
        value_str = re.findall("[+-]?\d+", price)
        if len(value_str) != 1:
            return []
        value = int(value_str[0])
        currency = [s.strip() for s in price.split(value_str[0]) if s != '']
        if len(currency) != 1:
            return []
        currency = currency[0]
        return [value, currency]

class InvalidInputOrDifferentCurrencyError(Exception):
    pass

class Concert(models.Model):
    festival = models.ForeignKey(Festival)
    artist = models.CharField(max_length=500)
    scene = models.SmallIntegerField(default=1)
    day = models.SmallIntegerField(default=1)
    start = models.DateTimeField()
    end = models.DateTimeField()
    first_uploaded = models.DateTimeField()
    last_modified = models.DateTimeField()

    def __str__(self):
        return self.artist