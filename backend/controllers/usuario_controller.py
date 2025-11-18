from models.usuario import Usuario
from config import db

def listar_usuarios():
    return [u.to_dict() for u in Usuario.query.all()]


def buscar_usuario(id_usuario):
    return Usuario.query.get(id_usuario)


def atualizar_usuario(id_usuario, data):
    user = Usuario.query.get(id_usuario)
    if not user:
        return None

    for campo, valor in data.items():
        if hasattr(user, campo) and valor is not None:
            setattr(user, campo, valor)

    db.session.commit()
    return user


def remover_usuario(id_usuario):
    user = Usuario.query.get(id_usuario)
    if not user:
        return False
    db.session.delete(user)
    db.session.commit()
    return True