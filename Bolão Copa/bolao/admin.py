from django.contrib import admin
from .models import Pais,Jogador,Partida,Aposta,Estadio

# Register your models here.

admin.site.register(Pais)
admin.site.register(Jogador)
admin.site.register(Partida)
admin.site.register(Aposta)
admin.site.register(Estadio)
