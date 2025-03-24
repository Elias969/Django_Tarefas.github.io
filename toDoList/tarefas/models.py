from django.db import models
from datetime import datetime
from django.utils import timezone
from pytz import timezone as pytz_timezone
from django.contrib.auth.models import User 

class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('em_andamento', 'Em andamento'),
        ('nao_feita', 'Não feita'),
        ('concluida', 'Concluída'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='em_andamento',
    )
    materia = models.CharField(max_length=50)
    descricao = models.CharField(max_length=250)
    
    prazo = models.DateTimeField(
        null=True,
        blank=True
    )
    
    criada_em = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        fuso_brasilia = pytz_timezone('America/Sao_Paulo')  # Definindo o fuso horário de Brasília
        agora_brasilia = timezone.now().astimezone(fuso_brasilia)  # Garantir que a data seja no fuso correto

        if self.prazo:
            # Garantir que a data está no fuso horário correto antes de aplicar o replace
            hora_prazo=self.prazo.hour
            minuto_prazo=self.prazo.minute
            segundo_prazo=self.prazo.second
            microsegundo_prazo=self.prazo.microsecond
            prazo_brasilia = self.prazo.astimezone(fuso_brasilia)

            # Ajustar a hora para 00:00
            prazo_brasilia = prazo_brasilia.replace(hour=hora_prazo, minute=minuto_prazo, second=segundo_prazo, microsecond=microsegundo_prazo)

            print(agora_brasilia, prazo_brasilia)
            if prazo_brasilia < agora_brasilia and self.status != 'concluida':
                print(self.materia)
                self.status = 'nao_feita'

        super().save(*args, **kwargs)

