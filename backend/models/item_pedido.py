from config import db
from decimal import Decimal


# ============================================================
#                     MODELO ITEM PEDIDO
# ============================================================

class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    
    # Colunas principais
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
    #                    RELACIONAMENTOS
    # ============================================================
    
    produto = db.relationship('Produto', backref='itens_pedido', lazy='joined')
    # Relacionamento com pedido já definido em Pedido
    
    # ============================================================
    #                    VALIDAÇÕES
    # ============================================================
    
    def validar_quantidade(self, quantidade: int) -> bool:
        """Valida se a quantidade é válida"""
        if quantidade <= 0:
            return False
        
        # Verifica estoque do produto se existir
        if self.produto:
            return self.produto.verificar_estoque(quantidade)
        
        return True
    
    # ============================================================
    #                    PROPRIEDADES CALCULADAS
    # ============================================================
    
    @property
    def valor_unitario_com_descricao(self) -> str:
        """Retorna o preço unitário formatado"""
        return f"R$ {float(self.preco_unitario):.2f}"
    
    @property
    def subtotal_formatado(self) -> str:
        """Retorna o subtotal formatado"""
        return f"R$ {float(self.subtotal):.2f}"
    
    # ============================================================
    #                    MÉTODOS DE NEGÓCIO
    # ============================================================
    
    def calcular_subtotal(self) -> Decimal:
        """Calcula o subtotal do item"""
        self.subtotal = Decimal(str(self.preco_unitario)) * Decimal(str(self.quantidade))
        return self.subtotal
    
    def atualizar_quantidade(self, nova_quantidade: int):
        """Atualiza a quantidade do item"""
        if nova_quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        
        # Verifica estoque disponível
        if self.produto and not self.produto.verificar_estoque(nova_quantidade):
            raise ValueError(
                f"Estoque insuficiente para {self.nome_produto}. "
                f"Disponível: {self.produto.quantidade_estoque}"
            )
        
        self.quantidade = nova_quantidade
        self.calcular_subtotal()
        db.session.commit()
    
    def atualizar_preco(self, novo_preco: Decimal):
        """Atualiza o preço unitário (útil para promoções)"""
        if novo_preco <= 0:
            raise ValueError("Preço deve ser positivo")
        
        self.preco_unitario = novo_preco
        self.calcular_subtotal()
        db.session.commit()
    
    def adicionar_observacao(self, observacao: str):
        """Adiciona ou atualiza observação do item"""
        if len(observacao) > 255:
            raise ValueError("Observação muito longa (máximo 255 caracteres)")
        
        self.observacoes = observacao
        db.session.commit()
    
    # ============================================================
    #                     SERIALIZAÇÃO
    # ============================================================
    
    def to_dict(self, include_produto=True):
        """Converte o modelo para dicionário"""
        data = {
            'id_item': self.id_item,
            'id_pedido': self.id_pedido,
            'id_produto': self.id_produto,
            'nome_produto': self.nome_produto,
            'quantidade': self.quantidade,
            'preco_unitario': float(self.preco_unitario),
            'subtotal': float(self.subtotal),
            'observacoes': self.observacoes,
            'valor_unitario_formatado': self.valor_unitario_com_descricao,
            'subtotal_formatado': self.subtotal_formatado
        }
        
        # Inclui dados do produto se solicitado
        if include_produto and self.produto:
            try:
                data['produto'] = {
                    'id_produto': self.produto.id_produto,
                    'nome': self.produto.nome,
                    'slug': self.produto.slug,
                    'descricao': self.produto.descricao,
                    'descricao_curta': self.produto.descricao_curta,
                    'imagem_principal_url': self.produto.imagem_principal_url,
                    'preco_atual': self.produto.preco_final,
                    'disponivel': self.produto.disponivel,
                    'estoque': self.produto.quantidade_estoque
                }
            except Exception as e:
                # Se houver erro ao carregar produto, retorna apenas ID
                data['produto'] = {
                    'id_produto': self.id_produto,
                    'nome': self.nome_produto,
                    'erro': str(e)
                }
        
        return data
    
    def to_dict_resumido(self):
        """Versão resumida do item (para listagens rápidas)"""
        return {
            'id_item': self.id_item,
            'nome_produto': self.nome_produto,
            'quantidade': self.quantidade,
            'preco_unitario': float(self.preco_unitario),
            'subtotal': float(self.subtotal)
        }
    
    def __repr__(self):
        return f'<ItemPedido {self.nome_produto} x{self.quantidade} - R$ {float(self.subtotal):.2f}>'