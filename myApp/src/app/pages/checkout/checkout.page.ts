import { Component } from '@angular/core';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Router } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-checkout',
  templateUrl: './checkout.page.html',
  styleUrls: ['./checkout.page.scss'],
  imports: [IonicModule, CommonModule, FormsModule]
})
export class CheckoutPage {
  endereco = '';
  metodo = 'pix';
  carregando = false;

  constructor(
    private api: ApiService,
    private router: Router,
    private toastCtrl: ToastController,
    private loadingCtrl: LoadingController
  ) {}

  async pagar() {
    if (!this.endereco || !this.metodo) {
      this.showToast('Preencha todos os campos!');
      return;
    }

    const loader = await this.loadingCtrl.create({
      message: 'Finalizando pedido...',
      spinner: 'crescent'
    });
    loader.present();

    const payload = { 
      id_usuario: 1, 
      itens: [], 
      endereco: this.endereco, 
      metodo: this.metodo 
    };

    this.api.criarPedido(payload).subscribe({
      next: async () => {
        await loader.dismiss();
        this.showToast('Pedido criado com sucesso!');
        this.router.navigateByUrl('/pedidos');
      },
      error: async (e) => {
        await loader.dismiss();
        this.showToast(e.error?.erro || 'Erro ao criar pedido');
      }
    });
  }

  async showToast(msg: string) {
    const toast = await this.toastCtrl.create({
      message: msg,
      duration: 2000,
      color: 'danger',
      position: 'bottom'
    });
    toast.present();
  }
}