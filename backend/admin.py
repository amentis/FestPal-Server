from django.contrib import admin

from .models import Client, Concert, Festival, Profile


class ClientAdmin(admin.ModelAdmin):
    fields = ['name', 'read_access', 'write_access', 'delete_access', 'vote_access']
    list_display = ('name', 'read_access', 'write_access', 'delete_access', 'vote_access')


class ConcertAdmin(admin.ModelAdmin):
    readonly_fields = ('last_modified', 'first_uploaded')
    fieldsets = [
        (None, {'fields': ['festival', 'artist', 'day', 'scene']}),
        ('From/to', {'fields': ['start', 'end']}),
        ('Modification info', {'fields': ['first_uploaded', 'last_modified']}),
    ]
    list_display = ('artist', 'festival', 'start', 'last_modified')


class FestivalAdmin(admin.ModelAdmin):
    readonly_fields = ('last_modified', 'first_uploaded')
    fieldsets = [
        (None, {'fields': ['name', 'description', 'genre', 'prices']}),
        ('Location', {'fields': ['country', 'city', 'address']}),
        ('Upload/download info', {'fields': ['uploader', 'official', 'downloads', 'voters']}),
        ('Modification info', {'fields': ['first_uploaded', 'last_modified']}),
    ]
    list_display = ('name', 'official', 'country', 'city', 'last_modified')


class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'representative', 'country', 'city']
    list_display = ('user', 'representative', 'country', 'city')

admin.site.register(Client, ClientAdmin)
admin.site.register(Festival, FestivalAdmin)
admin.site.register(Concert, ConcertAdmin)
admin.site.register(Profile, ProfileAdmin)
