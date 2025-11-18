SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- Remover banco se existir
DROP DATABASE IF EXISTS leons_cupcake;

-- Criar banco com configurações otimizadas
CREATE DATABASE leons_cupcake
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE leons_cupcake;

-- ==========================================
-- TABELA: enderecos
-- ==========================================
CREATE TABLE enderecos (
  id_endereco INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  cidade VARCHAR(100) NOT NULL,
  estado CHAR(2) NOT NULL COMMENT 'Sigla do estado (SP, RJ, MG, etc)',
  rua VARCHAR(150) NOT NULL,
  numero VARCHAR(10) NOT NULL,
  cep CHAR(9) NOT NULL COMMENT 'Formato: 12345-678',
  complemento VARCHAR(100) NULL,
  referencia VARCHAR(150) NULL,
  latitude DECIMAL(10,8) NULL COMMENT 'Coordenadas para entrega',
  longitude DECIMAL(11,8) NULL COMMENT 'Coordenadas para entrega',
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_cep (cep),
  INDEX idx_cidade_estado (cidade, estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Endereços de entrega dos clientes';

-- ==========================================
-- TABELA: usuarios
-- ==========================================
CREATE TABLE usuarios (
  id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_endereco INT UNSIGNED NULL,
  nome VARCHAR(100) NOT NULL,
  sobrenome VARCHAR(100) NULL,
  cpf CHAR(11) UNIQUE NOT NULL COMMENT 'Apenas números, sem formatação',
  telefone VARCHAR(15) NOT NULL COMMENT 'Com DDD, formato: (11)98765-4321',
  email VARCHAR(100) UNIQUE NOT NULL,
  senha_hash VARCHAR(255) NOT NULL,
  data_nascimento DATE NULL,
  sexo ENUM('M', 'F', 'Outro', 'Prefiro não informar') NULL,
  tipo_usuario ENUM('cliente', 'admin', 'entregador') NOT NULL DEFAULT 'cliente',
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  email_verificado BOOLEAN NOT NULL DEFAULT FALSE,
  foto_perfil_url VARCHAR(255) NULL,
  ultimo_acesso DATETIME NULL,
  tentativas_login TINYINT UNSIGNED NOT NULL DEFAULT 0,
  bloqueado_ate DATETIME NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_usuarios_endereco 
    FOREIGN KEY (id_endereco) REFERENCES enderecos(id_endereco)
    ON DELETE SET NULL,
  INDEX idx_email (email),
  INDEX idx_cpf (cpf),
  INDEX idx_tipo_ativo (tipo_usuario, ativo),
  INDEX idx_ultimo_acesso (ultimo_acesso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Usuários do sistema (clientes, admin, entregadores)';

-- ==========================================
-- TABELA: cartoes
-- ==========================================
CREATE TABLE cartoes (
  id_cartao INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT UNSIGNED NOT NULL,
  nome_titular VARCHAR(100) NOT NULL,
  tipo ENUM('credito','debito') NOT NULL,
  bandeira ENUM('Visa', 'Mastercard', 'Elo', 'American Express', 'Hipercard', 'Outro') NOT NULL,
  numero_cartao_hash VARCHAR(255) NOT NULL COMMENT 'Hash do número completo',
  ultimos_digitos CHAR(4) NOT NULL COMMENT 'Últimos 4 dígitos para exibição',
  validade_mes TINYINT UNSIGNED NOT NULL COMMENT 'Mês 1-12',
  validade_ano SMALLINT UNSIGNED NOT NULL COMMENT 'Ano com 4 dígitos',
  cvv_hash VARCHAR(255) NOT NULL COMMENT 'Hash do CVV',
  principal BOOLEAN NOT NULL DEFAULT FALSE,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_cartoes_usuario 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE,
  INDEX idx_usuario_ativo (id_usuario, ativo),
  CHECK (validade_mes BETWEEN 1 AND 12),
  CHECK (validade_ano >= 2025)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cartões de pagamento dos clientes';

-- ==========================================
-- TABELA: categorias
-- ==========================================
CREATE TABLE categorias (
  id_categoria SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL UNIQUE,
  slug VARCHAR(100) NOT NULL UNIQUE COMMENT 'URL-friendly: cupcakes-classicos',
  descricao TEXT NULL,
  imagem_url VARCHAR(255) NULL,
  ordem_exibicao TINYINT UNSIGNED NOT NULL DEFAULT 0,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_ativo_ordem (ativo, ordem_exibicao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Categorias de produtos';

-- ==========================================
-- TABELA: produtos
-- ==========================================
CREATE TABLE produtos (
  id_produto INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_categoria SMALLINT UNSIGNED NULL,
  sku VARCHAR(50) UNIQUE NOT NULL COMMENT 'Código único do produto',
  nome VARCHAR(100) NOT NULL,
  slug VARCHAR(120) NOT NULL UNIQUE COMMENT 'URL-friendly',
  descricao TEXT NULL,
  descricao_curta VARCHAR(255) NULL,
  preco DECIMAL(10,2) UNSIGNED NOT NULL,
  preco_promocional DECIMAL(10,2) UNSIGNED NULL,
  custo DECIMAL(10,2) UNSIGNED NULL COMMENT 'Custo de produção',
  peso DECIMAL(8,3) UNSIGNED NULL COMMENT 'Peso em gramas',
  calorias SMALLINT UNSIGNED NULL,
  quantidade_estoque INT UNSIGNED NOT NULL DEFAULT 0,
  estoque_minimo INT UNSIGNED NOT NULL DEFAULT 5,
  quantidade_vendida INT UNSIGNED NOT NULL DEFAULT 0,
  imagem_principal_url VARCHAR(255) NULL,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  destaque BOOLEAN NOT NULL DEFAULT FALSE,
  aceita_personalizacao BOOLEAN NOT NULL DEFAULT FALSE,
  tempo_preparo_minutos SMALLINT UNSIGNED NOT NULL DEFAULT 30,
  avaliacao_media DECIMAL(3,2) UNSIGNED NULL DEFAULT 0.00 COMMENT 'De 0.00 a 5.00',
  total_avaliacoes INT UNSIGNED NOT NULL DEFAULT 0,
  visualizacoes INT UNSIGNED NOT NULL DEFAULT 0,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_produtos_categoria 
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
    ON DELETE SET NULL,
  INDEX idx_nome (nome),
  INDEX idx_slug (slug),
  INDEX idx_sku (sku),
  INDEX idx_categoria_ativo (id_categoria, ativo),
  INDEX idx_destaque (destaque, ativo),
  INDEX idx_preco (preco),
  INDEX idx_avaliacao (avaliacao_media DESC),
  FULLTEXT INDEX idx_busca (nome, descricao),
  CHECK (preco > 0),
  CHECK (preco_promocional IS NULL OR preco_promocional < preco),
  CHECK (avaliacao_media IS NULL OR (avaliacao_media >= 0 AND avaliacao_media <= 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catálogo de produtos';

-- ==========================================
-- TABELA: imagens_produto
-- ==========================================
CREATE TABLE imagens_produto (
  id_imagem INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_produto INT UNSIGNED NOT NULL,
  url VARCHAR(255) NOT NULL,
  ordem TINYINT UNSIGNED NOT NULL DEFAULT 0,
  descricao VARCHAR(100) NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_imagens_produto 
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
    ON DELETE CASCADE,
  INDEX idx_produto_ordem (id_produto, ordem)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Galeria de imagens dos produtos';

-- ==========================================
-- TABELA: ingredientes
-- ==========================================
CREATE TABLE ingredientes (
  id_ingrediente SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL UNIQUE,
  tipo ENUM('Alérgeno', 'Comum', 'Premium', 'Orgânico') NOT NULL DEFAULT 'Comum',
  descricao TEXT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Ingredientes dos produtos';

-- ==========================================
-- TABELA: produto_ingredientes
-- ==========================================
CREATE TABLE produto_ingredientes (
  id_produto INT UNSIGNED NOT NULL,
  id_ingrediente SMALLINT UNSIGNED NOT NULL,
  quantidade VARCHAR(50) NULL COMMENT 'Ex: 100g, 2 unidades',
  PRIMARY KEY (id_produto, id_ingrediente),
  CONSTRAINT fk_prod_ing_produto 
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
    ON DELETE CASCADE,
  CONSTRAINT fk_prod_ing_ingrediente 
    FOREIGN KEY (id_ingrediente) REFERENCES ingredientes(id_ingrediente)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Ingredientes de cada produto';

-- ==========================================
-- TABELA: pedidos
-- ==========================================
CREATE TABLE pedidos (
  id_pedido INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT UNSIGNED NOT NULL,
  numero_pedido VARCHAR(20) UNIQUE NOT NULL COMMENT 'Formato: LCC-2025-000001',
  data_pedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  subtotal DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT 0.00,
  desconto DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT 0.00,
  taxa_entrega DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT 0.00,
  valor_total DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT 0.00,
  status ENUM('Aguardando pagamento', 'Pago', 'Em preparo', 'Pronto', 'Saiu para entrega', 'Entregue', 'Cancelado', 'Reembolsado') NOT NULL DEFAULT 'Aguardando pagamento',
  tipo_entrega ENUM('delivery', 'retirada') NOT NULL DEFAULT 'delivery',
  forma_pagamento ENUM('cartao_credito', 'cartao_debito', 'pix', 'dinheiro', 'mercadopago') NULL,
  observacoes TEXT NULL,
  codigo_rastreio VARCHAR(50) NULL,
  tempo_preparo_estimado SMALLINT UNSIGNED NULL COMMENT 'Minutos',
  tempo_entrega_estimado SMALLINT UNSIGNED NULL COMMENT 'Minutos',
  avaliacao TINYINT UNSIGNED NULL COMMENT '1-5 estrelas',
  comentario_avaliacao TEXT NULL,
  data_avaliacao DATETIME NULL,
  ip_cliente VARCHAR(45) NULL,
  user_agent TEXT NULL,
  CONSTRAINT fk_pedidos_usuario 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE,
  INDEX idx_numero_pedido (numero_pedido),
  INDEX idx_usuario_data (id_usuario, data_pedido DESC),
  INDEX idx_status (status),
  INDEX idx_data_pedido (data_pedido DESC),
  INDEX idx_avaliacao (avaliacao),
  CHECK (valor_total >= 0),
  CHECK (avaliacao IS NULL OR (avaliacao >= 1 AND avaliacao <= 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Pedidos dos clientes';

-- ==========================================
-- TABELA: itens_pedido
-- ==========================================
CREATE TABLE itens_pedido (
  id_item INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT UNSIGNED NOT NULL,
  id_produto INT UNSIGNED NOT NULL,
  nome_produto VARCHAR(100) NOT NULL COMMENT 'Snapshot do nome no momento da compra',
  quantidade SMALLINT UNSIGNED NOT NULL,
  preco_unitario DECIMAL(10,2) UNSIGNED NOT NULL,
  subtotal DECIMAL(10,2) UNSIGNED NOT NULL,
  observacoes VARCHAR(255) NULL COMMENT 'Personalizações do item',
  CONSTRAINT fk_itens_pedido_pedido 
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
    ON DELETE CASCADE,
  CONSTRAINT fk_itens_pedido_produto 
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
    ON DELETE RESTRICT,
  INDEX idx_pedido (id_pedido),
  INDEX idx_produto (id_produto),
  CHECK (quantidade > 0),
  CHECK (preco_unitario >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Itens de cada pedido';

-- ==========================================
-- TABELA: cupons (CORRIGIDA)
-- ==========================================
CREATE TABLE cupons (
  id_cupom SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) UNIQUE NOT NULL,
  descricao VARCHAR(255) NOT NULL,
  tipo_desconto ENUM('percentual', 'fixo', 'frete_gratis') NOT NULL,
  valor_desconto DECIMAL(10,2) UNSIGNED NOT NULL,
  valor_minimo_pedido DECIMAL(10,2) UNSIGNED NULL,
  quantidade_disponivel INT UNSIGNED NULL COMMENT 'NULL = ilimitado',
  quantidade_usada INT UNSIGNED NOT NULL DEFAULT 0,
  limite_por_usuario TINYINT UNSIGNED NULL COMMENT 'NULL = ilimitado',
  data_inicio DATETIME NOT NULL,
  data_expiracao DATETIME NOT NULL,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_codigo (codigo),
  INDEX idx_ativo_datas (ativo, data_inicio, data_expiracao),
  CHECK (valor_desconto >= 0),
  CHECK (data_expiracao > data_inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cupons de desconto';

-- ==========================================
-- TABELA: uso_cupons
-- ==========================================
CREATE TABLE uso_cupons (
  id_uso INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_cupom SMALLINT UNSIGNED NOT NULL,
  id_usuario INT UNSIGNED NOT NULL,
  id_pedido INT UNSIGNED NOT NULL,
  valor_desconto_aplicado DECIMAL(10,2) UNSIGNED NOT NULL,
  data_uso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_uso_cupom 
    FOREIGN KEY (id_cupom) REFERENCES cupons(id_cupom)
    ON DELETE CASCADE,
  CONSTRAINT fk_uso_usuario 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE,
  CONSTRAINT fk_uso_pedido 
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
    ON DELETE CASCADE,
  INDEX idx_cupom_usuario (id_cupom, id_usuario),
  INDEX idx_usuario_data (id_usuario, data_uso DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Histórico de uso de cupons';

-- ==========================================
-- TABELA: pagamentos
-- ==========================================
CREATE TABLE pagamentos (
  id_pagamento INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT UNSIGNED NOT NULL,
  metodo ENUM('cartao_credito', 'cartao_debito', 'pix', 'boleto', 'mercadopago', 'dinheiro') NOT NULL,
  status_transacao ENUM('pendente', 'processando', 'aprovado', 'recusado', 'cancelado', 'reembolsado') NOT NULL DEFAULT 'pendente',
  valor DECIMAL(10,2) UNSIGNED NOT NULL,
  valor_recebido DECIMAL(10,2) UNSIGNED NULL,
  troco DECIMAL(10,2) UNSIGNED NULL,
  parcelas TINYINT UNSIGNED NOT NULL DEFAULT 1,
  taxa_gateway DECIMAL(10,2) UNSIGNED NULL,
  codigo_transacao VARCHAR(100) NULL COMMENT 'ID da transação no gateway',
  codigo_autorizacao VARCHAR(100) NULL,
  nsu VARCHAR(50) NULL COMMENT 'Número Sequencial Único',
  tid VARCHAR(50) NULL COMMENT 'Transaction ID',
  mensagem_retorno TEXT NULL,
  dados_pix JSON NULL COMMENT 'QR Code, chave, etc',
  ip_pagador VARCHAR(45) NULL,
  data_processamento DATETIME NULL,
  data_aprovacao DATETIME NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_pagamentos_pedido 
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
    ON DELETE CASCADE,
  INDEX idx_pedido (id_pedido),
  INDEX idx_status (status_transacao),
  INDEX idx_codigo_transacao (codigo_transacao),
  INDEX idx_data_processamento (data_processamento DESC),
  CHECK (parcelas >= 1 AND parcelas <= 12)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Transações de pagamento';

-- ==========================================
-- TABELA: entregas
-- ==========================================
CREATE TABLE entregas (
  id_entrega INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT UNSIGNED NOT NULL,
  id_entregador INT UNSIGNED NULL,
  id_endereco INT UNSIGNED NOT NULL,
  status ENUM('Aguardando', 'Atribuído', 'A caminho', 'Próximo ao destino', 'Entregue', 'Não entregue', 'Cancelado') NOT NULL DEFAULT 'Aguardando',
  data_atribuicao DATETIME NULL,
  data_saida DATETIME NULL,
  data_entrega DATETIME NULL,
  distancia_km DECIMAL(8,3) UNSIGNED NULL,
  tempo_estimado_minutos SMALLINT UNSIGNED NULL,
  latitude_atual DECIMAL(10,8) NULL,
  longitude_atual DECIMAL(11,8) NULL,
  observacoes TEXT NULL,
  foto_comprovante_url VARCHAR(255) NULL,
  assinatura_digital TEXT NULL,
  avaliacao_entregador TINYINT UNSIGNED NULL COMMENT '1-5 estrelas',
  comentario_entregador TEXT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_entregas_pedido 
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
    ON DELETE CASCADE,
  CONSTRAINT fk_entregas_entregador 
    FOREIGN KEY (id_entregador) REFERENCES usuarios(id_usuario)
    ON DELETE SET NULL,
  CONSTRAINT fk_entregas_endereco 
    FOREIGN KEY (id_endereco) REFERENCES enderecos(id_endereco)
    ON DELETE RESTRICT,
  INDEX idx_pedido (id_pedido),
  INDEX idx_entregador_status (id_entregador, status),
  INDEX idx_status_data (status, data_atribuicao DESC),
  CHECK (avaliacao_entregador IS NULL OR (avaliacao_entregador >= 1 AND avaliacao_entregador <= 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Controle de entregas';

-- ==========================================
-- TABELA: historico_status_pedido
-- ==========================================
CREATE TABLE historico_status_pedido (
  id_historico INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT UNSIGNED NOT NULL,
  status_anterior VARCHAR(50) NULL,
  status_novo VARCHAR(50) NOT NULL,
  observacao TEXT NULL,
  alterado_por INT UNSIGNED NULL COMMENT 'ID do usuário que alterou',
  data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_historico_pedido 
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
    ON DELETE CASCADE,
  INDEX idx_pedido_data (id_pedido, data_alteracao DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Histórico de mudanças de status dos pedidos';

-- ==========================================
-- TABELA: notificacoes
-- ==========================================
CREATE TABLE notificacoes (
  id_notificacao INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT UNSIGNED NOT NULL,
  tipo ENUM('pedido', 'pagamento', 'entrega', 'promocao', 'sistema') NOT NULL,
  titulo VARCHAR(100) NOT NULL,
  mensagem TEXT NOT NULL,
  link VARCHAR(255) NULL,
  lida BOOLEAN NOT NULL DEFAULT FALSE,
  data_leitura DATETIME NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notificacoes_usuario 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE,
  INDEX idx_usuario_lida (id_usuario, lida, criado_em DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Notificações do sistema';

-- ==========================================
-- TABELA: logs_sistema
-- ==========================================
CREATE TABLE logs_sistema (
  id_log BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT UNSIGNED NULL,
  acao VARCHAR(100) NOT NULL,
  tabela VARCHAR(50) NULL,
  id_registro INT UNSIGNED NULL,
  dados_anteriores JSON NULL,
  dados_novos JSON NULL,
  ip VARCHAR(45) NULL,
  user_agent TEXT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_usuario_data (id_usuario, criado_em DESC),
  INDEX idx_acao (acao),
  INDEX idx_tabela_registro (tabela, id_registro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Log de auditoria do sistema';

SET FOREIGN_KEY_CHECKS = 1;

-- ==========================================
-- TRIGGERS
-- ==========================================

-- Trigger: Validar ano do cartão
DELIMITER $$
CREATE TRIGGER trg_before_insert_cartao
BEFORE INSERT ON cartoes
FOR EACH ROW
BEGIN
  IF NEW.validade_ano < YEAR(CURDATE()) THEN
    SIGNAL SQLSTATE '45000' 
    SET MESSAGE_TEXT = 'Ano de validade não pode ser menor que o ano atual';
  END IF;
END$$

CREATE TRIGGER trg_before_update_cartao
BEFORE UPDATE ON cartoes
FOR EACH ROW
BEGIN
  IF NEW.validade_ano < YEAR(CURDATE()) THEN
    SIGNAL SQLSTATE '45000' 
    SET MESSAGE_TEXT = 'Ano de validade não pode ser menor que o ano atual';
  END IF;
END$$
DELIMITER ;

-- Trigger: Atualizar estoque após pedido
DELIMITER $$
CREATE TRIGGER trg_after_insert_item_pedido
AFTER INSERT ON itens_pedido
FOR EACH ROW
BEGIN
  UPDATE produtos 
  SET quantidade_estoque = quantidade_estoque - NEW.quantidade
  WHERE id_produto = NEW.id_produto;
END$$
DELIMITER ;

-- Trigger: Calcular subtotal do item
DELIMITER $$
CREATE TRIGGER trg_before_insert_item_pedido
BEFORE INSERT ON itens_pedido
FOR EACH ROW
BEGIN
  SET NEW.subtotal = NEW.quantidade * NEW.preco_unitario;
END$$
DELIMITER ;

-- Trigger: Atualizar valor total do pedido
DELIMITER $$
CREATE TRIGGER trg_after_insert_item_update_total
AFTER INSERT ON itens_pedido
FOR EACH ROW
BEGIN
  UPDATE pedidos 
  SET subtotal = (
    SELECT COALESCE(SUM(subtotal), 0)
    FROM itens_pedido 
    WHERE id_pedido = NEW.id_pedido
  ),
  valor_total = subtotal + taxa_entrega - desconto
  WHERE id_pedido = NEW.id_pedido;
END$$
DELIMITER ;

-- Trigger: Registrar mudança de status no histórico
DELIMITER $$
CREATE TRIGGER trg_after_update_pedido_status
AFTER UPDATE ON pedidos
FOR EACH ROW
BEGIN
  IF OLD.status != NEW.status THEN
    INSERT INTO historico_status_pedido (id_pedido, status_anterior, status_novo, observacao)
    VALUES (NEW.id_pedido, OLD.status, NEW.status, 'Status alterado automaticamente');
  END IF;
END$$
DELIMITER ;

-- Trigger: Atualizar quantidade usada do cupom
DELIMITER $$
CREATE TRIGGER trg_after_insert_uso_cupom
AFTER INSERT ON uso_cupons
FOR EACH ROW
BEGIN
  UPDATE cupons 
  SET quantidade_usada = quantidade_usada + 1
  WHERE id_cupom = NEW.id_cupom;
END$$
DELIMITER ;

-- ==========================================
-- DADOS INICIAIS (SEED DATA)
-- ==========================================

-- 1. Inserir Endereços
INSERT INTO enderecos (cidade, estado, rua, numero, cep, latitude, longitude) VALUES
('São Paulo', 'SP', 'Rua das Flores', '123', '01234-567', -23.550520, -46.633308),
('Rio de Janeiro', 'RJ', 'Av. Atlântica', '456', '22021-001', -22.970722, -43.182365),
('Belo Horizonte', 'MG', 'Rua da Paz', '789', '30130-000', -19.916681, -43.934493);

-- 2. Inserir Usuários
INSERT INTO usuarios (id_endereco, nome, sobrenome, cpf, telefone, email, senha_hash, data_nascimento, sexo, tipo_usuario, ativo, email_verificado) VALUES
(NULL, 'Administrador', 'Sistema', '12345678901', '(11)98765-4321', 'admin@leonscupcake.com', 
 'pbkdf2:sha256:600000$sKzQF9ZxZp8gAZEe$f5a1c9f3e2d4b6a8c1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7',
 '1990-01-15', 'M', 'admin', TRUE, TRUE),

(1, 'João', 'Silva', '98765432101', '(11)91234-5678', 'joao@email.com',
 'pbkdf2:sha256:600000$sKzQF9ZxZp8gAZEe$f5a1c9f3e2d4b6a8c1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7',
 '1995-06-20', 'M', 'cliente', TRUE, TRUE),

(2, 'Maria', 'Santos', '11122233344', '(21)92345-6789', 'maria@email.com',
 'pbkdf2:sha256:600000$sKzQF9ZxZp8gAZEe$f5a1c9f3e2d4b6a8c1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7',
 '1992-03-10', 'F', 'cliente', TRUE, TRUE),

(3, 'Carlos', 'Oliveira', '55566677788', '(31)93456-7890', 'carlos@leonscupcake.com',
 'pbkdf2:sha256:600000$sKzQF9ZxZp8gAZEe$f5a1c9f3e2d4b6a8c1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7',
 '1988-11-25', 'M', 'entregador', TRUE, TRUE);

-- 3. Inserir Categorias
INSERT INTO categorias (nome, slug, descricao, ordem_exibicao, ativo) VALUES
('Cupcakes Clássicos', 'cupcakes-classicos', 'Sabores tradicionais e deliciosos', 1, TRUE),
('Cupcakes Premium', 'cupcakes-premium', 'Sabores sofisticados e ingredientes especiais', 2, TRUE),
('Cupcakes Veganos', 'cupcakes-veganos', 'Opções 100% veganas', 3, TRUE),
('Cupcakes Diet', 'cupcakes-diet', 'Opções com menos açúcar', 4, TRUE),
('Cupcakes Temáticos', 'cupcakes-tematicos', 'Para ocasiões especiais', 5, TRUE);

-- 4. Inserir Produtos
INSERT INTO produtos (id_categoria, sku, nome, slug, descricao, descricao_curta, preco, peso, calorias, quantidade_estoque, estoque_minimo, ativo, destaque, tempo_preparo_minutos) VALUES
-- Cupcakes Clássicos
(1, 'CUP-CLA-001', 'Cupcake de Chocolate', 'cupcake-chocolate', 
 'Delicioso cupcake de massa de chocolate com cobertura cremosa de chocolate belga', 
 'Massa de chocolate com cobertura cremosa', 8.50, 80.000, 280, 50, 10, TRUE, TRUE, 25),

(1, 'CUP-CLA-002', 'Cupcake de Baunilha', 'cupcake-baunilha',
 'Cupcake de massa de baunilha com cobertura suave e delicada',
 'Massa de baunilha com cobertura suave', 7.90, 75.000, 260, 45, 10, TRUE, FALSE, 25),

(1, 'CUP-CLA-003', 'Cupcake Red Velvet', 'cupcake-red-velvet',
 'Clássico red velvet com cobertura de cream cheese e toque de cacau',
 'Red velvet com cream cheese', 9.90, 85.000, 310, 30, 8, TRUE, TRUE, 30),

(1, 'CUP-CLA-004', 'Cupcake de Morango', 'cupcake-morango',
 'Massa leve com pedaços de morango fresco e cobertura de morango',
 'Com pedaços de morango fresco', 8.90, 78.000, 270, 40, 10, TRUE, FALSE, 25),

-- Cupcakes Premium
(2, 'CUP-PRE-001', 'Cupcake Ferrero Rocher', 'cupcake-ferrero',
 'Massa de chocolate com Nutella e bombom Ferrero Rocher no topo',
 'Com Nutella e Ferrero Rocher', 15.90, 95.000, 380, 20, 5, TRUE, TRUE, 35),

(2, 'CUP-PRE-002', 'Cupcake Pistache', 'cupcake-pistache',
 'Massa de pistache com cobertura especial e pistaches triturados',
 'Massa de pistache com cobertura especial', 14.50, 90.000, 340, 25, 5, TRUE, FALSE, 35),

(2, 'CUP-PRE-003', 'Cupcake Maracujá', 'cupcake-maracuja',
 'Massa leve e aerada com recheio e cobertura de maracujá',
 'Com recheio de maracujá', 12.90, 82.000, 290, 30, 8, TRUE, FALSE, 30),

(2, 'CUP-PRE-004', 'Cupcake Brownie', 'cupcake-brownie',
 'Massa densa de brownie com chocolate belga e cobertura ganache',
 'Brownie com chocolate belga', 13.90, 92.000, 360, 28, 8, TRUE, FALSE, 35),

-- Cupcakes Veganos
(3, 'CUP-VEG-001', 'Cupcake Vegano Chocolate', 'cupcake-vegano-chocolate',
 'Cupcake 100% vegano de chocolate com cobertura vegana cremosa',
 'Chocolate 100% vegano', 10.90, 80.000, 260, 35, 8, TRUE, FALSE, 30),

(3, 'CUP-VEG-002', 'Cupcake Vegano Limão', 'cupcake-vegano-limao',
 'Massa vegana de limão siciliano com cobertura cítrica',
 'Limão siciliano vegano', 10.50, 75.000, 240, 30, 8, TRUE, FALSE, 30),

(3, 'CUP-VEG-003', 'Cupcake Vegano Banana', 'cupcake-vegano-banana',
 'Massa vegana de banana com canela e cobertura de creme vegano',
 'Banana com canela vegano', 9.90, 77.000, 250, 32, 8, TRUE, FALSE, 28),

-- Cupcakes Diet
(4, 'CUP-DIE-001', 'Cupcake Diet Chocolate', 'cupcake-diet-chocolate',
 'Cupcake de chocolate sem açúcar, adoçado com stevia',
 'Chocolate sem açúcar', 11.90, 70.000, 180, 25, 5, TRUE, FALSE, 28),

(4, 'CUP-DIE-002', 'Cupcake Diet Coco', 'cupcake-diet-coco',
 'Massa de coco sem açúcar com cobertura light',
 'Coco sem açúcar', 11.50, 68.000, 170, 22, 5, TRUE, FALSE, 28),

-- Cupcakes Temáticos
(5, 'CUP-TEM-001', 'Cupcake Natal', 'cupcake-natal',
 'Decorado com tema natalino, perfeito para festas de fim de ano',
 'Decorado tema natalino', 12.90, 85.000, 300, 15, 5, TRUE, FALSE, 40),

(5, 'CUP-TEM-002', 'Cupcake Aniversário', 'cupcake-aniversario',
 'Decorado especialmente para aniversários com confeitos coloridos',
 'Decorado para aniversário', 11.90, 82.000, 290, 20, 5, TRUE, FALSE, 35),

(5, 'CUP-TEM-003', 'Cupcake Páscoa', 'cupcake-pascoa',
 'Decorado com tema de páscoa, com ovinhos de chocolate',
 'Decorado tema páscoa', 12.90, 86.000, 310, 18, 5, TRUE, FALSE, 40);

-- 5. Inserir Ingredientes
INSERT INTO ingredientes (nome, tipo) VALUES
('Farinha de Trigo', 'Comum'),
('Açúcar', 'Comum'),
('Ovos', 'Alérgeno'),
('Leite', 'Alérgeno'),
('Chocolate', 'Premium'),
('Manteiga', 'Comum'),
('Fermento', 'Comum'),
('Baunilha', 'Premium'),
('Morango', 'Comum'),
('Pistache', 'Premium'),
('Nozes', 'Alérgeno'),
('Glúten', 'Alérgeno');

-- 6. Relacionar Produtos com Ingredientes
INSERT INTO produto_ingredientes (id_produto, id_ingrediente, quantidade) VALUES
(1, 1, '100g'), (1, 2, '80g'), (1, 3, '2 unidades'), (1, 5, '50g'),
(2, 1, '100g'), (2, 2, '80g'), (2, 3, '2 unidades'), (2, 8, '5ml'),
(5, 1, '100g'), (5, 5, '80g'), (5, 3, '2 unidades'), (5, 11, '30g');

-- 7. Inserir Cupons (CORRIGIDO - valor_desconto >= 0)
INSERT INTO cupons (codigo, descricao, tipo_desconto, valor_desconto, valor_minimo_pedido, quantidade_disponivel, limite_por_usuario, data_inicio, data_expiracao, ativo) VALUES
('BEMVINDO10', 'Desconto de boas-vindas', 'percentual', 10.00, 30.00, 100, 1, '2025-01-01 00:00:00', '2025-12-31 23:59:59', TRUE),
('FRETEGRATIS', 'Frete grátis acima de R$50', 'frete_gratis', 0.00, 50.00, NULL, NULL, '2025-01-01 00:00:00', '2025-12-31 23:59:59', TRUE),
('PRIMEIRACOMPRA', 'Primeira compra com 15% OFF', 'percentual', 15.00, 40.00, 50, 1, '2025-01-01 00:00:00', '2025-06-30 23:59:59', TRUE);

-- 8. Inserir Pedido de Exemplo
INSERT INTO pedidos (id_usuario, numero_pedido, subtotal, taxa_entrega, valor_total, status, tipo_entrega, forma_pagamento, observacoes, tempo_preparo_estimado, tempo_entrega_estimado) VALUES
(2, 'LCC-2025-000001', 42.80, 8.00, 50.80, 'Em preparo', 'delivery', 'pix', 'Entregar após às 18h', 30, 45);

-- 9. Inserir Itens do Pedido
INSERT INTO itens_pedido (id_pedido, id_produto, nome_produto, quantidade, preco_unitario, subtotal) VALUES
(1, 1, 'Cupcake de Chocolate', 2, 8.50, 17.00),
(1, 3, 'Cupcake Red Velvet', 1, 9.90, 9.90),
(1, 5, 'Cupcake Ferrero Rocher', 1, 15.90, 15.90);

-- 10. Atualizar quantidade vendida dos produtos
UPDATE produtos SET quantidade_vendida = quantidade_vendida + 2 WHERE id_produto = 1;
UPDATE produtos SET quantidade_vendida = quantidade_vendida + 1 WHERE id_produto = 3;
UPDATE produtos SET quantidade_vendida = quantidade_vendida + 1 WHERE id_produto = 5;

-- 11. Inserir Pagamento
INSERT INTO pagamentos (id_pedido, metodo, status_transacao, valor, parcelas, codigo_transacao, data_processamento, data_aprovacao) VALUES
(1, 'pix', 'aprovado', 50.80, 1, 'PIX-2025-ABC123XYZ', '2025-11-17 14:30:00', '2025-11-17 14:30:15');

-- 12. Inserir Entrega
INSERT INTO entregas (id_pedido, id_entregador, id_endereco, status, data_atribuicao, data_saida, distancia_km, tempo_estimado_minutos, observacoes) VALUES
(1, 4, 2, 'A caminho', '2025-11-17 15:00:00', '2025-11-17 15:15:00', 5.200, 20, 'Cliente solicitou entrega pelos fundos');

-- 13. Inserir Histórico de Status
INSERT INTO historico_status_pedido (id_pedido, status_anterior, status_novo, observacao, alterado_por) VALUES
(1, NULL, 'Aguardando pagamento', 'Pedido criado', 2),
(1, 'Aguardando pagamento', 'Pago', 'Pagamento aprovado via PIX', NULL),
(1, 'Pago', 'Em preparo', 'Pedido enviado para cozinha', 1);

-- 14. Inserir Notificações
INSERT INTO notificacoes (id_usuario, tipo, titulo, mensagem, link, lida) VALUES
(2, 'pedido', 'Pedido Confirmado', 'Seu pedido #LCC-2025-000001 foi confirmado e está em preparo!', '/pedidos/1', FALSE),
(2, 'pagamento', 'Pagamento Aprovado', 'Pagamento de R$ 50,80 aprovado com sucesso via PIX', '/pedidos/1', FALSE),
(4, 'entrega', 'Nova Entrega', 'Você tem uma nova entrega atribuída', '/entregas/1', FALSE);

-- ==========================================
-- VIEWS ÚTEIS
-- ==========================================

-- View: Produtos em Destaque
CREATE OR REPLACE VIEW v_produtos_destaque AS
SELECT 
  p.id_produto,
  p.nome,
  p.slug,
  p.descricao_curta,
  p.preco,
  p.preco_promocional,
  p.imagem_principal_url,
  p.avaliacao_media,
  p.total_avaliacoes,
  c.nome AS categoria
FROM produtos p
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE p.ativo = TRUE AND p.destaque = TRUE
ORDER BY p.quantidade_vendida DESC, p.avaliacao_media DESC;

-- View: Pedidos Completos
CREATE OR REPLACE VIEW v_pedidos_completos AS
SELECT 
  p.id_pedido,
  p.numero_pedido,
  p.data_pedido,
  p.valor_total,
  p.status,
  u.nome AS cliente_nome,
  u.email AS cliente_email,
  u.telefone AS cliente_telefone,
  COUNT(ip.id_item) AS total_itens,
  pg.metodo AS metodo_pagamento,
  pg.status_transacao AS status_pagamento,
  e.status AS status_entrega,
  CONCAT(u_ent.nome, ' ', u_ent.sobrenome) AS entregador_nome
FROM pedidos p
INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
LEFT JOIN itens_pedido ip ON p.id_pedido = ip.id_pedido
LEFT JOIN pagamentos pg ON p.id_pedido = pg.id_pedido
LEFT JOIN entregas e ON p.id_pedido = e.id_pedido
LEFT JOIN usuarios u_ent ON e.id_entregador = u_ent.id_usuario
GROUP BY p.id_pedido, p.numero_pedido, p.data_pedido, p.valor_total, p.status, 
         u.nome, u.email, u.telefone, pg.metodo, pg.status_transacao, 
         e.status, u_ent.nome, u_ent.sobrenome;

-- View: Produtos Mais Vendidos
CREATE OR REPLACE VIEW v_produtos_mais_vendidos AS
SELECT 
  p.id_produto,
  p.nome,
  p.preco,
  p.quantidade_vendida,
  p.avaliacao_media,
  c.nome AS categoria,
  (p.preco * p.quantidade_vendida) AS receita_total
FROM produtos p
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE p.ativo = TRUE
ORDER BY p.quantidade_vendida DESC
LIMIT 10;

-- View: Estatísticas de Usuários
CREATE OR REPLACE VIEW v_estatisticas_usuarios AS
SELECT 
  tipo_usuario,
  COUNT(*) AS total,
  SUM(CASE WHEN ativo = TRUE THEN 1 ELSE 0 END) AS ativos,
  SUM(CASE WHEN ativo = FALSE THEN 1 ELSE 0 END) AS inativos
FROM usuarios
GROUP BY tipo_usuario;

-- ==========================================
-- STORED PROCEDURES
-- ==========================================

-- Procedure: Buscar produtos com filtros
DELIMITER $
CREATE PROCEDURE sp_buscar_produtos(
  IN p_categoria_id SMALLINT UNSIGNED,
  IN p_preco_min DECIMAL(10,2),
  IN p_preco_max DECIMAL(10,2),
  IN p_termo_busca VARCHAR(100),
  IN p_ordenacao VARCHAR(20)
)
BEGIN
  SELECT * FROM produtos 
  WHERE ativo = TRUE
    AND (p_categoria_id IS NULL OR id_categoria = p_categoria_id)
    AND (p_preco_min IS NULL OR preco >= p_preco_min)
    AND (p_preco_max IS NULL OR preco <= p_preco_max)
    AND (p_termo_busca IS NULL OR nome LIKE CONCAT('%', p_termo_busca, '%') OR descricao LIKE CONCAT('%', p_termo_busca, '%'))
  ORDER BY 
    CASE WHEN p_ordenacao = 'preco_asc' THEN preco END ASC,
    CASE WHEN p_ordenacao = 'preco_desc' THEN preco END DESC,
    CASE WHEN p_ordenacao = 'mais_vendidos' THEN quantidade_vendida END DESC,
    CASE WHEN p_ordenacao IS NULL OR p_ordenacao = 'avaliacao' THEN avaliacao_media END DESC;
END$
DELIMITER ;

-- Procedure: Calcular frete
DELIMITER $
CREATE PROCEDURE sp_calcular_frete(
  IN p_cep_destino CHAR(9),
  IN p_valor_pedido DECIMAL(10,2),
  OUT p_valor_frete DECIMAL(10,2)
)
BEGIN
  IF p_valor_pedido >= 50.00 THEN
    SET p_valor_frete = 0.00;
  ELSE
    SET p_valor_frete = 8.00;
  END IF;
END$
DELIMITER ;

-- Procedure: Aplicar cupom de desconto
DELIMITER $
CREATE PROCEDURE sp_aplicar_cupom(
  IN p_codigo_cupom VARCHAR(50),
  IN p_id_usuario INT UNSIGNED,
  IN p_valor_pedido DECIMAL(10,2),
  OUT p_desconto DECIMAL(10,2),
  OUT p_mensagem VARCHAR(255)
)
BEGIN
  DECLARE v_id_cupom SMALLINT UNSIGNED;
  DECLARE v_tipo_desconto VARCHAR(20);
  DECLARE v_valor_desconto DECIMAL(10,2);
  DECLARE v_valor_minimo DECIMAL(10,2);
  DECLARE v_qtd_disponivel INT UNSIGNED;
  DECLARE v_limite_usuario TINYINT UNSIGNED;
  DECLARE v_uso_usuario INT;
  DECLARE v_ativo BOOLEAN;
  DECLARE v_data_atual DATETIME;
  DECLARE v_data_inicio DATETIME;
  DECLARE v_data_expiracao DATETIME;
  
  SET v_data_atual = NOW();
  SET p_desconto = 0.00;
  
  SELECT id_cupom, tipo_desconto, valor_desconto, valor_minimo_pedido, 
         quantidade_disponivel, limite_por_usuario, ativo, 
         data_inicio, data_expiracao
  INTO v_id_cupom, v_tipo_desconto, v_valor_desconto, v_valor_minimo,
       v_qtd_disponivel, v_limite_usuario, v_ativo,
       v_data_inicio, v_data_expiracao
  FROM cupons
  WHERE codigo = p_codigo_cupom;
  
  IF v_id_cupom IS NULL THEN
    SET p_mensagem = 'Cupom inválido';
  ELSEIF v_ativo = FALSE THEN
    SET p_mensagem = 'Cupom inativo';
  ELSEIF v_data_atual < v_data_inicio THEN
    SET p_mensagem = 'Cupom ainda não está válido';
  ELSEIF v_data_atual > v_data_expiracao THEN
    SET p_mensagem = 'Cupom expirado';
  ELSEIF v_valor_minimo IS NOT NULL AND p_valor_pedido < v_valor_minimo THEN
    SET p_mensagem = CONCAT('Valor mínimo do pedido: R$ ', v_valor_minimo);
  ELSEIF v_qtd_disponivel IS NOT NULL AND v_qtd_disponivel <= 0 THEN
    SET p_mensagem = 'Cupom esgotado';
  ELSE
    SELECT COUNT(*) INTO v_uso_usuario
    FROM uso_cupons
    WHERE id_cupom = v_id_cupom AND id_usuario = p_id_usuario;
    
    IF v_limite_usuario IS NOT NULL AND v_uso_usuario >= v_limite_usuario THEN
      SET p_mensagem = 'Você já atingiu o limite de uso deste cupom';
    ELSE
      IF v_tipo_desconto = 'percentual' THEN
        SET p_desconto = (p_valor_pedido * v_valor_desconto) / 100;
      ELSEIF v_tipo_desconto = 'fixo' THEN
        SET p_desconto = v_valor_desconto;
      END IF;
      
      IF p_desconto > p_valor_pedido THEN
        SET p_desconto = p_valor_pedido;
      END IF;
      
      SET p_mensagem = 'Cupom aplicado com sucesso';
    END IF;
  END IF;
END$
DELIMITER ;

-- Procedure: Relatório de vendas por período
DELIMITER $
CREATE PROCEDURE sp_relatorio_vendas(
  IN p_data_inicio DATE,
  IN p_data_fim DATE
)
BEGIN
  SELECT 
    DATE(p.data_pedido) AS data,
    COUNT(DISTINCT p.id_pedido) AS total_pedidos,
    SUM(p.valor_total) AS faturamento,
    AVG(p.valor_total) AS ticket_medio,
    COUNT(DISTINCT p.id_usuario) AS clientes_unicos
  FROM pedidos p
  WHERE DATE(p.data_pedido) BETWEEN p_data_inicio AND p_data_fim
    AND p.status NOT IN ('Cancelado', 'Reembolsado')
  GROUP BY DATE(p.data_pedido)
  ORDER BY data DESC;
END$
DELIMITER ;

-- ==========================================
-- VERIFICAÇÃO FINAL
-- ==========================================

SELECT '✅ BANCO DE DADOS CRIADO COM SUCESSO!' AS Status;
SELECT '' AS '';

SELECT '📊 RESUMO DAS TABELAS:' AS Info;
SELECT 
  table_name AS Tabela,
  table_rows AS 'Linhas',
  ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Tamanho_MB'
FROM information_schema.TABLES
WHERE table_schema = 'leons_cupcake'
ORDER BY table_name;

SELECT '' AS '';
SELECT '📦 DADOS INICIAIS:' AS Info;
SELECT 'Endereços' AS Tabela, COUNT(*) AS Total FROM enderecos
UNION ALL SELECT 'Usuários', COUNT(*) FROM usuarios
UNION ALL SELECT 'Categorias', COUNT(*) FROM categorias
UNION ALL SELECT 'Produtos', COUNT(*) FROM produtos
UNION ALL SELECT 'Ingredientes', COUNT(*) FROM ingredientes
UNION ALL SELECT 'Cupons', COUNT(*) FROM cupons
UNION ALL SELECT 'Pedidos', COUNT(*) FROM pedidos
UNION ALL SELECT 'Itens Pedido', COUNT(*) FROM itens_pedido
UNION ALL SELECT 'Pagamentos', COUNT(*) FROM pagamentos
UNION ALL SELECT 'Entregas', COUNT(*) FROM entregas;

SELECT * FROM usuarios;

UPDATE usuarios
SET tipo_usuario = 'admin'
WHERE email = 'vinicius@gmail.com';