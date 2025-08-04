// frontend/src/services/project.ts
/**
 * 项目相关的API调用服务
 * 负责与后端API通信
 */

import { Project, ProjectCreate, ProjectUpdate, ProjectListResponse } from '../types/project';
import api from './api';

// 项目API服务类
export class ProjectService {
  
  /**
   * 获取项目列表
   * @param page 页码
   * @param size 每页数量  
   * @param search 搜索关键词
   * @param status 状态筛选
   */
  static async getProjects(
    page: number = 1,
    size: number = 10, 
    search?: string,
    status?: string
  ): Promise<ProjectListResponse> {
    const params: any = { page, size };
    if (search) params.search = search;
    if (status) params.status = status;
    
    const response = await api.get<ProjectListResponse>('projects/', { params });
    return response.data;
  }

  /**
   * 获取单个项目详情
   * @param id 项目ID
   */
  static async getProject(id: number): Promise<Project> {
    const response = await api.get<Project>(`projects/${id}/`);
    return response.data;
  }

  /**
   * 创建新项目
   * @param projectData 项目数据
   */
  static async createProject(projectData: ProjectCreate): Promise<Project> {
    const response = await api.post<Project>('projects/', projectData);
    return response.data;
  }

  /**
   * 更新项目
   * @param id 项目ID
   * @param projectData 更新数据
   */
  static async updateProject(id: number, projectData: ProjectUpdate): Promise<Project> {
    const response = await api.put<Project>(`projects/${id}/`, projectData);
    return response.data;
  }

  /**
   * 删除项目
   * @param id 项目ID
   */
  static async deleteProject(id: number): Promise<void> {
    await api.delete(`projects/${id}/`);
  }
}

// 导出默认实例
export default ProjectService;