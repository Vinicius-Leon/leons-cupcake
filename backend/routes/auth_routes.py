from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from controllers.auth_controller import registrar_usuario, autenticar, obter_usuario_por_id
from datetime import timedelta

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.post("/register")
def register():
    """
    Endpoint para registrar novo usuário
    
    Body JSON:
        {
            "nome": "string (obrigatório)",
            "email": "string (obrigatório)",
            "senha": "string (obrigatório, mín. 6 caracteres)",
            "cpf": "string (opcional)",
            "telefone": "string (opcional)"
        }
    
    Returns:
        201: Usuário criado com sucesso
        400: Erro de validação
        500: Erro interno
    """
    try:
        print("\n" + "="*60)
        print("📝 NOVO REGISTRO DE USUÁRIO")
        print("="*60)
        
        # Obter dados do request
        data = request.get_json()
        print(f"📦 Dados recebidos: {data}")
        
        # Validar se dados foram fornecidos
        if not data:
            print("❌ Nenhum dado fornecido no body")
            return jsonify({"erro": "Dados não fornecidos"}), 400
        
        # Validar campos obrigatórios
        required_fields = ['nome', 'email', 'senha', 'cpf', 'telefone']
        missing_fields = []
        
        if not data.get('cpf') or len(data.get('cpf').replace('.', '').replace('-', '').replace(' ', '')) != 11:
            return jsonify({"erro": "CPF válido é obrigatório"}), 400

        if not data.get('telefone') or len(data.get('telefone').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')) < 10:
            return jsonify({"erro": "Telefone válido é obrigatório"}), 400


        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                missing_fields.append(field)
        
        if missing_fields:
            erro = f"Campos obrigatórios faltando: {', '.join(missing_fields)}"
            print(f"❌ {erro}")
            return jsonify({"erro": erro}), 400
        
        # Extrair e limpar dados
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip().lower()
        senha = data.get('senha', '').strip()
        
        print(f"📋 Validando dados:")
        print(f"   - Nome: {nome}")
        print(f"   - Email: {email}")
        print(f"   - Senha: {'*' * len(senha)} ({len(senha)} caracteres)")
        
        # Validar nome
        if len(nome) < 3:
            print("❌ Nome muito curto")
            return jsonify({"erro": "Nome deve ter pelo menos 3 caracteres"}), 400
        
        # Validar email
        if '@' not in email or '.' not in email.split('@')[-1]:
            print(f"❌ Email inválido: {email}")
            return jsonify({"erro": "Email inválido"}), 400
        
        # Validar senha
        if len(senha) < 6:
            print(f"❌ Senha muito curta: {len(senha)} caracteres")
            return jsonify({"erro": "Senha deve ter pelo menos 6 caracteres"}), 400
        
        # Preparar dados limpos para o controller
        dados_limpos = {
            'nome': nome,
            'email': email,
            'senha': senha
        }
        
        # Adicionar campos opcionais se fornecidos
        if data.get('cpf'):
            cpf_limpo = data.get('cpf', '').replace('.', '').replace('-', '').strip()
            if cpf_limpo:
                dados_limpos['cpf'] = cpf_limpo
                print(f"   - CPF: {cpf_limpo[:3]}***{cpf_limpo[-2:]}")
        
        if data.get('telefone'):
            telefone_limpo = data.get('telefone', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '').strip()
            if telefone_limpo:
                dados_limpos['telefone'] = telefone_limpo
                print(f"   - Telefone: {telefone_limpo[:2]}***{telefone_limpo[-2:]}")
        
        print("✅ Dados validados com sucesso")
        print("🔄 Chamando controller para criar usuário...")
        
        # Criar usuário através do controller
        user = registrar_usuario(dados_limpos)
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   - ID: {user.id_usuario}")
        print(f"   - Nome: {user.nome}")
        print(f"   - Email: {user.email}")
        print("="*60 + "\n")
        
        return jsonify({
            "mensagem": "Usuário registrado com sucesso",
            "usuario": user.to_dict()
        }), 201
        
    except ValueError as e:
        # Erros de validação do controller
        print(f"❌ Erro de validação: {str(e)}")
        print("="*60 + "\n")
        return jsonify({"erro": str(e)}), 400
    
    except Exception as e:
        # Erros inesperados
        print(f"\n❌❌❌ ERRO INESPERADO NO REGISTRO ❌❌❌")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({
            "erro": "Erro ao registrar usuário",
            "detalhes": str(e)
        }), 500


@auth_bp.post("/login")
def login():
    """
    Endpoint para autenticar usuário
    
    Body JSON:
        {
            "email": "string (obrigatório)",
            "senha": "string (obrigatório)"
        }
    
    Returns:
        200: Login bem-sucedido com token JWT
        400: Dados inválidos
        401: Credenciais incorretas
        403: Usuário inativo
        500: Erro interno
    """
    try:
        print("\n" + "="*60)
        print("🔐 TENTATIVA DE LOGIN")
        print("="*60)
        
        # Obter dados do request
        data = request.get_json()
        
        if not data:
            print("❌ Nenhum dado fornecido")
            return jsonify({"erro": "Dados não fornecidos"}), 400
        
        # Extrair e limpar credenciais
        email = data.get("email", "").strip().lower()
        senha = data.get("senha", "")
        
        print(f"📧 Email: {email}")
        print(f"🔑 Senha: {'*' * len(senha) if senha else '(vazia)'}")
        
        # Validar campos
        if not email or not senha:
            print("❌ Email ou senha não fornecidos")
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400
        
        # Tentar autenticar
        print(f"🔍 Autenticando usuário...")
        user = autenticar(email, senha)
        
        if not user:
            print(f"❌ Credenciais inválidas para: {email}")
            print("="*60 + "\n")
            return jsonify({"erro": "Email ou senha incorretos"}), 401
        
        # Verificar se usuário está ativo
        if not user.ativo:
            print(f"⚠️ Usuário inativo: {email}")
            print("="*60 + "\n")
            return jsonify({"erro": "Usuário inativo. Entre em contato com o suporte"}), 403
        
        print(f"✅ Autenticação bem-sucedida!")
        print(f"   - ID: {user.id_usuario}")
        print(f"   - Nome: {user.nome}")
        print(f"   - Tipo: {user.tipo_usuario}")
        
        # Criar claims adicionais para o token
        additional_claims = {
            "tipo_usuario": user.tipo_usuario,
            "email": user.email,
            "nome": user.nome
        }
        
        print(f"🎫 Gerando token JWT...")
        
        # Gerar token JWT
        token = create_access_token(
            identity=user.id_usuario,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )
        
        print(f"✅ Token gerado: {token[:30]}...")
        
        # Preparar resposta
        response_data = {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 86400,  # 24 horas em segundos
            "user": user.to_dict()
        }
        
        print("✅ Login realizado com sucesso!")
        print("="*60 + "\n")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"\n❌❌❌ ERRO NO LOGIN ❌❌❌")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({
            "erro": "Erro ao fazer login",
            "detalhes": str(e)
        }), 500


@auth_bp.get("/me")
@jwt_required()
def get_current_user():
    """
    Endpoint para obter dados do usuário logado
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Dados do usuário
        404: Usuário não encontrado
        403: Usuário inativo
        401: Token inválido/expirado
    """
    try:
        print("\n" + "="*60)
        print("👤 BUSCAR DADOS DO USUÁRIO")
        print("="*60)
        
        # Obter ID do usuário do token JWT
        user_id = get_jwt_identity()
        print(f"🆔 User ID do token: {user_id}")
        
        # Buscar usuário no banco
        print("🔍 Buscando usuário no banco...")
        user = obter_usuario_por_id(user_id)
        
        if not user:
            print(f"❌ Usuário ID {user_id} não encontrado no banco")
            print("="*60 + "\n")
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        if not user.ativo:
            print(f"⚠️ Usuário ID {user_id} está inativo")
            print("="*60 + "\n")
            return jsonify({"erro": "Usuário inativo"}), 403
        
        print(f"✅ Usuário encontrado:")
        print(f"   - ID: {user.id_usuario}")
        print(f"   - Nome: {user.nome}")
        print(f"   - Email: {user.email}")
        print(f"   - Tipo: {user.tipo_usuario}")
        print("="*60 + "\n")
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        print(f"\n❌ Erro em /me: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({"erro": "Erro ao buscar informações do usuário"}), 500


@auth_bp.post("/refresh")
@jwt_required()
def refresh_token():
    """
    Endpoint para renovar token JWT
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Novo token gerado
        401: Token inválido/expirado
    """
    try:
        print("\n" + "="*60)
        print("🔄 RENOVAR TOKEN")
        print("="*60)
        
        # Obter dados do token atual
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        print(f"🆔 User ID: {user_id}")
        print(f"📋 Claims atuais: {claims.get('tipo_usuario')}")
        
        # Criar claims para novo token
        additional_claims = {
            "tipo_usuario": claims.get("tipo_usuario"),
            "email": claims.get("email"),
            "nome": claims.get("nome")
        }
        
        # Gerar novo token
        new_token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )
        
        print(f"✅ Novo token gerado: {new_token[:30]}...")
        print("="*60 + "\n")
        
        return jsonify({
            "access_token": new_token,
            "token_type": "Bearer",
            "expires_in": 86400
        }), 200
        
    except Exception as e:
        print(f"\n❌ Erro ao renovar token: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({"erro": "Erro ao renovar token"}), 500


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """
    Endpoint para logout (lado servidor apenas registra)
    O frontend deve limpar o token do localStorage
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Logout registrado
    """
    try:
        user_id = get_jwt_identity()
        print(f"\n👋 Logout do usuário ID: {user_id}\n")
        
        return jsonify({"mensagem": "Logout realizado com sucesso"}), 200
    
    except Exception as e:
        print(f"❌ Erro no logout: {str(e)}")
        return jsonify({"mensagem": "Logout realizado"}), 200


@auth_bp.get("/verify")
@jwt_required()
def verify_token():
    """
    Endpoint para verificar se token é válido
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Token válido com informações
        401: Token inválido/expirado
    """
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        return jsonify({
            "valido": True,
            "user_id": user_id,
            "tipo_usuario": claims.get("tipo_usuario"),
            "email": claims.get("email"),
            "nome": claims.get("nome")
        }), 200
        
    except Exception as e:
        return jsonify({
            "valido": False,
            "erro": str(e)
        }), 401


# Rota de teste (opcional - remover em produção)
@auth_bp.get("/test")
def test():
    """
    Endpoint de teste para verificar se a API está respondendo
    """
    return jsonify({
        "status": "ok",
        "message": "Auth routes funcionando",
        "endpoints": {
            "POST /register": "Registrar novo usuário",
            "POST /login": "Fazer login",
            "GET /me": "Dados do usuário logado (requer token)",
            "POST /refresh": "Renovar token (requer token)",
            "POST /logout": "Fazer logout (requer token)",
            "GET /verify": "Verificar token (requer token)"
        }
    }), 200