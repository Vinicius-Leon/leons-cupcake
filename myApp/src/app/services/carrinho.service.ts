import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface ItemCarrinho {
  id_produto: number;
  nome: string;
  descricao?: string;
  preco: number;
  quantidade: number;
  imagem_principal_url?: string;  // <-- campo correto
}

@Injectable({
  providedIn: 'root'
})
export class CarrinhoService {
  private readonly STORAGE_KEY = 'carrinho';
  private itensSubject = new BehaviorSubject<ItemCarrinho[]>(this.carregarItens());
  
  // Observable para componentes se inscreverem
  public itens$: Observable<ItemCarrinho[]> = this.itensSubject.asObservable();

  constructor() {}

  // =============================
  // GETTERS
  // =============================

  getItens(): ItemCarrinho[] {
    return this.itensSubject.value;
  }

  getQuantidadeTotal(): number {
    return this.getItens().reduce((total, item) => total + item.quantidade, 0);
  }

  getValorTotal(): number {
    return this.getItens().reduce((total, item) => total + (item.preco * item.quantidade), 0);
  }

  isEmpty(): boolean {
    return this.getItens().length === 0;
  }

  // =============================
  // ADICIONAR ITEM
  // =============================

  adicionarItem(produto: any, quantidade: number = 1): void {
    const itens = this.getItens();
    const index = itens.findIndex(item => item.id_produto === produto.id_produto);

    if (index > -1) {
      // Item já existe, aumenta quantidade
      itens[index].quantidade += quantidade;
    } else {
      // Novo item
      const novoItem: ItemCarrinho = {
        id_produto: produto.id_produto,
        nome: produto.nome,
        descricao: produto.descricao,
        preco: produto.preco,
        quantidade: quantidade,
        imagem_principal_url: produto.imagem_principal_url   // <-- CORRIGIDO
      };
      itens.push(novoItem);
    }

    this.atualizarItens(itens);
  }

  // =============================
  // REMOVER ITEM
  // =============================

  removerItem(id_produto: number): void {
    const itens = this.getItens().filter(item => item.id_produto !== id_produto);
    this.atualizarItens(itens);
  }

  removerItemPorIndex(index: number): void {
    const itens = this.getItens();
    if (index >= 0 && index < itens.length) {
      itens.splice(index, 1);
      this.atualizarItens(itens);
    }
  }

  // =============================
  // ATUALIZAR QUANTIDADE
  // =============================

  atualizarQuantidade(id_produto: number, quantidade: number): void {
    const itens = this.getItens();
    const index = itens.findIndex(item => item.id_produto === id_produto);

    if (index > -1) {
      if (quantidade <= 0) {
        itens.splice(index, 1); // remove item
      } else {
        itens[index].quantidade = quantidade;
      }
      this.atualizarItens(itens);
    }
  }

  aumentarQuantidade(id_produto: number): void {
    const itens = this.getItens();
    const item = itens.find(i => i.id_produto === id_produto);
    if (item) {
      item.quantidade++;
      this.atualizarItens(itens);
    }
  }

  diminuirQuantidade(id_produto: number): void {
    const itens = this.getItens();
    const item = itens.find(i => i.id_produto === id_produto);
    if (item) {
      if (item.quantidade > 1) {
        item.quantidade--;
        this.atualizarItens(itens);
      } else {
        this.removerItem(id_produto);
      }
    }
  }

  // =============================
  // LIMPAR
  // =============================

  limparCarrinho(): void {
    this.atualizarItens([]);
  }

  // =============================
  // PERSISTÊNCIA
  // =============================

  private atualizarItens(itens: ItemCarrinho[]): void {
    this.salvarItens(itens);
    this.itensSubject.next(itens);
  }

  private salvarItens(itens: ItemCarrinho[]): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(itens));
    } catch (error) {
      console.error('Erro ao salvar carrinho:', error);
    }
  }

  private carregarItens(): ItemCarrinho[] {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      const itens: ItemCarrinho[] = data ? JSON.parse(data) : [];

      // CORREÇÃO automática de itens antigos (com imagem_url)
      return itens.map(item => ({
        ...item,
        imagem_principal_url: item.imagem_principal_url || (item as any).imagem_url || null
      }));

    } catch (error) {
      console.error('Erro ao carregar carrinho:', error);
      return [];
    }
  }

  // =============================
  // CONVERSÃO PARA PEDIDO
  // =============================

  getPedidoPayload(): any {
    const itens = this.getItens().map(item => ({
      id_produto: item.id_produto,
      quantidade: item.quantidade
    }));

    return {
      itens: itens,
      valor_total: this.getValorTotal()
    };
  }
}