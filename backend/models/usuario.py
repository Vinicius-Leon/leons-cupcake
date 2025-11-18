from config import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re


# ============================================================
#                     MODELO USUÁRIO
# ============================================================

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    # Colunas principais
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_endereco = db.Column(db.Integer, db.ForeignKey('enderecos.id_endereco', ondelete='SET NULL'), nullable=True)
    
    # Dados pessoais
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    
    data_nascimento = db.Column(db.Date, nullable=True)
    sexo = db.Column(db.Enum('M', 'F', 'Outro', 'Prefiro não informar', name='sexo_enum'), nullable=True)
    
    # Tipo e permissões
    tipo_usuario = db.Column(
        db.Enum('cliente', 'admin', 'entregador', name='tipo_usuario_enum'),
        default='cliente',
        nullable=False,
        index=True
    )
    
    # Status e controle
    ativo = db.Column(db.Boolean, default=True, nullable=False, index=True)
    email_verificado = db.Column(db.Boolean, default=False, nullable=False)
    foto_perfil_url = db.Column(db.String(255), nullable=True)
    ultimo_acesso = db.Column(db.DateTime, nullable=True, index=True)
    tentativas_login = db.Column(db.SmallInteger, default=0, nullable=False)
    bloqueado_ate = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ============================================================
    #                    RELACIONAMENTOS
    # ============================================================
    
    endereco = db.relationship('Endereco', backref='usuarios', lazy=True, foreign_keys=[id_endereco])
    pedidos = db.relationship('Pedido', backref='usuario', lazy="select", cascade="all, delete-orphan")
    cartoes = db.relationship('Cartao', backref='usuario', lazy="select", cascade="all, delete-orphan")
    entregas = db.relationship('Entrega', foreign_keys='Entrega.id_entregador', backref='entregador', lazy="select")

    # ============================================================
    #                    VALIDAÇÕES
    # ============================================================

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF (apenas dígitos, 11 caracteres)"""
        if not cpf:
            return False
        
        # Remove formatação
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se não é uma sequência conhecida
        if cpf in ['00000000000', '11111111111', '22222222222', '33333333333',
                   '44444444444', '55555555555', '66666666666', '77777777777',
                   '88888888888', '99999999999']:
            return False
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        if digito1 >= 10:
            digito1 = 0
        
        if int(cpf[9]) != digito1:
            return False
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        if digito2 >= 10:
            digito2 = 0
        
        if int(cpf[10]) != digito2:
            return False
        
        return True

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida telefone brasileiro (com DDD)"""
        if not telefone:
            return False
        
        # Remove formatação
        telefone = re.sub(r'[^0-9]', '', telefone)
        
        # Verifica se tem 10 ou 11 dígitos (DDD + número)
        return len(telefone) in [10, 11]

    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """Retorna apenas os números do CPF"""
        if not cpf:
            return ""
        return re.sub(r'[^0-9]', '', cpf)

    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """Formata telefone para (XX)XXXXX-XXXX"""
        if not telefone:
            return ""
        
        # Remove formatação existente
        numeros = re.sub(r'[^0-9]', '', telefone)
        
        # Formata conforme tamanho
        if len(numeros) == 11:  # Celular com 9 dígitos
            return f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"
        elif len(numeros) == 10:  # Telefone fixo
            return f"({numeros[:2]}){numeros[2:6]}-{numeros[6:]}"
        
        return telefone

    # ============================================================
    #                    FUNÇÕES DE SENHA
    # ============================================================

    def set_senha(self, senha: str):
        """Define a senha do usuário com hash seguro"""
        if not senha:
            raise ValueError("Senha não pode ser vazia")
        
        if len(senha) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        
        # Gera hash com PBKDF2-SHA256 (padrão do Werkzeug)
        self.senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

    def check_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida está correta"""
        if not senha or not self.senha_hash:
            return False
        
        return check_password_hash(self.senha_hash, senha)

    # ============================================================
    #                    CONTROLE DE LOGIN
    # ============================================================

    def incrementar_tentativas_login(self):
        """Incrementa contador de tentativas de login falhadas"""
        self.tentativas_login += 1
        
        # Bloqueia após 5 tentativas
        if self.tentativas_login >= 5:
            self.bloqueado_ate = datetime.utcnow() + timedelta(minutes=30)
        
        db.session.commit()

    def resetar_tentativas_login(self):
        """Reseta contador de tentativas após login bem-sucedido"""
        self.tentativas_login = 0
        self.bloqueado_ate = None
        db.session.commit()

    def esta_bloqueado(self) -> bool:
        """Verifica se o usuário está temporariamente bloqueado"""
        if not self.bloqueado_ate:
            return False
        
        if datetime.utcnow() > self.bloqueado_ate:
            # Desbloqueio automático
            self.bloqueado_ate = None
            self.tentativas_login = 0
            db.session.commit()
            return False
        
        return True

    def atualizar_ultimo_acesso(self):
        """Atualiza timestamp do último acesso"""
        self.ultimo_acesso = datetime.utcnow()
        db.session.commit()

    # ============================================================
    #                    PERMISSÕES
    # ============================================================

    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador"""
        return self.tipo_usuario == 'admin'

    def is_entregador(self) -> bool:
        """Verifica se o usuário é entregador"""
        return self.tipo_usuario == 'entregador'

    def is_cliente(self) -> bool:
        """Verifica se o usuário é cliente"""
        return self.tipo_usuario == 'cliente'

    # ============================================================
    #                     SERIALIZAÇÃO
    # ============================================================

    def to_dict(self, include_sensitive=False):
        """Converte o modelo para dicionário"""
        data = {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'sobrenome': self.sobrenome,
            'email': self.email,
            'telefone': self.telefone,
            'tipo_usuario': self.tipo_usuario,
            'ativo': self.ativo,
            'email_verificado': self.email_verificado,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'sexo': self.sexo,
            'foto_perfil_url': self.foto_perfil_url,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

        # Inclui CPF apenas se solicitado (dados sensíveis)
        if include_sensitive:
            data['cpf'] = self.cpf
            data['tentativas_login'] = self.tentativas_login
            data['bloqueado_ate'] = self.bloqueado_ate.isoformat() if self.bloqueado_ate else None

        # Inclui endereço se existir
        if self.endereco:
            try:
                data['endereco'] = self.endereco.to_dict()
            except Exception:
                data['endereco'] = None

        return data

    def to_dict_resumido(self):
        """Versão resumida do usuário (para listagens)"""
        return {
            'id_usuario': self.id_usuario,
            'nome': f"{self.nome} {self.sobrenome or ''}".strip(),
            'email': self.email,
            'tipo_usuario': self.tipo_usuario,
            'ativo': self.ativo,
            'foto_perfil_url': self.foto_perfil_url
        }

    def __repr__(self):
        return f'<Usuario {self.email} ({self.tipo_usuario})>'


# ============================================================
#                     MODELO CARTÃO
# ============================================================

class Cartao(db.Model):
    __tablename__ = 'cartoes'

    id_cartao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False, index=True)

    nome_titular = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Enum('credito', 'debito', name='tipo_cartao_enum'), nullable=False)
    bandeira = db.Column(db.Enum(
        'Visa', 'Mastercard', 'Elo', 'American Express', 'Hipercard', 'Outro',
        name='bandeira_cartao_enum'
    ), nullable=False)

    numero_cartao_hash = db.Column(db.String(255), nullable=False)
    ultimos_digitos = db.Column(db.String(4), nullable=False)

    validade_mes = db.Column(db.SmallInteger, nullable=False)
    validade_ano = db.Column(db.SmallInteger, nullable=False)

    cvv_hash = db.Column(db.String(255), nullable=False)

    principal = db.Column(db.Boolean, default=False, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ============================================================
    #                    VALIDAÇÕES
    # ============================================================

    def esta_valido(self) -> bool:
        """Verifica se o cartão ainda está dentro da validade"""
        from datetime import date
        hoje = date.today()
        return (self.validade_ano > hoje.year or 
                (self.validade_ano == hoje.year and self.validade_mes >= hoje.month))

    @staticmethod
    def detectar_bandeira(numero: str) -> str:
        """Detecta a bandeira do cartão pelo número"""
        # Remove espaços e hífens
        numero = re.sub(r'[^0-9]', '', numero)
        
        if not numero:
            return 'Outro'
        
        # Visa: começa com 4
        if numero[0] == '4':
            return 'Visa'
        
        # Mastercard: começa com 51-55 ou 2221-2720
        if numero[:2] in ['51', '52', '53', '54', '55']:
            return 'Mastercard'
        if 2221 <= int(numero[:4]) <= 2720:
            return 'Mastercard'
        
        # Elo: vários BINs
        elo_bins = ['4011', '4312', '4389', '4514', '4573', '5067', '5090', '6277', '6362', '6363']
        if numero[:4] in elo_bins:
            return 'Elo'
        
        # American Express: começa com 34 ou 37
        if numero[:2] in ['34', '37']:
            return 'American Express'
        
        # Hipercard: começa com 6062
        if numero[:4] == '6062':
            return 'Hipercard'
        
        return 'Outro'

    # ============================================================
    #                     SERIALIZAÇÃO
    # ============================================================

    def to_dict(self, include_sensitive=False):
        """Converte o modelo para dicionário"""
        data = {
            'id_cartao': self.id_cartao,
            'nome_titular': self.nome_titular,
            'tipo': self.tipo,
            'bandeira': self.bandeira,
            'ultimos_digitos': self.ultimos_digitos,
            'validade_mes': self.validade_mes,
            'validade_ano': self.validade_ano,
            'principal': self.principal,
            'ativo': self.ativo,
            'valido': self.esta_valido()
        }
        
        # Nunca inclui hashes nos dicts (segurança)
        if include_sensitive:
            data['criado_em'] = self.criado_em.isoformat() if self.criado_em else None
        
        return data

    def __repr__(self):
        return f'<Cartao {self.bandeira} {self.tipo} ****{self.ultimos_digitos}>'


# Importa timedelta para o método de bloqueio
from datetime import timedelta