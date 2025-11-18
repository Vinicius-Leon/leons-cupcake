import { Component, OnInit } from '@angular/core';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  standalone: true,
  selector: 'app-admin',
  templateUrl: './admin.page.html',
  styleUrls: ['./admin.page.scss'],
  imports: [IonicModule, CommonModule]
})
export class AdminPage implements OnInit {
  produtos: any[] = [];
  carregando = true;

  constructor(private api: ApiService, private toastCtrl: ToastController, private loadingCtrl: LoadingController) {}

  ngOnInit() {
    this.load();
  }

  async load() {
    const loader = await this.loadingCtrl.create({
      message: 'Carregando produtos...',
      spinner: 'crescent'
    });
    loader.present();

    this.api.listarProdutos().subscribe({
      next: (r) => {
        this.produtos = r;
        this.carregando = false;
        loader.dismiss();
      },
      error: async (e) => {
        this.carregando = false;
        loader.dismiss();
        this.showToast('Erro ao carregar produtos');
      }
    });
  }

  async deletar(id: number) {
    const confirmed = window.confirm('Tem certeza que deseja remover este produto?');
    if (!confirmed) return;

    const loader = await this.loadingCtrl.create({
      message: 'Removendo produto...',
      spinner: 'crescent'
    });
    loader.present();

    this.api.removerProduto(id).subscribe({
      next: async () => {
        this.load();
        await loader.dismiss();
        this.showToast('Produto removido com sucesso');
      },
      error: async () => {
        await loader.dismiss();
        this.showToast('Erro ao remover produto');
      }
    });
  }

  async showToast(msg: string) {
    const toast = await this.toastCtrl.create({
      message: msg,
      duration: 2000,
      color: 'dark',
      position: 'bottom'
    });
    toast.present();
  }
}