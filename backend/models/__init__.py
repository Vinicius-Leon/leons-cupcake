"""
Models do sistema Leon's Cupcake

Este arquivo centraliza a importação de todos os modelos para facilitar
o acesso em outras partes da aplicação.

Uso:
    from models import Usuario, Produto, Pedido, etc.
"""

# Modelos de usuário e endereço
from .usuario import Usuario
from .endereco import Endereco

# Modelos de produtos
from .produto import Produto, Categoria

# Modelos de pedidos
from .pedido import Pedido
from .item_pedido import ItemPedido

# Modelos de entrega
from .entrega import Entrega

# Lista de todos os modelos (útil para migrations e debug)
__all__ = [
    'Usuario',
    'Endereco',
    'Produto',
    'Categoria',
    'Pedido',
    'ItemPedido',
    'Entrega'
]