from django.contrib import admin
from .models import PerfilUsuario, Produto, PrevisaoColheita, Categoria, ProdutoImagem

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'cargo', 'verificado')  # Exibir o campo no admin
    list_filter = ('verificado', 'cargo')  # Filtrar por verificação

admin.site.register(PrevisaoColheita)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria_pai')
    search_fields = ('nome',)

class ProdutoImagemInline(admin.TabularInline):
    model = ProdutoImagem
    extra = 1  # Número de imagens extras para adicionar no formulário

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_por_unidade', 'preco_final', 'desconto_percentual')
    inlines = [ProdutoImagemInline]
    def desconto_percentual(self, obj):
        return f"{obj.calcular_desconto_percentual()}%" if obj.calcular_desconto_percentual() is not None else "Sem desconto"
    desconto_percentual.short_description = "Desconto (%)"

admin.site.register(ProdutoImagem)