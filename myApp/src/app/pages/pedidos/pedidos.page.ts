import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';  // Adicionar RouterModule
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  standalone: true,
  selector: 'app-pedidos',
  templateUrl: './pedidos.page.html',
  styleUrls: ['./pedidos.page.scss'],
  imports: [IonicModule, CommonModule, RouterModule]  // Incluir RouterModule aqui
})
export class PedidosPage implements OnInit {
  pedidos: any[] = [];
  carregando = true;

  constructor(
    private api: ApiService,
    private toastCtrl: ToastController,
    private loadingCtrl: LoadingController
  ) {}

  ngOnInit() {
    this.loadPedidos();
  }

  async loadPedidos() {
    this.carregando = true;

    const loader = await this.loadingCtrl.create({
      message: 'Carregando pedidos...',
      spinner: 'crescent',
    });
    loader.present();

    this.api.listarPedidos().subscribe({
      next: async (res) => {
        this.pedidos = res;
        this.carregando = false;
        loader.dismiss();
      },
      error: async (err) => {
        this.carregando = false;
        loader.dismiss();
        this.showToast('Erro ao carregar pedidos.');
        console.error(err);
      },
    });
  }

  async showToast(msg: string) {
    const t = await this.toastCtrl.create({
      message: msg,
      duration: 2000,
      position: 'bottom',
      color: 'danger',
    });

    t.present();
  }
}