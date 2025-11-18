from config import db
from datetime import datetime


# ============================================================
#                     MODELO ENTREGA
# ============================================================

class Entrega(db.Model):
    __tablename__ = 'entregas'

    # Colunas principais
    id_entrega = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    id_entregador = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='SET NULL'), nullable=True, index=True)
    id_endereco = db.Column(db.Integer, db.ForeignKey('enderecos.id_endereco', ondelete='RESTRICT'), nullable=False)

    # Status e controle
    status = db.Column(
        db.Enum(
            'Aguardando', 
            'Atribuído', 
            'A caminho', 
            'Próximo ao destino', 
            'Entregue', 
            'Não entregue', 
            'Cancelado',
            name='status_entrega_enum'
        ),
        default='Aguardando',
        nullable=False,
        index=True
    )

    # Datas e horários
    data_atribuicao = db.Column(db.DateTime, nullable=True)
    data_saida = db.Column(db.DateTime, nullable=True)
    data_entrega = db.Column(db.DateTime, nullable=True)

    # Informações da entrega
    distancia_km = db.Column(db.Numeric(8, 3), nullable=True)
    tempo_estimado_minutos = db.Column(db.SmallInteger, nullable=True)

    # Localização em tempo real
    latitude_atual = db.Column(db.Numeric(10, 8), nullable=True)
    longitude_atual = db.Column(db.Numeric(11, 8), nullable=True)

    # Observações e comprovantes
    observacoes = db.Column(db.Text, nullable=True)
    foto_comprovante_url = db.Column(db.String(255), nullable=True)
    assinatura_digital = db.Column(db.Text, nullable=True)

    # Avaliação do entregador
    avaliacao_entregador = db.Column(db.SmallInteger, nullable=True)
    comentario_entregador = db.Column(db.Text, nullable=True)

    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ============================================================
    #                    RELACIONAMENTOS
    # ============================================================

    pedido = db.relationship('Pedido', backref=db.backref('entrega', uselist=False, lazy=True))
    endereco = db.relationship('Endereco', backref='entregas', lazy=True)
    # Relacionamento com entregador já definido em Usuario

    # ============================================================
    #                    MÉTODOS DE NEGÓCIO
    # ============================================================

    def atribuir_entregador(self, id_entregador: int):
        """Atribui um entregador à entrega"""
        self.id_entregador = id_entregador
        self.status = 'Atribuído'
        self.data_atribuicao = datetime.utcnow()
        db.session.commit()

    def iniciar_entrega(self):
        """Marca o início da entrega (saída para entrega)"""
        if self.status not in ['Atribuído', 'Aguardando']:
            raise ValueError(f"Não é possível iniciar entrega com status '{self.status}'")
        
        self.status = 'A caminho'
        self.data_saida = datetime.utcnow()
        db.session.commit()

    def marcar_proximo_destino(self):
        """Marca que o entregador está próximo ao destino"""
        if self.status != 'A caminho':
            raise ValueError(f"Não é possível marcar como próximo com status '{self.status}'")
        
        self.status = 'Próximo ao destino'
        db.session.commit()

    def finalizar_entrega(self, sucesso: bool = True, observacao: str = None):
        """Finaliza a entrega (entregue ou não entregue)"""
        if self.status not in ['A caminho', 'Próximo ao destino']:
            raise ValueError(f"Não é possível finalizar entrega com status '{self.status}'")
        
        self.status = 'Entregue' if sucesso else 'Não entregue'
        self.data_entrega = datetime.utcnow()
        
        if observacao:
            self.observacoes = observacao
        
        db.session.commit()

    def cancelar_entrega(self, motivo: str = None):
        """Cancela a entrega"""
        if self.status in ['Entregue', 'Cancelado']:
            raise ValueError(f"Não é possível cancelar entrega com status '{self.status}'")
        
        self.status = 'Cancelado'
        
        if motivo:
            obs_atual = self.observacoes or ""
            self.observacoes = f"{obs_atual}\nMotivo do cancelamento: {motivo}".strip()
        
        db.session.commit()

    def atualizar_localizacao(self, latitude: float, longitude: float):
        """Atualiza a localização atual do entregador"""
        self.latitude_atual = latitude
        self.longitude_atual = longitude
        db.session.commit()

    def adicionar_avaliacao(self, nota: int, comentario: str = None):
        """Adiciona avaliação do entregador"""
        if nota < 1 or nota > 5:
            raise ValueError("Avaliação deve estar entre 1 e 5")
        
        if self.status != 'Entregue':
            raise ValueError("Só é possível avaliar entregas concluídas")
        
        self.avaliacao_entregador = nota
        self.comentario_entregador = comentario
        db.session.commit()

    # ============================================================
    #                    PROPRIEDADES CALCULADAS
    # ============================================================

    @property
    def tempo_decorrido(self):
        """Calcula o tempo decorrido desde a atribuição"""
        if not self.data_atribuicao:
            return None
        
        fim = self.data_entrega or datetime.utcnow()
        delta = fim - self.data_atribuicao
        return delta.total_seconds() / 60  # Retorna em minutos

    @property
    def esta_em_andamento(self) -> bool:
        """Verifica se a entrega está em andamento"""
        return self.status in ['Atribuído', 'A caminho', 'Próximo ao destino']

    @property
    def foi_concluida(self) -> bool:
        """Verifica se a entrega foi concluída"""
        return self.status in ['Entregue', 'Não entregue', 'Cancelado']

    # ============================================================
    #                     SERIALIZAÇÃO
    # ============================================================

    def to_dict(self, include_pedido=False, include_entregador=False):
        """Converte o modelo para dicionário"""
        data = {
            'id_entrega': self.id_entrega,
            'id_pedido': self.id_pedido,
            'id_entregador': self.id_entregador,
            'id_endereco': self.id_endereco,
            'status': self.status,
            'data_atribuicao': self.data_atribuicao.isoformat() if self.data_atribuicao else None,
            'data_saida': self.data_saida.isoformat() if self.data_saida else None,
            'data_entrega': self.data_entrega.isoformat() if self.data_entrega else None,
            'distancia_km': float(self.distancia_km) if self.distancia_km else None,
            'tempo_estimado_minutos': self.tempo_estimado_minutos,
            'tempo_decorrido_minutos': self.tempo_decorrido,
            'latitude_atual': float(self.latitude_atual) if self.latitude_atual else None,
            'longitude_atual': float(self.longitude_atual) if self.longitude_atual else None,
            'observacoes': self.observacoes,
            'foto_comprovante_url': self.foto_comprovante_url,
            'avaliacao_entregador': self.avaliacao_entregador,
            'comentario_entregador': self.comentario_entregador,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'esta_em_andamento': self.esta_em_andamento,
            'foi_concluida': self.foi_concluida
        }

        # Inclui dados do pedido se solicitado
        if include_pedido and self.pedido:
            try:
                data['pedido'] = self.pedido.to_dict()
            except Exception:
                data['pedido'] = None

        # Inclui dados do entregador se solicitado
        if include_entregador and self.id_entregador:
            try:
                from models.usuario import Usuario
                entregador = Usuario.query.get(self.id_entregador)
                if entregador:
                    data['entregador'] = entregador.to_dict_resumido()
            except Exception:
                data['entregador'] = None

        # Inclui endereço
        if self.endereco:
            try:
                data['endereco'] = self.endereco.to_dict()
            except Exception:
                data['endereco'] = None

        return data

    def to_dict_resumido(self):
        """Versão resumida da entrega (para listagens)"""
        return {
            'id_entrega': self.id_entrega,
            'id_pedido': self.id_pedido,
            'status': self.status,
            'data_atribuicao': self.data_atribuicao.isoformat() if self.data_atribuicao else None,
            'tempo_estimado_minutos': self.tempo_estimado_minutos,
            'esta_em_andamento': self.esta_em_andamento
        }

    def __repr__(self):
        return f'<Entrega {self.id_entrega} - Pedido {self.id_pedido} - {self.status}>'