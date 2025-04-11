from django.urls import path
from . import views

urlpatterns = [
    path('criar/', views.criar_monografia, name='criar_monografia'),
    path('monografia/<int:pk>/', views.monografia_detalhe, name='monografia_detalhe'),
    path('listar/', views.listar_monografias, name='listar_monografias'),
    path('monografia/<int:pk>/editar/', views.editar_monografia, name='editar_monografia'),
    path('monografia/<int:pk>/historico/', views.historico_monografia, name='historico_monografia'),
    path('monografia/<int:pk>/excluir/', views.excluir_monografia, name='excluir_monografia'),
]