from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin', admin.site.urls),
    url(r'^cadastrar', views.cadastrar, name='cadastrar'),
    url(r'^$', views.login, name='login'),
    url(r'^sair', views.sair, name='sair'),
]
