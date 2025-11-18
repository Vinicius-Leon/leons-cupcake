import { Injectable } from '@angular/core';
import { Router, UrlTree } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean | UrlTree {
    console.log('AuthGuard - Verificando autenticação...');
    const isLoggedIn = this.auth.isLoggedIn();
    console.log('AuthGuard - Está logado?', isLoggedIn);
    
    if (!isLoggedIn) {
      console.log('AuthGuard - Redirecionando para /login');
      return this.router.createUrlTree(['/login']);
    }
    
    console.log('AuthGuard - Acesso permitido');
    return true;
  }
}

export const authGuard = (route: any, state: any) => {
  const guard = new AuthGuard(
    new AuthService(),
    // @ts-ignore
    window['router']
  );
  return guard.canActivate();
};