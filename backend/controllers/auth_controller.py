"""
Controller de Autenticação - Leon's Cupcake
Gerencia operações de registro, login e gerenciamento de usuários
Versão com busca case-insensitive e logs detalhados
"""

from models.usuario import Usuario
from config import db
import re


def registrar_usuario(data: dict) -> Usuario:
    """
    Registra um novo usuário no sistema
    Email é automaticamente normalizado para lowercase
    
    Args:
        data (dict): Dicionário contendo:
            - nome (str): Nome completo do usuário
            - email (str): Email único do usuário
            - senha (str): Senha (será hasheada automaticamente)
            - cpf (str, opcional): CPF do usuário
            - telefone (str, opcional): Telefone do usuário
            - data_nascimento (date, opcional): Data de nascimento
    
    Returns:
        Usuario: Instância do usuário criado
    
    Raises:
        ValueError: Se dados obrigatórios estiverem faltando ou inválidos
    """
    try:
        print("\n" + "="*60)
        print("📝 CONTROLLER: REGISTRAR USUÁRIO")
        print("="*60)
        
        # ===== EXTRAÇÃO E LIMPEZA DE DADOS =====
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip().lower()  # 🔥 NORMALIZAR
        senha = data.get('senha', '').strip()
        cpf = data.get('cpf', '').strip() if data.get('cpf') else None
        telefone = data.get('telefone', '').strip() if data.get('telefone') else None
        data_nascimento = data.get('data_nascimento')
        
        print(f"📋 Dados recebidos:")
        print(f"   - Nome: {nome}")
        print(f"   - Email original: {data.get('email', '')}")
        print(f"   - Email normalizado: {email}")
        print(f"   - Senha: {'*' * len(senha)} ({len(senha)} caracteres)")
        if cpf:
            print(f"   - CPF: {cpf[:3]}***{cpf[-2:]}")
        if telefone:
            print(f"   - Telefone: {telefone[:2]}***{telefone[-2:]}")
        if data_nascimento:
            print(f"   - Data Nascimento: {data_nascimento}")
        
        # ===== VALIDAÇÕES BÁSICAS =====
        
        if not nome or not email or not senha:
            raise ValueError("nome, email e senha são obrigatórios")
        
        print("🔍 Validando campos...")
        
        # Validar nome
        if len(nome) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        if len(nome) > 100:
            raise ValueError("Nome muito longo (máximo 100 caracteres)")
        
        print("   ✅ Nome válido")
        
        # Validar email
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError("Email inválido")
        
        if len(email) > 100:
            raise ValueError("Email muito longo (máximo 100 caracteres)")
        
        # Validação mais robusta de email
        if not validar_email(email):
            raise ValueError("Formato de email inválido")
        
        print("   ✅ Email válido")
        
        # Validar senha
        if len(senha) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        
        if len(senha) > 100:
            raise ValueError("Senha muito longa (máximo 100 caracteres)")
        
        print("   ✅ Senha válida")
        
        # Validar CPF (se fornecido)
        if cpf:
            cpf_limpo = re.sub(r'\D', '', cpf)
            if len(cpf_limpo) != 11:
                raise ValueError("CPF deve ter 11 dígitos")
            
            # Validação básica de CPFs inválidos conhecidos
            cpfs_invalidos = [
                '00000000000', '11111111111', '22222222222', 
                '33333333333', '44444444444', '55555555555',
                '66666666666', '77777777777', '88888888888', 
                '99999999999'
            ]
            
            if cpf_limpo in cpfs_invalidos:
                raise ValueError("CPF inválido")
            
            cpf = cpf_limpo
            print("   ✅ CPF válido")
        
        # Validar telefone (se fornecido)
        if telefone:
            telefone_limpo = re.sub(r'\D', '', telefone)
            if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
                raise ValueError("Telefone deve ter 10 ou 11 dígitos")
            
            telefone = telefone_limpo
            print("   ✅ Telefone válido")
        
        # ===== VERIFICAR EMAIL DUPLICADO (CASE-INSENSITIVE) =====
        
        print(f"\n🔍 Verificando se email já existe...")
        print(f"   Buscando: {email}")
        
        # Busca case-insensitive no banco
        existe = Usuario.query.filter(
            db.func.lower(Usuario.email) == email
        ).first()
        
        if existe:
            print(f"❌ Email JÁ CADASTRADO!")
            print(f"   ID existente: {existe.id_usuario}")
            print(f"   Nome existente: {existe.nome}")
            print(f"   Email no banco: {existe.email}")
            print("="*60 + "\n")
            raise ValueError("E-mail já está cadastrado")
        
        print("   ✅ Email disponível")
        
        # Verificar CPF duplicado (se fornecido)
        if cpf:
            print(f"🔍 Verificando se CPF já existe...")
            cpf_existente = Usuario.query.filter_by(cpf=cpf).first()
            
            if cpf_existente:
                print(f"❌ CPF já cadastrado!")
                print(f"   ID existente: {cpf_existente.id_usuario}")
                print(f"   Nome: {cpf_existente.nome}")
                print("="*60 + "\n")
                raise ValueError("Este CPF já está cadastrado")
            
            print("   ✅ CPF disponível")
        
        # ===== CRIAR USUÁRIO =====
        
        print("\n🔨 Criando novo usuário...")
        
        user = Usuario(
            nome=nome,
            email=email,  # Email já normalizado
            tipo_usuario='cliente',  # Por padrão, novo usuário é cliente
            ativo=True
        )
        
        # Validar CPF obrigatório (banco exige NOT NULL)
        cpf = data.get('cpf')
        if not cpf:
            raise ValueError("CPF é obrigatório")
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")

        # Validar Telefone obrigatório (banco exige NOT NULL)
        telefone = data.get('telefone')
        if not telefone:
            raise ValueError("Telefone é obrigatório")
        telefone = re.sub(r'\D', '', telefone)
        if len(telefone) < 10 or len(telefone) > 11:
            raise ValueError("Telefone inválido")
        
        user.cpf = cpf
        user.telefone = telefone

        # Campos opcionais
        if data_nascimento:
            user.data_nascimento = data_nascimento
        
        # Definir senha (será hasheada automaticamente)
        print("🔐 Gerando hash da senha...")
        user.set_senha(senha)
        print("   ✅ Hash gerado")
        
        # Adicionar ao banco
        print("💾 Salvando no banco de dados...")
        db.session.add(user)
        db.session.commit()
        
        print("\n✅✅✅ USUÁRIO CRIADO COM SUCESSO ✅✅✅")
        print(f"   ID: {user.id_usuario}")
        print(f"   Nome: {user.nome}")
        print(f"   Email: {user.email}")
        print(f"   CPF: {user.cpf if user.cpf else 'Não informado'}")
        print(f"   Telefone: {user.telefone if user.telefone else 'Não informado'}")
        print(f"   Tipo: {user.tipo_usuario}")
        print(f"   Ativo: {user.ativo}")
        print("="*60 + "\n")
        
        return user
        
    except ValueError:
        # Re-raise ValueError para manter mensagens de validação
        db.session.rollback()
        print("❌ Erro de validação - Rollback realizado")
        print("="*60 + "\n")
        raise
    
    except Exception as e:
        # Rollback em qualquer outro erro
        db.session.rollback()
        print(f"\n❌❌❌ ERRO INESPERADO ❌❌❌")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        raise ValueError(f"Erro ao criar usuário: {str(e)}")


def autenticar(email: str, senha: str):
    """
    Autentica um usuário com email e senha
    Busca é case-insensitive para o email
    
    Args:
        email (str): Email do usuário
        senha (str): Senha em texto plano
    
    Returns:
        Usuario | None: Instância do usuário se autenticado, None caso contrário
    """
    try:
        print("\n" + "="*60)
        print("🔐 CONTROLLER: AUTENTICAR USUÁRIO")
        print("="*60)
        
        # 🔥 NORMALIZAR EMAIL NA BUSCA
        email_original = email
        email_normalizado = email.strip().lower()
        
        print(f"📧 Email recebido: '{email_original}'")
        print(f"📧 Email normalizado: '{email_normalizado}'")
        print(f"🔑 Senha fornecida: {'Sim' if senha else 'Não'}")
        
        if not email_normalizado or not senha:
            print("❌ Email ou senha vazios")
            print("="*60 + "\n")
            return None
        
        # Busca case-insensitive no banco
        print(f"\n🔍 Buscando usuário no banco...")
        print(f"   Query: SELECT * FROM usuarios WHERE LOWER(email) = '{email_normalizado}'")
        
        user = Usuario.query.filter(
            db.func.lower(Usuario.email) == email_normalizado
        ).first()
        
        if not user:
            print(f"\n❌ USUÁRIO NÃO ENCONTRADO: '{email_normalizado}'")
            
            # Debug: verifica se existe usuário similar
            print(f"\n🔍 Procurando emails similares...")
            username = email_normalizado.split('@')[0]
            similar = Usuario.query.filter(
                Usuario.email.ilike(f"%{username}%")
            ).all()
            
            if similar:
                print(f"⚠️  Encontrados {len(similar)} emails similares:")
                for s in similar:
                    print(f"    - {s.email} (ID: {s.id_usuario})")
            else:
                print(f"⚠️  Nenhum email similar encontrado")
            
            # Debug: lista todos os emails do banco
            todos = Usuario.query.with_entities(
                Usuario.id_usuario, 
                Usuario.email, 
                Usuario.nome
            ).all()
            
            print(f"\n📋 Todos os emails cadastrados ({len(todos)}):")
            for u in todos:
                print(f"    ID: {u.id_usuario} | Email: {u.email} | Nome: {u.nome}")
            
            print("="*60 + "\n")
            return None
        
        print(f"\n✅ USUÁRIO ENCONTRADO!")
        print(f"   ID: {user.id_usuario}")
        print(f"   Nome: {user.nome}")
        print(f"   Email no banco: {user.email}")
        print(f"   Tipo: {user.tipo_usuario}")
        print(f"   Ativo: {user.ativo}")
        
        # Verifica se usuário está ativo
        if not user.ativo:
            print(f"\n❌ USUÁRIO INATIVO")
            print("="*60 + "\n")
            return None
        
        print("   ✅ Usuário ativo")
        
        # Verifica senha
        print(f"\n🔐 Verificando senha...")
        senha_valida = user.check_senha(senha)
        
        if not senha_valida:
            print(f"❌ SENHA INCORRETA")
            print("="*60 + "\n")
            return None
        
        print(f"✅ Senha CORRETA")
        print(f"\n✅✅✅ AUTENTICAÇÃO BEM-SUCEDIDA ✅✅✅")
        print(f"   Usuário: {user.nome}")
        print(f"   Email: {user.email}")
        print(f"   Tipo: {user.tipo_usuario}")
        print("="*60 + "\n")
        
        return user
        
    except Exception as e:
        print(f"\n❌❌❌ ERRO NA AUTENTICAÇÃO ❌❌❌")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        import traceback
        print("\nTraceback:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        return None


def obter_usuario_por_id(user_id: int):
    """
    Busca um usuário pelo ID
    
    Args:
        user_id (int): ID do usuário
    
    Returns:
        Usuario | None: Instância do usuário se encontrado, None caso contrário
    """
    try:
        print("\n" + "="*60)
        print("👤 CONTROLLER: BUSCAR USUÁRIO POR ID")
        print("="*60)
        print(f"🆔 ID solicitado: {user_id}")
        
        if not user_id:
            print("❌ ID não fornecido")
            print("="*60 + "\n")
            return None
        
        print(f"🔍 Buscando no banco...")
        user = Usuario.query.get(user_id)
        
        if user:
            print(f"\n✅ USUÁRIO ENCONTRADO")
            print(f"   ID: {user.id_usuario}")
            print(f"   Nome: {user.nome}")
            print(f"   Email: {user.email}")
            print(f"   CPF: {user.cpf if user.cpf else 'Não informado'}")
            print(f"   Telefone: {user.telefone if user.telefone else 'Não informado'}")
            print(f"   Tipo: {user.tipo_usuario}")
            print(f"   Ativo: {user.ativo}")
        else:
            print(f"\n❌ USUÁRIO NÃO ENCONTRADO com ID: {user_id}")
            
            # Debug: lista todos os IDs disponíveis
            all_users = Usuario.query.with_entities(
                Usuario.id_usuario, 
                Usuario.nome, 
                Usuario.email
            ).all()
            
            print(f"\n📋 Usuários cadastrados no sistema ({len(all_users)}):")
            for u in all_users:
                print(f"    ID: {u.id_usuario} | Nome: {u.nome} | Email: {u.email}")
        
        print("="*60 + "\n")
        return user
        
    except Exception as e:
        print(f"\n❌ ERRO ao buscar usuário por ID")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return None


def obter_usuario_por_email(email: str):
    """
    Busca um usuário pelo email (case-insensitive)
    
    Args:
        email (str): Email do usuário
    
    Returns:
        Usuario | None: Instância do usuário se encontrado, None caso contrário
    """
    try:
        email_normalizado = email.strip().lower()
        
        if not email_normalizado:
            return None
        
        print(f"🔍 Buscando usuário por email: {email_normalizado}")
        
        user = Usuario.query.filter(
            db.func.lower(Usuario.email) == email_normalizado
        ).first()
        
        if user:
            print(f"✅ Usuário encontrado: {user.nome}")
        else:
            print(f"❌ Nenhum usuário encontrado com email: {email_normalizado}")
        
        return user
        
    except Exception as e:
        print(f"❌ Erro ao buscar usuário por email: {str(e)}")
        return None


def validar_email(email: str) -> bool:
    """
    Valida formato de email usando regex
    
    Args:
        email (str): Email a ser validado
    
    Returns:
        bool: True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def email_existe(email: str) -> bool:
    """
    Verifica se um email já está cadastrado (case-insensitive)
    
    Args:
        email (str): Email a ser verificado
    
    Returns:
        bool: True se existe, False caso contrário
    """
    try:
        email_normalizado = email.strip().lower()
        usuario = Usuario.query.filter(
            db.func.lower(Usuario.email) == email_normalizado
        ).first()
        return usuario is not None
    except Exception:
        return False


def cpf_existe(cpf: str) -> bool:
    """
    Verifica se um CPF já está cadastrado
    
    Args:
        cpf (str): CPF a ser verificado (apenas números)
    
    Returns:
        bool: True se existe, False caso contrário
    """
    try:
        cpf_limpo = re.sub(r'\D', '', cpf)
        usuario = Usuario.query.filter_by(cpf=cpf_limpo).first()
        return usuario is not None
    except Exception:
        return False


def listar_usuarios_ativos():
    """
    Lista todos os usuários ativos do sistema
    
    Returns:
        list[Usuario]: Lista de usuários ativos
    """
    try:
        usuarios = Usuario.query.filter_by(ativo=True).all()
        print(f"📋 Listados {len(usuarios)} usuários ativos")
        return usuarios
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {str(e)}")
        return []


def contar_usuarios():
    """
    Conta o total de usuários cadastrados
    
    Returns:
        int: Total de usuários
    """
    try:
        total = Usuario.query.count()
        return total
    except Exception:
        return 0


def contar_usuarios_por_tipo():
    """
    Conta quantidade de usuários por tipo
    
    Returns:
        dict: Dicionário com contagem por tipo
    """
    try:
        from sqlalchemy import func
        
        resultado = db.session.query(
            Usuario.tipo_usuario,
            func.count(Usuario.id_usuario)
        ).group_by(Usuario.tipo_usuario).all()
        
        contagem = {tipo: count for tipo, count in resultado}
        return contagem
        
    except Exception as e:
        print(f"❌ Erro ao contar usuários: {str(e)}")
        return {}


def atualizar_ultimo_acesso(user_id: int) -> bool:
    """
    Atualiza o timestamp de último acesso do usuário
    
    Args:
        user_id (int): ID do usuário
    
    Returns:
        bool: True se atualizado com sucesso, False caso contrário
    """
    try:
        from datetime import datetime
        
        user = Usuario.query.get(user_id)
        if user and hasattr(user, 'ultimo_acesso'):
            user.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao atualizar último acesso: {str(e)}")
        db.session.rollback()
        return False


def debug_listar_todos_usuarios():
    """
    Função de debug para listar todos os usuários cadastrados
    Útil para troubleshooting
    
    Returns:
        list[dict]: Lista com informações básicas de todos os usuários
    """
    try:
        print("\n" + "="*60)
        print("🔍 DEBUG: LISTAR TODOS OS USUÁRIOS")
        print("="*60)
        
        usuarios = Usuario.query.all()
        
        print(f"\n📋 Total de usuários: {len(usuarios)}\n")
        
        resultado = []
        for u in usuarios:
            info = {
                'id': u.id_usuario,
                'nome': u.nome,
                'email': u.email,
                'cpf': u.cpf if u.cpf else 'N/A',
                'tipo': u.tipo_usuario,
                'ativo': u.ativo
            }
            resultado.append(info)
            
            print(f"ID: {u.id_usuario}")
            print(f"   Nome: {u.nome}")
            print(f"   Email: {u.email}")
            print(f"   CPF: {u.cpf if u.cpf else 'N/A'}")
            print(f"   Tipo: {u.tipo_usuario}")
            print(f"   Ativo: {u.ativo}")
            print()
        
        print("="*60 + "\n")
        return resultado
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {str(e)}")
        return []