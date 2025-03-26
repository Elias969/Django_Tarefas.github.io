from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('redefinir-senha/', views.redefinir_senha, name='redefinir_senha'),
    path('logout', views.logout_view, name='logout'),
    path('listar_tarefas/', views.listar_tarefas, name='listar_tarefas'),
    path('atualizar_status/', views.atualizar_status, name='atualizar_status'),
    path('criar_tarefa/', views.criar_tarefa, name='criar_tarefa'),
    path('excluir_tarefa/<int:tarefa_id>/', views.excluir_tarefa, name='excluir_tarefa'),
    path('editar_tarefa/<int:tarefa_id>/', views.editar_tarefa, name='editar_tarefa'),
]
