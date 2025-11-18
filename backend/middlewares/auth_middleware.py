from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from controllers.auth_controller import obter_usuario_por_id

def admin_required():
    """
    Decorator para proteger rotas que exigem permissão de admin.
    Uso: @admin_required()
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            
            # Obtém as claims do token JWT
            claims = get_jwt()
            tipo_usuario = claims.get("tipo_usuario")
            
            # Valida se o tipo de usuário no token é admin
            if tipo_usuario != "admin":
                return jsonify({
                    "erro": "Acesso negado",
                    "mensagem": "Apenas administradores podem acessar este recurso"
                }), 403
            
            # Validação extra: verifica no banco de dados (segurança adicional)
            user_id = get_jwt_identity()
            user = obter_usuario_por_id(user_id)
            
            if not user or user.tipo_usuario != "admin":
                return jsonify({
                    "erro": "Acesso negado",
                    "mensagem": "Permissões insuficientes"
                }), 403
            
            return fn(*args, **kwargs)
        
        return decorator
    return wrapper

def cliente_ou_admin_required():
    """
    Decorator para rotas que podem ser acessadas por clientes ou admins
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            
            claims = get_jwt()
            tipo_usuario = claims.get("tipo_usuario")
            
            if tipo_usuario not in ["cliente", "admin"]:
                return jsonify({
                    "erro": "Acesso negado",
                    "mensagem": "Permissão insuficiente"
                }), 403
            
            return fn(*args, **kwargs)
        
        return decorator
    return wrapper

def entregador_ou_admin_required():
    """
    Decorator para rotas acessíveis por entregadores ou admins
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            
            claims = get_jwt()
            tipo_usuario = claims.get("tipo_usuario")
            
            if tipo_usuario not in ["entregador", "admin"]:
                return jsonify({
                    "erro": "Acesso negado",
                    "mensagem": "Apenas entregadores ou administradores podem acessar"
                }), 403
            
            return fn(*args, **kwargs)
        
        return decorator
    return wrapper