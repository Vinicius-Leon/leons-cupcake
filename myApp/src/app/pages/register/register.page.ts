import { Component } from '@angular/core';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Router, RouterLink } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-register',
  templateUrl: './register.page.html',
  styleUrls: ['./register.page.scss'],
  imports: [IonicModule, CommonModule, FormsModule, RouterLink]
})
export class RegisterPage {
  nome = '';
  sobrenome = '';
  email = '';
  senha = '';
  confirmar = '';
  telefone = '';
  cpf = '';
  carregando = false;
  showPassword = false;
  showConfirmPassword = false;

  constructor(
    private api: ApiService,
    private router: Router,
    private toastCtrl: ToastController,
    private loadingCtrl: LoadingController
  ) {
    console.log('RegisterPage inicializado');
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPassword() {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  validarCampos(): { valido: boolean; erro?: string } {
    console.log('🔍 Validando campos...');
    
    // Validar nome
    const nomeTrimmed = this.nome.trim();
    if (!nomeTrimmed) {
      return { valido: false, erro: 'Nome é obrigatório' };
    }
    if (nomeTrimmed.length < 2) {
      return { valido: false, erro: 'Nome deve ter pelo menos 2 caracteres' };
    }

    // Validar email
    const emailTrimmed = this.email.trim().toLowerCase();
    if (!emailTrimmed) {
      return { valido: false, erro: 'Email é obrigatório' };
    }
    if (!this.isValidEmail(emailTrimmed)) {
      return { valido: false, erro: 'Email inválido' };
    }

    // Validar senha
    const senhaTrimmed = this.senha.trim();
    if (!senhaTrimmed) {
      return { valido: false, erro: 'Senha é obrigatória' };
    }
    if (senhaTrimmed.length < 6) {
      return { valido: false, erro: 'Senha deve ter pelo menos 6 caracteres' };
    }

    // Validar confirmação
    const confirmarTrimmed = this.confirmar.trim();
    if (!confirmarTrimmed) {
      return { valido: false, erro: 'Confirme sua senha' };
    }
    if (senhaTrimmed !== confirmarTrimmed) {
      return { valido: false, erro: 'As senhas não coincidem' };
    }

    // Validar CPF 
    if (!this.cpf.trim()) {
      return { valido: false, erro: 'CPF é obrigatório' };
    }
    if (!this.isValidCPF(this.cpf)) {
      return { valido: false, erro: 'CPF inválido' };
    }

    // Validar telefone 
    if (!this.telefone.trim()) {
      return { valido: false, erro: 'Telefone é obrigatório' };
    }
    const telLimpo = this.telefone.replace(/\D/g, '');
    if (telLimpo.length < 10) {
      return { valido: false, erro: 'Telefone inválido' };
    }

    console.log('✅ Campos validados com sucesso');
    return { valido: true };
  }

  async register() {
    console.log('\n' + '='.repeat(60));
    console.log('📝 INICIANDO REGISTRO');
    console.log('='.repeat(60));

    // Validar campos
    const validacao = this.validarCampos();
    if (!validacao.valido) {
      console.log(`❌ Validação falhou: ${validacao.erro}`);
      await this.showToast(validacao.erro!, 'warning');
      return;
    }

    // Mostrar loading
    this.carregando = true;
    const loader = await this.loadingCtrl.create({
      message: 'Criando conta...',
      spinner: 'crescent',
      backdropDismiss: false
    });
    await loader.present();

    // Preparar dados
    const dados: any = {
      nome: this.nome.trim(),
      email: this.email.trim().toLowerCase(),
      senha: this.senha.trim()
    };

    // Campos opcionais
    if (this.sobrenome.trim()) {
      dados.sobrenome = this.sobrenome.trim();
    }

    // Adicionar campos opcionais
    if (this.cpf.trim()) {
      dados.cpf = this.cpf.replace(/\D/g, '');
    }

    if (this.telefone.trim()) {
      dados.telefone = this.telefone.replace(/\D/g, '');
    }

    console.log('📤 Enviando dados:', { 
      ...dados, 
      senha: '***' 
    });

    // Fazer requisição
    this.api.registrar(dados).subscribe({
      next: async (response) => {
        console.log('✅ Resposta recebida:', response);
        
        await loader.dismiss();
        this.carregando = false;
        
        await this.showToast(
          'Conta criada com sucesso! Faça login para continuar.',
          'success'
        );
        
        // Limpar formulário
        this.limparFormulario();
        
        // Redirecionar após 1.5s
        setTimeout(() => {
          console.log('🔄 Redirecionando para login...');
          this.router.navigate(['/login']);
        }, 1500);
      },
      error: async (err) => {
        console.error('❌ Erro no registro:', err);
        
        await loader.dismiss();
        this.carregando = false;
        
        // Extrair mensagem de erro
        let mensagem = 'Erro ao criar conta';
        
        if (err.erro) {
          mensagem = err.erro;
        } else if (err.error?.erro) {
          mensagem = err.error.erro;
        } else if (err.error?.mensagem) {
          mensagem = err.error.mensagem;
        } else if (err.message) {
          mensagem = err.message;
        }
        
        console.log('📢 Exibindo erro:', mensagem);
        await this.showToast(mensagem, 'danger');
      }
    });
  }

  isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  isValidCPF(cpf: string): boolean {
    // Remove caracteres não numéricos
    cpf = cpf.replace(/\D/g, '');
    
    // Validação básica de tamanho
    if (cpf.length !== 11) {
      return false;
    }
    
    // Validação de CPFs conhecidos como inválidos
    const cpfsInvalidos = [
      '00000000000', '11111111111', '22222222222',
      '33333333333', '44444444444', '55555555555',
      '66666666666', '77777777777', '88888888888',
      '99999999999'
    ];
    
    return !cpfsInvalidos.includes(cpf);
  }

  formatarCPF() {
    let cpf = this.cpf.replace(/\D/g, '');
    
    if (cpf.length <= 11) {
      cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
      cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
      cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      this.cpf = cpf;
    }
  }

  formatarTelefone() {
    let tel = this.telefone.replace(/\D/g, '');
    
    if (tel.length <= 11) {
      tel = tel.replace(/^(\d{2})(\d)/g, '($1) $2');
      tel = tel.replace(/(\d)(\d{4})$/, '$1-$2');
      this.telefone = tel;
    }
  }

  limparFormulario() {
    console.log('🧹 Limpando formulário');
    this.nome = '';
    this.email = '';
    this.senha = '';
    this.confirmar = '';
    this.telefone = '';
    this.cpf = '';
    this.showPassword = false;
    this.showConfirmPassword = false;
  }

  async showToast(
    msg: string, 
    color: 'success' | 'danger' | 'warning' = 'danger'
  ) {
    const toast = await this.toastCtrl.create({
      message: msg,
      duration: color === 'success' ? 3000 : 2500,
      position: 'bottom',
      color: color,
      buttons: [
        {
          text: 'OK',
          role: 'cancel'
        }
      ]
    });
    
    await toast.present();
    console.log(`🍞 Toast exibido (${color}): ${msg}`);
  }

  goToLogin() {
    console.log('🔄 Navegando para login');
    this.router.navigate(['/login']);
  }
}