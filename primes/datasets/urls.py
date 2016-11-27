from django.conf.urls import url
from . import views

app_name = 'datasets'

urlpatterns = [
    # navigation
    url(r'^$', views.index, name='index'),

    # submit datasets; see submission list
    url(r'^submit$', views.submit, name='submit'),

    # process new datasets; see results of processing
    url(r'^process$', views.process, name='process'),

    # see results of processing
    url(r'^report$', views.report, name='report'),
]
