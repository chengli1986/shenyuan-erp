/**
 * 测试结果相关API服务
 */

import api from './api';
import { 
  TestRunListResponse, 
  TestRunDetailResponse,
  TestStatistics,
  LatestTestStatus
} from '../types/test';

export const testService = {
  /**
   * 获取测试运行列表
   */
  getTestRuns: async (params: {
    page?: number;
    size?: number;
    run_type?: string;
    status?: string;
    days?: number;
  }): Promise<TestRunListResponse> => {
    const response = await api.get('tests/runs/', { params });
    return response.data;
  },

  /**
   * 获取测试运行详情
   */
  getTestRunDetail: async (runId: string): Promise<TestRunDetailResponse> => {
    const response = await api.get(`tests/runs/${runId}/`);
    return response.data;
  },

  /**
   * 手动触发测试运行
   */
  triggerTestRun: async (testType: 'all' | 'unit' | 'integration'): Promise<{
    message: string;
    run_id: string;
    test_type: string;
  }> => {
    // 使用修复后的原始trigger端点
    const response = await api.post('/tests/runs/trigger', null, {
      params: { test_type: testType }
    });
    return response.data;
  },

  /**
   * 获取测试统计信息
   */
  getTestStatistics: async (days: number = 30): Promise<TestStatistics> => {
    const response = await api.get('tests/statistics/', {
      params: { days }
    });
    return response.data;
  },

  /**
   * 获取最新测试状态
   */
  getLatestTestStatus: async (): Promise<LatestTestStatus> => {
    const response = await api.get('tests/latest/');
    return response.data;
  }
};