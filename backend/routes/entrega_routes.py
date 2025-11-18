from flask import Blueprint, request, jsonify
from controllers.entrega_controller import listar_entregas, criar_entrega, atualizar_entrega

entrega_bp = Blueprint("entrega_bp", __name__)

@entrega_bp.get("/")
def get_entregas():
    return jsonify(listar_entregas()), 200

@entrega_bp.post("/")
def post_entrega():
    data = request.get_json() or {}
    try:
        ent = criar_entrega(data)
        return jsonify(ent.to_dict()), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@entrega_bp.put("/<int:id_entrega>")
def put_entrega(id_entrega):
    data = request.get_json() or {}
    ent = atualizar_entrega(id_entrega, data)
    if not ent:
        return jsonify({"erro": "Entrega não encontrada"}), 404
    return jsonify(ent.to_dict()), 200
