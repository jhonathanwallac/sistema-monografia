from django import forms
from django.core.validators import FileExtensionValidator
from .models import Monografia, ArquivoAdicional, PalavraChave, Professor


class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['nome', 'email', 'departamento']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PalavraChaveForm(forms.ModelForm):
    class Meta:
        model = PalavraChave
        fields = ['palavra']
        widgets = {
            'palavra': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MonografiaForm(forms.ModelForm):
    palavras_chave_texto = forms.CharField(
        label="Palavras-chave (separadas por vírgula)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    arquivo_pdf = forms.FileField(
        label="Arquivo PDF da Monografia",
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    class Meta:
        model = Monografia
        fields = [
            'titulo', 'autor', 'orientador', 'coorientador', 'resumo',
            'abstract', 'data_defesa', 'arquivo_pdf'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'orientador': forms.Select(attrs={'class': 'form-control'}),
            'coorientador': forms.Select(attrs={'class': 'form-control'}),
            'resumo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'data_defesa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

        if user:
            instance.cadastrado_por = user

        if commit:
            instance.save()
            self.save_m2m()

            # Processar palavras-chave
            if self.cleaned_data.get('palavras_chave_texto'):
                palavras = [p.strip() for p in self.cleaned_data['palavras_chave_texto'].split(',')]
                for palavra in palavras:
                    if palavra:
                        obj, created = PalavraChave.objects.get_or_create(palavra=palavra)
                        instance.palavras_chave.add(obj)

        return instance


class ArquivoAdicionalForm(forms.ModelForm):
    class Meta:
        model = ArquivoAdicional
        fields = ['descricao', 'arquivo']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class BuscaAvancadaForm(forms.Form):
    termo = forms.CharField(
        label="Termo de busca",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    campo = forms.ChoiceField(
        label="Buscar em",
        choices=[
            ('titulo', 'Título'),
            ('autor', 'Autor'),
            ('orientador', 'Orientador'),
            ('coorientador', 'Coorientador'),
            ('palavras_chave', 'Palavras-chave'),
            ('resumo', 'Resumo'),
            ('abstract', 'Abstract'),
            ('todos', 'Todos os campos'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    data_inicio = forms.DateField(
        label="Data inicial",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_fim = forms.DateField(
        label="Data final",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    ordenar_por = forms.ChoiceField(
        label="Ordenar por",
        choices=[
            ('data_defesa', 'Data de defesa'),
            ('titulo', 'Título'),
            ('autor', 'Autor'),
            ('data_cadastro', 'Data de cadastro'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ordem = forms.ChoiceField(
        label="Ordem",
        choices=[
            ('asc', 'Crescente'),
            ('desc', 'Decrescente'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )