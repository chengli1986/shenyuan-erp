/**
 * 通用API服务配置
 */

import axios from 'axios';

// 创建axios实例，使用相对路径通过代理
const api = axios.create({
  baseURL: '/api/v1/',
  timeout: 10000,
  withCredentials: true,  // 自动发送HttpOnly Cookie
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器（不再需要手动添加token，由cookie自动携带）
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 统一错误处理
    console.error('API请求错误:', error);

    // 401未授权，清除用户信息并跳转登录
    if (error.response?.status === 401) {
      localStorage.removeItem('currentUser');
      window.location.reload();
    }

    return Promise.reject(error);
  }
);

export default api;
