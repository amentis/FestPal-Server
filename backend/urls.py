from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^notlogged/$', views.not_logged_notify, name='not_logged_notify'),
    url(r'^login/$', views.log_in, name='log_in'),
    url(r'^logout/$', views.log_out, name='log_out'),
    url(r'^mult/fest/$', views.read_multiple_festivals, name='read_multiple_festivals'),
    url(r'^mult/conc/$', views.read_festival_concerts, name='read_festival_concerts'),
    url(r'^r/fest/$', views.read_festival_info, name='read_festival_info'),
    url(r'^w/fest/$', views.write_festival_info, name='write_festival_info'),
    url(r'^u/fest/$', views.update_festival_info, name = 'update_festival_info'),
    url(r'^d/fest/$', views.delete_festival, name = 'delete_festival'),
    url(r'^r/conc/$', views.read_concert_info, name='read_concert_info'),
    url(r'^w/conc/$', views.write_concert_info, name='write_concert_info'),
    url(r'^u/conc/$', views.update_concert_info, name = 'update_concert_info'),
    url(r'^d/conc/$', views.delete_concert, name='delete_concert'),
    url(r'^v/$', views.vote, name='vote'),
]
