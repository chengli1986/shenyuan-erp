// frontend/src/services/projectFile.ts
/**
 * 项目文件相关的API调用服务
 */

import axios from 'axios';
import { 
  ProjectFile, 
  ProjectFileListResponse, 
  FileUploadResult,
  FileSystemConfig,
  FileType
} from '../types/projectFile';
import { API_URL } from '../config/api';

// 创建axios实例
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 文件上传需要更长的超时时间
});

export class ProjectFileService {
  
  /**
   * 获取项目文件列表
   */
  static async getProjectFiles(
    projectId: number,
    fileType?: FileType
  ): Promise<ProjectFileListResponse> {
    const params: any = {};
    if (fileType) params.file_type = fileType;
    
    const response = await api.get<ProjectFileListResponse>(
      `/projects/${projectId}/files`,
      { params }
    );
    return response.data;
  }

  /**
   * 上传项目文件
   */
  static async uploadFile(
    projectId: number,
    file: File,
    fileType: FileType,
    description?: string,
    uploadedBy: string = '当前用户',
    onProgress?: (percent: number) => void
  ): Promise<FileUploadResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    formData.append('uploaded_by', uploadedBy);
    if (description) {
      formData.append('description', description);
    }

    const response = await api.post<FileUploadResult>(
      `/projects/${projectId}/files/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(percent);
          }
        },
      }
    );
    return response.data;
  }

  /**
   * 带重试机制的上传方法
   */
  static async uploadFileWithRetry(
    projectId: number,
    file: File,
    fileType: FileType,
    description?: string,
    uploadedBy: string = '当前用户',
    onProgress?: (percent: number) => void,
    maxRetries: number = 3
  ): Promise<FileUploadResult> {
    let lastError: any;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await this.uploadFile(projectId, file, fileType, description, uploadedBy, onProgress);
      } catch (error: any) {
        lastError = error;
        if (attempt < maxRetries) {
          console.warn(`上传失败，正在重试... (${attempt}/${maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // 递增延迟
        }
      }
    }
    
    throw lastError;
  }

  /**
   * 批量上传文件
   */
  static async uploadMultipleFiles(
    projectId: number,
    files: Array<{file: File, fileType: FileType, description?: string}>,
    uploadedBy: string = '当前用户',
    onProgress?: (fileIndex: number, percent: number) => void,
    onFileComplete?: (fileIndex: number, result: FileUploadResult) => void
  ): Promise<FileUploadResult[]> {
    const results: FileUploadResult[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const { file, fileType, description } = files[i];
      try {
        const result = await this.uploadFile(
          projectId, 
          file, 
          fileType, 
          description, 
          uploadedBy,
          (percent) => onProgress?.(i, percent)
        );
        results.push(result);
        onFileComplete?.(i, result);
      } catch (error: any) {
        const errorResult: FileUploadResult = {
          success: false,
          message: `文件 ${file.name} 上传失败: ${error.response?.data?.detail || error.message}`
        };
        results.push(errorResult);
        onFileComplete?.(i, errorResult);
      }
    }
    
    return results;
  }

  /**
   * 下载项目文件
   */
  static async downloadFile(
    projectId: number,
    fileId: number,
    fileName: string
  ): Promise<void> {
    const response = await api.get(
      `/projects/${projectId}/files/${fileId}/download`,
      {
        responseType: 'blob',
      }
    );

    // 创建下载链接
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * 批量下载文件
   */
  static async downloadMultipleFiles(
    projectId: number,
    files: ProjectFile[]
  ): Promise<void> {
    for (const file of files) {
      try {
        await this.downloadFile(projectId, file.id, file.file_name);
        // 添加小延迟避免浏览器阻止多个下载
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error(`下载文件 ${file.file_name} 失败:`, error);
      }
    }
  }

  /**
   * 删除项目文件
   */
  static async deleteFile(
    projectId: number,
    fileId: number
  ): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(
      `/projects/${projectId}/files/${fileId}`
    );
    return response.data;
  }

  /**
   * 批量删除文件
   */
  static async deleteMultipleFiles(
    projectId: number,
    fileIds: number[]
  ): Promise<{success: number, failed: number, errors: string[]}> {
    let success = 0;
    let failed = 0;
    const errors: string[] = [];

    for (const fileId of fileIds) {
      try {
        await this.deleteFile(projectId, fileId);
        success++;
      } catch (error: any) {
        failed++;
        errors.push(error.response?.data?.detail || error.message);
      }
    }

    return { success, failed, errors };
  }

  /**
   * 获取文件系统配置
   */
  static async getFileSystemConfig(): Promise<FileSystemConfig> {
    const response = await api.get<FileSystemConfig>('projects/file-types/');
    return response.data;
  }

  /**
   * 预览文件（用于支持的文件类型）
   */
  static getFilePreviewUrl(
    projectId: number,
    fileId: number
  ): string {
    return `${api.defaults.baseURL}/projects/${projectId}/files/${fileId}/preview`;
  }

  /**
   * 获取文件下载URL（不直接下载，用于预览等）
   */
  static getFileDownloadUrl(
    projectId: number,
    fileId: number
  ): string {
    return `${api.defaults.baseURL}/projects/${projectId}/files/${fileId}/download`;
  }

  /**
   * 检查文件是否存在
   */
  static async checkFileExists(
    projectId: number,
    fileId: number
  ): Promise<boolean> {
    try {
      await api.head(`/projects/${projectId}/files/${fileId}`);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 获取文件详细信息
   */
  static async getFileInfo(
    projectId: number,
    fileId: number
  ): Promise<ProjectFile> {
    const response = await api.get<ProjectFile>(
      `/projects/${projectId}/files/${fileId}`
    );
    return response.data;
  }

  /**
   * 更新文件信息（描述、文件类型等）
   */
  static async updateFileInfo(
    projectId: number,
    fileId: number,
    updates: Partial<Pick<ProjectFile, 'description' | 'file_type'>>
  ): Promise<ProjectFile> {
    const response = await api.patch<ProjectFile>(
      `/projects/${projectId}/files/${fileId}`,
      updates
    );
    return response.data;
  }
}

export default ProjectFileService;