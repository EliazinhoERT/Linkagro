from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('home/', home, name='home'),
    path('login/', login_usuario, name='login'),
    path('cadastro/', cadastro_usuario, name='cadastro'),
    path('verificacao_enviada/', verificacao_enviada, name='verificacao_enviada'),
    path('verificar/<uuid:token>/', verificar_usuario, name='verificar_usuario'),
    path('produtos/producer/', listar_produtos_para_producer, name='listar_produtos_para_producer'),
    path('produtos/buyer/', listar_produtos_para_buyer, name='listar_produtos_para_buyer'),
    path('produtos/agrodealer/', listar_produtos_para_agrodealer, name='listar_produtos_para_agrodealer'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)