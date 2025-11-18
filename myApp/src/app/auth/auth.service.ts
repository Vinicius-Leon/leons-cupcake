import { Injectable } from '@angular/core';

export interface User {
  id_usuario: number;
  nome: string;
  email: string;
  tipo_usuario: 'cliente' | 'admin' | 'entregador';
  cpf?: string;
  telefone?: string;
  ativo: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly USER_KEY = 'user';

  constructor() {
    console.log('AuthService inicializado');
  }

  saveToken(token: string): void {
    if (token) {
      console.log('AuthService - Salvando token:', token.substring(0, 50) + '...');
      localStorage.setItem(this.TOKEN_KEY, token);
      console.log('AuthService - Token salvo no localStorage');
    } else {
      console.error('AuthService - Tentativa de salvar token vazio');
    }
  }

  getToken(): string | null {
    const token = localStorage.getItem(this.TOKEN_KEY);
    console.log('AuthService - getToken:', token ? 'Token encontrado' : 'Sem token');
    return token;
  }

  removeToken(): void {
    console.log('AuthService - Removendo token');
    localStorage.removeItem(this.TOKEN_KEY);
  }

  isLoggedIn(): boolean {
    const token = this.getToken();
    console.log('AuthService - isLoggedIn - Token existe?', !!token);
    
    if (!token) {
      console.log('AuthService - isLoggedIn - FALSE (sem token)');
      return false;
    }

    try {
      const payload = this.decodeToken(token);
      console.log('AuthService - Token decodificado:', payload);
      
      if (!payload || !payload.exp) {
        console.log('AuthService - isLoggedIn - FALSE (payload inválido)');
        return false;
      }
      
      const now = Date.now() / 1000;
      const isValid = payload.exp > now;
      
      console.log('AuthService - Expira em:', new Date(payload.exp * 1000));
      console.log('AuthService - Agora:', new Date(now * 1000));
      console.log('AuthService - isLoggedIn -', isValid ? 'TRUE' : 'FALSE (expirado)');
      
      return isValid;
    } catch (error) {
      console.error('AuthService - Erro ao verificar token:', error);
      return false;
    }
  }

  private decodeToken(token: string): any {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('AuthService - Erro ao decodificar token:', error);
      return null;
    }
  }

  saveUser(user: User): void {
    if (user) {
      console.log('AuthService - Salvando usuário:', user.nome);
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      console.log('AuthService - Usuário salvo no localStorage');
    } else {
      console.error('AuthService - Tentativa de salvar usuário vazio');
    }
  }

  getUser(): User | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        console.log('AuthService - getUser:', user.nome);
        return user;
      } catch (error) {
        console.error('AuthService - Erro ao parsear usuário:', error);
        return null;
      }
    }
    console.log('AuthService - getUser: Sem usuário');
    return null;
  }

  removeUser(): void {
    console.log('AuthService - Removendo usuário');
    localStorage.removeItem(this.USER_KEY);
  }

  getUserType(): string | null {
    const user = this.getUser();
    return user ? user.tipo_usuario : null;
  }

  isAdmin(): boolean {
    return this.getUserType() === 'admin';
  }

  isEntregador(): boolean {
    return this.getUserType() === 'entregador';
  }

  isCliente(): boolean {
    return this.getUserType() === 'cliente';
  }

  logout(): void {
    console.log('AuthService - Fazendo logout');
    this.removeToken();
    this.removeUser();
    this.clearAllData();
  }

  private clearAllData(): void {
    const keysToRemove = ['carrinho', 'favoritos'];
    keysToRemove.forEach(key => {
      console.log('AuthService - Removendo', key);
      localStorage.removeItem(key);
    });
  }
}