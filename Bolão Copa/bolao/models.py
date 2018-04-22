from django.db import models
from django.utils import timezone

class Pais(models.Model):
    nome = models.CharField(max_length=50)
    inicial = models.CharField(max_length=3)
    bandeira = models.ImageField(upload_to="./bolao/static/flags")

    def __str__(self):
        return self.inicial

class Jogador(models.Model):
    nome = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=254)
    creditos =  models.DecimalField(max_digits=10, decimal_places=2, default=10)

    def __str__(self):
        return self.nome

    def creditar(self,novosCreditos):
        self.creditos = float(self.creditos) + novosCreditos
        self.save()

    def apostar(self):
        self.creditos -= 5
        self.save()

class Partida(models.Model):
    pais_1 = models.ForeignKey('Pais', related_name="pais_1", on_delete=models.CASCADE, blank = False, null = False)
    pais_2 = models.ForeignKey('Pais', related_name="pais_2", on_delete=models.CASCADE, blank = False, null = False)
    estadio = models.ForeignKey('Estadio', on_delete=models.CASCADE, blank = False, null = False, default=1)
    placar_1 = models.PositiveIntegerField(default=0)
    placar_2 = models.PositiveIntegerField(default=0)
    status = models.IntegerField(default=-1)
    data = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.pais_1.inicial + ' X ' + self.pais_2.inicial + ' - ' + str(self.estadio)

class Aposta(models.Model):
    jogador = models.ForeignKey('Jogador', on_delete=models.CASCADE, blank = False, null = False)
    partida = models.ForeignKey('Partida', on_delete=models.CASCADE, blank = False, null = False)
    placar_1 = models.PositiveIntegerField(default=0)
    placar_2 = models.PositiveIntegerField(default=0)
    status = models.IntegerField(default=-1)

    def __str__(self):
        return str(self.partida) + " : " + str(self.jogador).upper()
    
    def publish(self):
        if( self.placar_1 > self.placar_2):
            self.status = 1
            self.save()
        elif( self.placar_1 < self.placar_2 ):
            self.status = 2
            self.save()
        else:
            self.status = 0
            self.save()

class Estadio(models.Model):
    nome_estadio = models.CharField(max_length=254)
    cidade_estadio = models.CharField(max_length=254)
    estado_estadio = models.CharField(max_length=254)

    def __str__(self):
        return self.nome_estadio + ' - ' + self.cidade_estadio #+ ' : ' + self.estado_estadio
