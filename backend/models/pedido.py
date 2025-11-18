from config import db
from datetime import datetime
from decimal import Decimal


# ============================================================
#                     MODELO PEDIDO
# ============================================================

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    # Colunas principais
    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False, index=True)
    numero_pedido = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Datas
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Valores financeiros
    subtotal = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    desconto = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    taxa_entrega = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    
    # Status e tipo
    status = db.Column(
        db.Enum(
            'Aguardando pagamento', 
            'Pago', 
            'Em preparo', 
            'Pronto',
            'Saiu para entrega', 
            'Entregue', 
            'Cancelado', 
            'Reembolsado',
            name='status_pedido_enum'
        ),
        default='Aguardando pagamento',
        nullable=False,
        index=True
    )
    
    tipo_entrega = db.Column(
        db.Enum('delivery', 'retirada', name='tipo_entrega_enum'),
        default='delivery',
        nullable=False
    )
    
    forma_pagamento = db.Column(
        db.Enum(
            'cartao_credito', 
            'cartao_debito', 
            'pix', 
            'dinheiro', 
            'mercadopago',
            name='forma_pagamento_enum'
        ),
        nullable=True
    )
    
    # Informações adicionais
    observacoes = db.Column(db.Text, nullable=True)
    codigo_rastreio = db.Column(db.String(50), nullable=True)
    tempo_preparo_estimado = db.Column(db.SmallInteger, nullable=True)
    tempo_entrega_estimado = db.Column(db.SmallInteger, nullable=True)
    
    # Avaliação
    avaliacao = db.Column(db.SmallInteger, nullable=True)
    comentario_avaliacao = db.Column(db.Text, nullable=True)
    data_avaliacao = db.Column(db.DateTime, nullable=True)
    
    # Dados técnicos
    ip_cliente = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    # ============================================================
    #                    RELACIONAMENTOS
    # ============================================================
    
    itens = db.relationship(
        'ItemPedido', 
        backref='pedido', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        order_by='ItemPedido.id_item'
    )
    
    # Relacionamento com entrega (one-to-one)
    # entrega = db.relationship('Entrega', backref='pedido', uselist=False, lazy=True)
    
    # ============================================================
    #                    GERADOR DE NÚMERO DE PEDIDO
    # ============================================================
    
    @staticmethod
    def gerar_numero_pedido():
        """Gera um número único de pedido no formato LCC-2025-000001"""
        ano_atual = datetime.now().year
        
        # Busca o último pedido do ano
        ultimo_pedido = Pedido.query.filter(
            Pedido.numero_pedido.like(f'LCC-{ano_atual}-%')
        ).order_by(Pedido.id_pedido.desc()).first()
        
        if ultimo_pedido:
            # Extrai o número sequencial do último pedido
            partes = ultimo_pedido.numero_pedido.split('-')
            if len(partes) == 3:
                ultimo_numero = int(partes[2])
                proximo_numero = ultimo_numero + 1
            else:
                proximo_numero = 1
        else:
            proximo_numero = 1
        
        # Formata com zeros à esquerda (6 dígitos)
        return f"LCC-{ano_atual}-{proximo_numero:06d}"
    
    # ============================================================
    #                    PROPRIEDADES CALCULADAS
    # ============================================================
    
    @property
    def pode_ser_cancelado(self) -> bool:
        """Verifica se o pedido pode ser cancelado"""
        return self.status in ['Aguardando pagamento', 'Pago', 'Em preparo']
    
    @property
    def pode_ser_avaliado(self) -> bool:
        """Verifica se o pedido pode ser avaliado"""
        return self.status == 'Entregue' and self.avaliacao is None
    
    @property
    def esta_finalizado(self) -> bool:
        """Verifica se o pedido foi finalizado"""
        return self.status in ['Entregue', 'Cancelado', 'Reembolsado']
    
    @property
    def quantidade_itens(self) -> int:
        """Retorna a quantidade total de itens no pedido"""
        return sum(item.quantidade for item in self.itens)
    
    # ============================================================
    #                    CÁLCULOS FINANCEIROS
    # ============================================================
    
    def calcular_subtotal(self) -> Decimal:
        """Calcula o subtotal dos itens"""
        return sum(item.subtotal for item in self.itens)
    
    def calcular_total(self) -> Decimal:
        """Calcula o valor total do pedido"""
        subtotal = self.calcular_subtotal()
        total = subtotal + Decimal(self.taxa_entrega) - Decimal(self.desconto)
        return max(Decimal('0.00'), total)  # Garante que não seja negativo
    
    def recalcular_valores(self):
        """Recalcula todos os valores do pedido"""
        self.subtotal = self.calcular_subtotal()
        self.valor_total = self.calcular_total()
        db.session.commit()
    
    def aplicar_desconto(self, valor_desconto: Decimal):
        """Aplica um desconto ao pedido"""
        if valor_desconto < 0:
            raise ValueError("Desconto não pode ser negativo")
        
        if valor_desconto > self.subtotal:
            raise ValueError("Desconto não pode ser maior que o subtotal")
        
        self.desconto = valor_desconto
        self.recalcular_valores()
    
    def definir_taxa_entrega(self, taxa: Decimal):
        """Define a taxa de entrega"""
        if taxa < 0:
            raise ValueError("Taxa de entrega não pode ser negativa")
        
        self.taxa_entrega = taxa
        self.recalcular_valores()
    
    # ============================================================
    #                    MÉTODOS DE NEGÓCIO
    # ============================================================
    
    def adicionar_item(self, produto, quantidade: int, preco_unitario: Decimal = None, observacoes: str = None):
        """Adiciona um item ao pedido"""
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        
        # Verifica se o produto existe e está disponível
        if not produto.verificar_estoque(quantidade):
            raise ValueError(f"Estoque insuficiente para {produto.nome}")
        
        # Usa o preço atual do produto se não for fornecido
        if preco_unitario is None:
            preco_unitario = produto.preco_final
        
        # Verifica se já existe item deste produto no pedido
        item_existente = self.itens.filter_by(id_produto=produto.id_produto).first()
        
        if item_existente:
            # Atualiza quantidade do item existente
            item_existente.quantidade += quantidade
            item_existente.calcular_subtotal()
        else:
            # Cria novo item
            item = ItemPedido(
                id_pedido=self.id_pedido,
                id_produto=produto.id_produto,
                nome_produto=produto.nome,
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                observacoes=observacoes
            )
            item.calcular_subtotal()
            db.session.add(item)
        
        # Recalcula valores do pedido
        self.recalcular_valores()
    
    def remover_item(self, id_item: int):
        """Remove um item do pedido"""
        item = ItemPedido.query.filter_by(
            id_item=id_item, 
            id_pedido=self.id_pedido
        ).first()
        
        if not item:
            raise ValueError("Item não encontrado no pedido")
        
        db.session.delete(item)
        self.recalcular_valores()
    
    def atualizar_status(self, novo_status: str, observacao: str = None):
        """Atualiza o status do pedido"""
        status_validos = [
            'Aguardando pagamento', 'Pago', 'Em preparo', 'Pronto',
            'Saiu para entrega', 'Entregue', 'Cancelado', 'Reembolsado'
        ]
        
        if novo_status not in status_validos:
            raise ValueError(f"Status '{novo_status}' inválido")
        
        self.status = novo_status
        
        if observacao:
            obs_atual = self.observacoes or ""
            self.observacoes = f"{obs_atual}\n{novo_status}: {observacao}".strip()
        
        db.session.commit()
    
    def confirmar_pagamento(self, forma_pagamento: str):
        """Confirma o pagamento do pedido"""
        if self.status != 'Aguardando pagamento':
            raise ValueError(f"Pedido com status '{self.status}' não pode ter pagamento confirmado")
        
        self.forma_pagamento = forma_pagamento
        self.atualizar_status('Pago', 'Pagamento confirmado')
    
    def cancelar(self, motivo: str = None):
        """Cancela o pedido"""
        if not self.pode_ser_cancelado:
            raise ValueError(f"Pedido com status '{self.status}' não pode ser cancelado")
        
        # Devolve estoque dos produtos
        for item in self.itens:
            item.produto.devolver_estoque(item.quantidade)
        
        self.atualizar_status('Cancelado', motivo or 'Pedido cancelado')
    
    def adicionar_avaliacao(self, nota: int, comentario: str = None):
        """Adiciona avaliação ao pedido"""
        if not self.pode_ser_avaliado:
            raise ValueError("Este pedido não pode ser avaliado")
        
        if nota < 1 or nota > 5:
            raise ValueError("Avaliação deve estar entre 1 e 5")
        
        self.avaliacao = nota
        self.comentario_avaliacao = comentario
        self.data_avaliacao = datetime.utcnow()
        db.session.commit()
    
    # ============================================================
    #                     SERIALIZAÇÃO
    # ============================================================
    
    def to_dict(self, include_itens=True, include_usuario=False):
        """Converte o modelo para dicionário"""
        data = {
            'id_pedido': self.id_pedido,
            'numero_pedido': self.numero_pedido,
            'id_usuario': self.id_usuario,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'subtotal': float(self.subtotal),
            'desconto': float(self.desconto),
            'taxa_entrega': float(self.taxa_entrega),
            'valor_total': float(self.valor_total),
            'status': self.status,
            'tipo_entrega': self.tipo_entrega,
            'forma_pagamento': self.forma_pagamento,
            'observacoes': self.observacoes,
            'codigo_rastreio': self.codigo_rastreio,
            'tempo_preparo_estimado': self.tempo_preparo_estimado,
            'tempo_entrega_estimado': self.tempo_entrega_estimado,
            'avaliacao': self.avaliacao,
            'comentario_avaliacao': self.comentario_avaliacao,
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
            'quantidade_itens': self.quantidade_itens,
            'pode_ser_cancelado': self.pode_ser_cancelado,
            'pode_ser_avaliado': self.pode_ser_avaliado,
            'esta_finalizado': self.esta_finalizado
        }
        
        # Inclui itens se solicitado
        if include_itens:
            data['itens'] = [item.to_dict() for item in self.itens]
        
        # Inclui dados do usuário se solicitado
        if include_usuario and self.usuario:
            data['usuario'] = self.usuario.to_dict_resumido()
        
        return data
    
    def to_dict_resumido(self):
        """Versão resumida do pedido (para listagens)"""
        return {
            'id_pedido': self.id_pedido,
            'numero_pedido': self.numero_pedido,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido else None,
            'valor_total': float(self.valor_total),
            'status': self.status,
            'quantidade_itens': self.quantidade_itens
        }
    
    def __repr__(self):
        return f'<Pedido {self.numero_pedido} - {self.status}>'


# ============================================================
#                     MODELO ITEM PEDIDO
# ============================================================

class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    
    id_item = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido', ondelete='CASCADE'), nullable=False, index=True)
    id_produto = db.Column(db.Integer, db.ForeignKey('produtos.id_produto', ondelete='RESTRICT'), nullable=False, index=True)
    
    # Snapshot do produto no momento da compra
    nome_produto = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.SmallInteger, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Personalizações
    observacoes = db.Column(db.String(255), nullable=True)
    
    # ============================================================
    #                    PROPRIEDADES CALCULADAS
    # ============================================================
    
    def calcular_subtotal(self) -> Decimal:
        """Calcula o subtotal do item"""
        self.subtotal = Decimal(self.preco_unitario) * self.quantidade
        return self.subtotal
    
    # ============================================================
    #                    MÉTODOS DE NEGÓCIO
    # ============================================================
    
    def atualizar_quantidade(self, nova_quantidade: int):
        """Atualiza a quantidade do item"""
        if nova_quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        
        # Verifica estoque disponível
        if not self.produto.verificar_estoque(nova_quantidade):
            raise ValueError(f"Estoque insuficiente para {self.nome_produto}")
        
        self.quantidade = nova_quantidade
        self.calcular_subtotal()
        db.session.commit()
    
    # ============================================================
    #                     SERIALIZAÇÃO
    # ============================================================
    
    def to_dict(self, include_produto=False):
        """Converte o modelo para dicionário"""
        data = {
            'id_item': self.id_item,
            'id_pedido': self.id_pedido,
            'id_produto': self.id_produto,
            'nome_produto': self.nome_produto,
            'quantidade': self.quantidade,
            'preco_unitario': float(self.preco_unitario),
            'subtotal': float(self.subtotal),
            'observacoes': self.observacoes
        }
        
        # Inclui dados completos do produto se solicitado
        if include_produto and self.produto:
            data['produto'] = self.produto.to_dict_resumido()
        
        return data
    
    def __repr__(self):
        return f'<ItemPedido {self.nome_produto} x{self.quantidade}>'