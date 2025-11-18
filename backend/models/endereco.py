from config import db
from datetime import datetime
import re


# ============================================================
#                     MODELO ENDEREÇO
# ============================================================

class Endereco(db.Model):
    __tablename__ = 'enderecos'
    
    # Colunas principais
    id_endereco = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Localização
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)  # Sigla: SP, RJ, MG, etc
    rua = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    cep = db.Column(db.String(9), nullable=False, index=True)  # Formato: 12345-678
    
    # Complementos
    complemento = db.Column(db.String(100), nullable=True)
    referencia = db.Column(db.String(150), nullable=True)
    
    # Coordenadas para entrega
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    
    # Timestamp
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # ============================================================
    #                    RELACIONAMENTOS
    # ============================================================
    
    # usuarios = db.relationship('Usuario', backref='endereco', lazy=True)
    # Relacionamento já definido em Usuario
    
    # ============================================================
    #                    VALIDAÇÕES
    # ============================================================
    
    @staticmethod
    def validar_cep(cep: str) -> bool:
        """Valida formato de CEP brasileiro"""
        if not cep:
            return False
        
        # Remove formatação
        cep_limpo = re.sub(r'[^0-9]', '', cep)
        
        # Verifica se tem 8 dígitos
        return len(cep_limpo) == 8
    
    @staticmethod
    def formatar_cep(cep: str) -> str:
        """Formata CEP para o padrão 12345-678"""
        if not cep:
            return ""
        
        # Remove formatação existente
        cep_limpo = re.sub(r'[^0-9]', '', cep)
        
        # Formata se tiver 8 dígitos
        if len(cep_limpo) == 8:
            return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        
        return cep
    
    @staticmethod
    def validar_estado(estado: str) -> bool:
        """Valida sigla de estado brasileiro"""
        if not estado or len(estado) != 2:
            return False
        
        estados_validos = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        return estado.upper() in estados_validos
    
    @staticmethod
    def buscar_por_cep(cep: str):
        """Busca endereço por CEP usando API ViaCEP"""
        import requests
        
        try:
            # Remove formatação do CEP
            cep_limpo = re.sub(r'[^0-9]', '', cep)
            
            if len(cep_limpo) != 8:
                return None
            
            # Consulta API ViaCEP
            url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                dados = response.json()
                
                # Verifica se encontrou o CEP
                if 'erro' not in dados:
                    return {
                        'cep': Endereco.formatar_cep(dados.get('cep', '')),
                        'rua': dados.get('logradouro', ''),
                        'complemento': dados.get('complemento', ''),
                        'cidade': dados.get('localidade', ''),
                        'estado': dados.get('uf', ''),
                        'bairro': dados.get('bairro', '')
                    }
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar CEP: {e}")
            return None
    
    # ============================================================
    #                    MÉTODOS DE NEGÓCIO
    # ============================================================
    
    def endereco_completo(self) -> str:
        """Retorna o endereço formatado completo"""
        partes = [
            self.rua,
            self.numero,
            self.complemento if self.complemento else None,
            self.cidade,
            self.estado,
            f"CEP: {self.cep}"
        ]
        
        # Remove partes vazias
        partes_validas = [p for p in partes if p]
        
        return ", ".join(partes_validas)
    
    def endereco_resumido(self) -> str:
        """Retorna versão resumida do endereço"""
        return f"{self.rua}, {self.numero} - {self.cidade}/{self.estado}"
    
    def definir_coordenadas(self, latitude: float, longitude: float):
        """Define as coordenadas do endereço"""
        self.latitude = latitude
        self.longitude = longitude
        db.session.commit()
    
    def tem_coordenadas(self) -> bool:
        """Verifica se o endereço possui coordenadas"""
        return self.latitude is not None and self.longitude is not None
    
    # ============================================================
    #                     SERIALIZAÇÃO
    # ============================================================
    
    def to_dict(self, include_coordinates=False):
        """Converte o modelo para dicionário"""
        data = {
            'id_endereco': self.id_endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'rua': self.rua,
            'numero': self.numero,
            'cep': self.cep,
            'complemento': self.complemento,
            'referencia': self.referencia,
            'endereco_completo': self.endereco_completo(),
            'endereco_resumido': self.endereco_resumido(),
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
        
        # Inclui coordenadas apenas se solicitado
        if include_coordinates:
            data['latitude'] = float(self.latitude) if self.latitude else None
            data['longitude'] = float(self.longitude) if self.longitude else None
            data['tem_coordenadas'] = self.tem_coordenadas()
        
        return data
    
    def to_dict_resumido(self):
        """Versão resumida do endereço (para listagens)"""
        return {
            'id_endereco': self.id_endereco,
            'endereco': self.endereco_resumido(),
            'cep': self.cep
        }
    
    def __repr__(self):
        return f'<Endereco {self.rua}, {self.numero} - {self.cidade}/{self.estado}>'