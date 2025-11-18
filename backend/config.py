import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta, datetime

load_dotenv()

# ==================== ENVIRONMENT VARIABLES ====================
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "leons_cupcake")

def get_database_uri():
    """Gera a URI de conexão com o banco de dados MySQL"""
    if DB_PASS:
        return f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    else:
        return f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# ==================== EXTENSIONS ====================
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # ==================== CORS CONFIGURATION ====================
    CORS(app, 
         resources={r"/api/*": {
             "origins": [
                 "http://localhost:8100",      # Ionic Dev Server
                 "http://localhost:4200",      # Angular Dev Server
                 "http://127.0.0.1:8100",
                 "http://127.0.0.1:4200",
                 "capacitor://localhost",      # Capacitor iOS
                 "http://localhost"            # Capacitor Android
             ],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600  # Cache preflight por 1 hora
         }})
    
    # ==================== DATABASE CONFIGURATION ====================
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,        # Verifica conexões antes de usar
        "pool_recycle": 300,           # Recicla conexões a cada 5 minutos
        "pool_size": 10,               # Máximo de conexões no pool
        "max_overflow": 20,            # Conexões extras permitidas
        "echo": False                  # Não mostrar SQL queries (mudar para True para debug)
    }
    
    # ==================== JWT CONFIGURATION ====================
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "chave_super_secreta_para_jwt_leonscupcake")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_ERROR_MESSAGE_KEY"] = "erro"
    app.config["JWT_CSRF_CHECK_FORM"] = False
    app.config["JWT_CSRF_IN_COOKIES"] = False
    
    # ==================== FLASK CONFIGURATION ====================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "segredo_flask_leonscupcake")
    app.config["JSON_AS_ASCII"] = False  # Permite caracteres UTF-8 no JSON
    app.config["JSON_SORT_KEYS"] = False  # Mantém ordem das chaves JSON
    app.config["PROPAGATE_EXCEPTIONS"] = True  # Propaga exceções para logs
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Limite de 16MB para uploads
    
    # ==================== INITIALIZE EXTENSIONS ====================
    db.init_app(app)
    jwt.init_app(app)
    
    # ==================== JWT ERROR HANDLERS ====================
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"\n⚠️  JWT EXPIRADO")
        print(f"Header: {jwt_header}")
        print(f"Payload: {jwt_payload}")
        print(f"Expirou em: {datetime.fromtimestamp(jwt_payload['exp'])}\n")
        return jsonify({
            "erro": "Token expirado",
            "mensagem": "Por favor, faça login novamente",
            "codigo": "TOKEN_EXPIRED"
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"\n❌ JWT INVÁLIDO")
        print(f"Erro: {error}")
        print(f"Tipo: {type(error).__name__}\n")
        return jsonify({
            "erro": "Token inválido",
            "mensagem": "Autenticação falhou",
            "codigo": "TOKEN_INVALID",
            "detalhes": str(error)
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"\n🚫 JWT AUSENTE")
        print(f"Erro: {error}\n")
        return jsonify({
            "erro": "Token não fornecido",
            "mensagem": "Autenticação necessária",
            "codigo": "TOKEN_MISSING"
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        print(f"\n🔒 JWT REVOGADO")
        print(f"Header: {jwt_header}")
        print(f"Payload: {jwt_payload}\n")
        return jsonify({
            "erro": "Token revogado",
            "mensagem": "Token foi invalidado",
            "codigo": "TOKEN_REVOKED"
        }), 401
    
    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(jwt_header, jwt_payload):
        print(f"\n⛔ VERIFICAÇÃO DE TOKEN FALHOU")
        print(f"Header: {jwt_header}")
        print(f"Payload: {jwt_payload}\n")
        return jsonify({
            "erro": "Falha na verificação do token",
            "mensagem": "Token não pode ser verificado",
            "codigo": "TOKEN_VERIFICATION_FAILED"
        }), 401
    
    # ==================== GLOBAL ERROR HANDLERS ====================
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "erro": "Endpoint não encontrado",
            "mensagem": f"A rota {request.path} não existe",
            "codigo": "NOT_FOUND"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "erro": "Método não permitido",
            "mensagem": f"O método {request.method} não é permitido para {request.path}",
            "codigo": "METHOD_NOT_ALLOWED"
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        print(f"\n💥 ERRO INTERNO DO SERVIDOR")
        print(f"Erro: {error}\n")
        db.session.rollback()  # Rollback em caso de erro de banco
        return jsonify({
            "erro": "Erro interno do servidor",
            "mensagem": "Algo deu errado. Por favor, tente novamente",
            "codigo": "INTERNAL_ERROR"
        }), 500
    
    # ==================== REQUEST/RESPONSE LOGGING ====================
    @app.before_request
    def log_request():
        """Log detalhado de todas as requisições para /api/*"""
        if request.path.startswith('/api/'):
            print(f"\n{'='*80}")
            print(f"📥 REQUISIÇÃO: {request.method} {request.path}")
            print(f"{'='*80}")
            
            # Log do Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header:
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
                    token_preview = f"{token[:20]}...{token[-20:]}" if len(token) > 40 else token
                    print(f"🔑 Authorization: Bearer {token_preview}")
                else:
                    print(f"🔑 Authorization: {auth_header[:50]}...")
            else:
                print(f"🔑 Authorization: ❌ Não fornecido")
            
            # Log de outros headers importantes
            print(f"🌐 Origin: {request.headers.get('Origin', 'N/A')}")
            print(f"📱 Content-Type: {request.headers.get('Content-Type', 'N/A')}")
            print(f"🖥️  User-Agent: {request.headers.get('User-Agent', 'N/A')[:60]}...")
            
            # Log do body para POST/PUT/PATCH
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    body = request.get_json(silent=True)
                    if body:
                        # Oculta campos sensíveis
                        safe_body = {
                            k: '***' if any(s in k.lower() for s in ['senha', 'password', 'token', 'secret']) 
                            else v 
                            for k, v in body.items()
                        }
                        print(f"📦 Body: {safe_body}")
                except Exception as e:
                    print(f"⚠️  Não foi possível parsear o body: {e}")
            
            print(f"{'='*80}\n")
    
    @app.after_request
    def log_response(response):
        """Log da resposta"""
        if request.path.startswith('/api/'):
            status_emoji = "✅" if response.status_code < 400 else "❌"
            print(f"\n{'='*80}")
            print(f"📤 RESPOSTA: {status_emoji} {response.status_code} {request.method} {request.path}")
            print(f"{'='*80}\n")
        
        # Adiciona headers de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # ==================== REGISTER BLUEPRINTS ====================
    with app.app_context():
        try:
            from routes.auth_routes import auth_bp
            from routes.usuario_routes import usuario_bp
            from routes.produto_routes import produto_bp
            from routes.pedido_routes import pedido_bp
            from routes.entrega_routes import entrega_bp
            from routes.categoria_routes import categoria_bp
            
            app.register_blueprint(auth_bp, url_prefix="/api/auth")
            app.register_blueprint(usuario_bp, url_prefix="/api/usuarios")
            app.register_blueprint(produto_bp, url_prefix="/api/produtos")
            app.register_blueprint(pedido_bp, url_prefix="/api/pedidos")
            app.register_blueprint(entrega_bp, url_prefix="/api/entregas")
            app.register_blueprint(categoria_bp, url_prefix="/api/categorias")
            
            print("✅ Todos os blueprints registrados com sucesso!")
            
        except ImportError as e:
            print(f"⚠️  Erro ao importar blueprints: {e}")
            print("Alguns módulos podem não estar disponíveis ainda.")
        
        # ==================== UTILITY ROUTES ====================
        @app.route("/api/health", methods=["GET"])
        def health_check():
            """Verifica se a API está funcionando"""
            try:
                # Testa conexão com o banco
                db.session.execute(db.text("SELECT 1"))
                db_status = "conectado"
            except Exception as e:
                db_status = f"erro: {str(e)}"
            
            return jsonify({
                "status": "ok",
                "mensagem": "API Leon's Cupcake está funcionando! 🧁",
                "timestamp": datetime.utcnow().isoformat(),
                "banco_de_dados": db_status,
                "versao": "1.0.0"
            }), 200
        
        @app.route("/api/", methods=["GET"])
        def api_root():
            """Rota raiz da API"""
            return jsonify({
                "mensagem": "Bem-vindo à API Leon's Cupcake! 🧁",
                "versao": "1.0.0",
                "endpoints": {
                    "health": "/api/health",
                    "auth": "/api/auth",
                    "usuarios": "/api/usuarios",
                    "produtos": "/api/produtos",
                    "categorias": "/api/categorias",
                    "pedidos": "/api/pedidos",
                    "entregas": "/api/entregas"
                }
            }), 200
        
        # ==================== DEBUG ENDPOINTS (REMOVER EM PRODUÇÃO) ====================
        @app.route("/api/debug/token", methods=["GET"])
        @jwt_required()
        def debug_token():
            """Endpoint para testar se o token JWT está funcionando"""
            try:
                user_id = get_jwt_identity()
                claims = get_jwt()
                
                return jsonify({
                    "status": "ok",
                    "mensagem": "✅ Token válido e funcionando!",
                    "user_id": user_id,
                    "claims": claims
                }), 200
            except Exception as e:
                return jsonify({
                    "erro": str(e),
                    "tipo": type(e).__name__
                }), 500
        
        @app.route("/api/debug/db", methods=["GET"])
        def debug_db():
            """Endpoint para testar conexão com o banco"""
            try:
                result = db.session.execute(db.text("SELECT VERSION()"))
                version = result.scalar()
                
                return jsonify({
                    "status": "ok",
                    "mensagem": "✅ Banco de dados conectado!",
                    "versao_mysql": version,
                    "database": DB_NAME
                }), 200
            except Exception as e:
                return jsonify({
                    "erro": str(e),
                    "tipo": type(e).__name__,
                    "mensagem": "❌ Erro ao conectar no banco de dados"
                }), 500
    
    return app