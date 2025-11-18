"""
Script para gerar token JWT manualmente
Útil para debug quando há problemas de autenticação

USO:
    python reset_token.py                          # Gera token para vinicius@gmail.com
    python reset_token.py seu_email@example.com    # Gera token para email específico
"""
import sys
from config import create_app
from models.usuario import Usuario
from flask_jwt_extended import create_access_token
from datetime import timedelta


def gerar_token_usuario(email):
    """Gera um token JWT para um usuário específico"""
    app = create_app()
    
    with app.app_context():
        try:
            # Busca o usuário
            user = Usuario.query.filter_by(email=email).first()
            
            if not user:
                print(f"\n❌ Usuário '{email}' não encontrado!")
                print("\n📋 Usuários disponíveis no banco:")
                usuarios = Usuario.query.all()
                
                if not usuarios:
                    print("  ⚠️  Nenhum usuário encontrado no banco!")
                    print("  💡 Registre um usuário primeiro através da API")
                else:
                    for u in usuarios:
                        status = "✅ Ativo" if u.ativo else "❌ Inativo"
                        print(f"  - {u.email} | {u.tipo_usuario} | {status}")
                
                return None
            
            # Verifica se o usuário está ativo
            if not user.ativo:
                print(f"\n⚠️  ATENÇÃO: Usuário '{email}' está INATIVO!")
                print("   O token será gerado, mas pode ter problemas de acesso.")
            
            # Cria token com claims personalizados
            additional_claims = {
                "tipo_usuario": user.tipo_usuario,
                "email": user.email,
                "nome": user.nome,
                "ativo": user.ativo
            }
            
            token = create_access_token(
                identity=user.id_usuario,
                additional_claims=additional_claims,
                expires_delta=timedelta(hours=24)
            )
            
            # Exibe informações detalhadas
            print("\n" + "="*80)
            print("✅ TOKEN JWT GERADO COM SUCESSO!")
            print("="*80)
            print(f"\n👤 Usuário: {user.nome} {user.sobrenome or ''}")
            print(f"📧 Email: {user.email}")
            print(f"🔑 Tipo: {user.tipo_usuario.upper()}")
            print(f"🆔 ID: {user.id_usuario}")
            print(f"📱 Telefone: {user.telefone}")
            print(f"🟢 Status: {'Ativo' if user.ativo else 'Inativo'}")
            
            print(f"\n📋 TOKEN (válido por 24 horas):")
            print(f"\n{token}\n")
            
            print("="*80)
            print("\n📌 OPÇÃO 1 - USAR NO NAVEGADOR (localStorage):")
            print("─"*80)
            print("1. Abra o Console do navegador (F12 → Console)")
            print("2. Cole e execute este comando:")
            print(f"\n   localStorage.setItem('access_token', '{token}');\n")
            print("3. Recarregue a página (F5) ou navegue para o app")
            
            print("\n📌 OPÇÃO 2 - USAR NO POSTMAN/INSOMNIA:")
            print("─"*80)
            print("1. Adicione um header nas requisições:")
            print(f"   Authorization: Bearer {token[:50]}...")
            
            print("\n📌 OPÇÃO 3 - TESTAR NO TERMINAL:")
            print("─"*80)
            print("   curl -H 'Authorization: Bearer SEU_TOKEN' http://localhost:5000/api/debug/token")
            
            print("\n" + "="*80)
            print("✨ Token copiado para a área de transferência? Cole no seu app!")
            print("="*80 + "\n")
            
            return token
            
        except Exception as e:
            print(f"\n💥 ERRO ao gerar token:")
            print(f"   {type(e).__name__}: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return None


def listar_usuarios():
    """Lista todos os usuários cadastrados"""
    app = create_app()
    
    with app.app_context():
        try:
            usuarios = Usuario.query.all()
            
            if not usuarios:
                print("\n⚠️  Nenhum usuário encontrado no banco!")
                return
            
            print("\n" + "="*80)
            print(f"📋 USUÁRIOS CADASTRADOS ({len(usuarios)} total)")
            print("="*80)
            
            for u in usuarios:
                status = "✅" if u.ativo else "❌"
                tipo = u.tipo_usuario.upper()
                email_verificado = "✓" if u.email_verificado else "✗"
                
                print(f"\n{status} {u.nome} {u.sobrenome or ''}")
                print(f"   📧 {u.email} (verificado: {email_verificado})")
                print(f"   🔑 {tipo}")
                print(f"   🆔 ID: {u.id_usuario}")
                print(f"   📱 {u.telefone}")
                
                if u.ultimo_acesso:
                    print(f"   🕐 Último acesso: {u.ultimo_acesso}")
            
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"\n💥 ERRO ao listar usuários:")
            print(f"   {type(e).__name__}: {str(e)}\n")


def menu_interativo():
    """Menu interativo para facilitar o uso"""
    print("\n" + "="*80)
    print("🔧 GERADOR DE TOKEN JWT - Leon's Cupcake")
    print("="*80)
    print("\nEscolha uma opção:")
    print("  1. Gerar token para email específico")
    print("  2. Listar todos os usuários")
    print("  3. Gerar token para vinicius@gmail.com (padrão)")
    print("  0. Sair")
    print("="*80)
    
    escolha = input("\nDigite o número da opção: ").strip()
    
    if escolha == "1":
        email = input("\n📧 Digite o email do usuário: ").strip()
        if email:
            gerar_token_usuario(email)
        else:
            print("\n❌ Email inválido!")
    
    elif escolha == "2":
        listar_usuarios()
    
    elif escolha == "3":
        gerar_token_usuario("vinicius@gmail.com")
    
    elif escolha == "0":
        print("\n👋 Até logo!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Opção inválida!")


if __name__ == "__main__":
    # Verifica argumentos da linha de comando
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        # Comandos especiais
        if comando in ["-h", "--help", "help"]:
            print(__doc__)
            print("\nCOMANDOS:")
            print("  python reset_token.py                  - Menu interativo")
            print("  python reset_token.py email@example.com - Gera token para email")
            print("  python reset_token.py -l, --list       - Lista usuários")
            print("  python reset_token.py -h, --help       - Mostra esta ajuda\n")
        
        elif comando in ["-l", "--list", "list"]:
            listar_usuarios()
        
        else:
            # Trata como email
            email = sys.argv[1]
            gerar_token_usuario(email)
    
    else:
        # Menu interativo se não houver argumentos
        try:
            menu_interativo()
        except KeyboardInterrupt:
            print("\n\n👋 Operação cancelada pelo usuário.\n")
            sys.exit(0)