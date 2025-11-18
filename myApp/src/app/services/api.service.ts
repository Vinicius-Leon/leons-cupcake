import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  private getHeaders(): { headers: HttpHeaders } {
    const token = localStorage.getItem('access_token');
    const headers: any = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return { headers: new HttpHeaders(headers) };
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Ocorreu um erro desconhecido';
    
    if (error.error instanceof ErrorEvent) {
      // Erro do lado do cliente
      errorMessage = `Erro: ${error.error.message}`;
    } else {
      // Erro do lado do servidor
      errorMessage = error.error?.erro || error.error?.mensagem || error.message;
    }
    
    console.error('Erro na requisição:', error);
    return throwError(() => ({ erro: errorMessage, status: error.status }));
  }

  login(data: { email: string; senha: string }): Observable<any> {
    console.log('API Service - Enviando login para:', `${this.api}/auth/login`);
    console.log('API Service - Dados:', { email: data.email, senha: '***' });
    
    return this.http.post(`${this.api}/auth/login`, data).pipe(
      tap((response: any) => {
        console.log('API Service - Resposta recebida:', response);
      }),
      catchError((error) => {
        console.error('API Service - Erro no login:', error);
        return this.handleError(error);
      })
    );
  }

  registrar(data: any): Observable<any> {
    return this.http.post(`${this.api}/auth/register`, data)
      .pipe(catchError(this.handleError));
  }

  getUsuarioLogado(): Observable<any> {
    return this.http.get(`${this.api}/auth/me`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  refreshToken(): Observable<any> {
    return this.http.post(`${this.api}/auth/refresh`, {}, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  listarProdutos(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/produtos`)
      .pipe(catchError(this.handleError));
  }

  buscarProduto(id: number): Observable<any> {
    return this.http.get(`${this.api}/produtos/${id}`)
      .pipe(catchError(this.handleError));
  }

  criarProduto(data: any): Observable<any> {
    return this.http.post(`${this.api}/produtos`, data, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  atualizarProduto(id: number, data: any): Observable<any> {
    return this.http.put(`${this.api}/produtos/${id}`, data, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  removerProduto(id: number): Observable<any> {
    return this.http.delete(`${this.api}/produtos/${id}`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  listarCategorias(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/categorias`)
      .pipe(catchError(this.handleError));
  }

  criarCategoria(data: any): Observable<any> {
    return this.http.post(`${this.api}/categorias`, data, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  criarPedido(data: any): Observable<any> {
    return this.http.post(`${this.api}/pedidos`, data, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  listarPedidos(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/pedidos`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  listarMeusPedidos(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/pedidos/meus-pedidos`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  buscarPedido(id: number): Observable<any> {
    return this.http.get(`${this.api}/pedidos/${id}`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  atualizarStatusPedido(id: number, status: string): Observable<any> {
    return this.http.put(`${this.api}/pedidos/${id}/status`, { status }, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  cancelarPedido(id: number): Observable<any> {
    return this.http.delete(`${this.api}/pedidos/${id}`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  listarEntregas(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/entregas`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  criarEntrega(data: any): Observable<any> {
    return this.http.post(`${this.api}/entregas`, data, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  atualizarEntrega(id: number, data: any): Observable<any> {
    return this.http.put(`${this.api}/entregas/${id}`, data, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  listarUsuarios(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/usuarios`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  buscarUsuario(id: number): Observable<any> {
    return this.http.get(`${this.api}/usuarios/${id}`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  atualizarUsuario(id: number, data: any): Observable<any> {
    return this.http.put(`${this.api}/usuarios/${id}`, data, this.getHeaders())
      .pipe(catchError(this.handleError));
  }

  removerUsuario(id: number): Observable<any> {
    return this.http.delete(`${this.api}/usuarios/${id}`, this.getHeaders())
      .pipe(catchError(this.handleError));
  }
}