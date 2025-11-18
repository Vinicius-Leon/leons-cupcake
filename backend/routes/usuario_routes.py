from flask import Blueprint, request, jsonify
from controllers.usuario_controller import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from middlewares.auth_middleware import admin_required

usuario_bp = Blueprint("usuario_bp", __name__)

@usuario_bp.get("/")
@admin_required()
def listar():
    """Lista todos os usuários - APENAS ADMIN"""
    return jsonify(listar_usuarios())

@usuario_bp.get("/me")
@jwt_required()
def meu_perfil():
    """Retorna o perfil do usuário logado"""
    user_id = get_jwt_identity()
    u = buscar_usuario(user_id)
    if not u:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(u.to_dict())

@usuario_bp.get("/<int:id_usuario>")
@jwt_required()
def buscar(id_usuario):
    """Busca um usuário específico"""
    current_user_id = get_jwt_identity()
    
    # Se o usuário está buscando seu próprio perfil, permite
    if current_user_id == id_usuario:
        u = buscar_usuario(id_usuario)
        if not u:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify(u.to_dict())
    
    # Se está buscando outro usuário, verifica se é admin
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get("tipo_usuario") != "admin":
        return jsonify({
            "erro": "Acesso negado",
            "mensagem": "Você só pode visualizar seu próprio perfil"
        }), 403
    
    u = buscar_usuario(id_usuario)
    if not u:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(u.to_dict())

@usuario_bp.put("/<int:id_usuario>")
@jwt_required()
def atualizar(id_usuario):
    """Atualiza um usuário"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Se o usuário está atualizando seu próprio perfil
    if current_user_id == id_usuario:
        # Remove campos que o usuário não pode alterar sozinho
        campos_proibidos = ['tipo_usuario', 'id_usuario']
        for campo in campos_proibidos:
            data.pop(campo, None)
        
        user = atualizar_usuario(id_usuario, data)
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify(user.to_dict())
    
    # Se está tentando atualizar outro usuário, verifica se é admin
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get("tipo_usuario") != "admin":
        return jsonify({
            "erro": "Acesso negado",
            "mensagem": "Você só pode atualizar seu próprio perfil"
        }), 403
    
    user = atualizar_usuario(id_usuario, data)
    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(user.to_dict())

@usuario_bp.delete("/<int:id_usuario>")
@admin_required()
def remover(id_usuario):
    """Remove um usuário - APENAS ADMIN"""
    if remover_usuario(id_usuario):
        return jsonify({"mensagem": "Usuário removido com sucesso"}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404