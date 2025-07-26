// frontend/src/types/projectFile.ts
/**
 * 项目文件相关的TypeScript类型定义
 */

export enum FileType {
  AWARD_NOTICE = 'award_notice',
  CONTRACT = 'contract', 
  ATTACHMENT = 'attachment',
  OTHER = 'other'
}

// 项目文件接口
export interface ProjectFile {
  id: number;
  project_id: number;
  file_name: string;
  file_type: FileType;
  file_size: number;
  file_extension: string;
  mime_type?: string;
  description?: string;
  uploaded_by: string;
  upload_time: string;
  created_at: string;
}

// 文件上传结果
export interface FileUploadResult {
  success: boolean;
  message: string;
  file_id?: number;
  file_info?: ProjectFile;
}

// 文件列表响应
export interface ProjectFileListResponse {
  items: ProjectFile[];
  total: number;
}

// 文件类型配置
export interface FileTypeConfig {
  value: string;
  label: string;
  icon: string;
  color: string;
  max_count: number;
  description: string;
}

// 文件系统配置
export interface FileSystemConfig {
  file_types: FileTypeConfig[];
  allowed_extensions: string[];
  max_file_size: number;
  max_file_size_mb: number;
}

// 批量上传文件项
export interface BatchUploadItem {
  file: File;
  fileType: FileType;
  description?: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

// 文件大小限制
export const FILE_SIZE_LIMITS = {
  PDF: 50 * 1024 * 1024, // 50MB
  IMAGE: 10 * 1024 * 1024, // 10MB
  DOCUMENT: 20 * 1024 * 1024, // 20MB
  DEFAULT: 50 * 1024 * 1024 // 50MB
};

// 允许的文件类型
export const ALLOWED_FILE_TYPES = {
  [FileType.AWARD_NOTICE]: ['.pdf', '.doc', '.docx'],
  [FileType.CONTRACT]: ['.pdf', '.doc', '.docx'],
  [FileType.ATTACHMENT]: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'],
  [FileType.OTHER]: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip', '.rar']
};

// 文件类型显示配置
export const FILE_TYPE_DISPLAY = {
  [FileType.AWARD_NOTICE]: {
    name: '中标通知书',
    icon: '📋',
    color: 'blue'
  },
  [FileType.CONTRACT]: {
    name: '合同文件',
    icon: '📄', 
    color: 'green'
  },
  [FileType.ATTACHMENT]: {
    name: '附件',
    icon: '📎',
    color: 'orange'
  },
  [FileType.OTHER]: {
    name: '其他文件',
    icon: '📁',
    color: 'gray'
  }
};

// 文件大小格式化
export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

// 获取文件图标
export const getFileIcon = (extension: string): string => {
  const ext = extension.toLowerCase();
  if (['.pdf'].includes(ext)) return '📕';
  if (['.doc', '.docx'].includes(ext)) return '📘';
  if (['.xls', '.xlsx'].includes(ext)) return '📗';
  if (['.ppt', '.pptx'].includes(ext)) return '📙';
  if (['.jpg', '.jpeg', '.png', '.gif', '.bmp'].includes(ext)) return '🖼️';
  if (['.zip', '.rar', '.7z'].includes(ext)) return '📦';
  if (['.txt'].includes(ext)) return '📝';
  return '📄';
};

// 验证文件类型和大小
export const validateFile = (file: File, fileType: FileType): { valid: boolean; message?: string } => {
  const allowedExtensions = ALLOWED_FILE_TYPES[fileType];
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
  
  if (!allowedExtensions.includes(fileExtension)) {
    return {
      valid: false,
      message: `该文件类型不支持 ${fileExtension}，支持的格式：${allowedExtensions.join(', ')}`
    };
  }
  
  if (file.size > FILE_SIZE_LIMITS.DEFAULT) {
    return {
      valid: false,
      message: `文件大小超限，最大支持 ${formatFileSize(FILE_SIZE_LIMITS.DEFAULT)}`
    };
  }
  
  return { valid: true };
};

// 检查文件是否可预览
export const canPreviewFile = (extension: string): boolean => {
  const ext = extension.toLowerCase();
  return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf'].includes(ext);
};