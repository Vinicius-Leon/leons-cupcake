import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth/auth.service';

// Functional Guard
const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const isLoggedIn = authService.isLoggedIn();
  console.log('Guard - Verificando autenticação:', isLoggedIn);
  
  if (!isLoggedIn) {
    console.log('Guard - Redirecionando para login');
    return router.createUrlTree(['/login']);
  }
  
  return true;
};

export const routes: Routes = [
  { 
    path: '', 
    redirectTo: 'login', 
    pathMatch: 'full' 
  },
  { 
    path: 'login', 
    loadComponent: () => import('./pages/login/login.page').then(m => m.LoginPage) 
  },
  { 
    path: 'register', 
    loadComponent: () => import('./pages/register/register.page').then(m => m.RegisterPage) 
  },
  { 
    path: 'home', 
    loadComponent: () => import('./pages/home/home.page').then(m => m.HomePage),
    canActivate: [authGuard]
  },
  { 
    path: 'carrinho', 
    loadComponent: () => import('./pages/carrinho/carrinho.page').then(m => m.CarrinhoPage),
    canActivate: [authGuard]
  },
  { 
    path: 'pedidos', 
    loadComponent: () => import('./pages/pedidos/pedidos.page').then(m => m.PedidosPage),
    canActivate: [authGuard]
  },
  { 
    path: 'perfil', 
    loadComponent: () => import('./pages/perfil/perfil.page').then(m => m.PerfilPage),
    canActivate: [authGuard]
  },
  { 
    path: 'entrega', 
    loadComponent: () => import('./pages/entrega/entrega.page').then(m => m.EntregaPage),
    canActivate: [authGuard]
  },
  { 
    path: 'admin', 
    loadComponent: () => import('./pages/admin/admin.page').then(m => m.AdminPage),
    canActivate: [authGuard]
  }
];