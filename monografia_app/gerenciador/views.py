from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .forms import MonografiaForm, MonografiaBuscaForm
from .models import Monografia, ArquivoMonografia, HistoricoMonografia


def criar_monografia(request):
    if request.method == 'POST':
        form = MonografiaForm(request.POST, request.FILES)
        arquivos = request.FILES.getlist('arquivos')

        if form.is_valid():
            monografia = form.save()

            for arquivo in arquivos:
                if arquivo.size > 20 * 1024 * 1024:
                    messages.warning(request, f"O arquivo {arquivo.name} ultrapassa 20MB e foi ignorado.")
                    continue

                ArquivoMonografia.objects.create(
                    monografia=monografia,
                    arquivo=arquivo,
                    nome=arquivo.name
                )

            messages.success(request, 'Monografia cadastrada com sucesso!')
            return redirect('monografia_detalhe', pk=monografia.pk)
    else:
        form = MonografiaForm()

    return render(request, 'gerenciador/criar_monografia.html', {'form': form})


def monografia_detalhe(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)
    return render(request, 'gerenciador/monografia_detalhe.html', {'monografia': monografia})

def listar_monografias(request):
    form = MonografiaBuscaForm(request.GET or None)
    queryset = Monografia.objects.all()

    if form.is_valid():
        termo_busca = form.cleaned_data.get('termo_busca')
        campo = form.cleaned_data.get('campo')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')

        if termo_busca:
            if campo == 'titulo':
                queryset = queryset.filter(titulo__icontains=termo_busca)
            elif campo == 'autor':
                queryset = queryset.filter(autor__icontains=termo_busca)
            elif campo == 'orientador':
                queryset = queryset.filter(orientador__icontains=termo_busca)
            elif campo == 'coorientador':
                queryset = queryset.filter(coorientador__icontains=termo_busca)
            elif campo == 'palavras_chave':
                queryset = queryset.filter(palavras_chave__icontains=termo_busca)
            elif campo == 'resumo':
                queryset = queryset.filter(resumo__icontains=termo_busca)
            elif campo == 'abstract':
                queryset = queryset.filter(abstract__icontains=termo_busca)
            else:
                queryset = queryset.filter(
                    Q(titulo__icontains=termo_busca) |
                    Q(autor__icontains=termo_busca) |
                    Q(orientador__icontains=termo_busca) |
                    Q(coorientador__icontains=termo_busca) |
                    Q(palavras_chave__icontains=termo_busca) |
                    Q(resumo__icontains=termo_busca) |
                    Q(abstract__icontains=termo_busca)
                )

        if data_inicio:
            queryset = queryset.filter(data_defesa__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_defesa__lte=data_fim)

    ordem = request.GET.get('ordem', 'titulo')
    queryset = queryset.order_by(ordem)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gerenciador/listar_monografias.html', {
        'form': form,
        'page_obj': page_obj,
        'ordem': ordem
    })


def editar_monografia(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)
    arquivo_atual = monografia.arquivos.first()

    if request.method == 'POST':
        form = MonografiaForm(request.POST, request.FILES, instance=monografia)
        if form.is_valid():
            monografia_antes = Monografia.objects.get(pk=pk)
            monografia_atualizada = form.save()

            campos = ['titulo', 'autor', 'orientador', 'coorientador', 'resumo',
                      'abstract', 'palavras_chave', 'data_defesa']

            for campo in campos:
                valor_antigo = getattr(monografia_antes, campo)
                valor_novo = getattr(monografia_atualizada, campo)

                if str(valor_antigo) != str(valor_novo):
                    HistoricoMonografia.objects.create(
                        monografia=monografia_atualizada,
                        campo_alterado=campo,
                        valor_antigo=str(valor_antigo),
                        valor_novo=str(valor_novo),
                        usuario=request.user.username if request.user.is_authenticated else None
                    )

            arquivo_novo = request.FILES.get('arquivo')
            if arquivo_novo:
                if arquivo_atual:
                    HistoricoMonografia.objects.create(
                        monografia=monografia_atualizada,
                        campo_alterado='arquivo',
                        valor_antigo=arquivo_atual.nome,
                        valor_novo=arquivo_novo.name,
                        usuario=request.user.username if request.user.is_authenticated else None
                    )
                    arquivo_atual.delete()

                ArquivoMonografia.objects.create(
                    monografia=monografia_atualizada,
                    arquivo=arquivo_novo,
                    nome=arquivo_novo.name
                )

            messages.success(request, 'Monografia atualizada com sucesso!')
            return redirect('monografia_detalhe', pk=monografia.pk)
    else:
        form = MonografiaForm(instance=monografia)

    return render(request, 'gerenciador/editar_monografia.html', {
        'form': form,
        'monografia': monografia,
        'arquivo_atual': arquivo_atual
    })


def historico_monografia(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)
    historico = monografia.historico.all()

    return render(request, 'gerenciador/historico_monografia.html', {
        'monografia': monografia,
        'historico': historico
    })


def excluir_monografia(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)

    if request.method == 'POST':
        titulo = monografia.titulo
        monografia.delete()
        messages.success(request, f'Monografia "{titulo}" excluída com sucesso.')
        return redirect('listar_monografias')

    return render(request, 'gerenciador/confirmar_exclusao.html', {'monografia': monografia})