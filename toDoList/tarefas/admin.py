from django.contrib import admin
from .models import Tarefa

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('materia', 'descricao', 'prazo', 'criada_em', 'autor')