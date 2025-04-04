from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


def monografia_upload_path(instance, filename):
    # Gerando caminho baseado no título e autor para organizar os uploads
    return f'monografias/{instance.autor}/{instance.titulo}/{filename}'


class PalavraChave(models.Model):
    palavra = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.palavra

    class Meta:
        verbose_name = "Palavra-chave"
        verbose_name_plural = "Palavras-chave"
        ordering = ['palavra']


class Professor(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ['nome']


class Monografia(models.Model):
    titulo = models.CharField("Título", max_length=200)
    autor = models.CharField("Autor", max_length=100)
    orientador = models.ForeignKey(
        Professor,
        on_delete=models.PROTECT,
        related_name='monografias_orientadas'
    )
    coorientador = models.ForeignKey(
        Professor,
        on_delete=models.SET_NULL,
        related_name='monografias_coorientadas',
        blank=True,
        null=True
    )
    resumo = models.TextField("Resumo")
    abstract = models.TextField("Abstract")
    palavras_chave = models.ManyToManyField(PalavraChave, related_name='monografias')
    data_defesa = models.DateField("Data da Defesa")
    arquivo_pdf = models.FileField(
        upload_to=monografia_upload_path,
        validators=[
            # Validar tipo de arquivo aqui, se necessário
        ]
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    cadastrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='monografias_cadastradas'
    )

    def __str__(self):
        return f"{self.titulo} - {self.autor} ({self.data_defesa.year})"

    class Meta:
        verbose_name = "Monografia"
        verbose_name_plural = "Monografias"
        ordering = ['-data_defesa', 'titulo']


class ArquivoAdicional(models.Model):
    monografia = models.ForeignKey(
        Monografia,
        on_delete=models.CASCADE,
        related_name='arquivos_adicionais'
    )
    arquivo = models.FileField(upload_to=monografia_upload_path)
    descricao = models.CharField("Descrição", max_length=100)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - {self.monografia.titulo}"

    class Meta:
        verbose_name = "Arquivo Adicional"
        verbose_name_plural = "Arquivos Adicionais"


class HistoricoRevisao(models.Model):
    monografia = models.ForeignKey(
        Monografia,
        on_delete=models.CASCADE,
        related_name='historico_revisoes'
    )
    data_alteracao = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    descricao_alteracao = models.TextField("Descrição da alteração")

    def __str__(self):
        return f"Revisão em {self.data_alteracao.strftime('%d/%m/%Y %H:%M')} por {self.usuario.username}"

    class Meta:
        verbose_name = "Histórico de Revisão"
        verbose_name_plural = "Histórico de Revisões"
        ordering = ['-data_alteracao']