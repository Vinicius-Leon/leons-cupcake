from config import db
from models.entrega import Entrega

def listar_entregas():
    entregas = Entrega.query.order_by(Entrega.data_atribuicao.desc()).all()
    return [e.to_dict() for e in entregas]

def criar_entrega(data: dict):
    id_pedido = data.get('id_pedido')

    if not id_pedido:
        raise ValueError("id_pedido é obrigatório")

    entrega = Entrega(
        id_pedido=id_pedido,
        id_entregador=data.get('id_entregador'),
        observacoes=data.get('observacoes'),
        status=data.get('status', 'A caminho')
    )

    db.session.add(entrega)
    db.session.commit()
    return entrega

def atualizar_entrega(id_entrega: int, data: dict):
    entrega = Entrega.query.get(id_entrega)
    if not entrega:
        return None

    for campo in ['status','observacoes','id_entregador']:
        if campo in data:
            setattr(entrega, campo, data[campo])

    db.session.commit()
    return entrega