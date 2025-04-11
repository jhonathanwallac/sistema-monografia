# Generated by Django 5.2 on 2025-04-11 04:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Monografia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255, verbose_name='Título')),
                ('autor', models.CharField(max_length=255, verbose_name='Autor')),
                ('orientador', models.CharField(max_length=255, verbose_name='Orientador')),
                ('coorientador', models.CharField(blank=True, max_length=255, null=True, verbose_name='Coorientador')),
                ('resumo', models.TextField(verbose_name='Resumo')),
                ('abstract', models.TextField(verbose_name='Abstract')),
                ('palavras_chave', models.CharField(max_length=255, verbose_name='Palavras-chave')),
                ('data_defesa', models.DateField(verbose_name='Data da Defesa')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('arquivo', models.FileField(upload_to='monografias/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx'])], verbose_name='Arquivo (PDF, Word ou PowerPoint)')),
            ],
            options={
                'verbose_name': 'Monografia',
                'verbose_name_plural': 'Monografias',
                'ordering': ['-data_defesa'],
            },
        ),
    ]
