import uuid
from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    OPCOES_CARGO = [
        ('agrodealer', 'Agrodistribuidor'),
        ('producer', 'Produtor'),
        ('buyer', 'Atacadista'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=20, choices=OPCOES_CARGO)
    distrito = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=255)
    telefone = models.CharField(max_length=13, null=True, blank=True)
    verificado = models.BooleanField(default=False)  # Indica se o perfil está verificado
    auth_token = models.UUIDField(default=uuid.uuid4, unique=True)  # Token de autenticação único

    def __str__(self):
        return self.user.username

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    categoria_pai = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategorias'
    )

    def __str__(self):
        if self.categoria_pai:
            return f"{self.categoria_pai.nome} > {self.nome}"
        return self.nome
    
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    quantidade_disponivel = models.PositiveIntegerField()
    preco_por_unidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Preço com desconto
    localizacao = models.CharField(max_length=255)
    qualidade = models.CharField(max_length=100)
    produtor = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="produtos")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO: adicionar a epoca
    def __str__(self):
        return self.nome

    def calcular_desconto_percentual(self):
                
        if self.preco_final and self.preco_final < self.preco_por_unidade:
            desconto = ((self.preco_por_unidade - self.preco_final) / self.preco_por_unidade) * 100
            return round(desconto, 0)  # Arredonda para 2 casas decimais
        return None
    
class ProdutoImagem(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="imagens")
    imagem = models.ImageField(upload_to="produtos/imagens/")  # Caminho onde as imagens serão salvas
    descricao = models.CharField(max_length=255, blank=True, null=True)  # Descrição opcional da imagem

    def __str__(self):
        return f"Imagem de {self.produto.nome}"

# Modelo para previsões de colheitas
class PrevisaoColheita(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="previsoes")
    data_inicio = models.DateField()
    data_fim = models.DateField()
    quantidade_prevista = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.produto.nome} ({self.data_inicio} - {self.data_fim})"

# Modelo para informações complementares
class InformacaoComplementar(models.Model):
    tipo = models.CharField(max_length=50)  # Ex: Estado das vias, Meteorologia
    descricao = models.TextField()
    distrito = models.CharField(max_length=100)
    data_hora_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo} - {self.distrito}"
