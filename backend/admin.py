from django.contrib import admin

from .models import Client, Concert, Festival

class ClientAdmin(admin.ModelAdmin):
    fields = ['name', 'read_access', 'write_access', 'delete_access', 'vote_access']
    list_display = ('name', 'read_access', 'write_access', 'delete_access', 'vote_access')

class ConcertAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['festival', 'artist', 'day', 'scene']}),
        ('From/to', {'fields': ['start', 'end']}),
        ('Modification info', {'fields': ['first_uploaded', 'last_modified']}),
    ]
    list_display = ('artist', 'festival', 'start', 'last_modified')

class FestivalAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'description', 'genre', 'prices']}),
        ('Location', {'fields': ['country', 'city', 'address']}),
        ('Upload/download info', {'fields': ['uploader', 'official', 'downloads', 'voters', 'rank']}),
        ('Modification info', {'fields': ['first_uploaded', 'last_modified']}),
    ]
    list_display = ('name', 'official', 'country', 'city', 'last_modified')

admin.site.register(Client, ClientAdmin)
admin.site.register(Festival, FestivalAdmin)
admin.site.register(Concert, ConcertAdmin)