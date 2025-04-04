# monografia/admin.py
from django.contrib import admin
from .models import Monografia, Professor, PalavraChave, ArquivoAdicional, HistoricoRevisao


class ArquivoAdicionalInline(admin.TabularInline):
    model = ArquivoAdicional
    extra = 1


class HistoricoRevisaoInline(admin.TabularInline):
    model = HistoricoRevisao
    extra = 0
    readonly_fields = ['data_alteracao', 'usuario', 'descricao_alteracao']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Monografia)
class MonografiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'orientador', 'data_defesa', 'data_cadastro']
    list_filter = ['data_defesa', 'orientador', 'coorientador']
    search_fields = ['titulo', 'autor', 'resumo', 'abstract']
    date_hierarchy = 'data_defesa'
    filter_horizontal = ['palavras_chave']
    inlines = [ArquivoAdicionalInline, HistoricoRevisaoInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se é uma nova monografia
            obj.cadastrado_por = request.user
        super().save_model(request, obj, form, change)

        # Registrar alteração no histórico
        if change:  # Se é uma alteração, não uma criação
            HistoricoRevisao.objects.create(
                monografia=obj,
                usuario=request.user,
                descricao_alteracao="Alteração via painel administrativo."
            )


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'departamento']
    search_fields = ['nome', 'email', 'departamento']


@admin.register(PalavraChave)
class PalavraChaveAdmin(admin.ModelAdmin):
    list_display = ['palavra']
    search_fields = ['palavra']


@admin.register(ArquivoAdicional)
class ArquivoAdicionalAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'monografia', 'data_upload']
    list_filter = ['data_upload']
    search_fields = ['descricao', 'monografia__titulo']


@admin.register(HistoricoRevisao)
class HistoricoRevisaoAdmin(admin.ModelAdmin):
    list_display = ['monografia', 'data_alteracao', 'usuario', 'descricao_alteracao']
    list_filter = ['data_alteracao', 'usuario']
    search_fields = ['monografia__titulo', 'descricao_alteracao']
    readonly_fields = ['data_alteracao', 'usuario', 'descricao_alteracao', 'monografia']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False