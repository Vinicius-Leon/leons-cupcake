import { Component, OnInit } from '@angular/core';
import { IonicModule, ToastController, LoadingController, MenuController, AlertController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../auth/auth.service';
import { CarrinhoService } from '../../services/carrinho.service';

@Component({
  standalone: true,
  selector: 'app-home',
  templateUrl: './home.page.html',
  styleUrls: ['./home.page.scss'],
  imports: [IonicModule, CommonModule, FormsModule, RouterLink]
})
export class HomePage implements OnInit {
  produtos: any[] = [];
  carregando = true;
  usuario: any = null;
  quantidadeCarrinho = 0;
  isAdmin = false;
  isEntregador = false;

  constructor(
    private api: ApiService,
    private auth: AuthService,
    private carrinhoService: CarrinhoService,
    private router: Router,
    private toastCtrl: ToastController,
    private loadingCtrl: LoadingController,
    public menuCtrl: MenuController,  // MUDOU DE PRIVATE PARA PUBLIC
    private alertCtrl: AlertController
  ) {}

  ngOnInit() {
    this.carregarUsuario();
    this.carregarProdutos();
    this.atualizarBadgeCarrinho();
  }

  ionViewWillEnter() {
    this.atualizarBadgeCarrinho();
  }

  carregarUsuario() {
    this.api.getUsuarioLogado().subscribe({
      next: (res) => {
        this.usuario = res;
        this.auth.saveUser(res);
        this.isAdmin = res.tipo_usuario === 'admin';
        this.isEntregador = res.tipo_usuario === 'entregador';
      },
      error: (err) => {
        console.error('Erro ao carregar usuário:', err);
      }
    });
  }

  async carregarProdutos(event?: any) {
    if (!event) {
      this.carregando = true;
    }

    this.api.listarProdutos().subscribe({
      next: (res) => {
        this.produtos = res || [];
        this.carregando = false;
        if (event) event.target.complete();
      },
      error: async (err) => {
        this.carregando = false;
        if (event) event.target.complete();
        this.showToast('Erro ao carregar produtos', 'danger');
      }
    });
  }

  atualizarBadgeCarrinho() {
    this.quantidadeCarrinho = this.carrinhoService.getQuantidadeTotal();
  }

  async abrirProduto(produto: any) {
    const alert = await this.alertCtrl.create({
      header: produto.nome,
      message: `
        <div style="text-align: center;">
          <img src="${produto.imagem_principal_url}" 
               style="width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
          <p>${produto.descricao || 'Sem descrição'}</p>
          <p style="font-size: 1.2rem; color: #0079BF; font-weight: bold;">
            R$ ${produto.preco.toFixed(2)}
          </p>
          <p style="color: ${produto.quantidade > 0 ? 'green' : 'red'};">
            ${produto.quantidade_estoque > 0 ? `Estoque: ${produto.quantidade_estoque}` : 'Indisponível'}
          </p>
        </div>
      `,
      buttons: [
        {
          text: 'Fechar',
          role: 'cancel'
        },
        {
          text: 'Adicionar ao Carrinho',
          handler: () => {
            this.adicionarAoCarrinho(produto);
          }
        }
      ]
    });

    await alert.present();
  }

  async adicionarAoCarrinho(produto: any) {
    if (produto.quantidade <= 0) {
      await this.showToast('Produto indisponível', 'warning');
      return;
    }

    const alert = await this.alertCtrl.create({
      header: 'Quantidade',
      message: `Quantos ${produto.nome} deseja adicionar?`,
      inputs: [
        {
          name: 'quantidade',
          type: 'number',
          min: 1,
          max: produto.quantidade_estoque,
          value: 1,
          placeholder: 'Quantidade'
        }
      ],
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Adicionar',
          handler: (data) => {
            const qtd = parseInt(data.quantidade) || 1;
            
            if (qtd <= 0 || qtd > produto.quantidade_estoque) {
              this.showToast('Quantidade inválida', 'warning');
              return false;
            }

            this.carrinhoService.adicionarItem(produto, qtd);
            this.atualizarBadgeCarrinho();
            this.showToast(`${qtd}x ${produto.nome} adicionado ao carrinho`, 'success');
            return true;
          }
        }
      ]
    });

    await alert.present();
  }

  abrirMenu() {
    this.menuCtrl.open('main-menu');
  }

  verCarrinho() {
    this.router.navigate(['/carrinho']);
  }

  async logout() {
    const alert = await this.alertCtrl.create({
      header: 'Confirmar',
      message: 'Deseja realmente sair?',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Sair',
          role: 'destructive',
          handler: async () => {
            const loader = await this.loadingCtrl.create({
              message: 'Saindo...',
              duration: 1000
            });
            await loader.present();
            
            this.auth.logout();
            this.carrinhoService.limparCarrinho();
            
            await loader.dismiss();
            this.router.navigate(['/login']);
            this.showToast('Logout realizado com sucesso', 'success');
          }
        }
      ]
    });

    await alert.present();
  }

  async showToast(msg: string, color: 'success' | 'danger' | 'warning' = 'danger') {
    const toast = await this.toastCtrl.create({
      message: msg,
      duration: 2000,
      position: 'bottom',
      color: color
    });
    toast.present();
  }
}