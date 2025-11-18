from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from middlewares.auth_middleware import admin_required
from models.produto import Categoria
from config import db

categoria_bp = Blueprint("categoria_bp", __name__)


@categoria_bp.get("/")
def get_categorias():
    """Lista todas as categorias ativas"""
    try:
        categorias = Categoria.query.filter_by(ativo=True).all()
        return jsonify([c.to_dict() for c in categorias]), 200
    except Exception as e:
        print(f"Erro ao listar categorias: {str(e)}")
        return jsonify({"erro": "Erro ao listar categorias"}), 500


@categoria_bp.get("/<int:id_categoria>")
def get_categoria(id_categoria):
    """Busca uma categoria por ID"""
    try:
        categoria = Categoria.query.get(id_categoria)
        
        if not categoria:
            return jsonify({"erro": "Categoria não encontrada"}), 404
        
        return jsonify(categoria.to_dict()), 200
    except Exception as e:
        print(f"Erro ao buscar categoria: {str(e)}")
        return jsonify({"erro": "Erro ao buscar categoria"}), 500


@categoria_bp.post("/")
@admin_required()
def criar_categoria():
    """Cria uma nova categoria (apenas admin)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"erro": "Dados não fornecidos"}), 400
    
    nome = data.get("nome")
    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    
    try:
        # Verifica se já existe
        existe = Categoria.query.filter_by(nome=nome).first()
        if existe:
            return jsonify({"erro": "Categoria já existe"}), 400
        
        categoria = Categoria(
            nome=nome,
            descricao=data.get("descricao"),
            ativo=data.get("ativo", True)
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify({
            "mensagem": "Categoria criada com sucesso",
            "categoria": categoria.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar categoria: {str(e)}")
        return jsonify({"erro": "Erro ao criar categoria"}), 500


@categoria_bp.put("/<int:id_categoria>")
@admin_required()
def atualizar_categoria(id_categoria):
    """Atualiza uma categoria (apenas admin)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"erro": "Dados não fornecidos"}), 400
    
    try:
        categoria = Categoria.query.get(id_categoria)
        
        if not categoria:
            return jsonify({"erro": "Categoria não encontrada"}), 404
        
        # Atualiza campos
        if "nome" in data and data["nome"]:
            # Verifica se o nome já existe em outra categoria
            existe = Categoria.query.filter(
                Categoria.nome == data["nome"],
                Categoria.id_categoria != id_categoria
            ).first()
            
            if existe:
                return jsonify({"erro": "Nome já utilizado por outra categoria"}), 400
            
            categoria.nome = data["nome"]
        
        if "descricao" in data:
            categoria.descricao = data["descricao"]
        
        if "ativo" in data:
            categoria.ativo = data["ativo"]
        
        db.session.commit()
        
        return jsonify({
            "mensagem": "Categoria atualizada com sucesso",
            "categoria": categoria.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar categoria: {str(e)}")
        return jsonify({"erro": "Erro ao atualizar categoria"}), 500


@categoria_bp.delete("/<int:id_categoria>")
@admin_required()
def deletar_categoria(id_categoria):
    """Deleta uma categoria (apenas admin)"""
    try:
        categoria = Categoria.query.get(id_categoria)
        
        if not categoria:
            return jsonify({"erro": "Categoria não encontrada"}), 404
        
        # Verifica se tem produtos associados
        if categoria.produtos.count() > 0:
            return jsonify({
                "erro": "Não é possível deletar categoria com produtos associados",
                "mensagem": "Remova os produtos desta categoria primeiro"
            }), 400
        
        db.session.delete(categoria)
        db.session.commit()
        
        return jsonify({"mensagem": "Categoria removida com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar categoria: {str(e)}")
        return jsonify({"erro": "Erro ao deletar categoria"}), 500