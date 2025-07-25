// frontend/src/types/project.ts
/**
 * 项目相关的TypeScript类型定义
 * 这些类型要和后端保持一致
 */

export enum ProjectStatus {
  PLANNING = 'planning',
  IN_PROGRESS = 'in_progress', 
  COMPLETED = 'completed',
  SUSPENDED = 'suspended'
}

// 项目基础信息接口
export interface Project {
  id: number;
  project_code: string;
  project_name: string;
  contract_amount?: number;
  start_date?: string;
  end_date?: string;
  project_manager?: string;
  status?: ProjectStatus;
  description?: string;
  overall_progress?: number;
  purchase_progress?: number;
  created_at: string;
  updated_at?: string;
}

// 创建项目时的数据
export interface ProjectCreate {
  project_code: string;
  project_name: string;
  contract_amount?: number;
  start_date?: string;
  end_date?: string;
  project_manager?: string;
  status?: ProjectStatus;
  description?: string;
}

// 更新项目时的数据
export interface ProjectUpdate {
  project_code?: string;
  project_name?: string;
  contract_amount?: number;
  start_date?: string;
  end_date?: string;
  project_manager?: string;
  status?: ProjectStatus;
  description?: string;
  overall_progress?: number;
  purchase_progress?: number;
}

// API响应的项目列表
export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 状态显示配置
export const PROJECT_STATUS_CONFIG = {
  [ProjectStatus.PLANNING]: {
    text: '规划中',
    color: 'blue',
    icon: '📋'
  },
  [ProjectStatus.IN_PROGRESS]: {
    text: '进行中',
    color: 'green', 
    icon: '🚀'
  },
  [ProjectStatus.COMPLETED]: {
    text: '已完成',
    color: 'purple',
    icon: '✅'
  },
  [ProjectStatus.SUSPENDED]: {
    text: '暂停',
    color: 'orange',
    icon: '⏸️'
  }
};