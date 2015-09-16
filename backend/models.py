import re

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User)
    representative = models.BooleanField(default=False)
    country = models.CharField(max_length = 50, blank = True)
    city = models.CharField(max_length = 90, blank = True)


class Client(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    read_access = models.BooleanField(default=True)
    write_access = models.BooleanField(default=False)
    delete_access = models.BooleanField(default=False)
    vote_access = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Festival(models.Model):
    name = models.CharField(max_length = 400, unique = True)
    description = models.CharField(max_length=800, blank=True)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=90, blank=True)
    address = models.CharField(max_length=200, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    prices = models.CharField(max_length=400, blank=True)
    uploader = models.OneToOneField(User)
    official = models.BooleanField(default=False)
    downloads = models.ManyToManyField(User)
    voters = models.ManyToManyField(User)
    rank = models.SmallIntegerField(default=0)
    first_uploaded = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def voters_number(self):
        return self.voters.all().count()

    def downloads_number(self):
        return self.downloads.all().count()

    def price_is_in_range(self, min_price=None, max_price=None):
        if min_price is None and max_price is None:
            raise ValueError("Either min_price or max_price should be defined")
        min_price_formatted = []
        if min_price is not None:
            min_price_formatted = self._separate_value_from_currency(min_price)
            if min_price_formatted is []:
                raise InvalidInputOrDifferentCurrencyError('Invalid min_price.')
            if min_price_formatted[0] < 0:
                raise InvalidInputOrDifferentCurrencyError('Negative min_price.')
        max_price_formatted = []
        if max_price is not None:
            max_price_formatted = self._separate_value_from_currency(max_price)
            if max_price_formatted is []:
                raise InvalidInputOrDifferentCurrencyError('Invalid max_price')
            if max_price_formatted[0] < 0:
                raise InvalidInputOrDifferentCurrencyError('Negative max_price')
        if min_price_formatted is not None and max_price_formatted is not None:
            if min_price_formatted[1] != max_price_formatted[1]:
                raise InvalidInputOrDifferentCurrencyError('min_price and max_price currency mismatch')
            if min_price_formatted[0] > max_price_formatted[0]:
                raise InvalidInputOrDifferentCurrencyError('min_price higher than max_price')
        for price in self.prices.split(" "):
            price_formatted = self._separate_value_from_currency(price)
            if min_price is not None:
                if min_price_formatted[1] != price_formatted[1]:
                    raise InvalidInputOrDifferentCurrencyError('Input currency and currency in record mismatch')
            if max_price is not None:
                if max_price_formatted[1] != price_formatted[1]:
                    raise InvalidInputOrDifferentCurrencyError('Input currency and currency in record mismatch')
            if min_price is not None and max_price is None:
                if min_price_formatted[0] < price_formatted[0]:
                    return True
            elif min_price is None and max_price is not None:
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
    artist = models.CharField(max_length=500, unique = True)
    scene = models.SmallIntegerField(default=1)
    day = models.SmallIntegerField(default=1)
    start = models.DateTimeField()
    end = models.DateTimeField()
    first_uploaded = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.artist


def client_has_permission(name, permission):
    """
    Query clients in database for a client name, create new one if necessary,
    and return whether the permission requested is granted
    :param name: name of the client
    :param permission: permission type requested (read, write, delete or vote)
    :return: True if client has permission, False otherwise
    """
    if permission != 'read' and permission != 'write'\
            and permission != 'delete' and permission != 'vote':
        raise InvalidPermissionStringError('Permission %s not recognised! Acceptable values:'
                                           'read, write, error, vote', name)
    if Client.objects.filter(name=name).count() == 0:
        Client.objects.create(name=name)
    client = Client.objects.get(name=name)
    if permission == 'read':
        return client.read_access
    elif permission == 'write':
        return client.write_access
    elif permission == 'delete':
        return client.delete_access
    elif permission == 'vote':
        return client.vote_access


class InvalidPermissionStringError(Exception):
    pass
