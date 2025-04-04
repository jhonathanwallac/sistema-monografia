# monografia/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Views de listagem e busca
    path('', views.index, name='index'),
    path('busca/', views.busca_simples, name='busca_simples'),
    path('busca/avancada/', views.busca_avancada, name='busca_avancada'),
    path('monografia/<int:pk>/', views.detalhes_monografia, name='detalhes_monografia'),

    # Views de operações CRUD
    path('monografia/nova/', views.criar_monografia, name='criar_monografia'),
    path('monografia/<int:pk>/editar/', views.editar_monografia, name='editar_monografia'),
    path('monografia/<int:pk>/excluir/', views.excluir_monografia, name='excluir_monografia'),

    # Views para arquivos adicionais
    path('monografia/<int:monografia_pk>/adicionar-arquivo/', views.adicionar_arquivo, name='adicionar_arquivo'),
    path('arquivo/<int:pk>/excluir/', views.excluir_arquivo, name='excluir_arquivo'),

    # Views para administração
    path('monografia/<int:monografia_pk>/historico/', views.historico_revisoes, name='historico_revisoes'),
    path('download/<str:tipo>/<int:pk>/', views.baixar_arquivo, name='baixar_arquivo'),
]