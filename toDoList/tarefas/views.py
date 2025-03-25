from django.shortcuts import render, redirect, get_object_or_404
from .models import Tarefa
from .forms import TarefaForm  # Assumindo que você tenha um formulário definido.
from django.utils.timezone import now
from pytz import timezone
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('password')

        if nome and email and senha:
            if User.objects.filter(email=email).exists():
                return render(request, 'cadastro.html', {'error': 'E-mail já cadastrado'})
            
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome
            user.save()

            login(request, user)  # Faz login automaticamente após o cadastro
            return redirect('listar_tarefas')  # Redireciona para a página principal

    return render(request, 'cadastro.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticar o usuário
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('listar_tarefas/')  # Redireciona para a página inicial ou dashboard
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, 'login.html')

def redefinir_senha(request):
    if request.method == "POST":
        username_or_email = request.POST.get('username_or_email')
        senha_antiga = request.POST.get('senha_antiga')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Verifica se as senhas nova e de confirmação são iguais
        if nova_senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem.")
            return redirect('redefinir_senha')

        try:
            # Verifica se o usuário existe pelo nome de usuário ou email
            user = User.objects.get(username=username_or_email) if '@' not in username_or_email else User.objects.get(email=username_or_email)

            # Verifica se a senha antiga está correta
            if user.check_password(senha_antiga):
                # Atualiza a senha do usuário
                user.set_password(nova_senha)
                user.save()
                messages.success(request, "Senha redefinida com sucesso.")
                return redirect('login')  # Redireciona de volta para a página de login
            else:
                messages.error(request, "Senha antiga incorreta.")
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redireciona para a página de login após o logout


def atualizar_status_tarefas_expiradas():
    """
    Atualiza o status das tarefas cujo prazo expirou e estão em andamento.
    """

    agora_brasilia = datetime.now()
    hora_agora=agora_brasilia.hour
    minuto_agora=agora_brasilia.minute
    segundo_agora=agora_brasilia.second
    microsegundo_agora=agora_brasilia.microsecond
    # Imprime os prazos de todas as tarefas
    agora_brasilia = agora_brasilia.replace(hour=hora_agora, minute=minuto_agora, second=segundo_agora, microsecond=microsegundo_agora)
    tarefas_expiradas = Tarefa.objects.filter(prazo__lt=agora_brasilia, status='em_andamento')
    tarefas_expiradas.update(status='nao_feita')

@login_required
def listar_tarefas(request):
    """
    Exibe a lista de todas as tarefas.
    """
    atualizar_status_tarefas_expiradas()  # Atualiza status antes de listar
    tarefas = Tarefa.objects.filter(autor=request.user)
    return render(request, 'listar_tarefas.html', {'tarefas': tarefas})

@login_required
def atualizar_status(request):
    """
    Atualiza o status das tarefas selecionadas para 'concluída'.
    """
    if request.method == 'POST':
        tarefa_ids = request.POST.getlist('tarefa_ids')  # Pega os IDs dos checkboxes marcados
        if tarefa_ids:
            Tarefa.objects.filter(id__in=tarefa_ids).update(status='concluida')
        return redirect('listar_tarefas')  # Recarrega a página após atualizar
    return redirect('listar_tarefas')

@login_required
def criar_tarefa(request):
    """
    Cria uma nova tarefa com base nos dados enviados pelo formulário.
    """
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)  # Não salva imediatamente
            tarefa.autor = request.user  # Define o autor como o usuário logado
            tarefa.save()  # Agora salva a tarefa no banco
            
            return redirect('listar_tarefas')
    else:
        form = TarefaForm()
    return render(request, 'criar_tarefa.html', {'form': form})

@login_required
def excluir_tarefa(request, tarefa_id):
    """
    Exclui a tarefa especificada pelo ID.
    """
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    tarefa.delete()
    return redirect('listar_tarefas')

@login_required
def editar_tarefa(request, tarefa_id):
    """
    Edita os dados de uma tarefa existente.
    """
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa)
        if form.is_valid():
            form.save()
            return redirect('listar_tarefas')
    else:
        form = TarefaForm(instance=tarefa)

    return render(request, 'editar_tarefa.html', {'form': form, 'tarefa': tarefa})