# Generated by Django 5.2 on 2025-04-11 12:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gerenciador', '0003_alter_monografia_coorientador'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoMonografia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_alteracao', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.CharField(blank=True, max_length=255, null=True)),
                ('campo_alterado', models.CharField(max_length=50)),
                ('valor_antigo', models.TextField()),
                ('valor_novo', models.TextField()),
                ('monografia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico', to='gerenciador.monografia')),
            ],
            options={
                'verbose_name': 'Histórico de Revisão',
                'verbose_name_plural': 'Histórico de Revisões',
                'ordering': ['-data_alteracao'],
            },
        ),
    ]
