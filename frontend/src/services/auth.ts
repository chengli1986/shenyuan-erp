/**
 * 认证服务
 */

import api from './api';

export interface User {
  id: number;
  username: string;
  name: string;
  role: string;
  department?: string;
  is_active: boolean;
  can_view_price: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export class AuthService {
  private static instance: AuthService;
  private currentUser: User | null = null;

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  constructor() {
    // 从localStorage恢复用户信息
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      this.currentUser = JSON.parse(savedUser);
    }
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token, user } = response.data;
    
    // 保存token和用户信息
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('currentUser', JSON.stringify(user));
    this.currentUser = user;

    // 设置API默认认证header
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    return response.data;
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('currentUser');
    this.currentUser = null;
    delete api.defaults.headers.common['Authorization'];
  }

  getCurrentUser(): User | null {
    return this.currentUser;
  }

  isLoggedIn(): boolean {
    const token = localStorage.getItem('access_token');
    return token !== null && this.currentUser !== null;
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  async refreshUserInfo(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    this.currentUser = response.data;
    localStorage.setItem('currentUser', JSON.stringify(response.data));
    return response.data;
  }
}

export const authService = AuthService.getInstance();