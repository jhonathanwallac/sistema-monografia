from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.utils import timezone

from .models import Monografia, ArquivoAdicional, HistoricoRevisao, PalavraChave, Professor
from .forms import MonografiaForm, ArquivoAdicionalForm, BuscaAvancadaForm, ProfessorForm, PalavraChaveForm


# Views para listagem e busca
def index(request):
    monografias_recentes = Monografia.objects.all().order_by('-data_cadastro')[:5]
    total_monografias = Monografia.objects.count()
    total_professores = Professor.objects.count()

    context = {
        'monografias_recentes': monografias_recentes,
        'total_monografias': total_monografias,
        'total_professores': total_professores,
        'form_busca': BuscaAvancadaForm(),
    }
    return render(request, 'monografia/index.html', context)


def busca_simples(request):
    termo = request.GET.get('termo', '')

    if termo:
        resultados = Monografia.objects.filter(
            Q(titulo__icontains=termo) |
            Q(autor__icontains=termo) |
            Q(orientador__nome__icontains=termo) |
            Q(coorientador__nome__icontains=termo) |
            Q(resumo__icontains=termo) |
            Q(abstract__icontains=termo) |
            Q(palavras_chave__palavra__icontains=termo)
        ).distinct()
    else:
        resultados = Monografia.objects.all()

    paginator = Paginator(resultados.order_by('-data_defesa'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'termo': termo,
        'total_resultados': resultados.count(),
    }
    return render(request, 'monografia/resultados_busca.html', context)


def busca_avancada(request):
    form = BuscaAvancadaForm(request.GET)
    resultados = Monografia.objects.all()

    if form.is_valid():
        termo = form.cleaned_data.get('termo')
        campo = form.cleaned_data.get('campo')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        ordenar_por = form.cleaned_data.get('ordenar_por')
        ordem = form.cleaned_data.get('ordem')

        # Aplicar filtros se fornecidos
        if termo:
            if campo == 'titulo':
                resultados = resultados.filter(titulo__icontains=termo)
            elif campo == 'autor':
                resultados = resultados.filter(autor__icontains=termo)
            elif campo == 'orientador':
                resultados = resultados.filter(orientador__nome__icontains=termo)
            elif campo == 'coorientador':
                resultados = resultados.filter(coorientador__nome__icontains=termo)
            elif campo == 'palavras_chave':
                resultados = resultados.filter(palavras_chave__palavra__icontains=termo).distinct()
            elif campo == 'resumo':
                resultados = resultados.filter(resumo__icontains=termo)
            elif campo == 'abstract':
                resultados = resultados.filter(abstract__icontains=termo)
            elif campo == 'todos':
                resultados = resultados.filter(
                    Q(titulo__icontains=termo) |
                    Q(autor__icontains=termo) |
                    Q(orientador__nome__icontains=termo) |
                    Q(coorientador__nome__icontains=termo) |
                    Q(resumo__icontains=termo) |
                    Q(abstract__icontains=termo) |
                    Q(palavras_chave__palavra__icontains=termo)
                ).distinct()

        # Filtrar por datas
        if data_inicio:
            resultados = resultados.filter(data_defesa__gte=data_inicio)
        if data_fim:
            resultados = resultados.filter(data_defesa__lte=data_fim)

        # Ordenação
        order_prefix = '-' if ordem == 'desc' else ''
        resultados = resultados.order_by(f'{order_prefix}{ordenar_por}')

    paginator = Paginator(resultados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'total_resultados': resultados.count(),
    }
    return render(request, 'monografia/busca_avancada.html', context)


def detalhes_monografia(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)
    arquivos_adicionais = monografia.arquivos_adicionais.all()

    context = {
        'monografia': monografia,
        'arquivos_adicionais': arquivos_adicionais,
    }
    return render(request, 'monografia/detalhes_monografia.html', context)


# Views para operações CRUD
@login_required
@permission_required('monografia.add_monografia', raise_exception=True)
def criar_monografia(request):
    if request.method == 'POST':
        form = MonografiaForm(request.POST, request.FILES)
        if form.is_valid():
            monografia = form.save(commit=True, user=request.user)

            # Registrar no histórico
            HistoricoRevisao.objects.create(
                monografia=monografia,
                usuario=request.user,
                descricao_alteracao="Criação inicial da monografia."
            )

            messages.success(request, "Monografia cadastrada com sucesso!")
            return redirect('detalhes_monografia', pk=monografia.pk)
    else:
        form = MonografiaForm()

    context = {
        'form': form,
        'titulo': 'Cadastrar Nova Monografia',
    }
    return render(request, 'monografia/form_monografia.html', context)


@login_required
@permission_required('monografia.change_monografia', raise_exception=True)
def editar_monografia(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)

    if request.method == 'POST':
        form = MonografiaForm(request.POST, request.FILES, instance=monografia)
        if form.is_valid():
            # Guardar alterações para histórico
            alteracoes = []
            for field in form.changed_data:
                if field != 'arquivo_pdf' and field != 'palavras_chave_texto':
                    old_value = getattr(monografia, field)
                    new_value = form.cleaned_data[field]
                    alteracoes.append(f"{field}: {old_value} -> {new_value}")

            monografia = form.save(user=request.user)

            # Registrar no histórico se houver alterações
            if alteracoes or 'arquivo_pdf' in form.changed_data:
                descricao = "Alterações realizadas: " + "; ".join(alteracoes)
                if 'arquivo_pdf' in form.changed_data:
                    descricao += "; Arquivo PDF atualizado"

                HistoricoRevisao.objects.create(
                    monografia=monografia,
                    usuario=request.user,
                    descricao_alteracao=descricao
                )

            messages.success(request, "Monografia atualizada com sucesso!")
            return redirect('detalhes_monografia', pk=monografia.pk)
    else:
        # Pré-preencher palavras-chave
        palavras = ", ".join([p.palavra for p in monografia.palavras_chave.all()])
        form = MonografiaForm(instance=monografia, initial={'palavras_chave_texto': palavras})

    context = {
        'form': form,
        'monografia': monografia,
        'titulo': 'Editar Monografia',
    }
    return render(request, 'monografia/form_monografia.html', context)


@login_required
@permission_required('monografia.delete_monografia', raise_exception=True)
def excluir_monografia(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)

    if request.method == 'POST':
        if request.POST.get('confirmar') == 'sim':
            titulo = monografia.titulo
            monografia.delete()
            messages.success(request, f"Monografia '{titulo}' excluída com sucesso!")
            return redirect('index')
        else:
            return redirect('detalhes_monografia', pk=monografia.pk)

    context = {
        'monografia': monografia,
    }
    return render(request, 'monografia/confirmar_exclusao.html', context)


# Views para arquivos adicionais
@login_required
@permission_required('monografia.add_arquivoadicional', raise_exception=True)
def adicionar_arquivo(request, monografia_pk):
    monografia = get_object_or_404(Monografia, pk=monografia_pk)

    if request.method == 'POST':
        form = ArquivoAdicionalForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.save(commit=False)
            arquivo.monografia = monografia
            arquivo.save()

            # Registrar no histórico
            HistoricoRevisao.objects.create(
                monografia=monografia,
                usuario=request.user,
                descricao_alteracao=f"Arquivo adicional '{arquivo.descricao}' adicionado."
            )

            messages.success(request, "Arquivo adicional incluído com sucesso!")
            return redirect('detalhes_monografia', pk=monografia.pk)
    else:
        form = ArquivoAdicionalForm()

    context = {
        'form': form,
        'monografia': monografia,
    }
    return render(request, 'monografia/form_arquivo_adicional.html', context)


@login_required
@permission_required('monografia.delete_arquivoadicional', raise_exception=True)
def excluir_arquivo(request, pk):
    arquivo = get_object_or_404(ArquivoAdicional, pk=pk)
    monografia = arquivo.monografia

    if request.method == 'POST':
        if request.POST.get('confirmar') == 'sim':
            descricao = arquivo.descricao
            arquivo.delete()

            # Registrar no histórico
            HistoricoRevisao.objects.create(
                monografia=monografia,
                usuario=request.user,
                descricao_alteracao=f"Arquivo adicional '{descricao}' removido."
            )

            messages.success(request, f"Arquivo '{descricao}' excluído com sucesso!")

        return redirect('detalhes_monografia', pk=monografia.pk)

    context = {
        'arquivo': arquivo,
        'monografia': monografia,
    }
    return render(request, 'monografia/confirmar_exclusao_arquivo.html', context)


# Views para administração
@login_required
@permission_required('monografia.view_historicorevisao', raise_exception=True)
def historico_revisoes(request, monografia_pk):
    monografia = get_object_or_404(Monografia, pk=monografia_pk)
    revisoes = monografia.historico_revisoes.all().order_by('-data_alteracao')

    context = {
        'monografia': monografia,
        'revisoes': revisoes,
    }
    return render(request, 'monografia/historico_revisoes.html', context)


@login_required
def baixar_arquivo(request, tipo, pk):
    if tipo == 'monografia':
        arquivo = get_object_or_404(Monografia, pk=pk).arquivo_pdf
    else:
        arquivo = get_object_or_404(ArquivoAdicional, pk=pk).arquivo

    return FileResponse(arquivo.open(), as_attachment=True, filename=arquivo.name.split('/')[-1])