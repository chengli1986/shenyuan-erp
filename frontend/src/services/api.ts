/**
 * 通用API服务配置
 */

import axios from 'axios';
import { API_URL } from '../config/api';

// 创建axios实例，配置基础URL
const api = axios.create({
  baseURL: API_URL,
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