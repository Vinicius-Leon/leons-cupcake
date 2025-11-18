import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from 'src/app/services/api.service';
import { AuthService } from 'src/app/auth/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';

@Component({
  standalone: true,
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  imports: [IonicModule, CommonModule, FormsModule, RouterLink]
})
export class LoginPage {
  email: string = '';
  senha: string = '';
  loading: boolean = false;
  showPassword: boolean = false;

  constructor(
    private api: ApiService,
    private auth: AuthService,
    private router: Router,
    private toastCtrl: ToastController,
    private loadingCtrl: LoadingController
  ) {}

  ionViewWillEnter() {
    // Se já estiver logado, redireciona para home
    if (this.auth.isLoggedIn()) {
      this.router.navigate(['/home'], { replaceUrl: true });
    }
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  async login() {
    // Limpa espaços e converte email para minúsculo
    const emailTrimmed = this.email.trim().toLowerCase();
    const senhaTrimmed = this.senha.trim();

    // Validações básicas
    if (!emailTrimmed || !senhaTrimmed) {
      this.showToast('Preencha e-mail e senha!', 'warning');
      return;
    }

    if (!this.isValidEmail(emailTrimmed)) {
      this.showToast('E-mail inválido!', 'warning');
      return;
    }

    this.loading = true;
    const loader = await this.loadingCtrl.create({
      message: 'Entrando...',
      spinner: 'crescent',
    });
    await loader.present();

    console.log('Tentando fazer login com:', emailTrimmed);

    this.api.login({ email: emailTrimmed, senha: senhaTrimmed }).subscribe({
      next: async (response) => {
        console.log('Resposta do login:', response);
        
        // Salva o token
        if (response.access_token) {
          this.auth.saveToken(response.access_token);
          console.log('Token salvo:', response.access_token);
        } else {
          console.error('Token não encontrado na resposta');
        }
        
        // Salva os dados do usuário
        if (response.user) {
          this.auth.saveUser(response.user);
          console.log('Usuário salvo:', response.user);
        } else {
          console.error('Dados do usuário não encontrados na resposta');
        }
        
        await loader.dismiss();
        this.loading = false;
        
        const userName = response.user?.nome || 'Usuário';
        await this.showToast(`Bem-vindo(a), ${userName}!`, 'success');
        
        // Aguarda um pouco antes de redirecionar
        setTimeout(() => {
          this.router.navigate(['/home'], { replaceUrl: true });
        }, 500);
      },
      error: async (err) => {
        console.error('Erro no login:', err);
        
        await loader.dismiss();
        this.loading = false;
        
        const mensagem = err.erro || err.error?.erro || 'E-mail ou senha incorretos';
        await this.showToast(mensagem, 'danger');
        
        // Limpa apenas a senha em caso de erro
        this.senha = '';
      },
    });
  }

  isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  async showToast(msg: string, color: 'success' | 'danger' | 'warning' = 'danger') {
    const t = await this.toastCtrl.create({
      message: msg,
      duration: 3000,
      position: 'bottom',
      color: color,
    });
    await t.present();
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }
}