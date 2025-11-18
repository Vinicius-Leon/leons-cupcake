from flask import Blueprint, request, jsonify
from controllers.pedido_controller import criar_pedido, listar_pedidos, buscar_pedido

pedido_bp = Blueprint("pedido_bp", __name__)

@pedido_bp.post("/")
def post_pedido():
    data = request.get_json() or {}
    try:
        p = criar_pedido(data)
        return jsonify(p.to_dict()), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@pedido_bp.get("/")
def get_pedidos():
    return jsonify(listar_pedidos()), 200

@pedido_bp.get("/<int:id_pedido>")
def get_pedido(id_pedido):
    pedido = buscar_pedido(id_pedido)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    return jsonify(pedido.to_dict()), 200