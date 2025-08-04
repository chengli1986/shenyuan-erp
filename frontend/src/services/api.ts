/**
 * 通用API服务配置
 */

import axios from 'axios';
// 创建axios实例，使用相对路径通过代理（注意末尾斜杠）
const api = axios.create({
  baseURL: '/api/v1/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
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
    return Promise.reject(error);
  }
);

export default api;