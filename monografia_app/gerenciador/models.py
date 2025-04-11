from django.db import models
from django.core.validators import FileExtensionValidator


class Monografia(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título")
    autor = models.CharField(max_length=255, verbose_name="Autor")
    orientador = models.CharField(max_length=255, verbose_name="Orientador")
    coorientador = models.CharField(max_length=255, verbose_name="Coorientador")
    resumo = models.TextField(verbose_name="Resumo")
    abstract = models.TextField(verbose_name="Abstract")
    palavras_chave = models.CharField(max_length=255, verbose_name="Palavras-chave")
    data_defesa = models.DateField(verbose_name="Data da Defesa")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Monografia"
        verbose_name_plural = "Monografias"
        ordering = ['-data_defesa']


class ArquivoMonografia(models.Model):
    monografia = models.ForeignKey(Monografia, on_delete=models.CASCADE, related_name='arquivos')
    arquivo = models.FileField(
        upload_to='monografias/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx']
            )
        ],
        verbose_name="Arquivo (PDF, Word ou PowerPoint)"
    )
    nome = models.CharField(max_length=255, verbose_name="Nome do arquivo")

    def __str__(self):
        return f"{self.nome} - {self.monografia.titulo}"

    class Meta:
        verbose_name = "Arquivo de Monografia"
        verbose_name_plural = "Arquivos de Monografia"

class HistoricoMonografia(models.Model):
    monografia = models.ForeignKey(Monografia, on_delete=models.CASCADE, related_name='historico')
    data_alteracao = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=255, blank=True, null=True)
    campo_alterado = models.CharField(max_length=50)
    valor_antigo = models.TextField()
    valor_novo = models.TextField()

    class Meta:
        verbose_name = "Histórico de Revisão"
        verbose_name_plural = "Histórico de Revisões"
        ordering = ['-data_alteracao']

    def __str__(self):
        return f"Alteração em {self.monografia.titulo} - {self.campo_alterado} em {self.data_alteracao}"