import { Component, OnInit } from '@angular/core';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { AuthService } from 'src/app/auth/auth.service';
import { Router } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-perfil',
  templateUrl: './perfil.page.html',
  styleUrls: ['./perfil.page.scss'],
  imports: [IonicModule, CommonModule],
})
export class PerfilPage implements OnInit {
  user: any = null;
  carregando = true;

  constructor(
    private api: ApiService,
    private auth: AuthService,
    private toastCtrl: ToastController,
    private loadingCtrl: LoadingController,
    private router: Router
  ) {}

  async ngOnInit() {
    this.loadUser();
  }

  loadUser() {
    const u = this.auth.getUser();

    if (!u) {
      this.carregando = false;
      return;
    }

    this.user = u;
    this.carregando = false;
  }

  async logout() {
    const loader = await this.loadingCtrl.create({
      message: 'Saindo...',
      spinner: 'crescent',
      duration: 1200,
    });
    loader.present();

    this.auth.logout();
    this.router.navigate(['/login']);
  }
}