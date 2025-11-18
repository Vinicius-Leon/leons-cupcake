from models.produto import Produto
from config import db

def listar_produtos():
    produtos = Produto.query.filter_by(ativo=True).all()
    return [p.to_dict() for p in produtos]

def buscar_produto(id_produto: int):
    return Produto.query.get(id_produto)

def criar_produto(data: dict):
    nome = data.get('nome')
    preco = data.get('preco')

    if not nome or preco is None:
        raise ValueError("nome e preco são obrigatórios")

    produto = Produto(
        nome=nome,
        descricao=data.get('descricao'),
        preco=preco,
        quantidade=data.get('quantidade', 0),
        imagem_url=data.get('imagem_url'),
        ativo=data.get('ativo', True)
    )

    db.session.add(produto)
    db.session.commit()

    return produto

def atualizar_produto(id_produto: int, data: dict):
    produto = Produto.query.get(id_produto)
    if not produto:
        return None

    for campo in ['nome','descricao','preco','quantidade','imagem_url','ativo']:
        if campo in data:
            setattr(produto, campo, data[campo])

    db.session.commit()
    return produto

def remover_produto(id_produto: int):
    produto = Produto.query.get(id_produto)
    if not produto:
        return False

    db.session.delete(produto)
    db.session.commit()
    return True