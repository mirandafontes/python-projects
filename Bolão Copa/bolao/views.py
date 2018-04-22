from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from . import models
from .models import Partida,Jogador,Aposta,Pais
from django.utils import timezone


# Create your views here.

@login_required
def tela_inicial(request):
    partidas = Partida.objects.filter(data__gt=timezone.now()).order_by('data')
    return render(request, 'bolao/indexL.html', {'partidas':partidas})

def redirect(request):

    if request.POST:
        return HttpResponseRedirect('login/')
    else:
        return HttpResponseRedirect('signup/')
    
    return render_to_response('bolao/redirect.html',{},context_instance=RequestContext(request,{}))


def cadastrar(request):

    if request.POST:
        name = request.POST.get('nome')
        senha = request.POST.get('senha')
        senha1 = request.POST.get('senha1')
        mail = request.POST.get('mail')
    
        if senha != senha1:
            error = 'As senhas divergem!'
            
            return render_to_response('bolao/cadastro.html',{'error':error},context_instance=RequestContext(request,{}))

        elif len(senha) < 8:
            error = 'A senha possui menos de 8 digitios!'
            
            return render_to_response('bolao/cadastro.html',{'error':error},context_instance=RequestContext(request,{}))

        elif senha == senha1:
            if name and mail:
                u =  Jogador.objects.filter(nome=name)

                if not u:

                    jogador = Jogador.objects.create(nome = name, email = mail, password = senha )
                    jogador.save()

                    return  HttpResponseRedirect('/')
                    #return render_to_response('bolao/indexL.html',{},context_instance=RequestContext(request,{}))
                else:

                    error = 'Usuario já cadastrado!'
                    
                    return render_to_response('bolao/cadastro.html',{'error':error},context_instance=RequestContext(request,{}))

    return render_to_response('bolao/cadastro.html',{},context_instance=RequestContext(request,{}))

            

def login(request):

    if request.POST:
        name = request.POST.get('nome')
        senha = request.POST.get('senha')

        u = Jogador.objects.filter(nome=name, password = senha)
        
        if u:
            partidas = Partida.objects.all().order_by('data')
            
            apostador = Jogador.objects.get(nome=name)
            
            idApostador = Jogador.objects.filter(nome=name).values('id')
            
            jogadores = Jogador.objects.all().order_by('-creditos')
            
            apostas = Aposta.objects.filter(jogador_id=idApostador)

            erro = ""

            attPartidas(request)
            
            return render_to_response('bolao/indexTI.html',{'partidas':partidas, 'erro':erro, 'jogadores':jogadores, 'jogador':apostador,'apostas':apostas },context_instance=RequestContext(request,{}))             

        else:
            return render_to_response('bolao/indexL.html',{},context_instance=RequestContext(request,{}))

    elif request.GET:

        #Pegando campos do Request
        apostado = request.GET.get('apostado')
        placar1 = request.GET.get('placar1')
        placar2 = request.GET.get('placar2')
        jogador = request.GET.get('jogador')

        #Resgatando o Objecto do banco e o ID do Jogador
        jogador_BD = Jogador.objects.get(nome=jogador)
        jogador_ID = Jogador.objects.filter(nome=jogador).values('id')

        #Pegando os Paises pelo Split
        pais_1 = apostado.split(' ')[0]
        pais_2 = apostado.split(' ')[2]

        #Pegando os ID's dos Paises
        pais_1_ID = Pais.objects.filter(inicial=pais_1).values('id')
        pais_2_ID = Pais.objects.filter(inicial=pais_2).values('id')

        #Pegando o ID da partida
        partida_ID = Partida.objects.filter( pais_1 = pais_1_ID , pais_2 = pais_2_ID ).values('id')

        #Verificando se o jogador ja apostou naquela partida
        ja_apostado = Aposta.objects.filter( jogador_id = jogador_BD, partida = partida_ID )

        #Se sim ( ja apostou ), envia-o de volta para a tela
        if ja_apostado:

            partidas = Partida.objects.all().order_by('data')
            
            apostador = Jogador.objects.get(nome=jogador)
            
            idApostador = Jogador.objects.filter(nome=jogador).values('id')
            
            jogadores = Jogador.objects.all().order_by('-creditos')
            
            apostas = Aposta.objects.filter(jogador_id=idApostador)

            erro = 'Você já apostou nesta partida'

            attPartidas(request)
            
            return render_to_response('bolao/indexTI.html',{'partidas':partidas, 'erro':erro, 'jogadores':jogadores, 'jogador':apostador,'apostas':apostas },context_instance=RequestContext(request,{}))             

        #Senao, cria a aposta
        else:

            #list(d.values())

            Aposta.objects.create( jogador_id = list(jogador_ID.first().values())[0], partida_id = list(partida_ID.first().values())[0] , placar_1 = placar1, placar_2 = placar2 )

            attAposta = Aposta.objects.get( jogador_id = jogador_ID, partida_id = partida_ID )

            attAposta.placar_1 = int(placar1)
            attAposta.placar_2 = int(placar2)

            attAposta.publish()

            jogador_BD.apostar()

            #Exibe a tela novamente

            partidas = Partida.objects.all().order_by('data')
            
            apostador = Jogador.objects.get(nome=jogador)
            
            idApostador = Jogador.objects.filter(nome=jogador).values('id')
            
            jogadores = Jogador.objects.all().order_by('-creditos')
            
            apostas = Aposta.objects.filter(jogador_id=idApostador)

            erro = 'Apostado'

            attPartidas(request)
            
            return render_to_response('bolao/indexTI.html',{'partidas':partidas, 'erro':erro, 'jogadores':jogadores, 'jogador':apostador,'apostas':apostas },context_instance=RequestContext(request,{}))             

        
    return render_to_response('bolao/indexL.html',{},context_instance=RequestContext(request,{}))
   
def attPartidas(request):

    partidasTerminadas = Partida.objects.filter(status__gt=-1)

    idJogadoresP = []

    idJogadoresS = []

    valorTotalAposta = 0

    #apostas = Apostas.objects.all()

    for atualP in partidasTerminadas :

        apostas = Aposta.objects.filter(partida_id = atualP.id)
        
        for atualA in apostas :

            valorTotalAposta += 5

            if( atualA.placar_1 == atualP.placar_1 ) and ( atualA.placar_2 == atualP.placar_2 ) :
                
                idJogadoresP.append(atualA.jogador_id)

            elif atualA.status == atualP.status :
                
                idJogadoresS.append(atualA.jogador_id)

        if len(idJogadoresP) == 1 :

            apostador = Jogador.objects.get(id = idJogadoresP[0])
            apostador.creditar(valorTotalAposta)

            idJogadoresP = []
            idJogadoresS = []
            valorTotalAposta = 0

        elif len(idJogadoresP) > 1 :

            valorDividido = valorTotalAposta / len(idJogadoresP)

            for i in idJogadoresP :

                atual = Jogador.objects.get(id = i)

                atual.creditar(valorDividido)

            idJogadoresP = []
            idJogadoresS = []
            valorTotalAposta = 0


        elif len(idJogadoresS) == 1 :

            apostador = Jogador.objects.get(id = idJogadoresS[0])
            apostador.creditar(valorTotalAposta)

            idJogadoresP = []
            idJogadoresS = []
            valorTotalAposta = 0

        elif len(idJogadoresS) > 1 :

            valorDividido = valorTotalAposta / len(idJogadoresS)

            for i in idJogadoresS :

                atual = Jogador.objects.get(id = i)

                atual.creditar(valorDividido)

            idJogadoresP = []
            idJogadoresS = []
            valorTotalAposta = 0

        else:

            for atualA in apostas :

                apostador = Jogador.objects.get(id = atualA.jogador_id)

                apostador.creditar(5)

            idJogadoresP = []
            idJogadoresS = []
            valorTotalAposta = 0

        partidaAtual = Partida.objects.get(id = atualP.id)

        partidaAtual.status = -2
        partidaAtual.save()
        
            
def sair(request):
    logout(request)
    return render_to_response('bolao/sair.html',{},context_instance=RequestContext(request,{}))

