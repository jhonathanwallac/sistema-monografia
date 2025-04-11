import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import Monografia, ArquivoMonografia


class ArquivoMonografiaForm(forms.ModelForm):
    class Meta:
        model = ArquivoMonografia
        fields = ['arquivo', 'nome']
        widgets = {
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            if arquivo.size > 20 * 1024 * 1024:
                raise ValidationError("O arquivo não pode ser maior que 20MB.")
        return arquivo


class MonografiaForm(forms.ModelForm):
    class Meta:
        model = Monografia
        fields = ['titulo', 'autor', 'orientador', 'coorientador', 'resumo', 'abstract',
                  'palavras_chave', 'data_defesa']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'orientador': forms.TextInput(attrs={'class': 'form-control'}),
            'coorientador': forms.TextInput(attrs={'class': 'form-control'}),
            'resumo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'palavras_chave': forms.TextInput(attrs={'class': 'form-control'}),
            'data_defesa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        error_messages = {
            'titulo': {'required': 'O título é obrigatório.'},
            'autor': {'required': 'O autor é obrigatório.'},
            'orientador': {'required': 'O orientador é obrigatório.'},
            'coorientador': {'required': 'O coorientador é obrigatório.'},
            'resumo': {'required': 'O resumo é obrigatório.'},
            'abstract': {'required': 'O abstract é obrigatório.'},
            'palavras_chave': {'required': 'As palavras-chave são obrigatórias.'},
            'data_defesa': {'required': 'A data de defesa é obrigatória.'},
        }

    arquivo = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )

    def clean_data_defesa(self):
        data_defesa = self.cleaned_data.get('data_defesa')
        if data_defesa and data_defesa > datetime.date.today():
            raise ValidationError("A data de defesa não pode ser no futuro.")
        return data_defesa

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo and arquivo.size > 20 * 1024 * 1024:
            raise ValidationError("O arquivo não pode ser maior que 20MB.")
        return arquivo


class MonografiaBuscaForm(forms.Form):
    CAMPO_CHOICES = [
        ('todos', 'Todos os campos'),
        ('titulo', 'Título'),
        ('autor', 'Autor'),
        ('orientador', 'Orientador'),
        ('coorientador', 'Coorientador'),
        ('palavras_chave', 'Palavras-chave'),
        ('resumo', 'Resumo'),
        ('abstract', 'Abstract'),
    ]

    termo_busca = forms.CharField(
        label='Termo de busca',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    campo = forms.ChoiceField(
        label='Campo de busca',
        choices=CAMPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    data_inicio = forms.DateField(
        label='Data de defesa (início)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    data_fim = forms.DateField(
        label='Data de defesa (fim)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim and data_inicio > data_fim:
            raise forms.ValidationError("A data de início deve ser anterior à data de fim.")

        return cleaned_data
