from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from notifications.signals import notify
from django.core.mail import send_mail
from .models import *
from .forms import LoginForm, SignUpForm

from django.contrib.messages import constants
from django.contrib import messages

from django.conf import settings
import uuid

# Create your views here.
def home(request):
    produtos = Produto.objects.prefetch_related("imagens").all()
    categorias = Categoria.objects.filter(categoria_pai__isnull=True)  # Apenas categorias principais
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
    }
    return render(request, "linkagro/home.html", context)

def send_welcome_notification(user):
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        notify.send(sender=superuser, recipient=user, verb=f'Bem-vindo {user.username} à LinkAgro.',
                    description='Obrigado por ter se cadastrado e fazer login com sucesso.')
    else:
        print("Nenhum superusuário encontrado para enviar a notificação.")

@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("home")

def login_usuario(request):
    next_url = request.GET.get('next', 'home')  # 'home' é o padrão se 'next' não for fornecido

    if request.method == "POST":    
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Tentar autenticar com email ou username
        user = None
        
        if '@' in username:  # Se o 'username' parece ser um email
            user = authenticate(request, username=User.objects.get(email=username).username, password=password)
        else:
            user = authenticate(request, username=username, password=password)

        if user:
            profile_obj = PerfilUsuario.objects.filter(user=user).first()

            # Verificar se os perfis estão verificados
            if profile_obj and not profile_obj.verificado:
                messages.error(request, 'Conta não verificada. Por favor, verifique o seu e-mail.')
                return redirect('login')

            # Login com sucesso
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")

            # Garantir que next_url é válido
            next_url = request.POST.get('next', next_url)
            return redirect(next_url) if next_url else redirect("home")

        else:
            # Senha incorreta ou usuário não encontrado
            messages.error(request, "Usuário ou senha incorretos.")
    
    return render(request, "login.html")

def enviar_email_verificacao(user):
    """ Enviar o email de verificação ao usuário """
    token = user.perfilusuario.auth_token  # Acessa o auth_token do perfil do usuário
    link_verificacao = f"{settings.SITE_URL}/verificar/{token}/"  # Link para verificação (ajustar conforme a URL base do seu site)

    subject = "Verifique sua Conta"
    message = f"Olá {user.first_name},\n\nClique no link abaixo para verificar sua conta:\n\n{link_verificacao}\n\nSe não encontrar o email, verifique a caixa de spam."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

def cadastro_usuario(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        cargo = request.POST.get("cargo")

        try:
            # Validar senhas
            if password != password_confirm:
                raise ValueError("As senhas não correspondem.")

            # Verificar se o email já existe
            if User.objects.filter(email=email).exists():
                raise ValueError("O email já está em uso.")

            # Gerar um username único baseado no firstname
            username = firstname
            count = 1
            while User.objects.filter(username=username).exists():
                username = f"{firstname}{count}"
                count += 1

            # Criar o usuário
            user = User.objects.create_user(
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=password
            )

            # Criar o perfil
            perfil = PerfilUsuario.objects.create(
                user=user,
                cargo=cargo,
                distrito="",  # Ajustar conforme necessário
                localizacao="",
                telefone=telefone
            )

            # Enviar o email de verificação
            enviar_email_verificacao(user)

            # Adicionar mensagem de sucesso
            messages.success(request, "Cadastro realizado com sucesso! Verifique seu e-mail para ativar a conta. Confira também a caixa de spam.")

            # Redirecionar para a página de confirmação
            return redirect("verificacao_enviada")  # Roteamento para a página que informa que o email foi enviado

        except ValueError as e:
            # Adicionar mensagem de erro ao request
            messages.error(request, str(e))

        except Exception as e:
            # Captura de outros erros inesperados
            messages.error(request, "Ocorreu um erro inesperado. Tente novamente.")

    return render(request, "cadastro.html")

def verificar_usuario(request, token):
    perfil = get_object_or_404(PerfilUsuario, auth_token=token)

    # Marcar o perfil como verificado
    perfil.verificado = True
    perfil.save()

    # Logar o usuário automaticamente
    login(request, perfil.user)

    messages.success(request, "Sua conta foi verificada com sucesso! Agora você pode acessar a plataforma.")
    return redirect("home")  # Substituir 'home' pela sua página inicial

def verificacao_enviada(request):
    return render(request, "verificacao_enviada.html")

from django.core.exceptions import ObjectDoesNotExist
# View para listar produtos para Producers
@login_required
def listar_produtos_para_producer(request):
    try:
        perfil_usuario = request.user.perfilusuario
    except ObjectDoesNotExist:
        return render(request, 'erro.html', {'mensagem': 'Seu perfil não está configurado. Entre em contato com o suporte.'})

    if perfil_usuario.cargo != 'producer':
        return render(request, 'erro.html', {'mensagem': 'Acesso não autorizado.'})
    
    produtos = Produto.objects.filter(localizacao=perfil_usuario.distrito)
    print(produtos)
    context = {
        'produtos': produtos
    }
    return render(request, 'linkagro/home_usuario.html', context)

# View para listar produtos para Buyers
@login_required
def listar_produtos_para_buyer(request):
    # Filtrar produtos disponíveis para atacadistas
    perfil_usuario = request.user.perfilusuario
    if perfil_usuario.cargo != 'buyer':
        return render(request, 'erro.html', {'mensagem': 'Acesso não autorizado.'})

    produtos = Produto.objects.all()  # Buyers podem ver todos os produtos
    context = {
        'produtos': produtos
    }
    return render(request, 'linkagro/home_usuario.html', context)

# View para listar produtos para Agrodealers
@login_required
def listar_produtos_para_agrodealer(request):
    # Filtrar produtos disponíveis no mesmo distrito ou região do agrodistribuidor
    perfil_usuario = request.user.perfilusuario
    if perfil_usuario.cargo != 'agrodealer':
        return render(request, 'erro.html', {'mensagem': 'Acesso não autorizado.'})

    produtos = Produto.objects.filter(localizacao=perfil_usuario.distrito)
    context = {
        'produtos': produtos
    }
    return render(request, 'linkagro/home_usuario.html', context)