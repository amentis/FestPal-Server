from django.db import models

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

    def price_is_in_range(self, minPrice, maxPrice):
        return False


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