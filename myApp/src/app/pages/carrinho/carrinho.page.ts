import { Component, OnInit, OnDestroy } from '@angular/core';
import { IonicModule, ToastController, AlertController, LoadingController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CarrinhoService, ItemCarrinho } from '../../services/carrinho.service';
import { ApiService } from '../../services/api.service';
import { Subscription } from 'rxjs';

@Component({
  standalone: true,
  selector: 'app-carrinho',
  templateUrl: './carrinho.page.html',
  styleUrls: ['./carrinho.page.scss'],
  imports: [IonicModule, CommonModule, FormsModule, RouterLink]
})
export class CarrinhoPage implements OnInit, OnDestroy {
  itens: ItemCarrinho[] = [];
  private subscription?: Subscription;
  carregando = false;

  constructor(
    private carrinhoService: CarrinhoService,
    private api: ApiService,
    private router: Router,
    private toastCtrl: ToastController,
    private alertCtrl: AlertController,
    private loadingCtrl: LoadingController
  ) {}

  ngOnInit() {
    // Se inscreve para receber atualizações do carrinho
    this.subscription = this.carrinhoService.itens$.subscribe(itens => {
      this.itens = itens;
    });
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  // =============================
  // CÁLCULOS
  // =============================

  total(): number {
    return this.carrinhoService.getValorTotal();
  }

  subtotal(item: ItemCarrinho): number {
    return item.preco * item.quantidade;
  }

  // =============================
  // AÇÕES DO CARRINHO
  // =============================

  aumentar(item: ItemCarrinho) {
    this.carrinhoService.aumentarQuantidade(item.id_produto);
  }

  diminuir(item: ItemCarrinho) {
    this.carrinhoService.diminuirQuantidade(item.id_produto);
  }

  async remover(index: number) {
    const alert = await this.alertCtrl.create({
      header: 'Confirmar remoção',
      message: 'Deseja remover este item do carrinho?',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Remover',
          role: 'destructive',
          handler: () => {
            this.carrinhoService.removerItemPorIndex(index);
            this.showToast('Item removido com sucesso', 'success');
          }
        }
      ]
    });

    await alert.present();
  }

  async limparCarrinho() {
    const alert = await this.alertCtrl.create({
      header: 'Limpar carrinho',
      message: 'Tem certeza que deseja remover todos os itens?',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Limpar',
          role: 'destructive',
          handler: () => {
            this.carrinhoService.limparCarrinho();
            this.showToast('Carrinho limpo', 'success');
          }
        }
      ]
    });

    await alert.present();
  }

  // =============================
  // FINALIZAR COMPRA
  // =============================

  async finalizarCompra() {
    if (this.itens.length === 0) {
      this.showToast('Seu carrinho está vazio', 'warning');
      return;
    }

    const alert = await this.alertCtrl.create({
      header: 'Finalizar pedido',
      message: `Total: R$ ${this.total().toFixed(2)}`,
      inputs: [
        {
          name: 'observacoes',
          type: 'textarea',
          placeholder: 'Observações (opcional)'
        },
        {
          name: 'metodo_pagamento',
          type: 'radio',
          label: 'PIX',
          value: 'pix',
          checked: true
        },
        {
          name: 'metodo_pagamento',
          type: 'radio',
          label: 'Cartão',
          value: 'cartao'
        },
        {
          name: 'metodo_pagamento',
          type: 'radio',
          label: 'Boleto',
          value: 'boleto'
        }
      ],
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Confirmar',
          handler: (data) => {
            this.criarPedido(data.observacoes, data.metodo_pagamento);
          }
        }
      ]
    });

    await alert.present();
  }

  async criarPedido(observacoes: string, metodo_pagamento: string) {
    const loader = await this.loadingCtrl.create({
      message: 'Criando pedido...',
      spinner: 'crescent'
    });
    await loader.present();

    this.carregando = true;

    const payload = {
      ...this.carrinhoService.getPedidoPayload(),
      observacoes: observacoes || null,
      metodo_pagamento: metodo_pagamento || 'pix'
    };

    this.api.criarPedido(payload).subscribe({
      next: async (response) => {
        await loader.dismiss();
        this.carregando = false;
        
        // Limpa o carrinho após pedido criado
        this.carrinhoService.limparCarrinho();
        
        await this.showToast('Pedido criado com sucesso!', 'success');
        
        // Navega para página de pedidos
        this.router.navigate(['/pedidos']);
      },
      error: async (err) => {
        await loader.dismiss();
        this.carregando = false;
        const mensagem = err.erro || 'Erro ao criar pedido';
        await this.showToast(mensagem, 'danger');
      }
    });
  }

  // =============================
  // UTILITÁRIOS
  // =============================

  async showToast(msg: string, color: 'success' | 'danger' | 'warning' = 'danger') {
    const toast = await this.toastCtrl.create({
      message: msg,
      duration: 2500,
      color: color,
      position: 'bottom',
      buttons: [
        {
          text: 'OK',
          role: 'cancel'
        }
      ]
    });
    await toast.present();
  }

  continuarComprando() {
    this.router.navigate(['/home']);
  }
}