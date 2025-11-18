from flask import Blueprint, jsonify, request
from controllers.produto_controller import (
    listar_produtos,
    buscar_produto,
    criar_produto,
    atualizar_produto,
    remover_produto
)

produto_bp = Blueprint("produto_bp", __name__)

@produto_bp.get("/")
def get_produtos():
    return jsonify(listar_produtos()), 200

@produto_bp.get("/<int:id_produto>")
def get_produto(id_produto):
    produto = buscar_produto(id_produto)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(produto.to_dict()), 200

@produto_bp.post("/")
def post_produto():
    data = request.get_json() or {}
    try:
        produto = criar_produto(data)
        return jsonify(produto.to_dict()), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@produto_bp.put("/<int:id_produto>")
def put_produto(id_produto):
    data = request.get_json() or {}
    produto = atualizar_produto(id_produto, data)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(produto.to_dict()), 200

@produto_bp.delete("/<int:id_produto>")
def delete_produto(id_produto):
    ok = remover_produto(id_produto)
    if not ok:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify({"ok": True}), 200