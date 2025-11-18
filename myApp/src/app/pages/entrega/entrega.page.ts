import { Component, OnInit } from '@angular/core';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  standalone: true,
  selector: 'app-entrega',
  templateUrl: './entrega.page.html',
  styleUrls: ['./entrega.page.scss'],
  imports: [
    IonicModule,
    CommonModule,
    FormsModule
  ]
})
export class EntregaPage implements OnInit {

  entregas: any[] = [];
  carregando = true;

  constructor(
    private api: ApiService,
    private toastCtrl: ToastController,
    private loadingCtrl: LoadingController
  ) {}

  ngOnInit() {
    this.carregarEntregas();
  }

  async carregarEntregas(event?: any) {
    this.carregando = true;

    const loader = await this.loadingCtrl.create({
      message: 'Carregando entregas...',
      spinner: 'crescent'
    });
    loader.present();

    this.api.listarEntregas().subscribe({
      next: (dados) => {
        this.entregas = dados;
        this.carregando = false;
        loader.dismiss();
        if (event) event.target.complete();
      },
      error: async () => {
        this.carregando = false;
        loader.dismiss();
        this.showToast('Erro ao carregar entregas');
        if (event) event.target.complete();
      }
    });
  }

  verDetalhes(entrega: any) {
    this.showToast(`Entrega #${entrega.id}\nStatus: ${entrega.status}`);
  }

  async atualizarStatus(entrega: any) {
    const novoStatus =
      entrega.status === 'A caminho'
        ? 'Finalizada'
        : 'A caminho';

    const loader = await this.loadingCtrl.create({
      message: 'Atualizando status...',
      spinner: 'crescent'
    });
    loader.present();

    this.api.atualizarEntrega(entrega.id, { status: novoStatus }).subscribe({
      next: async () => {
        entrega.status = novoStatus;
        loader.dismiss();
        this.showToast('Status atualizado com sucesso');
      },
      error: async () => {
        loader.dismiss();
        this.showToast('Erro ao atualizar status');
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