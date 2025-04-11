from django.contrib import admin
from .models import Monografia

@admin.register(Monografia)
class MonografiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'orientador', 'data_defesa', 'criado_em')
    search_fields = ('titulo', 'autor', 'orientador', 'coorientador', 'resumo', 'abstract', 'palavras_chave')
    list_filter = ('data_defesa', 'criado_em')
    date_hierarchy = 'data_defesa'