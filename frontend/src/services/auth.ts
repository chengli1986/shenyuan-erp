/**
 * 认证服务
 * Token通过HttpOnly Cookie管理，前端不再直接操作token
 * localStorage仅保存非敏感的用户信息用于UI显示
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
    // 从localStorage恢复用户基本信息（非敏感，仅用于UI显示）
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

    const { user } = response.data;

    // 仅保存用户基本信息用于UI显示（token已通过HttpOnly Cookie设置）
    localStorage.setItem('currentUser', JSON.stringify(user));
    this.currentUser = user;

    return response.data;
  }

  async logout(): Promise<void> {
    try {
      // 调用后端登出接口清除HttpOnly Cookie
      await api.post('/auth/logout');
    } catch {
      // 即使后端调用失败，也要清除前端状态
    }
    localStorage.removeItem('currentUser');
    this.currentUser = null;
  }

  getCurrentUser(): User | null {
    return this.currentUser;
  }

  isLoggedIn(): boolean {
    // 通过用户信息判断是否已登录（token由cookie自动管理）
    return this.currentUser !== null;
  }

  async refreshUserInfo(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    this.currentUser = response.data;
    localStorage.setItem('currentUser', JSON.stringify(response.data));
    return response.data;
  }

  /**
   * 验证当前会话是否有效（HttpOnly Cookie是否仍然有效）
   * 在应用启动时调用，如果cookie过期则清除前端状态
   * @returns true 如果会话有效，false 如果无效（已自动清除状态）
   */
  async verifySession(): Promise<boolean> {
    // 如果localStorage中没有用户信息，无需验证
    if (!this.currentUser) {
      return false;
    }

    try {
      // _skipAuthRedirect 避免触发api.ts中的全局401拦截器导致重复处理
      const response = await api.get<User>('/auth/me', {
        _skipAuthRedirect: true,
      } as any);
      // 会话有效，顺便刷新用户信息
      this.currentUser = response.data;
      localStorage.setItem('currentUser', JSON.stringify(response.data));
      return true;
    } catch {
      // 401或其他错误表示会话无效，清除前端状态
      this.clearSession();
      return false;
    }
  }

  /**
   * 清除前端会话状态（不调用后端登出接口）
   */
  clearSession(): void {
    localStorage.removeItem('currentUser');
    this.currentUser = null;
  }
}

export const authService = AuthService.getInstance();
