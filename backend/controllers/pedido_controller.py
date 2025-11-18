from config import db
from models.pedido import Pedido, ItemPedido
from models.usuario import Usuario
from models.produto import Produto

def criar_pedido(payload: dict):
    id_usuario = payload.get("id_usuario")
    itens = payload.get("itens", [])

    if not id_usuario or not itens:
        raise ValueError("id_usuario e itens são obrigatórios")

    user = Usuario.query.get(id_usuario)
    if not user:
        raise ValueError("Usuário não encontrado")

    pedido = Pedido(id_usuario=id_usuario)
    db.session.add(pedido)
    db.session.flush()

    total = 0.0

    for it in itens:
        id_prod = it.get("id_produto")
        quantidade = it.get("quantidade", 1)

        produto = Produto.query.get(id_prod)
        if not produto:
            db.session.rollback()
            raise ValueError(f"Produto {id_prod} não encontrado")

        if produto.quantidade < quantidade:
            db.session.rollback()
            raise ValueError(f"Estoque insuficiente para {produto.nome}")

        produto.quantidade -= quantidade

        item = ItemPedido(
            id_pedido=pedido.id_pedido,
            id_produto=id_prod,
            quantidade=quantidade,
            preco_unitario=produto.preco
        )
        db.session.add(item)

        total += float(produto.preco) * quantidade

    pedido.valor_total = total
    db.session.commit()

    return pedido

def listar_pedidos():
    pedidos = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
    return [p.to_dict() for p in pedidos]

def buscar_pedido(id_pedido: int):
    return Pedido.query.get(id_pedido)